"""Compile filter AST nodes to safe DuckDB SQL fragments."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
import difflib
from functools import lru_cache
from typing import Any, NoReturn

import duckdb

from .ast import (
    BetweenPredicate,
    BooleanOp,
    Column,
    Comparison,
    Expr,
    InPredicate,
    Literal,
    LookupPredicate,
    Not,
    NullCheck,
    StringPredicate,
)
from .types import literal_to_type, string_date_type
from ..exceptions import FilterValidationError


TEXT_TYPES = {"string"}
NUMERIC_TYPES = {"int", "decimal"}
DATE_TYPES = {"date", "datetime"}
BOOL_TYPES = {"bool"}


@dataclass(slots=True)
class LookupBinding:
    name: str
    table_name: str
    value_column: str = "__value"


@dataclass(slots=True)
class CompileContext:
    columns: dict[str, str]
    column_types: dict[str, str] = field(default_factory=dict)
    lookups: dict[str, LookupBinding] = field(default_factory=dict)
    case_insensitive_columns: bool = False
    strict_values: bool = False


@dataclass(slots=True)
class CompiledFilter:
    sql: str
    params: list[Any] = field(default_factory=list)
    resolved_columns: set[str] = field(default_factory=set)


@dataclass(slots=True)
class _CompiledOperand:
    sql: str
    params: list[Any]
    type_name: str
    column_name: str | None = None


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def compile_filter(expr: Expr | None, context: CompileContext) -> CompiledFilter:
    compiler = _Compiler(context)
    if expr is None:
        return CompiledFilter("TRUE", [])
    compiled = compiler.compile_expr(expr)
    return CompiledFilter(compiled.sql, compiled.params, compiler.resolved_columns)


class _Compiler:
    def __init__(self, context: CompileContext) -> None:
        self.context = context
        self.resolved_columns: set[str] = set()

    def compile_expr(self, expr: Expr) -> _CompiledOperand:
        if isinstance(expr, BooleanOp):
            parts = [self.compile_expr(child) for child in expr.children]
            joiner = f" {expr.op.upper()} "
            sql = joiner.join(f"({part.sql})" for part in parts)
            return _CompiledOperand(sql, _merge_params(parts), "bool")
        if isinstance(expr, Not):
            inner = self.compile_expr(expr.expr)
            return _CompiledOperand(f"NOT ({inner.sql})", inner.params, "bool")
        if isinstance(expr, Comparison):
            return self._compile_comparison(expr)
        if isinstance(expr, InPredicate):
            return self._compile_in(expr)
        if isinstance(expr, LookupPredicate):
            return self._compile_lookup(expr)
        if isinstance(expr, BetweenPredicate):
            return self._compile_between(expr)
        if isinstance(expr, NullCheck):
            return self._compile_null_check(expr)
        if isinstance(expr, StringPredicate):
            return self._compile_string_predicate(expr)
        if isinstance(expr, (Column, Literal)):
            return self._compile_operand(expr)
        _raise_validation_error(
            f"Unsupported expression node: {type(expr).__name__}",
            code="unsupported_expression_node",
            node=type(expr).__name__,
        )

    def _compile_comparison(self, expr: Comparison) -> _CompiledOperand:
        op = "!=" if expr.op == "<>" else ("=" if expr.op == "==" else expr.op)
        if _is_null_literal(expr.left) or _is_null_literal(expr.right):
            return self._compile_null_comparison(expr.left, op, expr.right)
        desired_type = self._desired_type(expr.left, expr.right, op)
        left = self._compile_operand(expr.left, desired_type)
        right = self._compile_operand(expr.right, desired_type)
        return _CompiledOperand(f"{left.sql} {op} {right.sql}", [*left.params, *right.params], "bool")

    def _compile_null_comparison(self, left_expr: Expr, op: str, right_expr: Expr) -> _CompiledOperand:
        if op not in {"=", "!="}:
            _raise_validation_error(
                "NULL can only be compared with = or !=. Use IS NULL for clarity.",
                code="null_comparison_operator",
                operator=op,
            )

        left_is_null = _is_null_literal(left_expr)
        right_is_null = _is_null_literal(right_expr)
        if left_is_null and right_is_null:
            return _CompiledOperand("TRUE" if op == "=" else "FALSE", [], "bool")

        operand_expr = right_expr if left_is_null else left_expr
        operand = self._compile_operand(operand_expr)
        comparator = "IS NULL" if op == "=" else "IS NOT NULL"
        return _CompiledOperand(f"{operand.sql} {comparator}", operand.params, "bool")

    def _compile_between(self, expr: BetweenPredicate) -> _CompiledOperand:
        desired_type = self._desired_type(expr.left, expr.lower, "between", extra=expr.upper)
        left = self._compile_operand(expr.left, desired_type)
        lower = self._compile_operand(expr.lower, desired_type)
        upper = self._compile_operand(expr.upper, desired_type)
        params = [*left.params, *lower.params, *upper.params]
        return _CompiledOperand(f"{left.sql} BETWEEN {lower.sql} AND {upper.sql}", params, "bool")

    def _compile_in(self, expr: InPredicate) -> _CompiledOperand:
        if not expr.values:
            raise FilterValidationError("Membership filters require at least one value.", code="membership_empty")
        if any(value.value is None for value in expr.values):
            raise FilterValidationError(
                "Membership lists cannot contain NULL. Use IS NULL or combine it with another filter.",
                code="membership_null",
            )
        desired_type = self._desired_list_type(expr.left, expr.values)
        left = self._compile_operand(expr.left, desired_type)
        values = [self._compile_operand(value, desired_type) for value in expr.values]
        placeholders = ", ".join(value.sql for value in values)
        op = "NOT IN" if expr.negated else "IN"
        params = [*left.params, *_merge_params(values)]
        return _CompiledOperand(f"{left.sql} {op} ({placeholders})", params, "bool")

    def _compile_lookup(self, expr: LookupPredicate) -> _CompiledOperand:
        lookup = self.context.lookups.get(expr.lookup_name)
        if lookup is None:
            available = ", ".join(sorted(self.context.lookups)) or "(none)"
            _raise_validation_error(
                f"Unknown lookup '@{expr.lookup_name}'. Available lookups: {available}",
                code="unknown_lookup",
                lookup=expr.lookup_name,
                available=available,
            )
        left = self._compile_operand(expr.left, "string")
        op = "NOT IN" if expr.negated else "IN"
        sql = (
            f"{left.sql} {op} "
            f"(SELECT {quote_identifier(lookup.value_column)} FROM {quote_identifier(lookup.table_name)})"
        )
        return _CompiledOperand(sql, left.params, "bool")

    def _compile_null_check(self, expr: NullCheck) -> _CompiledOperand:
        left = self._compile_operand(expr.left)
        if expr.kind == "null":
            sql = f"{left.sql} IS NULL"
        elif expr.kind == "empty":
            text_sql = self._cast_sql(left.sql, "string")
            sql = f"({left.sql} IS NOT NULL AND {text_sql} = '')"
        else:
            text_sql = self._cast_sql(left.sql, "string")
            sql = f"({left.sql} IS NULL OR trim({text_sql}) = '')"
        if expr.negated:
            sql = f"NOT ({sql})"
        return _CompiledOperand(sql, left.params, "bool")

    def _compile_string_predicate(self, expr: StringPredicate) -> _CompiledOperand:
        left = self._compile_operand(expr.left, "string")
        right = self._compile_operand(expr.right, "string")
        if expr.op == "regex":
            pattern = _literal_value(expr.right)
            if not isinstance(pattern, str):
                _raise_validation_error(
                    "regex requires a string pattern.",
                    code="regex_pattern_type",
                    operator=expr.op,
                )
            _validate_duckdb_regex(pattern)
            return _CompiledOperand(
                f"regexp_matches({left.sql}, {right.sql})",
                [*left.params, *right.params],
                "bool",
            )

        if not isinstance(_literal_value(expr.right), str):
            _raise_validation_error(
                f"{expr.op.replace('_', ' ')} requires a string literal.",
                code="string_literal_required",
                operator=expr.op,
            )
        if expr.op == "contains":
            params = [*left.params, *[_escape_like_param(param) for param in right.params]]
            return _CompiledOperand(f"{left.sql} LIKE '%' || {right.sql} || '%' ESCAPE '\\'", params, "bool")
        if expr.op == "starts_with":
            params = [*left.params, *[_escape_like_param(param) for param in right.params]]
            return _CompiledOperand(f"{left.sql} LIKE {right.sql} || '%' ESCAPE '\\'", params, "bool")
        if expr.op == "ends_with":
            params = [*left.params, *[_escape_like_param(param) for param in right.params]]
            return _CompiledOperand(f"{left.sql} LIKE '%' || {right.sql} ESCAPE '\\'", params, "bool")
        _raise_validation_error(
            f"Unsupported string operator: {expr.op}",
            code="unsupported_string_operator",
            operator=expr.op,
        )

    def _compile_operand(self, expr: Expr, desired_type: str | None = None) -> _CompiledOperand:
        if isinstance(expr, Column):
            actual = self._resolve_column(expr.name)
            configured_type = self.context.column_types.get(actual, "string")
            type_name = desired_type or configured_type
            sql = quote_identifier(actual)
            if desired_type is not None:
                sql = self._cast_sql(sql, desired_type)
            self.resolved_columns.add(actual)
            return _CompiledOperand(sql, [], type_name, actual)
        if isinstance(expr, Literal):
            type_name = desired_type or literal_to_type(expr)
            value = self._coerce_literal(expr, type_name)
            return _CompiledOperand("?", [value], type_name)
        _raise_validation_error(
            f"Expected a column or literal, got {type(expr).__name__}.",
            code="operand_type",
            node=type(expr).__name__,
        )

    def _resolve_column(self, requested: str) -> str:
        if requested in self.context.columns:
            return self.context.columns[requested]
        if self.context.case_insensitive_columns:
            matches = [actual for key, actual in self.context.columns.items() if key.lower() == requested.lower()]
            if len(matches) == 1:
                return matches[0]
            if len(matches) > 1:
                raise FilterValidationError(
                    f"Column '{requested}' is ambiguous under case-insensitive matching.",
                    code="ambiguous_column",
                    context={"column": requested},
                )
        suggestions = difflib.get_close_matches(requested, list(self.context.columns.values()), n=3)
        hint = f" Did you mean: {', '.join(suggestions)}?" if suggestions else ""
        raise FilterValidationError(
            f"Missing column '{requested}'.{hint}",
            code="missing_column",
            context={"column": requested, "suggestions": suggestions},
        )

    def _desired_type(self, left: Expr, right: Expr, op: str, extra: Expr | None = None) -> str:
        candidates = [self._expr_type(left), self._expr_type(right)]
        if extra is not None:
            candidates.append(self._expr_type(extra))
        non_null = [candidate for candidate in candidates if candidate != "null"]
        if any(candidate in DATE_TYPES for candidate in non_null):
            return "datetime" if "datetime" in non_null else "date"
        if any(candidate in NUMERIC_TYPES for candidate in non_null):
            return "decimal"
        if any(candidate in BOOL_TYPES for candidate in non_null):
            return "bool"
        if op in {">", ">=", "<", "<=", "between"}:
            date_types = _string_literal_date_types(left, right, extra)
            if date_types:
                return "datetime" if "datetime" in date_types else "date"
        return "string"

    def _desired_list_type(self, left: Expr, values: tuple[Literal, ...]) -> str:
        candidates = [self._expr_type(left), *(literal_to_type(value) for value in values)]
        non_null = [candidate for candidate in candidates if candidate != "null"]
        if any(candidate in DATE_TYPES for candidate in non_null):
            return "datetime" if "datetime" in non_null else "date"
        if any(candidate in NUMERIC_TYPES for candidate in non_null):
            return "decimal"
        if any(candidate in BOOL_TYPES for candidate in non_null):
            return "bool"
        return "string"

    def _expr_type(self, expr: Expr | None, *, infer_string_dates: bool = False) -> str:
        if isinstance(expr, Literal):
            if infer_string_dates:
                inferred = string_date_type(expr.value)
                if inferred is not None:
                    return inferred
            return literal_to_type(expr)
        if isinstance(expr, Column):
            actual = self._resolve_column(expr.name)
            return self.context.column_types.get(actual, "string")
        return "string"

    def _cast_sql(self, sql: str, type_name: str) -> str:
        duck_type = {
            "string": "VARCHAR",
            "int": "BIGINT",
            "decimal": "DECIMAL(38,10)",
            "bool": "BOOLEAN",
            "date": "DATE",
            "datetime": "TIMESTAMP",
        }[type_name]
        cast_fn = "CAST" if self.context.strict_values else "TRY_CAST"
        return f"{cast_fn}({sql} AS {duck_type})"

    def _coerce_literal(self, literal: Literal, type_name: str) -> Any:
        value = literal.value
        if value is None:
            return None
        if type_name == "string":
            return str(value)
        if type_name == "decimal":
            if isinstance(value, Decimal):
                return value
            try:
                return Decimal(str(value))
            except Exception as exc:  # noqa: BLE001
                raise FilterValidationError(
                    f"Expected decimal literal, got {value!r}.",
                    code="literal_decimal",
                    context={"value": repr(value)},
                ) from exc
        if type_name == "int":
            try:
                return int(value)
            except Exception as exc:  # noqa: BLE001
                raise FilterValidationError(
                    f"Expected integer literal, got {value!r}.",
                    code="literal_integer",
                    context={"value": repr(value)},
                ) from exc
        if type_name == "bool":
            if isinstance(value, bool):
                return value
            if isinstance(value, str) and value.lower() in {"true", "false"}:
                return value.lower() == "true"
            _raise_validation_error(
                f"Expected boolean literal, got {value!r}.",
                code="literal_boolean",
                value=repr(value),
            )
        if type_name == "date":
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, date):
                return value
            if isinstance(value, str):
                try:
                    return date.fromisoformat(value)
                except ValueError as exc:
                    raise FilterValidationError(
                        f"Expected ISO date literal, got {value!r}.",
                        code="literal_iso_date",
                        context={"value": repr(value)},
                    ) from exc
        if type_name == "datetime":
            if isinstance(value, datetime):
                if value.tzinfo is not None and value.utcoffset() is not None:
                    raise FilterValidationError(
                        "Timezone-aware datetime literals are not supported. "
                        "Use a local ISO datetime without a timezone.",
                        code="timezone_aware_datetime",
                    )
                return value
            if isinstance(value, date):
                return datetime.combine(value, datetime.min.time())
            if isinstance(value, str):
                try:
                    parsed = datetime.fromisoformat(value)
                except ValueError as exc:
                    raise FilterValidationError(
                        f"Expected ISO datetime literal, got {value!r}.",
                        code="literal_iso_datetime",
                        context={"value": repr(value)},
                    ) from exc
                if parsed.tzinfo is not None and parsed.utcoffset() is not None:
                    raise FilterValidationError(
                        "Timezone-aware datetime literals are not supported. "
                        "Use a local ISO datetime without a timezone.",
                        code="timezone_aware_datetime",
                    )
                return parsed
        _raise_validation_error(
            f"Cannot coerce {value!r} to {type_name}.",
            code="literal_coerce_failed",
            value=repr(value),
            type=type_name,
        )


def _merge_params(parts: list[_CompiledOperand]) -> list[Any]:
    params: list[Any] = []
    for part in parts:
        params.extend(part.params)
    return params


def _literal_value(expr: Expr) -> object:
    if isinstance(expr, Literal):
        return expr.value
    return None


def _is_null_literal(expr: Expr) -> bool:
    return isinstance(expr, Literal) and expr.value is None


def _string_literal_date_types(*exprs: Expr | None) -> list[str]:
    date_types: list[str] = []
    for expr in exprs:
        if not isinstance(expr, Literal) or not isinstance(expr.value, str):
            continue
        inferred = string_date_type(expr.value)
        if inferred is None:
            return []
        date_types.append(inferred)
    return date_types


def _escape_like_param(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    return value.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")


@lru_cache(maxsize=512)
def _validate_duckdb_regex(pattern: str) -> None:
    try:
        connection = duckdb.connect(database=":memory:")
        try:
            connection.execute("SELECT regexp_matches('', ?)", [pattern]).fetchone()
        finally:
            connection.close()
    except duckdb.Error as exc:
        raise FilterValidationError(
            f"Invalid regex pattern for DuckDB: {exc}",
            code="invalid_regex_pattern",
            context={"reason": str(exc)},
        ) from exc


def _raise_validation_error(message: str, *, code: str, **context: Any) -> NoReturn:
    raise FilterValidationError(message, code=code, context=context)
