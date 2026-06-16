"""Small localization helpers for user-facing CLI text."""

from __future__ import annotations

from contextvars import ContextVar
import re
from typing import Final


DEFAULT_LANGUAGE: Final = "pt-BR"
SUPPORTED_LANGUAGES: Final = ("pt-BR", "en-US")

_language: ContextVar[str] = ContextVar("gt_dataslicer_language", default=DEFAULT_LANGUAGE)


_MESSAGES: Final[dict[str, dict[str, str]]] = {
    "pt-BR": {
        "app.help": "Filtra arquivos CSV grandes e exporta as linhas correspondentes para CSV ou XLSX.",
        "command.inspect.help": "Inspeciona as colunas e tipos detectados no CSV.",
        "command.validate_filter.help": "Analisa e valida filtros sem exportar dados.",
        "command.filter.help": "Filtra um arquivo CSV e exporta as linhas correspondentes para CSV ou XLSX.",
        "option.lang": "Idioma da saída da CLI: pt-BR ou en-US. Deve ser usado antes do comando.",
        "option.typed_mode": "Permite que o DuckDB infira tipos das colunas do CSV.",
        "option.where": "Expressão de filtro. Repita para combinar filtros com E/AND.",
        "option.lookup": "Lookup no formato NOME=CAMINHO:COLUNA.",
        "option.type": "Tipo de coluna no formato COLUNA=TIPO.",
        "option.output": "Caminho de saída. O padrão é CSV, exceto quando .xlsx é usado.",
        "option.format": "Formato de saída: csv ou xlsx. Sobrescreve output_format da configuração.",
        "option.select": "Coluna a incluir. Pode ser repetida.",
        "option.rename": "Renomeia uma coluna de saída no formato ANTIGO=NOVO.",
        "option.sort": "Ordenação no formato COLUNA[:asc|desc].",
        "option.strict_values": "Falha em casts inválidos em vez de usar TRY_CAST.",
        "schema_title": "Esquema: {path}",
        "schema_column": "Coluna",
        "schema_duckdb_type": "Tipo DuckDB",
        "filter_valid": "Filtro válido.",
        "dry_run_succeeded": "Execução de teste concluída.",
        "export_complete": "Exportação concluída.",
        "rows_written": "{rows} linhas gravadas em {paths}",
        "report_written": "Relatório gravado em {path}",
        "error_prefix": "Erro:",
        "invalid_language": "Idioma inválido '{language}'. Use um destes valores: {supported}.",
        "warning.sort_temp_disk": "Ordenar saídas filtradas grandes pode exigir bastante espaço temporário em disco.",
    },
    "en-US": {
        "app.help": "Filter large CSV files and export matching rows to CSV or XLSX.",
        "command.inspect.help": "Inspect detected CSV columns and types.",
        "command.validate_filter.help": "Parse and validate filters without exporting.",
        "command.filter.help": "Filter a CSV file and export matching rows to CSV or XLSX.",
        "option.lang": "CLI output language: pt-BR or en-US. Must be used before the command.",
        "option.typed_mode": "Allow DuckDB to infer CSV column types.",
        "option.where": "Filter expression. Repeat to AND filters.",
        "option.lookup": "Lookup NAME=PATH:COLUMN.",
        "option.type": "Column type override, COLUMN=TYPE.",
        "option.output": "Output path. Defaults to CSV unless .xlsx is used.",
        "option.format": "Output format: csv or xlsx. Overrides config output_format.",
        "option.select": "Column to include, repeatable.",
        "option.rename": "Rename output column, OLD=NEW.",
        "option.sort": "Sort COLUMN[:asc|desc].",
        "option.strict_values": "Fail on invalid casts instead of using TRY_CAST.",
        "schema_title": "Schema: {path}",
        "schema_column": "Column",
        "schema_duckdb_type": "DuckDB Type",
        "filter_valid": "Filter is valid.",
        "dry_run_succeeded": "Dry run succeeded.",
        "export_complete": "Export complete.",
        "rows_written": "{rows} rows written to {paths}",
        "report_written": "Report written to {path}",
        "error_prefix": "Error:",
        "invalid_language": "Invalid language '{language}'. Use one of: {supported}.",
        "warning.sort_temp_disk": "Sorting large filtered outputs can require substantial temporary disk space.",
    },
}


_EXACT_PT: Final[dict[str, str]] = {
    "Config files must be YAML, JSON, or TOML.": "Arquivos de configuração devem ser YAML, JSON ou TOML.",
    "Config root must be an object/table.": "A raiz da configuração deve ser um objeto/tabela.",
    "Config contains presets; pass --preset to choose one.": (
        "A configuração contém presets; passe --preset para escolher um."
    ),
    "--preset was provided, but config has no presets table.": (
        "--preset foi informado, mas a configuração não possui tabela de presets."
    ),
    "Output path suffix must be .csv or .xlsx, or omit the suffix.": (
        "O sufixo do caminho de saída deve ser .csv, .xlsx, ou omitido."
    ),
    "--split-mode must be one of: sheets, files, both.": "--split-mode deve ser um de: sheets, files, both.",
    "--max-rows-per-sheet must be between 2 and 1048576.": (
        "--max-rows-per-sheet deve estar entre 2 e 1048576."
    ),
    "--sheets-per-file must be at least 1.": "--sheets-per-file deve ser pelo menos 1.",
    "--batch-size must be at least 1.": "--batch-size deve ser pelo menos 1.",
    "--rejects requires --store-rejects so DuckDB captures rejected rows.": (
        "--rejects requer --store-rejects para que o DuckDB capture linhas rejeitadas."
    ),
    "Boolean expression is empty.": "A expressão booleana está vazia.",
    "Expected a string literal.": "Era esperado um literal de texto.",
    "date(...) requires a string literal.": "date(...) requer um literal de texto.",
    "datetime(...) requires a string literal.": "datetime(...) requer um literal de texto.",
}


