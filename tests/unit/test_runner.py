from pathlib import Path

from gt_dataslicer.config import FilterRunOptions
from gt_dataslicer.engine.duckdb_engine import CsvSchema
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
