"""Command-line interface."""

from __future__ import annotations

from pathlib import Path
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
from .logging_utils import configure_logging


app = typer.Typer(no_args_is_help=True, help="Filter large CSV files and export matching rows to CSV or XLSX.")
console = Console()


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, DataSlicerError):
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(exc.exit_code) from exc
    raise exc


@app.command("inspect")
def inspect_command(
    input_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    encoding: Annotated[str | None, typer.Option("--encoding")] = None,
    delimiter: Annotated[str | None, typer.Option("--delimiter")] = None,
    header: Annotated[bool | None, typer.Option("--header/--no-header")] = None,
    typed_mode: Annotated[bool, typer.Option("--typed-mode", help="Allow DuckDB to infer CSV column types.")] = False,
    log_level: Annotated[str, typer.Option("--log-level")] = "WARNING",
    json_logs: Annotated[bool, typer.Option("--json-logs")] = False,
) -> None:
    """Inspect detected CSV columns and types."""
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

    table = Table(title=f"Schema: {input_csv}")
    table.add_column("Column")
    table.add_column("DuckDB Type")
    for column, type_name in schema.types.items():
        table.add_row(column, type_name)
    console.print(table)


@app.command("validate-filter")
def validate_filter_command(
    input_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    where: Annotated[list[str] | None, typer.Option("--where", help="Filter expression. Repeat to AND filters.")] = None,
    config: Annotated[Path | None, typer.Option("--config", exists=True, dir_okay=False)] = None,
    preset: Annotated[str | None, typer.Option("--preset")] = None,
    lookup: Annotated[list[str] | None, typer.Option("--lookup", help="Lookup NAME=PATH:COLUMN.")] = None,
    type_: Annotated[list[str] | None, typer.Option("--type", help="Column type override, COLUMN=TYPE.")] = None,
    case_insensitive_columns: Annotated[bool, typer.Option("--case-insensitive-columns")] = False,
    encoding: Annotated[str | None, typer.Option("--encoding")] = None,
    delimiter: Annotated[str | None, typer.Option("--delimiter")] = None,
    header: Annotated[bool | None, typer.Option("--header/--no-header")] = None,
    log_level: Annotated[str, typer.Option("--log-level")] = "WARNING",
    json_logs: Annotated[bool, typer.Option("--json-logs")] = False,
) -> None:
    """Parse and validate filters without exporting."""
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
    console.print("[green]Filter is valid.[/green]")
    console.print(compiled.sql)


@app.command("filter")
def filter_command(
    input_csv: Annotated[Path, typer.Argument(exists=True, dir_okay=False, readable=True)],
    output: Annotated[Path, typer.Option("--output", "-o", help="Output path. Defaults to CSV unless .xlsx is used.")],
    format_: Annotated[
        str | None,
        typer.Option("--format", help="Output format: csv or xlsx. Overrides config output_format."),
    ] = None,
    where: Annotated[list[str] | None, typer.Option("--where", help="Filter expression. Repeat to AND filters.")] = None,
    config: Annotated[Path | None, typer.Option("--config", exists=True, dir_okay=False)] = None,
    preset: Annotated[str | None, typer.Option("--preset")] = None,
    select: Annotated[list[str] | None, typer.Option("--select", help="Column to include, repeatable.")] = None,
    select_file: Annotated[Path | None, typer.Option("--select-file", exists=True, dir_okay=False)] = None,
    rename: Annotated[list[str] | None, typer.Option("--rename", help="Rename output column, OLD=NEW.")] = None,
    dedupe: Annotated[bool, typer.Option("--dedupe")] = False,
    dedupe_key: Annotated[list[str] | None, typer.Option("--dedupe-key")] = None,
    sort: Annotated[list[str] | None, typer.Option("--sort", help="Sort COLUMN[:asc|desc].")] = None,
    encoding: Annotated[str | None, typer.Option("--encoding")] = None,
    delimiter: Annotated[str | None, typer.Option("--delimiter")] = None,
    quotechar: Annotated[str | None, typer.Option("--quotechar")] = None,
    escapechar: Annotated[str | None, typer.Option("--escapechar")] = None,
    header: Annotated[bool | None, typer.Option("--header/--no-header")] = None,
    null_value: Annotated[list[str] | None, typer.Option("--null-value")] = None,
    date_format: Annotated[str | None, typer.Option("--date-format")] = None,
    timestamp_format: Annotated[str | None, typer.Option("--timestamp-format")] = None,
    strict_csv: Annotated[bool, typer.Option("--strict-csv/--lenient-csv")] = True,
    store_rejects: Annotated[bool, typer.Option("--store-rejects")] = False,
    sample_size: Annotated[int | None, typer.Option("--sample-size")] = None,
    max_line_size: Annotated[int | None, typer.Option("--max-line-size")] = None,
    sheet_prefix: Annotated[str, typer.Option("--sheet-prefix")] = "Results",
    max_rows_per_sheet: Annotated[int, typer.Option("--max-rows-per-sheet")] = 1_048_576,
    split_mode: Annotated[str, typer.Option("--split-mode")] = "sheets",
    sheets_per_file: Annotated[int, typer.Option("--sheets-per-file")] = 31,
    lookup: Annotated[list[str] | None, typer.Option("--lookup", help="Lookup NAME=PATH:COLUMN.")] = None,
    report: Annotated[Path | None, typer.Option("--report")] = None,
    rejects: Annotated[Path | None, typer.Option("--rejects")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    case_insensitive_columns: Annotated[bool, typer.Option("--case-insensitive-columns")] = False,
    type_: Annotated[list[str] | None, typer.Option("--type", help="Column type override, COLUMN=TYPE.")] = None,
    typed_mode: Annotated[bool, typer.Option("--typed-mode", help="Allow DuckDB to infer CSV column types.")] = False,
    strict_values: Annotated[bool, typer.Option("--strict-values", help="Fail on invalid casts instead of using TRY_CAST.")] = False,
    batch_size: Annotated[int, typer.Option("--batch-size")] = 10_000,
    log_level: Annotated[str, typer.Option("--log-level")] = "INFO",
    json_logs: Annotated[bool, typer.Option("--json-logs")] = False,
) -> None:
    """Filter a CSV file and export matching rows to CSV or XLSX."""
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
        console.print("[green]Dry run succeeded.[/green]")
        return

    console.print(
        "[green]Export complete.[/green] "
        f"{run_report.output_rows} rows written to {', '.join(run_report.output_paths)}"
    )
    if report is not None:
        console.print(f"Report written to {report}")


if __name__ == "__main__":
    app()
