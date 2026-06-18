from types import SimpleNamespace
from threading import Event
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


def test_window_close_guard_cancels_only_while_job_is_running() -> None:
    handlers = []
    scripts = []
    notified = Event()

    class FakeEvent:
        def __iadd__(self, handler):
            handlers.append(handler)
            return self

    class FakeApi:
        running = True

        def has_running_job(self) -> bool:
            return self.running

    api = FakeApi()
    class FakeWindow:
        events = SimpleNamespace(closing=FakeEvent())

        def evaluate_js(self, script: str) -> None:
            scripts.append(script)
            notified.set()

    window = FakeWindow()

    ui_app._bind_close_guard(window, api)

    assert len(handlers) == 1
    assert handlers[0]() is False
    assert notified.wait(timeout=2)
    assert scripts == ["window.dataslicerNotifyCloseBlocked && window.dataslicerNotifyCloseBlocked()"]
    api.running = False
    assert handlers[0]() is True
    assert len(scripts) == 1


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
