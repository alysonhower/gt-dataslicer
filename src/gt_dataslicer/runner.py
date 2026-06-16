"""Sequential execution helpers for resolved input queues."""

from __future__ import annotations

from dataclasses import replace
from typing import Callable

from .config import FilterRunOptions
from .engine.duckdb_engine import DuckDBEngine
from .exceptions import DataSlicerError
from .inputs import ResolvedInput, output_path_for_input
from .report import QueueRunReport, RunReport


ProgressCallback = Callable[[str], None]


def run_filter_inputs(
    base_options: FilterRunOptions,
    inputs: list[ResolvedInput],
    *,
    progress: ProgressCallback | None = None,
    reuse_schema: bool = False,
    resolution_warnings: list[str] | None = None,
) -> RunReport | QueueRunReport:
    if not inputs:
        raise ValueError("At least one resolved input is required.")
    warnings = resolution_warnings or []
    if len(inputs) == 1:
        options = replace(base_options, input_path=inputs[0].source_path, resolved_input=inputs[0])
        report = DuckDBEngine().run_filter(options, progress=progress)
        report.warnings.extend(warnings)
        return report

    queue_report = QueueRunReport(input_paths=[item.source_label for item in inputs])
    queue_report.warnings.extend(warnings)
    reusable_schema = None
    reusable_column_types = None
    if reuse_schema:
        queue_report.warnings.append("Reusing the first input schema for queue validation.")
        schema_engine = DuckDBEngine()
        reusable_schema = schema_engine.inspect_input(inputs[0], base_options.csv, typed_mode=base_options.typed_mode)
        reusable_column_types = schema_engine.resolve_column_types(reusable_schema, base_options)

    for index, input_ in enumerate(inputs, start=1):
        if progress is not None:
            progress(f"queue:{index}:{len(inputs)}")
        output_path = output_path_for_input(
            base_options.output_path,
            input_,
            index=index,
            total=len(inputs),
            output_format=base_options.output_format,
        )
        options = replace(
            base_options,
            input_path=input_.source_path,
            output_path=output_path,
            resolved_input=input_,
        )
        try:
            report = DuckDBEngine().run_filter(
                options,
                progress=progress,
                schema_override=reusable_schema,
                column_types_override=reusable_column_types,
            )
            queue_report.add_run(report)
        except DataSlicerError as exc:
            queue_report.add_error(input_.source_label, exc)
        except Exception as exc:  # noqa: BLE001
            queue_report.add_error(input_.source_label, exc)

    queue_report.finish()
    return queue_report
