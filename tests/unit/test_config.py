import json
from pathlib import Path

import pytest

from gt_dataslicer.config import (
    CsvOptions,
    as_list,
    load_config_file,
    merge_config_and_cli,
    parse_lookup_items,
    parse_output_format,
    parse_rename_items,
    parse_sort_items,
    parse_type_items,
    read_select_file,
    select_preset,
)
from gt_dataslicer.exceptions import ConfigError


def _merge_options(
    tmp_path: Path,
    *,
    output_name: str,
    preset_config: dict[str, object] | None = None,
    cli_output_format: str | None = None,
    csv_options: CsvOptions | None = None,
    select_file: Path | None = None,
    split_mode: str = "sheets",
    max_rows_per_sheet: int = 1_048_576,
    sheets_per_file: int = 31,
    batch_size: int = 10_000,
    rejects_path: Path | None = None,
    cli_summarize: bool = False,
    cli_summary_only: bool = False,
    cli_summary_group_by: list[str] | None = None,
    cli_summary_totals: list[str] | None = None,
):
    return merge_config_and_cli(
        input_path=tmp_path / "input.csv",
        output_path=tmp_path / output_name,
        cli_output_format=cli_output_format,
        preset_config=preset_config or {},
        config_base_dir=None,
        cli_where=[],
        cli_select=[],
        select_file=select_file,
        cli_summarize=cli_summarize,
        cli_summary_only=cli_summary_only,
        cli_summary_group_by=cli_summary_group_by or [],
        cli_summary_totals=cli_summary_totals or [],
        cli_renames=[],
        cli_dedupe=False,
        cli_dedupe_keys=[],
        cli_sorts=[],
        cli_lookups=[],
        cli_types=[],
        cli_derived_columns=[],
        derived_columns_file=None,
        cli_output_names=[],
        csv_options=csv_options or CsvOptions(),
        sheet_prefix="Results",
        max_rows_per_sheet=max_rows_per_sheet,
        split_mode=split_mode,
        sheets_per_file=sheets_per_file,
        report_path=None,
        rejects_path=rejects_path,
        dry_run=False,
        case_insensitive_columns=False,
        typed_mode=False,
        strict_values=False,
        batch_size=batch_size,
    )


@pytest.mark.parametrize(
    ("file_name", "contents"),
    [
        ("filters.yaml", "presets:\n  excel:\n    output_format: xlsx\n"),
        ("filters.json", json.dumps({"presets": {"excel": {"output_format": "xlsx"}}})),
        ("filters.toml", '[presets.excel]\noutput_format = "xlsx"\n'),
    ],
)
def test_output_format_config_presets_support_yaml_json_and_toml(
    tmp_path: Path,
    file_name: str,
    contents: str,
) -> None:
    config_path = tmp_path / file_name
    config_path.write_text(contents, encoding="utf-8")

    preset = select_preset(load_config_file(config_path), "excel")
    options = _merge_options(tmp_path, output_name="result", preset_config=preset)

    assert options.output_format == "xlsx"
    assert options.output_path == tmp_path / "result.xlsx"


