"""
設定ダイアログのテスト
SettingsDialogのUI要素と動作をテスト
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QTabWidget, QCheckBox, QSpinBox, QComboBox, QLabel, QPushButton
from PyQt6.QtCore import Qt

from src.viewmodels.settings_service import SettingsService
from src.ui.settings_dialog import SettingsDialog
from src.calendar_client import CalendarClient


@pytest.fixture
def settings_service(tmp_path):
    """テスト用SettingsService"""
    return SettingsService(settings_dir=tmp_path)


@pytest.fixture
def dialog(qtbot, settings_service):
    """テスト用SettingsDialog"""
    dlg = SettingsDialog(settings_service)
    qtbot.addWidget(dlg)
    return dlg


class TestSettingsDialogInit:
    """SettingsDialog 初期化テスト"""

    def test_dialog_exists(self):
        """SettingsDialogクラスが存在すること"""
        assert SettingsDialog is not None

    def test_dialog_title(self, dialog):
        """ダイアログのタイトルが正しいこと"""
        assert dialog.windowTitle() == "設定"

    def test_dialog_has_tab_widget(self, dialog):
        """タブウィジェットが存在すること"""
        tab_widget = dialog.findChild(QTabWidget)
        assert tab_widget is not None

    def test_dialog_has_two_tabs(self, dialog):
        """2つのタブが存在すること（自動更新、表示設定）"""
        tab_widget = dialog.findChild(QTabWidget)
        assert tab_widget.count() >= 2


class TestAutoUpdateTab:
    """自動更新タブのテスト"""

    def test_auto_update_checkbox_exists(self, dialog):
        """自動更新チェックボックスが存在すること"""
        assert dialog.auto_update_checkbox is not None
        assert isinstance(dialog.auto_update_checkbox, QCheckBox)

    def test_auto_update_checkbox_default(self, dialog, settings_service):
        """自動更新チェックボックスの初期値がconfig値と一致すること"""
        expected = settings_service.get("auto_update_enabled")
        assert dialog.auto_update_checkbox.isChecked() == expected

    def test_interval_spinbox_exists(self, dialog):
        """更新間隔スピンボックスが存在すること"""
        assert dialog.interval_spinbox is not None
        assert isinstance(dialog.interval_spinbox, QSpinBox)

    def test_interval_spinbox_default(self, dialog, settings_service):
        """更新間隔スピンボックスの初期値がconfig値と一致すること"""
        expected = settings_service.get("auto_update_interval_minutes")
        assert dialog.interval_spinbox.value() == expected

    def test_interval_spinbox_range(self, dialog):
        """更新間隔の範囲が適切であること（15分〜480分）"""
        assert dialog.interval_spinbox.minimum() == 15
        assert dialog.interval_spinbox.maximum() == 480

    def test_interval_disabled_when_auto_update_off(self, qtbot, dialog):
        """自動更新OFF時に間隔スピンボックスが無効になること"""
        dialog.auto_update_checkbox.setChecked(False)
        assert not dialog.interval_spinbox.isEnabled()

    def test_interval_enabled_when_auto_update_on(self, qtbot, dialog):
        """自動更新ON時に間隔スピンボックスが有効になること"""
        dialog.auto_update_checkbox.setChecked(True)
        assert dialog.interval_spinbox.isEnabled()


class TestDisplayTab:
    """表示設定タブのテスト"""

    def test_auto_detect_checkbox_exists(self, dialog):
        """解像度自動検出チェックボックスが存在すること"""
        assert dialog.auto_detect_checkbox is not None
        assert isinstance(dialog.auto_detect_checkbox, QCheckBox)

    def test_shadow_checkbox_exists(self, dialog):
        """カード影チェックボックスが存在すること"""
        assert dialog.shadow_checkbox is not None
        assert isinstance(dialog.shadow_checkbox, QCheckBox)


class TestSettingsDialogSave:
    """設定保存テスト"""

    def test_get_settings_returns_dict(self, dialog):
        """get_settings()がdictを返すこと"""
        settings = dialog.get_settings()
        assert isinstance(settings, dict)

    def test_get_settings_includes_auto_update(self, dialog):
        """get_settings()に自動更新設定が含まれること"""
        settings = dialog.get_settings()
        assert "auto_update_enabled" in settings
        assert "auto_update_interval_minutes" in settings

    def test_get_settings_reflects_ui_changes(self, qtbot, dialog):
        """UI変更がget_settings()に反映されること"""
        dialog.auto_update_checkbox.setChecked(False)
        dialog.interval_spinbox.setValue(120)
        settings = dialog.get_settings()
        assert settings["auto_update_enabled"] is False
        assert settings["auto_update_interval_minutes"] == 120

    def test_load_settings_updates_ui(self, dialog, settings_service):
        """load_settings()でUIが更新されること"""
        settings_service.set("auto_update_enabled", False)
        settings_service.set("auto_update_interval_minutes", 30)
        dialog.load_settings(settings_service)
        assert dialog.auto_update_checkbox.isChecked() is False
        assert dialog.interval_spinbox.value() == 30


# === Googleアカウントタブのテスト ===

@pytest.fixture
def mock_calendar_client():
    """テスト用CalendarClientモック"""
    client = MagicMock(spec=CalendarClient)
    client.is_authenticated = False
    return client


@pytest.fixture
def dialog_with_auth(qtbot, settings_service, mock_calendar_client):
    """CalendarClient付きSettingsDialog"""
    dlg = SettingsDialog(settings_service, calendar_client=mock_calendar_client)
    qtbot.addWidget(dlg)
    return dlg


class TestGoogleAccountTab:
    """Googleアカウントタブのテスト"""

    def test_google_account_tab_exists(self, dialog_with_auth):
        """Googleアカウントタブが存在すること"""
        tab_widget = dialog_with_auth.findChild(QTabWidget)
        tab_names = [tab_widget.tabText(i) for i in range(tab_widget.count())]
        assert "Googleアカウント" in tab_names

    def test_dialog_has_three_tabs(self, dialog_with_auth):
        """3つのタブが存在すること（自動更新、表示設定、Googleアカウント）"""
        tab_widget = dialog_with_auth.findChild(QTabWidget)
        assert tab_widget.count() == 3

    def test_auth_status_label_exists(self, dialog_with_auth):
        """認証状態ラベルが存在すること"""
        assert hasattr(dialog_with_auth, 'auth_status_label')
        assert isinstance(dialog_with_auth.auth_status_label, QLabel)

    def test_auth_status_shows_not_authenticated(self, dialog_with_auth, mock_calendar_client):
        """未認証時に「未ログイン」と表示されること"""
        mock_calendar_client.is_authenticated = False
        dialog_with_auth._update_auth_status()
        assert "未ログイン" in dialog_with_auth.auth_status_label.text()

    def test_auth_status_shows_authenticated(self, dialog_with_auth, mock_calendar_client):
        """認証済み時に「ログイン済み」と表示されること"""
        mock_calendar_client.is_authenticated = True
        dialog_with_auth._update_auth_status()
        assert "ログイン済み" in dialog_with_auth.auth_status_label.text()

    def test_login_button_exists(self, dialog_with_auth):
        """Googleログインボタンが存在すること"""
        assert hasattr(dialog_with_auth, 'login_button')
        assert isinstance(dialog_with_auth.login_button, QPushButton)

    def test_logout_button_exists(self, dialog_with_auth):
        """ログアウトボタンが存在すること"""
        assert hasattr(dialog_with_auth, 'logout_button')
        assert isinstance(dialog_with_auth.logout_button, QPushButton)

    def test_login_button_calls_authenticate(self, qtbot, dialog_with_auth, mock_calendar_client):
        """ログインボタンクリックでauthenticate()が呼ばれること"""
        mock_calendar_client.authenticate.return_value = True
        mock_calendar_client.is_authenticated = True

        qtbot.mouseClick(dialog_with_auth.login_button, Qt.MouseButton.LeftButton)

        mock_calendar_client.authenticate.assert_called_once()

    def test_logout_button_calls_logout(self, qtbot, dialog_with_auth, mock_calendar_client):
        """ログアウトボタンクリックでlogout()が呼ばれること"""
        mock_calendar_client.is_authenticated = True
        dialog_with_auth._update_auth_status()

        qtbot.mouseClick(dialog_with_auth.logout_button, Qt.MouseButton.LeftButton)

        mock_calendar_client.logout.assert_called_once()

    def test_login_updates_status(self, qtbot, dialog_with_auth, mock_calendar_client):
        """ログイン成功後に認証状態が更新されること"""
        mock_calendar_client.authenticate.return_value = True
        mock_calendar_client.is_authenticated = True

        qtbot.mouseClick(dialog_with_auth.login_button, Qt.MouseButton.LeftButton)

        assert "ログイン済み" in dialog_with_auth.auth_status_label.text()

    def test_logout_updates_status(self, qtbot, dialog_with_auth, mock_calendar_client):
        """ログアウト後に認証状態が更新されること"""
        # まずログイン状態にする
        mock_calendar_client.is_authenticated = True
        dialog_with_auth._update_auth_status()

        # ログアウト
        def side_effect():
            mock_calendar_client.is_authenticated = False
        mock_calendar_client.logout.side_effect = side_effect

        qtbot.mouseClick(dialog_with_auth.logout_button, Qt.MouseButton.LeftButton)

        assert "未ログイン" in dialog_with_auth.auth_status_label.text()

    def test_login_failure_shows_error(self, qtbot, dialog_with_auth, mock_calendar_client):
        """ログイン失敗時にエラーメッセージが表示されること"""
        mock_calendar_client.authenticate.return_value = False
        mock_calendar_client.is_authenticated = False

        qtbot.mouseClick(dialog_with_auth.login_button, Qt.MouseButton.LeftButton)

        assert "失敗" in dialog_with_auth.auth_status_label.text()

    def test_login_button_disabled_when_authenticated(self, dialog_with_auth, mock_calendar_client):
        """ログイン済みの場合、ログインボタンが無効になること"""
        mock_calendar_client.is_authenticated = True
        dialog_with_auth._update_auth_status()

        assert not dialog_with_auth.login_button.isEnabled()

    def test_logout_button_disabled_when_not_authenticated(self, dialog_with_auth, mock_calendar_client):
        """未認証の場合、ログアウトボタンが無効になること"""
        mock_calendar_client.is_authenticated = False
        dialog_with_auth._update_auth_status()

        assert not dialog_with_auth.logout_button.isEnabled()

    def test_no_google_tab_without_calendar_client(self, dialog):
        """CalendarClientなしの場合、Googleアカウントタブが表示されないこと"""
        tab_widget = dialog.findChild(QTabWidget)
        tab_names = [tab_widget.tabText(i) for i in range(tab_widget.count())]
        assert "Googleアカウント" not in tab_names
