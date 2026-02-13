#!/usr/bin/env python
"""
GUIアプリケーション起動スクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

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


def _set_macos_dock_name(name: str):
    """macOSのDock表示名を設定（開発環境用）"""
    if sys.platform != 'darwin':
        return
    try:
        from Foundation import NSBundle
        bundle = NSBundle.mainBundle()
        info = bundle.infoDictionary()
        if info is not None:
            info['CFBundleName'] = name
    except ImportError:
        pass


def main():
    """GUIアプリケーションを起動"""
    _set_macos_dock_name("Calesk")
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
