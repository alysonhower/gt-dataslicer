from pathlib import Path
import csv
import re

import pytest

from gt_dataslicer.artifacts import commit_with_temporary_path
from gt_dataslicer.export.csv import CsvExportOptions, export_query_to_csv
from gt_dataslicer.export.parquet import ParquetExportOptions, export_query_to_parquet
from gt_dataslicer.report import RunReport


class _FakeCursor:
    def __init__(self, rows: int) -> None:
        self._rows = rows

    def fetchone(self) -> tuple[int]:
        return (self._rows,)


class _FakeSelectCursor:
    description = [("A",), ("B",)]

    def __init__(self) -> None:
        self._batches = [
            [
                ("=1+1", "+cmd"),
                ("-10", "@name"),
                ("\tTabbed", "\rCarriage"),
                ("safe", 5),
            ],
            [],
        ]

    def fetchmany(self, _batch_size: int) -> list[tuple[object, ...]]:
        return self._batches.pop(0)


def _copy_target(sql: str) -> Path:
    match = re.search(r" TO '([^']+)'", sql)
    assert match is not None, sql
    return Path(match.group(1).replace("''", "'"))


def test_commit_with_temporary_path_keeps_existing_file_on_failure(tmp_path: Path) -> None:
    output_path = tmp_path / "output.csv"
    output_path.write_text("old", encoding="utf-8")

    def failing_writer(temp_path: Path) -> None:
        temp_path.write_text("partial", encoding="utf-8")
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        commit_with_temporary_path(output_path, failing_writer)

    assert output_path.read_text(encoding="utf-8") == "old"
    assert list(tmp_path.glob(".*.tmp-*")) == []


def test_run_report_writes_json_atomically(tmp_path: Path) -> None:
    report_path = tmp_path / "report.json"
    report = RunReport(input_path="input.csv")
    report.output_rows = 2
    report.finish()

    report.write_json(report_path)

    assert '"output_rows": 2' in report_path.read_text(encoding="utf-8")
    assert list(tmp_path.glob(".*.tmp-*")) == []


def test_csv_export_commits_temporary_file_only_after_copy_success(tmp_path: Path) -> None:
    output_path = tmp_path / "output.csv"

    class FakeConnection:
        def execute(self, sql: str, params: list[object]) -> _FakeCursor:
            target = _copy_target(sql)
            assert target.name.startswith(".output.csv.tmp-")
            target.write_text("A\n1\n", encoding="utf-8")
            assert params == [1]
            return _FakeCursor(1)

    rows = export_query_to_csv(
        FakeConnection(),
        query="SELECT ? AS A",
        params=[1],
        options=CsvExportOptions(output_path=output_path),
    )

    assert rows == 1
    assert output_path.read_text(encoding="utf-8") == "A\n1\n"
    assert list(tmp_path.glob(".*.tmp-*")) == []


def test_csv_export_keeps_existing_file_when_copy_fails(tmp_path: Path) -> None:
    output_path = tmp_path / "output.csv"
    output_path.write_text("old", encoding="utf-8")

    class FakeConnection:
        def execute(self, sql: str, params: list[object]) -> _FakeCursor:
            _copy_target(sql).write_text("partial", encoding="utf-8")
            raise RuntimeError("copy failed")

    with pytest.raises(RuntimeError, match="copy failed"):
        export_query_to_csv(
            FakeConnection(),
            query="SELECT 1 AS A",
            params=[],
            options=CsvExportOptions(output_path=output_path),
        )

    assert output_path.read_text(encoding="utf-8") == "old"
    assert list(tmp_path.glob(".*.tmp-*")) == []


def test_csv_export_spreadsheet_safe_mode_prefixes_formula_like_text(tmp_path: Path) -> None:
    output_path = tmp_path / "output.csv"

    class FakeConnection:
        def execute(self, sql: str, params: list[object]) -> _FakeSelectCursor:
            assert sql == "SELECT A, B FROM data"
            assert params == []
            return _FakeSelectCursor()

    rows = export_query_to_csv(
        FakeConnection(),
        query="SELECT A, B FROM data",
        params=[],
        options=CsvExportOptions(output_path=output_path, spreadsheet_safe=True, batch_size=2),
    )

    assert rows == 4
    with output_path.open(newline="", encoding="utf-8") as file:
        assert list(csv.reader(file)) == [
            ["A", "B"],
            ["'=1+1", "'+cmd"],
            ["'-10", "'@name"],
            ["'\tTabbed", "'\rCarriage"],
            ["safe", "5"],
        ]


def test_parquet_export_keeps_existing_file_when_copy_fails(tmp_path: Path) -> None:
    output_path = tmp_path / "output.parquet"
    output_path.write_bytes(b"old")

    class FakeConnection:
        def execute(self, sql: str, params: list[object]) -> _FakeCursor:
            target = _copy_target(sql)
            assert target.name.startswith(".output.parquet.tmp-")
            target.write_bytes(b"partial")
            raise RuntimeError("copy failed")

    with pytest.raises(RuntimeError, match="copy failed"):
        export_query_to_parquet(
            FakeConnection(),
            query="SELECT 1 AS A",
            params=[],
            options=ParquetExportOptions(output_path=output_path),
        )

    assert output_path.read_bytes() == b"old"
    assert list(tmp_path.glob(".*.tmp-*")) == []
