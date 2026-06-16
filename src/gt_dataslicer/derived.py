"""Post-filter derived column definitions and SQL compilation."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import tomllib
from typing import Any, Literal

import yaml
from xlsxwriter.utility import xl_rowcol_to_cell

from .exceptions import ConfigError, FilterValidationError
from .filters.compiler import quote_identifier, quote_literal


PositionMode = Literal["append", "before", "after"]

CASE_OPERATIONS = {"uppercase", "lowercase", "title_case"}
NO_PARAM_OPERATIONS = {
    "uppercase",
    "lowercase",
    "title_case",
    "trim",
    "remove_extra_spaces",
    "keep_digits",
    "keep_letters",
    "remove_accents",
    "remove_punctuation",
    "remove_symbols",
    "remove_spaces",
    "format_cpf",
    "format_cnpj",
    "format_phone",
}
TEXT_PARAM_OPERATIONS = {
    "add_prefix",
    "add_suffix",
    "extract_before",
    "extract_after",
    "default_if_blank",
    "default_if_empty",
    "default_if_null",
}
COUNT_PARAM_OPERATIONS = {"pad_left", "pad_right", "take_first", "take_last", "remove_first", "remove_last"}

OPERATION_ALIASES = {
    "upper": "uppercase",
    "lower": "lowercase",
    "title": "title_case",
    "proper": "title_case",
    "strip": "trim",
    "normalize_spaces": "remove_extra_spaces",
    "keep_numbers": "keep_digits",
    "only_digits": "keep_digits",
    "only_letters": "keep_letters",
    "remove_symbols": "remove_punctuation",
    "prefix": "add_prefix",
    "suffix": "add_suffix",
    "replace": "replace_text",
    "default": "default_if_blank",
}


@dataclass(slots=True)
class TransformSpec:
    operation: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DerivedColumnPosition:
    mode: PositionMode = "append"
    target: str | None = None


@dataclass(slots=True)
class DerivedColumnSpec:
    source: str
    transforms: list[TransformSpec] = field(default_factory=list)
    output_name: str | None = None
    name_prefix: str = ""
    name_suffix: str = ""
    name_separator: str = ""
    position: DerivedColumnPosition = field(default_factory=DerivedColumnPosition)

    def generated_name(self, source_name: str | None = None) -> str:
        if self.output_name:
            return self.output_name
        source = source_name or self.source
        prefix = _affix_before(self.name_prefix, self.name_separator)
        suffix = _affix_after(self.name_suffix, self.name_separator)
        return f"{prefix}{source}{suffix}"


@dataclass(slots=True)
class ResolvedDerivedColumn:
    source_column: str
    output_name: str
    sql_expression: str
    transforms: list[TransformSpec]
    position: DerivedColumnPosition
    source_output_name: str | None = None


@dataclass(slots=True)
class ProjectionItem:
    sql_expression: str
    output_name: str
    source_column: str | None = None
    derived: ResolvedDerivedColumn | None = None


@dataclass(slots=True)
class DerivedProjection:
    items: list[ProjectionItem]
    output_columns: list[str]
    required_source_columns: list[str]
    derived_columns: list[ResolvedDerivedColumn]

    @property
    def select_items(self) -> list[str]:
        return [
            f"{item.sql_expression} AS {quote_identifier(item.output_name)}"
            for item in self.items
        ]

    def excel_formula_builders(self) -> dict[int, Callable[[int], str]]:
        builders: dict[int, Callable[[int], str]] = {}
        output_index = {name: index for index, name in enumerate(self.output_columns)}
        for item in self.items:
            if item.derived is None or item.derived.source_output_name is None:
                continue
            target_index = output_index[item.output_name]
            source_index = output_index.get(item.derived.source_output_name)
            if source_index is None:
                continue
            builder = _excel_formula_builder(item.derived.transforms, source_index)
            if builder is not None:
                builders[target_index] = builder
        return builders


def load_derived_columns_file(path: Path) -> list[DerivedColumnSpec]:
    if not path.exists():
        raise ConfigError(f"Derived columns file not found: {path}")
    suffix = path.suffix.lower()
    try:
        if suffix in {".yaml", ".yml"}:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        elif suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        elif suffix == ".toml":
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        else:
            raise ConfigError("Derived columns files must be YAML, JSON, or TOML.")
    except ConfigError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ConfigError(f"Could not parse derived columns file {path}: {exc}") from exc
    return parse_derived_columns(_extract_derived_columns(data))


def parse_derived_columns(value: Any) -> list[DerivedColumnSpec]:
    if value is None or value == "":
        return []
    raw_items = _extract_derived_columns(value)
    specs: list[DerivedColumnSpec] = []
    for index, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            raise ConfigError(f"Derived column #{index} must be an object.")
        specs.append(_parse_derived_column(raw, index=index))
    return specs


def parse_derived_column_json_items(items: Iterable[str]) -> list[DerivedColumnSpec]:
    specs: list[DerivedColumnSpec] = []
    for item in items:
        try:
            decoded = json.loads(item)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid derived column JSON: {exc}") from exc
        specs.extend(parse_derived_columns(decoded))
    return specs


def build_projection(
    *,
    schema_columns: dict[str, str],
    selected_columns: list[str],
    output_columns: list[str],
    derived_columns: list[DerivedColumnSpec],
    case_insensitive_columns: bool,
) -> DerivedProjection:
    items = [
        ProjectionItem(
            sql_expression=quote_identifier(source),
            output_name=output,
            source_column=source,
        )
        for source, output in zip(selected_columns, output_columns, strict=True)
    ]
    required = list(selected_columns)
    resolved: list[ResolvedDerivedColumn] = []

    for spec in derived_columns:
        source_column = _resolve_column(schema_columns, spec.source, case_insensitive_columns)
        if source_column not in required:
            required.append(source_column)
        output_name = spec.generated_name(source_column).strip()
        if not output_name:
            raise FilterValidationError("Derived column name cannot be empty.")
        if output_name in [item.output_name for item in items]:
            raise FilterValidationError(f"Derived column name '{output_name}' already exists.")

        expression = _compile_transform_chain(quote_identifier(source_column), spec.transforms)
        source_output_name = _source_output_name(source_column, selected_columns, output_columns)
        derived = ResolvedDerivedColumn(
            source_column=source_column,
            output_name=output_name,
            sql_expression=expression,
            transforms=spec.transforms,
            position=spec.position,
            source_output_name=source_output_name,
        )
        item = ProjectionItem(
            sql_expression=expression,
            output_name=output_name,
            source_column=source_column,
            derived=derived,
        )
        insert_at = _position_index(items, spec.position, schema_columns, selected_columns, output_columns, case_insensitive_columns)
        items.insert(insert_at, item)
        resolved.append(derived)

    return DerivedProjection(
        items=items,
        output_columns=[item.output_name for item in items],
        required_source_columns=required,
        derived_columns=resolved,
    )


def _extract_derived_columns(data: Any) -> list[Any]:
    if isinstance(data, dict):
        if "derived_columns" in data:
            raw = data["derived_columns"]
        elif "columns" in data:
            raw = data["columns"]
        else:
            raw = [data]
    else:
        raw = data
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return [raw]
    raise ConfigError("derived_columns must be a list of objects.")


def _parse_derived_column(raw: dict[str, Any], *, index: int) -> DerivedColumnSpec:
    source = str(raw.get("source") or raw.get("column") or "").strip()
    if not source:
        raise ConfigError(f"Derived column #{index} requires a source column.")

    name_raw = raw.get("name") or {}
    output_name = _optional_text(raw.get("output_name") or raw.get("output"))
    prefix = ""
    suffix = ""
    separator = ""
    if isinstance(name_raw, str):
        output_name = name_raw.strip() or output_name
    elif isinstance(name_raw, dict):
        output_name = _optional_text(name_raw.get("output") or name_raw.get("value") or output_name)
        prefix = str(name_raw.get("prefix") or "")
        suffix = str(name_raw.get("suffix") or "")
        separator = str(name_raw.get("separator") or "")
    elif name_raw:
        raise ConfigError(f"Derived column #{index} name must be text or an object.")

    position = _parse_position(raw.get("position"))
    transforms = [_parse_transform(item, column_index=index) for item in _extract_transforms(raw)]
    _validate_transform_chain(transforms, column_index=index)
    return DerivedColumnSpec(
        source=source,
        transforms=transforms,
        output_name=output_name,
        name_prefix=prefix,
        name_suffix=suffix,
        name_separator=separator,
        position=position,
    )


def _extract_transforms(raw: dict[str, Any]) -> list[Any]:
    transforms = raw.get("transforms") or raw.get("transformations") or []
    if isinstance(transforms, str):
        return [{"operation": transforms}]
    if not isinstance(transforms, list):
        raise ConfigError("Derived column transforms must be a list.")
    return transforms


def _parse_transform(raw: Any, *, column_index: int) -> TransformSpec:
    if isinstance(raw, str):
        operation = raw
        params: dict[str, Any] = {}
    elif isinstance(raw, dict):
        operation = str(raw.get("operation") or raw.get("type") or "").strip()
        params = {str(key): value for key, value in raw.items() if key not in {"operation", "type"}}
    else:
        raise ConfigError(f"Derived column #{column_index} transform must be text or an object.")
    operation = OPERATION_ALIASES.get(operation, operation)
    if not operation:
        raise ConfigError(f"Derived column #{column_index} has a transform without operation.")
    return TransformSpec(operation=operation, params=params)


def _parse_position(raw: Any) -> DerivedColumnPosition:
    if raw is None or raw == "":
        return DerivedColumnPosition()
    if isinstance(raw, str):
        mode = raw.strip().lower()
        if mode != "append":
            raise ConfigError("Derived column position text must be 'append'.")
        return DerivedColumnPosition()
    if not isinstance(raw, dict):
        raise ConfigError("Derived column position must be an object.")
    mode = str(raw.get("mode") or "append").strip().lower()
    if mode not in {"append", "before", "after"}:
        raise ConfigError("Derived column position mode must be append, before, or after.")
    target = _optional_text(raw.get("target") or raw.get("column"))
    if mode in {"before", "after"} and not target:
        raise ConfigError("Derived column position before/after requires a target column.")
    return DerivedColumnPosition(mode=mode, target=target)


def _validate_transform_chain(transforms: list[TransformSpec], *, column_index: int) -> None:
    seen_case = [item.operation for item in transforms if item.operation in CASE_OPERATIONS]
    if len(seen_case) > 1:
        raise ConfigError(f"Derived column #{column_index} cannot combine case transformations.")
    for transform in transforms:
        operation = transform.operation
        if operation == "replace_text":
            _required_text(transform, "old", aliases=("find", "from"))
            _required_text(transform, "new", aliases=("replace", "to", "with"))
        elif operation in NO_PARAM_OPERATIONS:
            continue
        elif operation in TEXT_PARAM_OPERATIONS:
            _required_text(transform, "text", aliases=("value", "separator", "default"))
        elif operation in COUNT_PARAM_OPERATIONS:
            _required_count(transform)
        else:
            raise ConfigError(f"Unsupported derived column transform: {operation}")


def _compile_transform_chain(base_expression: str, transforms: list[TransformSpec]) -> str:
    expression = f"CAST({base_expression} AS VARCHAR)"
    for transform in transforms:
        expression = _apply_transform_sql(expression, transform)
    return expression


def _apply_transform_sql(expression: str, transform: TransformSpec) -> str:
    operation = transform.operation
    if operation == "replace_text":
        old = _text_param(transform, "old", aliases=("find", "from"))
        new = _text_param(transform, "new", aliases=("replace", "to", "with"))
        return f"replace({expression}, {quote_literal(old)}, {quote_literal(new)})"
    if operation == "uppercase":
        return f"upper({expression})"
    if operation == "lowercase":
        return f"lower({expression})"
    if operation == "title_case":
        return (
            "array_to_string("
            f"list_transform(regexp_split_to_array(lower({expression}), '\\s+'), "
            "x -> upper(left(x, 1)) || substring(x, 2)), ' ')"
        )
    if operation == "trim":
        return f"trim({expression})"
    if operation == "remove_extra_spaces":
        return f"regexp_replace(trim({expression}), '\\s+', ' ', 'g')"
    if operation == "add_prefix":
        return f"{quote_literal(_text_param(transform, 'text', aliases=('value',)))} || {expression}"
    if operation == "add_suffix":
        return f"{expression} || {quote_literal(_text_param(transform, 'text', aliases=('value',)))}"
    if operation == "keep_digits":
        return f"regexp_replace({expression}, '[^0-9]', '', 'g')"
    if operation == "keep_letters":
        return f"regexp_replace({expression}, '[^A-Za-zÀ-ÿ]', '', 'g')"
    if operation == "remove_accents":
        return f"strip_accents({expression})"
    if operation in {"remove_punctuation", "remove_symbols"}:
        return f"regexp_replace({expression}, '[^0-9A-Za-zÀ-ÿ\\s]', '', 'g')"
    if operation == "remove_spaces":
        return f"regexp_replace({expression}, '\\s+', '', 'g')"
    if operation == "pad_left":
        return f"lpad({expression}, {_count_param(transform)}, {quote_literal(_fill_param(transform))})"
    if operation == "pad_right":
        return f"rpad({expression}, {_count_param(transform)}, {quote_literal(_fill_param(transform))})"
    if operation == "take_first":
        return f"left({expression}, {_count_param(transform)})"
    if operation == "take_last":
        return f"right({expression}, {_count_param(transform)})"
    if operation == "remove_first":
        return f"substring({expression}, {_count_param(transform) + 1})"
    if operation == "remove_last":
        count = _count_param(transform)
        return f"CASE WHEN length({expression}) > {count} THEN left({expression}, length({expression}) - {count}) ELSE '' END"
    if operation == "extract_before":
        separator = _text_param(transform, "text", aliases=("value", "separator"))
        return f"CASE WHEN instr({expression}, {quote_literal(separator)}) > 0 THEN split_part({expression}, {quote_literal(separator)}, 1) ELSE {expression} END"
    if operation == "extract_after":
        separator = _text_param(transform, "text", aliases=("value", "separator"))
        return f"CASE WHEN instr({expression}, {quote_literal(separator)}) > 0 THEN substring({expression}, instr({expression}, {quote_literal(separator)}) + length({quote_literal(separator)})) ELSE '' END"
    if operation == "default_if_blank":
        return f"coalesce(nullif(trim({expression}), ''), {quote_literal(_text_param(transform, 'text', aliases=('value', 'default')))})"
    if operation == "default_if_empty":
        return f"coalesce(nullif({expression}, ''), {quote_literal(_text_param(transform, 'text', aliases=('value', 'default')))})"
    if operation == "default_if_null":
        return f"coalesce({expression}, {quote_literal(_text_param(transform, 'text', aliases=('value', 'default')))})"
    if operation == "format_cpf":
        return _format_cpf_sql(expression)
    if operation == "format_cnpj":
        return _format_cnpj_sql(expression)
    if operation == "format_phone":
        return _format_phone_sql(expression)
    raise ConfigError(f"Unsupported derived column transform: {operation}")


def _format_cpf_sql(expression: str) -> str:
    digits = f"regexp_replace({expression}, '[^0-9]', '', 'g')"
    return (
        f"CASE WHEN length({digits}) = 11 THEN "
        f"substring({digits}, 1, 3) || '.' || substring({digits}, 4, 3) || '.' || "
        f"substring({digits}, 7, 3) || '-' || substring({digits}, 10, 2) ELSE {digits} END"
    )


def _format_cnpj_sql(expression: str) -> str:
    digits = f"regexp_replace({expression}, '[^0-9]', '', 'g')"
    return (
        f"CASE WHEN length({digits}) = 14 THEN "
        f"substring({digits}, 1, 2) || '.' || substring({digits}, 3, 3) || '.' || "
        f"substring({digits}, 6, 3) || '/' || substring({digits}, 9, 4) || '-' || substring({digits}, 13, 2) "
        f"ELSE {digits} END"
    )


def _format_phone_sql(expression: str) -> str:
    digits = f"regexp_replace({expression}, '[^0-9]', '', 'g')"
    return (
        f"CASE WHEN length({digits}) = 11 THEN '(' || substring({digits}, 1, 2) || ') ' || "
        f"substring({digits}, 3, 5) || '-' || substring({digits}, 8, 4) "
        f"WHEN length({digits}) = 10 THEN '(' || substring({digits}, 1, 2) || ') ' || "
        f"substring({digits}, 3, 4) || '-' || substring({digits}, 7, 4) ELSE {digits} END"
    )


def _position_index(
    items: list[ProjectionItem],
    position: DerivedColumnPosition,
    schema_columns: dict[str, str],
    selected_columns: list[str],
    output_columns: list[str],
    case_insensitive_columns: bool,
) -> int:
    if position.mode == "append":
        return len(items)
    target = position.target or ""
    target_output = target if target in [item.output_name for item in items] else None
    if target_output is None:
        try:
            target_source = _resolve_column(schema_columns, target, case_insensitive_columns)
        except FilterValidationError as exc:
            raise FilterValidationError(f"Derived column position target '{target}' was not found.") from exc
        target_output = _source_output_name(target_source, selected_columns, output_columns)
    if target_output is None:
        raise FilterValidationError(f"Derived column position target '{target}' is not in the output columns.")
    for index, item in enumerate(items):
        if item.output_name == target_output:
            return index if position.mode == "before" else index + 1
    raise FilterValidationError(f"Derived column position target '{target}' was not found.")


def _source_output_name(source: str, selected_columns: list[str], output_columns: list[str]) -> str | None:
    for selected, output in zip(selected_columns, output_columns, strict=True):
        if selected == source:
            return output
    return None


def _resolve_column(columns: dict[str, str], requested: str, case_insensitive: bool) -> str:
    if requested in columns:
        return columns[requested]
    if case_insensitive:
        matches = [actual for actual in columns.values() if actual.lower() == requested.lower()]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise FilterValidationError(f"Column '{requested}' is ambiguous under case-insensitive matching.")
    raise FilterValidationError(f"Missing column '{requested}'.")


def _excel_formula_builder(transforms: list[TransformSpec], source_index: int) -> Callable[[int], str] | None:
    if not transforms:
        return None
    if any(transform.operation not in _EXCEL_FORMULA_OPERATIONS for transform in transforms):
        return None

    def build(row_index: int) -> str:
        expression = xl_rowcol_to_cell(row_index, source_index)
        for transform in transforms:
            expression = _apply_transform_excel(expression, transform)
        return f"={expression}"

    return build


_EXCEL_FORMULA_OPERATIONS = {
    "replace_text",
    "uppercase",
    "lowercase",
    "title_case",
    "trim",
    "remove_extra_spaces",
    "add_prefix",
    "add_suffix",
    "remove_spaces",
    "default_if_blank",
    "default_if_empty",
    "default_if_null",
}


def _apply_transform_excel(expression: str, transform: TransformSpec) -> str:
    operation = transform.operation
    if operation == "replace_text":
        old = _excel_string(_text_param(transform, "old", aliases=("find", "from")))
        new = _excel_string(_text_param(transform, "new", aliases=("replace", "to", "with")))
        return f"SUBSTITUTE({expression},{old},{new})"
    if operation == "uppercase":
        return f"UPPER({expression})"
    if operation == "lowercase":
        return f"LOWER({expression})"
    if operation == "title_case":
        return f"PROPER({expression})"
    if operation in {"trim", "remove_extra_spaces"}:
        return f"TRIM({expression})"
    if operation == "add_prefix":
        return f"{_excel_string(_text_param(transform, 'text', aliases=('value',)))}&{expression}"
    if operation == "add_suffix":
        return f"{expression}&{_excel_string(_text_param(transform, 'text', aliases=('value',)))}"
    if operation == "remove_spaces":
        return f"SUBSTITUTE({expression},\" \",\"\")"
    if operation in {"default_if_blank", "default_if_empty", "default_if_null"}:
        default = _excel_string(_text_param(transform, "text", aliases=("value", "default")))
        return f"IF(TRIM({expression})=\"\",{default},{expression})"
    raise ConfigError(f"Unsupported Excel formula transform: {operation}")


def _excel_string(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _required_text(transform: TransformSpec, key: str, *, aliases: tuple[str, ...] = ()) -> None:
    _text_param(transform, key, aliases=aliases)


def _required_count(transform: TransformSpec) -> None:
    _count_param(transform)


def _text_param(transform: TransformSpec, key: str, *, aliases: tuple[str, ...] = ()) -> str:
    for name in (key, *aliases):
        value = transform.params.get(name)
        if value is not None and str(value) != "":
            return str(value)
    names = ", ".join((key, *aliases))
    raise ConfigError(f"Transform '{transform.operation}' requires one of: {names}.")


def _count_param(transform: TransformSpec) -> int:
    raw = transform.params.get("count", transform.params.get("n", transform.params.get("width")))
    try:
        count = int(raw)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Transform '{transform.operation}' requires a positive count.") from exc
    if count < 1:
        raise ConfigError(f"Transform '{transform.operation}' requires a positive count.")
    return count


def _fill_param(transform: TransformSpec) -> str:
    fill = str(transform.params.get("fill") or transform.params.get("char") or " ")
    return fill[:1] or " "


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _affix_before(prefix: str, separator: str) -> str:
    if not prefix:
        return ""
    if separator and not prefix.endswith(separator):
        return f"{prefix}{separator}"
    return prefix


def _affix_after(suffix: str, separator: str) -> str:
    if not suffix:
        return ""
    if separator and not suffix.startswith(separator):
        return f"{separator}{suffix}"
    return suffix
