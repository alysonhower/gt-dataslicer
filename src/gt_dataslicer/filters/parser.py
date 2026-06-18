"""Parser for the filter DSL."""

from __future__ import annotations

import ast as py_ast
from datetime import date, datetime
from decimal import Decimal
from functools import lru_cache
from importlib import resources
import re
from typing import Iterable

from lark import Lark, Token, Transformer, UnexpectedInput, v_args
from lark.exceptions import VisitError

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
from ..exceptions import FilterSyntaxError


_EMPTY_MEMBERSHIP_RE = re.compile(r"\b(?:IN|EM)\s*\(\s*\)", re.IGNORECASE)


@lru_cache(maxsize=1)
def _parser() -> Lark:
    grammar = resources.files("gt_dataslicer.filters").joinpath("grammar.lark").read_text(encoding="utf-8")
    return Lark(grammar, parser="lalr", lexer="contextual", propagate_positions=True)


def parse_filter(expression: str) -> Expr:
    try:
        tree = _parser().parse(expression)
        return _FilterTransformer().transform(tree)
    except UnexpectedInput as exc:
        if _EMPTY_MEMBERSHIP_RE.search(expression):
            raise FilterSyntaxError("Membership filters require at least one value.", code="membership_empty") from exc
        context = exc.get_context(expression, span=60).strip()
        raise FilterSyntaxError(
            f"Invalid filter syntax at line {exc.line}, column {exc.column}: {context}",
            code="filter_syntax_at_location",
            context={"line": exc.line, "column": exc.column, "context": context},
        ) from exc
    except VisitError as exc:
        if isinstance(exc.orig_exc, ValueError):
            message = str(exc.orig_exc)
            code, context = _syntax_error_details(message)
            raise FilterSyntaxError(message, code=code, context=context) from exc
        raise
    except ValueError as exc:
        message = str(exc)
        code, context = _syntax_error_details(message)
        raise FilterSyntaxError(message, code=code, context=context) from exc


def combine_filters(filters: Iterable[str]) -> Expr | None:
    parsed = [parse_filter(text) for text in filters if text.strip()]
    if not parsed:
        return None
    if len(parsed) == 1:
        return parsed[0]
    return BooleanOp("and", tuple(parsed))


def _syntax_error_details(message: str) -> tuple[str | None, dict[str, object]]:
    if message == "Membership filters require at least one value.":
        return "membership_empty", {}
    if message == "Boolean expression is empty.":
        return "boolean_expression_empty", {}
    if message == "Expected a string literal.":
        return "string_literal_expected", {}
    if message == "date(...) requires a string literal.":
        return "date_string_literal", {}
    if message == "datetime(...) requires a string literal.":
        return "datetime_string_literal", {}
    if message.startswith("Invalid date literal: "):
        return "invalid_date_literal", {"value": message.removeprefix("Invalid date literal: ")}
    if message.startswith("Invalid datetime literal: "):
        return "invalid_datetime_literal", {"value": message.removeprefix("Invalid datetime literal: ")}
    if message.startswith("Timezone-aware datetime literals are not supported."):
        return "timezone_aware_datetime", {}
    return None, {}


def _fold_boolean(op: str, items: list[object]) -> Expr:
    children = [item for item in items if not isinstance(item, Token)]
    if not children:
        raise ValueError("Boolean expression is empty.")
    if len(children) == 1:
        return children[0]
    return BooleanOp(op, tuple(children))


def _decode_quoted(token: Token) -> str:
    return py_ast.literal_eval(str(token))


def _decode_string_literal(value: Literal | Token) -> str:
    if isinstance(value, Literal) and isinstance(value.value, str):
        return value.value
    if isinstance(value, Token):
        return _decode_quoted(value)
    raise ValueError("Expected a string literal.")


def _decode_wrapped_name(token: Token) -> str:
    text = str(token)
    inner = text[1:-1]
    return inner.replace(r"\]", "]").replace(r"\`", "`").replace(r"\\", "\\")


