"""
pytestの共通設定

PyQt6テストの共通フィクスチャと設定を提供します。
"""

import sys
import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """
    QApplicationのセッションスコープフィクスチャ

    テストセッション全体で1つのQApplicationインスタンスを使用します。
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def qapp_run(qapp, qtbot):
    """
    QApplicationイベントループを実行するフィクスチャ

    UIテストで非同期処理を待つために使用します。
    """
    return qtbot
