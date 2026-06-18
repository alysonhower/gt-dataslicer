"""Sequential execution helpers for resolved input queues."""

from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
from typing import Callable, Iterable, NoReturn

from .config import FilterRunOptions
from .engine.duckdb_engine import DuckDBEngine

from .exceptions import ConfigError, DataSlicerError
from .inputs import ResolvedInput, output_path_for_input
from .report import QueueRunReport, RunReport


ProgressCallback = Callable[[str], None]
CancelRegistration = Callable[[Callable[[], None]], Callable[[], None]]


def planned_run_artifacts(base_options: FilterRunOptions, inputs: list[ResolvedInput]) -> list[Path]:
    if not inputs:
        raise ValueError("At least one resolved input is required.")
    output_paths, summary_paths = _queue_output_paths(base_options, inputs)
    _validate_artifact_paths(base_options, inputs, output_paths, summary_paths)
    planned = _planned_output_artifacts(base_options, output_paths, summary_paths)
    planned.extend(_existing_split_xlsx_output_artifacts(base_options, planned))
    if base_options.report_path is not None:
        planned.append(base_options.report_path)
    if base_options.rejects_path is not None:
        planned.append(base_options.rejects_path)
    return _dedupe_paths(planned)


def run_filter_inputs(
    base_options: FilterRunOptions,
    inputs: list[ResolvedInput],
    *,
    progress: ProgressCallback | None = None,
    register_cancel: CancelRegistration | None = None,
    reuse_schema: bool = False,
    resolution_warnings: list[str] | None = None,
) -> RunReport | QueueRunReport:
    if not inputs:
        raise ValueError("At least one resolved input is required.")
    warnings = resolution_warnings or []
    output_paths, summary_paths = _queue_output_paths(base_options, inputs)
    _validate_artifact_paths(base_options, inputs, output_paths, summary_paths)

    if len(inputs) == 1:
        output_path = output_paths[0]
        options = replace(
            base_options,
            input_path=inputs[0].source_path,
            output_path=output_path,
            summary_output_path=summary_paths[0],
            resolved_input=inputs[0],
        )
        engine = DuckDBEngine()
        unregister_cancel = _register_engine_interrupt(register_cancel, engine)
        try:
            report = engine.run_filter(options, progress=progress)
        finally:
            unregister_cancel()
            _close_engine(engine)
        report.warnings.extend(warnings)
        return report

    queue_report = QueueRunReport(input_paths=[item.source_label for item in inputs])
    queue_report.warnings.extend(warnings)
    reusable_schema = None
    reusable_column_types = None
    if reuse_schema:
        queue_report.warnings.append("Reusing the first input schema for queue validation.")
        schema_engine = DuckDBEngine()
        unregister_cancel = _register_engine_interrupt(register_cancel, schema_engine)
        try:
            reusable_schema = schema_engine.inspect_input(inputs[0], base_options.csv, typed_mode=base_options.typed_mode)
            reusable_column_types = schema_engine.resolve_column_types(reusable_schema, base_options)
        finally:
            unregister_cancel()
            _close_engine(schema_engine)

    for index, (input_, output_path, summary_path) in enumerate(
        zip(inputs, output_paths, summary_paths, strict=True),
        start=1,
    ):
        if progress is not None:
            progress(f"queue:{index}:{len(inputs)}")
        options = replace(
            base_options,
            input_path=input_.source_path,
            output_path=output_path,
            summary_output_path=summary_path,
            resolved_input=input_,
        )
        try:
            engine = DuckDBEngine()
            unregister_cancel = _register_engine_interrupt(register_cancel, engine)
            try:
                report = engine.run_filter(
                    options,
                    progress=progress,
                    schema_override=reusable_schema,
                    column_types_override=reusable_column_types,
                )
            finally:
                unregister_cancel()
                _close_engine(engine)
            queue_report.add_run(report)
        except DataSlicerError as exc:
            queue_report.add_error(input_.source_label, exc)
        except Exception as exc:  # noqa: BLE001
            queue_report.add_error(input_.source_label, exc)

    queue_report.finish()
    return queue_report


def _queue_output_paths(base_options: FilterRunOptions, inputs: list[ResolvedInput]) -> tuple[list[Path], list[Path | None]]:
    plan = [
        _output_paths_for_input(base_options, input_, index=index, total=len(inputs))
        for index, input_ in enumerate(inputs, start=1)
    ]
    output_paths = [filtered for filtered, _summary in plan]
    summary_paths = [summary for _filtered, summary in plan]
    seen: dict[str, str] = {}
    for input_, filtered_path, summary_path in zip(inputs, output_paths, summary_paths, strict=True):
        for path in (filtered_path, summary_path):
            if path is None:
                continue
            key = _path_key(path)
            previous = seen.get(key)
            if previous is not None and previous != input_.source_label:
                _raise_config_error(
                    "Output names resolve to the same file: "
                    f"{previous} and {input_.source_label} both use {path}.",
                    code="output_name_collision",
                    previous=previous,
                    current=input_.source_label,
                    path=path,
                )
            seen[key] = input_.source_label
    return output_paths, summary_paths


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


