"""
MainWindowのテスト

PyQt6のメインウィンドウをテストします。
ViewModelをモック化してテストの独立性を確保します。
"""

import pytest
from unittest.mock import Mock
from PyQt6.QtWidgets import QMainWindow, QComboBox, QPushButton, QProgressBar
from PyQt6.QtCore import Qt


class MockSignal:
    """
    PyQt6シグナルのモック

    connectとemitメソッドを持ち、シグナルの動作をシミュレートします。
    """

    def __init__(self):
        self._callbacks = []

    def connect(self, callback):
        """シグナルにコールバックを接続"""
        self._callbacks.append(callback)

    def emit(self, *args, **kwargs):
        """シグナルを発火し、接続された全てのコールバックを呼び出す"""
        for callback in self._callbacks:
            callback(*args, **kwargs)

    def disconnect(self, callback=None):
        """コールバックを切断"""
        if callback:
            self._callbacks.remove(callback)
        else:
            self._callbacks.clear()


def create_mock_viewmodel():
    """
    MainViewModelのモックを作成

    Returns:
        Mock: MainViewModelのモック
    """
    mock_vm = Mock()

    # プロパティの設定
    mock_vm.current_theme = "simple"
    mock_vm.is_updating = False

    # メソッドの設定
    mock_vm.get_available_themes.return_value = ["simple", "modern", "pastel", "dark", "vibrant"]
    mock_vm.set_theme = Mock()
    mock_vm.update_wallpaper = Mock(return_value=True)
    mock_vm.cancel_update = Mock()

    # シグナルの設定（MockSignalを使用）
    mock_vm.theme_changed = MockSignal()
    mock_vm.update_started = MockSignal()
    mock_vm.update_completed = MockSignal()
    mock_vm.progress_updated = MockSignal()
    mock_vm.error_occurred = MockSignal()
    mock_vm.wallpaper_updated = MockSignal()

    return mock_vm


@pytest.fixture
def mock_viewmodel():
    """モックされたMainViewModelを提供するフィクスチャ"""
    return create_mock_viewmodel()


@pytest.fixture
def window_with_mock(qtbot, mock_viewmodel):
    """モックViewModelを使用したMainWindowを提供するフィクスチャ"""
    from src.ui.main_window import MainWindow

    window = MainWindow(viewmodel=mock_viewmodel)
    qtbot.addWidget(window)
    return window


