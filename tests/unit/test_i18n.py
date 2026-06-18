import pytest

from gt_dataslicer.exceptions import (
    ConfigError,
    CsvReadError,
    ExportLimitError,
    FilterValidationError,
    InputReadError,
    QueryExecutionError,
    ZipPasswordRequiredError,
)
from gt_dataslicer.i18n import localize_error, set_language


@pytest.fixture(autouse=True)
def reset_language() -> None:
    set_language("pt-BR")
    yield
    set_language("pt-BR")


def test_structured_missing_column_localization_uses_context() -> None:
    set_language("pt-BR")
    error = FilterValidationError(
        "Legacy fallback text that should not be parsed.",
        code="missing_column",
        context={"column": "Status", "suggestions": ["STATUS"]},
    )

    assert localize_error(error) == "Coluna ausente 'Status'. Você quis dizer: STATUS?"


def test_structured_unknown_lookup_localization_uses_context() -> None:
    set_language("pt-BR")
    error = FilterValidationError(
        "Unknown lookup '@ids'. Available lookups: (none)",
        code="unknown_lookup",
        context={"lookup": "ids", "available": "(none)"},
    )

    assert localize_error(error) == "Lookup desconhecido '@ids'. Lookups disponíveis: (none)"


def test_structured_literal_coercion_localization_uses_context() -> None:
    set_language("pt-BR")
    error = FilterValidationError(
        "Expected decimal literal, got 'abc'.",
        code="literal_decimal",
        context={"value": "'abc'"},
    )

    assert localize_error(error) == "Literal decimal esperado; recebido 'abc'."


def test_structured_null_comparison_localization_uses_context() -> None:
    set_language("pt-BR")
    error = FilterValidationError(
        "NULL can only be compared with = or !=. Use IS NULL for clarity.",
        code="null_comparison_operator",
        context={"operator": ">"},
    )

    assert localize_error(error) == "NULL só pode ser comparado com = ou !=. Use É NULO para maior clareza."


def test_structured_parser_literal_localization_uses_context() -> None:
    set_language("pt-BR")
    error = FilterValidationError(
        "Invalid date literal: 2024-99-99",
        code="invalid_date_literal",
        context={"value": "2024-99-99"},
    )

    assert localize_error(error) == "Literal de data inválido: 2024-99-99"


def test_structured_boolean_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "spreadsheet_safe_csv must be true or false.",
        code="boolean_value",
        context={"key": "spreadsheet_safe_csv"},
    )

    assert localize_error(error) == "spreadsheet_safe_csv deve ser true ou false."


def test_structured_integer_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "max_rows_per_sheet must be an integer.",
        code="integer_value",
        context={"key": "max_rows_per_sheet"},
    )

    assert localize_error(error) == "max_rows_per_sheet deve ser um número inteiro."


def test_structured_lookup_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Lookup must include NAME, PATH, and COLUMN: ids=ids.csv:",
        code="lookup_missing_parts",
        context={"item": "ids=ids.csv:"},
    )

    assert localize_error(error) == "Lookup deve incluir NOME, CAMINHO e COLUNA: ids=ids.csv:"


def test_structured_config_string_list_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Config key 'lookup' must be a string or list of strings.",
        code="config_string_list",
        context={"key": "lookup"},
    )

    assert localize_error(error) == "Chave de configuração 'lookup' deve ser texto ou lista de textos."


def test_structured_config_file_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Config file not found: config.yaml",
        code="config_file_not_found",
        context={"path": "config.yaml"},
    )

    assert localize_error(error) == "Arquivo de configuração não encontrado: config.yaml"


def test_structured_preset_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Preset 'demo' was not found. Available presets: ativos",
        code="config_preset_not_found",
        context={"preset": "demo", "available": "ativos"},
    )

    assert localize_error(error) == "Preset 'demo' não foi encontrado. Presets disponíveis: ativos"


def test_structured_output_format_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "--format must be one of: csv, parquet, xlsx.",
        code="output_format_invalid",
        context={"source": "--format", "value": "pdf", "valid": "csv, parquet, xlsx"},
    )

    assert localize_error(error) == "--format deve ser um de: csv, parquet, xlsx."


def test_structured_visual_filter_operator_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Unsupported visual filter operator: near",
        code="visual_filter_operator",
        context={"operator": "near"},
    )

    assert localize_error(error) == "Operador de filtro visual não suportado: near"


