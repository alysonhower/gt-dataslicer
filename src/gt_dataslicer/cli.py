"""Command-line interface."""

from __future__ import annotations

from pathlib import Path
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
from .engine.duckdb_engine import DuckDBEngine
from .exceptions import DataSlicerError
from .filters.compiler import CompileContext, compile_filter
from .filters.parser import combine_filters
from .i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    invalid_language_message,
    localize_error_message,
    set_language,
    tr,
)
from .logging_utils import configure_logging


console = Console()


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

    @localized_app.command("inspect", help=tr("command.inspect.help"), hidden=True)
    @localized_app.command("inspecionar", help=tr("command.inspect.help"))
    def inspect_command(
        input_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True, metavar="ARQUIVO_CSV")],
        encoding: Annotated[str | None, typer.Option("--codificacao", "--encoding", metavar="TEXTO")] = None,
        delimiter: Annotated[str | None, typer.Option("--delimitador", "--delimiter", metavar="TEXTO")] = None,
        header: Annotated[
            bool | None, typer.Option("--cabecalho/--sem-cabecalho", "--header/--no-header")
        ] = None,
        typed_mode: Annotated[
            bool, typer.Option("--modo-tipado", "--typed-mode", help=tr("option.typed_mode"))
        ] = False,
        log_level: Annotated[str, typer.Option("--nivel-log", "--log-level", metavar="NIVEL")] = "WARNING",
        json_logs: Annotated[bool, typer.Option("--logs-json", "--json-logs")] = False,
    ) -> None:
        configure_logging(log_level, json_logs)
        try:
            schema = DuckDBEngine().inspect_csv(
                input_csv,
                CsvOptions(encoding=encoding, delimiter=delimiter, header=header),
                typed_mode=typed_mode,
            )
        except Exception as exc:  # noqa: BLE001
            _handle_error(exc)
            return

        table = Table(title=tr("schema_title", path=input_csv))
        table.add_column(tr("schema_column"))
        table.add_column(tr("schema_duckdb_type"))
        for column, type_name in schema.types.items():
            table.add_row(column, type_name)
        console.print(table)

    @localized_app.command("validate-filter", help=tr("command.validate_filter.help"), hidden=True)
    @localized_app.command("validar-filtro", help=tr("command.validate_filter.help"))
    def validate_filter_command(
        input_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True, metavar="ARQUIVO_CSV")],
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
                input_path=input_csv,
                output_path=Path("dry-run"),
                cli_output_format=None,
                preset_config=cfg,
                config_base_dir=config.resolve().parent if config is not None else None,
                cli_where=where or [],
                cli_select=[],
                select_file=None,
                cli_renames=[],
                cli_dedupe=False,
                cli_dedupe_keys=[],
                cli_sorts=[],
                cli_lookups=lookup or [],
                cli_types=type_ or [],
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
            engine = DuckDBEngine()
            schema = engine.inspect_csv(input_csv, options.csv, typed_mode=False)
            column_types = engine.resolve_column_types(schema, options)
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
        except Exception as exc:  # noqa: BLE001
            _handle_error(exc)
            return
        console.print(f"[green]{tr('filter_valid')}[/green]")
        console.print(compiled.sql)

    @localized_app.command("filter", help=tr("command.filter.help"), hidden=True)
    @localized_app.command("filtrar", help=tr("command.filter.help"))
    def filter_command(
        input_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True, metavar="ARQUIVO_CSV")],
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
        dedupe_key: Annotated[
            list[str] | None, typer.Option("--chave-deduplicacao", "--dedupe-key", metavar="COLUNA")
        ] = None,
        sort: Annotated[
            list[str] | None, typer.Option("--ordenar", "--sort", help=tr("option.sort"), metavar="TEXTO")
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
        report: Annotated[Path | None, typer.Option("--relatorio", "--report", metavar="CAMINHO")] = None,
        rejects: Annotated[Path | None, typer.Option("--rejeitados", "--rejects", metavar="CAMINHO")] = None,
        dry_run: Annotated[bool, typer.Option("--teste", "--dry-run")] = False,
        case_insensitive_columns: Annotated[
            bool, typer.Option("--colunas-sem-diferenciar-caixa", "--case-insensitive-columns")
        ] = False,
        type_: Annotated[
            list[str] | None, typer.Option("--tipo", "--type", help=tr("option.type"), metavar="TEXTO")
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
                input_path=input_csv,
                output_path=output,
                cli_output_format=format_,
                preset_config=cfg,
                config_base_dir=config.resolve().parent if config is not None else None,
                cli_where=where or [],
                cli_select=select or [],
                select_file=select_file,
                cli_renames=rename or [],
                cli_dedupe=dedupe,
                cli_dedupe_keys=dedupe_key or [],
                cli_sorts=sort or [],
                cli_lookups=lookup or [],
                cli_types=type_ or [],
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
            )
            run_report = DuckDBEngine().run_filter(options)
            if report is not None:
                run_report.write_json(report)
        except Exception as exc:  # noqa: BLE001
            _handle_error(exc)
            return

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
