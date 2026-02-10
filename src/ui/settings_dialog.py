"""
設定ダイアログ
自動更新、表示設定などをタブ形式で管理
"""
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QCheckBox, QSpinBox, QLabel, QPushButton, QGroupBox, QFormLayout,
    QListWidget, QListWidgetItem, QInputDialog, QColorDialog
)
from PyQt6.QtCore import Qt

from ..viewmodels.settings_service import SettingsService

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """設定ダイアログ"""

    def __init__(self, settings_service: SettingsService, calendar_client=None, parent=None):
        super().__init__(parent)
        self._settings_service = settings_service
        self._calendar_client = calendar_client
        self.setWindowTitle("設定")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self._setup_ui()
        self.load_settings(settings_service)

    def _setup_ui(self):
        """UI構築"""
        layout = QVBoxLayout(self)

        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # タブ追加
        self.tab_widget.addTab(self._create_auto_update_tab(), "自動更新")
        self.tab_widget.addTab(self._create_display_tab(), "表示設定")

        # CalendarClientがある場合のみGoogleアカウントタブを追加
        if self._calendar_client is not None:
            self.tab_widget.addTab(self._create_google_account_tab(), "Googleアカウント")

        # ボタン行
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _create_auto_update_tab(self) -> QWidget:
        """自動更新タブを作成"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 自動更新グループ
        group = QGroupBox("自動更新設定")
        form = QFormLayout()

        self.auto_update_checkbox = QCheckBox("自動更新を有効にする")
        self.auto_update_checkbox.stateChanged.connect(self._on_auto_update_toggled)
        form.addRow(self.auto_update_checkbox)

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(15)
        self.interval_spinbox.setMaximum(480)
        self.interval_spinbox.setSuffix(" 分")
        form.addRow("更新間隔:", self.interval_spinbox)

        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()
        return tab

    def _create_display_tab(self) -> QWidget:
        """表示設定タブを作成"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 解像度グループ
        res_group = QGroupBox("解像度")
        res_form = QFormLayout()

        self.auto_detect_checkbox = QCheckBox("解像度を自動検出する")
        res_form.addRow(self.auto_detect_checkbox)

        res_group.setLayout(res_form)
        layout.addWidget(res_group)

        # 描画グループ
        draw_group = QGroupBox("描画設定")
        draw_form = QFormLayout()

        self.shadow_checkbox = QCheckBox("カードの影を表示する")
        draw_form.addRow(self.shadow_checkbox)

        draw_group.setLayout(draw_form)
        layout.addWidget(draw_group)

        layout.addStretch()
        return tab

    def _create_google_account_tab(self) -> QWidget:
        """Googleアカウントタブを作成"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 認証状態グループ
        auth_group = QGroupBox("Googleアカウント")
        auth_layout = QVBoxLayout()

        # 認証状態ラベル
        self.auth_status_label = QLabel()
        self.auth_status_label.setObjectName("auth_status_label")
        auth_layout.addWidget(self.auth_status_label)

        # ボタン行
        btn_layout = QHBoxLayout()

        self.login_button = QPushButton("Googleログイン")
        self.login_button.setObjectName("login_button")
        self.login_button.clicked.connect(self._on_login_clicked)
        btn_layout.addWidget(self.login_button)

        self.logout_button = QPushButton("ログアウト")
        self.logout_button.setObjectName("logout_button")
        self.logout_button.clicked.connect(self._on_logout_clicked)
        btn_layout.addWidget(self.logout_button)

        btn_layout.addStretch()
        auth_layout.addLayout(btn_layout)

        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)

        # アカウント管理グループ（Phase 3）
        accounts_group = QGroupBox("アカウント管理")
        accounts_layout = QVBoxLayout()

        # アカウント一覧
        self.account_list_widget = QListWidget()
        accounts_layout.addWidget(self.account_list_widget)

        # ボタン行
        accounts_btn_layout = QHBoxLayout()

        self.add_account_button = QPushButton("アカウント追加")
        self.add_account_button.clicked.connect(self._on_add_account)
        accounts_btn_layout.addWidget(self.add_account_button)

        self.remove_account_button = QPushButton("削除")
        self.remove_account_button.clicked.connect(self._on_remove_account)
        accounts_btn_layout.addWidget(self.remove_account_button)

        self.change_color_button = QPushButton("色変更")
        self.change_color_button.clicked.connect(self._on_change_color)
        accounts_btn_layout.addWidget(self.change_color_button)

        accounts_btn_layout.addStretch()
        accounts_layout.addLayout(accounts_btn_layout)

        accounts_group.setLayout(accounts_layout)
        layout.addWidget(accounts_group)

        layout.addStretch()

        # 初期状態を反映
        self._update_auth_status()
        self.refresh_account_list()

        return tab

    def _update_auth_status(self):
        """認証状態をUIに反映"""
        is_auth = self._calendar_client and self._calendar_client.is_authenticated
        if is_auth:
            self.auth_status_label.setText("ステータス: ログイン済み")
        else:
            self.auth_status_label.setText("ステータス: 未ログイン")

        # ボタンの有効/無効を切り替え
        if hasattr(self, 'login_button'):
            self.login_button.setEnabled(not is_auth)
        if hasattr(self, 'logout_button'):
            self.logout_button.setEnabled(bool(is_auth))

    def _on_login_clicked(self):
        """Googleログインボタンのクリック処理"""
        if self._calendar_client:
            success = self._calendar_client.authenticate()
            self._update_auth_status()
            if success:
                logger.info("Googleログインに成功しました")
            else:
                self.auth_status_label.setText("ステータス: ログイン失敗")
                logger.warning("Googleログインに失敗しました")

    def _on_logout_clicked(self):
        """ログアウトボタンのクリック処理"""
        if self._calendar_client:
            self._calendar_client.logout()
            self._update_auth_status()
            logger.info("Googleログアウトを実行しました")

    def _on_add_account(self):
        """アカウント追加ボタンクリック"""
        if not self._calendar_client:
            return

        display_name, ok = QInputDialog.getText(
            self, "アカウント追加", "アカウント名:"
        )
        if ok and display_name:
            # OAuth2フロー起動
            account = self._calendar_client.add_account(display_name)
            if account:
                logger.info(f"アカウントを追加しました: {account.get('email', display_name)}")
            self.refresh_account_list()

    def _on_remove_account(self):
        """削除ボタンクリック"""
        if not self._calendar_client:
            return

        selected = self.account_list_widget.currentItem()
        if selected:
            account_id = selected.data(Qt.ItemDataRole.UserRole)
            self._calendar_client.remove_account(account_id)
            logger.info(f"アカウントを削除しました: {account_id}")
            self.refresh_account_list()

    def _on_change_color(self):
        """色変更ボタンクリック"""
        if not self._calendar_client:
            return

        selected = self.account_list_widget.currentItem()
        if selected:
            account_id = selected.data(Qt.ItemDataRole.UserRole)
            color = QColorDialog.getColor()
            if color.isValid():
                success = self._calendar_client.update_account_color(
                    account_id, color.name()
                )
                if success:
                    logger.info(f"アカウント色を変更しました: {account_id} -> {color.name()}")
                self.refresh_account_list()

    def refresh_account_list(self):
        """アカウント一覧を更新"""
        if not self._calendar_client:
            return

        self.account_list_widget.clear()

        # CalendarClient.accountsからアカウント情報を取得
        for account_id, account_data in self._calendar_client.accounts.items():
            email = account_data.get('email', account_id)
            display_name = account_data.get('display_name', email)
            color = account_data.get('color', '#4285f4')

            # リストアイテム作成
            item_text = f"{display_name} ({email})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, account_id)

            self.account_list_widget.addItem(item)

    def _on_auto_update_toggled(self, state):
        """自動更新チェックボックスの状態変更"""
        enabled = state == Qt.CheckState.Checked.value
        self.interval_spinbox.setEnabled(enabled)

    def load_settings(self, settings_service: SettingsService):
        """設定をUIに反映"""
        self.auto_update_checkbox.setChecked(
            settings_service.get("auto_update_enabled", True)
        )
        self.interval_spinbox.setValue(
            settings_service.get("auto_update_interval_minutes", 60)
        )
        self.auto_detect_checkbox.setChecked(
            settings_service.get("auto_detect_resolution", True)
        )
        self.shadow_checkbox.setChecked(
            settings_service.get("card_shadow_enabled", True)
        )

        # 自動更新チェックに応じて間隔を有効/無効
        self.interval_spinbox.setEnabled(self.auto_update_checkbox.isChecked())

    def get_settings(self) -> dict:
        """UIの現在値を辞書で返す"""
        return {
            "auto_update_enabled": self.auto_update_checkbox.isChecked(),
            "auto_update_interval_minutes": self.interval_spinbox.value(),
            "auto_detect_resolution": self.auto_detect_checkbox.isChecked(),
            "card_shadow_enabled": self.shadow_checkbox.isChecked(),
        }
