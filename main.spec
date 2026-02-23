# -*- mode: python ; coding: utf-8 -*-

# region Prepare pyzbar dll paths to add them to binaries.
# NOTE: tried adding 'pyzbar' to hiddenimports. but didn't work for some reason.
from pathlib import Path

import pyzbar

pyzbar_path = Path(pyzbar.__file__).parent
libiconv_dll_path = pyzbar_path / "libiconv.dll"
libzbar_64_dll_path = pyzbar_path / "libzbar-64.dll"
# endregion

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[(libiconv_dll_path.as_posix(), "pyzbar"), (libzbar_64_dll_path.as_posix(), "pyzbar")],
    datas=[('.\\src\\resources\\', 'resources')],
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
    a.binaries,
    a.datas,
    [],
    name='Paste Bar Code',
    icon='src/resources/icon.ico',
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
)
