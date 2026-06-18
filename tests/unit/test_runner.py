from pathlib import Path

import pytest

from gt_dataslicer.config import FilterRunOptions, LookupSpec
from gt_dataslicer.engine.duckdb_engine import CsvSchema
from gt_dataslicer.exceptions import ConfigError
from gt_dataslicer.inputs import ResolvedInput
from gt_dataslicer.report import RunReport
from gt_dataslicer import runner as runner_module


def test_queue_reuse_schema_passes_first_schema_to_each_run(tmp_path: Path, monkeypatch) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text("A\n1\n", encoding="utf-8")
    second.write_text("A\n2\n", encoding="utf-8")
    schema = CsvSchema(columns={"A": "A"}, types={"A": "VARCHAR"})
    seen_schema_overrides: list[CsvSchema | None] = []
    closed_engines: list["FakeDuckDBEngine"] = []

    class FakeDuckDBEngine:
        inspect_calls = 0

        def inspect_input(self, *_args, **_kwargs):
            FakeDuckDBEngine.inspect_calls += 1
            return schema

        def resolve_column_types(self, *_args, **_kwargs):
            return {"A": "string"}

        def run_filter(self, options, progress=None, *, schema_override=None, column_types_override=None):
            seen_schema_overrides.append(schema_override)
            report = RunReport(input_path=options.resolved_input.source_label)
            report.output_paths = [str(options.output_path)]
            report.output_rows = 1
            report.finish()
            return report

        def close(self) -> None:
            closed_engines.append(self)

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(input_path=first, output_path=tmp_path / "filtered.csv")
    inputs = [
        ResolvedInput(path=first, format="csv", display_name="first", source_path=first),
        ResolvedInput(path=second, format="csv", display_name="second", source_path=second),
    ]

    report = runner_module.run_filter_inputs(options, inputs, reuse_schema=True)

    assert FakeDuckDBEngine.inspect_calls == 1
    assert seen_schema_overrides == [schema, schema]
    assert len(closed_engines) == 3
    assert report.output_rows == 2


def test_runner_closes_single_input_engine_when_run_fails(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("A\n1\n", encoding="utf-8")
    closed_engines: list["FakeDuckDBEngine"] = []

    class FakeDuckDBEngine:
        def run_filter(self, *_args, **_kwargs):
            raise RuntimeError("export failed")

        def close(self) -> None:
            closed_engines.append(self)

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(input_path=csv_path, output_path=tmp_path / "output.csv")
    inputs = [ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)]

    with pytest.raises(RuntimeError, match="export failed"):
        runner_module.run_filter_inputs(options, inputs)

    assert len(closed_engines) == 1


def test_runner_registers_current_engine_interrupt_for_cancellation(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("A\n1\n", encoding="utf-8")
    active_callbacks = []
    engines: list["FakeDuckDBEngine"] = []

    class FakeDuckDBEngine:
        def __init__(self) -> None:
            self.interrupted = False
            engines.append(self)

        def run_filter(self, options, progress=None):
            assert len(active_callbacks) == 1
            active_callbacks[0]()
            report = RunReport(input_path=options.resolved_input.source_label)
            report.output_paths = [str(options.output_path)]
            report.finish()
            return report

        def interrupt(self) -> None:
            self.interrupted = True

        def close(self) -> None:
            pass

    def register_cancel(callback):
        active_callbacks.append(callback)

        def unregister() -> None:
            active_callbacks.remove(callback)

        return unregister

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(input_path=csv_path, output_path=tmp_path / "output.csv")
    inputs = [ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)]

    report = runner_module.run_filter_inputs(options, inputs, register_cancel=register_cancel)

    assert isinstance(report, RunReport)
    assert engines[0].interrupted is True
    assert active_callbacks == []


def test_queue_rejects_duplicate_custom_output_names(tmp_path: Path, monkeypatch) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text("A\n1\n", encoding="utf-8")
    second.write_text("A\n2\n", encoding="utf-8")

    class FakeDuckDBEngine:
        def run_filter(self, *_args, **_kwargs):
            raise AssertionError("duplicate output names should fail before exporting")

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(
        input_path=first,
        output_path=tmp_path / "filtered.csv",
        output_names=["resultado", "resultado.csv"],
    )
    inputs = [
        ResolvedInput(path=first, format="csv", display_name="first", source_path=first),
        ResolvedInput(path=second, format="csv", display_name="second", source_path=second),
    ]

    with pytest.raises(ConfigError, match="same file") as exc_info:
        runner_module.run_filter_inputs(options, inputs)

    assert exc_info.value.code == "output_name_collision"
    assert exc_info.value.context["previous"] == str(first)
    assert exc_info.value.context["current"] == str(second)
    assert exc_info.value.context["path"] == str(tmp_path / "resultado.csv")


def test_planned_run_artifacts_returns_queue_outputs_and_diagnostics(tmp_path: Path) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    output_dir = tmp_path / "outputs"
    report_path = tmp_path / "report.json"
    rejects_path = tmp_path / "rejects.csv"
    first.write_text("A\n1\n", encoding="utf-8")
    second.write_text("A\n2\n", encoding="utf-8")
    output_dir.mkdir()
    options = FilterRunOptions(
        input_path=first,
        output_path=output_dir,
        output_format="csv",
        report_path=report_path,
        rejects_path=rejects_path,
    )
    inputs = [
        ResolvedInput(path=first, format="csv", display_name="first", source_path=first),
        ResolvedInput(path=second, format="csv", display_name="second", source_path=second),
    ]

    planned = runner_module.planned_run_artifacts(options, inputs)

    assert planned == [
        output_dir / "001_first_filtered.csv",
        output_dir / "002_second_filtered.csv",
        report_path,
        rejects_path,
    ]


