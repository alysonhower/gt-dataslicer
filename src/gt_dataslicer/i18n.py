"""Small localization helpers for user-facing text."""

from __future__ import annotations

from contextvars import ContextVar
import re
from typing import Final


DEFAULT_LANGUAGE: Final = "pt-BR"
SUPPORTED_LANGUAGES: Final = ("pt-BR", "en-US")

_language: ContextVar[str] = ContextVar("gt_dataslicer_language", default=DEFAULT_LANGUAGE)


_MESSAGES: Final[dict[str, dict[str, str]]] = {
    "pt-BR": {
        "invalid_language": "Idioma inválido '{language}'. Use um destes valores: {supported}.",
        "warning.sort_temp_disk": "Ordenar saídas filtradas grandes pode exigir bastante espaço temporário em disco.",
        "error.summary_total_derived_text": "A coluna derivada '{column}' gera texto. Use em Agrupar por ou escolha uma coluna numérica para somar.",
        "ui.app_name": "DataSlicer",
        "ui.descriptor": "Powered by Grant Thornton Brasil",
        "ui.error.unexpected": "Não foi possível concluir a ação. Veja os detalhes técnicos ou tente novamente.",
        "ui.error.window_not_ready": "A janela ainda não está pronta para abrir este diálogo.",
        "ui.error.input_required": "Escolha um arquivo de entrada antes de continuar.",
        "ui.error.output_required": "Escolha a pasta de destino antes de continuar.",
        "ui.error.job_running": "Já existe uma exportação em andamento. Aguarde terminar antes de iniciar outra.",
        "ui.phase.queued": "Na fila",
        "ui.phase.queue": "Processando fila",
        "ui.phase.inspecting": "Lendo arquivo",
        "ui.phase.validating": "Validando filtro",
        "ui.phase.exporting": "Gerando saída",
        "ui.phase.finishing": "Finalizando",
        "ui.phase.done": "Concluído",
        "ui.phase.error": "Erro",
    },
    "en-US": {
        "invalid_language": "Invalid language '{language}'. Use one of: {supported}.",
        "warning.sort_temp_disk": "Sorting large filtered outputs can require substantial temporary disk space.",
        "error.summary_total_derived_text": "Derived column '{column}' creates text. Use it in Group by or choose a numeric column to sum.",
        "ui.app_name": "DataSlicer",
        "ui.descriptor": "Powered by Grant Thornton Brasil",
        "ui.error.unexpected": "The action could not be completed. Review technical details or try again.",
        "ui.error.window_not_ready": "The window is not ready to open this dialog yet.",
        "ui.error.input_required": "Choose an input file before continuing.",
        "ui.error.output_required": "Choose a destination folder before continuing.",
        "ui.error.job_running": "An export is already running. Wait for it to finish before starting another.",
        "ui.phase.queued": "Queued",
        "ui.phase.queue": "Processing queue",
        "ui.phase.inspecting": "Reading file",
        "ui.phase.validating": "Validating filter",
        "ui.phase.exporting": "Creating output",
        "ui.phase.finishing": "Finishing",
        "ui.phase.done": "Done",
        "ui.phase.error": "Error",
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
    "Output path suffix must be .csv, .xlsx, .parquet, or omit the suffix.": (
        "O sufixo do caminho de saída deve ser .csv, .xlsx, .parquet, ou omitido."
    ),
    "At least one input file is required.": "Informe pelo menos um arquivo de entrada.",
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


def messages_for(language: str | None = None, *, prefix: str | None = None) -> dict[str, str]:
    selected_language = language or get_language()
    if selected_language not in SUPPORTED_LANGUAGES:
        raise ValueError(invalid_language_message(selected_language))
    messages = _MESSAGES[selected_language]
    if prefix is None:
        return dict(messages)
    return {key: value for key, value in messages.items() if key.startswith(prefix)}


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
        "Could not inspect input ": "Não foi possível inspecionar o arquivo ",
        "Input file not found: ": "Arquivo de entrada não encontrado: ",
        "Input path is not a file: ": "O caminho de entrada não é um arquivo: ",
        "No supported input files were found.": "Nenhum arquivo de entrada compatível foi encontrado.",
        "ZIP file requires a password: ": "O arquivo ZIP requer senha: ",
        "Could not extract ZIP file ": "Não foi possível extrair o ZIP ",
        "Could not read Excel file ": "Não foi possível ler o Excel ",
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
