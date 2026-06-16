"""Launcher used by PyInstaller to freeze the DataSlicer desktop UI."""

from __future__ import annotations


def main() -> None:
    from gt_dataslicer.ui.app import main as ui_main

    ui_main()


if __name__ == "__main__":
    main()