def _validate_artifact_paths(
    base_options: FilterRunOptions,
    inputs: list[ResolvedInput],
    output_paths: list[Path],
    summary_paths: list[Path | None],
) -> None:
    input_paths = _path_set(_input_artifact_paths(inputs))
    lookup_paths = _path_set(lookup.path for lookup in base_options.lookups)
    output_keys: dict[str, Path] = {}
    planned_outputs = _planned_output_artifacts(base_options, output_paths, summary_paths)
    for output_path in planned_outputs:
        output_key = _path_key(output_path)
        if output_key in input_paths:
            _raise_config_error(
                f"Output path would overwrite an input file: {output_path}",
                code="output_overwrites_input",
                path=output_path,
            )
        if output_key in lookup_paths:
            _raise_config_error(
                f"Output path would overwrite a lookup file: {output_path}",
                code="output_overwrites_lookup",
                path=output_path,
            )
        output_keys[output_key] = output_path
    for input_path in _input_artifact_paths(inputs):
        if _matches_split_xlsx_output(base_options, planned_outputs, input_path):
            _raise_config_error(
                f"Output path would overwrite an input file: {input_path}",
                code="output_overwrites_input",
                path=input_path,
            )
    for lookup in base_options.lookups:
        if _matches_split_xlsx_output(base_options, planned_outputs, lookup.path):
            _raise_config_error(
                f"Output path would overwrite a lookup file: {lookup.path}",
                code="output_overwrites_lookup",
                path=lookup.path,
            )

    optional_artifacts = [
        ("report", base_options.report_path),
        ("rejects", base_options.rejects_path),
    ]
    seen_artifacts: dict[str, str] = {key: "output" for key in output_keys}
    for label, artifact_path in optional_artifacts:
        if artifact_path is None:
            continue
        artifact_key = _path_key(artifact_path)
        if artifact_key in input_paths:
            _raise_config_error(
                f"{label.capitalize()} path would overwrite an input file: {artifact_path}",
                code="artifact_overwrites_input",
                artifact=label,
                path=artifact_path,
            )
        if artifact_key in lookup_paths:
            _raise_config_error(
                f"{label.capitalize()} path would overwrite a lookup file: {artifact_path}",
                code="artifact_overwrites_lookup",
                artifact=label,
                path=artifact_path,
            )
        previous = seen_artifacts.get(artifact_key)
        if previous is not None or _matches_split_xlsx_output(base_options, planned_outputs, artifact_path):
            _raise_config_error(
                f"Output, report, and rejects paths must not resolve to the same file: {artifact_path}",
                code="artifact_path_collision",
                artifact=label,
                previous=previous or "output",
                path=artifact_path,
            )
        seen_artifacts[artifact_key] = label


def _planned_output_artifacts(
    base_options: FilterRunOptions,
    output_paths: list[Path],
    summary_paths: list[Path | None],
) -> list[Path]:
    planned: list[Path] = []
    for output_path, summary_path in zip(output_paths, summary_paths, strict=True):
        planned.append(output_path)
        if summary_path is not None:
            planned.append(summary_path)
    if base_options.output_format == "xlsx" and base_options.split_mode in {"files", "both"}:
        split_roots = list(planned)
        planned.extend(_xlsx_split_output_path(path, 1) for path in split_roots)
    return planned


def _existing_split_xlsx_output_artifacts(base_options: FilterRunOptions, output_paths: list[Path]) -> list[Path]:
    if base_options.output_format != "xlsx" or base_options.split_mode not in {"files", "both"}:
        return []
    existing: list[Path] = []
    for output_path in output_paths:
        parent = output_path.parent
        if not parent.exists() or not parent.is_dir():
            continue
        for candidate in parent.iterdir():
            if candidate.is_file() and _matches_split_xlsx_output(base_options, [output_path], candidate):
                existing.append(candidate)
    return sorted(existing, key=_path_key)


def _matches_split_xlsx_output(base_options: FilterRunOptions, output_paths: list[Path], artifact_path: Path) -> bool:
    if base_options.output_format != "xlsx" or base_options.split_mode not in {"files", "both"}:
        return False
    artifact_parent = _path_key(artifact_path.parent)
    artifact_suffix = artifact_path.suffix.lower()
    for output_path in output_paths:
        suffix = (output_path.suffix or ".xlsx").lower()
        prefix = f"{output_path.stem}_"
        if artifact_parent != _path_key(output_path.parent):
            continue
        if artifact_suffix != suffix:
            continue
        suffix_number = artifact_path.stem[len(prefix) :]
        if artifact_path.stem.startswith(prefix) and len(suffix_number) == 3 and suffix_number.isdigit():
            return True
    return False


def _xlsx_split_output_path(base: Path, file_index: int) -> Path:
    return base.with_name(f"{base.stem}_{file_index:03d}{base.suffix or '.xlsx'}")


def _input_artifact_paths(inputs: list[ResolvedInput]) -> list[Path]:
    paths: list[Path] = []
    for input_ in inputs:
        paths.append(input_.path)
        paths.append(input_.source_path)
        if input_.zip_source is not None:
            paths.append(input_.zip_source)
    return paths


def _path_set(paths: Iterable[Path]) -> set[str]:
    return {_path_key(path) for path in paths}


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = _path_key(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _path_key(path: Path) -> str:
    resolved = path.resolve(strict=False)
    return os.path.normcase(str(resolved))


def _close_engine(engine: object) -> None:
    close = getattr(engine, "close", None)
    if callable(close):
        close()


def _register_engine_interrupt(register_cancel: CancelRegistration | None, engine: DuckDBEngine) -> Callable[[], None]:
    if register_cancel is None:
        return lambda: None
    return register_cancel(engine.interrupt)


def _raise_config_error(message: str, *, code: str, **context: object) -> NoReturn:
    cleaned = {key: str(value) if isinstance(value, Path) else value for key, value in context.items()}
    raise ConfigError(message, code=code, context=cleaned)
