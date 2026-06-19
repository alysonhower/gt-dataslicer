from pathlib import Path
import csv
from threading import Event
import time
import zipfile

import duckdb
from openpyxl import load_workbook

from gt_dataslicer.ui.api import DataSlicerApi
from gt_dataslicer.ui import api as ui_api
from gt_dataslicer.ui.jobs import JobManager
from gt_dataslicer.report import RunReport


def write_people_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "ID,Nome,Status,Valor",
                "1,Ana Silva,ATIVO,1500",
                "2,Bruno Lima,CANCELADO,500",
                "3,Camila Silva,ATIVO,2500",
            ]
        ),
        encoding="utf-8",
    )


def wait_for_job(api: DataSlicerApi, job_id: str) -> dict[str, object]:
    for _ in range(100):
        response = api.get_job_status(job_id)
        assert response["ok"], response
        data = response["data"]
        assert isinstance(data, dict)
        if not data["running"]:
            return data
        time.sleep(0.02)
    raise AssertionError("job did not finish")


def test_ui_api_uses_public_engine_preparation_boundary() -> None:
    source = Path(ui_api.__file__).read_text(encoding="utf-8")

    assert "prepare_filter_query" in source
    assert "._resolve_selected_columns" not in source
    assert "._resolve_renames" not in source
    assert "._resolve_named_list" not in source
    assert "._resolve_sorts" not in source
    assert "._prepare_source_relation" not in source
    assert "._build_query" not in source


def test_ui_api_inspects_and_validates_visual_filter(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    write_people_csv(csv_path)
    api = DataSlicerApi()

    inspect_response = api.inspect_csv({"input_path": str(csv_path), "csv_options": {"delimiter": ","}})
    assert inspect_response["ok"], inspect_response
    inspect_data = inspect_response["data"]
    assert isinstance(inspect_data, dict)
    assert inspect_data["columns"] == ["ID", "Nome", "Status", "Valor"]

    validate_response = api.validate_filter(
        {
            "input_path": str(csv_path),
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [
                    {"column": "Status", "operator": "equals", "value": "ATIVO", "value_type": "string"},
                    {"column": "Valor", "operator": "gt", "value": "1000", "value_type": "number"},
                ],
            },
        }
    )

    assert validate_response["ok"], validate_response
    validate_data = validate_response["data"]
    assert isinstance(validate_data, dict)
    assert validate_data["valid"] is True
    assert "Status" in str(validate_data["sql"])


def test_ui_api_validate_filter_checks_every_queued_input(tmp_path: Path) -> None:
    first_path = tmp_path / "first.csv"
    second_path = tmp_path / "second.csv"
    first_path.write_text("ID,Status\n1,ATIVO\n", encoding="utf-8")
    second_path.write_text("ID,Other\n2,ATIVO\n", encoding="utf-8")
    api = DataSlicerApi()

    response = api.validate_filter(
        {
            "input_paths": [str(first_path), str(second_path)],
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
        }
    )

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert "Coluna ausente 'Status'" in str(error["message"])
    assert error["code"] == "missing_column"
    assert error["context"] == {"column": "Status", "suggestions": []}