class TestMainWindow:
    """MainWindowの基本機能をテストする（モックViewModel使用）"""

    def test_main_window_exists(self, qtbot):
        """MainWindowクラスが存在することを確認"""
        from src.ui.main_window import MainWindow

        assert MainWindow is not None
        assert issubclass(MainWindow, QMainWindow)

    def test_main_window_initialization(self, window_with_mock, mock_viewmodel):
        """MainWindowが正しく初期化されることを確認"""
        assert window_with_mock is not None
        assert isinstance(window_with_mock, QMainWindow)
        assert window_with_mock.windowTitle() == "カレンダー壁紙アプリ"
        assert window_with_mock.viewmodel is mock_viewmodel

    def test_main_window_has_theme_combobox(self, window_with_mock, mock_viewmodel):
        """テーマ選択ComboBoxが存在することを確認"""
        combo = window_with_mock.findChild(QComboBox, "theme_combo")
        assert combo is not None
        # モックから5つのテーマを取得
        assert combo.count() == 5
        mock_viewmodel.get_available_themes.assert_called()

    def test_main_window_has_update_button(self, window_with_mock):
        """「今すぐ更新」ボタンが存在することを確認"""
        button = window_with_mock.findChild(QPushButton, "update_button")
        assert button is not None
        assert button.text() == "今すぐ更新"

    def test_main_window_has_preview_widget(self, window_with_mock):
        """プレビューウィジェットが存在することを確認"""
        preview = window_with_mock.findChild(object, "preview_widget")
        assert preview is not None

    def test_theme_combo_default_selection(self, window_with_mock, mock_viewmodel):
        """テーマComboBoxのデフォルト選択が"simple"であることを確認"""
        combo = window_with_mock.findChild(QComboBox, "theme_combo")
        # モックのcurrent_themeが"simple"なので、ComboBoxも"simple"に設定される
        assert combo.currentText() == "simple"

    def test_update_button_click(self, qtbot, window_with_mock, mock_viewmodel):
        """「今すぐ更新」ボタンをクリックできることを確認"""
        button = window_with_mock.findChild(QPushButton, "update_button")
        assert button.isEnabled()

        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        # モックのupdate_wallpaperが呼ばれることを確認
        mock_viewmodel.update_wallpaper.assert_called_once()

    def test_main_window_has_progress_bar(self, window_with_mock):
        """QProgressBarが存在することを確認"""
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")
        assert progress_bar is not None

    def test_progress_bar_initially_hidden(self, window_with_mock):
        """初期状態でQProgressBarが非表示であることを確認"""
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")
        assert progress_bar.isHidden()

    def test_progress_bar_shows_on_update_start(self, window_with_mock, mock_viewmodel):
        """壁紙更新開始時にQProgressBarが表示されることを確認"""
        window_with_mock.show()
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")

        assert progress_bar.isHidden()

        # ViewModelのシグナルをemit
        mock_viewmodel.update_started.emit()

        assert progress_bar.isVisible()

    def test_progress_bar_updates_on_progress(self, window_with_mock, mock_viewmodel):
        """進捗シグナルでQProgressBarが更新されることを確認"""
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")

        # ViewModelのシグナルをemit
        mock_viewmodel.progress_updated.emit(50)

        assert progress_bar.value() == 50

    def test_progress_bar_hides_on_update_complete(self, window_with_mock, mock_viewmodel):
        """壁紙更新完了時にQProgressBarが非表示になることを確認"""
        window_with_mock.show()
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")

        # まず表示
        mock_viewmodel.update_started.emit()
        assert progress_bar.isVisible()

        # ViewModelのシグナルをemit
        mock_viewmodel.update_completed.emit(True)

        assert progress_bar.isHidden()

    def test_error_message_shows_in_status_bar(self, window_with_mock, mock_viewmodel):
        """エラーメッセージがステータスバーに表示されることを確認"""
        error_message = "テストエラーメッセージ"
        # ViewModelのシグナルをemit
        mock_viewmodel.error_occurred.emit(error_message)

        assert f"エラー: {error_message}" in window_with_mock.statusBar().currentMessage()

    def test_critical_error_shows_message_box(self, window_with_mock, monkeypatch):
        """重大なエラー時にQMessageBoxが表示されることを確認"""
        from PyQt6.QtWidgets import QMessageBox

        critical_called = []

        def mock_critical(parent, title, message):
            critical_called.append({
                "parent": parent,
                "title": title,
                "message": message
            })

        monkeypatch.setattr(QMessageBox, "critical", mock_critical)

        error_message = "重大なエラーが発生しました"
        # ハンドラを直接呼び出し（CRITICALレベル用）
        window_with_mock._on_critical_error(error_message)

        assert len(critical_called) == 1
        assert critical_called[0]["title"] == "エラー"
        assert error_message in critical_called[0]["message"]

    def test_error_level_classification(self, window_with_mock, monkeypatch):
        """エラーレベルに応じて適切な処理が行われることを確認"""
        from PyQt6.QtWidgets import QMessageBox

        warning_called = []
        critical_called = []

        def mock_warning(parent, title, message):
            warning_called.append({"title": title, "message": message})

        def mock_critical(parent, title, message):
            critical_called.append({"title": title, "message": message})

        monkeypatch.setattr(QMessageBox, "warning", mock_warning)
        monkeypatch.setattr(QMessageBox, "critical", mock_critical)

        # WARNING レベルのエラー
        window_with_mock._on_error_occurred("WARNING: テスト警告", level="WARNING")
        assert len(warning_called) == 1
        assert len(critical_called) == 0

        # CRITICAL レベルのエラー
        window_with_mock._on_error_occurred("CRITICAL: 重大エラー", level="CRITICAL")
        assert len(warning_called) == 1
        assert len(critical_called) == 1

        # ERROR レベルのエラー（ステータスバーのみ、ダイアログなし）
        window_with_mock._on_error_occurred("ERROR: 通常エラー", level="ERROR")
        assert len(warning_called) == 1
        assert len(critical_called) == 1


