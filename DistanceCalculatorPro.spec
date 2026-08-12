# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path(SPECPATH)
presentation = project_root / "app" / "presentation"

datas = [
    (
        str(presentation / "styles"),
        "app/presentation/styles",
    ),
    (
        str(presentation / "resources"),
        "app/presentation/resources",
    ),
    (
        str(project_root / "build" / "bundled-browser" / "chromium"),
        "app/browser/chromium",
    ),
]

a = Analysis(
    ["app/__main__.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DistanceCalculatorPro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=[],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DistanceCalculatorPro",
)
