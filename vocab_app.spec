# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('simple.html', '.'),
        ('vocab_data.json', '.'),
        ('bbdc_vocab.json', '.'),
        ('books.json', '.'),
        ('assets/MAPLEMONO-NF-CN-REGULAR.TTF', 'assets'),
    ],
    hiddenimports=['webview', 'bottle', 'screeninfo'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='考研词汇背单词',
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
