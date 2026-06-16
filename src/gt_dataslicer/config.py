"""Configuration loading and CLI option models."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import tomllib
from typing import Any, Literal, cast

import yaml

from .derived import (
    DerivedColumnSpec,
    load_derived_columns_file,
    parse_derived_column_json_items,
    parse_derived_columns,
)
from .exceptions import ConfigError
from .inputs import ResolvedInput


SUPPORTED_COLUMN_TYPES = {"string", "int", "integer", "decimal", "bool", "boolean", "date", "datetime"}
OUTPUT_FORMATS = {"csv", "parquet", "xlsx"}
OutputFormat = Literal["csv", "parquet", "xlsx"]


@dataclass(slots=True)
class CsvOptions:
    encoding: str | None = None
    delimiter: str | None = None
    quotechar: str | None = None
    escapechar: str | None = None
    header: bool | None = None
    null_values: list[str] = field(default_factory=list)
    date_format: str | None = None
    timestamp_format: str | None = None
    strict_mode: bool = True
    store_rejects: bool = False
    sample_size: int | None = None
    max_line_size: int | None = None


@dataclass(slots=True)
class LookupSpec:
    name: str
    path: Path
    column: str


@dataclass(slots=True)
class SortSpec:
    column: str
    direction: str = "asc"


@dataclass(slots=True)
class FilterRunOptions:
    input_path: Path
    output_path: Path
    output_format: OutputFormat = "csv"
    resolved_input: ResolvedInput | None = None
    where: list[str] = field(default_factory=list)
    select: list[str] = field(default_factory=list)
    renames: dict[str, str] = field(default_factory=dict)
    dedupe: bool = False
    dedupe_keys: list[str] = field(default_factory=list)
    sorts: list[SortSpec] = field(default_factory=list)
    lookups: list[LookupSpec] = field(default_factory=list)
    csv: CsvOptions = field(default_factory=CsvOptions)
    sheet_prefix: str = "Results"
    max_rows_per_sheet: int = 1_048_576
    split_mode: str = "sheets"
    sheets_per_file: int = 31
    report_path: Path | None = None
    rejects_path: Path | None = None
    dry_run: bool = False
    case_insensitive_columns: bool = False
    column_types: dict[str, str] = field(default_factory=dict)
    typed_mode: bool = False
    strict_values: bool = False
    batch_size: int = 10_000
    derived_columns: list[DerivedColumnSpec] = field(default_factory=list)
    output_names: list[str] = field(default_factory=list)


def load_config_file(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    suffix = path.suffix.lower()
    try:
        if suffix in {".yaml", ".yml"}:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        elif suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        elif suffix == ".toml":
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        else:
            raise ConfigError("Config files must be YAML, JSON, or TOML.")
    except ConfigError:
        raise
    except Exception as exc:  # noqa: BLE001 - report parser failures as config errors.
        raise ConfigError(f"Could not parse config file {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Config root must be an object/table.")
    return data


def select_preset(config: dict[str, Any], preset: str | None) -> dict[str, Any]:
    if not config:
        return {}
    if preset is None:
        if "presets" in config and len(config) == 1:
            raise ConfigError("Config contains presets; pass --preset to choose one.")
        return config

    presets = config.get("presets")
    if not isinstance(presets, dict):
        raise ConfigError("--preset was provided, but config has no presets table.")
    selected = presets.get(preset)
    if selected is None:
        available = ", ".join(sorted(presets)) or "(none)"
        raise ConfigError(f"Preset '{preset}' was not found. Available presets: {available}")
    if not isinstance(selected, dict):
        raise ConfigError(f"Preset '{preset}' must be an object/table.")
    return selected


def as_list(value: Any, *, key: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    raise ConfigError(f"Config key '{key}' must be a string or list of strings.")


def parse_rename_items(items: list[str]) -> dict[str, str]:
    renames: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ConfigError(f"Rename must use OLD=NEW syntax: {item}")
        old, new = item.split("=", 1)
        old = old.strip()
        new = new.strip()
        if not old or not new:
            raise ConfigError(f"Rename must include both OLD and NEW: {item}")
        renames[old] = new
    return renames


def parse_sort_items(items: list[str]) -> list[SortSpec]:
    specs: list[SortSpec] = []
    for item in items:
        column, sep, direction = item.rpartition(":")
        if not sep:
            column, direction = item, "asc"
        direction = direction.lower().strip()
        column = column.strip()
        if not column:
            raise ConfigError(f"Sort column cannot be empty: {item}")
        if direction not in {"asc", "desc"}:
            raise ConfigError(f"Sort direction for '{column}' must be asc or desc.")
        specs.append(SortSpec(column=column, direction=direction))
    return specs


def parse_lookup_items(items: list[str], *, base_dir: Path | None = None) -> list[LookupSpec]:
    specs: list[LookupSpec] = []
    for item in items:
        if "=" not in item:
            raise ConfigError(f"Lookup must use NAME=PATH:COLUMN syntax: {item}")
        name, rest = item.split("=", 1)
        path_text, sep, column = rest.rpartition(":")
        if not sep:
            raise ConfigError(f"Lookup must include a column after the last colon: {item}")
        name = name.strip()
        column = column.strip()
        if not name or not path_text or not column:
            raise ConfigError(f"Lookup must include NAME, PATH, and COLUMN: {item}")
        path = Path(path_text)
        if base_dir is not None and not path.is_absolute():
            path = base_dir / path
        specs.append(LookupSpec(name=name, path=path, column=column))
    return specs


def parse_type_items(items: list[str]) -> dict[str, str]:
    types: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ConfigError(f"Column type must use COLUMN=TYPE syntax: {item}")
        column, type_name = item.split("=", 1)
        column = column.strip()
        type_name = type_name.strip().lower()
        if type_name not in SUPPORTED_COLUMN_TYPES:
            valid = ", ".join(sorted(SUPPORTED_COLUMN_TYPES))
            raise ConfigError(f"Unsupported type '{type_name}' for column '{column}'. Valid types: {valid}")
        types[column] = normalize_column_type(type_name)
    return types


def parse_output_format(value: Any, *, source: str) -> OutputFormat | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f"{source} must be csv, xlsx, or parquet.")
    normalized = value.strip().lower()
    if normalized not in OUTPUT_FORMATS:
        valid = ", ".join(sorted(OUTPUT_FORMATS))
        raise ConfigError(f"{source} must be one of: {valid}.")
    return cast(OutputFormat, normalized)


def resolve_output_target(
    output_path: Path,
    *,
    cli_output_format: str | None,
    config_output_format: Any,
    allow_directory: bool = False,
) -> tuple[Path, OutputFormat]:
    cli_format = parse_output_format(cli_output_format, source="--format")
    config_format = (
        None
        if cli_format is not None
        else parse_output_format(config_output_format, source="Config key 'output_format'")
    )
    explicit_format = cli_format or config_format
    suffix_format = _format_from_suffix(output_path)

    if allow_directory and output_path.exists() and output_path.is_dir():
        return output_path, explicit_format or "csv"

    if explicit_format is not None:
        if suffix_format is not None and suffix_format != explicit_format:
            raise ConfigError(
                f"Output format '{explicit_format}' conflicts with output path suffix '{output_path.suffix}'."
            )
        if suffix_format is None:
            if output_path.suffix:
                raise ConfigError("Output path suffix must be .csv, .xlsx, .parquet, or omit the suffix.")
            output_path = output_path.with_suffix(f".{explicit_format}")
        return output_path, explicit_format

    if suffix_format is not None:
        return output_path, suffix_format
    if output_path.suffix:
        raise ConfigError("Output path suffix must be .csv, .xlsx, .parquet, or omit the suffix.")
    return output_path.with_suffix(".csv"), "csv"


def _format_from_suffix(path: Path) -> OutputFormat | None:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".xlsx":
        return "xlsx"
    if suffix == ".parquet":
        return "parquet"
    return None


def normalize_column_type(type_name: str) -> str:
    if type_name == "integer":
        return "int"
    if type_name == "boolean":
        return "bool"
    return type_name


def read_select_file(path: Path | None) -> list[str]:
    if path is None:
        return []
    if not path.exists():
        raise ConfigError(f"Select file not found: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def merge_config_and_cli(
    *,
    input_path: Path,
    output_path: Path,
    cli_output_format: str | None,
    preset_config: dict[str, Any],
    config_base_dir: Path | None,
    cli_where: list[str],
    cli_select: list[str],
    select_file: Path | None,
    cli_renames: list[str],
    cli_dedupe: bool,
    cli_dedupe_keys: list[str],
    cli_sorts: list[str],
    cli_lookups: list[str],
    cli_types: list[str],
    cli_derived_columns: list[str],
    derived_columns_file: Path | None,
    cli_output_names: list[str],
    csv_options: CsvOptions,
    sheet_prefix: str,
    max_rows_per_sheet: int,
    split_mode: str,
    sheets_per_file: int,
    report_path: Path | None,
    rejects_path: Path | None,
    dry_run: bool,
    case_insensitive_columns: bool,
    typed_mode: bool,
    strict_values: bool,
    batch_size: int,
    allow_output_directory: bool = False,
) -> FilterRunOptions:
    output_path, output_format = resolve_output_target(
        output_path,
        cli_output_format=cli_output_format,
        config_output_format=preset_config.get("output_format"),
        allow_directory=allow_output_directory,
    )
    config_where = as_list(preset_config.get("where"), key="where")
    config_select = as_list(preset_config.get("select"), key="select")
    config_dedupe_keys = as_list(preset_config.get("dedupe_key") or preset_config.get("dedupe_keys"), key="dedupe_key")
    config_sorts = as_list(preset_config.get("sort") or preset_config.get("sorts"), key="sort")
    config_lookups = as_list(preset_config.get("lookup") or preset_config.get("lookups"), key="lookup")
    output_names = [
        *as_list(preset_config.get("output_name") or preset_config.get("output_names"), key="output_names"),
        *cli_output_names,
    ]

    config_renames_raw = preset_config.get("rename") or preset_config.get("renames") or {}
    if isinstance(config_renames_raw, dict):
        config_renames = {str(k): str(v) for k, v in config_renames_raw.items()}
    else:
        config_renames = parse_rename_items(as_list(config_renames_raw, key="rename"))

    config_types_raw = preset_config.get("types") or preset_config.get("column_types") or {}
    if isinstance(config_types_raw, dict):
        config_types = parse_type_items([f"{key}={value}" for key, value in config_types_raw.items()])
    else:
        config_types = parse_type_items(as_list(config_types_raw, key="types"))

    select_from_file = read_select_file(select_file)
    select = cli_select or select_from_file or config_select
    renames = {**config_renames, **parse_rename_items(cli_renames)}
    column_types = {**config_types, **parse_type_items(cli_types)}

    split_mode = split_mode.lower()
    if split_mode not in {"sheets", "files", "both"}:
        raise ConfigError("--split-mode must be one of: sheets, files, both.")
    if not 2 <= max_rows_per_sheet <= 1_048_576:
        raise ConfigError("--max-rows-per-sheet must be between 2 and 1048576.")
    if sheets_per_file < 1:
        raise ConfigError("--sheets-per-file must be at least 1.")
    if batch_size < 1:
        raise ConfigError("--batch-size must be at least 1.")
    if rejects_path is not None and not csv_options.store_rejects:
        raise ConfigError("--rejects requires --store-rejects so DuckDB captures rejected rows.")

    config_lookup_specs = parse_lookup_items(config_lookups, base_dir=config_base_dir)
    cli_lookup_specs = parse_lookup_items(cli_lookups)
    derived_columns = [
        *parse_derived_columns(preset_config.get("derived_columns")),
        *(load_derived_columns_file(derived_columns_file) if derived_columns_file is not None else []),
        *parse_derived_column_json_items(cli_derived_columns),
    ]

    return FilterRunOptions(
        input_path=input_path,
        output_path=output_path,
        output_format=output_format,
        where=[*config_where, *cli_where],
        select=select,
        renames=renames,
        dedupe=bool(preset_config.get("dedupe", False)) or cli_dedupe,
        dedupe_keys=cli_dedupe_keys or config_dedupe_keys,
        sorts=parse_sort_items(cli_sorts or config_sorts),
        lookups=[*config_lookup_specs, *cli_lookup_specs],
        csv=csv_options,
        sheet_prefix=sheet_prefix,
        max_rows_per_sheet=max_rows_per_sheet,
        split_mode=split_mode,
        sheets_per_file=sheets_per_file,
        report_path=report_path,
        rejects_path=rejects_path,
        dry_run=dry_run,
        case_insensitive_columns=case_insensitive_columns,
        column_types=column_types,
        typed_mode=typed_mode,
        strict_values=strict_values,
        batch_size=batch_size,
        derived_columns=derived_columns,
        output_names=output_names,
    )
