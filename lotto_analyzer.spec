# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all


PROJECT_ROOT = Path(SPEC).resolve().parent

ICON_PATH = (
    PROJECT_ROOT
    / "assets"
    / "LottoAnalyzer.ico"
)

VERSION_FILE = (
    PROJECT_ROOT
    / "version_info.txt"
)


pillow_datas, pillow_binaries, pillow_hiddenimports = collect_all(
    "PIL"
)

reportlab_datas, reportlab_binaries, reportlab_hiddenimports = collect_all(
    "reportlab"
)


a = Analysis(
    [str(PROJECT_ROOT / "main.py")],
    pathex=[
        str(PROJECT_ROOT),
    ],
    binaries=(
        pillow_binaries
        + reportlab_binaries
    ),
    datas=[
        (
            str(ICON_PATH),
            "assets",
        ),
    ]
    + pillow_datas
    + reportlab_datas,
    hiddenimports=(
        pillow_hiddenimports
        + reportlab_hiddenimports
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)


pyz = PYZ(
    a.pure
)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Lotto Analyzer",
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
    icon=str(ICON_PATH),
    version=str(VERSION_FILE),
)