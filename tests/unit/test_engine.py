from pathlib import Path
import csv

import duckdb
import pytest

from gt_dataslicer.config import CsvOptions, FilterRunOptions, LookupSpec
from gt_dataslicer.engine import duckdb_engine as engine_module
from gt_dataslicer.engine.duckdb_engine import DuckDBEngine
from gt_dataslicer.exceptions import CsvReadError, QueryExecutionError
from gt_dataslicer.inputs import ResolvedInput


def test_duckdb_engine_context_manager_closes_connection() -> None:
    with DuckDBEngine() as engine:
        assert engine.connection.execute("SELECT 1").fetchone() == (1,)

    with pytest.raises(Exception):
        engine.connection.execute("SELECT 1").fetchone()


def test_inspect_source_preserves_unexpected_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine = DuckDBEngine()

    class BrokenConnection:
        def execute(self, _query: str):
            raise RuntimeError("programming bug")

        def close(self) -> None:
            pass

    monkeypatch.setattr(engine, "connection", BrokenConnection())

    with pytest.raises(RuntimeError, match="programming bug"):
        engine.inspect_csv(tmp_path / "input.csv", CsvOptions())


def test_primary_reject_rows_preserves_unexpected_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = DuckDBEngine()
    input_ = ResolvedInput(path=Path("input.csv"), format="csv", display_name="input", source_path=Path("input.csv"))

    class BrokenConnection:
        def execute(self, _query: str):
            raise RuntimeError("programming bug")

        def close(self) -> None:
            pass

    monkeypatch.setattr(engine, "connection", BrokenConnection())

    with pytest.raises(RuntimeError, match="programming bug"):
        engine._primary_reject_rows(input_)  # noqa: SLF001 - regression for exception narrowing.


def test_filter_does_not_count_input_rows_without_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    csv_path.write_text("A\n1\n2\n", encoding="utf-8")
    engine = DuckDBEngine()

    def fail_count(*args: object, **kwargs: object) -> int:
        raise AssertionError("_count_source_rows should not run unless report_path is set")

    monkeypatch.setattr(engine, "_count_source_rows", fail_count)

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
    output_path = tmp_path / "output.csv"
    report_path = tmp_path / "report.json"
    csv_path.write_text("A\n1\n2\n", encoding="utf-8")
    engine = DuckDBEngine()
    counted_sources: list[str] = []

    def fake_count(source: str) -> int:
        counted_sources.append(source)
        return 2

    monkeypatch.setattr(engine, "_count_source_rows", fake_count)

    report = engine.run_filter(
        FilterRunOptions(
            input_path=csv_path,
            output_path=output_path,
            report_path=report_path,
            csv=CsvOptions(delimiter=","),
            typed_mode=True,
            where=["A IS NOT NULL"],
        )
    )

    assert counted_sources == ['"__gt_ds_input"']
    assert report.input_rows == 2


def test_prepare_filter_query_exposes_shared_projection_and_source_boundary(tmp_path: Path) -> None:
    csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    csv_path.write_text("A,B\n1,Ana\n2,Bia\n", encoding="utf-8")
    input_ = ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)

    with DuckDBEngine() as engine:
        prepared = engine.prepare_filter_query(
            input_,
            FilterRunOptions(
                input_path=csv_path,
                output_path=output_path,
                csv=CsvOptions(delimiter=","),
                typed_mode=True,
                where=["A > 1"],
                select=["B"],
                renames={"B": "Nome"},
            ),
            materialize_source=True,
        )

        assert prepared.source == '"__gt_ds_input"'
        assert prepared.projection.output_columns == ["Nome"]
        assert prepared.renamed_columns == {"B": "Nome"}
        assert 'FROM "__gt_ds_input" WHERE' in prepared.query
        assert engine.connection.execute(f"SELECT COUNT(*) FROM {prepared.source}").fetchone() == (2,)


def test_prepare_filter_query_materializes_untyped_csv_source_when_requested(tmp_path: Path) -> None:
    csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    csv_path.write_text("A,B\n1,Ana\n2,Bia\n", encoding="utf-8")
    input_ = ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)

    with DuckDBEngine() as engine:
        prepared = engine.prepare_filter_query(
            input_,
            FilterRunOptions(
                input_path=csv_path,
                output_path=output_path,
                csv=CsvOptions(delimiter=","),
                where=['B != "Zed"'],
            ),
            materialize_source=True,
        )

        assert prepared.source == '"__gt_ds_input"'
        assert 'FROM "__gt_ds_input" WHERE' in prepared.query
        assert engine.connection.execute(f"SELECT COUNT(*) FROM {prepared.source}").fetchone() == (2,)


