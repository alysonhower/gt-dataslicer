from gt_dataslicer.filters.parser import parse_filter
from gt_dataslicer.ui.filters import build_filter_expression, quote_column, quote_string


def test_visual_filter_builder_generates_pt_br_expression() -> None:
    expression = build_filter_expression(
        {
            "combine": "and",
            "conditions": [
                {"column": "CD_EMPRESA", "operator": "equals", "value": "1", "value_type": "number"},
                {"column": "ST_CONTRATO", "operator": "not_equals", "value": "P", "value_type": "string"},
                {
                    "column": "CD_NATUREZA_OPERACAO",
                    "operator": "not_in",
                    "value": "14, 15",
                    "value_type": "number",
                },
                {"column": "CD_MODALIDADE", "operator": "lte", "value": "13", "value_type": "number"},
            ],
        }
    )

    assert expression == (
        "([CD_EMPRESA] = 1) E ([ST_CONTRATO] != \"P\") E "
        "([CD_NATUREZA_OPERACAO] NÃO EM (14, 15)) E ([CD_MODALIDADE] <= 13)"
    )
    assert parse_filter(expression) is not None


def test_visual_filter_builder_supports_between_and_string_ops() -> None:
    expression = build_filter_expression(
        {
            "combine": "or",
            "conditions": [
                {
                    "column": "Data admissão",
                    "operator": "between",
                    "value": "2020-01-01",
                    "value2": "2023-12-31",
                    "value_type": "date",
                },
                {"column": "Nome completo", "operator": "contains", "value": "SILVA", "value_type": "string"},
            ],
        }
    )

    assert "[Data admissão] ENTRE date(\"2020-01-01\") E date(\"2023-12-31\")" in expression
    assert "[Nome completo] contém \"SILVA\"" in expression
    assert parse_filter(expression) is not None


def test_visual_filter_builder_escapes_columns_and_strings() -> None:
    assert quote_column("A]B") == r"[A\]B]"
    assert quote_string('A "quoted" value') == r'"A \"quoted\" value"'


def test_visual_filter_builder_supports_null_empty_blank_checks() -> None:
    expression = build_filter_expression(
        {
            "combine": "and",
            "conditions": [
                {"column": "CPF", "operator": "is_not_null"},
                {"column": "OBSERVACAO", "operator": "is_blank"},
            ],
        }
    )

    assert expression == "([CPF] NÃO É NULO) E ([OBSERVACAO] É BRANCO)"
    assert parse_filter(expression) is not None


def test_visual_filter_builder_ignores_incomplete_value_rows() -> None:
    expression = build_filter_expression(
        {
            "combine": "and",
            "conditions": [
                {"column": "STATUS", "operator": "equals", "value": ""},
                {"column": "CPF", "operator": "is_not_null"},
            ],
        }
    )

    assert expression == "[CPF] NÃO É NULO"
    assert parse_filter(expression) is not None


def test_visual_filter_builder_ignores_incomplete_between_rows() -> None:
    expression = build_filter_expression(
        {
            "conditions": [
                {"column": "DATA", "operator": "between", "value": "2024-01-01", "value2": ""},
            ],
        }
    )

    assert expression == ""


def test_visual_filter_builder_defaults_missing_value_type_to_text() -> None:
    expression = build_filter_expression(
        {
            "conditions": [
                {"column": "CPF", "operator": "equals", "value": "00123"},
            ],
        }
    )

    assert expression == '[CPF] = "00123"'
