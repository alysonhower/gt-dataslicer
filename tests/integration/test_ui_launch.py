from types import SimpleNamespace
import sys

from typer.testing import CliRunner

from gt_dataslicer.cli import app
from gt_dataslicer.ui import app as ui_app


runner = CliRunner()


def test_cli_abrir_launches_ui(monkeypatch) -> None:
    called = {}

    def fake_main(*, language: str) -> None:
        called["language"] = language

    monkeypatch.setattr(ui_app, "main", fake_main)

    result = runner.invoke(app, ["abrir"])

    assert result.exit_code == 0, result.output
    assert called == {"language": "pt-BR"}


def test_cli_ui_alias_launches_ui_in_en_us(monkeypatch) -> None:
    called = {}

    def fake_main(*, language: str) -> None:
        called["language"] = language

    monkeypatch.setattr(ui_app, "main", fake_main)

    result = runner.invoke(app, ["--idioma", "en-US", "ui"])

    assert result.exit_code == 0, result.output
    assert called == {"language": "en-US"}


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

    ui_app.main()

    assert calls["title"] == "DataSlicer"
    assert calls["kwargs"]["width"] == 1180
    assert calls["kwargs"]["height"] == 760
    assert calls["kwargs"]["min_size"] == (960, 640)
    assert calls["kwargs"]["text_select"] is True
    assert str(calls["kwargs"]["url"]).endswith("index.html")
    assert calls["start"] == {"debug": False, "http_server": True}