def test_prepare_filter_query_materializes_parquet_source_when_requested(tmp_path: Path) -> None:
    parquet_path = tmp_path / "input.parquet"
    output_path = tmp_path / "output.csv"
    duckdb.connect().execute(
        f"COPY (SELECT 1 AS A, 'Ana' AS B UNION ALL SELECT 2, 'Bia') TO '{parquet_path.as_posix()}'"
        " (FORMAT parquet)"
    )
    input_ = ResolvedInput(path=parquet_path, format="parquet", display_name="input", source_path=parquet_path)

    with DuckDBEngine() as engine:
        prepared = engine.prepare_filter_query(
            input_,
            FilterRunOptions(
                input_path=parquet_path,
                output_path=output_path,
                where=["A >= 1"],
            ),
            materialize_source=True,
        )

        assert prepared.source == '"__gt_ds_input"'
        assert 'FROM "__gt_ds_input" WHERE' in prepared.query
        assert engine.connection.execute(f"SELECT COUNT(*) FROM {prepared.source}").fetchone() == (2,)


def test_rejected_rows_count_distinct_primary_physical_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "bad.csv"
    output_path = tmp_path / "output.csv"
    rejects_path = tmp_path / "rejects.csv"
    csv_path.write_text("A,B\n1,2\n3,too,many\n4,5\n", encoding="utf-8")

    report = DuckDBEngine().run_filter(
        FilterRunOptions(
            input_path=csv_path,
            output_path=output_path,
            csv=CsvOptions(delimiter=",", strict_mode=True, store_rejects=True),
            where=["A IS NOT NULL"],
            typed_mode=True,
            report_path=tmp_path / "report.json",
            rejects_path=rejects_path,
        )
    )

    assert report.rejected_rows == 1
    with rejects_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert {row["line"] for row in rows} == {"3"}


def test_lookup_rejects_do_not_contaminate_primary_reject_count(tmp_path: Path) -> None:
    csv_path = tmp_path / "input.csv"
    lookup_path = tmp_path / "lookup.csv"
    output_path = tmp_path / "output.csv"
    rejects_path = tmp_path / "rejects.csv"
    csv_path.write_text("A\n1\n2\n", encoding="utf-8")
    lookup_path.write_text("ID\n1\n2,extra\n", encoding="utf-8")

    report = DuckDBEngine().run_filter(
        FilterRunOptions(
            input_path=csv_path,
            output_path=output_path,
            csv=CsvOptions(delimiter=",", strict_mode=True, store_rejects=True),
            where=["A IN @ids"],
            lookups=[LookupSpec(name="ids", path=lookup_path, column="ID")],
            rejects_path=rejects_path,
        )
    )

    assert report.rejected_rows == 0
    with rejects_path.open(newline="", encoding="utf-8") as file:
        assert list(csv.DictReader(file)) == []


def test_typed_csv_validation_reads_unselected_columns(tmp_path: Path) -> None:
    csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    csv_path.write_text(
        "NAME,AGE\n" + "".join(f"Person {index},{index}\n" for index in range(5_000)) + "Bad,not_an_int\n",
        encoding="utf-8",
    )

    with pytest.raises(QueryExecutionError) as exc_info:
        DuckDBEngine().run_filter(
            FilterRunOptions(
                input_path=csv_path,
                output_path=output_path,
                csv=CsvOptions(delimiter=",", sample_size=1, strict_mode=True),
                typed_mode=True,
                select=["NAME"],
            )
        )

    assert exc_info.value.code == "duckdb_query_failed"
    assert "Could not convert" in str(exc_info.value.context["reason"])
    assert not output_path.exists()


def test_rejects_write_failure_uses_structured_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_path = tmp_path / "input.csv"
    rejects_path = tmp_path / "rejects.csv"
    csv_path.write_text("A\n1\n", encoding="utf-8")
    input_ = ResolvedInput(path=csv_path, format="csv", display_name="input", source_path=csv_path)

    def fail_commit(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("disk full")

    monkeypatch.setattr(engine_module, "commit_with_temporary_path", fail_commit)

    with DuckDBEngine() as engine:
        with pytest.raises(CsvReadError, match="Could not write rejects file") as exc_info:
            engine._write_rejects(rejects_path, input_)  # noqa: SLF001 - regression for structured wrapper.

    assert exc_info.value.code == "rejects_write_failed"
    assert exc_info.value.context == {"path": str(rejects_path), "reason": "disk full"}


def test_typed_csv_store_rejects_excludes_unselected_malformed_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    rejects_path = tmp_path / "rejects.csv"
    csv_path.write_text(
        "NAME,AGE\n" + "".join(f"Person {index},{index}\n" for index in range(5_000)) + "Bad,not_an_int\n",
        encoding="utf-8",
    )

    report = DuckDBEngine().run_filter(
        FilterRunOptions(
            input_path=csv_path,
            output_path=output_path,
            rejects_path=rejects_path,
            csv=CsvOptions(delimiter=",", sample_size=1, strict_mode=True, store_rejects=True),
            typed_mode=True,
            select=["NAME"],
        )
    )

    assert report.output_rows == 5_000
    assert report.rejected_rows == 1
    with output_path.open(newline="", encoding="utf-8") as file:
        output_rows = list(csv.DictReader(file))
    assert output_rows[-1] == {"NAME": "Person 4999"}
    assert "Bad" not in {row["NAME"] for row in output_rows}
    with rejects_path.open(newline="", encoding="utf-8") as file:
        reject_rows = list(csv.DictReader(file))
    assert {row["line"] for row in reject_rows} == {"5002"}
