from datetime import date, datetime
from decimal import Decimal

import pytest

from gt_dataslicer.exceptions import FilterSyntaxError
from gt_dataslicer.filters.ast import (
    BetweenPredicate,
    BooleanOp,
    Column,
    Comparison,
    InPredicate,
    Literal,
    Not,
    NullCheck,
    StringPredicate,
)
from gt_dataslicer.filters.parser import parse_filter


def test_parse_boolean_precedence() -> None:
    expr = parse_filter('A = 1 OR NOT (B = "x" AND C IS NOT NULL)')
    assert isinstance(expr, BooleanOp)
    assert expr.op == "or"
    assert isinstance(expr.children[1], Not)


def test_parse_in_and_decimal() -> None:
    expr = parse_filter("CD_NATUREZA_OPERACAO NOT IN (14, 15)")
    assert isinstance(expr, InPredicate)
    assert expr.negated is True
    assert expr.values == (Literal(Decimal("14"), "decimal"), Literal(Decimal("15"), "decimal"))


def test_parse_bracketed_column_and_contains() -> None:
    expr = parse_filter('[Nome completo] contains "SILVA"')
    assert isinstance(expr, StringPredicate)
    assert expr.op == "contains"


def test_parse_null_check() -> None:
    expr = parse_filter("CPF IS NOT NULL")
    assert isinstance(expr, NullCheck)
    assert expr.negated is True


def test_parse_pt_br_boolean_logic_and_membership() -> None:
    expr = parse_filter("A = 1 E NÃO (B = 2 OU C NAO EM (3, 4))")

    assert isinstance(expr, BooleanOp)
    assert expr.op == "and"
    assert isinstance(expr.children[1], Not)


@pytest.mark.parametrize("expression", ["STATUS EM ('ATIVO')", "STATUS NAO EM ('ATIVO')", "STATUS NÃO EM ('ATIVO')"])
def test_parse_pt_br_membership_aliases(expression: str) -> None:
    expr = parse_filter(expression)

    assert isinstance(expr, InPredicate)
    assert expr.values == (Literal("ATIVO", "string"),)


def test_parse_pt_br_between_alias() -> None:
    expr = parse_filter('DATA_ADMISSAO ENTRE "2020-01-01" E "2023-12-31"')

    assert isinstance(expr, BetweenPredicate)


@pytest.mark.parametrize(
    ("expression", "op"),
    [
        ('NOME contem "SILVA"', "contains"),
        ('NOME contém "SILVA"', "contains"),
        ('NOME comeca com "JO"', "starts_with"),
        ('NOME começa com "JO"', "starts_with"),
        ('NOME termina com "SILVA"', "ends_with"),
    ],
)
def test_parse_pt_br_string_operator_aliases(expression: str, op: str) -> None:
    expr = parse_filter(expression)

    assert isinstance(expr, StringPredicate)
    assert expr.op == op


@pytest.mark.parametrize(
    ("expression", "kind", "negated"),
    [
        ("CPF E NULO", "null", False),
        ("CPF É NULO", "null", False),
        ("CPF NAO E NULO", "null", True),
        ("CPF NÃO É NULO", "null", True),
        ("CPF E VAZIO", "empty", False),
        ("CPF NÃO É VAZIO", "empty", True),
        ("CPF E BRANCO", "blank", False),
        ("CPF NAO E BRANCO", "blank", True),
    ],
)
def test_parse_pt_br_null_empty_blank_aliases(expression: str, kind: str, negated: bool) -> None:
    expr = parse_filter(expression)

    assert isinstance(expr, NullCheck)
    assert expr.kind == kind
    assert expr.negated is negated


@pytest.mark.parametrize("expression", ["[E] = 1", "[OU] = 1", "[NÃO] = 1", "`STATUS FINAL` = 'ATIVO'"])
def test_parse_keyword_like_columns_when_escaped(expression: str) -> None:
    expr = parse_filter(expression)

    assert isinstance(expr, Comparison)
    assert isinstance(expr.left, Column)


def test_parse_explicit_date_and_datetime_literals() -> None:
    date_expr = parse_filter('DATA = date("2024-01-31")')
    datetime_expr = parse_filter('TS = datetime("2024-01-31T10:30:00")')

    assert isinstance(date_expr, Comparison)
    assert date_expr.right == Literal(date(2024, 1, 31), "date")
    assert isinstance(datetime_expr, Comparison)
    assert datetime_expr.right == Literal(datetime(2024, 1, 31, 10, 30), "datetime")


def test_invalid_explicit_date_has_user_error() -> None:
    with pytest.raises(FilterSyntaxError, match="Invalid date literal"):
        parse_filter('DATA = date("2024-99-99")')


def test_invalid_syntax_has_user_error() -> None:
    with pytest.raises(FilterSyntaxError):
        parse_filter("A =")
