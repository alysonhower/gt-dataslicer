"""Pywebview JavaScript bridge for the DataSlicer desktop UI."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
import logging
import os
from pathlib import Path
import subprocess
from typing import Any

import yaml

from ..config import (
    CsvOptions,
    load_config_file,
    merge_config_and_cli,
    select_preset,
)
from ..derived import build_projection, parse_derived_columns
from ..engine.duckdb_engine import DuckDBEngine
from ..exceptions import ConfigError, DataSlicerError
from ..filters.compiler import CompileContext, compile_filter
from ..filters.parser import combine_filters
from ..i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    localize_error_message,
    messages_for,
    set_language,
    tr,
)
from ..inputs import InputResolutionOptions, InputResolutionSession
from ..runner import run_filter_inputs
from .filters import build_filter_expression
from .jobs import JobAlreadyRunningError, JobManager, ProgressCallback


LOGGER = logging.getLogger(__name__)


class DataSlicerApi:
    """JSON-safe API exposed to the web UI."""

    def __init__(self, *, language: str = DEFAULT_LANGUAGE, job_manager: JobManager | None = None) -> None:
        self._language = language
        set_language(language)
        self._jobs = job_manager or JobManager()
        self._window: Any | None = None

    def bind_window(self, window: Any) -> None:
        self._window = window

    def get_app_info(self) -> dict[str, object]:
        return _ok(
            {
                "name": tr("ui.app_name"),
                "descriptor": tr("ui.descriptor"),
                "version": _package_version(),
                "language": self._language,
                "supported_languages": list(SUPPORTED_LANGUAGES),
                "output_formats": ["csv", "xlsx", "parquet"],
            }
        )

    def set_language(self, language: str) -> dict[str, object]:
        try:
            set_language(language)
        except ValueError as exc:
            return _error("invalid_language", str(exc), details=str(exc))
        self._language = language
        return _ok({"language": self._language, "messages": messages_for(language, prefix="ui.")})

    def get_messages(self, language: str | None = None) -> dict[str, object]:
        try:
            selected_language = language or self._language
            return _ok({"language": selected_language, "messages": messages_for(selected_language, prefix="ui.")})
        except ValueError as exc:
            return _error("invalid_language", str(exc), details=str(exc))

    def choose_input_csv(self) -> dict[str, object]:
        return self.choose_input_files()

    def choose_input_files(self) -> dict[str, object]:
        return self._choose_open_file(
            (
                "Arquivos de entrada (*.csv;*.parquet;*.pq;*.xlsx;*.zip)",
                "Todos os arquivos (*.*)",
            ),
            allow_multiple=True,
        )

    def choose_config_file(self) -> dict[str, object]:
        return self._choose_open_file(("Configurações (*.yaml;*.yml;*.json;*.toml)", "Todos os arquivos (*.*)"))

    def choose_lookup_file(self) -> dict[str, object]:
        return self._choose_open_file(("CSV (*.csv)", "Todos os arquivos (*.*)"))

    def save_config(self, payload: dict[str, Any]) -> dict[str, object]:
        self._activate_language()
        if self._window is None:
            return _error("window_not_ready", tr("ui.error.window_not_ready"))
        try:
            webview = _import_webview()
            result = self._window.create_file_dialog(
                webview.FileDialog.SAVE,
                save_filename="dataslicer-config.yaml",
                file_types=("YAML (*.yaml)", "Todos os arquivos (*.*)"),
            )
            path_text = _first_dialog_path(result)
            if not path_text:
                return _ok({"path": ""})
            path = Path(path_text)
            config = _config_from_payload(payload)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")
            return _ok({"path": str(path)})
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def choose_report_file(self) -> dict[str, object]:
        return self._choose_save_file("json", ("JSON (*.json)", "Todos os arquivos (*.*)"))

    def choose_rejects_file(self) -> dict[str, object]:
        return self._choose_save_file("csv", ("CSV (*.csv)", "Todos os arquivos (*.*)"))

    def choose_output_file(self, output_format: str = "csv") -> dict[str, object]:
        normalized_format = output_format if output_format in {"csv", "xlsx", "parquet"} else "csv"
        file_types = {
            "csv": ("CSV (*.csv)", "Todos os arquivos (*.*)"),
            "xlsx": ("Excel (*.xlsx)", "Todos os arquivos (*.*)"),
            "parquet": ("Parquet (*.parquet)", "Todos os arquivos (*.*)"),
        }[normalized_format]
        return self._choose_save_file(normalized_format, file_types)

    def open_output_folder(self, path: str) -> dict[str, object]:
        self._activate_language()
        try:
            target = Path(path)
            folder = target if target.is_dir() else target.parent
            if os.name == "nt":
                os.startfile(folder)  # type: ignore[attr-defined]
            elif os.name == "posix":
                opener = "open" if os.uname().sysname == "Darwin" else "xdg-open"
                subprocess.Popen([opener, str(folder)])
            return _ok({"path": str(folder)})
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def _choose_save_file(self, suffix: str, file_types: tuple[str, str]) -> dict[str, object]:
        self._activate_language()
        if self._window is None:
            return _error("window_not_ready", tr("ui.error.window_not_ready"))
        try:
            webview = _import_webview()
            result = self._window.create_file_dialog(
                webview.FileDialog.SAVE,
                save_filename=f"resultado.{suffix}",
                file_types=file_types,
            )
            return _ok({"path": _first_dialog_path(result)})
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def inspect_csv(self, payload: dict[str, Any]) -> dict[str, object]:
        self._activate_language()
        try:
            csv_options = _csv_options(payload)
            typed_mode = bool(payload.get("typed_mode", False))
            with InputResolutionSession(
                _input_paths(payload),
                options=_input_resolution_options(payload),
            ) as session:
                first_input = session.inputs[0]
                schema = DuckDBEngine().inspect_input(first_input, csv_options, typed_mode=typed_mode)
                inputs = [_input_summary(item) for item in session.inputs]
                warnings = list(session.warnings)
                display_path = first_input.zip_source or first_input.source_path
                size_path = display_path if display_path.exists() else first_input.path
                size_bytes = size_path.stat().st_size if size_path.exists() else 0
            return _ok(
                {
                    "path": str(display_path),
                    "paths": [item["source_path"] for item in inputs],
                    "inputs": inputs,
                    "columns": list(schema.columns.values()),
                    "types": schema.types,
                    "size_bytes": size_bytes,
                    "warnings": warnings,
                }
            )
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def validate_filter(self, payload: dict[str, Any]) -> dict[str, object]:
        self._activate_language()
        try:
            options = build_options_from_payload(payload, require_output=False, force_dry_run=True)
            with InputResolutionSession(
                _input_paths(payload),
                options=_input_resolution_options(payload),
            ) as session:
                first_input = session.inputs[0]
                engine = DuckDBEngine()
                schema = engine.inspect_input(first_input, options.csv, typed_mode=options.typed_mode)
                column_types = engine.resolve_column_types(schema, options)
                lookup_bindings = engine.register_lookups(
                    options.lookups,
                    options.csv,
                    case_insensitive_columns=options.case_insensitive_columns,
                )
                expr = combine_filters(options.where)
                compiled = compile_filter(
                    expr,
                    CompileContext(
                        columns=schema.columns,
                        column_types=column_types,
                        lookups=lookup_bindings,
                        case_insensitive_columns=options.case_insensitive_columns,
                        strict_values=options.strict_values,
                    ),
                )
                selected_columns = engine._resolve_selected_columns(  # noqa: SLF001 - shared validation path.
                    schema,
                    options.select,
                    options.case_insensitive_columns,
                )
                resolved_renames = engine._resolve_renames(  # noqa: SLF001 - shared validation path.
                    schema,
                    options.renames,
                    options.case_insensitive_columns,
                )
                output_columns = [resolved_renames.get(column, column) for column in selected_columns]
                build_projection(
                    schema_columns=schema.columns,
                    selected_columns=selected_columns,
                    output_columns=output_columns,
                    derived_columns=options.derived_columns,
                    case_insensitive_columns=options.case_insensitive_columns,
                )
            return _ok(
                {
                    "valid": True,
                    "normalized_filters": options.where,
                    "sql": compiled.sql,
                    "columns": list(schema.columns.values()),
                }
            )
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def start_filter_run(self, payload: dict[str, Any]) -> dict[str, object]:
        self._activate_language()
        try:
            options = build_options_from_payload(payload, require_output=True, force_dry_run=False)
            language = self._language

            def runner(progress: ProgressCallback) -> Any:
                set_language(language)
                with InputResolutionSession(
                    _input_paths(payload),
                    options=_input_resolution_options(payload),
                ) as session:
                    return run_filter_inputs(
                        options,
                        session.inputs,
                        progress=progress,
                        reuse_schema=bool(payload.get("reuse_schema", False)),
                        resolution_warnings=session.warnings,
                    )

            job = self._jobs.start(runner, on_error=self._ui_error_from_exception)
            return _ok(job.to_dict())
        except JobAlreadyRunningError:
            return _error("job_running", tr("ui.error.job_running"))
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def get_job_status(self, job_id: str) -> dict[str, object]:
        self._activate_language()
        try:
            return _ok(self._jobs.get(job_id).to_dict())
        except KeyError:
            return _error("job_not_found", f"Job not found: {job_id}", details=job_id)
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def _choose_open_file(self, file_types: tuple[str, str], *, allow_multiple: bool = False) -> dict[str, object]:
        self._activate_language()
        if self._window is None:
            return _error("window_not_ready", tr("ui.error.window_not_ready"))
        try:
            webview = _import_webview()
            result = self._window.create_file_dialog(
                webview.FileDialog.OPEN,
                allow_multiple=allow_multiple,
                file_types=file_types,
            )
            paths = _dialog_paths(result)
            return _ok({"path": paths[0] if paths else None, "paths": paths})
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def _activate_language(self) -> None:
        set_language(self._language)

    def _exception_response(self, exc: Exception) -> dict[str, object]:
        return _error_payload(self._ui_error_from_exception(exc))

    def _ui_error_from_exception(self, exc: Exception) -> dict[str, str]:
        set_language(self._language)
        if isinstance(exc, DataSlicerError):
            return {
                "type": exc.__class__.__name__,
                "message": localize_error_message(str(exc)),
                "details": str(exc),
            }
        LOGGER.exception("Unexpected DataSlicer UI error")
        return {
            "type": exc.__class__.__name__,
            "message": tr("ui.error.unexpected"),
            "details": str(exc),
        }


def build_options_from_payload(
    payload: dict[str, Any],
    *,
    require_output: bool,
    force_dry_run: bool,
) -> Any:
    input_paths = _input_paths(payload)
    input_path = input_paths[0]
    output_path = _output_path(payload) if require_output else Path("dry-run")
    config_path = _optional_path(payload.get("config_path"))
    preset = _optional_text(payload.get("preset"))
    preset_config = select_preset(load_config_file(config_path), preset)

    filter_expression = _filter_expression(payload)
    cli_where = [filter_expression] if filter_expression else _string_list(payload.get("where"))

    options = merge_config_and_cli(
        input_path=input_path,
        output_path=output_path,
        cli_output_format=_optional_text(payload.get("output_format")),
        preset_config=preset_config,
        config_base_dir=config_path.resolve().parent if config_path is not None else None,
        cli_where=cli_where,
        cli_select=_string_list(payload.get("select") or payload.get("selected_columns")),
        select_file=_optional_path(payload.get("select_file")),
        cli_summarize=bool(payload.get("summarize", False)),
        cli_summary_only=bool(payload.get("summary_only", False)),
        cli_summary_group_by=_string_list(payload.get("summary_group_by")),
        cli_summary_totals=_string_list(payload.get("summary_totals")),
        cli_renames=_rename_items(payload.get("renames") or payload.get("rename")),
        cli_dedupe=bool(payload.get("dedupe", False)),
        cli_dedupe_keys=_string_list(payload.get("dedupe_keys") or payload.get("dedupe_key")),
        cli_sorts=_sort_items(payload.get("sorts") or payload.get("sort")),
        cli_lookups=_lookup_items(payload.get("lookups") or payload.get("lookup")),
        cli_types=_type_items(payload.get("types") or payload.get("column_types")),
        cli_derived_columns=[],
        derived_columns_file=None,
        cli_output_names=_output_name_items(payload.get("output_names") or payload.get("output_name")),
        csv_options=_csv_options(payload),
        sheet_prefix=str(payload.get("sheet_prefix") or "Results"),
        max_rows_per_sheet=int(payload.get("max_rows_per_sheet") or 1_048_576),
        split_mode=str(payload.get("split_mode") or "sheets"),
        sheets_per_file=int(payload.get("sheets_per_file") or 31),
        report_path=_optional_path(payload.get("report_path")),
        rejects_path=_optional_path(payload.get("rejects_path")),
        dry_run=force_dry_run or bool(payload.get("dry_run", False)),
        case_insensitive_columns=bool(payload.get("case_insensitive_columns", False)),
        typed_mode=bool(payload.get("typed_mode", False)),
        strict_values=bool(payload.get("strict_values", False)),
        batch_size=int(payload.get("batch_size") or 10_000),
        allow_output_directory=len(input_paths) > 1,
    )
    options.derived_columns = [*options.derived_columns, *parse_derived_columns(payload.get("derived_columns"))]
    return options


def _filter_expression(payload: dict[str, Any]) -> str:
    filters_payload = payload.get("filters")
    if isinstance(filters_payload, dict):
        return build_filter_expression(filters_payload)
    raw_filter = payload.get("raw_filter")
    if raw_filter:
        return str(raw_filter).strip()
    conditions = payload.get("conditions")
    if isinstance(conditions, list):
        return build_filter_expression(
            {
                "mode": "visual",
                "combine": payload.get("combine") or "and",
                "conditions": conditions,
            }
        )
    return ""


def _config_from_payload(payload: dict[str, Any]) -> dict[str, object]:
    config: dict[str, object] = {}
    output_format = _optional_text(payload.get("output_format"))
    if output_format:
        config["output_format"] = output_format
    filter_expression = _filter_expression(payload)
    if filter_expression:
        config["where"] = [filter_expression]
    select = _string_list(payload.get("select") or payload.get("selected_columns"))
    if select:
        config["select"] = select
    renames = _rename_items(payload.get("renames") or payload.get("rename"))
    if renames:
        config["rename"] = renames
    if payload.get("summarize"):
        config["summarize"] = bool(payload.get("summarize"))
    if payload.get("summary_only"):
        config["summary_only"] = True
    summary_group_by = _string_list(payload.get("summary_group_by"))
    if summary_group_by:
        config["summary_group_by"] = summary_group_by
    summary_totals = _string_list(payload.get("summary_totals"))
    if summary_totals:
        config["summary_totals"] = summary_totals
    if payload.get("dedupe"):
        config["dedupe"] = True
    dedupe_keys = _string_list(payload.get("dedupe_keys") or payload.get("dedupe_key"))
    if dedupe_keys:
        config["dedupe_keys"] = dedupe_keys
    sorts = _sort_items(payload.get("sorts") or payload.get("sort"))
    if sorts:
        config["sort"] = sorts
    derived_columns = payload.get("derived_columns")
    if isinstance(derived_columns, list) and derived_columns:
        config["derived_columns"] = derived_columns
    output_names = _output_name_items(payload.get("output_names") or payload.get("output_name"))
    if any(output_names):
        config["output_names"] = output_names
    csv_options = payload.get("csv_options")
    if isinstance(csv_options, dict):
        clean_csv = {
            key: value
            for key, value in csv_options.items()
            if not _empty_config_value(value)
        }
        if clean_csv:
            config["csv_options"] = clean_csv
    return config


def _empty_config_value(value: object) -> bool:
    return value is None or value == "" or value is False or value == []


def _csv_options(payload: dict[str, Any]) -> CsvOptions:
    csv_payload = payload.get("csv_options") or {}
    if not isinstance(csv_payload, dict):
        raise ConfigError("csv_options must be an object.")
    rejects_path = _optional_path(payload.get("rejects_path"))
    return CsvOptions(
        encoding=_optional_text(csv_payload.get("encoding")),
        delimiter=_optional_text(csv_payload.get("delimiter")),
        quotechar=_optional_text(csv_payload.get("quotechar")),
        escapechar=_optional_text(csv_payload.get("escapechar")),
        header=_optional_bool(csv_payload.get("header")),
        null_values=_string_list(csv_payload.get("null_values") or csv_payload.get("null_value")),
        date_format=_optional_text(csv_payload.get("date_format")),
        timestamp_format=_optional_text(csv_payload.get("timestamp_format")),
        strict_mode=bool(csv_payload.get("strict_mode", True)),
        store_rejects=bool(csv_payload.get("store_rejects", False)) or rejects_path is not None,
        sample_size=_optional_int(csv_payload.get("sample_size")),
        max_line_size=_optional_int(csv_payload.get("max_line_size")),
    )


def _input_path(payload: dict[str, Any]) -> Path:
    paths = _input_paths(payload)
    return paths[0]


def _input_paths(payload: dict[str, Any]) -> list[Path]:
    raw_paths = payload.get("input_paths")
    paths = [Path(path) for path in _string_list(raw_paths)]
    value = _optional_text(payload.get("input_path"))
    if value is not None:
        paths.insert(0, Path(value))
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        text = str(path)
        if text in seen:
            continue
        seen.add(text)
        unique.append(path)
    if not unique:
        raise ConfigError(tr("ui.error.input_required"))
    return unique


def _input_resolution_options(payload: dict[str, Any]) -> InputResolutionOptions:
    return InputResolutionOptions(
        zip_passwords=_string_list(payload.get("zip_passwords") or payload.get("zip_password")),
        delete_zip_after_extract=bool(payload.get("delete_zip_after_extract", False)),
        excel_all_sheets=bool(payload.get("all_excel_sheets", False)),
    )


def _input_summary(input_: Any) -> dict[str, object]:
    return {
        "path": str(input_.path),
        "source_path": input_.source_label,
        "display_name": input_.display_name,
        "label": input_.label,
        "format": input_.format,
        "zip_source": str(input_.zip_source) if input_.zip_source is not None else None,
        "zip_member": input_.zip_member,
        "excel_sheet": input_.excel_sheet,
        "staged": input_.staged,
        "warnings": input_.warnings,
    }


def _output_path(payload: dict[str, Any]) -> Path:
    value = _optional_text(payload.get("output_path"))
    if value is None:
        raise ConfigError(tr("ui.error.output_required"))
    return Path(value)


def _optional_path(value: object) -> Path | None:
    text = _optional_text(value)
    return Path(text) if text is not None else None


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_bool(value: object) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "sim"}:
            return True
        if lowered in {"false", "0", "no", "nao", "não"}:
            return False
    return bool(value)


def _optional_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _string_list(value: object) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _output_name_items(value: object) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value]
    return [str(value).strip()]


def _rename_items(value: object) -> list[str]:
    if isinstance(value, dict):
        return [f"{key}={item}" for key, item in value.items()]
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if isinstance(item, dict):
                old = item.get("old") or item.get("from")
                new = item.get("new") or item.get("to")
                if old and new:
                    items.append(f"{old}={new}")
            else:
                items.append(str(item))
        return items
    return _string_list(value)


def _sort_items(value: object) -> list[str]:
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if isinstance(item, dict):
                column = item.get("column")
                direction = item.get("direction") or "asc"
                if column:
                    items.append(f"{column}:{direction}")
            else:
                items.append(str(item))
        return items
    return _string_list(value)


def _lookup_items(value: object) -> list[str]:
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if isinstance(item, dict):
                name = item.get("name")
                path = item.get("path")
                column = item.get("column")
                if name and path and column:
                    items.append(f"{name}={path}:{column}")
            else:
                items.append(str(item))
        return items
    return _string_list(value)


def _type_items(value: object) -> list[str]:
    if isinstance(value, dict):
        return [f"{key}={item}" for key, item in value.items()]
    return _string_list(value)


def _ok(data: dict[str, object]) -> dict[str, object]:
    return {"ok": True, "data": data}


def _error(error_type: str, message: str, *, details: str | None = None) -> dict[str, object]:
    return _error_payload({"type": error_type, "message": message, "details": details or message})


def _error_payload(error: dict[str, str]) -> dict[str, object]:
    return {"ok": False, "error": error}


def _package_version() -> str:
    try:
        return version("gt-dataslicer")
    except PackageNotFoundError:
        return "0.1.0"


def _import_webview() -> Any:
    import webview

    return webview


def _first_dialog_path(result: object) -> str | None:
    paths = _dialog_paths(result)
    return paths[0] if paths else None


def _dialog_paths(result: object) -> list[str]:
    if result is None:
        return []
    if isinstance(result, (list, tuple)):
        return [str(item) for item in result]
    return [str(result)]