def test_config_file_errors_are_structured(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.yaml"

    with pytest.raises(ConfigError, match="Config file not found") as missing_info:
        load_config_file(missing_path)

    assert missing_info.value.code == "config_file_not_found"
    assert missing_info.value.context == {"path": str(missing_path)}

    root_path = tmp_path / "root.yaml"
    root_path.write_text("- item\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="Config root") as root_info:
        load_config_file(root_path)

    assert root_info.value.code == "config_root_type"
    assert root_info.value.context == {}


def test_config_preset_errors_are_structured() -> None:
    with pytest.raises(ConfigError, match="pass --preset") as required_info:
        select_preset({"presets": {"ativos": {"where": "STATUS = 'ATIVO'"}}}, None)

    assert required_info.value.code == "config_preset_required"
    assert required_info.value.context == {}

    with pytest.raises(ConfigError, match="was not found") as missing_info:
        select_preset({"presets": {"ativos": {}}}, "inativos")

    assert missing_info.value.code == "config_preset_not_found"
    assert missing_info.value.context == {"preset": "inativos", "available": "ativos"}

    with pytest.raises(ConfigError, match="object/table") as type_info:
        select_preset({"presets": {"ativos": []}}, "ativos")

    assert type_info.value.code == "config_preset_type"
    assert type_info.value.context == {"preset": "ativos"}


def test_merge_config_enables_summary_when_summary_flags_are_set(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        cli_summarize=True,
        cli_summary_group_by=["STATUS"],
        cli_summary_totals=["VALOR_TOTAL"],
    )

    assert options.summarize is True
    assert options.summary_group_by == ["STATUS"]
    assert options.summary_totals == ["VALOR_TOTAL"]
    assert options.summary_only is False


def test_merge_config_enables_summary_from_preset_summary_only(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        preset_config={"summary_only": True},
    )

    assert options.summarize is True
    assert options.summary_only is True
    assert options.summary_group_by == []
    assert options.summary_totals == []


def test_merge_config_uses_summary_only_cli_flag(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        cli_summary_only=True,
    )

    assert options.summarize is True
    assert options.summary_only is True


def test_cli_output_format_overrides_config_output_format(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        preset_config={"output_format": "xlsx"},
        cli_output_format="csv",
    )

    assert options.output_format == "csv"
    assert options.output_path == tmp_path / "result.csv"


def test_output_format_supports_parquet_from_config_and_suffix(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        preset_config={"output_format": "parquet"},
    )

    assert options.output_format == "parquet"
    assert options.output_path == tmp_path / "result.parquet"

    suffix_options = _merge_options(tmp_path, output_name="result.parquet")

    assert suffix_options.output_format == "parquet"
    assert suffix_options.output_path == tmp_path / "result.parquet"


def test_cli_output_format_ignores_invalid_config_output_format(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        preset_config={"output_format": "nope"},
        cli_output_format="csv",
    )

    assert options.output_format == "csv"
    assert options.output_path == tmp_path / "result.csv"


def test_output_format_defaults_to_csv_for_paths_without_suffix(tmp_path: Path) -> None:
    options = _merge_options(tmp_path, output_name="result")

    assert options.output_format == "csv"
    assert options.output_path == tmp_path / "result.csv"


def test_output_format_rejects_conflicting_explicit_format_and_suffix(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="conflicts with output path suffix") as exc_info:
        _merge_options(tmp_path, output_name="result.xlsx", cli_output_format="csv")
    assert exc_info.value.code == "output_format_suffix_conflict"
    assert exc_info.value.context == {"output_format": "csv", "suffix": ".xlsx"}


def test_output_format_errors_are_structured(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="must be csv") as type_info:
        parse_output_format(123, source="--format")

    assert type_info.value.code == "output_format_type"
    assert type_info.value.context == {"source": "--format"}

    with pytest.raises(ConfigError, match="must be one of") as invalid_info:
        parse_output_format("pdf", source="--format")

    assert invalid_info.value.code == "output_format_invalid"
    assert invalid_info.value.context == {"source": "--format", "value": "pdf", "valid": "csv, parquet, xlsx"}

    with pytest.raises(ConfigError, match="Output path suffix") as suffix_info:
        _merge_options(tmp_path, output_name="result.txt", cli_output_format="csv")

    assert suffix_info.value.code == "output_suffix_invalid"
    assert suffix_info.value.context == {"suffix": ".txt"}


def test_select_file_errors_are_structured(tmp_path: Path) -> None:
    missing_path = tmp_path / "columns.txt"

    with pytest.raises(ConfigError, match="Select file not found") as exc_info:
        read_select_file(missing_path)

    assert exc_info.value.code == "select_file_not_found"
    assert exc_info.value.context == {"path": str(missing_path)}


def test_config_option_boundary_errors_are_structured(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="--split-mode") as split_info:
        _merge_options(tmp_path, output_name="result", split_mode="sideways")

    assert split_info.value.code == "split_mode"
    assert split_info.value.context == {"value": "sideways"}

    with pytest.raises(ConfigError, match="--max-rows-per-sheet") as rows_info:
        _merge_options(tmp_path, output_name="result", max_rows_per_sheet=1)

    assert rows_info.value.code == "max_rows_per_sheet"
    assert rows_info.value.context == {"min": 2, "max": 1_048_576, "value": 1}

    rejects_path = tmp_path / "rejects.csv"
    with pytest.raises(ConfigError, match="--rejects requires --store-rejects") as rejects_info:
        _merge_options(tmp_path, output_name="result", rejects_path=rejects_path)

    assert rejects_info.value.code == "rejects_requires_store_rejects"
    assert rejects_info.value.context == {"path": str(rejects_path)}


def test_config_dedupe_string_false_is_not_truthy(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        preset_config={"dedupe": "false"},
    )

    assert options.dedupe is False


def test_config_dedupe_rejects_unknown_boolean_text(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="dedupe") as exc_info:
        _merge_options(
            tmp_path,
            output_name="result",
            preset_config={"dedupe": "sometimes"},
        )
    assert exc_info.value.code == "config_boolean"
    assert exc_info.value.context == {"key": "dedupe"}


def test_config_no_longer_exposes_spreadsheet_safe_csv(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        preset_config={"spreadsheet_safe_csv": "true"},
    )

    assert not hasattr(options, "spreadsheet_safe_csv")


def test_lookup_item_errors_are_structured() -> None:
    with pytest.raises(ConfigError) as exc_info:
        parse_lookup_items(["ids=ids.csv:"])

    assert exc_info.value.code == "lookup_missing_parts"
    assert exc_info.value.context == {"item": "ids=ids.csv:"}


def test_config_string_list_errors_are_structured() -> None:
    with pytest.raises(ConfigError) as exc_info:
        as_list({"bad": "shape"}, key="lookup")

    assert exc_info.value.code == "config_string_list"
    assert exc_info.value.context == {"key": "lookup"}


def test_rename_item_errors_are_structured() -> None:
    with pytest.raises(ConfigError) as exc_info:
        parse_rename_items(["OLD="])

    assert exc_info.value.code == "rename_missing_parts"
    assert exc_info.value.context == {"item": "OLD="}


def test_sort_item_errors_are_structured() -> None:
    with pytest.raises(ConfigError) as exc_info:
        parse_sort_items(["STATUS:sideways"])

    assert exc_info.value.code == "sort_direction"
    assert exc_info.value.context == {"column": "STATUS", "direction": "sideways"}


def test_column_type_item_errors_are_structured() -> None:
    with pytest.raises(ConfigError) as exc_info:
        parse_type_items(["VALOR=money"])

    assert exc_info.value.code == "unsupported_column_type"
    assert exc_info.value.context == {
        "type": "money",
        "column": "VALOR",
        "valid": "bool, boolean, date, datetime, decimal, int, integer, string",
    }
