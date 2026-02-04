"""
定期実行管理モジュール
壁紙更新と通知チェックのスケジューリング
"""
import time
import logging
from typing import Callable
import schedule

from .config import UPDATE_TIME

logger = logging.getLogger(__name__)


class Scheduler:
    """スケジューラークラス"""

    def __init__(self):
        self.is_running = False
        self.update_callback = None
        self.notification_callback = None

    def set_update_callback(self, callback: Callable) -> None:
        """
        壁紙更新のコールバック関数を設定

        Args:
            callback: 壁紙更新時に呼び出される関数
        """
        self.update_callback = callback
        logger.info("壁紙更新コールバックを設定しました")

    def set_notification_callback(self, callback: Callable) -> None:
        """
        通知チェックのコールバック関数を設定

        Args:
            callback: 通知チェック時に呼び出される関数
        """
        self.notification_callback = callback
        logger.info("通知チェックコールバックを設定しました")

    def schedule_tasks(self) -> None:
        """
        タスクをスケジュール
        """
        # 壁紙更新: 毎日指定時刻
        if self.update_callback:
            schedule.every().day.at(UPDATE_TIME).do(self._run_update)
            logger.info(f"壁紙更新を {UPDATE_TIME} にスケジュールしました")

        # 通知チェック: 5分ごと
        if self.notification_callback:
            schedule.every(5).minutes.do(self._run_notification_check)
            logger.info("通知チェックを5分ごとにスケジュールしました")

    def _run_update(self) -> None:
        """
        壁紙更新タスクを実行（内部用）
        """
        try:
            logger.info("=== 壁紙更新タスクを開始 ===")
            if self.update_callback:
                self.update_callback()
            logger.info("=== 壁紙更新タスクが完了 ===")
        except Exception as e:
            logger.error(f"壁紙更新タスクでエラーが発生: {e}")

    def _run_notification_check(self) -> None:
        """
        通知チェックタスクを実行（内部用）
        """
        try:
            logger.debug("通知チェックを実行中...")
            if self.notification_callback:
                self.notification_callback()
        except Exception as e:
            logger.error(f"通知チェックでエラーが発生: {e}")

    def run_once(self) -> None:
        """
        スケジュールされたタスクを即座に1回実行
        （テスト・初回実行用）
        """
        logger.info("手動実行: 壁紙更新タスク")
        self._run_update()

        logger.info("手動実行: 通知チェック")
        self._run_notification_check()

    def start(self) -> None:
        """
        スケジューラーを開始（ブロッキング）
        """
        if self.is_running:
            logger.warning("スケジューラーは既に実行中です")
            return

        logger.info("スケジューラーを開始します")
        self.is_running = True

        # 初回実行
        self.run_once()

        # スケジュールループ
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック

        except KeyboardInterrupt:
            logger.info("スケジューラーを停止します (Ctrl+C)")
            self.stop()

    def stop(self) -> None:
        """
        スケジューラーを停止
        """
        self.is_running = False
        schedule.clear()
        logger.info("スケジューラーを停止しました")
