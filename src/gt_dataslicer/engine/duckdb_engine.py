"""DuckDB-backed CSV filtering pipeline."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import logging
import os
from pathlib import Path
from typing import Any, Callable

import duckdb

from ..artifacts import commit_with_temporary_path
from ..config import CsvOptions, FilterRunOptions, LookupSpec, SortSpec
from ..derived import DerivedProjection, build_projection
from ..exceptions import CsvReadError, FilterValidationError, QueryExecutionError
from ..export.csv import CsvExportOptions, export_query_to_csv
from ..export.excel import ExcelExportOptions, batched_rows, export_rows_to_xlsx
from ..export.parquet import ParquetExportOptions, export_query_to_parquet
from ..filters.compiler import CompiledFilter, CompileContext, LookupBinding, compile_filter, quote_identifier, quote_literal
from ..filters.parser import combine_filters
from ..i18n import tr
from ..inputs import ResolvedInput, source_expression
from ..report import RunReport


LOGGER = logging.getLogger(__name__)
_REJECT_ERROR_COLUMNS = [
    "scan_id",
    "file_id",
    "line",
    "line_byte_position",
    "byte_position",
    "column_idx",
    "column_name",
    "error_type",
    "csv_line",
    "error_message",
]


@dataclass(slots=True)
class CsvSchema:
    columns: dict[str, str]
    types: dict[str, str]


@dataclass(slots=True)
class PreparedFilterQuery:
    schema: CsvSchema
    column_types: dict[str, str]
    compiled_filter: CompiledFilter
    projection: DerivedProjection
    query: str
    source: str
    renamed_columns: dict[str, str]


class DuckDBEngine:
    def __init__(self) -> None:
        self.connection = duckdb.connect(database=":memory:")

    def close(self) -> None:
        self.connection.close()

    def interrupt(self) -> None:
        self.connection.interrupt()

    def __enter__(self) -> "DuckDBEngine":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def inspect_csv(self, path: Path, csv_options: CsvOptions, *, typed_mode: bool = False) -> CsvSchema:
        source = self._read_csv_expr(path, csv_options, typed_mode=typed_mode)
        return self._inspect_source(source, path)

    def inspect_input(self, input_: ResolvedInput, csv_options: CsvOptions, *, typed_mode: bool = False) -> CsvSchema:
        source = self._source_expr(input_, csv_options, typed_mode=typed_mode)
        return self._inspect_source(source, input_.source_path)

    def _inspect_source(self, source: str, path: Path) -> CsvSchema:
        try:
            description = self.connection.execute(f"DESCRIBE SELECT * FROM {source}").fetchall()
        except duckdb.Error as exc:
            raise CsvReadError(
                f"Could not inspect input {path}: {exc}",
                code="input_inspect_failed",
                context={"path": str(path), "reason": str(exc)},
            ) from exc
        columns = {row[0]: row[0] for row in description}
        types = {row[0]: str(row[1]) for row in description}
        return CsvSchema(columns=columns, types=types)

    def register_lookups(
        self, lookups: list[LookupSpec], csv_options: CsvOptions, *, case_insensitive_columns: bool = False
    ) -> dict[str, LookupBinding]:
        return self._register_lookups(lookups, csv_options, case_insensitive_columns)

    def resolve_column_types(self, schema: CsvSchema, options: FilterRunOptions) -> dict[str, str]:
        return self._resolve_column_types(schema, options)

    def prepare_filter_query(
        self,
        input_: ResolvedInput,
        options: FilterRunOptions,
        *,
        schema_override: CsvSchema | None = None,
        column_types_override: dict[str, str] | None = None,
        materialize_source: bool = False,
    ) -> PreparedFilterQuery:
        schema = schema_override or self.inspect_input(input_, options.csv, typed_mode=options.typed_mode)
        column_types = column_types_override or self.resolve_column_types(schema, options)
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
        output_columns = [resolved_renames.get(column, column) for column in selected_columns]
        projection = build_projection(
            schema_columns=schema.columns,
            selected_columns=selected_columns,
            output_columns=output_columns,
            derived_columns=options.derived_columns,
            case_insensitive_columns=options.case_insensitive_columns,
        )
        source = (
            self._prepare_source_relation(input_, options.csv, options.typed_mode, schema)
            if materialize_source
            else self._source_expr(input_, options.csv, typed_mode=options.typed_mode)
        )
        query = self._build_query(
            source=source,
            select_items=projection.select_items,
            required_columns=projection.required_source_columns,
            where_sql=compiled.sql,
            dedupe=options.dedupe,
            dedupe_keys=self._resolve_named_list(schema, options.dedupe_keys, options.case_insensitive_columns),
            sorts=self._resolve_sorts(schema, options.sorts, options.case_insensitive_columns),
        )
        return PreparedFilterQuery(
            schema=schema,
            column_types=column_types,
            compiled_filter=compiled,
            projection=projection,
            query=query,
            source=source,
            renamed_columns=resolved_renames,
        )

    def run_filter(
        self,
        options: FilterRunOptions,
        progress: Callable[[str], None] | None = None,
        *,
        schema_override: CsvSchema | None = None,
        column_types_override: dict[str, str] | None = None,
    ) -> RunReport:
        input_ = options.resolved_input or ResolvedInput(
            path=options.input_path,
            format="csv",
            display_name=options.input_path.stem,
            source_path=options.input_path,
        )
        report = RunReport(
            input_path=input_.source_label,
            applied_filters=options.where,
            selected_columns=options.select,
            renamed_columns=options.renames,
            engine_options={
                "typed_mode": options.typed_mode,
                "strict_values": options.strict_values,
                "output_format": options.output_format,
                "input_format": input_.format,
                "excel_sheet": input_.excel_sheet,
                "zip_source": str(input_.zip_source) if input_.zip_source is not None else None,
                "split_mode": options.split_mode,
                "max_rows_per_sheet": options.max_rows_per_sheet,
                "spreadsheet_safe_csv": options.spreadsheet_safe_csv,
            },
            dry_run=options.dry_run,
        )

        if progress is not None:
            progress("inspecting")
        schema = schema_override or self.inspect_input(input_, options.csv, typed_mode=options.typed_mode)
        report.schema = schema.types
        column_types = column_types_override or self.resolve_column_types(schema, options)

        if progress is not None:
            progress("validating")
        try:
            prepared = self.prepare_filter_query(
                input_,
                options,
                schema_override=schema,
                column_types_override=column_types,
                materialize_source=True,
            )
            report.renamed_columns = prepared.renamed_columns
            report.engine_options["derived_columns"] = [
                {"source": item.source_column, "output": item.output_name}
                for item in prepared.projection.derived_columns
            ]
            LOGGER.debug("Compiled query: %s", prepared.query)
            if options.sorts:
                report.warnings.append(tr("warning.sort_temp_disk"))

            if options.dry_run:
                if progress is not None:
                    progress("finishing")
                report.finish()
                return report
            if progress is not None:
                progress("exporting")
            if options.report_path is not None:
                report.input_rows = self._count_source_rows(prepared.source)
            if options.output_format == "csv":
                report.output_rows = export_query_to_csv(
                    self.connection,
                    query=prepared.query,
                    params=prepared.compiled_filter.params,
                    options=CsvExportOptions(
                        output_path=options.output_path,
                        spreadsheet_safe=options.spreadsheet_safe_csv,
                        batch_size=options.batch_size,
                    ),
                )
                report.output_paths = [str(options.output_path)]
                report.rejected_rows = self._rejected_row_count(input_)
            elif options.output_format == "parquet":
                report.output_rows = export_query_to_parquet(
                    self.connection,
                    query=prepared.query,
                    params=prepared.compiled_filter.params,
                    options=ParquetExportOptions(output_path=options.output_path),
                )
                report.output_paths = [str(options.output_path)]
                report.rejected_rows = self._rejected_row_count(input_)
            else:
                cursor = self.connection.execute(prepared.query, prepared.compiled_filter.params)
                report.output_rows = export_rows_to_xlsx(
                    headers=prepared.projection.output_columns,
                    rows=batched_rows(cursor, options.batch_size),
                    options=ExcelExportOptions(
                        output_path=options.output_path,
                        sheet_prefix=options.sheet_prefix,
                        max_rows_per_sheet=options.max_rows_per_sheet,
                        split_mode=options.split_mode,
                        sheets_per_file=options.sheets_per_file,
                    ),
                    report=report,
                    formula_builders=prepared.projection.excel_formula_builders(),
                    finalize_report=lambda: setattr(report, "rejected_rows", self._rejected_row_count(input_)),
                )
            if options.rejects_path is not None:
                self._write_rejects(options.rejects_path, input_)
        except duckdb.Error as exc:
            report.finish()
            raise QueryExecutionError(
                f"DuckDB query failed: {exc}",
                code="duckdb_query_failed",
                context={"reason": str(exc)},
            ) from exc
        except Exception:
            report.finish()
            raise

        if progress is not None:
            progress("finishing")
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

    def _source_expr(self, input_: ResolvedInput, csv_options: CsvOptions, *, typed_mode: bool) -> str:
        return source_expression(
            input_,
            csv_expr=lambda path: self._read_csv_expr(path, csv_options, typed_mode=typed_mode),
        )

    def _register_lookups(
        self, lookups: list[LookupSpec], csv_options: CsvOptions, case_insensitive_columns: bool
    ) -> dict[str, LookupBinding]:
        bindings: dict[str, LookupBinding] = {}
        for lookup in lookups:
            schema = self.inspect_csv(lookup.path, csv_options, typed_mode=False)
            try:
                lookup_column = resolve_column_name(schema, lookup.column, case_insensitive_columns)
            except FilterValidationError as exc:
                raise FilterValidationError(
                    f"Lookup '{lookup.name}' column error: {exc}",
                    code="lookup_column_error",
                    context={
                        "lookup": lookup.name,
                        "column": lookup.column,
                        "cause_code": exc.code,
                        "reason": str(exc),
                    },
                ) from exc
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
        source: str,
        select_items: list[str],
        required_columns: list[str],
        where_sql: str,
        dedupe: bool,
        dedupe_keys: list[str],
        sorts: list[SortSpec],
    ) -> str:
        if dedupe_keys:
            if not sorts:
                raise FilterValidationError(
                    "Key-based deduplication requires at least one sort key.",
                    code="dedupe_sort_required",
                )
            partition = ", ".join(quote_identifier(column) for column in dedupe_keys)
            window_order = ", ".join(f"{quote_identifier(spec.column)} {spec.direction.upper()}" for spec in sorts)
            inner_columns = _unique_columns([*required_columns, *(spec.column for spec in sorts)])
            inner_select = ", ".join(f"{quote_identifier(column)}" for column in inner_columns)
            base = (
                "SELECT "
                f"{inner_select}, "
                f"row_number() OVER (PARTITION BY {partition} ORDER BY {window_order}) AS __gt_ds_rownum "
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

    def _prepare_source_relation(
        self,
        input_: ResolvedInput,
        csv_options: CsvOptions,
        typed_mode: bool,
        schema: CsvSchema,
    ) -> str:
        source = self._source_expr(input_, csv_options, typed_mode=typed_mode)
        table_name = "__gt_ds_input"
        select_items = ", ".join(quote_identifier(column) for column in schema.columns.values()) or "*"
        self.connection.execute(
            f"CREATE OR REPLACE TEMP TABLE {quote_identifier(table_name)} AS SELECT {select_items} FROM {source}"
        )
        return quote_identifier(table_name)

    def _count_source_rows(self, source: str) -> int:
        return int(self.connection.execute(f"SELECT COUNT(*) FROM {source}").fetchone()[0])

    def _rejected_row_count(self, input_: ResolvedInput) -> int | None:
        rows = self._primary_reject_rows(input_)
        if rows is None:
            return None
        physical_rows = {(row[2], row[3], row[8]) for row in rows}
        return len(physical_rows)

    def _write_rejects(self, path: Path, input_: ResolvedInput) -> None:
        try:
            rows = self._primary_reject_rows(input_) or []
            unique_rows = _dedupe_reject_error_rows(rows)

            def write_temp(temp_path: Path) -> None:
                with temp_path.open("w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(_REJECT_ERROR_COLUMNS)
                    writer.writerows(unique_rows)

            commit_with_temporary_path(path, write_temp)
        except Exception as exc:  # noqa: BLE001
            raise CsvReadError(
                f"Could not write rejects file {path}: {exc}",
                code="rejects_write_failed",
                context={"path": str(path), "reason": str(exc)},
            ) from exc

    def _primary_reject_rows(self, input_: ResolvedInput) -> list[tuple[Any, ...]] | None:
        try:
            rows = self.connection.execute(
                """
                SELECT
                    s.file_path,
                    e.scan_id,
                    e.file_id,
                    e.line,
                    e.line_byte_position,
                    e.byte_position,
                    e.column_idx,
                    e.column_name,
                    e.error_type,
                    e.csv_line,
                    e.error_message
                FROM reject_errors AS e
                JOIN reject_scans AS s
                    ON e.scan_id = s.scan_id AND e.file_id = s.file_id
                ORDER BY e.line, e.byte_position, e.error_type
                """
            ).fetchall()
        except duckdb.Error:  # Reject tables only exist after DuckDB records rejects for a CSV scan.
            return None

        input_key = _path_key(input_.path)
        return [
            row[1:]
            for row in rows
            if row[0] is not None and _path_key(Path(str(row[0]))) == input_key
        ]


def resolve_column_name(schema: CsvSchema, requested: str, case_insensitive: bool) -> str:
    if requested in schema.columns:
        return schema.columns[requested]
    if case_insensitive:
        matches = [actual for actual in schema.columns.values() if actual.lower() == requested.lower()]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise FilterValidationError(
                f"Column '{requested}' is ambiguous under case-insensitive matching.",
                code="ambiguous_column",
                context={"column": requested},
            )
    raise FilterValidationError(
        f"Missing column '{requested}'.",
        code="missing_column",
        context={"column": requested, "suggestions": []},
    )


def _unique_columns(columns: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for column in columns:
        if column in seen:
            continue
        seen.add(column)
        unique.append(column)
    return unique


def _dedupe_reject_error_rows(rows: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    seen: set[tuple[Any, ...]] = set()
    unique: list[tuple[Any, ...]] = []
    for row in rows:
        key = row[2:]
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def _path_key(path: Path) -> str:
    return os.path.normcase(str(path.resolve(strict=False)))
