from importlib import metadata, util
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]


def test_manual_test_data_is_ignored_and_documented() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "manual-test-data/" in gitignore
    assert "manual-test-data" in readme
    assert "manual-test-data/" in agents


def test_project_has_no_cli_surface() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    direct_dependencies = set(pyproject["project"]["dependencies"])
    optional_dependencies = {
        dependency
        for dependencies in pyproject["project"].get("optional-dependencies", {}).values()
        for dependency in dependencies
    }
    entry_points = metadata.distribution("gt-dataslicer").entry_points

    assert not (ROOT / "src" / "gt_dataslicer" / "cli.py").exists()
    assert not (ROOT / "tests" / "integration" / "test_cli.py").exists()
    assert util.find_spec("gt_dataslicer.cli") is None
    assert "typer" not in direct_dependencies | optional_dependencies
    assert "rich" not in direct_dependencies | optional_dependencies
    assert not any(entry_point.name in {"gt-dataslicer", "dataslicer"} for entry_point in entry_points)
    assert not any(entry_point.value.startswith("gt_dataslicer.cli") for entry_point in entry_points)
