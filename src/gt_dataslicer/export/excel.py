"""Streaming XLSX export."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import xlsxwriter

from ..exceptions import ExportLimitError
from ..report import RunReport


EXCEL_MAX_ROWS = 1_048_576
EXCEL_MAX_COLUMNS = 16_384


@dataclass(slots=True)
class ExcelExportOptions:
    output_path: Path
    sheet_prefix: str = "Results"
    max_rows_per_sheet: int = EXCEL_MAX_ROWS
    split_mode: str = "sheets"
    sheets_per_file: int = 31


@dataclass(slots=True)
class _WorkbookState:
    workbook: Any
    path: Path
    sheet_count: int = 0
    worksheet: Any | None = None
    row_index: int = 0
    data_rows_in_sheet: int = 0
    paths: list[str] = field(default_factory=list)


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
        raise ExportLimitError(f"Excel supports at most {EXCEL_MAX_COLUMNS} columns; selected {len(headers)}.")
    if not 2 <= options.max_rows_per_sheet <= EXCEL_MAX_ROWS:
        raise ExportLimitError("--max-rows-per-sheet must be between 2 and 1048576.")

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
    finally:
        state.workbook.close()

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
    workbook = xlsxwriter.Workbook(
        str(path),
        {
            "constant_memory": True,
            "strings_to_formulas": False,
            "strings_to_urls": False,
        },
    )
    return _WorkbookState(workbook=workbook, path=path)


def _output_path(base: Path, split_mode: str, file_index: int) -> Path:
    if split_mode == "sheets":
        return base
    return base.with_name(f"{base.stem}_{file_index:03d}{base.suffix or '.xlsx'}")


def _ensure_sheet(state: _WorkbookState, options: ExcelExportOptions, headers: Sequence[str]) -> None:
    if state.worksheet is not None:
        return
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

    state.workbook.close()
    next_index = len(state.paths) + 1
    new_state = _open_workbook(options, next_index)
    state.workbook = new_state.workbook
    state.path = new_state.path
    state.sheet_count = 0
    state.worksheet = None
    state.row_index = 0
    state.data_rows_in_sheet = 0
    state.paths.append(str(new_state.path))
    _ensure_sheet(state, options, headers)


def _sheet_name(prefix: str, index: int) -> str:
    invalid_chars = set('[]:*?/\\')
    safe_prefix = "".join("_" if char in invalid_chars else char for char in prefix).strip() or "Results"
    suffix = f"_{index:03d}"
    max_prefix = 31 - len(suffix)
    return f"{safe_prefix[:max_prefix]}{suffix}"


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
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (str, int, float, bool, date, datetime)):
        return value
    return str(value)


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
