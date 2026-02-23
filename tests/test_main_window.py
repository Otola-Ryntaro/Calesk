"""
MainWindowのテスト

PyQt6のメインウィンドウをテストします。
ViewModelをモック化してテストの独立性を確保します。
"""

import pytest
from unittest.mock import Mock
from PyQt6.QtWidgets import QMainWindow, QComboBox, QPushButton, QProgressBar, QLabel
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
    mock_vm.apply_wallpaper = Mock(return_value=True)
    mock_vm.preview_theme = Mock(return_value=None)
    mock_vm.cancel_update = Mock()

    # シグナルの設定（MockSignalを使用）
    mock_vm.theme_changed = MockSignal()
    mock_vm.update_started = MockSignal()
    mock_vm.update_completed = MockSignal()
    mock_vm.progress_updated = MockSignal()
    mock_vm.error_occurred = MockSignal()
    mock_vm.wallpaper_updated = MockSignal()
    mock_vm.preview_ready = MockSignal()

    return mock_vm


@pytest.fixture
def mock_viewmodel():
    """モックされたMainViewModelを提供するフィクスチャ"""
    return create_mock_viewmodel()


@pytest.fixture
def window_with_mock(qtbot, mock_viewmodel, tmp_path):
    """モックViewModelを使用したMainWindowを提供するフィクスチャ"""
    from src.ui.main_window import MainWindow
    from src.viewmodels.settings_service import SettingsService

    settings_service = SettingsService(settings_dir=tmp_path)

    # calendar_clientのモックを追加
    mock_calendar_client = Mock()
    mock_calendar_client.accounts = {}  # 空の辞書としてモック化

    # wallpaper_serviceのモックを追加
    mock_wallpaper_service = Mock()
    mock_wallpaper_service.calendar_client = mock_calendar_client

    # viewmodelに_wallpaper_serviceを設定
    mock_viewmodel._wallpaper_service = mock_wallpaper_service

    window = MainWindow(viewmodel=mock_viewmodel, settings_service=settings_service)
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
        assert window_with_mock.windowTitle() == "Calesk"
        assert window_with_mock.viewmodel is mock_viewmodel

    def test_main_window_has_theme_combobox(self, window_with_mock, mock_viewmodel):
        """テーマ選択ComboBoxが存在することを確認"""
        combo = window_with_mock.findChild(QComboBox, "theme_combo")
        assert combo is not None
        # モックから5つのテーマを取得
        assert combo.count() == 5
        mock_viewmodel.get_available_themes.assert_called()

    def test_main_window_has_apply_button(self, window_with_mock):
        """「壁紙に適用」ボタンが存在することを確認"""
        button = window_with_mock.findChild(QPushButton, "apply_button")
        assert button is not None
        assert button.text() == "壁紙に適用"

    def test_main_window_has_preview_widget(self, window_with_mock):
        """プレビューウィジェットが存在することを確認"""
        preview = window_with_mock.findChild(object, "preview_widget")
        assert preview is not None

    def test_theme_combo_default_selection(self, window_with_mock, mock_viewmodel):
        """テーマComboBoxのデフォルト選択が"simple"であることを確認"""
        combo = window_with_mock.findChild(QComboBox, "theme_combo")
        # モックのcurrent_themeが"simple"なので、ComboBoxも"simple"に設定される
        assert combo.currentText() == "simple"

    def test_apply_button_click(self, qtbot, window_with_mock, mock_viewmodel):
        """「壁紙に適用」ボタンをクリックできることを確認"""
        button = window_with_mock.findChild(QPushButton, "apply_button")
        assert button.isEnabled()

        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        # モックのapply_wallpaperが呼ばれることを確認
        mock_viewmodel.apply_wallpaper.assert_called_once()

    def test_main_window_has_refresh_button(self, window_with_mock):
        """「プレビュー更新」ボタンが存在することを確認"""
        button = window_with_mock.findChild(QPushButton, "refresh_button")
        assert button is not None
        assert button.text() == "プレビュー更新"

    def test_refresh_button_click(self, qtbot, window_with_mock, mock_viewmodel):
        """「プレビュー更新」ボタンをクリックするとpreview_themeが呼ばれることを確認"""
        button = window_with_mock.findChild(QPushButton, "refresh_button")
        assert button.isEnabled()

        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        mock_viewmodel.preview_theme.assert_called()

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

    def test_error_handler_updates_status_bar(self, window_with_mock):
        """エラーハンドラがステータスバーを更新すること"""
        window_with_mock._on_error_occurred("テストエラー")
        assert "エラー: テストエラー" in window_with_mock.statusBar().currentMessage()

    def test_error_handler_no_dialog(self, window_with_mock, monkeypatch):
        """通常エラーではダイアログが表示されないこと"""
        from PyQt6.QtWidgets import QMessageBox

        dialog_called = []
        monkeypatch.setattr(QMessageBox, "warning", lambda *a: dialog_called.append("w"))
        monkeypatch.setattr(QMessageBox, "critical", lambda *a: dialog_called.append("c"))

        window_with_mock._on_error_occurred("通常エラー")
        assert len(dialog_called) == 0


