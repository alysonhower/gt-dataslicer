"""Sequential execution helpers for resolved input queues."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Callable

from .config import FilterRunOptions
from .engine.duckdb_engine import DuckDBEngine

from .exceptions import ConfigError, DataSlicerError
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
        output_name = base_options.output_names[0] if base_options.output_names else None
        output_path = output_path_for_input(
            base_options.output_path,
            inputs[0],
            index=1,
            total=1,
            output_format=base_options.output_format,
            output_name=output_name,
        )
        options = replace(base_options, input_path=inputs[0].source_path, output_path=output_path, resolved_input=inputs[0])
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

    output_paths = _queue_output_paths(base_options, inputs)

    for index, (input_, output_path) in enumerate(zip(inputs, output_paths, strict=True), start=1):
        if progress is not None:
            progress(f"queue:{index}:{len(inputs)}")
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


def _queue_output_paths(base_options: FilterRunOptions, inputs: list[ResolvedInput]) -> list[Path]:
    output_paths = [
        output_path_for_input(
            base_options.output_path,
            input_,
            index=index,
            total=len(inputs),
            output_format=base_options.output_format,
            output_name=base_options.output_names[index - 1] if index <= len(base_options.output_names) else None,
        )
        for index, input_ in enumerate(inputs, start=1)
    ]
    seen: dict[str, str] = {}
    for input_, output_path in zip(inputs, output_paths, strict=True):
        key = str(output_path.resolve() if output_path.is_absolute() else output_path.absolute()).lower()
        previous = seen.get(key)
        if previous is not None:
            raise ConfigError(
                "Output names resolve to the same file: "
                f"{previous} and {input_.source_label} both use {output_path}."
            )
        seen[key] = input_.source_label
    return output_paths
