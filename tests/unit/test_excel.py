from pathlib import Path

from openpyxl import load_workbook

from gt_dataslicer.export.excel import ExcelExportOptions, export_rows_to_xlsx
from gt_dataslicer.report import RunReport


def test_summary_sheet_uses_finalized_report_values(tmp_path: Path) -> None:
    output_path = tmp_path / "output.xlsx"
    report = RunReport(input_path="input.csv")

    def finalize_report() -> None:
        report.rejected_rows = 7

    row_count = export_rows_to_xlsx(
        headers=["A"],
        rows=[["x"]],
        options=ExcelExportOptions(output_path=output_path),
        report=report,
        finalize_report=finalize_report,
    )

    workbook = load_workbook(output_path, read_only=True)
    summary = dict(workbook["_Summary"].iter_rows(values_only=True))
    assert row_count == 1
    assert summary["rejected_rows"] == 7


def test_string_values_are_not_exported_as_formulas_or_urls(tmp_path: Path) -> None:
    output_path = tmp_path / "output.xlsx"
    report = RunReport(input_path="input.csv")

    export_rows_to_xlsx(
        headers=["FormulaLike", "UrlLike"],
        rows=[["=1+1", "https://example.com"]],
        options=ExcelExportOptions(output_path=output_path),
        report=report,
    )

    workbook = load_workbook(output_path, data_only=False, read_only=False)
    worksheet = workbook["Results_001"]
    assert worksheet["A2"].data_type == "s"
    assert worksheet["A2"].value == "=1+1"
    assert worksheet["B2"].data_type == "s"
    assert worksheet["B2"].value == "https://example.com"
