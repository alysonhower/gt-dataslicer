import pytest

from gt_dataslicer.exceptions import ConfigError
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


def test_visual_filter_builder_rejects_incomplete_value_rows() -> None:
    with pytest.raises(ConfigError, match="STATUS") as exc_info:
        build_filter_expression(
            {
                "combine": "and",
                "conditions": [
                    {"column": "STATUS", "operator": "equals", "value": ""},
                    {"column": "CPF", "operator": "is_not_null"},
                ],
            }
        )
    assert exc_info.value.code == "visual_filter_missing_value"
    assert exc_info.value.context == {"column": "STATUS", "reason": "a value", "field": "value"}


def test_visual_filter_builder_rejects_malformed_condition_payloads_with_structured_errors() -> None:
    with pytest.raises(ConfigError, match="conditions must be a list") as conditions_info:
        build_filter_expression({"conditions": {"column": "STATUS"}})

    assert conditions_info.value.code == "visual_filter_conditions_type"
    assert conditions_info.value.context == {}

    with pytest.raises(ConfigError, match="condition must be an object") as condition_info:
        build_filter_expression({"conditions": ["STATUS = ATIVO"]})

    assert condition_info.value.code == "visual_filter_condition_type"
    assert condition_info.value.context == {}


def test_visual_filter_builder_rejects_unknown_operator_with_structured_error() -> None:
    with pytest.raises(ConfigError, match="Unsupported visual filter operator") as exc_info:
        build_filter_expression({"conditions": [{"column": "STATUS", "operator": "near", "value": "ATIVO"}]})

    assert exc_info.value.code == "visual_filter_operator"
    assert exc_info.value.context == {"operator": "near"}


def test_visual_filter_builder_rejects_incomplete_between_rows() -> None:
    with pytest.raises(ConfigError, match="between") as exc_info:
        build_filter_expression(
            {
                "conditions": [
                    {"column": "DATA", "operator": "between", "value": "2024-01-01", "value2": ""},
                ],
            }
        )
    assert exc_info.value.code == "visual_filter_missing_value"
    assert exc_info.value.context == {"column": "DATA", "reason": "both values for between", "field": "value2"}


def test_visual_filter_builder_rejects_empty_membership_values() -> None:
    with pytest.raises(ConfigError, match="at least one value") as exc_info:
        build_filter_expression(
            {
                "conditions": [
                    {"column": "STATUS", "operator": "in", "value": ""},
                ],
            }
        )
    assert exc_info.value.code == "membership_empty"


def test_visual_filter_builder_rejects_invalid_membership_values_shape() -> None:
    with pytest.raises(ConfigError, match="IN values") as exc_info:
        build_filter_expression(
            {
                "conditions": [
                    {"column": "STATUS", "operator": "in", "values": {"bad": "shape"}},
                ],
            }
        )

    assert exc_info.value.code == "visual_filter_values_type"
    assert exc_info.value.context == {}


def test_visual_filter_builder_rejects_invalid_typed_literals_with_structured_errors() -> None:
    with pytest.raises(ConfigError, match="Expected boolean literal") as bool_info:
        build_filter_expression(
            {
                "conditions": [
                    {"column": "ATIVO", "operator": "equals", "value": "maybe", "value_type": "boolean"},
                ],
            }
        )

    assert bool_info.value.code == "visual_filter_boolean_literal"
    assert bool_info.value.context == {"value": "maybe"}

    with pytest.raises(ConfigError, match="Expected decimal literal") as decimal_info:
        build_filter_expression(
            {
                "conditions": [
                    {"column": "VALOR", "operator": "gt", "value": "abc", "value_type": "number"},
                ],
            }
        )

    assert decimal_info.value.code == "visual_filter_decimal_literal"
    assert decimal_info.value.context == {"value": "abc"}


def test_visual_filter_builder_defaults_missing_value_type_to_text() -> None:
    expression = build_filter_expression(
        {
            "conditions": [
                {"column": "CPF", "operator": "equals", "value": "00123"},
            ],
        }
    )

    assert expression == '[CPF] = "00123"'