def test_structured_sort_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Sort direction for 'STATUS' must be asc or desc.",
        code="sort_direction",
        context={"column": "STATUS", "direction": "sideways"},
    )

    assert localize_error(error) == "Direção de ordenação para 'STATUS' deve ser asc ou desc."


def test_structured_input_file_localization_uses_context() -> None:
    set_language("pt-BR")
    error = InputReadError(
        "Input file not found: dados.csv",
        code="input_file_not_found",
        context={"path": "dados.csv"},
    )

    assert localize_error(error) == "Arquivo de entrada não encontrado: dados.csv"


def test_structured_zip_password_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ZipPasswordRequiredError(
        "ZIP file requires a password: dados.zip",
        context={"path": "dados.zip"},
    )

    assert localize_error(error) == "O arquivo ZIP requer senha: dados.zip"


def test_structured_excel_sheet_localization_uses_context() -> None:
    set_language("pt-BR")
    error = InputReadError(
        "Excel sheet 'Dados' declares 2 rows and 2 columns (4 cells; limit: 3).",
        code="excel_sheet_too_large",
        context={"sheet": "Dados", "rows": 2, "columns": 2, "cells": 4, "limit": 3},
    )

    assert (
        localize_error(error)
        == "Aba 'Dados' declara 2 linhas e 2 colunas (4 células; limite: 3). "
        "Remova linhas ou colunas sem uso, salve o arquivo e tente novamente."
    )


def test_structured_excel_export_limit_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ExportLimitError(
        "Excel supports at most 16384 columns; selected 16385.",
        code="excel_column_limit",
        context={"limit": 16384, "selected": 16385},
    )

    assert localize_error(error) == "O Excel aceita no máximo 16384 colunas; 16385 foram selecionadas."


def test_structured_excel_string_limit_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ExportLimitError(
        "Excel supports at most 32767 characters in one cell; got 32768.",
        code="excel_string_limit",
        context={"limit": 32767, "length": 32768},
    )

    assert localize_error(error) == "O Excel aceita no máximo 32767 caracteres em uma célula; recebeu 32768."


def test_structured_engine_error_localization_uses_context() -> None:
    set_language("pt-BR")
    error = QueryExecutionError(
        "DuckDB query failed: conversion failed",
        code="duckdb_query_failed",
        context={"reason": "conversion failed"},
    )

    assert localize_error(error) == "Consulta DuckDB falhou: conversion failed"


def test_structured_rejects_write_localization_uses_context() -> None:
    set_language("pt-BR")
    error = CsvReadError(
        "Could not write rejects file rejeitados.csv: disk full",
        code="rejects_write_failed",
        context={"path": "rejeitados.csv", "reason": "disk full"},
    )

    assert localize_error(error) == "Não foi possível gravar o arquivo de rejeições rejeitados.csv: disk full"


def test_structured_runner_collision_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Output path would overwrite an input file: input.csv",
        code="output_overwrites_input",
        context={"path": "input.csv"},
    )

    assert localize_error(error) == "O caminho de saída sobrescreveria um arquivo de entrada: input.csv"


def test_structured_derived_source_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Derived column #1 requires a source column.",
        code="derived_source_required",
        context={"index": 1},
    )

    assert localize_error(error) == "Coluna derivada #1 precisa de uma coluna de origem."


def test_structured_derived_file_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Derived columns file not found: missing.yaml",
        code="derived_columns_file_not_found",
        context={"path": "missing.yaml"},
    )

    assert localize_error(error) == "Arquivo de colunas derivadas não encontrado: missing.yaml"


def test_structured_derived_transform_count_localization_uses_context() -> None:
    set_language("pt-BR")
    error = ConfigError(
        "Transform 'take_first' requires a positive count.",
        code="derived_transform_count_required",
        context={"operation": "take_first"},
    )

    assert localize_error(error) == "Transformação 'take_first' precisa de uma contagem positiva."


def test_structured_derived_position_target_localization_uses_context() -> None:
    set_language("pt-BR")
    error = FilterValidationError(
        "Derived column position target 'CPF' is not in the output columns.",
        code="derived_position_target_not_selected",
        context={"target": "CPF"},
    )

    assert localize_error(error) == "Coluna alvo da posição da coluna derivada 'CPF' não está na saída."


def test_structured_errors_preserve_english_message_in_en_us() -> None:
    set_language("en-US")
    error = FilterValidationError(
        "Missing column 'Status'.",
        code="missing_column",
        context={"column": "Status", "suggestions": []},
    )

    assert localize_error(error) == "Missing column 'Status'."
