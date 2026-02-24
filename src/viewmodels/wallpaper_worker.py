"""
WallpaperWorker

非同期壁紙更新ワーカー。
UIスレッドをブロックせずに壁紙生成と設定を実行します。
"""

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """
    WallpaperWorkerのシグナル

    QRunnableはQObjectを継承していないため、
    シグナルを持つ別のQObjectクラスを用意します。
    """
    started = pyqtSignal()
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(bool)


class PreviewSignals(QObject):
    """PreviewWorkerのシグナル"""
    preview_ready = pyqtSignal(object)  # 生成されたPathまたはNone
    error = pyqtSignal(str)


class WallpaperWorker(QRunnable):
    """
    壁紙更新ワーカー

    QThreadPoolで実行される非同期ワーカーです。
    壁紙の生成と設定をバックグラウンドで実行し、
    進捗やエラーをシグナルで通知します。
    """

    def __init__(self, wallpaper_service, theme_name: str):
        """
        WallpaperWorkerを初期化

        Args:
            wallpaper_service: WallpaperServiceインスタンス
            theme_name (str): 使用するテーマ名
        """
        super().__init__()
        self.signals = WorkerSignals()
        self._wallpaper_service = wallpaper_service
        self._theme_name = theme_name
        self._is_cancelled = False

    @pyqtSlot()
    def run(self):
        """
        ワーカーを実行

        壁紙の生成と設定を実行し、進捗をシグナルで通知します。
        """
        try:
            # 開始シグナル
            self.signals.started.emit()
            self.signals.progress.emit(0)

            # キャンセルチェック
            if self._is_cancelled:
                logger.info("ワーカーがキャンセルされました")
                self.signals.result.emit(False)
                return

            # 壁紙生成と設定を実行
            self.signals.progress.emit(50)

            # 実行前にもう一度キャンセルチェック
            if self._is_cancelled:
                logger.info("ワーカーがキャンセルされました（実行前）")
                self.signals.result.emit(False)
                return

            # WallpaperServiceが内部でCalendarClientを使ってイベント取得
            success = self._wallpaper_service.generate_and_set_wallpaper(
                theme_name=self._theme_name
            )

            # 実行後にキャンセルされていた場合は失敗扱い
            if self._is_cancelled:
                logger.info("ワーカーがキャンセルされました（実行後）")
                success = False

            # 完了
            self.signals.progress.emit(100)
            self.signals.result.emit(success)

            logger.info(f"壁紙更新が完了しました: success={success}")

        except Exception as e:
            logger.error(f"壁紙更新中にエラーが発生しました: {e}")
            self.signals.error.emit(str(e))
            self.signals.result.emit(False)

        finally:
            self.signals.finished.emit()

    def cancel(self):
        """
        ワーカーをキャンセル

        実行中のワーカーにキャンセルフラグを設定します。
        """
        self._is_cancelled = True
        logger.info("ワーカーのキャンセルが要求されました")


class PreviewWorker(QRunnable):
    """
    プレビュー生成ワーカー

    UIスレッドをブロックせずにプレビュー画像を生成します。
    壁紙の設定は行いません。
    """

    def __init__(self, wallpaper_service, theme_name: str):
        """
        PreviewWorkerを初期化

        Args:
            wallpaper_service: WallpaperServiceインスタンス
            theme_name (str): プレビューするテーマ名
        """
        super().__init__()
        self.signals = PreviewSignals()
        self._wallpaper_service = wallpaper_service
        self._theme_name = theme_name
        self._is_cancelled = False

    @pyqtSlot()
    def run(self):
        """プレビュー画像を生成"""
        try:
            if self._is_cancelled:
                return

            if getattr(type(self._wallpaper_service), "generate_preview", None):
                preview_path = self._wallpaper_service.generate_preview(
                    theme_name=self._theme_name
                )
            else:
                preview_path = self._wallpaper_service.generate_wallpaper(
                    theme_name=self._theme_name
                )

            if not self._is_cancelled:
                self.signals.preview_ready.emit(preview_path)
                logger.info(f"プレビュー生成完了: {preview_path}")

        except Exception as e:
            if not self._is_cancelled:
                logger.error(f"プレビュー生成エラー: {e}")
                self.signals.error.emit(str(e))

    def cancel(self):
        """ワーカーをキャンセル"""
        self._is_cancelled = True
