# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_packaged.py'],
    pathex=[],
    binaries=[],
    datas=[('api', 'api'), ('algorithms', 'algorithms'), ('utils', 'utils')],
    hiddenimports=['flask', 'flask_cors', 'loguru', 'numpy', 'scipy', 'pandas', 'sklearn', 'sympy', 'gplearn', 'pysr', 'matplotlib', 'seaborn', 'plotly', 'openpyxl', 'xlrd', 'python-dotenv', 'pydantic'],
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
    name='tcm-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
