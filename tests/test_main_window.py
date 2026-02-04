"""
MainWindowのテスト

PyQt6のメインウィンドウをテストします。
"""

import pytest
from PyQt6.QtWidgets import QMainWindow, QComboBox, QPushButton, QProgressBar
from PyQt6.QtCore import Qt


class TestMainWindow:
    """MainWindowの基本機能をテストする"""

    def test_main_window_exists(self, qtbot):
        """MainWindowクラスが存在することを確認"""
        from src.ui.main_window import MainWindow

        assert MainWindow is not None
        assert issubclass(MainWindow, QMainWindow)

    def test_main_window_initialization(self, qtbot):
        """MainWindowが正しく初期化されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        assert window is not None
        assert isinstance(window, QMainWindow)
        assert window.windowTitle() == "カレンダー壁紙アプリ"

    def test_main_window_has_theme_combobox(self, qtbot):
        """テーマ選択ComboBoxが存在することを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # ComboBoxを検索
        combo = window.findChild(QComboBox, "theme_combo")
        assert combo is not None
        assert combo.count() >= 5  # 最低5つのテーマ（simple, modern, pastel, dark, vibrant）

    def test_main_window_has_update_button(self, qtbot):
        """「今すぐ更新」ボタンが存在することを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # ボタンを検索
        button = window.findChild(QPushButton, "update_button")
        assert button is not None
        assert button.text() == "今すぐ更新"

    def test_main_window_has_preview_widget(self, qtbot):
        """プレビューウィジェットが存在することを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # PreviewWidgetを検索
        preview = window.findChild(object, "preview_widget")
        assert preview is not None

    def test_theme_combo_default_selection(self, qtbot):
        """テーマComboBoxのデフォルト選択が"simple"であることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        combo = window.findChild(QComboBox, "theme_combo")
        assert combo.currentText() == "simple"

    def test_update_button_click(self, qtbot):
        """「今すぐ更新」ボタンをクリックできることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        button = window.findChild(QPushButton, "update_button")
        # ボタンが有効であることを確認
        assert button.isEnabled()

        # ボタンクリックをシミュレート
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        # クリック後の動作は別途テスト

    def test_main_window_has_progress_bar(self, qtbot):
        """QProgressBarが存在することを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # ProgressBarを検索
        progress_bar = window.findChild(QProgressBar, "progress_bar")
        assert progress_bar is not None

    def test_progress_bar_initially_hidden(self, qtbot):
        """初期状態でQProgressBarが非表示であることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        progress_bar = window.findChild(QProgressBar, "progress_bar")
        assert progress_bar.isHidden()

    def test_progress_bar_shows_on_update_start(self, qtbot):
        """壁紙更新開始時にQProgressBarが表示されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()  # ウィンドウを表示

        progress_bar = window.findChild(QProgressBar, "progress_bar")

        # 初期状態で非表示であることを確認
        assert progress_bar.isHidden()

        # update_started ハンドラを直接呼び出し
        window._on_update_started()

        # ProgressBarが表示されることを確認
        assert progress_bar.isVisible()

    def test_progress_bar_updates_on_progress(self, qtbot):
        """進捗シグナルでQProgressBarが更新されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        progress_bar = window.findChild(QProgressBar, "progress_bar")

        # progress_updated ハンドラを直接呼び出し
        window._on_progress_updated(50)

        # ProgressBarの値が更新されることを確認
        assert progress_bar.value() == 50

    def test_progress_bar_hides_on_update_complete(self, qtbot):
        """壁紙更新完了時にQProgressBarが非表示になることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()  # ウィンドウを表示

        progress_bar = window.findChild(QProgressBar, "progress_bar")

        # まず表示
        window._on_update_started()
        assert progress_bar.isVisible()

        # update_completed ハンドラを直接呼び出し
        window._on_update_completed(True)

        # ProgressBarが非表示になることを確認
        assert progress_bar.isHidden()

    # MEDIUM-6: エラーフィードバック改善テスト
    def test_error_message_shows_in_status_bar(self, qtbot):
        """エラーメッセージがステータスバーに表示されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # エラーハンドラを直接呼び出し
        error_message = "テストエラーメッセージ"
        window._on_error_occurred(error_message)

        # ステータスバーにエラーが表示される
        assert f"エラー: {error_message}" in window.statusBar().currentMessage()

    def test_critical_error_shows_message_box(self, qtbot, monkeypatch):
        """重大なエラー時にQMessageBoxが表示されることを確認"""
        from src.ui.main_window import MainWindow
        from PyQt6.QtWidgets import QMessageBox

        window = MainWindow()
        qtbot.addWidget(window)

        # QMessageBox.critical のモック
        critical_called = []

        def mock_critical(parent, title, message):
            critical_called.append({
                "parent": parent,
                "title": title,
                "message": message
            })

        monkeypatch.setattr(QMessageBox, "critical", mock_critical)

        # 重大なエラーハンドラを直接呼び出し
        error_message = "重大なエラーが発生しました"
        window._on_critical_error(error_message)

        # QMessageBox.criticalが呼ばれたことを確認
        assert len(critical_called) == 1
        assert critical_called[0]["title"] == "エラー"
        assert error_message in critical_called[0]["message"]

    def test_error_level_classification(self, qtbot, monkeypatch):
        """エラーレベルに応じて適切な処理が行われることを確認"""
        from src.ui.main_window import MainWindow
        from PyQt6.QtWidgets import QMessageBox

        window = MainWindow()
        qtbot.addWidget(window)

        # QMessageBox のモック
        warning_called = []
        critical_called = []

        def mock_warning(parent, title, message):
            warning_called.append({"title": title, "message": message})

        def mock_critical(parent, title, message):
            critical_called.append({"title": title, "message": message})

        monkeypatch.setattr(QMessageBox, "warning", mock_warning)
        monkeypatch.setattr(QMessageBox, "critical", mock_critical)

        # WARNING レベルのエラー
        window._on_error_occurred("WARNING: テスト警告", level="WARNING")
        assert len(warning_called) == 1
        assert len(critical_called) == 0

        # CRITICAL レベルのエラー
        window._on_error_occurred("CRITICAL: 重大エラー", level="CRITICAL")
        assert len(warning_called) == 1
        assert len(critical_called) == 1

        # ERROR レベルのエラー（ステータスバーのみ、ダイアログなし）
        window._on_error_occurred("ERROR: 通常エラー", level="ERROR")
        assert len(warning_called) == 1  # 変化なし
        assert len(critical_called) == 1  # 変化なし
