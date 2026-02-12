"""
通知機能モジュール
予定開始前にデスクトップ通知を送信
"""
import logging
from datetime import datetime, timedelta
from typing import List, Set

from plyer import notification

from .config import NOTIFICATION_ADVANCE_MINUTES
from .models.event import CalendarEvent

logger = logging.getLogger(__name__)


class Notifier:
    """通知送信クラス"""

    def __init__(self):
        self.advance_minutes = NOTIFICATION_ADVANCE_MINUTES
        self.notified_event_ids: Set[str] = set()

    def send_notification(
        self,
        title: str,
        message: str,
        app_name: str = 'Calesk',
        timeout: int = 10
    ) -> bool:
        """
        デスクトップ通知を送信

        Args:
            title: 通知タイトル
            message: 通知メッセージ
            app_name: アプリケーション名
            timeout: 通知表示時間（秒）

        Returns:
            bool: 送信成功でTrue、失敗でFalse
        """
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=app_name,
                timeout=timeout
            )
            logger.info(f"通知を送信しました: {title}")
            return True

        except Exception as e:
            logger.error(f"通知送信エラー: {e}")
            return False

    def check_upcoming_events(self, events: List[CalendarEvent]) -> None:
        """
        今後の予定をチェックして通知が必要なイベントを通知

        Args:
            events: イベントリスト
        """
        now = datetime.now()
        notification_time = now + timedelta(minutes=self.advance_minutes)

        for event in events:
            # 終日イベントはスキップ
            if event.is_all_day:
                continue

            start_time = event.start_datetime

            # タイムゾーンをローカルに変換（必要に応じて）
            if start_time.tzinfo:
                start_time = start_time.replace(tzinfo=None)

            # 通知タイミングをチェック
            time_until_event = (start_time - now).total_seconds() / 60

            if 0 < time_until_event <= self.advance_minutes:
                # 通知済みのイベントはスキップ
                if event.id in self.notified_event_ids:
                    continue
                self._send_event_notification(event, int(time_until_event))

    def _send_event_notification(self, event: CalendarEvent, minutes_until: int) -> None:
        """
        特定のイベントについて通知を送信

        Args:
            event: イベント情報
            minutes_until: 開始までの分数
        """
        title = f"予定開始 {minutes_until}分前"
        start_time = event.start_datetime.strftime('%H:%M')
        summary = event.summary
        location = event.location

        if location:
            message = f"{start_time} - {summary}\n場所: {location}"
        else:
            message = f"{start_time} - {summary}"

        success = self.send_notification(title, message)
        if success:
            self.notified_event_ids.add(event.id)

    def clear_notified_ids(self) -> None:
        """
        通知済みイベントIDをクリア

        日付変更時やリセットが必要な場合に使用する。
        """
        self.notified_event_ids = set()

    def send_update_notification(self) -> None:
        """
        壁紙更新完了の通知を送信
        """
        self.send_notification(
            title='壁紙を更新しました',
            message='今日の予定が表示されています',
            timeout=5
        )