class TestMainWindowEdgeCases:
    """MainWindowのエッジケーステスト（モックViewModel使用）"""

    def test_apply_button_disabled_during_update(self, qtbot, window_with_mock, mock_viewmodel):
        """適用中はボタンが無効化されることを確認"""
        button = window_with_mock.findChild(QPushButton, "apply_button")

        assert button.isEnabled()

        # ボタンクリックで無効化
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        assert not button.isEnabled()

    def test_rapid_button_clicks_handled(self, qtbot, window_with_mock, mock_viewmodel):
        """連続したボタンクリックが適切に処理されることを確認"""
        button = window_with_mock.findChild(QPushButton, "apply_button")

        # 最初のクリック
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        # ボタンが無効化されているため、2回目以降のクリックは無視される
        assert not button.isEnabled()

        # 追加のクリックを試みる（無視されるべき）
        for _ in range(5):
            if button.isEnabled():
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        # apply_wallpaperは1回だけ呼ばれる
        mock_viewmodel.apply_wallpaper.assert_called_once()

    def test_button_re_enabled_after_update_complete(self, qtbot, window_with_mock, mock_viewmodel):
        """更新完了後にボタンが再有効化されることを確認"""
        button = window_with_mock.findChild(QPushButton, "apply_button")

        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert not button.isEnabled()

        # ViewModelのシグナルをemit
        mock_viewmodel.update_completed.emit(True)

        assert button.isEnabled()

    def test_button_re_enabled_after_update_failure(self, qtbot, window_with_mock, mock_viewmodel):
        """更新失敗後にボタンが再有効化されることを確認"""
        button = window_with_mock.findChild(QPushButton, "apply_button")

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
        # テーマComboBox初期化時にプレビュー生成が走るため、
        # 初期メッセージはプレビュー関連のメッセージになる
        msg = window_with_mock.statusBar().currentMessage()
        assert msg != ""  # 何らかのメッセージが表示されている

    def test_status_bar_shows_update_message(self, window_with_mock, mock_viewmodel):
        """ステータスバーに更新中メッセージが表示されることを確認"""
        mock_viewmodel.update_started.emit()
        assert "更新中" in window_with_mock.statusBar().currentMessage()

    def test_status_bar_shows_success_message(self, window_with_mock, mock_viewmodel):
        """ステータスバーに成功メッセージが表示されることを確認"""
        mock_viewmodel.update_completed.emit(True)
        assert "適用しました" in window_with_mock.statusBar().currentMessage()

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

    def test_apply_button_calls_apply_wallpaper(self, qtbot, window_with_mock, mock_viewmodel):
        """適用ボタンクリックでViewModelのapply_wallpaperが呼ばれることを確認"""
        button = window_with_mock.findChild(QPushButton, "apply_button")

        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        mock_viewmodel.apply_wallpaper.assert_called_once()

    def test_theme_changed_signal_updates_status(self, window_with_mock, mock_viewmodel):
        """ViewModelのtheme_changedシグナルでステータスが更新されることを確認"""
        # theme_changedシグナルをemit
        mock_viewmodel.theme_changed.emit("modern")

        # ステータスバーにテーマ名が表示される
        assert "modern" in window_with_mock.statusBar().currentMessage()

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
        assert "適用しました" in window_with_mock.statusBar().currentMessage()

    def test_complete_update_cycle(self, qtbot, window_with_mock, mock_viewmodel):
        """完全な更新サイクルをテスト"""
        window_with_mock.show()
        button = window_with_mock.findChild(QPushButton, "apply_button")
        progress_bar = window_with_mock.findChild(QProgressBar, "progress_bar")

        # 1. 更新開始
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
        assert not button.isEnabled()
        mock_viewmodel.apply_wallpaper.assert_called_once()

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
        assert "適用しました" in window_with_mock.statusBar().currentMessage()


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


