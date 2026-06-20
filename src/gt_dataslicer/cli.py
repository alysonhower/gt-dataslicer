"""Command-line interface."""

from __future__ import annotations

from pathlib import Path
import getpass
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .config import (
    CsvOptions,
    load_config_file,
    merge_config_and_cli,
    select_preset,
)
from .derived import build_projection
from .engine.duckdb_engine import DuckDBEngine
from .exceptions import DataSlicerError
from .filters.compiler import CompileContext, compile_filter
from .filters.parser import combine_filters
from .i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    get_language,
    invalid_language_message,
    localize_error_message,
    set_language,
    tr,
)
from .logging_utils import configure_logging
from .inputs import InputResolutionOptions, InputResolutionSession
from .runner import run_filter_inputs


console = Console()


def _prompt_zip_password(path: Path) -> str | None:
    return getpass.getpass(f"{tr('zip_password_prompt', path=path)} ")


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, DataSlicerError):
        console.print(f"[red]{tr('error_prefix')}[/red] {localize_error_message(str(exc))}")
        raise typer.Exit(exc.exit_code) from exc
    raise exc


def _configure_language(language: str, *, fallback_language: str) -> None:
    try:
        set_language(language)
    except ValueError:
        set_language(fallback_language)
        console.print(f"[red]{tr('error_prefix')}[/red] {invalid_language_message(language)}")
        raise typer.Exit(2) from None


def _pre_scan_language(args: list[str]) -> str:
    for index, arg in enumerate(args):
        if arg in {"--idioma", "--lang"} and index + 1 < len(args):
            return args[index + 1]
        if arg.startswith("--idioma=") or arg.startswith("--lang="):
            return arg.split("=", 1)[1]
    return DEFAULT_LANGUAGE