@v_args(inline=True)
class _FilterTransformer(Transformer):
    def or_expr(self, *items: object) -> Expr:
        return _fold_boolean("or", list(items))

    def and_expr(self, *items: object) -> Expr:
        return _fold_boolean("and", list(items))

    def not_expr(self, _not_token: Token, expr: Expr) -> Expr:
        return Not(expr)

    def grouped(self, expr: Expr) -> Expr:
        return expr

    def comparison(self, left: Expr, op: Token, right: Expr) -> Expr:
        return Comparison(left, str(op), right)

    def in_predicate(self, left: Expr, _in_token: Token, values: list[Literal]) -> Expr:
        return InPredicate(left, tuple(values), negated=False)

    def not_in_predicate(self, left: Expr, _not_token: Token, _in_token: Token, values: list[Literal]) -> Expr:
        return InPredicate(left, tuple(values), negated=True)

    def lookup_predicate(self, left: Expr, _in_token: Token, lookup_name: str) -> Expr:
        return LookupPredicate(left, lookup_name, negated=False)

    def not_lookup_predicate(self, left: Expr, _not_token: Token, _in_token: Token, lookup_name: str) -> Expr:
        return LookupPredicate(left, lookup_name, negated=True)

    def between_predicate(self, left: Expr, _between: Token, lower: Expr, _and: Token, upper: Expr) -> Expr:
        return BetweenPredicate(left, lower, upper)

    def is_predicate(self, left: Expr, _is: Token, kind: str) -> Expr:
        return NullCheck(left, kind, negated=False)

    def is_not_predicate(self, left: Expr, _is: Token, _not: Token, kind: str) -> Expr:
        return NullCheck(left, kind, negated=True)

    def is_pt_null_predicate(self, left: Expr, _token: Token) -> Expr:
        return NullCheck(left, "null", negated=False)

    def is_pt_empty_predicate(self, left: Expr, _token: Token) -> Expr:
        return NullCheck(left, "empty", negated=False)

    def is_pt_blank_predicate(self, left: Expr, _token: Token) -> Expr:
        return NullCheck(left, "blank", negated=False)

    def is_not_pt_null_predicate(self, left: Expr, _not: Token, _token: Token) -> Expr:
        return NullCheck(left, "null", negated=True)

    def is_not_pt_empty_predicate(self, left: Expr, _not: Token, _token: Token) -> Expr:
        return NullCheck(left, "empty", negated=True)

    def is_not_pt_blank_predicate(self, left: Expr, _not: Token, _token: Token) -> Expr:
        return NullCheck(left, "blank", negated=True)

    def contains_predicate(self, left: Expr, _token: Token, right: Expr) -> Expr:
        return StringPredicate(left, "contains", right)

    def starts_with_predicate(self, left: Expr, _token: Token, right: Expr) -> Expr:
        return StringPredicate(left, "starts_with", right)

    def ends_with_predicate(self, left: Expr, _token: Token, right: Expr) -> Expr:
        return StringPredicate(left, "ends_with", right)

    def regex_predicate(self, left: Expr, _token: Token, right: Expr) -> Expr:
        return StringPredicate(left, "regex", right)

    def literal_list(self, *items: Literal) -> list[Literal]:
        if not items:
            raise ValueError("Membership filters require at least one value.")
        return list(items)

    def lookup_ref(self, token: Token) -> str:
        return str(token)[1:]

    def string_lit(self, token: Token) -> Literal:
        return Literal(_decode_quoted(token), "string")

    def number_lit(self, token: Token) -> Literal:
        return Literal(Decimal(str(token)), "decimal")

    def true_lit(self, _token: Token) -> Literal:
        return Literal(True, "bool")

    def false_lit(self, _token: Token) -> Literal:
        return Literal(False, "bool")

    def null_lit(self, _token: Token) -> Literal:
        return Literal(None, "null")

    def date_literal(self, _func: Token, literal: Literal | Token) -> Literal:
        try:
            text = _decode_string_literal(literal)
        except ValueError as exc:
            raise ValueError("date(...) requires a string literal.") from exc
        try:
            return Literal(date.fromisoformat(text), "date")
        except ValueError as exc:
            raise ValueError(f"Invalid date literal: {text}") from exc

    def datetime_literal(self, _func: Token, literal: Literal | Token) -> Literal:
        try:
            value = _decode_string_literal(literal)
        except ValueError as exc:
            raise ValueError("datetime(...) requires a string literal.") from exc
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"Invalid datetime literal: {value}") from exc
        if parsed.tzinfo is not None and parsed.utcoffset() is not None:
            raise ValueError(
                "Timezone-aware datetime literals are not supported. "
                "Use a local ISO datetime without a timezone."
            )
        return Literal(parsed, "datetime")

    def bare_column(self, token: Token) -> Column:
        return Column(str(token))

    def bracket_column(self, token: Token) -> Column:
        return Column(_decode_wrapped_name(token))

    def backtick_column(self, token: Token) -> Column:
        return Column(_decode_wrapped_name(token))

    def null_kind(self, _token: Token) -> str:
        return "null"

    def empty_kind(self, _token: Token) -> str:
        return "empty"

    def blank_kind(self, _token: Token) -> str:
        return "blank"
