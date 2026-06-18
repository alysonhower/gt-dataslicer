"""Streaming XLSX export."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import xlsxwriter

from ..artifacts import sibling_temp_path
from ..exceptions import ExportLimitError
from ..report import RunReport


EXCEL_MAX_ROWS = 1_048_576
EXCEL_MAX_COLUMNS = 16_384
EXCEL_MAX_STRING_LENGTH = 32_767
EXCEL_MAX_EXACT_NUMBER_DIGITS = 15


@dataclass(slots=True)
class ExcelExportOptions:
    output_path: Path
    sheet_prefix: str = "Results"
    max_rows_per_sheet: int = EXCEL_MAX_ROWS
    split_mode: str = "sheets"
    sheets_per_file: int = 31


@dataclass(slots=True)
class _WorkbookState:
    workbook: Any | None
    path: Path
    temp_path: Path
    sheet_count: int = 0
    worksheet: Any | None = None
    row_index: int = 0
    data_rows_in_sheet: int = 0
    paths: list[str] = field(default_factory=list)
    pending_workbooks: list[_PendingWorkbook] = field(default_factory=list)


@dataclass(slots=True)
class _PendingWorkbook:
    path: Path
    temp_path: Path


def export_rows_to_xlsx(
    *,
    headers: Sequence[str],
    rows: Iterable[Sequence[Any]],
    options: ExcelExportOptions,
    report: RunReport,
    formula_builders: dict[int, Callable[[int], str]] | None = None,
    finalize_report: Callable[[], None] | None = None,
) -> int:
    if len(headers) > EXCEL_MAX_COLUMNS:
        raise ExportLimitError(
            f"Excel supports at most {EXCEL_MAX_COLUMNS} columns; selected {len(headers)}.",
            code="excel_column_limit",
            context={"limit": EXCEL_MAX_COLUMNS, "selected": len(headers)},
        )
    if not 2 <= options.max_rows_per_sheet <= EXCEL_MAX_ROWS:
        raise ExportLimitError(
            "--max-rows-per-sheet must be between 2 and 1048576.",
            code="excel_max_rows_per_sheet",
            context={"min": 2, "max": EXCEL_MAX_ROWS, "value": options.max_rows_per_sheet},
        )
    if options.split_mode not in {"sheets", "files", "both"}:
        raise ExportLimitError(
            "--split-mode must be sheets, files, or both.",
            code="excel_split_mode",
            context={"value": options.split_mode},
        )
    if options.sheets_per_file < 1:
        raise ExportLimitError(
            "--sheets-per-file must be at least 1.",
            code="excel_sheets_per_file",
            context={"min": 1, "value": options.sheets_per_file},
        )

    data_capacity = options.max_rows_per_sheet - 1
    state = _open_workbook(options, file_index=1)
    state.paths.append(str(state.path))
    row_count = 0

    try:
        _ensure_sheet(state, options, headers)
        for row in rows:
            if state.data_rows_in_sheet >= data_capacity:
                _rollover(state, options, headers)
            _write_row(state.worksheet, state.row_index, row, formula_builders=formula_builders)
            state.row_index += 1
            state.data_rows_in_sheet += 1
            row_count += 1

        if finalize_report is not None:
            finalize_report()
        if options.split_mode == "sheets":
            _write_summary_sheet(state.workbook, report, output_rows=row_count)
        _close_workbook(state)
        _commit_workbooks(state.pending_workbooks)
    except Exception:
        _cleanup_workbooks(state)
        raise

    report.output_paths = state.paths
    return row_count


def batched_rows(cursor: Any, batch_size: int) -> Iterator[Sequence[Any]]:
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield from batch


def _open_workbook(options: ExcelExportOptions, file_index: int) -> _WorkbookState:
    path = _output_path(options.output_path, options.split_mode, file_index)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = sibling_temp_path(path)
    workbook = xlsxwriter.Workbook(
        str(temp_path),
        {
            "constant_memory": True,
            "strings_to_formulas": False,
            "strings_to_urls": False,
        },
    )
    return _WorkbookState(workbook=workbook, path=path, temp_path=temp_path)


def _output_path(base: Path, split_mode: str, file_index: int) -> Path:
    if split_mode == "sheets":
        return base
    return base.with_name(f"{base.stem}_{file_index:03d}{base.suffix or '.xlsx'}")


def _ensure_sheet(state: _WorkbookState, options: ExcelExportOptions, headers: Sequence[str]) -> None:
    if state.worksheet is not None:
        return
    if state.workbook is None:
        raise ExportLimitError("Excel workbook is already closed.", code="excel_workbook_closed")
    state.sheet_count += 1
    sheet_name = _sheet_name(options.sheet_prefix, state.sheet_count)
    state.worksheet = state.workbook.add_worksheet(sheet_name)
    _write_row(state.worksheet, 0, headers, header=True)
    state.row_index = 1
    state.data_rows_in_sheet = 0


def _rollover(state: _WorkbookState, options: ExcelExportOptions, headers: Sequence[str]) -> None:
    if options.split_mode == "sheets" or (
        options.split_mode == "both" and state.sheet_count < options.sheets_per_file
    ):
        state.worksheet = None
        _ensure_sheet(state, options, headers)
        return

    _close_workbook(state)
    next_index = len(state.paths) + 1
    new_state = _open_workbook(options, next_index)
    state.workbook = new_state.workbook
    state.path = new_state.path
    state.temp_path = new_state.temp_path
    state.sheet_count = 0
    state.worksheet = None
    state.row_index = 0
    state.data_rows_in_sheet = 0
    state.paths.append(str(new_state.path))
    _ensure_sheet(state, options, headers)


def _sheet_name(prefix: str, index: int) -> str:
    invalid_chars = set('[]:*?/\\')
    safe_prefix = "".join("_" if char in invalid_chars else char for char in prefix).strip().strip("'") or "Results"
    suffix = f"_{index:03d}"
    max_prefix = 31 - len(suffix)
    return f"{safe_prefix[:max_prefix]}{suffix}"


def _close_workbook(state: _WorkbookState) -> None:
    workbook = state.workbook
    if workbook is None:
        return
    state.workbook = None
    workbook.close()
    state.pending_workbooks.append(_PendingWorkbook(path=state.path, temp_path=state.temp_path))


def _commit_workbooks(workbooks: list[_PendingWorkbook]) -> None:
    try:
        for pending in workbooks:
            pending.temp_path.replace(pending.path)
    except Exception:
        for pending in workbooks:
            pending.temp_path.unlink(missing_ok=True)
        raise


def _cleanup_workbooks(state: _WorkbookState) -> None:
    if state.workbook is not None:
        workbook = state.workbook
        state.workbook = None
        try:
            workbook.close()
        except Exception:  # noqa: BLE001 - cleanup must preserve the original export failure.
            pass
    state.temp_path.unlink(missing_ok=True)
    for pending in state.pending_workbooks:
        pending.temp_path.unlink(missing_ok=True)


def _write_row(
    worksheet: Any,
    row_index: int,
    values: Sequence[Any],
    *,
    header: bool = False,
    formula_builders: dict[int, Callable[[int], str]] | None = None,
) -> None:
    for col_index, value in enumerate(values):
        normalized = _normalize_cell(value)
        if formula_builders and col_index in formula_builders and not header:
            worksheet.write_formula(row_index, col_index, formula_builders[col_index](row_index), None, normalized)
        elif isinstance(normalized, str):
            worksheet.write_string(row_index, col_index, normalized)
        else:
            worksheet.write(row_index, col_index, normalized)
    if header:
        worksheet.freeze_panes(1, 0)


def _normalize_cell(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, Decimal):
        return _validate_excel_string(format(value, "f"))
    if isinstance(value, int):
        text = str(value)
        if len(text.lstrip("-")) > EXCEL_MAX_EXACT_NUMBER_DIGITS:
            return _validate_excel_string(text)
        return value
    if isinstance(value, str):
        return _validate_excel_string(value)
    if isinstance(value, (float, date, datetime)):
        return value
    return _validate_excel_string(str(value))


def _validate_excel_string(value: str) -> str:
    if len(value) > EXCEL_MAX_STRING_LENGTH:
        raise ExportLimitError(
            f"Excel supports at most {EXCEL_MAX_STRING_LENGTH} characters in one cell; "
            f"got {len(value)}.",
            code="excel_string_limit",
            context={"limit": EXCEL_MAX_STRING_LENGTH, "length": len(value)},
        )
    return value


def _write_summary_sheet(workbook: Any, report: RunReport, *, output_rows: int) -> None:
    worksheet = workbook.add_worksheet("_Summary")
    rows = [
        ("input_path", report.input_path),
        ("input_rows", report.input_rows),
        ("output_rows", output_rows),
        ("rejected_rows", report.rejected_rows),
        ("filters", " AND ".join(report.applied_filters)),
        ("warnings", " | ".join(report.warnings)),
    ]
    for row_index, row in enumerate(rows):
        _write_row(worksheet, row_index, row)
