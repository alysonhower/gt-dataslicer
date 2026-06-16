from pathlib import Path

import pytest

from gt_dataslicer.config import CsvOptions, FilterRunOptions
from gt_dataslicer.engine.duckdb_engine import DuckDBEngine


def test_filter_does_not_count_input_rows_without_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.xlsx"
    csv_path.write_text("A\n1\n2\n", encoding="utf-8")
    engine = DuckDBEngine()

    def fail_count(*args: object, **kwargs: object) -> int:
        raise AssertionError("_count_rows should not run unless report_path is set")

    monkeypatch.setattr(engine, "_count_rows", fail_count)

    report = engine.run_filter(
        FilterRunOptions(
            input_path=csv_path,
            output_path=output_path,
            csv=CsvOptions(delimiter=","),
            where=["A IS NOT NULL"],
        )
    )

    assert report.input_rows is None
    assert report.output_rows == 2


def test_filter_counts_input_rows_when_report_requested(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.xlsx"
    report_path = tmp_path / "report.json"
    csv_path.write_text("A\n1\n2\n", encoding="utf-8")
    engine = DuckDBEngine()
    calls = 0

    def fake_count(*args: object, **kwargs: object) -> int:
        nonlocal calls
        calls += 1
        return 2

    monkeypatch.setattr(engine, "_count_rows", fake_count)

    report = engine.run_filter(
        FilterRunOptions(
            input_path=csv_path,
            output_path=output_path,
            report_path=report_path,
            csv=CsvOptions(delimiter=","),
            where=["A IS NOT NULL"],
        )
    )

    assert calls == 1
    assert report.input_rows == 2
