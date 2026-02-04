"""
MainWindow

PyQt6のメインウィンドウ。
MVVMパターンにおけるView層。
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot
import logging

from src.ui.widgets.preview_widget import PreviewWidget
from src.viewmodels.main_viewmodel import MainViewModel

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    メインウィンドウ

    カレンダー壁紙アプリのメインウィンドウです。
    テーマ選択、プレビュー表示、壁紙更新機能を提供します。
    """

    def __init__(self, viewmodel: MainViewModel = None, parent=None):
        """
        MainWindowを初期化

        Args:
            viewmodel (MainViewModel, optional): MainViewModel。Noneの場合は自動生成。
            parent (QWidget, optional): 親ウィジェット。デフォルトはNone。
        """
        super().__init__(parent)
        self.setWindowTitle("カレンダー壁紙アプリ")
        self.resize(800, 600)

        # ViewModelの初期化
        self.viewmodel = viewmodel or MainViewModel()

        # 中央ウィジェットを作成
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # メインレイアウト
        main_layout = QVBoxLayout(central_widget)

        # 上部: コントロールエリア
        self._setup_control_area(main_layout)

        # 中央: プレビューエリア
        self._setup_preview_area(main_layout)

        # 下部: ステータスバー
        self._setup_status_bar()

        # ViewModelとの接続
        self._connect_viewmodel()

        logger.info("MainWindowを初期化しました")

    def _setup_control_area(self, parent_layout):
        """
        コントロールエリアをセットアップ

        テーマ選択ComboBoxと「今すぐ更新」ボタンを配置します。

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

        # 「今すぐ更新」ボタン
        self.update_button = QPushButton("今すぐ更新")
        self.update_button.setObjectName("update_button")
        self.update_button.clicked.connect(self._on_update_clicked)
        control_layout.addWidget(self.update_button)

        parent_layout.addLayout(control_layout)

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

        # テーマ一覧をComboBoxに設定
        themes = self.viewmodel.get_available_themes()
        if themes:
            self.theme_combo.clear()
            self.theme_combo.addItems(themes)
            self.theme_combo.setCurrentText(self.viewmodel.current_theme)

    @pyqtSlot(str)
    def _on_theme_changed(self, theme_name: str):
        """
        テーマが変更されたときの処理

        Args:
            theme_name (str): 新しいテーマ名
        """
        self.viewmodel.set_theme(theme_name)
        logger.info(f"テーマを変更しました: {theme_name}")

    @pyqtSlot(str)
    def _on_viewmodel_theme_changed(self, theme_name: str):
        """
        ViewModelのテーマが変更されたときの処理

        Args:
            theme_name (str): 新しいテーマ名
        """
        # プレビューをクリア（テーマ変更時）
        self.preview_widget.clear_preview()
        self.statusBar().showMessage(f"テーマ: {theme_name}")

    @pyqtSlot()
    def _on_update_clicked(self):
        """
        「今すぐ更新」ボタンがクリックされたときの処理

        ViewModelに壁紙更新を依頼します。
        """
        # ボタンを無効化
        self.update_button.setEnabled(False)

        # ViewModelに壁紙更新を依頼
        self.viewmodel.update_wallpaper()

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
        self.update_button.setEnabled(True)

        # ProgressBarを非表示
        self.progress_bar.hide()

        if success:
            self.statusBar().showMessage("壁紙を更新しました")
            logger.info("壁紙更新が完了しました")
        else:
            self.statusBar().showMessage("壁紙の更新に失敗しました")
            logger.warning("壁紙更新に失敗しました")

    @pyqtSlot(str)
    def _on_error_occurred(self, error_message: str, level: str = "ERROR"):
        """
        エラー発生時の処理

        Args:
            error_message (str): エラーメッセージ
            level (str): エラーレベル（ERROR, WARNING, CRITICAL）
        """
        # ステータスバーに表示
        self.statusBar().showMessage(f"エラー: {error_message}")
        logger.error(f"エラーが発生しました: {error_message}")

        # レベルに応じてダイアログ表示
        if level == "WARNING":
            QMessageBox.warning(self, "警告", error_message)
        elif level == "CRITICAL":
            QMessageBox.critical(self, "エラー", error_message)
        # ERROR レベルはステータスバーのみ（既存動作維持）

    def _on_critical_error(self, error_message: str):
        """
        重大なエラー発生時の処理

        Args:
            error_message (str): エラーメッセージ
        """
        # ステータスバーに表示
        self.statusBar().showMessage(f"エラー: {error_message}")
        logger.critical(f"重大なエラーが発生しました: {error_message}")

        # ダイアログで表示
        QMessageBox.critical(self, "エラー", error_message)