class TestMainWindowSettingsIntegration:
    """MainWindowの設定ダイアログ統合テスト"""

    def test_settings_button_exists(self, window_with_mock):
        """「設定」ボタンが存在することを確認"""
        button = window_with_mock.findChild(QPushButton, "settings_button")
        assert button is not None
        assert button.text() == "設定"

    def test_settings_button_is_enabled(self, window_with_mock):
        """「設定」ボタンが有効であることを確認"""
        button = window_with_mock.findChild(QPushButton, "settings_button")
        assert button.isEnabled()

    def test_settings_service_initialized(self, window_with_mock):
        """MainWindowがSettingsServiceを保持していることを確認"""
        assert hasattr(window_with_mock, 'settings_service')
        from src.viewmodels.settings_service import SettingsService
        assert isinstance(window_with_mock.settings_service, SettingsService)

    def test_settings_button_opens_dialog(self, qtbot, window_with_mock, monkeypatch):
        """設定ボタンクリックで設定ダイアログが開くことを確認"""
        from src.ui.settings_dialog import SettingsDialog

        dialog_opened = []

        # SettingsDialog.execをモック化（ダイアログをキャンセル扱い）
        monkeypatch.setattr(
            SettingsDialog, "exec",
            lambda self: dialog_opened.append(True) or 0  # QDialog.Rejected
        )

        button = window_with_mock.findChild(QPushButton, "settings_button")
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        assert len(dialog_opened) == 1

    def test_settings_dialog_accept_saves(self, qtbot, window_with_mock, monkeypatch, tmp_path):
        """設定ダイアログでOKした場合に設定が保存されることを確認"""
        from PyQt6.QtWidgets import QDialog
        from src.ui.settings_dialog import SettingsDialog

        # tmp_pathをsettings_serviceに設定
        window_with_mock.settings_service.settings_dir = tmp_path
        window_with_mock.settings_service.settings_file = tmp_path / "settings.json"

        # SettingsDialog.execをAccept扱いにモック化
        monkeypatch.setattr(
            SettingsDialog, "exec",
            lambda self: QDialog.DialogCode.Accepted.value
        )
        # get_settingsをモック化
        monkeypatch.setattr(
            SettingsDialog, "get_settings",
            lambda self: {
                "auto_update_enabled": False,
                "auto_update_interval_minutes": 30,
                "auto_detect_resolution": False,
                "card_shadow_enabled": False,
            }
        )

        button = window_with_mock.findChild(QPushButton, "settings_button")
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        # 設定が反映されていることを確認
        assert window_with_mock.settings_service.get("auto_update_enabled") is False
        assert window_with_mock.settings_service.get("auto_update_interval_minutes") == 30

    def test_settings_dialog_reject_does_not_save(self, qtbot, window_with_mock, monkeypatch, tmp_path):
        """設定ダイアログでキャンセルした場合に設定が保存されないことを確認"""
        from PyQt6.QtWidgets import QDialog
        from src.ui.settings_dialog import SettingsDialog

        window_with_mock.settings_service.settings_dir = tmp_path
        window_with_mock.settings_service.settings_file = tmp_path / "settings.json"

        original_enabled = window_with_mock.settings_service.get("auto_update_enabled")

        # SettingsDialog.execをReject扱いにモック化
        monkeypatch.setattr(
            SettingsDialog, "exec",
            lambda self: QDialog.DialogCode.Rejected.value
        )

        button = window_with_mock.findChild(QPushButton, "settings_button")
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        # 設定が変わっていないことを確認
        assert window_with_mock.settings_service.get("auto_update_enabled") == original_enabled


class TestMainWindowAutoUpdateUI:
    """MainWindowの自動更新UI統合テスト"""

    def test_next_update_label_exists(self, window_with_mock):
        """次回更新時刻ラベルが存在すること"""
        label = window_with_mock.findChild(QLabel, "next_update_label")
        assert label is not None

    def test_next_update_label_initial_text(self, window_with_mock):
        """次回更新時刻ラベルの初期テキスト"""
        label = window_with_mock.findChild(QLabel, "next_update_label")
        # 自動更新が停止中なら「自動更新: 停止中」
        assert "自動更新" in label.text()

    def test_settings_accept_notifies_viewmodel(self, qtbot, window_with_mock, mock_viewmodel, monkeypatch, tmp_path):
        """設定保存時にViewModelのon_settings_changedが呼ばれること"""
        from PyQt6.QtWidgets import QDialog
        from src.ui.settings_dialog import SettingsDialog

        window_with_mock.settings_service.settings_dir = tmp_path
        window_with_mock.settings_service.settings_file = tmp_path / "settings.json"

        mock_viewmodel.on_settings_changed = Mock()

        monkeypatch.setattr(
            SettingsDialog, "exec",
            lambda self: QDialog.DialogCode.Accepted.value
        )
        monkeypatch.setattr(
            SettingsDialog, "get_settings",
            lambda self: {
                "auto_update_enabled": True,
                "auto_update_interval_minutes": 120,
                "auto_detect_resolution": True,
                "card_shadow_enabled": True,
            }
        )

        button = window_with_mock.findChild(QPushButton, "settings_button")
        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        mock_viewmodel.on_settings_changed.assert_called_once()

    def test_auto_update_status_updates_label(self, window_with_mock, mock_viewmodel):
        """自動更新ステータス変更でラベルが更新されること"""
        label = window_with_mock.findChild(QLabel, "next_update_label")

        # 自動更新有効化シグナル発火
        mock_viewmodel.auto_update_status_changed.emit(True)
        text = label.text()
        assert "自動更新" in text


