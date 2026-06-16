"""Pywebview launcher for the DataSlicer desktop UI."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from ..i18n import DEFAULT_LANGUAGE, set_language, tr
from .api import DataSlicerApi


WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 760
WINDOW_MIN_SIZE = (960, 640)
BACKGROUND_COLOR = "#FFFFFF"


def main(language: str = DEFAULT_LANGUAGE, *, debug: bool = False) -> None:
    """Launch the DataSlicer desktop UI."""

    set_language(language)
    webview = _import_webview()
    api = DataSlicerApi(language=language)

    index_resource = resources.files("gt_dataslicer.ui").joinpath("web", "index.html")
    with resources.as_file(index_resource) as index_path:
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
        webview.start(debug=debug, http_server=True)


def _import_webview() -> object:
    import webview

    return webview


if __name__ == "__main__":
    main()

