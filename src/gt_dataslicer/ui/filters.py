"""Helpers for converting visual UI filters into the existing DSL."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re
from typing import Any

from ..exceptions import ConfigError


_NUMERIC_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)")

_OPERATOR_ALIASES = {
    "equals": "equals",
    "igual": "equals",
    "not_equals": "not_equals",
    "diferente": "not_equals",
    "gt": "gt",
    "maior": "gt",
    "gte": "gte",
    "maior_igual": "gte",
    "lt": "lt",
    "menor": "lt",
    "lte": "lte",
    "menor_igual": "lte",
    "in": "in",
    "em": "in",
    "not_in": "not_in",
    "nao_em": "not_in",
    "between": "between",
    "entre": "between",
    "contains": "contains",
    "contem": "contains",
    "starts_with": "starts_with",
    "comeca_com": "starts_with",
    "ends_with": "ends_with",
    "termina_com": "ends_with",
    "regex": "regex",
    "is_null": "is_null",
    "nulo": "is_null",
    "is_not_null": "is_not_null",
    "nao_nulo": "is_not_null",
    "is_empty": "is_empty",
    "vazio": "is_empty",
    "is_not_empty": "is_not_empty",
    "nao_vazio": "is_not_empty",
    "is_blank": "is_blank",
    "branco": "is_blank",
    "is_not_blank": "is_not_blank",
    "nao_branco": "is_not_blank",
}

_NO_VALUE_OPERATORS = {"is_null", "is_not_null", "is_empty", "is_not_empty", "is_blank", "is_not_blank"}
_VALUE_OPERATORS = {
    "equals",
    "not_equals",
    "gt",
    "gte",
    "lt",
    "lte",
    "contains",
    "starts_with",
    "ends_with",
    "regex",
}


def build_filter_expression(filters_payload: dict[str, Any] | None) -> str:
    """Build a DSL expression from a raw or visual filter payload."""

    payload = filters_payload or {}
    mode = str(payload.get("mode") or "visual").strip().lower()
    if mode == "raw":
        return str(payload.get("raw") or payload.get("raw_filter") or "").strip()

    conditions = payload.get("conditions") or []
    if not isinstance(conditions, list):
        raise ConfigError("Visual filter conditions must be a list.")

    fragments = [condition_to_expression(condition) for condition in conditions if _has_condition_value(condition)]
    if not fragments:
        return ""

    combine = str(payload.get("combine") or "and").strip().lower()
    joiner = " OU " if combine == "or" else " E "
    if len(fragments) == 1:
        return fragments[0]
    return joiner.join(f"({fragment})" for fragment in fragments)


def condition_to_expression(condition: dict[str, Any]) -> str:
    if not isinstance(condition, dict):
        raise ConfigError("Visual filter condition must be an object.")
    column = str(condition.get("column") or "").strip()
    if not column:
        raise ConfigError("Visual filter condition is missing a column.")
    operator = _normalize_operator(condition.get("operator"))
    column_sql = quote_column(column)
    value_type = str(condition.get("value_type") or condition.get("valueType") or "string").strip().lower()

    if operator == "equals":
        return f"{column_sql} = {_literal(condition.get('value'), value_type=value_type)}"
    if operator == "not_equals":
        return f"{column_sql} != {_literal(condition.get('value'), value_type=value_type)}"
    if operator == "gt":
        return f"{column_sql} > {_literal(condition.get('value'), value_type=value_type)}"
    if operator == "gte":
        return f"{column_sql} >= {_literal(condition.get('value'), value_type=value_type)}"
    if operator == "lt":
        return f"{column_sql} < {_literal(condition.get('value'), value_type=value_type)}"
    if operator == "lte":
        return f"{column_sql} <= {_literal(condition.get('value'), value_type=value_type)}"
    if operator == "in":
        return _in_expression(column_sql, condition, value_type=value_type, negated=False)
    if operator == "not_in":
        return _in_expression(column_sql, condition, value_type=value_type, negated=True)
    if operator == "between":
        lower = _literal(condition.get("value"), value_type=value_type)
        upper = _literal(condition.get("value2"), value_type=value_type)
        return f"{column_sql} ENTRE {lower} E {upper}"
    if operator == "contains":
        return f"{column_sql} contém {_literal(condition.get('value'), value_type='string')}"
    if operator == "starts_with":
        return f"{column_sql} começa com {_literal(condition.get('value'), value_type='string')}"
    if operator == "ends_with":
        return f"{column_sql} termina com {_literal(condition.get('value'), value_type='string')}"
    if operator == "regex":
        return f"{column_sql} regex {_literal(condition.get('value'), value_type='string')}"
    if operator == "is_null":
        return f"{column_sql} É NULO"
    if operator == "is_not_null":
        return f"{column_sql} NÃO É NULO"
    if operator == "is_empty":
        return f"{column_sql} É VAZIO"
    if operator == "is_not_empty":
        return f"{column_sql} NÃO É VAZIO"
    if operator == "is_blank":
        return f"{column_sql} É BRANCO"
    if operator == "is_not_blank":
        return f"{column_sql} NÃO É BRANCO"
    raise ConfigError(f"Unsupported visual filter operator: {operator}")


def quote_column(column: str) -> str:
    escaped = column.replace("\\", "\\\\").replace("]", r"\]")
    return f"[{escaped}]"


def quote_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _normalize_operator(operator: object) -> str:
    normalized = str(operator or "").strip().lower().replace("-", "_").replace(" ", "_")
    result = _OPERATOR_ALIASES.get(normalized)
    if result is None:
        raise ConfigError(f"Unsupported visual filter operator: {operator}")
    return result


def _in_expression(column_sql: str, condition: dict[str, Any], *, value_type: str, negated: bool) -> str:
    lookup = str(condition.get("lookup") or "").strip()
    op = "NÃO EM" if negated else "EM"
    if lookup:
        lookup_ref = lookup if lookup.startswith("@") else f"@{lookup}"
        return f"{column_sql} {op} {lookup_ref}"

    values = condition.get("values")
    if values is None:
        values = _split_list_text(str(condition.get("value") or ""))
    if not isinstance(values, list):
        raise ConfigError("IN values must be a list or comma-separated text.")
    literal_list = ", ".join(_literal(value, value_type=value_type) for value in values)
    return f"{column_sql} {op} ({literal_list})"


def _literal(value: object, *, value_type: str) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value).strip()
    if value_type in {"int", "integer", "number", "decimal", "numeric"}:
        return _numeric_literal(text)
    if value_type in {"bool", "boolean"}:
        lowered = text.lower()
        if lowered in {"true", "false"}:
            return lowered
        raise ConfigError(f"Expected boolean literal, got {value!r}.")
    if value_type == "date":
        return f"date({quote_string(text)})"
    if value_type in {"datetime", "timestamp"}:
        return f"datetime({quote_string(text)})"
    if value_type in {"null", "none"}:
        return "null"
    if value_type == "auto":
        lowered = text.lower()
        if lowered == "null":
            return "null"
        if lowered in {"true", "false"}:
            return lowered
        if _NUMERIC_RE.fullmatch(text):
            return _numeric_literal(text)
    return quote_string(text)


def _numeric_literal(text: str) -> str:
    try:
        Decimal(text)
    except InvalidOperation as exc:
        raise ConfigError(f"Expected decimal literal, got {text!r}.") from exc
    return text


def _split_list_text(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _has_condition_value(condition: object) -> bool:
    if not isinstance(condition, dict):
        return False
    column = str(condition.get("column") or "").strip()
    if not column:
        return False
    try:
        operator = _normalize_operator(condition.get("operator"))
    except ConfigError:
        return False
    if operator in _NO_VALUE_OPERATORS:
        return True
    if operator == "between":
        return bool(str(condition.get("value") or "").strip() and str(condition.get("value2") or "").strip())
    if operator in {"in", "not_in"}:
        return bool(
            str(condition.get("lookup") or "").strip()
            or condition.get("values")
            or str(condition.get("value") or "").strip()
        )
    if operator in _VALUE_OPERATORS:
        return bool(str(condition.get("value") or "").strip())
    return False
