"""Sequential execution helpers for resolved input queues."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Callable, Mapping

from .config import FilterRunOptions
from .engine.duckdb_engine import DuckDBEngine

from .exceptions import ConfigError, DataSlicerError
from .inputs import ResolvedInput, output_path_for_input
from .report import QueueRunReport, RunReport


ProgressUpdate = str | Mapping[str, object]
ProgressCallback = Callable[[ProgressUpdate], None]


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
        if base_options.avoid_existing_output_paths:
            filtered_output_path, summary_output_path = _avoid_existing_single_paths(
                filtered_output_path,
                summary_output_path,
            )
        options = replace(
            base_options,
            input_path=inputs[0].source_path,
            output_path=filtered_output_path,
            output_format=_engine_output_format(base_options, index=1),
            summary_output_format=_engine_summary_output_format(base_options, index=1),
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
            progress(_queue_progress_update("queue", input_, index, len(inputs)))
        output_summary_path = summary_paths[index - 1] if index <= len(summary_paths) else None
        options = replace(
            base_options,
            input_path=input_.source_path,
            output_path=output_path,
            output_format=_engine_output_format(base_options, index=index),
            summary_output_format=_engine_summary_output_format(base_options, index=index),
            summary_output_path=output_summary_path,
            resolved_input=input_,
        )
        try:
            report = DuckDBEngine().run_filter(
                options,
                progress=_progress_for_input(progress, input_, index, len(inputs)),
                schema_override=reusable_schema,
                column_types_override=reusable_column_types,
            )
            queue_report.add_run(report)
            if progress is not None:
                progress(
                    _queue_progress_update(
                        "queue",
                        input_,
                        index,
                        len(inputs),
                        percent=round(index / len(inputs) * 100),
                    )
                )
        except DataSlicerError as exc:
            queue_report.add_error(input_.source_label, exc)
        except Exception as exc:  # noqa: BLE001
            queue_report.add_error(input_.source_label, exc)

    queue_report.finish()
    return queue_report


def _progress_for_input(
    progress: ProgressCallback | None,
    input_: ResolvedInput,
    index: int,
    total: int,
) -> ProgressCallback | None:
    if progress is None:
        return None

    def update(current: ProgressUpdate) -> None:
        if isinstance(current, str):
            phase = current
            payload: dict[str, object] = {}
        else:
            phase = str(current.get("phase") or "running")
            payload = dict(current)
        payload.update(_queue_progress_update(phase, input_, index, total))
        progress(payload)

    return update


def _queue_progress_update(
    phase: str,
    input_: ResolvedInput,
    index: int,
    total: int,
    *,
    percent: int | None = None,
) -> dict[str, object]:
    queue_percent = percent if percent is not None else round(((index - 1) / total) * 100)
    return {
        "phase": phase,
        "input_index": index,
        "input_total": total,
        "input_name": input_.label,
        "percent": queue_percent,
        "determinate": True,
    }


def _engine_output_format(base_options: FilterRunOptions, *, index: int) -> str:
    output_name = base_options.output_names[index - 1] if index <= len(base_options.output_names) else None
    if base_options.summary_only and output_name is not None:
        return base_options.summary_output_format
    return base_options.output_format


def _engine_summary_output_format(base_options: FilterRunOptions, *, index: int) -> str:
    output_name = base_options.output_names[index - 1] if index <= len(base_options.output_names) else None
    if output_name is not None:
        return base_options.summary_output_format
    return base_options.output_format


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
        if output_name is None:
            return filtered_path, filtered_path
        summary_path = output_path_for_input(
            base_options.output_path,
            input_,
            index=index,
            total=total,
            output_format=base_options.summary_output_format,
            output_name=output_name,
            artifact="filtered",
        )
        return summary_path, summary_path
    summary_format = base_options.summary_output_format if output_name is not None else base_options.output_format
    summary_artifact = "summarization" if output_name is not None else "summary"
    summary_artifact_suffix = base_options.summary_output_suffix if base_options.summary_output_suffix else None
    summary_path = output_path_for_input(
        base_options.output_path,
        input_,
        index=index,
        total=total,
        output_format=summary_format,
        output_name=output_name,
        artifact=summary_artifact,
        artifact_suffix=summary_artifact_suffix,
    )
    return filtered_path, summary_path


def _queue_output_paths(base_options: FilterRunOptions, inputs: list[ResolvedInput]) -> tuple[list[Path], list[Path]]:
    output_plan: list[tuple[int, ResolvedInput, Path, Path | None]] = [
        (index, input_, *_output_paths_for_input(base_options, input_, index=index, total=len(inputs)))
        for index, input_ in enumerate(inputs, start=1)
    ]
    if base_options.avoid_existing_output_paths:
        output_plan = _avoid_existing_queue_paths(output_plan)
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


def _avoid_existing_single_paths(filtered_path: Path, summary_path: Path | None) -> tuple[Path, Path | None]:
    occupied: set[str] = set()
    safe_filtered = _available_output_path(filtered_path, occupied)
    if summary_path is None:
        return safe_filtered, None
    if summary_path == filtered_path:
        return safe_filtered, safe_filtered
    return safe_filtered, _available_output_path(summary_path, occupied)


def _avoid_existing_queue_paths(
    output_plan: list[tuple[int, ResolvedInput, Path, Path | None]],
) -> list[tuple[int, ResolvedInput, Path, Path | None]]:
    occupied: set[str] = set()
    safe_plan: list[tuple[int, ResolvedInput, Path, Path | None]] = []
    for index, input_, filtered_path, summary_path in output_plan:
        safe_filtered = _available_output_path(filtered_path, occupied)
        if summary_path is None:
            safe_summary = None
        elif summary_path == filtered_path:
            safe_summary = safe_filtered
        else:
            safe_summary = _available_output_path(summary_path, occupied)
        safe_plan.append((index, input_, safe_filtered, safe_summary))
    return safe_plan


def _available_output_path(path: Path, occupied: set[str]) -> Path:
    candidate = path
    counter = 2
    while _output_path_key(candidate) in occupied or candidate.exists():
        candidate = path.with_name(f"{path.stem}_{counter:03d}{path.suffix}")
        counter += 1
    occupied.add(_output_path_key(candidate))
    return candidate


def _assert_no_output_path_conflicts(output_paths: list[tuple[int, Path]]) -> None:
    seen: dict[str, int] = {}
    for input_index, output_path in output_paths:
        if output_path is None:
            continue
        key = _output_path_key(output_path)
        previous_input_index = seen.get(key)
        if previous_input_index is not None and previous_input_index != input_index:
            raise ConfigError(
                "Output names resolve to the same file: "
                f"input #{previous_input_index} and input #{input_index} both use {output_path}."
            )
        seen[key] = input_index


def _output_path_key(output_path: Path) -> str:
    return str(output_path.resolve() if output_path.is_absolute() else output_path.absolute()).lower()
