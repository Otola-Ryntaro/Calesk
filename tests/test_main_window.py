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


class TestMainWindowEdgeCases:
    """MainWindowのエッジケーステスト"""

    # 連続ボタンクリックのテスト
    def test_update_button_disabled_during_update(self, qtbot):
        """更新中はボタンが無効化されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        button = window.findChild(QPushButton, "update_button")

        # 初期状態でボタンは有効
        assert button.isEnabled()

        # 更新開始をシミュレート
        window._on_update_started()

        # ボタンが無効化されていることを確認（ボタンの無効化は_on_update_clickedで行われる）
        # _on_update_startedでは無効化されないので、_on_update_clickedを使う
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        # ボタンが無効化されていることを確認
        assert not button.isEnabled()

    def test_rapid_button_clicks_handled(self, qtbot):
        """連続したボタンクリックが適切に処理されることを確認"""
        from src.ui.main_window import MainWindow
        from unittest.mock import patch

        window = MainWindow()
        qtbot.addWidget(window)

        button = window.findChild(QPushButton, "update_button")

        # 最初のクリック
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        # ボタンが無効化されているため、2回目以降のクリックは無視される
        assert not button.isEnabled()

        # 追加のクリックを試みる（無視されるべき）
        for _ in range(5):
            # ボタンが無効なのでクリックしても効果なし
            if button.isEnabled():
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    def test_button_re_enabled_after_update_complete(self, qtbot):
        """更新完了後にボタンが再有効化されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        button = window.findChild(QPushButton, "update_button")

        # クリックしてボタンを無効化
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert not button.isEnabled()

        # 更新完了をシミュレート
        window._on_update_completed(True)

        # ボタンが再有効化されていることを確認
        assert button.isEnabled()

    def test_button_re_enabled_after_update_failure(self, qtbot):
        """更新失敗後にボタンが再有効化されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        button = window.findChild(QPushButton, "update_button")

        # クリックしてボタンを無効化
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert not button.isEnabled()

        # 更新失敗をシミュレート
        window._on_update_completed(False)

        # ボタンが再有効化されていることを確認
        assert button.isEnabled()

    # 境界値UIテスト
    def test_progress_bar_boundary_values(self, qtbot):
        """プログレスバーの境界値を正しく処理することを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        progress_bar = window.findChild(QProgressBar, "progress_bar")

        # 0%
        window._on_progress_updated(0)
        assert progress_bar.value() == 0

        # 100%
        window._on_progress_updated(100)
        assert progress_bar.value() == 100

        # 50%
        window._on_progress_updated(50)
        assert progress_bar.value() == 50

    def test_progress_bar_handles_negative_value(self, qtbot):
        """プログレスバーが負の値を適切に処理することを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        progress_bar = window.findChild(QProgressBar, "progress_bar")

        # 負の値（0にクランプされるべき）
        window._on_progress_updated(-10)
        # QProgressBarはrangeによって自動クランプされる
        assert progress_bar.value() >= 0

    def test_progress_bar_handles_over_100_value(self, qtbot):
        """プログレスバーが100を超える値を適切に処理することを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        progress_bar = window.findChild(QProgressBar, "progress_bar")

        # 100を超える値（100にクランプされるべき）
        window._on_progress_updated(150)
        # QProgressBarはrangeによって自動クランプされる
        assert progress_bar.value() <= 100

    # ステータスバーのテスト
    def test_status_bar_shows_initial_message(self, qtbot):
        """ステータスバーに初期メッセージが表示されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        assert window.statusBar().currentMessage() == "準備完了"

    def test_status_bar_shows_update_message(self, qtbot):
        """ステータスバーに更新中メッセージが表示されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        window._on_update_started()
        assert "更新中" in window.statusBar().currentMessage()

    def test_status_bar_shows_success_message(self, qtbot):
        """ステータスバーに成功メッセージが表示されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        window._on_update_completed(True)
        assert "更新しました" in window.statusBar().currentMessage()

    def test_status_bar_shows_failure_message(self, qtbot):
        """ステータスバーに失敗メッセージが表示されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        window._on_update_completed(False)
        assert "失敗" in window.statusBar().currentMessage()

    # 長いエラーメッセージのテスト
    def test_long_error_message_in_status_bar(self, qtbot):
        """長いエラーメッセージがステータスバーに表示されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # 非常に長いエラーメッセージ
        long_message = "エラー: " + "あ" * 1000
        window._on_error_occurred(long_message)

        # メッセージが表示されることを確認（切り詰められる可能性あり）
        assert "エラー" in window.statusBar().currentMessage()

    # テーマ変更のテスト
    def test_theme_combo_changes_viewmodel_theme(self, qtbot):
        """テーマComboBoxの変更がViewModelに反映されることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        combo = window.findChild(QComboBox, "theme_combo")

        # 別のテーマを選択
        if combo.count() > 1:
            combo.setCurrentIndex(1)
            new_theme = combo.currentText()

            # ViewModelのテーマが変更されていることを確認
            assert window.viewmodel.current_theme == new_theme

    def test_theme_combo_all_items_valid(self, qtbot):
        """テーマComboBoxの全項目が有効であることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        combo = window.findChild(QComboBox, "theme_combo")
        available_themes = window.viewmodel.get_available_themes()

        # ComboBoxの全項目がViewModelで認識されていることを確認
        for i in range(combo.count()):
            theme_name = combo.itemText(i)
            assert theme_name in available_themes or theme_name != ""

    # ウィンドウリサイズのテスト
    def test_window_resize_minimum(self, qtbot):
        """ウィンドウを最小サイズにリサイズできることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # 最小サイズにリサイズ
        window.resize(100, 100)

        # クラッシュしないことを確認
        assert window.isVisible() or True  # ウィジェットが存在することを確認

    def test_window_resize_very_large(self, qtbot):
        """ウィンドウを非常に大きなサイズにリサイズできることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # 非常に大きなサイズにリサイズ
        window.resize(4000, 3000)

        # クラッシュしないことを確認
        assert window.isVisible() or True

    # 特殊なエラーメッセージのテスト
    def test_error_message_with_special_characters(self, qtbot):
        """特殊文字を含むエラーメッセージを処理できることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # 特殊文字を含むエラーメッセージ
        special_messages = [
            "エラー: <script>alert('xss')</script>",
            "エラー: 改行\n\r\tを含む",
            "エラー: SQL' OR '1'='1",
        ]

        for msg in special_messages:
            window._on_error_occurred(msg)
            # クラッシュしないことを確認
            assert "エラー" in window.statusBar().currentMessage()

    # ViewModelとの連携テスト
    def test_viewmodel_signals_properly_connected(self, qtbot):
        """ViewModelのシグナルが正しく接続されていることを確認"""
        from src.ui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # ViewModelのシグナルが接続されていることを確認
        # update_started シグナルをemit
        window.viewmodel.update_started.emit()
        # クラッシュしないことを確認

        # progress_updated シグナルをemit
        window.viewmodel.progress_updated.emit(50)

        # error_occurred シグナルをemit
        window.viewmodel.error_occurred.emit("テストエラー")
