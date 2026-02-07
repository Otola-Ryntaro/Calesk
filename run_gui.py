#!/usr/bin/env python
"""
GUIアプリケーション起動スクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """GUIアプリケーションを起動"""
    app = QApplication(sys.argv)
    app.setApplicationName("カレンダー壁紙アプリ")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
