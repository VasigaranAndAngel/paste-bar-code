# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('.\\src\\resources\\', 'resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Add pyzbar DLLs dynamically if they exist
import os
import sys
from pathlib import Path

def find_pyzbar_dlls():
    """Find pyzbar DLLs in the current environment"""
    dlls = []
    try:
        # Try to find pyzbar site-packages
        import pyzbar
        pyzbar_path = Path(pyzbar.__file__).parent
        
        # Look for DLLs in pyzbar directory
        for dll_name in ['libiconv.dll', 'libzbar-64.dll']:
            dll_path = pyzbar_path / dll_name
            if dll_path.exists():
                dlls.append((str(dll_path), 'pyzbar'))
            else:
                print(f"Warning: {dll_name} not found at {dll_path}")
    except ImportError:
        print("Warning: pyzbar not found during spec processing")
    except Exception as e:
        print(f"Warning: Error finding pyzbar DLLs: {e}")
    
    return dlls

# Add DLLs to binaries
pyzbar_dlls = find_pyzbar_dlls()
if pyzbar_dlls:
    a.binaries.extend(pyzbar_dlls)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Paste Bar Code',
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