def test_planned_run_artifacts_includes_existing_later_split_xlsx_outputs(tmp_path: Path) -> None:
    csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.xlsx"
    existing_later_split = tmp_path / "output_002.xlsx"
    csv_path.write_text("A\n1\n", encoding="utf-8")
    existing_later_split.write_text("old workbook", encoding="utf-8")
    options = FilterRunOptions(
        input_path=csv_path,
        output_path=output_path,
        output_format="xlsx",
        split_mode="files",
    )
    inputs = [ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)]

    planned = runner_module.planned_run_artifacts(options, inputs)

    assert planned == [output_path, tmp_path / "output_001.xlsx", existing_later_split]


def test_runner_rejects_output_path_that_overwrites_input(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("A\n1\n", encoding="utf-8")

    class FakeDuckDBEngine:
        def run_filter(self, *_args, **_kwargs):
            raise AssertionError("input/output collisions should fail before exporting")

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(input_path=csv_path, output_path=csv_path)
    inputs = [ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)]

    with pytest.raises(ConfigError, match="would overwrite an input") as exc_info:
        runner_module.run_filter_inputs(options, inputs)

    assert exc_info.value.code == "output_overwrites_input"
    assert exc_info.value.context == {"path": str(csv_path)}


def test_runner_rejects_output_report_and_reject_collisions(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    csv_path.write_text("A\n1\n", encoding="utf-8")

    class FakeDuckDBEngine:
        def run_filter(self, *_args, **_kwargs):
            raise AssertionError("artifact collisions should fail before exporting")

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    inputs = [ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)]

    with pytest.raises(ConfigError, match="same file") as report_info:
        runner_module.run_filter_inputs(
            FilterRunOptions(input_path=csv_path, output_path=output_path, report_path=output_path),
            inputs,
        )

    assert report_info.value.code == "artifact_path_collision"
    assert report_info.value.context == {"artifact": "report", "previous": "output", "path": str(output_path)}

    with pytest.raises(ConfigError, match="same file") as rejects_info:
        runner_module.run_filter_inputs(
            FilterRunOptions(
                input_path=csv_path,
                output_path=output_path,
                report_path=tmp_path / "diagnostics.csv",
                rejects_path=tmp_path / "diagnostics.csv",
            ),
            inputs,
        )

    assert rejects_info.value.code == "artifact_path_collision"
    assert rejects_info.value.context == {
        "artifact": "rejects",
        "previous": "report",
        "path": str(tmp_path / "diagnostics.csv"),
    }


def test_runner_rejects_output_path_that_overwrites_lookup(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "input.csv"
    lookup_path = tmp_path / "lookup.csv"
    csv_path.write_text("A\n1\n", encoding="utf-8")
    lookup_path.write_text("A\n1\n", encoding="utf-8")

    class FakeDuckDBEngine:
        def run_filter(self, *_args, **_kwargs):
            raise AssertionError("lookup/output collisions should fail before exporting")

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(
        input_path=csv_path,
        output_path=lookup_path,
        lookups=[LookupSpec(name="ids", path=lookup_path, column="A")],
    )
    inputs = [ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)]

    with pytest.raises(ConfigError, match="would overwrite a lookup") as exc_info:
        runner_module.run_filter_inputs(options, inputs)

    assert exc_info.value.code == "output_overwrites_lookup"
    assert exc_info.value.context == {"path": str(lookup_path)}


def test_runner_rejects_split_xlsx_output_that_overwrites_input(tmp_path: Path, monkeypatch) -> None:
    input_path = tmp_path / "output_002.xlsx"
    input_path.write_text("A\n1\n", encoding="utf-8")

    class FakeDuckDBEngine:
        def run_filter(self, *_args, **_kwargs):
            raise AssertionError("split output collisions should fail before exporting")

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(
        input_path=input_path,
        output_path=tmp_path / "output.xlsx",
        output_format="xlsx",
        split_mode="files",
    )
    inputs = [ResolvedInput(path=input_path, format="csv", display_name="input", source_path=input_path)]

    with pytest.raises(ConfigError, match="would overwrite an input") as exc_info:
        runner_module.run_filter_inputs(options, inputs)

    assert exc_info.value.code == "output_overwrites_input"
    assert exc_info.value.context == {"path": str(input_path)}


def test_runner_rejects_report_or_rejects_matching_split_xlsx_output(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("A\n1\n", encoding="utf-8")

    class FakeDuckDBEngine:
        def run_filter(self, *_args, **_kwargs):
            raise AssertionError("split artifact collisions should fail before exporting")

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    inputs = [ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)]
    base_options = {
        "input_path": csv_path,
        "output_path": tmp_path / "output.xlsx",
        "output_format": "xlsx",
        "split_mode": "both",
    }

    with pytest.raises(ConfigError, match="same file") as report_info:
        runner_module.run_filter_inputs(
            FilterRunOptions(**base_options, report_path=tmp_path / "output_002.xlsx"),
            inputs,
        )

    assert report_info.value.code == "artifact_path_collision"
    assert report_info.value.context == {
        "artifact": "report",
        "previous": "output",
        "path": str(tmp_path / "output_002.xlsx"),
    }

    with pytest.raises(ConfigError, match="same file") as rejects_info:
        runner_module.run_filter_inputs(
            FilterRunOptions(**base_options, rejects_path=tmp_path / "output_003.xlsx"),
            inputs,
        )

    assert rejects_info.value.code == "artifact_path_collision"
    assert rejects_info.value.context == {
        "artifact": "rejects",
        "previous": "output",
        "path": str(tmp_path / "output_003.xlsx"),
    }
