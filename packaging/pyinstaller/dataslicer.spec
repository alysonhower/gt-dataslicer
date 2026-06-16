# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the DataSlicer single-file desktop executable."""

from pathlib import Path


block_cipher = None
project_root = Path(SPECPATH).parents[1]
launcher = project_root / "packaging" / "pyinstaller" / "dataslicer_launcher.py"
web_assets = project_root / "src" / "gt_dataslicer" / "ui" / "web"


a = Analysis(
    [str(launcher)],
    pathex=[str(project_root), str(project_root / "src")],
    binaries=[],
    datas=[(str(web_assets), "gt_dataslicer/ui/web")],
    hiddenimports=[
        "duckdb",
        "lark",
        "yaml",
        "webview",
        "xlsxwriter",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# One-file mode is represented by creating EXE directly and not adding a COLLECT stage.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="DataSlicer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

