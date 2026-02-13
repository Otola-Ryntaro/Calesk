# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('backgrounds', 'backgrounds'),
        # credentials は含めない -- 実行時にユーザーのホームディレクトリから読み込む
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'google.oauth2',
        'google_auth_oauthlib',
        'googleapiclient',
        'googleapiclient.discovery',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'plyer.platforms.macosx.notification',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'pytest-qt',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Calesk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Calesk',
)
app = BUNDLE(
    coll,
    name='Calesk.app',
    icon='assets/Calesk.icns',
    bundle_identifier='com.tkojima.calesk',
    info_plist={
        'CFBundleDisplayName': 'Calesk',
        'CFBundleName': 'Calesk',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSSupportsAutomaticGraphicsSwitching': True,
        'LSUIElement': True,  # 常駐アプリのため Dock アイコンを非表示
    },
)
