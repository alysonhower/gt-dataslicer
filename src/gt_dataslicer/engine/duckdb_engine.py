"""DuckDB-backed CSV filtering pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any

import duckdb

from ..config import CsvOptions, FilterRunOptions, LookupSpec, SortSpec
from ..exceptions import CsvReadError, FilterValidationError, QueryExecutionError
from ..export.csv import CsvExportOptions, export_query_to_csv
from ..export.excel import ExcelExportOptions, batched_rows, export_rows_to_xlsx
from ..filters.compiler import CompileContext, LookupBinding, compile_filter, quote_identifier, quote_literal
from ..filters.parser import combine_filters
from ..i18n import tr
from ..report import RunReport


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class CsvSchema:
    columns: dict[str, str]
    types: dict[str, str]


class DuckDBEngine:
    def __init__(self) -> None:
        self.connection = duckdb.connect(database=":memory:")

    def inspect_csv(self, path: Path, csv_options: CsvOptions, *, typed_mode: bool = False) -> CsvSchema:
        source = self._read_csv_expr(path, csv_options, typed_mode=typed_mode)
        try:
            description = self.connection.execute(f"DESCRIBE SELECT * FROM {source}").fetchall()
        except Exception as exc:  # noqa: BLE001
            raise CsvReadError(f"Could not inspect CSV {path}: {exc}") from exc
        columns = {row[0]: row[0] for row in description}
        types = {row[0]: str(row[1]) for row in description}
        return CsvSchema(columns=columns, types=types)

    def register_lookups(
        self, lookups: list[LookupSpec], csv_options: CsvOptions, *, case_insensitive_columns: bool = False
    ) -> dict[str, LookupBinding]:
        return self._register_lookups(lookups, csv_options, case_insensitive_columns)

    def resolve_column_types(self, schema: CsvSchema, options: FilterRunOptions) -> dict[str, str]:
        return self._resolve_column_types(schema, options)

    def run_filter(self, options: FilterRunOptions) -> RunReport:
        report = RunReport(
            input_path=str(options.input_path),
            applied_filters=options.where,
            selected_columns=options.select,
            renamed_columns=options.renames,
            engine_options={
                "typed_mode": options.typed_mode,
                "strict_values": options.strict_values,
                "output_format": options.output_format,
                "split_mode": options.split_mode,
                "max_rows_per_sheet": options.max_rows_per_sheet,
            },
            dry_run=options.dry_run,
        )

        schema = self.inspect_csv(options.input_path, options.csv, typed_mode=options.typed_mode)
        report.schema = schema.types
        column_types = self.resolve_column_types(schema, options)

        lookup_bindings = self._register_lookups(options.lookups, options.csv, options.case_insensitive_columns)
        expr = combine_filters(options.where)
        compiled = compile_filter(
            expr,
            CompileContext(
                columns=schema.columns,
                column_types=column_types,
                lookups=lookup_bindings,
                case_insensitive_columns=options.case_insensitive_columns,
                strict_values=options.strict_values,
            ),
        )

        selected_columns = self._resolve_selected_columns(schema, options.select, options.case_insensitive_columns)
        resolved_renames = self._resolve_renames(schema, options.renames, options.case_insensitive_columns)
        report.renamed_columns = resolved_renames
        output_columns = [resolved_renames.get(column, column) for column in selected_columns]
        query = self._build_query(
            input_path=options.input_path,
            csv_options=options.csv,
            typed_mode=options.typed_mode,
            selected_columns=selected_columns,
            output_columns=output_columns,
            where_sql=compiled.sql,
            dedupe=options.dedupe,
            dedupe_keys=self._resolve_named_list(schema, options.dedupe_keys, options.case_insensitive_columns),
            sorts=self._resolve_sorts(schema, options.sorts, options.case_insensitive_columns),
        )

        LOGGER.debug("Compiled query: %s", query)
        if options.sorts:
            report.warnings.append(tr("warning.sort_temp_disk"))

        if options.dry_run:
            report.finish()
            return report

        try:
            if options.report_path is not None:
                report.input_rows = self._count_rows(options.input_path, options.csv, options.typed_mode)
            if options.output_format == "csv":
                report.output_rows = export_query_to_csv(
                    self.connection,
                    query=query,
                    params=compiled.params,
                    options=CsvExportOptions(output_path=options.output_path),
                )
                report.output_paths = [str(options.output_path)]
                report.rejected_rows = self._rejected_row_count()
            else:
                cursor = self.connection.execute(query, compiled.params)
                report.output_rows = export_rows_to_xlsx(
                    headers=output_columns,
                    rows=batched_rows(cursor, options.batch_size),
                    options=ExcelExportOptions(
                        output_path=options.output_path,
                        sheet_prefix=options.sheet_prefix,
                        max_rows_per_sheet=options.max_rows_per_sheet,
                        split_mode=options.split_mode,
                        sheets_per_file=options.sheets_per_file,
                    ),
                    report=report,
                    finalize_report=lambda: setattr(report, "rejected_rows", self._rejected_row_count()),
                )
            if options.rejects_path is not None:
                self._write_rejects(options.rejects_path)
        except duckdb.Error as exc:
            report.finish()
            raise QueryExecutionError(f"DuckDB query failed: {exc}") from exc
        except Exception:
            report.finish()
            raise

        report.finish()
        return report

    def _read_csv_expr(self, path: Path, csv_options: CsvOptions, *, typed_mode: bool) -> str:
        options: list[str] = ["auto_detect=true", f"all_varchar={'false' if typed_mode else 'true'}"]
        if csv_options.header is not None:
            options.append(f"header={'true' if csv_options.header else 'false'}")
        if csv_options.encoding:
            options.append(f"encoding={quote_literal(csv_options.encoding)}")
        if csv_options.delimiter:
            options.append(f"delim={quote_literal(csv_options.delimiter)}")
        if csv_options.quotechar:
            options.append(f"quote={quote_literal(csv_options.quotechar)}")
        if csv_options.escapechar:
            options.append(f"escape={quote_literal(csv_options.escapechar)}")
        if csv_options.null_values:
            nulls = ", ".join(quote_literal(value) for value in csv_options.null_values)
            options.append(f"nullstr=[{nulls}]")
        if csv_options.date_format:
            options.append(f"dateformat={quote_literal(csv_options.date_format)}")
        if csv_options.timestamp_format:
            options.append(f"timestampformat={quote_literal(csv_options.timestamp_format)}")
        options.append(f"strict_mode={'true' if csv_options.strict_mode else 'false'}")
        options.append(f"store_rejects={'true' if csv_options.store_rejects else 'false'}")
        if csv_options.sample_size is not None:
            options.append(f"sample_size={int(csv_options.sample_size)}")
        if csv_options.max_line_size is not None:
            options.append(f"max_line_size={int(csv_options.max_line_size)}")
        return f"read_csv({quote_literal(str(path))}, {', '.join(options)})"

    def _register_lookups(
        self, lookups: list[LookupSpec], csv_options: CsvOptions, case_insensitive_columns: bool
    ) -> dict[str, LookupBinding]:
        bindings: dict[str, LookupBinding] = {}
        for lookup in lookups:
            schema = self.inspect_csv(lookup.path, csv_options, typed_mode=False)
            try:
                lookup_column = resolve_column_name(schema, lookup.column, case_insensitive_columns)
            except FilterValidationError as exc:
                raise FilterValidationError(f"Lookup '{lookup.name}' column error: {exc}") from exc
            table_name = f"lookup_{lookup.name}"
            source = self._read_csv_expr(lookup.path, csv_options, typed_mode=False)
            sql = (
                f"CREATE OR REPLACE TEMP VIEW {quote_identifier(table_name)} AS "
                f"SELECT DISTINCT TRY_CAST({quote_identifier(lookup_column)} AS VARCHAR) AS {quote_identifier('__value')} "
                f"FROM {source} WHERE {quote_identifier(lookup_column)} IS NOT NULL"
            )
            self.connection.execute(sql)
            bindings[lookup.name] = LookupBinding(name=lookup.name, table_name=table_name)
        return bindings

    def _resolve_column_types(self, schema: CsvSchema, options: FilterRunOptions) -> dict[str, str]:
        resolved: dict[str, str] = {}
        for requested, type_name in options.column_types.items():
            actual = resolve_column_name(schema, requested, options.case_insensitive_columns)
            resolved[actual] = type_name
        return resolved

    def _resolve_selected_columns(
        self, schema: CsvSchema, requested_columns: list[str], case_insensitive: bool
    ) -> list[str]:
        if not requested_columns:
            return list(schema.columns.values())
        return self._resolve_named_list(schema, requested_columns, case_insensitive)

    def _resolve_named_list(self, schema: CsvSchema, names: list[str], case_insensitive: bool) -> list[str]:
        return [resolve_column_name(schema, name, case_insensitive) for name in names]

    def _resolve_sorts(self, schema: CsvSchema, sorts: list[SortSpec], case_insensitive: bool) -> list[SortSpec]:
        return [
            SortSpec(column=resolve_column_name(schema, spec.column, case_insensitive), direction=spec.direction)
            for spec in sorts
        ]

    def _resolve_renames(self, schema: CsvSchema, renames: dict[str, str], case_insensitive: bool) -> dict[str, str]:
        return {
            resolve_column_name(schema, requested, case_insensitive): output_name
            for requested, output_name in renames.items()
        }

    def _build_query(
        self,
        *,
        input_path: Path,
        csv_options: CsvOptions,
        typed_mode: bool,
        selected_columns: list[str],
        output_columns: list[str],
        where_sql: str,
        dedupe: bool,
        dedupe_keys: list[str],
        sorts: list[SortSpec],
    ) -> str:
        source = self._read_csv_expr(input_path, csv_options, typed_mode=typed_mode)
        select_items = [
            f"{quote_identifier(source_col)} AS {quote_identifier(output_col)}"
            for source_col, output_col in zip(selected_columns, output_columns, strict=True)
        ]

        if dedupe_keys:
            partition = ", ".join(quote_identifier(column) for column in dedupe_keys)
            inner_columns = _unique_columns([*selected_columns, *(spec.column for spec in sorts)])
            inner_select = ", ".join(f"{quote_identifier(column)}" for column in inner_columns)
            base = (
                "SELECT "
                f"{inner_select}, row_number() OVER (PARTITION BY {partition}) AS __gt_ds_rownum "
                f"FROM {source} WHERE {where_sql}"
            )
            query = f"SELECT {', '.join(select_items)} FROM ({base}) AS filtered WHERE __gt_ds_rownum = 1"
        else:
            distinct = "DISTINCT " if dedupe else ""
            query = f"SELECT {distinct}{', '.join(select_items)} FROM {source} WHERE {where_sql}"

        if sorts:
            order_by = ", ".join(f"{quote_identifier(spec.column)} {spec.direction.upper()}" for spec in sorts)
            query += f" ORDER BY {order_by}"
        return query

    def _count_rows(self, input_path: Path, csv_options: CsvOptions, typed_mode: bool) -> int:
        source = self._read_csv_expr(input_path, csv_options, typed_mode=typed_mode)
        return int(self.connection.execute(f"SELECT COUNT(*) FROM {source}").fetchone()[0])

    def _rejected_row_count(self) -> int | None:
        try:
            row = self.connection.execute("SELECT COUNT(*) FROM reject_errors").fetchone()
            return int(row[0])
        except Exception:  # noqa: BLE001 - rejects table only exists when DuckDB creates it.
            return None

    def _write_rejects(self, path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            self.connection.execute(f"COPY reject_errors TO {quote_literal(str(path))} (HEADER, DELIMITER ',')")
        except Exception as exc:  # noqa: BLE001
            raise CsvReadError(f"Could not write rejects file {path}: {exc}") from exc


def resolve_column_name(schema: CsvSchema, requested: str, case_insensitive: bool) -> str:
    if requested in schema.columns:
        return schema.columns[requested]
    if case_insensitive:
        matches = [actual for actual in schema.columns.values() if actual.lower() == requested.lower()]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise FilterValidationError(f"Column '{requested}' is ambiguous under case-insensitive matching.")
    raise FilterValidationError(f"Missing column '{requested}'.")


def _unique_columns(columns: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for column in columns:
        if column in seen:
            continue
        seen.add(column)
        unique.append(column)
    return unique