def set_language(language: str) -> None:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(invalid_language_message(language))
    _language.set(language)


def get_language() -> str:
    return _language.get()


def tr(key: str, **kwargs: object) -> str:
    language = get_language()
    template = _MESSAGES.get(language, {}).get(key) or _MESSAGES["en-US"].get(key) or key
    return template.format(**kwargs)


def invalid_language_message(language: str) -> str:
    return tr("invalid_language", language=language, supported=", ".join(SUPPORTED_LANGUAGES))


def localize_error_message(message: str) -> str:
    if get_language() == "en-US":
        return message

    exact = _EXACT_PT.get(message)
    if exact is not None:
        return exact

    syntax_match = re.match(r"Invalid filter syntax at line (\d+), column (\d+): (.*)", message, re.DOTALL)
    if syntax_match:
        line, column, context = syntax_match.groups()
        return f"Sintaxe de filtro inválida na linha {line}, coluna {column}: {context}"

    missing_column_match = re.match(r"Missing column '([^']+)'\.(?: Did you mean: (.*)\?)?", message)
    if missing_column_match:
        column, suggestions = missing_column_match.groups()
        suffix = f" Você quis dizer: {suggestions}?" if suggestions else ""
        return f"Coluna ausente '{column}'.{suffix}"

    output_conflict_match = re.match(
        r"Output format '([^']+)' conflicts with output path suffix '([^']+)'\.", message
    )
    if output_conflict_match:
        output_format, suffix = output_conflict_match.groups()
        return f"Formato de saída '{output_format}' conflita com o sufixo do caminho de saída '{suffix}'."

    ambiguous_match = re.match(r"Column '([^']+)' is ambiguous under case-insensitive matching\.", message)
    if ambiguous_match:
        return f"Coluna '{ambiguous_match.group(1)}' é ambígua com correspondência sem diferenciar maiúsculas."

    prefix_translations = {
        "Config file not found: ": "Arquivo de configuração não encontrado: ",
        "Could not parse config file ": "Não foi possível analisar o arquivo de configuração ",
        "Preset ": "Preset ",
        "Config key ": "Chave de configuração ",
        "Rename must use OLD=NEW syntax: ": "Rename deve usar a sintaxe ANTIGO=NOVO: ",
        "Rename must include both OLD and NEW: ": "Rename deve incluir ANTIGO e NOVO: ",
        "Sort column cannot be empty: ": "A coluna de ordenação não pode ficar vazia: ",
        "Lookup must use NAME=PATH:COLUMN syntax: ": "Lookup deve usar a sintaxe NOME=CAMINHO:COLUNA: ",
        "Lookup must include a column after the last colon: ": "Lookup deve incluir uma coluna após o último dois-pontos: ",
        "Lookup must include NAME, PATH, and COLUMN: ": "Lookup deve incluir NOME, CAMINHO e COLUNA: ",
        "Column type must use COLUMN=TYPE syntax: ": "Tipo de coluna deve usar a sintaxe COLUNA=TIPO: ",
        "Unsupported type ": "Tipo não suportado ",
        "Output format ": "Formato de saída ",
        "Select file not found: ": "Arquivo de seleção não encontrado: ",
        "Could not inspect CSV ": "Não foi possível inspecionar o CSV ",
        "DuckDB query failed: ": "Consulta DuckDB falhou: ",
        "Lookup ": "Lookup ",
        "Could not write rejects file ": "Não foi possível gravar o arquivo de rejeições ",
        "Invalid date literal: ": "Literal de data inválido: ",
        "Invalid datetime literal: ": "Literal de data/hora inválido: ",
        "Invalid regex pattern for DuckDB: ": "Padrão regex inválido para DuckDB: ",
        "Unknown lookup ": "Lookup desconhecido ",
        "Expected decimal literal, got ": "Literal decimal esperado; recebido ",
        "Expected integer literal, got ": "Literal inteiro esperado; recebido ",
        "Expected boolean literal, got ": "Literal booleano esperado; recebido ",
        "Expected ISO date literal, got ": "Literal de data ISO esperado; recebido ",
        "Expected ISO datetime literal, got ": "Literal de data/hora ISO esperado; recebido ",
        "Cannot coerce ": "Não foi possível converter ",
    }
    for prefix, replacement in prefix_translations.items():
        if message.startswith(prefix):
            return replacement + message.removeprefix(prefix)

    return message