def test_ui_api_preview_rows_uses_filter_projection_and_derived_columns(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    write_people_csv(csv_path)
    api = DataSlicerApi()

    response = api.preview_rows(
        {
            "input_path": str(csv_path),
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
            "select": ["Nome"],
            "derived_columns": [
                {
                    "source": "Nome",
                    "name": {"suffix": "LIMPO", "separator": "_"},
                    "transforms": [{"operation": "uppercase"}],
                }
            ],
            "limit": 1,
        }
    )

    assert response["ok"], response
    data = response["data"]
    assert isinstance(data, dict)
    assert data["columns"] == ["Nome", "Nome_LIMPO"]
    assert data["rows"] == [["Ana Silva", "ANA SILVA"]]
    assert data["limit"] == 1
    assert data["input_count"] == 1
    assert data["previewed_input_index"] == 1


def test_ui_api_returns_structured_derived_column_errors(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    write_people_csv(csv_path)
    api = DataSlicerApi()

    response = api.preview_rows(
        {
            "input_path": str(csv_path),
            "csv_options": {"delimiter": ","},
            "derived_columns": [{"name": "Nome_LIMPO", "transforms": ["trim"]}],
            "limit": 1,
        }
    )

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["code"] == "derived_source_required"
    assert error["context"] == {"index": 1}
    assert error["message"] == "Coluna derivada #1 precisa de uma coluna de origem."


def test_ui_api_preview_rows_labels_first_input_when_queue_has_multiple_files(tmp_path: Path) -> None:
    first_path = tmp_path / "first.csv"
    second_path = tmp_path / "second.csv"
    first_path.write_text("Nome,Status\nAna,ATIVO\n", encoding="utf-8")
    second_path.write_text("Nome,Status\nBia,ATIVO\n", encoding="utf-8")
    api = DataSlicerApi()

    response = api.preview_rows(
        {
            "input_paths": [str(first_path), str(second_path)],
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
            "limit": 5,
        }
    )

    assert response["ok"], response
    data = response["data"]
    assert isinstance(data, dict)
    assert data["rows"] == [["Ana", "ATIVO"]]
    assert data["input_count"] == 2
    assert data["previewed_input_index"] == 1


def test_ui_api_inspect_reports_per_input_schema_mismatches(tmp_path: Path) -> None:
    first_path = tmp_path / "first.csv"
    second_path = tmp_path / "second.csv"
    first_path.write_text("ID,Status\n1,ATIVO\n", encoding="utf-8")
    second_path.write_text("ID,Other\n2,ATIVO\n", encoding="utf-8")
    api = DataSlicerApi()

    response = api.inspect_csv(
        {
            "input_paths": [str(first_path), str(second_path)],
            "csv_options": {"delimiter": ","},
        }
    )

    assert response["ok"], response
    data = response["data"]
    assert isinstance(data, dict)
    assert data["columns"] == ["ID", "Status"]
    assert data["schema_compatible"] is False
    assert data["schema_mismatches"] == [str(second_path)]
    assert "Alguns arquivos da fila" in str(data["warnings"])
    inputs = data["inputs"]
    assert isinstance(inputs, list)
    assert inputs[0]["columns"] == ["ID", "Status"]
    assert inputs[0]["schema_matches_first"] is True
    assert inputs[1]["columns"] == ["ID", "Other"]
    assert inputs[1]["schema_matches_first"] is False


def test_ui_api_inspect_returns_input_resolution_warnings(tmp_path: Path) -> None:
    zip_path = tmp_path / "inputs.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("data.csv", "ID,Status\n1,ATIVO\n")
        archive.writestr("ignored.txt", "not supported")
    api = DataSlicerApi()

    response = api.inspect_csv({"input_path": str(zip_path), "csv_options": {"delimiter": ","}})

    assert response["ok"], response
    data = response["data"]
    assert isinstance(data, dict)
    assert data["warnings"] == ["Unsupported ZIP entry skipped: ignored.txt"]


def test_ui_api_inspect_and_validate_never_delete_zip_archives(tmp_path: Path) -> None:
    zip_path = tmp_path / "inputs.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("data.csv", "ID,Status\n1,ATIVO\n")
    api = DataSlicerApi()
    payload = {
        "input_path": str(zip_path),
        "csv_options": {"delimiter": ","},
        "delete_zip_after_extract": True,
        "filters": {
            "mode": "visual",
            "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
        },
    }

    inspect_response = api.inspect_csv(payload)
    validate_response = api.validate_filter(payload)

    assert inspect_response["ok"], inspect_response
    assert validate_response["ok"], validate_response
    assert zip_path.exists()


def test_ui_api_start_run_honors_explicit_zip_deletion(tmp_path: Path) -> None:
    zip_path = tmp_path / "inputs.zip"
    output_path = tmp_path / "filtered.csv"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("data.csv", "ID,Status\n1,ATIVO\n2,CANCELADO\n")
    api = DataSlicerApi()

    start_response = api.start_filter_run(
        {
            "input_path": str(zip_path),
            "output_path": str(output_path),
            "output_format": "csv",
            "csv_options": {"delimiter": ","},
            "delete_zip_after_extract": True,
            "confirm_delete_zip_after_extract": True,
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
        }
    )

    assert start_response["ok"], start_response
    start_data = start_response["data"]
    assert isinstance(start_data, dict)
    job = wait_for_job(api, str(start_data["job_id"]))
    assert job["phase"] == "done"
    assert output_path.exists()
    assert not zip_path.exists()


def test_ui_api_runs_csv_export(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.csv"
    write_people_csv(csv_path)
    api = DataSlicerApi()

    start_response = api.start_filter_run(
        {
            "input_path": str(csv_path),
            "output_path": str(output_path),
            "output_format": "csv",
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Nome", "operator": "contains", "value": "Silva"}],
            },
            "select": ["Nome"],
        }
    )

    assert start_response["ok"], start_response
    start_data = start_response["data"]
    assert isinstance(start_data, dict)
    job = wait_for_job(api, str(start_data["job_id"]))
    report = job["report"]
    assert isinstance(report, dict)
    assert report["output_rows"] == 2
    assert output_path.read_text(encoding="utf-8").splitlines() == ["Nome", "Ana Silva", "Camila Silva"]


def test_ui_api_runs_summary_export(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.csv"
    write_people_csv(csv_path)
    api = DataSlicerApi()

    start_response = api.start_filter_run(
        {
            "input_path": str(csv_path),
            "output_path": str(output_path),
            "output_format": "csv",
            "csv_options": {"delimiter": ","},
            "summarize": True,
            "summary_group_by": ["Status"],
            "summary_totals": ["Valor"],
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
        }
    )

    assert start_response["ok"], start_response
    start_data = start_response["data"]
    assert isinstance(start_data, dict)
    job = wait_for_job(api, str(start_data["job_id"]))
    report = job["report"]
    assert isinstance(report, dict)
    summary_path = tmp_path / "filtered_summary.csv"
    assert report["output_paths"] == [str(output_path), str(summary_path)]
    with summary_path.open(newline="", encoding="utf-8") as handle:
        assert list(csv.reader(handle)) == [["Status", "total_Valor", "count"], ["ATIVO", "4000.0", "2"]]


def test_ui_api_requires_confirmation_before_overwriting_output(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.csv"
    write_people_csv(csv_path)
    output_path.write_text("old contents\n", encoding="utf-8")
    api = DataSlicerApi()
    payload = {
        "input_path": str(csv_path),
        "output_path": str(output_path),
        "output_format": "csv",
        "csv_options": {"delimiter": ","},
        "filters": {
            "mode": "visual",
            "conditions": [{"column": "Nome", "operator": "contains", "value": "Silva"}],
        },
        "select": ["Nome"],
    }

    response = api.start_filter_run(payload)

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["type"] == "overwrite_confirmation_required"
    assert error["code"] == "overwrite_confirmation_required"
    assert str(error["message"]).startswith("Alguns arquivos de saída já existem")
    assert error["paths"] == [str(output_path)]
    assert error["context"] == {"paths": [str(output_path)]}
    assert output_path.read_text(encoding="utf-8") == "old contents\n"


def test_ui_api_overwrites_output_after_explicit_confirmation(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.csv"
    write_people_csv(csv_path)
    output_path.write_text("old contents\n", encoding="utf-8")
    api = DataSlicerApi()

    start_response = api.start_filter_run(
        {
            "input_path": str(csv_path),
            "output_path": str(output_path),
            "output_format": "csv",
            "confirm_overwrite": True,
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Nome", "operator": "contains", "value": "Silva"}],
            },
            "select": ["Nome"],
        }
    )

    assert start_response["ok"], start_response
    start_data = start_response["data"]
    assert isinstance(start_data, dict)
    job = wait_for_job(api, str(start_data["job_id"]))
    report = job["report"]
    assert isinstance(report, dict)
    assert report["output_rows"] == 2
    assert output_path.read_text(encoding="utf-8").splitlines() == ["Nome", "Ana Silva", "Camila Silva"]


def test_ui_api_requires_confirmation_for_existing_multi_input_output_child(tmp_path: Path) -> None:
    first_path = tmp_path / "first.csv"
    second_path = tmp_path / "second.csv"
    output_dir = tmp_path / "outputs"
    first_path.write_text("Nome,Status\nAna,ATIVO\n", encoding="utf-8")
    second_path.write_text("Nome,Status\nBia,ATIVO\n", encoding="utf-8")
    output_dir.mkdir()
    existing_child = output_dir / "002_second_filtered.csv"
    existing_child.write_text("old contents\n", encoding="utf-8")
    api = DataSlicerApi()

    response = api.start_filter_run(
        {
            "input_paths": [str(first_path), str(second_path)],
            "output_path": str(output_dir),
            "output_format": "csv",
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
            "select": ["Nome"],
        }
    )

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["type"] == "overwrite_confirmation_required"
    assert error["code"] == "overwrite_confirmation_required"
    assert error["paths"] == [str(existing_child)]
    assert error["context"] == {"paths": [str(existing_child)]}
    assert existing_child.read_text(encoding="utf-8") == "old contents\n"


def test_ui_api_requires_confirmation_for_existing_later_split_xlsx_output(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.xlsx"
    existing_later_split = tmp_path / "filtered_002.xlsx"
    write_people_csv(csv_path)
    existing_later_split.write_text("old contents\n", encoding="utf-8")
    api = DataSlicerApi()

    response = api.start_filter_run(
        {
            "input_path": str(csv_path),
            "output_path": str(output_path),
            "output_format": "xlsx",
            "split_mode": "files",
            "max_rows_per_sheet": 2,
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
        }
    )

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["type"] == "overwrite_confirmation_required"
    assert error["code"] == "overwrite_confirmation_required"
    assert error["paths"] == [str(existing_later_split)]
    assert error["context"] == {"paths": [str(existing_later_split)]}
    assert existing_later_split.read_text(encoding="utf-8") == "old contents\n"


def test_ui_api_runs_multi_input_export_to_output_folder(tmp_path: Path) -> None:
    first_path = tmp_path / "first.csv"
    second_path = tmp_path / "second.csv"
    output_dir = tmp_path / "outputs"
    first_path.write_text("Nome,Status\nAna,ATIVO\n", encoding="utf-8")
    second_path.write_text("Nome,Status\nBia,ATIVO\n", encoding="utf-8")
    output_dir.mkdir()
    api = DataSlicerApi()

    start_response = api.start_filter_run(
        {
            "input_paths": [str(first_path), str(second_path)],
            "output_path": str(output_dir),
            "output_format": "csv",
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
            "select": ["Nome"],
        }
    )

    assert start_response["ok"], start_response
    start_data = start_response["data"]
    assert isinstance(start_data, dict)
    job = wait_for_job(api, str(start_data["job_id"]))
    report = job["report"]
    assert isinstance(report, dict)
    assert report["output_rows"] == 2
    assert sorted(path.name for path in output_dir.glob("*.csv")) == [
        "001_first_filtered.csv",
        "002_second_filtered.csv",
    ]


def test_ui_api_string_false_booleans_remain_false(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.csv"
    write_people_csv(csv_path)
    api = DataSlicerApi()

    options = ui_api.build_options_from_payload(
        {
            "input_path": str(csv_path),
            "output_path": str(output_path),
            "output_format": "csv",
            "dedupe": "false",
            "dry_run": "false",
            "case_insensitive_columns": "false",
            "typed_mode": "false",
            "strict_values": "false",
            "summarize": "false",
            "summary_only": "false",
            "csv_options": {
                "delimiter": ",",
                "strict_mode": "false",
                "store_rejects": "false",
            },
        },
        require_output=True,
        force_dry_run=False,
    )

    assert options.dedupe is False
    assert options.dry_run is False
    assert options.case_insensitive_columns is False
    assert options.typed_mode is False
    assert options.strict_values is False
    assert not hasattr(options, "spreadsheet_safe_csv")
    assert options.summarize is False
    assert options.summary_only is False
    assert options.csv.strict_mode is False
    assert options.csv.store_rejects is False

    resolution_options = ui_api._input_resolution_options(  # noqa: SLF001 - regression for bridge parser.
        {"input_path": str(csv_path), "delete_zip_after_extract": "false", "all_excel_sheets": "false"}
    )
    assert resolution_options.delete_zip_after_extract is False
    assert resolution_options.excel_all_sheets is False

    config = ui_api._config_from_payload(  # noqa: SLF001 - regression for bridge parser.
        {"dedupe": "false", "summarize": "false", "summary_only": "false"}
    )
    assert "dedupe" not in config
    assert "summarize" not in config
    assert "summary_only" not in config
    assert api.get_app_info()["ok"] is True


def test_ui_api_rejects_ambiguous_boolean_text(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.csv"
    write_people_csv(csv_path)

    response = DataSlicerApi().start_filter_run(
        {
            "input_path": str(csv_path),
            "output_path": str(output_path),
            "output_format": "csv",
            "dedupe": "maybe",
        }
    )

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["type"] == "ConfigError"
    assert error["code"] == "boolean_value"
    assert error["context"] == {"key": "dedupe"}
    assert "dedupe" in str(error["message"])
    assert "dedupe" in str(error["details"])


def test_ui_api_rejects_invalid_integer_text_without_unexpected_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.xlsx"
    write_people_csv(csv_path)

    response = DataSlicerApi().start_filter_run(
        {
            "input_path": str(csv_path),
            "output_path": str(output_path),
            "output_format": "xlsx",
            "split_mode": "files",
            "max_rows_per_sheet": "many",
        }
    )

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["type"] == "ConfigError"
    assert error["code"] == "integer_value"
    assert error["context"] == {"key": "max_rows_per_sheet"}
    assert "número inteiro" in str(error["message"])
    assert "max_rows_per_sheet must be an integer" in str(error["details"])
    assert not output_path.exists()


def test_ui_api_rejects_unconfirmed_zip_deletion(tmp_path: Path) -> None:
    zip_path = tmp_path / "inputs.zip"
    output_path = tmp_path / "filtered.csv"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("data.csv", "ID\n1\n")

    response = DataSlicerApi().start_filter_run(
        {
            "input_path": str(zip_path),
            "output_path": str(output_path),
            "output_format": "csv",
            "delete_zip_after_extract": True,
        }
    )

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["code"] == "zip_delete_confirmation_required"
    assert error["context"] == {}
    assert "Confirme a exclusão do ZIP" in str(error["message"])
    assert zip_path.exists()


def test_ui_api_rejects_bad_csv_options_shape(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    write_people_csv(csv_path)

    response = DataSlicerApi().inspect_csv({"input_path": str(csv_path), "csv_options": "bad"})

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["code"] == "csv_options_type"
    assert error["context"] == {}
    assert "csv_options deve ser um objeto" in str(error["message"])


def test_ui_api_requires_input_and_output_with_structured_errors(tmp_path: Path) -> None:
    input_response = DataSlicerApi().inspect_csv({})

    assert input_response["ok"] is False
    input_error = input_response["error"]
    assert isinstance(input_error, dict)
    assert input_error["code"] == "ui_input_required"

    csv_path = tmp_path / "people.csv"
    write_people_csv(csv_path)
    output_response = DataSlicerApi().start_filter_run({"input_path": str(csv_path)})

    assert output_response["ok"] is False
    output_error = output_response["error"]
    assert isinstance(output_error, dict)
    assert output_error["code"] == "ui_output_required"


def test_ui_api_cancel_job_requests_running_job_cancellation() -> None:
    manager = JobManager()
    api = DataSlicerApi(job_manager=manager)
    entered = Event()
    release = Event()

    def runner(progress, register_cancel):
        register_cancel(lambda: None)
        progress("exporting")
        entered.set()
        release.wait(timeout=2)
        progress("finishing")
        report = RunReport(input_path="input.csv")
        report.finish()
        return report

    job = manager.start(runner, on_error=lambda exc: {"type": type(exc).__name__, "message": str(exc), "details": str(exc)})
    assert entered.wait(timeout=2)

    response = api.cancel_job(job.job_id)

    assert response["ok"], response
    data = response["data"]
    assert isinstance(data, dict)
    assert data["running"] is True
    assert data["cancel_requested"] is True
    assert data["phase"] == "canceling"
    release.set()
    for _attempt in range(50):
        final = api.get_job_status(job.job_id)
        assert final["ok"], final
        final_data = final["data"]
        assert isinstance(final_data, dict)
        if not final_data["running"]:
            break
        time.sleep(0.01)
    assert final_data["phase"] == "cancelled"


def test_ui_api_runs_xlsx_export(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.xlsx"
    write_people_csv(csv_path)
    api = DataSlicerApi()

    start_response = api.start_filter_run(
        {
            "input_path": str(csv_path),
            "output_path": str(output_path),
            "output_format": "xlsx",
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
            "select": ["Nome"],
        }
    )

    assert start_response["ok"], start_response
    start_data = start_response["data"]
    assert isinstance(start_data, dict)
    job = wait_for_job(api, str(start_data["job_id"]))
    assert job["phase"] == "done"
    workbook = load_workbook(output_path, read_only=True)
    rows = [tuple(row) for row in workbook["Results_001"].iter_rows(values_only=True)]
    assert rows == [("Nome",), ("Ana Silva",), ("Camila Silva",)]


def test_ui_api_runs_parquet_export_with_derived_column(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    output_path = tmp_path / "filtered.parquet"
    write_people_csv(csv_path)
    api = DataSlicerApi()

    start_response = api.start_filter_run(
        {
            "input_path": str(csv_path),
            "output_path": str(output_path),
            "output_format": "parquet",
            "csv_options": {"delimiter": ","},
            "filters": {
                "mode": "visual",
                "conditions": [{"column": "Status", "operator": "equals", "value": "ATIVO"}],
            },
            "select": ["Nome"],
            "derived_columns": [
                {
                    "source": "Nome",
                    "name": {"suffix": "LIMPO", "separator": "_"},
                    "transforms": [{"operation": "remove_accents"}, {"operation": "uppercase"}],
                }
            ],
        }
    )

    assert start_response["ok"], start_response
    start_data = start_response["data"]
    assert isinstance(start_data, dict)
    job = wait_for_job(api, str(start_data["job_id"]))
    assert job["phase"] == "done"
    rows = duckdb.connect().execute(f"SELECT * FROM read_parquet('{output_path.as_posix()}')").fetchall()
    assert rows == [("Ana Silva", "ANA SILVA"), ("Camila Silva", "CAMILA SILVA")]


def test_ui_api_returns_json_safe_errors(tmp_path: Path) -> None:
    csv_path = tmp_path / "people.csv"
    write_people_csv(csv_path)
    api = DataSlicerApi()

    response = api.start_filter_run(
        {
            "input_path": str(csv_path),
            "output_format": "csv",
            "filters": {"mode": "raw", "raw": "Status = 'ATIVO'"},
        }
    )

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert "Escolha onde salvar" in str(error["message"])


def test_ui_api_message_bundle_supports_both_languages() -> None:
    api = DataSlicerApi()

    pt = api.get_messages("pt-BR")
    en = api.get_messages("en-US")

    assert pt["ok"] is True
    assert en["ok"] is True
    assert pt["data"]["messages"]["ui.app_name"] == "DataSlicer"  # type: ignore[index]
    assert en["data"]["messages"]["ui.error.input_required"] == "Choose an input file before continuing."  # type: ignore[index]


def test_ui_api_loads_reusable_config_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "output_format: parquet",
                "split_mode: files",
                "max_rows_per_sheet: 1000",
                "sheets_per_file: 2",
                "where:",
                "  - Status = 'ATIVO'",
                "lookup:",
                "  - empresas=empresas.csv:ID",
                "select:",
                "  - Nome",
                "derived_columns:",
                "  - source: Nome",
                "    name:",
                "      suffix: LIMPO",
                "      separator: _",
                "    transforms:",
                "      - operation: uppercase",
            ]
        ),
        encoding="utf-8",
    )

    response = DataSlicerApi().load_config({"config_path": str(config_path)})

    assert response["ok"], response
    data = response["data"]
    assert isinstance(data, dict)
    assert data["path"] == str(config_path)
    config = data["config"]
    assert isinstance(config, dict)
    assert config["output_format"] == "parquet"
    assert config["split_mode"] == "files"
    assert config["max_rows_per_sheet"] == 1000
    assert config["sheets_per_file"] == 2
    assert "spreadsheet_safe_csv" not in config
    assert config["where"] == ["Status = 'ATIVO'"]
    assert config["lookup"] == [
        {"name": "empresas", "path": str(tmp_path / "empresas.csv"), "column": "ID"}
    ]
    assert config["derived_columns"][0]["source"] == "Nome"


def test_ui_api_rejects_missing_config_path() -> None:
    response = DataSlicerApi().load_config({})

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["code"] == "ui_config_required"
    assert error["context"] == {}
    assert "Escolha um arquivo de configuração" in str(error["message"])


def test_ui_api_rejects_config_keys_the_ui_cannot_apply_safely(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "output_format: csv",
                "strict_values: true",
                "csv_options:",
                "  header: false",
            ]
        ),
        encoding="utf-8",
    )

    response = DataSlicerApi().load_config({"config_path": str(config_path)})

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    details = str(error["details"])
    assert error["code"] == "ui_unsupported_config_keys"
    assert error["context"] == {"keys": "strict_values, csv_options.header"}
    assert "strict_values" in details
    assert "csv_options.header" in details


def test_ui_api_rejects_removed_spreadsheet_safe_csv_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("spreadsheet_safe_csv: true\n", encoding="utf-8")

    response = DataSlicerApi().load_config({"config_path": str(config_path)})

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["code"] == "ui_unsupported_config_keys"
    assert error["context"] == {"keys": "spreadsheet_safe_csv"}


def test_ui_api_choose_output_uses_folder_dialog_for_multi_file_runs(tmp_path: Path, monkeypatch) -> None:
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    calls: list[object] = []

    class FakeFileDialog:
        SAVE = object()
        FOLDER = object()

    class FakeWebview:
        FileDialog = FakeFileDialog

    class FakeWindow:
        def create_file_dialog(self, dialog_type, **_kwargs):
            calls.append(dialog_type)
            return (str(output_dir),)

    monkeypatch.setattr(ui_api, "_import_webview", lambda: FakeWebview)
    api = DataSlicerApi()
    api.bind_window(FakeWindow())

    response = api.choose_output_file("csv", True)

    assert response["ok"], response
    data = response["data"]
    assert isinstance(data, dict)
    assert data["path"] == str(output_dir)
    assert data["mode"] == "folder"
    assert calls == [FakeFileDialog.FOLDER]


def test_ui_api_choose_output_keeps_save_dialog_for_single_file_runs(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "output.csv"
    calls: list[tuple[object, dict[str, object]]] = []

    class FakeFileDialog:
        SAVE = object()
        FOLDER = object()

    class FakeWebview:
        FileDialog = FakeFileDialog

    class FakeWindow:
        def create_file_dialog(self, dialog_type, **kwargs):
            calls.append((dialog_type, kwargs))
            return (str(output_path),)

    monkeypatch.setattr(ui_api, "_import_webview", lambda: FakeWebview)
    api = DataSlicerApi()
    api.bind_window(FakeWindow())

    response = api.choose_output_file("csv", False)

    assert response["ok"], response
    data = response["data"]
    assert isinstance(data, dict)
    assert data["path"] == str(output_path)
    assert calls[0][0] is FakeFileDialog.SAVE
    assert calls[0][1]["save_filename"] == "resultado.csv"


def test_ui_api_saves_reusable_config_without_zip_passwords(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "config.yaml"

    class FakeFileDialog:
        SAVE = object()

    class FakeWebview:
        FileDialog = FakeFileDialog

    class FakeWindow:
        def create_file_dialog(self, *_args, **_kwargs):
            return (str(output_path),)

    writes: list[tuple[Path, str, str]] = []

    def fake_write_text_atomic(path: Path, text: str, *, encoding: str = "utf-8") -> None:
        writes.append((path, text, encoding))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding=encoding)

    monkeypatch.setattr(ui_api, "_import_webview", lambda: FakeWebview)
    monkeypatch.setattr(ui_api, "write_text_atomic", fake_write_text_atomic)
    api = DataSlicerApi()
    api.bind_window(FakeWindow())

    response = api.save_config(
        {
            "output_format": "parquet",
            "split_mode": "files",
            "max_rows_per_sheet": 1000,
            "sheets_per_file": 2,
            "summarize": True,
            "summary_only": True,
            "summary_group_by": ["Status"],
            "summary_totals": ["Valor"],
            "zip_passwords": ["secret"],
            "lookups": [{"name": "empresas", "path": "empresas.csv", "column": "ID"}],
            "filters": {"mode": "raw", "raw": "Status = 'ATIVO'"},
            "select": ["Nome"],
            "derived_columns": [
                {
                    "source": "Nome",
                    "name": {"suffix": "LIMPO", "separator": "_"},
                    "transforms": [{"operation": "uppercase"}],
                }
            ],
        }
    )

    assert response["ok"], response
    assert writes and writes[0][0] == output_path
    contents = output_path.read_text(encoding="utf-8")
    assert "output_format: parquet" in contents
    assert "split_mode: files" in contents
    assert "max_rows_per_sheet: 1000" in contents
    assert "sheets_per_file: 2" in contents
    assert "spreadsheet_safe_csv" not in contents
    assert "summarize: true" in contents
    assert "summary_only: true" in contents
    assert "summary_group_by:" in contents
    assert "- Status" in contents
    assert "summary_totals:" in contents
    assert "- Valor" in contents
    assert "lookup:" in contents
    assert "empresas=empresas.csv:ID" in contents
    assert "derived_columns:" in contents
    assert "secret" not in contents


def test_ui_api_rejects_incomplete_lookup_payload_without_dropping_it(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "config.yaml"

    class FakeFileDialog:
        SAVE = object()

    class FakeWebview:
        FileDialog = FakeFileDialog

    class FakeWindow:
        def create_file_dialog(self, *_args, **_kwargs):
            return (str(output_path),)

    monkeypatch.setattr(ui_api, "_import_webview", lambda: FakeWebview)
    api = DataSlicerApi()
    api.bind_window(FakeWindow())

    response = api.save_config({"lookups": [{"name": "empresas", "path": "empresas.csv", "column": ""}]})

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["type"] == "ConfigError"
    assert error["code"] == "lookup_missing_parts"
    assert error["context"] == {"item": "{'name': 'empresas', 'path': 'empresas.csv', 'column': ''}"}
    assert "Lookup must include NAME, PATH, and COLUMN" in str(error["details"])
    assert not output_path.exists()


def test_ui_api_save_config_rejects_invalid_integer_text(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "config.yaml"

    class FakeFileDialog:
        SAVE = object()

    class FakeWebview:
        FileDialog = FakeFileDialog

    class FakeWindow:
        def create_file_dialog(self, *_args, **_kwargs):
            return (str(output_path),)

    monkeypatch.setattr(ui_api, "_import_webview", lambda: FakeWebview)
    api = DataSlicerApi()
    api.bind_window(FakeWindow())

    response = api.save_config(
        {
            "output_format": "xlsx",
            "split_mode": "files",
            "sheets_per_file": "several",
        }
    )

    assert response["ok"] is False
    error = response["error"]
    assert isinstance(error, dict)
    assert error["code"] == "integer_value"
    assert error["context"] == {"key": "sheets_per_file"}
    assert "sheets_per_file must be an integer" in str(error["details"])
    assert not output_path.exists()
