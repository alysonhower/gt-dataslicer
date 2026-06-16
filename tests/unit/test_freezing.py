from importlib import util
from pathlib import Path

from gt_dataslicer.ui import app as ui_app


ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "packaging" / "pyinstaller" / "dataslicer.spec"
LAUNCHER_PATH = ROOT / "packaging" / "pyinstaller" / "dataslicer_launcher.py"
BUILD_SCRIPT_PATH = ROOT / "scripts" / "build-dataslicer.ps1"
PYPROJECT_PATH = ROOT / "pyproject.toml"


def test_pyinstaller_spec_includes_launcher_and_ui_assets() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")

    assert "dataslicer_launcher.py" in spec
    assert 'project_root / "src" / "gt_dataslicer" / "ui" / "web"' in spec
    assert "gt_dataslicer/ui/web" in spec
    assert 'project_root / "src" / "gt_dataslicer" / "filters" / "grammar.lark"' in spec
    assert "gt_dataslicer/filters" in spec
    assert 'project_root / "icon.png"' in spec
    assert "gt_dataslicer/ui" in spec
    assert "gtil-global-sub-brand-guidelines.pdf" not in spec
    assert "tests" not in spec


def test_package_metadata_includes_freeze_icon_dependencies() -> None:
    pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")

    assert '"pillow>=10"' in pyproject
    assert '"icon.png" = "gt_dataslicer/ui/icon.png"' in pyproject
    assert '"src/gt_dataslicer/filters/grammar.lark" = "gt_dataslicer/filters/grammar.lark"' in pyproject


def test_pyinstaller_spec_configures_single_file_dataslicer_exe() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")

    assert "name=\"DataSlicer\"" in spec
    assert "console=False" in spec
    assert "COLLECT(" not in spec
    assert "duckdb" in spec
    assert "webview" in spec
    assert "xlsxwriter" in spec
    assert "icon=str(icon_png)" in spec
    assert "icon=None" not in spec


def test_dataslicer_launcher_calls_ui_main(monkeypatch) -> None:
    called = {}

    def fake_main() -> None:
        called["main"] = True

    monkeypatch.setattr(ui_app, "main", fake_main)
    module_spec = util.spec_from_file_location("dataslicer_launcher_test", LAUNCHER_PATH)
    assert module_spec is not None
    assert module_spec.loader is not None
    module = util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    module.main()

    assert called == {"main": True}


def test_build_script_uses_canonical_spec_and_expected_output() -> None:
    script = BUILD_SCRIPT_PATH.read_text(encoding="utf-8")

    assert "$ErrorActionPreference = \"Stop\"" in script
    assert "packaging\\pyinstaller\\dataslicer.spec" in script
    assert "python -m PyInstaller" in script
    assert "Get-Command python" in script
    assert "Get-Command uv" in script
    assert "Invoke-PythonBuild" in script
    assert "Invoke-UvBuild" in script
    assert "Falling back to uv" in script
    assert "uv run --extra freeze python -m PyInstaller" in script
    assert "-not $buildSucceeded -and $uvCommand" in script
    assert "--noconfirm --clean" in script
    assert "dist\\DataSlicer.exe" in script
