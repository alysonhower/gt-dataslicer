"""Pywebview launcher for the DataSlicer desktop UI."""

from __future__ import annotations

from contextlib import ExitStack
from importlib import resources
from pathlib import Path
import sys

from ..i18n import DEFAULT_LANGUAGE, set_language, tr
from .api import DataSlicerApi


WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 760
WINDOW_MIN_SIZE = (960, 640)
BACKGROUND_COLOR = "#FFFFFF"
RUNTIME_ICON_PLATFORMS = ("linux",)


def main(language: str = DEFAULT_LANGUAGE, *, debug: bool = False) -> None:
    """Launch the DataSlicer desktop UI."""

    set_language(language)
    webview = _import_webview()
    api = DataSlicerApi(language=language)

    index_resource = resources.files("gt_dataslicer.ui").joinpath("web", "index.html")
    with ExitStack() as stack:
        index_path = stack.enter_context(resources.as_file(index_resource))
        icon_path = _runtime_icon_path(stack)
        window = webview.create_window(
            tr("ui.app_name"),
            url=str(Path(index_path)),
            js_api=api,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            min_size=WINDOW_MIN_SIZE,
            background_color=BACKGROUND_COLOR,
            text_select=True,
        )
        api.bind_window(window)
        start_kwargs: dict[str, object] = {"debug": debug, "http_server": True}
        if icon_path is not None:
            start_kwargs["icon"] = str(icon_path)
        webview.start(**start_kwargs)


def _import_webview() -> object:
    import webview

    return webview


def _runtime_icon_path(stack: ExitStack, *, platform: str | None = None) -> Path | None:
    platform = platform or sys.platform
    if not platform.startswith(RUNTIME_ICON_PLATFORMS):
        return None
    icon_resource = resources.files("gt_dataslicer.ui").joinpath("icon.png")
    if not icon_resource.is_file():
        source_icon = Path(__file__).resolve().parents[3] / "icon.png"
        return source_icon if source_icon.is_file() else None
    return stack.enter_context(resources.as_file(icon_resource))


if __name__ == "__main__":
    main()
