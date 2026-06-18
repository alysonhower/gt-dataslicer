"""Pywebview JavaScript bridge for the DataSlicer desktop UI."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from importlib.metadata import PackageNotFoundError, version
import logging
import os
from pathlib import Path
import subprocess
from typing import Any

import yaml

from ..artifacts import write_text_atomic
from ..config import (
    CsvOptions,
    load_config_file,
    merge_config_and_cli,
    parse_lookup_items,
    select_preset,
)
from ..derived import parse_derived_columns
from ..engine.duckdb_engine import DuckDBEngine
from ..exceptions import ConfigError, DataSlicerError
from ..i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    localize_error,
    messages_for,
    set_language,
    tr,
)
from ..inputs import InputResolutionOptions, InputResolutionSession
from ..runner import planned_run_artifacts, run_filter_inputs
from .filters import build_filter_expression
from .jobs import JobAlreadyRunningError, JobManager, ProgressCallback


LOGGER = logging.getLogger(__name__)


_UI_LOADABLE_CONFIG_KEYS = {
    "case_insensitive_columns",
    "csv_options",
    "dedupe",
    "dedupe_key",
    "dedupe_keys",
    "derived_columns",
    "lookup",
    "lookups",
    "max_rows_per_sheet",
    "output_format",
    "output_name",
    "output_names",
    "rename",
    "renames",
    "select",
    "sheets_per_file",
    "split_mode",
    "sort",
    "sorts",
    "spreadsheet_safe_csv",
    "summarize",
    "summary_group_by",
    "summary_only",
    "summary_totals",
    "where",
}
_UI_LOADABLE_CSV_OPTION_KEYS = {"delimiter", "encoding", "null_value", "null_values"}


class DataSlicerApi:
    """JSON-safe API exposed to the web UI."""

    def __init__(self, *, language: str = DEFAULT_LANGUAGE, job_manager: JobManager | None = None) -> None:
        self._language = language
        set_language(language)
        self._jobs = job_manager or JobManager()
        self._window: Any | None = None

    def bind_window(self, window: Any) -> None:
        self._window = window

    def has_running_job(self) -> bool:
        return self._jobs.has_running_job()

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

    def load_config(self, payload: dict[str, Any]) -> dict[str, object]:
        self._activate_language()
        try:
            config_path = _optional_path(payload.get("config_path"))
            if config_path is None:
                raise ConfigError(tr("ui.error.config_required"), code="ui_config_required")
            config = select_preset(load_config_file(config_path), _optional_text(payload.get("preset")))
            _validate_ui_loadable_config(config)
            return _ok({"path": str(config_path), "config": config})
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

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
            write_text_atomic(path, yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
            return _ok({"path": str(path)})
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def choose_report_file(self) -> dict[str, object]:
        return self._choose_save_file("json", ("JSON (*.json)", "Todos os arquivos (*.*)"))

    def choose_rejects_file(self) -> dict[str, object]:
        return self._choose_save_file("csv", ("CSV (*.csv)", "Todos os arquivos (*.*)"))

    def choose_output_file(self, output_format: str = "csv", multi_file: object = False) -> dict[str, object]:
        normalized_format = output_format if output_format in {"csv", "xlsx", "parquet"} else "csv"
        if _bool_option(multi_file, key="multi_file"):
            return self._choose_output_folder()
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

    def _choose_output_folder(self) -> dict[str, object]:
        self._activate_language()
        if self._window is None:
            return _error("window_not_ready", tr("ui.error.window_not_ready"))
        try:
            webview = _import_webview()
            result = self._window.create_file_dialog(webview.FileDialog.FOLDER)
            return _ok({"path": _first_dialog_path(result), "mode": "folder"})
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def inspect_csv(self, payload: dict[str, Any]) -> dict[str, object]:
        self._activate_language()
        try:
            csv_options = _csv_options(payload)
            typed_mode = _bool_option(payload.get("typed_mode"), key="typed_mode")
            with InputResolutionSession(
                _input_paths(payload),
                options=_input_resolution_options(payload),
            ) as session:
                inspected = []
                for input_ in session.inputs:
                    with DuckDBEngine() as engine:
                        inspected.append((input_, engine.inspect_input(input_, csv_options, typed_mode=typed_mode)))
                first_input, schema = inspected[0]
                first_signature = _schema_signature(schema)
                inputs = []
                schema_mismatches: list[str] = []
                for input_, input_schema in inspected:
                    summary = _input_summary(input_)
                    matches_first = _schema_signature(input_schema) == first_signature
                    summary.update(
                        {
                            "columns": list(input_schema.columns.values()),
                            "types": input_schema.types,
                            "column_count": len(input_schema.columns),
                            "schema_matches_first": matches_first,
                        }
                    )
                    if not matches_first:
                        schema_mismatches.append(input_.source_label)
                    inputs.append(summary)
                warnings = list(session.warnings)
                if schema_mismatches:
                    warnings.append(tr("ui.warning.schema_mismatch"))
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
                    "schema_compatible": not schema_mismatches,
                    "schema_mismatches": schema_mismatches,
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
                compiled = None
                first_schema = None
                validated_inputs: list[str] = []
                for input_ in session.inputs:
                    with DuckDBEngine() as engine:
                        prepared = engine.prepare_filter_query(input_, options, materialize_source=False)
                        schema = prepared.schema
                        if first_schema is None:
                            first_schema = schema
                        if compiled is None:
                            compiled = prepared.compiled_filter
                    validated_inputs.append(input_.source_label)
                assert compiled is not None
                assert first_schema is not None
            return _ok(
                {
                    "valid": True,
                    "normalized_filters": options.where,
                    "sql": compiled.sql,
                    "columns": list(first_schema.columns.values()),
                    "validated_inputs": validated_inputs,
                }
            )
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def preview_rows(self, payload: dict[str, Any]) -> dict[str, object]:
        self._activate_language()
        try:
            options = build_options_from_payload(payload, require_output=False, force_dry_run=True)
            limit = max(1, min(_optional_int(payload.get("limit"), key="limit") or 20, 100))
            with InputResolutionSession(
                _input_paths(payload),
                options=_input_resolution_options(payload),
            ) as session:
                input_ = session.inputs[0]
                input_count = len(session.inputs)
                with DuckDBEngine() as engine:
                    prepared = engine.prepare_filter_query(input_, options, materialize_source=True)
                    rows = engine.connection.execute(
                        f"SELECT * FROM ({prepared.query}) AS preview_rows LIMIT {limit}",
                        prepared.compiled_filter.params,
                    ).fetchall()
            return _ok(
                {
                    "input_path": input_.source_label,
                    "input_count": input_count,
                    "previewed_input_index": 1,
                    "columns": prepared.projection.output_columns,
                    "rows": [[_json_safe_cell(cell) for cell in row] for row in rows],
                    "limit": limit,
                }
            )
        except Exception as exc:  # noqa: BLE001
            return self._exception_response(exc)

    def start_filter_run(self, payload: dict[str, Any]) -> dict[str, object]:
        self._activate_language()
        try:
            if _bool_option(payload.get("delete_zip_after_extract"), key="delete_zip_after_extract") and not _bool_option(
                payload.get("confirm_delete_zip_after_extract"), key="confirm_delete_zip_after_extract"
            ):
                raise ConfigError(
                    tr("ui.error.zip_delete_confirmation_required"),
                    code="zip_delete_confirmation_required",
                )
            options = build_options_from_payload(payload, require_output=True, force_dry_run=False)
            if not _bool_option(payload.get("confirm_overwrite"), key="confirm_overwrite"):
                existing_artifacts = _existing_planned_artifacts(payload, options)
                if existing_artifacts:
                    return _error_payload(
                        {
                            "type": "overwrite_confirmation_required",
                            "code": "overwrite_confirmation_required",
                            "message": tr("ui.error.overwrite_confirmation_required"),
                            "details": "\n".join(str(path) for path in existing_artifacts),
                            "paths": [str(path) for path in existing_artifacts],
                            "context": {"paths": [str(path) for path in existing_artifacts]},
                        }
                    )
            language = self._language

            def runner(progress: ProgressCallback, register_cancel: Any) -> Any:
                set_language(language)
                with InputResolutionSession(
                    _input_paths(payload),
                    options=_input_resolution_options(payload, allow_delete_zip=True),
                ) as session:
                    return run_filter_inputs(
                        options,
                        session.inputs,
                        progress=progress,
                        register_cancel=register_cancel,
                        reuse_schema=_bool_option(payload.get("reuse_schema"), key="reuse_schema"),
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

    def cancel_job(self, job_id: str) -> dict[str, object]:
        self._activate_language()
        try:
            return _ok(self._jobs.cancel(job_id).to_dict())
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
                "code": exc.code,
                "message": localize_error(exc),
                "details": str(exc),
                "context": exc.context,
            }
        LOGGER.exception("Unexpected DataSlicer UI error")
        return {
            "type": exc.__class__.__name__,
            "code": "unexpected_error",
            "message": tr("ui.error.unexpected"),
            "details": str(exc),
            "context": {},
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
        cli_summarize=_bool_option(payload.get("summarize"), key="summarize"),
        cli_summary_only=_bool_option(payload.get("summary_only"), key="summary_only"),
        cli_summary_group_by=_string_list(payload.get("summary_group_by")),
        cli_summary_totals=_string_list(payload.get("summary_totals")),
        cli_renames=_rename_items(payload.get("renames") or payload.get("rename")),
        cli_dedupe=_bool_option(payload.get("dedupe"), key="dedupe"),
        cli_dedupe_keys=_string_list(payload.get("dedupe_keys") or payload.get("dedupe_key")),
        cli_sorts=_sort_items(payload.get("sorts") or payload.get("sort")),
        cli_lookups=_lookup_items(payload.get("lookups") or payload.get("lookup")),
        cli_types=_type_items(payload.get("types") or payload.get("column_types")),
        cli_derived_columns=[],
        derived_columns_file=None,
        cli_output_names=_output_name_items(payload.get("output_names") or payload.get("output_name")),
        csv_options=_csv_options(payload),
        sheet_prefix=str(payload.get("sheet_prefix") or "Results"),
        max_rows_per_sheet=_int_option(
            payload.get("max_rows_per_sheet"),
            key="max_rows_per_sheet",
            default=1_048_576,
        ),
        split_mode=str(payload.get("split_mode") or "sheets"),
        sheets_per_file=_int_option(payload.get("sheets_per_file"), key="sheets_per_file", default=31),
        report_path=_optional_path(payload.get("report_path")),
        rejects_path=_optional_path(payload.get("rejects_path")),
        dry_run=force_dry_run or _bool_option(payload.get("dry_run"), key="dry_run"),
        case_insensitive_columns=_bool_option(payload.get("case_insensitive_columns"), key="case_insensitive_columns"),
        typed_mode=_bool_option(payload.get("typed_mode"), key="typed_mode"),
        strict_values=_bool_option(payload.get("strict_values"), key="strict_values"),
        batch_size=_int_option(payload.get("batch_size"), key="batch_size", default=10_000),
        cli_spreadsheet_safe_csv=_bool_option(payload.get("spreadsheet_safe_csv"), key="spreadsheet_safe_csv"),
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
    split_mode = _optional_text(payload.get("split_mode"))
    if split_mode and split_mode not in {"sheets", "files", "both"}:
        raise ConfigError(
            "split_mode must be sheets, files, or both.",
            code="ui_split_mode",
            context={"value": split_mode},
        )
    if split_mode and split_mode != "sheets":
        config["split_mode"] = split_mode
    max_rows_per_sheet = _optional_int(payload.get("max_rows_per_sheet"), key="max_rows_per_sheet")
    if max_rows_per_sheet is not None and max_rows_per_sheet != 1_048_576:
        config["max_rows_per_sheet"] = max_rows_per_sheet
    sheets_per_file = _optional_int(payload.get("sheets_per_file"), key="sheets_per_file")
    if sheets_per_file is not None and sheets_per_file != 31:
        config["sheets_per_file"] = sheets_per_file
    if _bool_option(payload.get("spreadsheet_safe_csv"), key="spreadsheet_safe_csv"):
        config["spreadsheet_safe_csv"] = True
    if _bool_option(payload.get("summarize"), key="summarize"):
        config["summarize"] = True
    if _bool_option(payload.get("summary_only"), key="summary_only"):
        config["summary_only"] = True
    summary_group_by = _string_list(payload.get("summary_group_by"))
    if summary_group_by:
        config["summary_group_by"] = summary_group_by
    summary_totals = _string_list(payload.get("summary_totals"))
    if summary_totals:
        config["summary_totals"] = summary_totals
    filter_expression = _filter_expression(payload)
    if filter_expression:
        config["where"] = [filter_expression]
    select = _string_list(payload.get("select") or payload.get("selected_columns"))
    if select:
        config["select"] = select
    renames = _rename_items(payload.get("renames") or payload.get("rename"))
    if renames:
        config["rename"] = renames
    if _bool_option(payload.get("dedupe"), key="dedupe"):
        config["dedupe"] = True
    dedupe_keys = _string_list(payload.get("dedupe_keys") or payload.get("dedupe_key"))
    if dedupe_keys:
        config["dedupe_keys"] = dedupe_keys
    sorts = _sort_items(payload.get("sorts") or payload.get("sort"))
    if sorts:
        config["sort"] = sorts
    lookups = _lookup_items(payload.get("lookups") or payload.get("lookup"))
    if lookups:
        config["lookup"] = lookups
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


def _validate_ui_loadable_config(config: dict[str, Any]) -> None:
    unsupported = sorted(key for key in config if key not in _UI_LOADABLE_CONFIG_KEYS)
    csv_options = config.get("csv_options")
    if isinstance(csv_options, dict):
        unsupported.extend(
            f"csv_options.{key}" for key in sorted(csv_options) if key not in _UI_LOADABLE_CSV_OPTION_KEYS
        )
    elif csv_options is not None:
        unsupported.append("csv_options")
    if unsupported:
        keys = ", ".join(unsupported)
        raise ConfigError(
            tr("ui.error.unsupported_config_keys", keys=keys),
            code="ui_unsupported_config_keys",
            context={"keys": keys},
        )
    parse_lookup_items(_lookup_items(config.get("lookup") or config.get("lookups")))


def _empty_config_value(value: object) -> bool:
    return value is None or value == "" or value is False or value == []


def _csv_options(payload: dict[str, Any]) -> CsvOptions:
    csv_payload = payload.get("csv_options") or {}
    if not isinstance(csv_payload, dict):
        raise ConfigError("csv_options must be an object.", code="csv_options_type")
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
        strict_mode=_bool_option(csv_payload.get("strict_mode"), key="csv_options.strict_mode", default=True),
        store_rejects=_bool_option(csv_payload.get("store_rejects"), key="csv_options.store_rejects")
        or rejects_path is not None,
        sample_size=_optional_int(csv_payload.get("sample_size"), key="csv_options.sample_size"),
        max_line_size=_optional_int(csv_payload.get("max_line_size"), key="csv_options.max_line_size"),
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
        raise ConfigError(tr("ui.error.input_required"), code="ui_input_required")
    return unique


def _input_resolution_options(payload: dict[str, Any], *, allow_delete_zip: bool = False) -> InputResolutionOptions:
    delete_zip = _bool_option(payload.get("delete_zip_after_extract"), key="delete_zip_after_extract")
    return InputResolutionOptions(
        zip_passwords=_string_list(payload.get("zip_passwords") or payload.get("zip_password")),
        delete_zip_after_extract=delete_zip if allow_delete_zip else False,
        excel_all_sheets=_bool_option(payload.get("all_excel_sheets"), key="all_excel_sheets"),
    )


def _existing_planned_artifacts(payload: dict[str, Any], options: Any) -> list[Path]:
    with InputResolutionSession(
        _input_paths(payload),
        options=_input_resolution_options(payload),
    ) as session:
        planned = planned_run_artifacts(options, session.inputs)

    existing: list[Path] = []
    seen: set[str] = set()
    for path in planned:
        key = os.path.normcase(str(path.resolve(strict=False)))
        if key in seen:
            continue
        seen.add(key)
        if path.exists() and path.is_file():
            existing.append(path)
    return existing


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


def _schema_signature(schema: Any) -> tuple[tuple[str, str], ...]:
    return tuple((column, str(schema.types[column])) for column in schema.columns.values())


def _output_path(payload: dict[str, Any]) -> Path:
    value = _optional_text(payload.get("output_path"))
    if value is None:
        raise ConfigError(tr("ui.error.output_required"), code="ui_output_required")
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
    return _bool_option(value, key="boolean value")


def _bool_option(value: object, *, key: str, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "sim"}:
            return True
        if lowered in {"false", "0", "no", "n", "nao", "não"}:
            return False
        raise ConfigError(f"{key} must be true or false.", code="boolean_value", context={"key": key})
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    raise ConfigError(f"{key} must be true or false.", code="boolean_value", context={"key": key})


def _int_option(value: object, *, key: str, default: int) -> int:
    if value is None or value == "":
        return default
    result = _optional_int(value, key=key)
    assert result is not None
    return result


def _optional_int(value: object, *, key: str) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ConfigError(f"{key} must be an integer.", code="integer_value", context={"key": key})
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{key} must be an integer.", code="integer_value", context={"key": key}) from exc


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
                name = _optional_text(item.get("name"))
                path = _optional_text(item.get("path"))
                column = _optional_text(item.get("column"))
                if not (name or path or column):
                    continue
                if not (name and path and column):
                    raise ConfigError(
                        f"Lookup must include NAME, PATH, and COLUMN: {item}",
                        code="lookup_missing_parts",
                        context={"item": str(item)},
                    )
                items.append(f"{name}={path}:{column}")
            else:
                items.append(str(item))
        return items
    if isinstance(value, dict):
        name = _optional_text(value.get("name"))
        path = _optional_text(value.get("path"))
        column = _optional_text(value.get("column"))
        if not (name or path or column):
            return []
        if not (name and path and column):
            raise ConfigError(
                f"Lookup must include NAME, PATH, and COLUMN: {value}",
                code="lookup_missing_parts",
                context={"item": str(value)},
            )
        return [f"{name}={path}:{column}"]
    return _string_list(value)


def _type_items(value: object) -> list[str]:
    if isinstance(value, dict):
        return [f"{key}={item}" for key, item in value.items()]
    return _string_list(value)


def _ok(data: dict[str, object]) -> dict[str, object]:
    return {"ok": True, "data": data}


def _json_safe_cell(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    if isinstance(value, date):
        return value.isoformat()
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)


def _error(error_type: str, message: str, *, details: str | None = None) -> dict[str, object]:
    return _error_payload(
        {
            "type": error_type,
            "code": error_type,
            "message": message,
            "details": details or message,
            "context": {},
        }
    )


def _error_payload(error: dict[str, object]) -> dict[str, object]:
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
