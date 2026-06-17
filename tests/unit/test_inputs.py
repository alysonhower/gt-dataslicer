from pathlib import Path
import zipfile

from openpyxl import Workbook
import pyzipper
import pytest

from gt_dataslicer.exceptions import InputReadError, ZipPasswordRequiredError
from gt_dataslicer.inputs import (
    InputResolutionOptions,
    InputResolutionSession,
    detect_input_format,
    output_path_for_input,
)


def test_detect_input_format_supports_csv_parquet_and_xlsx() -> None:
    assert detect_input_format(Path("input.csv")) == "csv"
    assert detect_input_format(Path("input.parquet")) == "parquet"
    assert detect_input_format(Path("input.pq")) == "parquet"
    assert detect_input_format(Path("input.xlsx")) == "xlsx"
    assert detect_input_format(Path("input.xls")) is None


def test_xlsx_is_staged_from_first_sheet_by_default(tmp_path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Primeira"
    sheet.append(["A", "B"])
    sheet.append([1, "x"])
    second = workbook.create_sheet("Segunda")
    second.append(["A", "B"])
    second.append([2, "y"])
    xlsx_path = tmp_path / "input.xlsx"
    workbook.save(xlsx_path)

    with InputResolutionSession([xlsx_path]) as session:
        assert len(session.inputs) == 1
        resolved = session.inputs[0]
        assert resolved.format == "csv"
        assert resolved.excel_sheet == "Primeira"
        assert resolved.path.read_text(encoding="utf-8").splitlines() == ["A,B", "1,x"]


def test_xlsx_all_sheets_become_queue_items(tmp_path: Path) -> None:
    workbook = Workbook()
    workbook.active.title = "Aba 1"
    workbook.active.append(["A"])
    workbook.create_sheet("Aba 2").append(["B"])
    xlsx_path = tmp_path / "input.xlsx"
    workbook.save(xlsx_path)

    with InputResolutionSession([xlsx_path], options=InputResolutionOptions(excel_all_sheets=True)) as session:
        assert [item.excel_sheet for item in session.inputs] == ["Aba 1", "Aba 2"]


def test_xlsx_staging_paths_are_unique_for_duplicate_file_names(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    paths: list[Path] = []
    for directory, value in ((first_dir, "FIRST"), (second_dir, "SECOND")):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Dados"
        sheet.append(["VAL"])
        sheet.append([value])
        path = directory / "same.xlsx"
        workbook.save(path)
        paths.append(path)

    with InputResolutionSession(paths) as session:
        assert len(session.inputs) == 2
        assert session.inputs[0].path != session.inputs[1].path
        assert session.inputs[0].path.read_text(encoding="utf-8").splitlines() == ["VAL", "FIRST"]
        assert session.inputs[1].path.read_text(encoding="utf-8").splitlines() == ["VAL", "SECOND"]


def test_zip_extracts_supported_files_and_rejects_unsafe_paths(tmp_path: Path) -> None:
    zip_path = tmp_path / "input.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("data.csv", "A\n1\n")
        archive.writestr("ignore.txt", "nope")

    with InputResolutionSession([zip_path]) as session:
        assert len(session.inputs) == 1
        assert session.inputs[0].zip_source == zip_path
        assert session.inputs[0].zip_member == "data.csv"
        assert session.inputs[0].source_label == f"{zip_path}!data.csv"
        assert session.inputs[0].path.read_text(encoding="utf-8") == "A\n1\n"
        assert session.warnings == ["Unsupported ZIP entry skipped: ignore.txt"]

    unsafe_zip = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(unsafe_zip, "w") as archive:
        archive.writestr("../evil.csv", "A\n1\n")

    with pytest.raises(InputReadError, match="Unsafe ZIP entry path"):
        with InputResolutionSession([unsafe_zip]):
            pass


def test_encrypted_zip_requires_session_password(tmp_path: Path) -> None:
    zip_path = tmp_path / "secure.zip"
    with pyzipper.AESZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as archive:
        archive.setpassword(b"secret")
        archive.writestr("data.csv", "A\n1\n")

    with pytest.raises(ZipPasswordRequiredError):
        with InputResolutionSession([zip_path]):
            pass

    with InputResolutionSession([zip_path], options=InputResolutionOptions(zip_passwords=["secret"])) as session:
        assert len(session.inputs) == 1


def test_output_path_for_queue_uses_numbered_file_names(tmp_path: Path) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text("A\n1\n", encoding="utf-8")
    second.write_text("A\n2\n", encoding="utf-8")

    with InputResolutionSession([first, second]) as session:
        output = output_path_for_input(tmp_path / "filtered.csv", session.inputs[1], index=2, total=2, output_format="csv")

    assert output == tmp_path / "filtered_002_second.csv"


def test_output_path_for_directory_queue_keeps_duplicate_stems_unique(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    first = first_dir / "same.csv"
    second = second_dir / "same.csv"
    first.write_text("A\n1\n", encoding="utf-8")
    second.write_text("A\n2\n", encoding="utf-8")

    with InputResolutionSession([first, second]) as session:
        outputs = [
            output_path_for_input(output_dir, input_, index=index, total=2, output_format="csv")
            for index, input_ in enumerate(session.inputs, start=1)
        ]

    assert outputs == [
        output_dir / "001_same.csv",
        output_dir / "002_same.csv",
    ]
