"""Small localization helpers for user-facing CLI text."""

from __future__ import annotations

from contextvars import ContextVar
import re
from typing import Final

from .exceptions import DataSlicerError


DEFAULT_LANGUAGE: Final = "pt-BR"
SUPPORTED_LANGUAGES: Final = ("pt-BR", "en-US")

_language: ContextVar[str] = ContextVar("gt_dataslicer_language", default=DEFAULT_LANGUAGE)


_MESSAGES: Final[dict[str, dict[str, str]]] = {
    "pt-BR": {
        "app.help": "Filtra arquivos grandes e exporta as linhas correspondentes para CSV, XLSX ou Parquet.",
        "command.inspect.help": "Inspeciona as colunas e tipos detectados no arquivo.",
        "command.validate_filter.help": "Analisa e valida filtros sem exportar dados.",
        "command.filter.help": "Filtra um ou mais arquivos e exporta as linhas correspondentes para CSV, XLSX ou Parquet.",
        "command.ui.help": "Abre a tela visual do DataSlicer.",
        "option.lang": "Idioma da saída da CLI: pt-BR ou en-US. Use antes do comando.",
        "option.typed_mode": "Permite que o DuckDB infira tipos das colunas do CSV.",
        "option.where": "Expressão de filtro. Repita para combinar filtros com E/AND.",
        "option.lookup": "Lookup no formato NOME=CAMINHO:COLUNA.",
        "option.type": "Tipo de coluna no formato COLUNA=TIPO.",
        "option.output": "Caminho de saída. O padrão é CSV, exceto quando .xlsx ou .parquet é usado.",
        "option.format": "Formato de saída: csv, xlsx ou parquet. Sobrescreve output_format da configuração.",
        "option.derived_column": "Coluna derivada em JSON. Repita para adicionar mais de uma.",
        "option.output_name": "Nome de saída para cada arquivo da fila. Repita na mesma ordem dos arquivos resolvidos.",
        "option.select": "Coluna a incluir. Pode ser repetida.",
        "option.rename": "Renomeia uma coluna de saída no formato ANTIGO=NOVO.",
        "option.sort": "Ordenação no formato COLUNA[:asc|desc].",
        "option.summarize": "Gera arquivo de resumo do resultado.",
        "option.summary_only": "Executa apenas o resumo, sem exportar base filtrada.",
        "option.summary_group_by": "Colunas para agrupar o resumo (uma por linha).",
        "option.summary_totals": "Colunas para somar no resumo (uma por linha).",
        "option.strict_values": "Falha em casts inválidos em vez de usar TRY_CAST.",
        "option.spreadsheet_safe_csv": (
            "Protege CSVs que serão abertos em planilhas, prefixando textos que poderiam virar fórmulas."
        ),
        "schema_title": "Esquema: {path}",
        "schema_column": "Coluna",
        "schema_duckdb_type": "Tipo DuckDB",
        "filter_valid": "Filtro válido.",
        "dry_run_succeeded": "Execução de teste concluída.",
        "export_complete": "Exportação concluída.",
        "rows_written": "{rows} linhas gravadas em {paths}",
        "report_written": "Relatório gravado em {path}",
        "queue_failed": "{count} arquivo(s) não puderam ser processados.",
        "zip_password_prompt": "Senha do ZIP {path}:",
        "error_prefix": "Erro:",
        "invalid_language": "Idioma inválido '{language}'. Use um destes valores: {supported}.",
        "warning.sort_temp_disk": "Ordenar saídas filtradas grandes pode exigir bastante espaço temporário em disco.",
        "ui.app_name": "DataSlicer",
        "ui.descriptor": "Powered by Grant Thornton Brasil",
        "ui.error.unexpected": "Não foi possível concluir a ação. Veja os detalhes técnicos ou tente novamente.",
        "ui.error.window_not_ready": "A janela ainda não está pronta para abrir este diálogo.",
        "ui.error.input_required": "Escolha um arquivo de entrada antes de continuar.",
        "ui.error.config_required": "Escolha um arquivo de configuração antes de continuar.",
        "ui.error.unsupported_config_keys": (
            "Esta configuração usa opções que esta tela ainda não consegue editar com segurança: {keys}."
        ),
        "ui.error.output_required": "Escolha onde salvar o resultado antes de continuar.",
        "ui.error.job_running": "Já existe uma exportação em andamento. Aguarde terminar antes de iniciar outra.",
        "ui.error.overwrite_confirmation_required": (
            "Alguns arquivos de saída já existem. Confirme antes de substituir."
        ),
        "ui.error.zip_delete_confirmation_required": (
            "Confirme a exclusão do ZIP antes de iniciar uma execução que remove o arquivo original."
        ),
        "ui.warning.schema_mismatch": (
            "Alguns arquivos da fila têm colunas ou tipos diferentes do primeiro arquivo. "
            "A validação e a execução ainda verificarão cada arquivo."
        ),
        "ui.phase.queued": "Na fila",
        "ui.phase.inspecting": "Lendo o arquivo",
        "ui.phase.validating": "Validando o filtro",
        "ui.phase.exporting": "Gerando o arquivo",
        "ui.phase.finishing": "Finalizando",
        "ui.phase.done": "Concluído",
        "ui.phase.error": "Erro",
    },
    "en-US": {
        "app.help": "Filter large files and export matching rows to CSV, XLSX, or Parquet.",
        "command.inspect.help": "Inspect detected columns and types.",
        "command.validate_filter.help": "Parse and validate filters without exporting.",
        "command.filter.help": "Filter one or more files and export matching rows to CSV, XLSX, or Parquet.",
        "command.ui.help": "Open the DataSlicer visual interface.",
        "option.lang": "CLI output language: pt-BR or en-US. Use before the command.",
        "option.typed_mode": "Allow DuckDB to infer CSV column types.",
        "option.where": "Filter expression. Repeat to AND filters.",
        "option.lookup": "Lookup NAME=PATH:COLUMN.",
        "option.type": "Column type override, COLUMN=TYPE.",
        "option.output": "Output path. Defaults to CSV unless .xlsx or .parquet is used.",
        "option.format": "Output format: csv, xlsx, or parquet. Overrides config output_format.",
        "option.derived_column": "Derived column as JSON. Repeat to add more than one.",
        "option.output_name": "Output name for each queued file. Repeat in the same order as resolved inputs.",
        "option.select": "Column to include, repeatable.",
        "option.rename": "Rename output column, OLD=NEW.",
        "option.sort": "Sort COLUMN[:asc|desc].",
        "option.summarize": "Generate summary output for filtered rows.",
        "option.summary_only": "Only generate the summary, without exporting filtered rows.",
        "option.summary_group_by": "Columns to group the summary by (repeat per column).",
        "option.summary_totals": "Columns to total in the summary (repeat per column).",
        "option.strict_values": "Fail on invalid casts instead of using TRY_CAST.",
        "option.spreadsheet_safe_csv": (
            "Protect CSVs intended for spreadsheet apps by prefixing text that could become formulas."
        ),
        "schema_title": "Schema: {path}",
        "schema_column": "Column",
        "schema_duckdb_type": "DuckDB Type",
        "filter_valid": "Filter is valid.",
        "dry_run_succeeded": "Dry run succeeded.",
        "export_complete": "Export complete.",
        "rows_written": "{rows} rows written to {paths}",
        "report_written": "Report written to {path}",
        "queue_failed": "{count} file(s) could not be processed.",
        "zip_password_prompt": "ZIP password for {path}:",
        "error_prefix": "Error:",
        "invalid_language": "Invalid language '{language}'. Use one of: {supported}.",
        "warning.sort_temp_disk": "Sorting large filtered outputs can require substantial temporary disk space.",
        "ui.app_name": "DataSlicer",
        "ui.descriptor": "Powered by Grant Thornton Brasil",
        "ui.error.unexpected": "The action could not be completed. Review technical details or try again.",
        "ui.error.window_not_ready": "The window is not ready to open this dialog yet.",
        "ui.error.input_required": "Choose an input file before continuing.",
        "ui.error.config_required": "Choose a configuration file before continuing.",
        "ui.error.unsupported_config_keys": (
            "This configuration uses options this screen cannot safely edit yet: {keys}."
        ),
        "ui.error.output_required": "Choose where to save the result before continuing.",
        "ui.error.job_running": "An export is already running. Wait for it to finish before starting another.",
        "ui.error.overwrite_confirmation_required": (
            "Some output files already exist. Confirm before replacing them."
        ),
        "ui.error.zip_delete_confirmation_required": (
            "Confirm ZIP deletion before starting a run that removes the original archive."
        ),
        "ui.warning.schema_mismatch": (
            "Some queued files have columns or types that differ from the first file. "
            "Validation and execution will still check each file."
        ),
        "ui.phase.queued": "Queued",
        "ui.phase.inspecting": "Reading file",
        "ui.phase.validating": "Validating filter",
        "ui.phase.exporting": "Creating output file",
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
    "Membership filters require at least one value.": "Filtros de lista precisam de pelo menos um valor.",
    "Membership lists cannot contain NULL. Use IS NULL or combine it with another filter.": (
        "Listas de valores não podem conter NULL. Use É NULO ou combine com outro filtro."
    ),
    "Timezone-aware datetime literals are not supported. Use a local ISO datetime without a timezone.": (
        "Literais de data/hora com fuso horário não são compatíveis. Use uma data/hora ISO local sem fuso."
    ),
    "Visual filter condition is missing a column.": "A condição visual está sem coluna.",
    "Key-based deduplication requires at least one sort key.": (
        "Deduplicação por chave requer pelo menos uma coluna de ordenação."
    ),
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


def localize_error(error: Exception | str) -> str:
    if isinstance(error, DataSlicerError):
        structured = _localize_structured_error(error)
        if structured is not None:
            return structured
    return localize_error_message(str(error))


def _localize_structured_error(error: DataSlicerError) -> str | None:
    if get_language() == "en-US":
        return str(error)

    context = error.context
    if error.code == "filter_syntax_at_location":
        return (
            "Sintaxe de filtro inválida na linha "
            f"{context.get('line')}, coluna {context.get('column')}: {context.get('context')}"
        )
    if error.code == "boolean_expression_empty":
        return "A expressão booleana está vazia."
    if error.code == "string_literal_expected":
        return "Era esperado um literal de texto."
    if error.code == "date_string_literal":
        return "date(...) requer um literal de texto."
    if error.code == "datetime_string_literal":
        return "datetime(...) requer um literal de texto."
    if error.code == "invalid_date_literal":
        return f"Literal de data inválido: {context.get('value')}"
    if error.code == "invalid_datetime_literal":
        return f"Literal de data/hora inválido: {context.get('value')}"
    if error.code == "missing_column":
        column = context.get("column")
        suggestions = context.get("suggestions") or []
        if isinstance(suggestions, str):
            suggestions_text = suggestions
        else:
            suggestions_text = ", ".join(str(item) for item in suggestions)
        suffix = f" Você quis dizer: {suggestions_text}?" if suggestions_text else ""
        return f"Coluna ausente '{column}'.{suffix}"
    if error.code == "ambiguous_column":
        return f"Coluna '{context.get('column')}' é ambígua com correspondência sem diferenciar maiúsculas."
    if error.code == "output_format_suffix_conflict":
        return (
            f"Formato de saída '{context.get('output_format')}' conflita com o sufixo "
            f"do caminho de saída '{context.get('suffix')}'."
        )
    if error.code == "visual_filter_missing_value":
        reason = str(context.get("reason") or "")
        translated_reason = {
            "a value": "um valor",
            "both values for between": "os dois valores do intervalo",
        }.get(reason, reason)
        return f"A condição visual da coluna '{context.get('column')}' precisa de {translated_reason}."
    if error.code == "visual_filter_conditions_type":
        return "Condições do filtro visual devem ser uma lista."
    if error.code == "visual_filter_condition_type":
        return "Condição do filtro visual deve ser um objeto."
    if error.code == "visual_filter_missing_column":
        return "A condição visual está sem coluna."
    if error.code == "visual_filter_operator":
        return f"Operador de filtro visual não suportado: {context.get('operator')}"
    if error.code == "visual_filter_values_type":
        return "Valores de EM/IN devem ser uma lista ou texto separado por vírgulas."
    if error.code == "visual_filter_boolean_literal":
        return f"Literal booleano esperado; recebido {context.get('value')!r}."
    if error.code == "visual_filter_decimal_literal":
        return f"Literal decimal esperado; recebido {context.get('value')!r}."
    if error.code == "membership_empty":
        return "Filtros de lista precisam de pelo menos um valor."
    if error.code == "membership_null":
        return "Listas de valores não podem conter NULL. Use É NULO ou combine com outro filtro."
    if error.code == "unsupported_expression_node":
        return f"Nó de expressão não suportado: {context.get('node')}"
    if error.code == "null_comparison_operator":
        return "NULL só pode ser comparado com = ou !=. Use É NULO para maior clareza."
    if error.code == "unknown_lookup":
        return f"Lookup desconhecido '@{context.get('lookup')}'. Lookups disponíveis: {context.get('available')}"
    if error.code == "regex_pattern_type":
        return "regex requer um padrão de texto."
    if error.code == "string_literal_required":
        operator = str(context.get("operator") or "").replace("_", " ")
        return f"{operator} requer um literal de texto."
    if error.code == "unsupported_string_operator":
        return f"Operador de texto não suportado: {context.get('operator')}"
    if error.code == "operand_type":
        return f"Era esperada uma coluna ou literal; recebido {context.get('node')}."
    if error.code == "literal_decimal":
        return f"Literal decimal esperado; recebido {context.get('value')}."
    if error.code == "literal_integer":
        return f"Literal inteiro esperado; recebido {context.get('value')}."
    if error.code == "literal_boolean":
        return f"Literal booleano esperado; recebido {context.get('value')}."
    if error.code == "literal_iso_date":
        return f"Literal de data ISO esperado; recebido {context.get('value')}."
    if error.code == "literal_iso_datetime":
        return f"Literal de data/hora ISO esperado; recebido {context.get('value')}."
    if error.code == "literal_coerce_failed":
        return f"Não foi possível converter {context.get('value')} para {context.get('type')}."
    if error.code == "timezone_aware_datetime":
        return "Literais de data/hora com fuso horário não são compatíveis. Use uma data/hora ISO local sem fuso."
    if error.code == "invalid_regex_pattern":
        return f"Padrão regex inválido para DuckDB: {context.get('reason')}"
    if error.code == "boolean_value":
        return f"{context.get('key')} deve ser true ou false."
    if error.code == "integer_value":
        return f"{context.get('key')} deve ser um número inteiro."
    if error.code == "ui_config_required":
        return tr("ui.error.config_required")
    if error.code == "ui_input_required":
        return tr("ui.error.input_required")
    if error.code == "ui_output_required":
        return tr("ui.error.output_required")
    if error.code == "ui_unsupported_config_keys":
        return tr("ui.error.unsupported_config_keys", keys=context.get("keys"))
    if error.code == "ui_split_mode":
        return "split_mode deve ser sheets, files ou both."
    if error.code == "csv_options_type":
        return "csv_options deve ser um objeto."
    if error.code == "zip_delete_confirmation_required":
        return tr("ui.error.zip_delete_confirmation_required")
    if error.code == "config_boolean":
        return f"Chave de configuração '{context.get('key')}' deve ser true ou false."
    if error.code == "config_string_list":
        return f"Chave de configuração '{context.get('key')}' deve ser texto ou lista de textos."
    if error.code == "config_file_not_found":
        return f"Arquivo de configuração não encontrado: {context.get('path')}"
    if error.code == "config_file_type":
        return "Arquivos de configuração devem ser YAML, JSON ou TOML."
    if error.code == "config_file_parse":
        return f"Não foi possível analisar o arquivo de configuração {context.get('path')}: {context.get('reason')}"
    if error.code == "config_root_type":
        return "A raiz da configuração deve ser um objeto/tabela."
    if error.code == "config_preset_required":
        return "A configuração contém presets; passe --preset para escolher um."
    if error.code == "config_presets_missing":
        return "--preset foi informado, mas a configuração não possui tabela de presets."
    if error.code == "config_preset_not_found":
        return f"Preset '{context.get('preset')}' não foi encontrado. Presets disponíveis: {context.get('available')}"
    if error.code == "config_preset_type":
        return f"Preset '{context.get('preset')}' deve ser um objeto/tabela."
    if error.code == "rename_syntax":
        return f"Rename deve usar a sintaxe ANTIGO=NOVO: {context.get('item')}"
    if error.code == "rename_missing_parts":
        return f"Rename deve incluir ANTIGO e NOVO: {context.get('item')}"
    if error.code == "sort_empty_column":
        return f"A coluna de ordenação não pode ficar vazia: {context.get('item')}"
    if error.code == "sort_direction":
        return f"Direção de ordenação para '{context.get('column')}' deve ser asc ou desc."
    if error.code == "lookup_syntax":
        return f"Lookup deve usar a sintaxe NOME=CAMINHO:COLUNA: {context.get('item')}"
    if error.code == "lookup_missing_column":
        return f"Lookup deve incluir uma coluna após o último dois-pontos: {context.get('item')}"
    if error.code == "lookup_missing_parts":
        return f"Lookup deve incluir NOME, CAMINHO e COLUNA: {context.get('item')}"
    if error.code == "column_type_syntax":
        return f"Tipo de coluna deve usar a sintaxe COLUNA=TIPO: {context.get('item')}"
    if error.code == "unsupported_column_type":
        return (
            f"Tipo não suportado '{context.get('type')}' para coluna '{context.get('column')}'. "
            f"Tipos válidos: {context.get('valid')}"
        )
    if error.code == "output_format_type":
        return f"{context.get('source')} deve ser csv, xlsx ou parquet."
    if error.code == "output_format_invalid":
        return f"{context.get('source')} deve ser um de: {context.get('valid')}."
    if error.code == "output_suffix_invalid":
        return "O sufixo do caminho de saída deve ser .csv, .xlsx, .parquet, ou omitido."
    if error.code == "select_file_not_found":
        return f"Arquivo de seleção não encontrado: {context.get('path')}"
    if error.code == "split_mode":
        return "--split-mode deve ser um de: sheets, files, both."
    if error.code == "max_rows_per_sheet":
        return "--max-rows-per-sheet deve estar entre 2 e 1048576."
    if error.code == "sheets_per_file":
        return "--sheets-per-file deve ser pelo menos 1."
    if error.code == "batch_size":
        return "--batch-size deve ser pelo menos 1."
    if error.code == "rejects_requires_store_rejects":
        return "--rejects requer --store-rejects para que o DuckDB capture linhas rejeitadas."
    if error.code == "input_required":
        return "Informe pelo menos um arquivo de entrada."
    if error.code == "input_file_not_found":
        return f"Arquivo de entrada não encontrado: {context.get('path')}"
    if error.code == "input_path_not_file":
        return f"O caminho de entrada não é um arquivo: {context.get('path')}"
    if error.code == "no_supported_input":
        return "Nenhum arquivo de entrada compatível foi encontrado."
    if error.code == "zip_password_required":
        return f"O arquivo ZIP requer senha: {context.get('path')}"
    if error.code == "zip_too_many_entries":
        return f"O ZIP tem entradas demais: {context.get('path')}"
    if error.code == "zip_too_large":
        return f"O ZIP é grande demais após a extração: {context.get('path')}"
    if error.code == "zip_extract_failed":
        return f"Não foi possível extrair o ZIP {context.get('path')}: {context.get('reason')}"
    if error.code == "unsafe_zip_entry":
        return f"Caminho inseguro dentro do ZIP: {context.get('member')}"
    if error.code == "excel_read_failed":
        return f"Não foi possível ler o Excel {context.get('path')}: {context.get('reason')}"
    if error.code == "excel_too_many_worksheets":
        return (
            f"O Excel tem abas selecionadas demais: {context.get('count')} "
            f"(limite: {context.get('limit')})."
        )
    if error.code == "excel_too_many_entries":
        return f"O Excel tem entradas internas demais: {context.get('path')}"
    if error.code == "excel_too_large":
        return f"O Excel é grande demais após a descompactação: {context.get('path')}"
    if error.code == "excel_unsafe_compression_ratio":
        return f"O Excel tem uma taxa de compressão insegura: {context.get('path')}"
    if error.code == "excel_sheet_too_large":
        return (
            f"Aba '{context.get('sheet')}' declara {context.get('rows')} linhas e "
            f"{context.get('columns')} colunas ({context.get('cells')} células; "
            f"limite: {context.get('limit')}). Remova linhas ou colunas sem uso, "
            "salve o arquivo e tente novamente."
        )
    if error.code == "excel_formula_missing_cached_value":
        return (
            f"Aba '{context.get('sheet')}' contém fórmula sem valor salvo em {context.get('examples')}. "
            "Abra o arquivo no Excel ou LibreOffice, recalcule, salve e tente novamente."
        )
    if error.code == "excel_column_limit":
        return (
            f"O Excel aceita no máximo {context.get('limit')} colunas; "
            f"{context.get('selected')} foram selecionadas."
        )
    if error.code == "excel_string_limit":
        return (
            f"O Excel aceita no máximo {context.get('limit')} caracteres em uma célula; "
            f"recebeu {context.get('length')}."
        )
    if error.code == "excel_max_rows_per_sheet":
        return "--max-rows-per-sheet deve estar entre 2 e 1048576."
    if error.code == "excel_split_mode":
        return "--split-mode deve ser um de: sheets, files, both."
    if error.code == "excel_sheets_per_file":
        return "--sheets-per-file deve ser pelo menos 1."
    if error.code == "excel_workbook_closed":
        return "A pasta de trabalho do Excel já foi fechada."
    if error.code == "input_inspect_failed":
        return f"Não foi possível inspecionar o arquivo {context.get('path')}: {context.get('reason')}"
    if error.code == "duckdb_query_failed":
        return f"Consulta DuckDB falhou: {context.get('reason')}"
    if error.code == "lookup_column_error":
        return f"Erro na coluna do lookup '{context.get('lookup')}': {context.get('reason')}"
    if error.code == "dedupe_sort_required":
        return "Deduplicação por chave requer pelo menos uma coluna de ordenação."
    if error.code == "rejects_write_failed":
        return f"Não foi possível gravar o arquivo de rejeições {context.get('path')}: {context.get('reason')}"
    if error.code == "output_name_collision":
        return (
            "Nomes de saída resolvem para o mesmo arquivo: "
            f"{context.get('previous')} e {context.get('current')} usam {context.get('path')}."
        )
    if error.code == "output_overwrites_input":
        return f"O caminho de saída sobrescreveria um arquivo de entrada: {context.get('path')}"
    if error.code == "output_overwrites_lookup":
        return f"O caminho de saída sobrescreveria um arquivo de lookup: {context.get('path')}"
    if error.code == "artifact_overwrites_input":
        labels = {"report": "relatório", "rejects": "rejeitados"}
        label = labels.get(str(context.get("artifact")), str(context.get("artifact")))
        return f"O caminho de {label} sobrescreveria um arquivo de entrada: {context.get('path')}"
    if error.code == "artifact_overwrites_lookup":
        labels = {"report": "relatório", "rejects": "rejeitados"}
        label = labels.get(str(context.get("artifact")), str(context.get("artifact")))
        return f"O caminho de {label} sobrescreveria um arquivo de lookup: {context.get('path')}"
    if error.code == "artifact_path_collision":
        return f"Saída, relatório e rejeitados não podem resolver para o mesmo arquivo: {context.get('path')}"
    if error.code == "derived_columns_type":
        return "derived_columns deve ser uma lista de objetos."
    if error.code == "derived_columns_file_not_found":
        return f"Arquivo de colunas derivadas não encontrado: {context.get('path')}"
    if error.code == "derived_columns_file_type":
        return "Arquivos de colunas derivadas devem ser YAML, JSON ou TOML."
    if error.code == "derived_columns_file_parse":
        return f"Não foi possível analisar o arquivo de colunas derivadas {context.get('path')}: {context.get('reason')}"
    if error.code == "derived_column_json":
        return f"JSON de coluna derivada inválido: {context.get('reason')}"
    if error.code == "derived_column_type":
        return f"Coluna derivada #{context.get('index')} deve ser um objeto."
    if error.code == "derived_source_required":
        return f"Coluna derivada #{context.get('index')} precisa de uma coluna de origem."
    if error.code == "derived_name_type":
        return f"Nome da coluna derivada #{context.get('index')} deve ser texto ou objeto."
    if error.code == "derived_transforms_type":
        return f"Transformações da coluna derivada #{context.get('index')} devem ser uma lista."
    if error.code == "derived_transform_type":
        return f"Transformação da coluna derivada #{context.get('index')} deve ser texto ou objeto."
    if error.code == "derived_transform_operation_required":
        return f"Transformação da coluna derivada #{context.get('index')} precisa de uma operação."
    if error.code == "derived_position_text":
        return "Texto de posição da coluna derivada deve ser 'append'."
    if error.code == "derived_position_type":
        return "Posição da coluna derivada deve ser um objeto."
    if error.code == "derived_position_mode":
        return "Modo de posição da coluna derivada deve ser append, before ou after."
    if error.code == "derived_position_target_required":
        return "Posição before/after da coluna derivada precisa de uma coluna alvo."
    if error.code == "derived_case_conflict":
        return (
            f"Coluna derivada #{context.get('index')} não pode combinar transformações de maiúsculas/minúsculas: "
            f"{context.get('operations')}."
        )
    if error.code == "derived_transform_unsupported":
        return f"Transformação de coluna derivada não suportada: {context.get('operation')}"
    if error.code == "derived_excel_transform_unsupported":
        return f"Transformação de fórmula Excel não suportada: {context.get('operation')}"
    if error.code == "derived_transform_text_required":
        return (
            f"Transformação '{context.get('operation')}' precisa de um destes campos: "
            f"{context.get('names')}."
        )
    if error.code == "derived_transform_count_required":
        return f"Transformação '{context.get('operation')}' precisa de uma contagem positiva."
    if error.code == "derived_name_empty":
        return "Nome de coluna derivada não pode ficar vazio."
    if error.code == "derived_name_duplicate":
        return f"Nome de coluna derivada '{context.get('name')}' já existe."
    if error.code == "derived_position_target_missing":
        return f"Coluna alvo da posição da coluna derivada '{context.get('target')}' não foi encontrada."
    if error.code == "derived_position_target_not_selected":
        return f"Coluna alvo da posição da coluna derivada '{context.get('target')}' não está na saída."
    return None


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

    visual_value_match = re.match(r"Visual filter condition for column '([^']+)' needs (.*)\.", message)
    if visual_value_match:
        column, reason = visual_value_match.groups()
        translated_reason = {
            "a value": "um valor",
            "both values for between": "os dois valores do intervalo",
        }.get(reason, reason)
        return f"A condição visual da coluna '{column}' precisa de {translated_reason}."

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