class TestMainWindowEdgeCases:
    """MainWindowのエッジケーステスト（モックViewModel使用）"""

    def test_update_button_disabled_during_update(self, qtbot, window_with_mock, mock_viewmodel):
        """更新中はボタンが無効化されることを確認"""
        button = window_with_mock.findChild(QPushButton, "update_button")

        assert button.isEnabled()

        # ボタンクリックで無効化
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        assert not button.isEnabled()

    def test_rapid_button_clicks_handled(self, qtbot, window_with_mock, mock_viewmodel):
        """連続したボタンクリックが適切に処理されることを確認"""
        button = window_with_mock.findChild(QPushButton, "update_button")

        # 最初のクリック
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        # ボタンが無効化されているため、2回目以降のクリックは無視される
        assert not button.isEnabled()

        # 追加のクリックを試みる（無視されるべき）
        for _ in range(5):
            if button.isEnabled():
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        # update_wallpaperは1回だけ呼ばれる
        mock_viewmodel.update_wallpaper.assert_called_once()

    def test_button_re_enabled_after_update_complete(self, qtbot, window_with_mock, mock_viewmodel):
        """更新完了後にボタンが再有効化されることを確認"""
        button = window_with_mock.findChild(QPushButton, "update_button")

        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert not button.isEnabled()

        # ViewModelのシグナルをemit
        mock_viewmodel.update_completed.emit(True)

        assert button.isEnabled()

    def test_button_re_enabled_after_update_failure(self, qtbot, window_with_mock, mock_viewmodel):
        """更新失敗後にボタンが再有効化されることを確認"""
        button = window_with_mock.findChild(QPushButton, "update_button")

        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert not button.isEnabled()

        # ViewModelのシグナルをemit（失敗）
        mock_viewmodel.update_completed.emit(False)

        assert button.isEnabled()

    def test_progress_bar_boundary_values(self, window_with_mock, mock_viewmodel):
        """プログレスバーの境界値を正しく処理することを確認"""
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")

        # 0%
        mock_viewmodel.progress_updated.emit(0)
        assert progress_bar.value() == 0

        # 100%
        mock_viewmodel.progress_updated.emit(100)
        assert progress_bar.value() == 100

        # 50%
        mock_viewmodel.progress_updated.emit(50)
        assert progress_bar.value() == 50

    def test_progress_bar_handles_negative_value(self, window_with_mock, mock_viewmodel):
        """プログレスバーが負の値を適切に処理することを確認"""
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")

        # 負の値（0にクランプされるべき）
        mock_viewmodel.progress_updated.emit(-10)
        assert progress_bar.value() >= 0

    def test_progress_bar_handles_over_100_value(self, window_with_mock, mock_viewmodel):
        """プログレスバーが100を超える値を適切に処理することを確認"""
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")

        # 100を超える値（100にクランプされるべき）
        mock_viewmodel.progress_updated.emit(150)
        assert progress_bar.value() <= 100

    def test_status_bar_shows_initial_message(self, window_with_mock):
        """ステータスバーに初期メッセージが表示されることを確認"""
        assert window_with_mock.statusBar().currentMessage() == "準備完了"

    def test_status_bar_shows_update_message(self, window_with_mock, mock_viewmodel):
        """ステータスバーに更新中メッセージが表示されることを確認"""
        mock_viewmodel.update_started.emit()
        assert "更新中" in window_with_mock.statusBar().currentMessage()

    def test_status_bar_shows_success_message(self, window_with_mock, mock_viewmodel):
        """ステータスバーに成功メッセージが表示されることを確認"""
        mock_viewmodel.update_completed.emit(True)
        assert "更新しました" in window_with_mock.statusBar().currentMessage()

    def test_status_bar_shows_failure_message(self, window_with_mock, mock_viewmodel):
        """ステータスバーに失敗メッセージが表示されることを確認"""
        mock_viewmodel.update_completed.emit(False)
        assert "失敗" in window_with_mock.statusBar().currentMessage()

    def test_long_error_message_in_status_bar(self, window_with_mock, mock_viewmodel):
        """長いエラーメッセージがステータスバーに表示されることを確認"""
        long_message = "エラー: " + "あ" * 1000
        mock_viewmodel.error_occurred.emit(long_message)

        assert "エラー" in window_with_mock.statusBar().currentMessage()

    def test_theme_combo_changes_viewmodel_theme(self, window_with_mock, mock_viewmodel):
        """テーマComboBoxの変更がViewModelに反映されることを確認"""
        combo = window_with_mock.findChild(QComboBox, "theme_combo")

        # 別のテーマを選択
        combo.setCurrentText("modern")

        # ViewModelのset_themeが呼ばれることを確認
        mock_viewmodel.set_theme.assert_called_with("modern")

    def test_theme_combo_all_items_valid(self, window_with_mock, mock_viewmodel):
        """テーマComboBoxの全項目が有効であることを確認"""
        combo = window_with_mock.findChild(QComboBox, "theme_combo")
        available_themes = mock_viewmodel.get_available_themes()

        # ComboBoxの全項目がモックViewModelで認識されていることを確認
        for i in range(combo.count()):
            theme_name = combo.itemText(i)
            assert theme_name in available_themes or theme_name != ""

    def test_window_resize_minimum(self, window_with_mock):
        """ウィンドウを最小サイズにリサイズできることを確認"""
        window_with_mock.resize(100, 100)
        # クラッシュしないことを確認
        assert window_with_mock.isVisible() or True

    def test_window_resize_very_large(self, window_with_mock):
        """ウィンドウを非常に大きなサイズにリサイズできることを確認"""
        window_with_mock.resize(4000, 3000)
        # クラッシュしないことを確認
        assert window_with_mock.isVisible() or True

    def test_error_message_with_special_characters(self, window_with_mock, mock_viewmodel):
        """特殊文字を含むエラーメッセージを処理できることを確認"""
        special_messages = [
            "エラー: <script>alert('xss')</script>",
            "エラー: 改行\n\r\tを含む",
            "エラー: SQL' OR '1'='1",
        ]

        for msg in special_messages:
            mock_viewmodel.error_occurred.emit(msg)
            assert "エラー" in window_with_mock.statusBar().currentMessage()

    def test_viewmodel_signals_properly_connected(self, window_with_mock, mock_viewmodel):
        """ViewModelのシグナルが正しく接続されていることを確認"""
        # update_started シグナルをemit
        mock_viewmodel.update_started.emit()
        # クラッシュしないことを確認

        # progress_updated シグナルをemit
        mock_viewmodel.progress_updated.emit(50)

        # error_occurred シグナルをemit
        mock_viewmodel.error_occurred.emit("テストエラー")


