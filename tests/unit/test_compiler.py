import pytest

from gt_dataslicer.exceptions import FilterValidationError
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
    with pytest.raises(FilterValidationError, match="Missing column"):
        compile_filter(expr, CompileContext(columns={"CD_EMPRESA": "CD_EMPRESA"}))


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
    with pytest.raises(FilterValidationError, match="NULL can only be compared"):
        compile_filter(expr, CompileContext(columns={"A": "A"}))


def test_compile_raw_null_empty_blank_checks_stay_distinct() -> None:
    null_expr = parse_filter("A É NULO")
    empty_expr = parse_filter("A É VAZIO")
    blank_expr = parse_filter("A É BRANCO")

    context = CompileContext(columns={"A": "A"})
    assert compile_filter(null_expr, context).sql == '"A" IS NULL'
    assert compile_filter(empty_expr, context).sql == '("A" IS NOT NULL AND TRY_CAST("A" AS VARCHAR) = \'\')'
    assert compile_filter(blank_expr, context).sql == '("A" IS NULL OR trim(TRY_CAST("A" AS VARCHAR)) = \'\')'


def test_compile_date_like_string_equality_stays_text_for_untyped_column() -> None:
    expr = parse_filter('CODE != "2024-01-31"')
    compiled = compile_filter(expr, CompileContext(columns={"CODE": "CODE"}))

    assert 'AS VARCHAR' in compiled.sql
    assert 'AS DATE' not in compiled.sql
    assert compiled.params == ["2024-01-31"]


def test_compile_regex_rejects_patterns_duckdb_cannot_execute() -> None:
    expr = parse_filter(r'NOME regex "(.)\\1"')

    with pytest.raises(FilterValidationError, match="Invalid regex pattern for DuckDB"):
        compile_filter(expr, CompileContext(columns={"NOME": "NOME"}))