def create_app(language: str = DEFAULT_LANGUAGE) -> typer.Typer:
    if language not in SUPPORTED_LANGUAGES:
        set_language(DEFAULT_LANGUAGE)
        raise ValueError(invalid_language_message(language))
    initial_language = language
    set_language(language)

    localized_app = typer.Typer(no_args_is_help=True, help=tr("app.help"))

    @localized_app.callback()
    def global_options(
        lang: Annotated[str, typer.Option("--idioma", "--lang", help=tr("option.lang"), metavar="IDIOMA")] = (
            DEFAULT_LANGUAGE
        ),
    ) -> None:
        _configure_language(lang, fallback_language=initial_language)

    @localized_app.command("ui", help=tr("command.ui.help"), hidden=True)
    @localized_app.command("abrir", help=tr("command.ui.help"))
    def ui_command(
        pywebview_debug: Annotated[
            bool,
            typer.Option(
                "--depurar-pywebview",
                "--pywebview-debug",
                help="Developer-only: launch Pywebview with native debug/devtools enabled.",
                hidden=True,
            ),
        ] = False,
    ) -> None:
        from .ui.app import main as ui_main

        ui_main(language=get_language(), debug=pywebview_debug)

    @localized_app.command("inspect", help=tr("command.inspect.help"), hidden=True)
    @localized_app.command("inspecionar", help=tr("command.inspect.help"))
    def inspect_command(
        input_files: Annotated[
            list[Path], typer.Argument(exists=True, dir_okay=False, readable=True, metavar="ARQUIVOS")
        ],
        encoding: Annotated[str | None, typer.Option("--codificacao", "--encoding", metavar="TEXTO")] = None,
        delimiter: Annotated[str | None, typer.Option("--delimitador", "--delimiter", metavar="TEXTO")] = None,
        header: Annotated[
            bool | None, typer.Option("--cabecalho/--sem-cabecalho", "--header/--no-header")
        ] = None,
        zip_password: Annotated[
            list[str] | None, typer.Option("--senha-zip", "--zip-password", metavar="TEXTO")
        ] = None,
        prompt_zip_password: Annotated[
            bool, typer.Option("--perguntar-senha-zip", "--prompt-zip-password")
        ] = False,
        all_excel_sheets: Annotated[bool, typer.Option("--todas-abas", "--all-excel-sheets")] = False,
        typed_mode: Annotated[
            bool, typer.Option("--modo-tipado", "--typed-mode", help=tr("option.typed_mode"))
        ] = False,
        log_level: Annotated[str, typer.Option("--nivel-log", "--log-level", metavar="NIVEL")] = "WARNING",
        json_logs: Annotated[bool, typer.Option("--logs-json", "--json-logs")] = False,
    ) -> None:
        configure_logging(log_level, json_logs)
        try:
            csv_options = CsvOptions(encoding=encoding, delimiter=delimiter, header=header)
            with InputResolutionSession(
                input_files,
                options=InputResolutionOptions(
                    zip_passwords=zip_password or [],
                    prompt_zip_password=_prompt_zip_password if prompt_zip_password else None,
                    excel_all_sheets=all_excel_sheets,
                ),
            ) as session:
                schemas = [
                    (input_, DuckDBEngine().inspect_input(input_, csv_options, typed_mode=typed_mode))
                    for input_ in session.inputs
                ]
        except Exception as exc:  # noqa: BLE001
            _handle_error(exc)
            return

        for input_, schema in schemas:
            table = Table(title=tr("schema_title", path=input_.label))
            table.add_column(tr("schema_column"))
            table.add_column(tr("schema_duckdb_type"))
            for column, type_name in schema.types.items():
                table.add_row(column, type_name)
            console.print(table)

    @localized_app.command("validate-filter", help=tr("command.validate_filter.help"), hidden=True)
    @localized_app.command("validar-filtro", help=tr("command.validate_filter.help"))
    def validate_filter_command(
        input_files: Annotated[
            list[Path], typer.Argument(exists=True, dir_okay=False, readable=True, metavar="ARQUIVOS")
        ],
        where: Annotated[
            list[str] | None, typer.Option("--filtro", "--where", help=tr("option.where"), metavar="TEXTO")
        ] = None,
        config: Annotated[
            Path | None,
            typer.Option("--configuracao", "--config", exists=True, dir_okay=False, metavar="CAMINHO"),
        ] = None,
        preset: Annotated[str | None, typer.Option("--predefinicao", "--preset", metavar="NOME")] = None,
        lookup: Annotated[
            list[str] | None, typer.Option("--consulta", "--lookup", help=tr("option.lookup"), metavar="TEXTO")
        ] = None,
        type_: Annotated[
            list[str] | None, typer.Option("--tipo", "--type", help=tr("option.type"), metavar="TEXTO")
        ] = None,
        derived_column: Annotated[
            list[str] | None,
            typer.Option("--coluna-derivada", "--derived-column", help=tr("option.derived_column"), metavar="JSON"),
        ] = None,
        derived_columns_file: Annotated[
            Path | None,
            typer.Option(
                "--colunas-derivadas-arquivo",
                "--derived-columns-file",
                exists=True,
                dir_okay=False,
                metavar="CAMINHO",
            ),
        ] = None,
        output_name: Annotated[
            list[str] | None,
            typer.Option("--nome-saida", "--output-name", help=tr("option.output_name"), metavar="NOME"),
        ] = None,
        zip_password: Annotated[
            list[str] | None, typer.Option("--senha-zip", "--zip-password", metavar="TEXTO")
        ] = None,
        prompt_zip_password: Annotated[
            bool, typer.Option("--perguntar-senha-zip", "--prompt-zip-password")
        ] = False,
        delete_zip_after_extract: Annotated[
            bool, typer.Option("--excluir-zip-apos-extrair", "--delete-zip-after-extract")
        ] = False,
        all_excel_sheets: Annotated[bool, typer.Option("--todas-abas", "--all-excel-sheets")] = False,
        reuse_schema: Annotated[bool, typer.Option("--reutilizar-esquema", "--reuse-schema")] = False,
        case_insensitive_columns: Annotated[
            bool, typer.Option("--colunas-sem-diferenciar-caixa", "--case-insensitive-columns")
        ] = False,
        encoding: Annotated[str | None, typer.Option("--codificacao", "--encoding", metavar="TEXTO")] = None,
        delimiter: Annotated[str | None, typer.Option("--delimitador", "--delimiter", metavar="TEXTO")] = None,
        header: Annotated[
            bool | None, typer.Option("--cabecalho/--sem-cabecalho", "--header/--no-header")
        ] = None,
        log_level: Annotated[str, typer.Option("--nivel-log", "--log-level", metavar="NIVEL")] = "WARNING",
        json_logs: Annotated[bool, typer.Option("--logs-json", "--json-logs")] = False,
    ) -> None:
        configure_logging(log_level, json_logs)
        try:
            cfg = select_preset(load_config_file(config), preset)
            options = merge_config_and_cli(
                input_path=input_files[0],
                output_path=Path("dry-run"),
                cli_output_format=None,
                preset_config=cfg,
                config_base_dir=config.resolve().parent if config is not None else None,
                cli_where=where or [],
                cli_select=[],
                select_file=None,
                cli_summarize=False,
                cli_summary_only=False,
                cli_summary_group_by=[],
                cli_summary_totals=[],
                cli_renames=[],
                cli_dedupe=False,
                cli_dedupe_keys=[],
                cli_sorts=[],
                cli_lookups=lookup or [],
                cli_types=type_ or [],
                cli_derived_columns=derived_column or [],
                derived_columns_file=derived_columns_file,
                cli_output_names=output_name or [],
                csv_options=CsvOptions(encoding=encoding, delimiter=delimiter, header=header),
                sheet_prefix="Results",
                max_rows_per_sheet=1_048_576,
                split_mode="sheets",
                sheets_per_file=31,
                report_path=None,
                rejects_path=None,
                dry_run=True,
                case_insensitive_columns=case_insensitive_columns,
                typed_mode=False,
                strict_values=False,
                batch_size=10_000,
            )
            with InputResolutionSession(
                input_files,
                options=InputResolutionOptions(
                    zip_passwords=zip_password or [],
                    prompt_zip_password=_prompt_zip_password if prompt_zip_password else None,
                    excel_all_sheets=all_excel_sheets,
                ),
            ) as session:
                compiled = None
                reusable_schema = None
                reusable_column_types = None
                for input_ in session.inputs:
                    engine = DuckDBEngine()
                    schema = reusable_schema or engine.inspect_input(input_, options.csv, typed_mode=False)
                    if reuse_schema and reusable_schema is None:
                        reusable_schema = schema
                    column_types = reusable_column_types or engine.resolve_column_types(schema, options)
                    if reuse_schema and reusable_column_types is None:
                        reusable_column_types = column_types
                    lookup_bindings = engine.register_lookups(
                        options.lookups, options.csv, case_insensitive_columns=options.case_insensitive_columns
                    )
                    expr = combine_filters(options.where)
                    compiled = compile_filter(
                        expr,
                        CompileContext(
                            columns=schema.columns,
                            column_types=column_types,
                            lookups=lookup_bindings,
                            case_insensitive_columns=case_insensitive_columns,
                        ),
                    )
                    selected_columns = engine._resolve_selected_columns(  # noqa: SLF001 - shared validation path.
                        schema,
                        options.select,
                        options.case_insensitive_columns,
                    )
                    resolved_renames = engine._resolve_renames(  # noqa: SLF001 - shared validation path.
                        schema,
                        options.renames,
                        options.case_insensitive_columns,
                    )
                    output_columns = [resolved_renames.get(column, column) for column in selected_columns]
                    build_projection(
                        schema_columns=schema.columns,
                        selected_columns=selected_columns,
                        output_columns=output_columns,
                        derived_columns=options.derived_columns,
                        case_insensitive_columns=options.case_insensitive_columns,
                    )
        except Exception as exc:  # noqa: BLE001
            _handle_error(exc)
            return
        console.print(f"[green]{tr('filter_valid')}[/green]")
        console.print(compiled.sql)

    @localized_app.command("filter", help=tr("command.filter.help"), hidden=True)
    @localized_app.command("filtrar", help=tr("command.filter.help"))
    def filter_command(
        input_files: Annotated[
            list[Path], typer.Argument(exists=True, dir_okay=False, readable=True, metavar="ARQUIVOS")
        ],
        output: Annotated[
            Path, typer.Option("--saida", "-o", "--output", help=tr("option.output"), metavar="CAMINHO")
        ],
        format_: Annotated[
            str | None,
            typer.Option("--formato", "--format", help=tr("option.format"), metavar="FORMATO"),
        ] = None,
        where: Annotated[
            list[str] | None, typer.Option("--filtro", "--where", help=tr("option.where"), metavar="TEXTO")
        ] = None,
        config: Annotated[
            Path | None,
            typer.Option("--configuracao", "--config", exists=True, dir_okay=False, metavar="CAMINHO"),
        ] = None,
        preset: Annotated[str | None, typer.Option("--predefinicao", "--preset", metavar="NOME")] = None,
        select: Annotated[
            list[str] | None, typer.Option("--selecionar", "--select", help=tr("option.select"), metavar="COLUNA")
        ] = None,
        select_file: Annotated[
            Path | None,
            typer.Option("--arquivo-selecao", "--select-file", exists=True, dir_okay=False, metavar="CAMINHO"),
        ] = None,
        rename: Annotated[
            list[str] | None, typer.Option("--renomear", "--rename", help=tr("option.rename"), metavar="TEXTO")
        ] = None,
        dedupe: Annotated[bool, typer.Option("--deduplicar", "--dedupe")] = False,
        summarization: Annotated[
            bool, typer.Option("--sumarizacao", "--summarization", help=tr("option.summarize"))
        ] = False,
        legacy_summarize: Annotated[
            bool, typer.Option("--resumir", "--summarize", hidden=True)
        ] = False,
        summarization_only: Annotated[
            bool, typer.Option("--somente-sumarizacao", "--summarization-only", help=tr("option.summary_only"))
        ] = False,
        legacy_summary_only: Annotated[
            bool, typer.Option("--somente-resumo", "--summary-only", hidden=True)
        ] = False,
        dedupe_key: Annotated[
            list[str] | None, typer.Option("--chave-deduplicacao", "--dedupe-key", metavar="COLUNA")
        ] = None,
        sort: Annotated[
            list[str] | None, typer.Option("--ordenar", "--sort", help=tr("option.sort"), metavar="TEXTO")
        ] = None,
        summarization_group_by: Annotated[
            list[str] | None, typer.Option("--grupo-sumarizacao", "--summarization-group-by", metavar="COLUNA")
        ] = None,
        legacy_summary_group_by: Annotated[
            list[str] | None, typer.Option("--grupo-resumo", "--summary-group-by", hidden=True, metavar="COLUNA")
        ] = None,
        summarization_totals: Annotated[
            list[str] | None, typer.Option("--totais-sumarizacao", "--summarization-totals", metavar="COLUNA")
        ] = None,
        legacy_summary_totals: Annotated[
            list[str] | None, typer.Option("--totais-resumo", "--summary-totals", hidden=True, metavar="COLUNA")
        ] = None,
        encoding: Annotated[str | None, typer.Option("--codificacao", "--encoding", metavar="TEXTO")] = None,
        delimiter: Annotated[str | None, typer.Option("--delimitador", "--delimiter", metavar="TEXTO")] = None,
        quotechar: Annotated[str | None, typer.Option("--aspas", "--quotechar", metavar="TEXTO")] = None,
        escapechar: Annotated[str | None, typer.Option("--escape", "--escapechar", metavar="TEXTO")] = None,
        header: Annotated[
            bool | None, typer.Option("--cabecalho/--sem-cabecalho", "--header/--no-header")
        ] = None,
        null_value: Annotated[
            list[str] | None, typer.Option("--valor-nulo", "--null-value", metavar="TEXTO")
        ] = None,
        date_format: Annotated[str | None, typer.Option("--formato-data", "--date-format", metavar="TEXTO")] = None,
        timestamp_format: Annotated[
            str | None, typer.Option("--formato-timestamp", "--timestamp-format", metavar="TEXTO")
        ] = None,
        strict_csv: Annotated[
            bool, typer.Option("--csv-estrito/--csv-flexivel", "--strict-csv/--lenient-csv")
        ] = True,
        store_rejects: Annotated[bool, typer.Option("--armazenar-rejeitados", "--store-rejects")] = False,
        sample_size: Annotated[int | None, typer.Option("--tamanho-amostra", "--sample-size", metavar="NUMERO")] = None,
        max_line_size: Annotated[
            int | None, typer.Option("--tamanho-max-linha", "--max-line-size", metavar="NUMERO")
        ] = None,
        sheet_prefix: Annotated[str, typer.Option("--prefixo-aba", "--sheet-prefix", metavar="TEXTO")] = "Results",
        max_rows_per_sheet: Annotated[
            int, typer.Option("--max-linhas-por-aba", "--max-rows-per-sheet", metavar="NUMERO")
        ] = 1_048_576,
        split_mode: Annotated[str, typer.Option("--modo-divisao", "--split-mode", metavar="TEXTO")] = "sheets",
        sheets_per_file: Annotated[int, typer.Option("--abas-por-arquivo", "--sheets-per-file", metavar="NUMERO")] = 31,
        lookup: Annotated[
            list[str] | None, typer.Option("--consulta", "--lookup", help=tr("option.lookup"), metavar="TEXTO")
        ] = None,
        zip_password: Annotated[
            list[str] | None, typer.Option("--senha-zip", "--zip-password", metavar="TEXTO")
        ] = None,
        prompt_zip_password: Annotated[
            bool, typer.Option("--perguntar-senha-zip", "--prompt-zip-password")
        ] = False,
        delete_zip_after_extract: Annotated[
            bool, typer.Option("--excluir-zip-apos-extrair", "--delete-zip-after-extract")
        ] = False,
        all_excel_sheets: Annotated[bool, typer.Option("--todas-abas", "--all-excel-sheets")] = False,
        reuse_schema: Annotated[bool, typer.Option("--reutilizar-esquema", "--reuse-schema")] = False,
        report: Annotated[Path | None, typer.Option("--relatorio", "--report", metavar="CAMINHO")] = None,
        rejects: Annotated[Path | None, typer.Option("--rejeitados", "--rejects", metavar="CAMINHO")] = None,
        dry_run: Annotated[bool, typer.Option("--teste", "--dry-run")] = False,
        case_insensitive_columns: Annotated[
            bool, typer.Option("--colunas-sem-diferenciar-caixa", "--case-insensitive-columns")
        ] = False,
        type_: Annotated[
            list[str] | None, typer.Option("--tipo", "--type", help=tr("option.type"), metavar="TEXTO")
        ] = None,
        derived_column: Annotated[
            list[str] | None,
            typer.Option("--coluna-derivada", "--derived-column", help=tr("option.derived_column"), metavar="JSON"),
        ] = None,
        derived_columns_file: Annotated[
            Path | None,
            typer.Option(
                "--colunas-derivadas-arquivo",
                "--derived-columns-file",
                exists=True,
                dir_okay=False,
                metavar="CAMINHO",
            ),
        ] = None,
        output_name: Annotated[
            list[str] | None,
            typer.Option("--nome-saida", "--output-name", help=tr("option.output_name"), metavar="NOME"),
        ] = None,
        typed_mode: Annotated[
            bool, typer.Option("--modo-tipado", "--typed-mode", help=tr("option.typed_mode"))
        ] = False,
        strict_values: Annotated[
            bool, typer.Option("--valores-estritos", "--strict-values", help=tr("option.strict_values"))
        ] = False,
        batch_size: Annotated[int, typer.Option("--tamanho-lote", "--batch-size", metavar="NUMERO")] = 10_000,
        log_level: Annotated[str, typer.Option("--nivel-log", "--log-level", metavar="NIVEL")] = "INFO",
        json_logs: Annotated[bool, typer.Option("--logs-json", "--json-logs")] = False,
    ) -> None:
        configure_logging(log_level, json_logs)
        try:
            cfg = select_preset(load_config_file(config), preset)
            options = merge_config_and_cli(
                input_path=input_files[0],
                output_path=output,
                cli_output_format=format_,
                preset_config=cfg,
                config_base_dir=config.resolve().parent if config is not None else None,
                cli_where=where or [],
                cli_select=select or [],
                select_file=select_file,
                cli_renames=rename or [],
                cli_summarize=summarization or legacy_summarize,
                cli_summary_only=summarization_only or legacy_summary_only,
                cli_summary_group_by=(summarization_group_by or []) + (legacy_summary_group_by or []),
                cli_summary_totals=(summarization_totals or []) + (legacy_summary_totals or []),
                cli_dedupe=dedupe,
                cli_dedupe_keys=dedupe_key or [],
                cli_sorts=sort or [],
                cli_lookups=lookup or [],
                cli_types=type_ or [],
                cli_derived_columns=derived_column or [],
                derived_columns_file=derived_columns_file,
                cli_output_names=output_name or [],
                csv_options=CsvOptions(
                    encoding=encoding,
                    delimiter=delimiter,
                    quotechar=quotechar,
                    escapechar=escapechar,
                    header=header,
                    null_values=null_value or [],
                    date_format=date_format,
                    timestamp_format=timestamp_format,
                    strict_mode=strict_csv,
                    store_rejects=store_rejects,
                    sample_size=sample_size,
                    max_line_size=max_line_size,
                ),
                sheet_prefix=sheet_prefix,
                max_rows_per_sheet=max_rows_per_sheet,
                split_mode=split_mode,
                sheets_per_file=sheets_per_file,
                report_path=report,
                rejects_path=rejects,
                dry_run=dry_run,
                case_insensitive_columns=case_insensitive_columns,
                typed_mode=typed_mode,
                strict_values=strict_values,
                batch_size=batch_size,
                allow_output_directory=len(input_files) > 1 or bool(output_name) or (output.exists() and output.is_dir()),
            )
            with InputResolutionSession(
                input_files,
                options=InputResolutionOptions(
                    zip_passwords=zip_password or [],
                    prompt_zip_password=_prompt_zip_password if prompt_zip_password else None,
                    delete_zip_after_extract=delete_zip_after_extract,
                    excel_all_sheets=all_excel_sheets,
                ),
            ) as session:
                run_report = run_filter_inputs(
                    options,
                    session.inputs,
                    reuse_schema=reuse_schema,
                    resolution_warnings=session.warnings,
                )
            if report is not None:
                run_report.write_json(report)
        except Exception as exc:  # noqa: BLE001
            _handle_error(exc)
            return

        if getattr(run_report, "failed_inputs", 0):
            console.print(f"[red]{tr('queue_failed', count=run_report.failed_inputs)}[/red]")
            raise typer.Exit(1)
        if dry_run:
            console.print(f"[green]{tr('dry_run_succeeded')}[/green]")
            return

        console.print(
            f"[green]{tr('export_complete')}[/green] "
            f"{tr('rows_written', rows=run_report.output_rows, paths=', '.join(run_report.output_paths))}"
        )
        if report is not None:
            console.print(tr("report_written", path=report))

    return localized_app


app = create_app(DEFAULT_LANGUAGE)


def main() -> None:
    try:
        create_app(_pre_scan_language(sys.argv[1:]))()
    except ValueError as exc:
        console.print(f"[red]{tr('error_prefix')}[/red] {exc}")
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
