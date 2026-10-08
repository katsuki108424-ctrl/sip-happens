# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


racine = Path(SPECPATH)

analyse = Analysis(
    [str(racine / "main.py")],
    pathex=[str(racine)],
    binaries=[],
    datas=[(str(racine / "assets"), "assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
archive_python = PYZ(analyse.pure)

executable = EXE(
    archive_python,
    analyse.scripts,
    analyse.binaries,
    analyse.datas,
    [],
    name="Sip Happens",
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
    icon=[str(racine / "assets" / "icon" / "sip-happens.ico")],
)
