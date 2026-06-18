from decimal import Decimal

import pytest

from gt_dataslicer.exceptions import FilterValidationError
from gt_dataslicer.filters.ast import Column, Expr, Literal, StringPredicate
from gt_dataslicer.filters.compiler import CompileContext, compile_filter
from gt_dataslicer.filters.parser import parse_filter


def test_compile_uses_parameters_for_literals() -> None:
    expr = parse_filter('CD_EMPRESA = 1 AND ST_CONTRATO != "P"')
    compiled = compile_filter(expr, CompileContext(columns={"CD_EMPRESA": "CD_EMPRESA", "ST_CONTRATO": "ST_CONTRATO"}))
    assert compiled.sql.count("?") == 2
    assert compiled.params[0].is_finite()
    assert str(compiled.params[0]) == "1"
    assert compiled.params[1] == "P"


def test_compile_missing_column_suggests_error() -> None:
    expr = parse_filter("CD_EMPRES = 1")
    with pytest.raises(FilterValidationError, match="Missing column") as exc_info:
        compile_filter(expr, CompileContext(columns={"CD_EMPRESA": "CD_EMPRESA"}))
    assert exc_info.value.code == "missing_column"
    assert exc_info.value.context == {"column": "CD_EMPRES", "suggestions": ["CD_EMPRESA"]}


def test_compile_date_between_casts_column() -> None:
    expr = parse_filter('DATA_ADMISSAO BETWEEN "2020-01-01" AND "2023-12-31"')
    compiled = compile_filter(expr, CompileContext(columns={"DATA_ADMISSAO": "DATA_ADMISSAO"}))
    assert 'TRY_CAST("DATA_ADMISSAO" AS DATE)' in compiled.sql


def test_compile_reversed_date_like_ordering_casts_column() -> None:
    expr = parse_filter('"2020-01-01" < DATA_ADMISSAO')
    compiled = compile_filter(expr, CompileContext(columns={"DATA_ADMISSAO": "DATA_ADMISSAO"}))

    assert '? < TRY_CAST("DATA_ADMISSAO" AS DATE)' in compiled.sql


def test_compile_null_equality_uses_is_null() -> None:
    expr = parse_filter("A = null")
    compiled = compile_filter(expr, CompileContext(columns={"A": "A"}))
    assert compiled.sql == '"A" IS NULL'
    assert compiled.params == []


def test_compile_null_inequality_uses_is_not_null() -> None:
    expr = parse_filter("null != A")
    compiled = compile_filter(expr, CompileContext(columns={"A": "A"}))
    assert compiled.sql == '"A" IS NOT NULL'
    assert compiled.params == []


def test_compile_rejects_ordering_against_null() -> None:
    expr = parse_filter("A > null")
    with pytest.raises(FilterValidationError, match="NULL can only be compared") as exc_info:
        compile_filter(expr, CompileContext(columns={"A": "A"}))
    assert exc_info.value.code == "null_comparison_operator"
    assert exc_info.value.context == {"operator": ">"}


def test_compile_date_like_string_equality_stays_text_for_untyped_column() -> None:
    expr = parse_filter('CODE != "2024-01-31"')
    compiled = compile_filter(expr, CompileContext(columns={"CODE": "CODE"}))

    assert 'AS VARCHAR' in compiled.sql
    assert 'AS DATE' not in compiled.sql
    assert compiled.params == ["2024-01-31"]


def test_compile_regex_rejects_patterns_duckdb_cannot_execute() -> None:
    expr = parse_filter(r'NOME regex "(.)\\1"')

    with pytest.raises(FilterValidationError, match="Invalid regex pattern for DuckDB") as exc_info:
        compile_filter(expr, CompileContext(columns={"NOME": "NOME"}))
    assert exc_info.value.code == "invalid_regex_pattern"
    assert exc_info.value.context["reason"]


def test_compile_rejects_regex_pattern_that_is_not_text_with_structured_error() -> None:
    expr = parse_filter("NOME regex 1")

    with pytest.raises(FilterValidationError, match="regex requires a string pattern") as exc_info:
        compile_filter(expr, CompileContext(columns={"NOME": "NOME"}))

    assert exc_info.value.code == "regex_pattern_type"
    assert exc_info.value.context == {"operator": "regex"}


def test_compile_rejects_string_operator_literal_type_with_structured_error() -> None:
    expr = StringPredicate(Column("NOME"), "contains", Literal(Decimal("1"), "number"))

    with pytest.raises(FilterValidationError, match="contains requires a string literal") as exc_info:
        compile_filter(expr, CompileContext(columns={"NOME": "NOME"}))

    assert exc_info.value.code == "string_literal_required"
    assert exc_info.value.context == {"operator": "contains"}


def test_compile_rejects_unknown_lookup_with_structured_error() -> None:
    expr = parse_filter("A IN @ids")

    with pytest.raises(FilterValidationError, match="Unknown lookup") as exc_info:
        compile_filter(expr, CompileContext(columns={"A": "A"}))

    assert exc_info.value.code == "unknown_lookup"
    assert exc_info.value.context == {"lookup": "ids", "available": "(none)"}


def test_compile_rejects_null_inside_membership_list() -> None:
    expr = parse_filter("STATUS IN (null)")

    with pytest.raises(FilterValidationError, match="cannot contain NULL") as exc_info:
        compile_filter(expr, CompileContext(columns={"STATUS": "STATUS"}))
    assert exc_info.value.code == "membership_null"


def test_compile_rejects_timezone_aware_datetime_string_for_typed_column() -> None:
    expr = parse_filter('TS = "2024-01-01T12:30:00Z"')

    with pytest.raises(FilterValidationError, match="Timezone-aware datetime") as exc_info:
        compile_filter(expr, CompileContext(columns={"TS": "TS"}, column_types={"TS": "datetime"}))
    assert exc_info.value.code == "timezone_aware_datetime"


def test_compile_rejects_typed_literal_coercions_with_structured_errors() -> None:
    cases = [
        ("VALOR", "decimal", "literal_decimal"),
        ("ATIVO", "bool", "literal_boolean"),
        ("DATA", "date", "literal_iso_date"),
        ("TS", "datetime", "literal_iso_datetime"),
    ]

    for column, type_name, code in cases:
        expr = parse_filter(f'{column} = "not-valid"')

        with pytest.raises(FilterValidationError) as exc_info:
            compile_filter(expr, CompileContext(columns={column: column}, column_types={column: type_name}))

        assert exc_info.value.code == code
        assert exc_info.value.context == {"value": "'not-valid'"}


def test_compile_rejects_unsupported_expression_node_with_structured_error() -> None:
    with pytest.raises(FilterValidationError, match="Unsupported expression node") as exc_info:
        compile_filter(Expr(), CompileContext(columns={}))

    assert exc_info.value.code == "unsupported_expression_node"
    assert exc_info.value.context == {"node": "Expr"}