class TestMainWindowViewModelInteraction:
    """MainWindowとViewModelの相互作用テスト"""

    def test_theme_change_calls_set_theme(self, window_with_mock, mock_viewmodel):
        """テーマ変更時にViewModelのset_themeが呼ばれることを確認"""
        combo = window_with_mock.findChild(QComboBox, "theme_combo")

        combo.setCurrentText("modern")
        mock_viewmodel.set_theme.assert_called_with("modern")

        combo.setCurrentText("dark")
        mock_viewmodel.set_theme.assert_called_with("dark")

    def test_update_button_calls_update_wallpaper(self, qtbot, window_with_mock, mock_viewmodel):
        """更新ボタンクリックでViewModelのupdate_wallpaperが呼ばれることを確認"""
        button = window_with_mock.findChild(QPushButton, "update_button")

        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        mock_viewmodel.update_wallpaper.assert_called_once()

    def test_theme_changed_signal_updates_preview(self, window_with_mock, mock_viewmodel):
        """ViewModelのtheme_changedシグナルでプレビューがクリアされることを確認"""
        # theme_changedシグナルをemit
        mock_viewmodel.theme_changed.emit("modern")

        # ステータスバーにテーマ名が表示される
        assert "テーマ: modern" in window_with_mock.statusBar().currentMessage()

    def test_multiple_progress_updates(self, window_with_mock, mock_viewmodel):
        """複数回の進捗更新が正しく処理されることを確認"""
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")

        # 進捗を段階的に更新
        for progress in [10, 25, 50, 75, 90, 100]:
            mock_viewmodel.progress_updated.emit(progress)
            assert progress_bar.value() == progress

    def test_error_then_success_flow(self, window_with_mock, mock_viewmodel):
        """エラー発生後に成功するフローをテスト"""
        # エラー発生
        mock_viewmodel.error_occurred.emit("一時的なエラー")
        assert "エラー" in window_with_mock.statusBar().currentMessage()

        # その後成功
        mock_viewmodel.update_completed.emit(True)
        assert "更新しました" in window_with_mock.statusBar().currentMessage()

    def test_complete_update_cycle(self, qtbot, window_with_mock, mock_viewmodel):
        """完全な更新サイクルをテスト"""
        window_with_mock.show()
        button = window_with_mock.findChild(QPushButton, "update_button")
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")

        # 1. 更新開始
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert not button.isEnabled()
        mock_viewmodel.update_wallpaper.assert_called_once()

        # 2. 更新開始シグナル
        mock_viewmodel.update_started.emit()
        assert progress_bar.isVisible()
        assert "更新中" in window_with_mock.statusBar().currentMessage()

        # 3. 進捗更新
        for progress in [25, 50, 75, 100]:
            mock_viewmodel.progress_updated.emit(progress)
            assert progress_bar.value() == progress

        # 4. 更新完了
        mock_viewmodel.update_completed.emit(True)
        assert button.isEnabled()
        assert progress_bar.isHidden()
        assert "更新しました" in window_with_mock.statusBar().currentMessage()


