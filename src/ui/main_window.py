"""
MainWindow

PyQt6のメインウィンドウ。
MVVMパターンにおけるView層。
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QProgressBar, QMessageBox, QFileDialog, QDialog,
    QSystemTrayIcon, QMenu, QApplication
)
from PyQt6.QtCore import Qt, pyqtSlot
from pathlib import Path
import logging

from src.ui.widgets.preview_widget import PreviewWidget
from src.ui.settings_dialog import SettingsDialog
from src.viewmodels.main_viewmodel import MainViewModel
from src.viewmodels.settings_service import SettingsService

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    メインウィンドウ

    カレンダー壁紙アプリのメインウィンドウです。
    テーマ選択、プレビュー表示、壁紙更新機能を提供します。
    """

    def __init__(self, viewmodel: MainViewModel = None, settings_service: SettingsService = None, parent=None):
        """
        MainWindowを初期化

        Args:
            viewmodel (MainViewModel, optional): MainViewModel。Noneの場合は自動生成。
            settings_service (SettingsService, optional): 設定サービス。Noneの場合は自動生成。
            parent (QWidget, optional): 親ウィジェット。デフォルトはNone。
        """
        super().__init__(parent)
        self.setWindowTitle("カレンダー壁紙アプリ")
        self.resize(800, 600)

        # ViewModelの初期化
        self.viewmodel = viewmodel or MainViewModel()

        # SettingsServiceの初期化
        self.settings_service = settings_service or SettingsService()

        # 中央ウィジェットを作成
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # メインレイアウト
        main_layout = QVBoxLayout(central_widget)

        # 上部: コントロールエリア
        self._setup_control_area(main_layout)

        # 背景画像エリア
        self._setup_background_area(main_layout)

        # 自動更新ステータスエリア
        self._setup_auto_update_area(main_layout)

        # 中央: プレビューエリア
        self._setup_preview_area(main_layout)

        # 下部: ステータスバー
        self._setup_status_bar()

        # ViewModelとの接続
        self._connect_viewmodel()

        # システムトレイアイコンの初期化
        self._setup_tray_icon()

        # 背景画像設定を復元
        self._restore_background_setting()

        logger.info("MainWindowを初期化しました")

    def _setup_control_area(self, parent_layout):
        """
        コントロールエリアをセットアップ

        テーマ選択ComboBox、プレビュー、壁紙適用ボタンを配置します。

        Args:
            parent_layout: 親レイアウト
        """
        control_layout = QHBoxLayout()

        # テーマ選択ラベル
        theme_label = QLabel("テーマ:")
        control_layout.addWidget(theme_label)

        # テーマ選択ComboBox（テーマはViewModelから取得）
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("theme_combo")
        control_layout.addWidget(self.theme_combo)

        control_layout.addStretch()

        # 「設定」ボタン
        self.settings_button = QPushButton("設定")
        self.settings_button.setObjectName("settings_button")
        self.settings_button.clicked.connect(self._on_settings_clicked)
        control_layout.addWidget(self.settings_button)

        # 「壁紙に適用」ボタン
        self.apply_button = QPushButton("壁紙に適用")
        self.apply_button.setObjectName("apply_button")
        self.apply_button.clicked.connect(self._on_apply_clicked)
        control_layout.addWidget(self.apply_button)

        parent_layout.addLayout(control_layout)

    def _setup_background_area(self, parent_layout):
        """
        背景画像選択エリアをセットアップ

        Args:
            parent_layout: 親レイアウト
        """
        from src.config import PRESET_BACKGROUNDS

        bg_layout = QHBoxLayout()

        # 背景画像ラベル
        bg_label = QLabel("背景画像:")
        bg_layout.addWidget(bg_label)

        # プリセット選択コンボボックス
        self.bg_combo = QComboBox()
        self.bg_combo.setObjectName("bg_combo")
        for preset in PRESET_BACKGROUNDS:
            self.bg_combo.addItem(preset["name"], preset["file"])
        self.bg_combo.currentIndexChanged.connect(self._on_background_combo_changed)
        bg_layout.addWidget(self.bg_combo)

        # クロップ位置選択
        crop_label = QLabel("位置:")
        bg_layout.addWidget(crop_label)

        self.crop_combo = QComboBox()
        self.crop_combo.setObjectName("crop_combo")
        self.crop_combo.addItem("中央", "center")
        self.crop_combo.addItem("上寄せ", "top")
        self.crop_combo.addItem("下寄せ", "bottom")
        self.crop_combo.currentIndexChanged.connect(self._on_crop_position_changed)
        bg_layout.addWidget(self.crop_combo)

        bg_layout.addStretch()

        # 「カスタム画像を選択」ボタン
        self.bg_select_button = QPushButton("カスタム画像を選択")
        self.bg_select_button.setObjectName("bg_select_button")
        self.bg_select_button.clicked.connect(self._on_select_background)
        bg_layout.addWidget(self.bg_select_button)

        parent_layout.addLayout(bg_layout)

    def _setup_auto_update_area(self, parent_layout):
        """自動更新ステータスエリアをセットアップ"""
        auto_layout = QHBoxLayout()

        self.next_update_label = QLabel("自動更新: 停止中")
        self.next_update_label.setObjectName("next_update_label")
        auto_layout.addWidget(self.next_update_label)

        auto_layout.addStretch()
        parent_layout.addLayout(auto_layout)

    def _setup_preview_area(self, parent_layout):
        """
        プレビューエリアをセットアップ

        Args:
            parent_layout: 親レイアウト
        """
        # PreviewWidgetを使用
        self.preview_widget = PreviewWidget()
        self.preview_widget.setObjectName("preview_widget")

        parent_layout.addWidget(self.preview_widget)

        # QProgressBarを追加
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("進捗: %p%")
        self.progress_bar.hide()  # 初期状態では非表示

        parent_layout.addWidget(self.progress_bar)

    def _setup_status_bar(self):
        """ステータスバーをセットアップ"""
        self.statusBar().showMessage("準備完了")

    def _connect_viewmodel(self):
        """ViewModelとの接続を設定"""
        # テーマComboBoxの変更をViewModelに接続
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)

        # ViewModelのシグナルをUIに接続
        self.viewmodel.update_started.connect(self._on_update_started)
        self.viewmodel.update_completed.connect(self._on_update_completed)
        self.viewmodel.progress_updated.connect(self._on_progress_updated)
        self.viewmodel.error_occurred.connect(self._on_error_occurred)
        self.viewmodel.theme_changed.connect(self._on_viewmodel_theme_changed)
        self.viewmodel.preview_ready.connect(self._on_preview_ready)
        self.viewmodel.auto_update_status_changed.connect(self._on_auto_update_status_changed)

        # テーマ一覧をComboBoxに設定
        themes = self.viewmodel.get_available_themes()
        if themes:
            self.theme_combo.clear()
            self.theme_combo.addItems(themes)
            self.theme_combo.setCurrentText(self.viewmodel.current_theme)

    @pyqtSlot(str)
    def _on_theme_changed(self, theme_name: str):
        """
        テーマが変更されたときの処理（プレビューのみ生成）

        Args:
            theme_name (str): 新しいテーマ名
        """
        self.viewmodel.set_theme(theme_name)
        # プレビュー画像を生成（壁紙は適用しない）
        self.statusBar().showMessage(f"プレビュー生成中: {theme_name}")
        self.viewmodel.preview_theme(theme_name)
        logger.info(f"テーマプレビューを要求しました: {theme_name}")

    @pyqtSlot(str)
    def _on_viewmodel_theme_changed(self, theme_name: str):
        """
        ViewModelのテーマが変更されたときの処理

        Args:
            theme_name (str): 新しいテーマ名
        """
        self.statusBar().showMessage(f"テーマ: {theme_name}（プレビュー中）")

    @pyqtSlot(object)
    def _on_preview_ready(self, preview_path):
        """
        プレビュー画像が生成されたときの処理

        Args:
            preview_path: 生成されたプレビュー画像のパス
        """
        if preview_path and Path(preview_path).exists():
            self.preview_widget.set_image(preview_path)
            self.statusBar().showMessage(f"プレビュー表示中 - 「壁紙に適用」で反映されます")
            logger.info(f"プレビューを表示しました: {preview_path}")
        else:
            self.statusBar().showMessage("プレビュー生成に失敗しました")

    @pyqtSlot()
    def _on_settings_clicked(self):
        """「設定」ボタンがクリックされたときの処理"""
        # ViewModelからCalendarClientを取得
        calendar_client = None
        if hasattr(self.viewmodel, '_wallpaper_service') and self.viewmodel._wallpaper_service:
            calendar_client = self.viewmodel._wallpaper_service.calendar_client

        dialog = SettingsDialog(self.settings_service, calendar_client=calendar_client, parent=self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted.value:
            new_settings = dialog.get_settings()
            self.settings_service.update(new_settings)
            if self.settings_service.save():
                self.statusBar().showMessage("設定を保存しました")
                logger.info(f"設定を保存しました: {new_settings}")
            else:
                self.statusBar().showMessage("設定の保存に失敗しました")
                logger.error("設定の保存に失敗しました")
            # ViewModelに設定変更を通知
            self.viewmodel.on_settings_changed(new_settings)

    @pyqtSlot()
    def _on_apply_clicked(self):
        """
        「壁紙に適用」ボタンがクリックされたときの処理

        ViewModelに壁紙適用を依頼します。
        """
        # ボタンを無効化
        self.apply_button.setEnabled(False)

        # ViewModelに壁紙適用を依頼
        self.viewmodel.apply_wallpaper()

    def _on_background_combo_changed(self, index: int):
        """背景画像コンボボックスの選択変更"""
        if index < 0:
            return
        data = self.bg_combo.itemData(index)
        if data and not data.startswith("custom:"):
            # プリセット選択
            self.viewmodel.set_preset_background(data)
            self._save_background_setting(f"preset:{data}")
            self.statusBar().showMessage(f"背景画像: {self.bg_combo.itemText(index)}")
            self.viewmodel.preview_theme(self.viewmodel.current_theme)

    def _on_crop_position_changed(self, index: int):
        """クロップ位置の変更"""
        if index < 0:
            return
        position = self.crop_combo.itemData(index)
        self.viewmodel.set_crop_position(position)
        self.settings_service.set("background_crop_position", position)
        self.settings_service.save()
        self.viewmodel.preview_theme(self.viewmodel.current_theme)

    @pyqtSlot()
    def _on_select_background(self):
        """カスタム背景画像を選択するファイルダイアログを表示"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "背景画像を選択",
            "",
            "画像ファイル (*.png *.jpg *.jpeg);;すべてのファイル (*)"
        )

        if file_path:
            path = Path(file_path)
            self.viewmodel.set_background_image(path)
            # コンボボックスにカスタム項目を追加/更新
            custom_label = f"カスタム: {path.name}"
            self._set_custom_combo_item(custom_label, f"custom:{file_path}")
            self._save_background_setting(str(file_path))
            self.statusBar().showMessage(f"背景画像を設定しました: {path.name}")
            self.viewmodel.preview_theme(self.viewmodel.current_theme)
            logger.info(f"背景画像を選択しました: {file_path}")

    def _set_custom_combo_item(self, label: str, data: str):
        """コンボボックスのカスタム項目を設定"""
        # 既存のカスタム項目を探す
        for i in range(self.bg_combo.count()):
            item_data = self.bg_combo.itemData(i)
            if item_data and str(item_data).startswith("custom:"):
                self.bg_combo.setItemText(i, label)
                self.bg_combo.setItemData(i, data)
                self.bg_combo.blockSignals(True)
                self.bg_combo.setCurrentIndex(i)
                self.bg_combo.blockSignals(False)
                return
        # カスタム項目がなければ追加
        self.bg_combo.blockSignals(True)
        self.bg_combo.addItem(label, data)
        self.bg_combo.setCurrentIndex(self.bg_combo.count() - 1)
        self.bg_combo.blockSignals(False)

    def _save_background_setting(self, value: str):
        """背景画像設定を永続化"""
        self.settings_service.set("background_image_path", value)
        self.settings_service.save()

    def _restore_background_setting(self):
        """起動時に背景画像設定を復元"""
        # クロップ位置を復元
        crop_pos = self.settings_service.get("background_crop_position", "center")
        for i in range(self.crop_combo.count()):
            if self.crop_combo.itemData(i) == crop_pos:
                self.crop_combo.blockSignals(True)
                self.crop_combo.setCurrentIndex(i)
                self.crop_combo.blockSignals(False)
                self.viewmodel.set_crop_position(crop_pos)
                break

        # 背景画像を復元
        bg_value = self.settings_service.get("background_image_path", "")
        if not bg_value:
            return

        if bg_value.startswith("preset:"):
            filename = bg_value[len("preset:"):]
            # コンボボックスからプリセットを選択
            for i in range(self.bg_combo.count()):
                if self.bg_combo.itemData(i) == filename:
                    self.bg_combo.blockSignals(True)
                    self.bg_combo.setCurrentIndex(i)
                    self.bg_combo.blockSignals(False)
                    self.viewmodel.set_preset_background(filename)
                    return
        else:
            # カスタム画像パス
            path = Path(bg_value)
            if path.exists():
                self.viewmodel.set_background_image(path)
                custom_label = f"カスタム: {path.name}"
                self._set_custom_combo_item(custom_label, f"custom:{bg_value}")

    @pyqtSlot()
    def _on_update_started(self):
        """壁紙更新開始時の処理"""
        self.statusBar().showMessage("壁紙を更新中...")
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        logger.info("壁紙更新を開始しました")

    @pyqtSlot(int)
    def _on_progress_updated(self, value: int):
        """
        進捗更新時の処理

        Args:
            value (int): 進捗値（0-100）
        """
        self.progress_bar.setValue(value)
        logger.debug(f"進捗: {value}%")

    @pyqtSlot(bool)
    def _on_update_completed(self, success: bool):
        """
        壁紙更新完了時の処理

        Args:
            success (bool): 更新が成功したかどうか
        """
        # ボタンを有効化
        self.apply_button.setEnabled(True)

        # ProgressBarを非表示
        self.progress_bar.hide()

        if success:
            self.statusBar().showMessage("壁紙に適用しました")
            logger.info("壁紙適用が完了しました")

            # プレビューを更新
            self._update_preview()
        else:
            self.statusBar().showMessage("壁紙の適用に失敗しました")
            logger.warning("壁紙適用に失敗しました")

    def _update_preview(self):
        """
        最新の壁紙をプレビューに表示
        """
        try:
            from datetime import datetime
            from src.config import OUTPUT_DIR, WALLPAPER_FILENAME_TEMPLATE

            # 現在のテーマ名と日付からファイル名を生成
            theme_name = self.viewmodel.current_theme
            date_str = datetime.now().strftime('%Y%m%d')
            filename = WALLPAPER_FILENAME_TEMPLATE.format(
                theme=theme_name,
                date=date_str
            )
            image_path = OUTPUT_DIR / filename

            # 画像が存在する場合のみプレビューに設定
            if image_path.exists():
                self.preview_widget.set_image(image_path)
                logger.info(f"プレビューを更新しました: {image_path}")
            else:
                logger.warning(f"プレビュー画像が見つかりません: {image_path}")

        except Exception as e:
            logger.error(f"プレビュー更新エラー: {e}")

    @pyqtSlot(bool)
    def _on_auto_update_status_changed(self, enabled: bool):
        """自動更新ステータスが変更されたときの処理"""
        if enabled:
            next_time = self.viewmodel.get_next_update_time()
            if next_time:
                self.next_update_label.setText(f"自動更新: 次回 {next_time}")
            else:
                self.next_update_label.setText("自動更新: 有効")
        else:
            self.next_update_label.setText("自動更新: 停止中")

    @pyqtSlot(str)
    def _on_error_occurred(self, error_message: str):
        """
        エラー発生時の処理

        Args:
            error_message (str): エラーメッセージ
        """
        self.statusBar().showMessage(f"エラー: {error_message}")
        logger.error(f"エラーが発生しました: {error_message}")

    def _setup_tray_icon(self):
        """システムトレイアイコンをセットアップ"""
        # システムトレイが利用可能かチェック
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("システムトレイが利用できません。トレイアイコン機能を無効化します。")
            self._tray_icon = None
            return

        # トレイアイコンを作成
        self._tray_icon = QSystemTrayIcon(self)

        # アイコンを設定（システムのデフォルトアイコンを使用）
        # NOTE: カスタムアイコンは assets/tray_icon.png に配置可能
        self._tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))

        # トレイメニューを作成
        tray_menu = QMenu(self)

        # 「今すぐ更新」アクション
        update_action = tray_menu.addAction("今すぐ更新")
        update_action.triggered.connect(self.viewmodel.update_wallpaper)

        # 「設定」アクション
        settings_action = tray_menu.addAction("設定")
        settings_action.triggered.connect(self._on_settings_clicked)

        # セパレータ
        tray_menu.addSeparator()

        # 「表示」アクション
        show_action = tray_menu.addAction("表示")
        show_action.triggered.connect(self._show_window)

        # 「終了」アクション
        quit_action = tray_menu.addAction("終了")
        quit_action.triggered.connect(self._quit_application)

        # メニューをトレイアイコンに設定
        self._tray_icon.setContextMenu(tray_menu)

        # ダブルクリックでウィンドウを表示
        self._tray_icon.activated.connect(self._on_tray_icon_activated)

        # トレイアイコンを表示
        self._tray_icon.show()

        logger.info("システムトレイアイコンを初期化しました")

    def _on_tray_icon_activated(self, reason):
        """
        トレイアイコンのactivatedシグナル処理

        Args:
            reason: ActivationReason（DoubleClick等）
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        """トレイからウィンドウを表示"""
        self.show()
        self.raise_()
        self.activateWindow()
        logger.info("ウィンドウを表示しました")

    def _perform_shutdown(self):
        """アプリケーションの終了処理を実行"""
        if self.viewmodel.is_updating:
            logger.info("終了前に壁紙更新をキャンセルします")
            self.viewmodel.cancel_update()

            # QThreadPoolのすべてのワーカーが終了するまで待機（最大3秒）
            from PyQt6.QtCore import QThreadPool
            thread_pool = QThreadPool.globalInstance()
            if not thread_pool.waitForDone(3000):  # 3秒のタイムアウト
                logger.warning("一部のワーカーがタイムアウト内に終了しませんでした")

        self.viewmodel.cleanup()

    def _quit_application(self):
        """アプリケーションを終了"""
        logger.info("トレイメニューから終了を選択しました")
        self._perform_shutdown()
        QApplication.quit()

    def closeEvent(self, event):
        """
        ウィンドウを閉じる際の処理

        トレイアイコンが有効な場合は、ウィンドウを非表示にするだけで
        アプリケーションは終了しません。

        Args:
            event: CloseEvent
        """
        # トレイアイコンが有効な場合は非表示にするだけ
        if self._tray_icon is not None and self._tray_icon.isVisible():
            event.ignore()
            self.hide()
            logger.info("ウィンドウをトレイに格納しました")
        else:
            # トレイアイコンが無効な場合は通常の終了処理
            self._perform_shutdown()
            logger.info("アプリケーションを終了します")
            event.accept()
