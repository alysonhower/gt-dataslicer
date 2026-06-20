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
    cli_summarize: bool = False,
    cli_summary_only: bool = False,
    cli_summary_group_by: list[str] | None = None,
    cli_summary_totals: list[str] | None = None,
    cli_output_names: list[str] | None = None,
    allow_output_directory: bool = False,
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
        cli_summarize=cli_summarize,
        cli_summary_only=cli_summary_only,
        cli_summary_group_by=cli_summary_group_by or [],
        cli_summary_totals=cli_summary_totals or [],
        cli_output_names=cli_output_names or [],
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
        allow_output_directory=allow_output_directory,
    )


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


def test_merge_config_enables_summarization_from_preset_summarization_only(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        preset_config={"summarization_only": True},
    )

    assert options.summarize is True
    assert options.summary_only is True
    assert options.summary_group_by == []
    assert options.summary_totals == []


def test_merge_config_keeps_legacy_summary_only_alias(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        preset_config={"summary_only": True},
    )

    assert options.summarize is True
    assert options.summary_only is True


def test_merge_config_uses_summary_only_cli_flag(tmp_path: Path) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        cli_summary_only=True,
    )

    assert options.summarize is True
    assert options.summary_only is True


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


@pytest.mark.parametrize("input_name", ["input.csv", "input.xlsx", "input.parquet"])
def test_output_format_defaults_to_csv_for_suffixless_cli_paths(
    tmp_path: Path,
    input_name: str,
) -> None:
    input_path = tmp_path / input_name

    options = merge_config_and_cli(
        input_path=input_path,
        output_path=tmp_path / "result",
        cli_output_format=None,
        preset_config={},
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
        cli_summarize=False,
        cli_summary_only=False,
        cli_summary_group_by=[],
        cli_summary_totals=[],
        cli_output_names=[],
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

    assert options.output_format == "csv"
    assert options.output_path == tmp_path / "result.csv"


@pytest.mark.parametrize(
    ("preset_config", "cli_summarize", "cli_summary_only"),
    [
        ({}, True, False),
        ({"summarization_only": True}, False, False),
    ],
)
def test_summary_outputs_default_to_xlsx_when_summary_is_enabled(
    tmp_path: Path,
    preset_config: dict[str, object],
    cli_summarize: bool,
    cli_summary_only: bool,
) -> None:
    options = _merge_options(
        tmp_path,
        output_name="result",
        preset_config=preset_config,
        cli_summarize=cli_summarize,
        cli_summary_only=cli_summary_only,
        cli_summary_group_by=["STATUS"],
        cli_summary_totals=["VALOR_TOTAL"],
    )

    assert options.output_format == "csv"
    assert options.output_path == tmp_path / "result.csv"
    assert options.summary_output_format == "xlsx"


def test_named_outputs_reject_file_destination(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        _merge_options(
            tmp_path,
            output_name="result.csv",
            cli_output_names=["resultado"],
        )


def test_ui_directory_named_outputs_do_not_change_cli_file_semantics(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    options = _merge_options(
        tmp_path,
        output_name="outputs",
        cli_output_names=["entrada_tratada.csv"],
        allow_output_directory=True,
    )

    assert options.output_path == output_dir
    assert options.output_names == ["entrada_tratada.csv"]

    cli_options = _merge_options(tmp_path, output_name="outputs")
    assert cli_options.output_path == tmp_path / "outputs.csv"


def test_output_format_rejects_conflicting_explicit_format_and_suffix(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="conflicts with output path suffix"):
        _merge_options(tmp_path, output_name="result.xlsx", cli_output_format="csv")
