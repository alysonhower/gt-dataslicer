from types import SimpleNamespace
import sys

from typer.testing import CliRunner

from gt_dataslicer.cli import app
from gt_dataslicer.ui import app as ui_app


runner = CliRunner()


def test_cli_abrir_launches_ui(monkeypatch) -> None:
    called = {}

    def fake_main(*, language: str, debug: bool) -> None:
        called["language"] = language
        called["debug"] = debug

    monkeypatch.setattr(ui_app, "main", fake_main)

    result = runner.invoke(app, ["abrir"])

    assert result.exit_code == 0, result.output
    assert called == {"language": "pt-BR", "debug": False}


def test_cli_ui_alias_launches_ui_in_en_us(monkeypatch) -> None:
    called = {}

    def fake_main(*, language: str, debug: bool) -> None:
        called["language"] = language
        called["debug"] = debug

    monkeypatch.setattr(ui_app, "main", fake_main)

    result = runner.invoke(app, ["--idioma", "en-US", "ui"])

    assert result.exit_code == 0, result.output
    assert called == {"language": "en-US", "debug": False}


def test_cli_abrir_pywebview_debug_flag_launches_debug_ui(monkeypatch) -> None:
    called = {}

    def fake_main(*, language: str, debug: bool) -> None:
        called["language"] = language
        called["debug"] = debug

    monkeypatch.setattr(ui_app, "main", fake_main)

    result = runner.invoke(app, ["abrir", "--pywebview-debug"])

    assert result.exit_code == 0, result.output
    assert called == {"language": "pt-BR", "debug": True}


def test_cli_abrir_help_hides_pywebview_debug_flag() -> None:
    result = runner.invoke(app, ["abrir", "--help"])

    assert result.exit_code == 0, result.output
    assert "pywebview-debug" not in result.output
    assert "depurar-pywebview" not in result.output


def test_dataslicer_entrypoint_builds_webview_window(monkeypatch) -> None:
    calls = {}

    def fake_create_window(title, **kwargs):
        calls["title"] = title
        calls["kwargs"] = kwargs
        return object()

    def fake_start(**kwargs):
        calls["start"] = kwargs

    fake_webview = SimpleNamespace(
        create_window=fake_create_window,
        start=fake_start,
        FileDialog=SimpleNamespace(OPEN="open", SAVE="save"),
    )
    monkeypatch.setitem(sys.modules, "webview", fake_webview)
    monkeypatch.setattr(ui_app.sys, "platform", "win32")

    ui_app.main()

    assert calls["title"] == "DataSlicer"
    assert calls["kwargs"]["width"] == 1180
    assert calls["kwargs"]["height"] == 760
    assert calls["kwargs"]["min_size"] == (960, 640)
    assert calls["kwargs"]["text_select"] is True
    assert str(calls["kwargs"]["url"]).endswith("index.html")
    assert calls["start"] == {"debug": False, "http_server": True}


def test_dataslicer_entrypoint_sets_runtime_icon_on_linux(monkeypatch) -> None:
    calls = {}

    def fake_create_window(title, **kwargs):
        calls["title"] = title
        calls["kwargs"] = kwargs
        return object()

    def fake_start(**kwargs):
        calls["start"] = kwargs

    fake_webview = SimpleNamespace(
        create_window=fake_create_window,
        start=fake_start,
        FileDialog=SimpleNamespace(OPEN="open", SAVE="save"),
    )
    monkeypatch.setitem(sys.modules, "webview", fake_webview)
    monkeypatch.setattr(ui_app.sys, "platform", "linux")

    ui_app.main()

    assert calls["start"]["debug"] is False
    assert calls["start"]["http_server"] is True
    assert calls["start"]["icon"].endswith("icon.png")


def test_runtime_icon_path_uses_packaged_png_on_linux() -> None:
    from contextlib import ExitStack

    with ExitStack() as stack:
        icon_path = ui_app._runtime_icon_path(stack, platform="linux")
        assert icon_path is not None
        assert icon_path.name == "icon.png"
        assert icon_path.exists()


def test_runtime_icon_path_is_omitted_on_windows() -> None:
    from contextlib import ExitStack

    with ExitStack() as stack:
        assert ui_app._runtime_icon_path(stack, platform="win32") is None
