"""DuckDB-backed CSV filtering pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, Callable, Final, Mapping

import duckdb

from ..config import CsvOptions, FilterRunOptions, LookupSpec, SortSpec
from ..derived import ResolvedDerivedColumn, build_projection
from ..exceptions import CsvReadError, FilterValidationError, QueryExecutionError
from ..export.csv import CsvExportOptions, export_query_to_csv
from ..export.excel import ExcelExportOptions, batched_rows, export_rows_to_xlsx
from ..export.parquet import ParquetExportOptions, export_query_to_parquet
from ..filters.compiler import CompileContext, LookupBinding, compile_filter, quote_identifier, quote_literal
from ..filters.parser import combine_filters
from ..i18n import tr
from ..inputs import ResolvedInput, source_expression
from ..report import OutputArtifact, RunReport


LOGGER = logging.getLogger(__name__)
NUMERIC_DERIVED_TOTAL_OPERATIONS: Final = {"keep_digits"}
ProgressUpdate = str | Mapping[str, object]
ProgressCallback = Callable[[ProgressUpdate], None]


@dataclass(slots=True)
class CsvSchema:
    columns: dict[str, str]
    types: dict[str, str]


@dataclass(frozen=True, slots=True)
class SummaryColumnScope:
    schema: CsvSchema
    output_columns: tuple[str, ...]
    case_insensitive: bool


def _progress_update(phase: str, input_: ResolvedInput, *, artifact: str | None = None) -> dict[str, object]:
    return {
        "phase": phase,
        "label_key": f"ui.phase.{phase}",
        "input_name": input_.label,
        "artifact": artifact,
        "percent": None,
        "determinate": False,
    }


class DuckDBEngine:
    def __init__(self) -> None:
        self.connection = duckdb.connect(database=":memory:")

    def inspect_csv(self, path: Path, csv_options: CsvOptions, *, typed_mode: bool = False) -> CsvSchema:
        source = self._read_csv_expr(path, csv_options, typed_mode=typed_mode)
        return self._inspect_source(source, path)

    def inspect_input(self, input_: ResolvedInput, csv_options: CsvOptions, *, typed_mode: bool = False) -> CsvSchema:
        source = self._source_expr(input_, csv_options, typed_mode=typed_mode)
        return self._inspect_source(source, input_.source_path)

    def _inspect_source(self, source: str, path: Path) -> CsvSchema:
        try:
            description = self.connection.execute(f"DESCRIBE SELECT * FROM {source}").fetchall()
        except Exception as exc:  # noqa: BLE001
            raise CsvReadError(f"Could not inspect input {path}: {exc}") from exc
        columns = {row[0]: row[0] for row in description}
        types = {row[0]: str(row[1]) for row in description}
        return CsvSchema(columns=columns, types=types)

    def register_lookups(
        self, lookups: list[LookupSpec], csv_options: CsvOptions, *, case_insensitive_columns: bool = False
    ) -> dict[str, LookupBinding]:
        return self._register_lookups(lookups, csv_options, case_insensitive_columns)

    def resolve_column_types(self, schema: CsvSchema, options: FilterRunOptions) -> dict[str, str]:
        return self._resolve_column_types(schema, options)

    def run_filter(
        self,
        options: FilterRunOptions,
        progress: ProgressCallback | None = None,
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
                "summarize": options.summarize,
                "summary_only": options.summary_only,
                "summary_group_by": options.summary_group_by,
                "summary_totals": options.summary_totals,
            },
            dry_run=options.dry_run,
        )

        def emit_progress(phase: str, artifact: str | None = None) -> None:
            if progress is not None:
                progress(_progress_update(phase, input_, artifact=artifact))

        emit_progress("inspecting")
        schema = schema_override or self.inspect_input(input_, options.csv, typed_mode=options.typed_mode)
        report.schema = schema.types
        column_types = column_types_override or self.resolve_column_types(schema, options)

        emit_progress("validating")
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
        projection = build_projection(
            schema_columns=schema.columns,
            selected_columns=selected_columns,
            output_columns=output_columns,
            derived_columns=options.derived_columns,
            case_insensitive_columns=options.case_insensitive_columns,
        )
        report.engine_options["derived_columns"] = [
            {"source": item.source_column, "output": item.output_name}
            for item in projection.derived_columns
        ]
        resolved_dedupe_keys = self._resolve_named_list(schema, options.dedupe_keys, options.case_insensitive_columns)
        resolved_sorts = self._resolve_sorts(schema, options.sorts, options.case_insensitive_columns)
        summary_scope = SummaryColumnScope(
            schema=schema,
            output_columns=tuple(projection.output_columns),
            case_insensitive=options.case_insensitive_columns,
        )
        summary_group_by = self._resolve_summary_columns(summary_scope, options.summary_group_by)
        summary_totals = self._resolve_summary_columns(summary_scope, options.summary_totals)
        self._validate_derived_summary_totals(projection.derived_columns, summary_totals)
        query = self._build_query(
            input_=input_,
            csv_options=options.csv,
            typed_mode=options.typed_mode,
            select_items=projection.select_items,
            required_columns=projection.required_source_columns,
            where_sql=compiled.sql,
            dedupe=options.dedupe,
            dedupe_keys=resolved_dedupe_keys,
            sorts=resolved_sorts,
        )
        summary_query = None
        summary_headers: list[str] = []
        if options.summarize:
            summary_query, summary_headers = self._build_summary_query(
                input_=input_,
                csv_options=options.csv,
                typed_mode=options.typed_mode,
                where_sql=compiled.sql,
                dedupe=options.dedupe,
                dedupe_keys=resolved_dedupe_keys,
                filtered_select_items=projection.select_items,
                filtered_required_columns=projection.required_source_columns,
                filtered_output_columns=projection.output_columns,
                summary_group_by=summary_group_by,
                summary_totals=summary_totals,
                strict_values=options.strict_values,
            )
        LOGGER.debug("Compiled query: %s", query)

        if resolved_sorts:
            report.warnings.append(tr("warning.sort_temp_disk"))

        if options.dry_run:
            emit_progress("finishing")
            report.finish()
            return report

        try:
            capture_rejects = lambda: setattr(report, "rejected_rows", self._rejected_row_count())
            if options.report_path is not None:
                report.input_rows = self._count_rows(input_, options.csv, options.typed_mode)
            if not options.summary_only:
                emit_progress("exporting", "filtered")
                filtered_rows, filtered_output_paths = self._export_query(
                    query=query,
                    params=compiled.params,
                    output_format=options.output_format,
                    output_path=options.output_path,
                    headers=projection.output_columns,
                    report=report,
                    run_options=options,
                    formula_builders=projection.excel_formula_builders(),
                    finalize_report=capture_rejects,
                )
                report.output_rows = filtered_rows
                report.output_paths.extend(filtered_output_paths)
                report.artifacts.append(OutputArtifact(kind="filtered", path=str(options.output_path), rows=filtered_rows))
            if options.summarize:
                emit_progress("exporting", "summarization")
                summary_output = options.summary_output_path or self._summary_output_path(
                    options.output_path,
                    options.summary_output_format,
                )
                summary_rows, summary_output_paths = self._export_query(
                    query=summary_query,
                    params=compiled.params,
                    output_format=options.summary_output_format,
                    output_path=summary_output,
                    headers=summary_headers,
                    report=report,
                    formula_builders=None,
                    run_options=options,
                    finalize_report=capture_rejects if options.summary_only else None,
                )
                report.output_paths.extend(summary_output_paths)
                report.artifacts.append(OutputArtifact(kind="summarization", path=str(summary_output), rows=summary_rows))
                if options.summary_only:
                    report.output_rows = summary_rows
            if options.rejects_path is not None:
                self._write_rejects(options.rejects_path)
        except duckdb.Error as exc:
            report.finish()
            raise QueryExecutionError(f"DuckDB query failed: {exc}") from exc
        except Exception:
            report.finish()
            raise

        emit_progress("finishing")
        report.finish()
        return report

    def _export_query(
        self,
        *,
        query: str | None,
        params: list[Any],
        output_format: str,
        output_path: Path,
        run_options: FilterRunOptions,
        headers: list[str],
        report: RunReport,
        formula_builders: dict[int, object] | None = None,
        finalize_report: Callable[[], None] | None = None,
    ) -> tuple[int, list[str]]:
        if query is None:
            return 0, []
        if output_format == "csv":
            row_count = export_query_to_csv(
                self.connection,
                query=query,
                params=params,
                options=CsvExportOptions(output_path=output_path),
            )
            if finalize_report is not None:
                finalize_report()
            return row_count, [str(output_path)]
        if output_format == "parquet":
            row_count = export_query_to_parquet(
                self.connection,
                query=query,
                params=params,
                options=ParquetExportOptions(output_path=output_path),
            )
            if finalize_report is not None:
                finalize_report()
            return row_count, [str(output_path)]
        options = ExcelExportOptions(
            output_path=output_path,
            sheet_prefix=run_options.sheet_prefix,
            max_rows_per_sheet=run_options.max_rows_per_sheet,
            split_mode=run_options.split_mode,
            sheets_per_file=run_options.sheets_per_file,
        )
        cursor = self.connection.execute(query, params)
        existing_output_paths = list(report.output_paths)
        row_count = export_rows_to_xlsx(
            headers=headers,
            rows=batched_rows(cursor, run_options.batch_size),
            options=options,
            report=report,
            formula_builders=formula_builders or {},
            finalize_report=finalize_report,
        )
        output_paths = list(report.output_paths)
        report.output_paths = existing_output_paths
        return row_count, output_paths

    def _build_summary_query(
        self,
        *,
        input_: ResolvedInput,
        csv_options: CsvOptions,
        typed_mode: bool,
        where_sql: str,
        dedupe: bool,
        dedupe_keys: list[str],
        filtered_select_items: list[str],
        filtered_required_columns: list[str],
        filtered_output_columns: list[str],
        summary_group_by: list[str],
        summary_totals: list[str],
        strict_values: bool,
    ) -> tuple[str, list[str]]:
        summary_columns = _unique_columns([*summary_group_by, *summary_totals])
        projected_summary_columns = [column for column in summary_columns if column in filtered_output_columns]
        source_summary_columns = [column for column in summary_columns if column not in filtered_output_columns]
        summary_aliases = self._summary_internal_aliases(source_summary_columns, filtered_output_columns)
        summary_references = {
            **{column: column for column in projected_summary_columns},
            **summary_aliases,
        }
        summary_select_items = [
            f"{quote_identifier(column)} AS {quote_identifier(summary_aliases[column])}"
            for column in source_summary_columns
        ]
        source_query = self._build_query(
            input_=input_,
            csv_options=csv_options,
            typed_mode=typed_mode,
            select_items=[*filtered_select_items, *summary_select_items],
            required_columns=_unique_columns([*filtered_required_columns, *source_summary_columns]),
            where_sql=where_sql,
            dedupe=dedupe,
            dedupe_keys=dedupe_keys,
            sorts=[],
        )

        aggregate_items = [
            self._summary_sum_expression(summary_references[column], strict_values, alias=self._summary_total_alias(column))
            for column in summary_totals
        ]
        count_expr = f"COUNT(*) AS {quote_identifier(self._summary_count_alias())}"

        if summary_group_by:
            select_columns = [
                f"{quote_identifier(summary_references[column])} AS {quote_identifier(column)}"
                for column in summary_group_by
            ]
            select_items = [*select_columns, *aggregate_items, count_expr]
            group_by_columns = ", ".join(quote_identifier(summary_references[column]) for column in summary_group_by)
            headers = [*summary_group_by, *[self._summary_total_alias(column) for column in summary_totals], self._summary_count_alias()]
            base_query = (
                f"SELECT {', '.join(select_items)} "
                f"FROM ({source_query}) AS summary_base "
                f"GROUP BY {group_by_columns}"
            )
        else:
            select_items = [count_expr, *aggregate_items]
            headers = [self._summary_count_alias(), *[self._summary_total_alias(column) for column in summary_totals]]
            base_query = f"SELECT {', '.join(select_items)} FROM ({source_query}) AS summary_base"
        return base_query, headers

    def _summary_internal_aliases(self, columns: list[str], existing_names: list[str]) -> dict[str, str]:
        used = set(existing_names)
        aliases: dict[str, str] = {}
        for index, column in enumerate(columns, start=1):
            alias = f"__gt_ds_summary_{index}"
            while alias in used:
                alias = f"_{alias}"
            used.add(alias)
            aliases[column] = alias
        return aliases

    def _validate_derived_summary_totals(
        self,
        derived_columns: list[ResolvedDerivedColumn],
        summary_totals: list[str],
    ) -> None:
        derived_by_output = {column.output_name: column for column in derived_columns}
        for total in summary_totals:
            derived = derived_by_output.get(total)
            if derived is None or self._derived_total_is_numeric_compatible(derived):
                continue
            raise FilterValidationError(tr("error.summary_total_derived_text", column=total))

    def _derived_total_is_numeric_compatible(self, derived: ResolvedDerivedColumn) -> bool:
        return any(transform.operation in NUMERIC_DERIVED_TOTAL_OPERATIONS for transform in derived.transforms)

    def _summary_output_path(self, output_path: Path, output_format: str) -> Path:
        return output_path.with_name(f"{output_path.stem}_summarization.{output_format}")

    def _summary_count_alias(self) -> str:
        return "count"

    def _summary_total_alias(self, column: str) -> str:
        return f"total_{column}"

    def _summary_sum_expression(self, column: str, strict_values: bool, *, alias: str) -> str:
        source = quote_identifier(column)
        if strict_values:
            casted = f"CAST({source} AS DOUBLE)"
        else:
            casted = f"COALESCE(TRY_CAST({source} AS DOUBLE), 0)"
        return f"SUM({casted}) AS {quote_identifier(alias)}"

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

    def _resolve_summary_columns(
        self,
        scope: SummaryColumnScope,
        names: list[str],
    ) -> list[str]:
        return [self._resolve_summary_column(scope, name) for name in names]

    def _resolve_summary_column(self, scope: SummaryColumnScope, requested: str) -> str:
        if requested in scope.output_columns:
            return requested
        if requested in scope.schema.columns:
            return scope.schema.columns[requested]
        if scope.case_insensitive:
            projected_matches = [column for column in scope.output_columns if column.lower() == requested.lower()]
            if len(projected_matches) == 1:
                return projected_matches[0]
            if len(projected_matches) > 1:
                raise FilterValidationError(f"Column '{requested}' is ambiguous under case-insensitive matching.")
            schema_matches = [actual for actual in scope.schema.columns.values() if actual.lower() == requested.lower()]
            if len(schema_matches) == 1:
                return schema_matches[0]
            if len(schema_matches) > 1:
                raise FilterValidationError(f"Column '{requested}' is ambiguous under case-insensitive matching.")
        raise FilterValidationError(f"Missing column '{requested}'.")

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
        input_: ResolvedInput,
        csv_options: CsvOptions,
        typed_mode: bool,
        select_items: list[str],
        required_columns: list[str],
        where_sql: str,
        dedupe: bool,
        dedupe_keys: list[str],
        sorts: list[SortSpec],
    ) -> str:
        source = self._source_expr(input_, csv_options, typed_mode=typed_mode)

        if dedupe_keys:
            partition = ", ".join(quote_identifier(column) for column in dedupe_keys)
            inner_columns = _unique_columns([*required_columns, *(spec.column for spec in sorts)])
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

    def _count_rows(self, input_: ResolvedInput, csv_options: CsvOptions, typed_mode: bool) -> int:
        source = self._source_expr(input_, csv_options, typed_mode=typed_mode)
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