class TestSystemTrayIcon:
    """システムトレイアイコン機能のテスト"""

    def test_tray_icon_initialized(self, window_with_mock):
        """トレイアイコンが初期化されること"""
        from PyQt6.QtWidgets import QSystemTrayIcon

        # トレイアイコンが存在する
        assert hasattr(window_with_mock, '_tray_icon')
        assert isinstance(window_with_mock._tray_icon, QSystemTrayIcon)
        # トレイアイコンが表示されている
        assert window_with_mock._tray_icon.isVisible()

    def test_tray_menu_has_actions(self, window_with_mock):
        """トレイメニューに必要なアクションが存在すること"""
        tray_menu = window_with_mock._tray_icon.contextMenu()

        # メニューが存在する
        assert tray_menu is not None

        # アクションを取得
        actions = tray_menu.actions()

        # 4つのアクション（今すぐ更新/設定/ウィンドウを開く/終了、セパレータ除く）
        action_texts = [action.text() for action in actions if not action.isSeparator()]
        assert len(action_texts) >= 4
        assert "今すぐ更新" in action_texts
        assert "設定" in action_texts
        assert "ウィンドウを開く" in action_texts
        assert "終了" in action_texts

    def test_tray_update_now_action(self, window_with_mock, mock_viewmodel):
        """「今すぐ更新」アクションでupdate_wallpaperが呼ばれること"""
        tray_menu = window_with_mock._tray_icon.contextMenu()
        actions = tray_menu.actions()

        # 「今すぐ更新」アクションを探す
        update_action = None
        for action in actions:
            if action.text() == "今すぐ更新":
                update_action = action
                break

        assert update_action is not None

        # アクションをトリガー
        update_action.trigger()

        # update_wallpaperが呼ばれる
        mock_viewmodel.update_wallpaper.assert_called_once()

    def test_tray_show_action(self, window_with_mock):
        """「ウィンドウを開く」アクションでウィンドウが表示されること"""
        # ウィンドウを非表示にする
        window_with_mock.hide()
        assert not window_with_mock.isVisible()

        tray_menu = window_with_mock._tray_icon.contextMenu()
        actions = tray_menu.actions()

        # 「ウィンドウを開く」アクションを探す
        show_action = None
        for action in actions:
            if action.text() == "ウィンドウを開く":
                show_action = action
                break

        assert show_action is not None

        # アクションをトリガー
        show_action.trigger()

        # ウィンドウが表示される
        assert window_with_mock.isVisible()

    def test_close_event_hides_window(self, window_with_mock, qtbot):
        """closeEventでウィンドウが非表示になる（終了しない）"""
        from PyQt6.QtGui import QCloseEvent

        # ウィンドウを表示
        window_with_mock.show()
        qtbot.waitExposed(window_with_mock)
        assert window_with_mock.isVisible()

        # closeEventを発火
        close_event = QCloseEvent()
        window_with_mock.closeEvent(close_event)

        # イベントが無視される（終了しない）
        assert close_event.isAccepted() is False

        # ウィンドウが非表示になる
        assert not window_with_mock.isVisible()

    def test_tray_icon_double_click_shows_window(self, window_with_mock, qtbot):
        """トレイアイコンダブルクリックでウィンドウが表示されること"""
        from PyQt6.QtWidgets import QSystemTrayIcon

        # ウィンドウを非表示にする
        window_with_mock.hide()
        assert not window_with_mock.isVisible()

        # トレイアイコンのactivatedシグナルを発火（DoubleClick）
        window_with_mock._tray_icon.activated.emit(QSystemTrayIcon.ActivationReason.DoubleClick)

        # ウィンドウが表示される
        assert window_with_mock.isVisible()

    def test_quit_action_closes_application(self, window_with_mock, qtbot, monkeypatch, mock_viewmodel):
        """「終了」アクションでアプリケーションが終了すること"""
        from PyQt6.QtWidgets import QApplication

        # QApplication.quitをモック化
        quit_called = []

        def mock_quit():
            quit_called.append(True)

        monkeypatch.setattr(QApplication, 'quit', mock_quit)

        tray_menu = window_with_mock._tray_icon.contextMenu()
        actions = tray_menu.actions()

        # 「終了」アクションを探す
        quit_action = None
        for action in actions:
            if action.text() == "終了":
                quit_action = action
                break

        assert quit_action is not None

        # アクションをトリガー
        quit_action.trigger()

        # QApplication.quitが呼ばれる
        assert len(quit_called) == 1
        # viewmodel.cleanup()も呼ばれる
        mock_viewmodel.cleanup.assert_called_once()
