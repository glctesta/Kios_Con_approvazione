# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file per Kiosk Reports Service
Uso: pyinstaller build_service.spec
"""

block_cipher = None

a = Analysis(
    ['service_wrapper.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('db_config.enc', '.'),  # Include configurazione DB se esiste
    ],
    hiddenimports=[
        'win32timezone',
        'win32service',
        'win32serviceutil',
        'win32event',
        'servicemanager',
        'pyodbc',
        'schedule',
        'config_manager',
        'db_connection',
        'email_connector',
        'service_kiosk_reports',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KioskReportsService',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # True per vedere output durante debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Aggiungi path a .ico se disponibile
)
