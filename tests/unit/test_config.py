import json
from pathlib import Path

import pytest

from gt_dataslicer.config import CsvOptions, load_config_file, merge_config_and_cli, select_preset
from gt_dataslicer.exceptions import ConfigError


def _merge_options(
    tmp_path: Path,
    *,
    output_name: str,
    preset_config: dict[str, object] | None = None,
    cli_output_format: str | None = None,
):
    return merge_config_and_cli(
        input_path=tmp_path / "input.csv",
        output_path=tmp_path / output_name,
        cli_output_format=cli_output_format,
        preset_config=preset_config or {},
        config_base_dir=None,
        cli_where=[],
        cli_select=[],
        select_file=None,
        cli_renames=[],
        cli_dedupe=False,
        cli_dedupe_keys=[],
        cli_sorts=[],
        cli_lookups=[],
        cli_types=[],
        cli_derived_columns=[],
        derived_columns_file=None,
        csv_options=CsvOptions(),
        sheet_prefix="Results",
        max_rows_per_sheet=1_048_576,
        split_mode="sheets",
        sheets_per_file=31,
        report_path=None,
        rejects_path=None,
        dry_run=False,
        case_insensitive_columns=False,
        typed_mode=False,
        strict_values=False,
        batch_size=10_000,
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
    with pytest.raises(ConfigError, match="conflicts with output path suffix"):
        _merge_options(tmp_path, output_name="result.xlsx", cli_output_format="csv")
