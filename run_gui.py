#!/usr/bin/env python
"""
GUIアプリケーション起動スクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# macOS Dock表示名の設定（PyQt6インポート前に実行する必要がある）
if sys.platform == 'darwin':
    try:
        from Foundation import NSBundle
        bundle = NSBundle.mainBundle()
        info = bundle.infoDictionary()
        if info is not None:
            info['CFBundleName'] = 'Calesk'
            info['CFBundleDisplayName'] = 'Calesk'
    except ImportError:
        pass
    # プロセス名を変更（Dockホバー表示用）
    import ctypes
    import ctypes.util
    _libc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))
    _libc.setprogname(b'Calesk')

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.ui.main_window import MainWindow


def _find_icon() -> str | None:
    """アイコンファイルのパスを返す（見つからなければNone）"""
    candidates = [
        Path(__file__).parent / 'assets' / 'icon_1024.png',
        Path(__file__).parent / 'assets' / 'Calesk.icns',
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


def main():
    """GUIアプリケーションを起動"""
    app = QApplication(sys.argv)
    app.setApplicationName("Calesk")

    icon_path = _find_icon()
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
