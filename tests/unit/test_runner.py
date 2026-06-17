from pathlib import Path

import pytest

from gt_dataslicer.config import FilterRunOptions
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

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(input_path=first, output_path=tmp_path / "filtered.csv")
    inputs = [
        ResolvedInput(path=first, format="csv", display_name="first", source_path=first),
        ResolvedInput(path=second, format="csv", display_name="second", source_path=second),
    ]

    report = runner_module.run_filter_inputs(options, inputs, reuse_schema=True)

    assert FakeDuckDBEngine.inspect_calls == 1
    assert seen_schema_overrides == [schema, schema]
    assert report.output_rows == 2


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

    with pytest.raises(ConfigError, match="same file"):
        runner_module.run_filter_inputs(options, inputs)


def test_queue_output_paths_include_summary_outputs(tmp_path: Path, monkeypatch) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text("A\n1\n", encoding="utf-8")
    second.write_text("A\n2\n", encoding="utf-8")
    output_base = tmp_path / "filtered.csv"
    observed: list[tuple[Path, Path, Path | None]] = []

    class FakeDuckDBEngine:
        def run_filter(self, options, progress=None, *, schema_override=None, column_types_override=None):
            observed.append((options.output_path, options.summary_output_path, options.input_path))
            report = RunReport(input_path=options.input_path)
            if options.summary_only:
                report.output_paths = [str(options.output_path)]
            else:
                report.output_paths = [str(options.output_path), str(options.summary_output_path)]
            report.output_rows = 1
            report.finish()
            return report

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(input_path=first, output_path=output_base, summarize=True)
    inputs = [
        ResolvedInput(path=first, format="csv", display_name="first", source_path=first),
        ResolvedInput(path=second, format="csv", display_name="second", source_path=second),
    ]

    report = runner_module.run_filter_inputs(options, inputs)

    assert report.output_rows == 2
    assert len(observed) == 2
    assert observed[0][0] == tmp_path / "filtered_001_first.csv"
    assert observed[0][1] == tmp_path / "filtered_001_first_summary.csv"
    assert observed[1][0] == tmp_path / "filtered_002_second.csv"
    assert observed[1][1] == tmp_path / "filtered_002_second_summary.csv"
    assert report.output_paths == [
        str(tmp_path / "filtered_001_first.csv"),
        str(tmp_path / "filtered_001_first_summary.csv"),
        str(tmp_path / "filtered_002_second.csv"),
        str(tmp_path / "filtered_002_second_summary.csv"),
    ]


def test_queue_summary_only_uses_only_summary_paths(tmp_path: Path, monkeypatch) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text("A\n1\n", encoding="utf-8")
    second.write_text("A\n2\n", encoding="utf-8")
    output_base = tmp_path / "filtered.csv"
    observed: list[tuple[Path, Path | None]] = []

    class FakeDuckDBEngine:
        def run_filter(self, options, progress=None, *, schema_override=None, column_types_override=None):
            observed.append((options.output_path, options.summary_output_path))
            report = RunReport(input_path=options.input_path)
            report.output_paths = [str(options.output_path)]
            report.output_rows = 1
            report.finish()
            return report

    monkeypatch.setattr(runner_module, "DuckDBEngine", FakeDuckDBEngine)
    options = FilterRunOptions(input_path=first, output_path=output_base, summarize=True, summary_only=True)
    inputs = [
        ResolvedInput(path=first, format="csv", display_name="first", source_path=first),
        ResolvedInput(path=second, format="csv", display_name="second", source_path=second),
    ]

    report = runner_module.run_filter_inputs(options, inputs)

    assert report.output_rows == 2
    assert len(observed) == 2
    assert observed[0][0] == tmp_path / "filtered_001_first.csv"
    assert observed[0][0] == observed[0][1]
    assert observed[1][0] == tmp_path / "filtered_002_second.csv"
    assert observed[1][0] == observed[1][1]
    assert report.output_paths == [
        str(tmp_path / "filtered_001_first.csv"),
        str(tmp_path / "filtered_002_second.csv"),
    ]