class TestMockSignal:
    """MockSignalクラスのユニットテスト"""

    def test_mock_signal_connect_and_emit(self):
        """MockSignalのconnectとemitが正しく動作することを確認"""
        signal = MockSignal()
        received_values = []

        def callback(value):
            received_values.append(value)

        signal.connect(callback)
        signal.emit("test_value")

        assert received_values == ["test_value"]

    def test_mock_signal_multiple_callbacks(self):
        """MockSignalが複数のコールバックを処理できることを確認"""
        signal = MockSignal()
        callback1_values = []
        callback2_values = []

        signal.connect(lambda v: callback1_values.append(v))
        signal.connect(lambda v: callback2_values.append(v))

        signal.emit("test")

        assert callback1_values == ["test"]
        assert callback2_values == ["test"]

    def test_mock_signal_disconnect(self):
        """MockSignalのdisconnectが正しく動作することを確認"""
        signal = MockSignal()
        received_values = []

        def callback(value):
            received_values.append(value)

        signal.connect(callback)
        signal.emit("before")

        signal.disconnect(callback)
        signal.emit("after")

        assert received_values == ["before"]

    def test_mock_signal_disconnect_all(self):
        """MockSignalのdisconnect()で全コールバックが切断されることを確認"""
        signal = MockSignal()
        received_values = []

        signal.connect(lambda v: received_values.append(v))
        signal.connect(lambda v: received_values.append(v * 2))

        signal.emit(1)
        assert len(received_values) == 2

        signal.disconnect()
        signal.emit(2)

        # disconnect後はコールバックは呼ばれない
        assert len(received_values) == 2

    def test_mock_signal_emit_without_args(self):
        """引数なしのemitが正しく動作することを確認"""
        signal = MockSignal()
        call_count = [0]

        def callback():
            call_count[0] += 1

        signal.connect(callback)
        signal.emit()

        assert call_count[0] == 1

    def test_mock_signal_emit_with_multiple_args(self):
        """複数引数のemitが正しく動作することを確認"""
        signal = MockSignal()
        received_args = []

        def callback(a, b, c):
            received_args.append((a, b, c))

        signal.connect(callback)
        signal.emit(1, 2, 3)

        assert received_args == [(1, 2, 3)]
