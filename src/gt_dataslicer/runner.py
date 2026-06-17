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
        filtered_output_path, summary_output_path = _output_paths_for_input(base_options, inputs[0], index=1, total=1)
        options = replace(
            base_options,
            input_path=inputs[0].source_path,
            output_path=filtered_output_path,
            summary_output_path=summary_output_path,
            resolved_input=inputs[0],
        )
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

    output_paths, summary_paths = _queue_output_paths(base_options, inputs)

    for index, (input_, output_path) in enumerate(zip(inputs, output_paths, strict=True), start=1):
        if progress is not None:
            progress(f"queue:{index}:{len(inputs)}")
        output_summary_path = summary_paths[index - 1] if index <= len(summary_paths) else None
        options = replace(
            base_options,
            input_path=input_.source_path,
            output_path=output_path,
            summary_output_path=output_summary_path,
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


def _output_paths_for_input(
    base_options: FilterRunOptions,
    input_: ResolvedInput,
    *,
    index: int,
    total: int,
) -> tuple[Path, Path | None]:
    output_name = base_options.output_names[index - 1] if index <= len(base_options.output_names) else None
    filtered_path = output_path_for_input(
        base_options.output_path,
        input_,
        index=index,
        total=total,
        output_format=base_options.output_format,
        output_name=output_name,
        artifact="filtered",
    )
    if not base_options.summarize:
        return filtered_path, None
    if base_options.summary_only:
        return filtered_path, filtered_path
    summary_path = output_path_for_input(
        base_options.output_path,
        input_,
        index=index,
        total=total,
        output_format=base_options.output_format,
        output_name=output_name,
        artifact="summary",
    )
    return filtered_path, summary_path


def _queue_output_paths(base_options: FilterRunOptions, inputs: list[ResolvedInput]) -> tuple[list[Path], list[Path]]:
    output_plan: list[tuple[int, ResolvedInput, Path, Path | None]] = [
        (index, input_, *_output_paths_for_input(base_options, input_, index=index, total=len(inputs)))
        for index, input_ in enumerate(inputs, start=1)
    ]
    filtered_paths = [filtered for _index, _input_, filtered, _summary in output_plan]
    summary_paths = [summary for _index, _input_, _filtered, summary in output_plan if summary is not None]
    _assert_no_output_path_conflicts(
        [(index, path) for index, _input_, path, _summary in output_plan]
        + [
            (index, summary)
            for index, _input_, _filtered, summary in output_plan
            if summary is not None
        ],
    )
    output_paths = filtered_paths
    return output_paths, summary_paths


def _assert_no_output_path_conflicts(output_paths: list[tuple[int, Path]]) -> None:
    seen: dict[str, int] = {}
    for input_index, output_path in output_paths:
        if output_path is None:
            continue
        key = str(output_path.resolve() if output_path.is_absolute() else output_path.absolute()).lower()
        previous_input_index = seen.get(key)
        if previous_input_index is not None and previous_input_index != input_index:
            raise ConfigError(
                "Output names resolve to the same file: "
                f"input #{previous_input_index} and input #{input_index} both use {output_path}."
            )
        seen[key] = input_index
