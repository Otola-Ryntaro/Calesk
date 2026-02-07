"""
Notifier（通知機能）のテスト

通知の重複送信防止、エッジケース、基本動作を検証する。
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.notifier import Notifier
from src.models.event import CalendarEvent


# === ヘルパー関数 ===

def _make_event(
    event_id: str = "evt_001",
    summary: str = "テスト会議",
    minutes_from_now: int = 10,
    is_all_day: bool = False,
    location: str = "",
    calendar_id: str = "primary",
) -> CalendarEvent:
    """テスト用イベントを生成するヘルパー"""
    now = datetime.now()
    start = now + timedelta(minutes=minutes_from_now)
    end = start + timedelta(hours=1)
    return CalendarEvent(
        id=event_id,
        summary=summary,
        start_datetime=start,
        end_datetime=end,
        is_all_day=is_all_day,
        calendar_id=calendar_id,
        location=location,
    )


# === send_notification のテスト ===

class TestSendNotification:
    """send_notification メソッドの基本動作テスト"""

    @patch("src.notifier.notification")
    def test_send_notification_success(self, mock_notification):
        """通知送信が成功した場合 True を返す"""
        notifier = Notifier()
        result = notifier.send_notification("テスト", "テストメッセージ")

        assert result is True
        mock_notification.notify.assert_called_once_with(
            title="テスト",
            message="テストメッセージ",
            app_name="カレンダー壁紙アプリ",
            timeout=10,
        )

    @patch("src.notifier.notification")
    def test_send_notification_failure(self, mock_notification):
        """通知送信が失敗した場合 False を返す"""
        mock_notification.notify.side_effect = Exception("通知エラー")
        notifier = Notifier()
        result = notifier.send_notification("テスト", "テストメッセージ")

        assert result is False

    @patch("src.notifier.notification")
    def test_send_notification_custom_params(self, mock_notification):
        """カスタムパラメータで通知を送信できる"""
        notifier = Notifier()
        result = notifier.send_notification(
            "カスタム", "メッセージ", app_name="テストアプリ", timeout=5
        )

        assert result is True
        mock_notification.notify.assert_called_once_with(
            title="カスタム",
            message="メッセージ",
            app_name="テストアプリ",
            timeout=5,
        )


# === check_upcoming_events のテスト ===

class TestCheckUpcomingEvents:
    """check_upcoming_events メソッドの基本動作テスト"""

    @patch("src.notifier.notification")
    def test_notifies_upcoming_event_within_window(self, mock_notification):
        """通知ウィンドウ内のイベントに対して通知を送信する"""
        notifier = Notifier()
        event = _make_event(minutes_from_now=10)

        notifier.check_upcoming_events([event])

        mock_notification.notify.assert_called_once()

    @patch("src.notifier.notification")
    def test_skips_all_day_events(self, mock_notification):
        """終日イベントは通知しない"""
        notifier = Notifier()
        event = _make_event(is_all_day=True, minutes_from_now=10)

        notifier.check_upcoming_events([event])

        mock_notification.notify.assert_not_called()

    @patch("src.notifier.notification")
    def test_skips_past_events(self, mock_notification):
        """過去のイベントは通知しない"""
        notifier = Notifier()
        event = _make_event(minutes_from_now=-5)

        notifier.check_upcoming_events([event])

        mock_notification.notify.assert_not_called()

    @patch("src.notifier.notification")
    def test_skips_far_future_events(self, mock_notification):
        """通知ウィンドウ外（遠い未来）のイベントは通知しない"""
        notifier = Notifier()
        event = _make_event(minutes_from_now=120)

        notifier.check_upcoming_events([event])

        mock_notification.notify.assert_not_called()

    @patch("src.notifier.notification")
    def test_notifies_multiple_different_events(self, mock_notification):
        """複数の異なるイベントにはそれぞれ通知する"""
        notifier = Notifier()
        events = [
            _make_event(event_id="evt_001", summary="会議A", minutes_from_now=10),
            _make_event(event_id="evt_002", summary="会議B", minutes_from_now=15),
        ]

        notifier.check_upcoming_events(events)

        assert mock_notification.notify.call_count == 2

    @patch("src.notifier.notification")
    def test_empty_event_list(self, mock_notification):
        """空のイベントリストでは通知しない"""
        notifier = Notifier()
        notifier.check_upcoming_events([])

        mock_notification.notify.assert_not_called()


# === 重複通知防止のテスト（核心部分） ===

class TestDuplicateNotificationPrevention:
    """
    同一イベントに対する重複通知防止のテスト

    これが M-1 チケットの核心。
    5分ごとに check_upcoming_events が呼ばれても、
    同じイベントIDに対しては1回のみ通知することを検証する。
    """

    @patch("src.notifier.notification")
    def test_same_event_notified_only_once(self, mock_notification):
        """同一イベントを2回チェックしても通知は1回のみ"""
        notifier = Notifier()
        event = _make_event(event_id="evt_dup_001", minutes_from_now=10)

        # 1回目: 通知される
        notifier.check_upcoming_events([event])
        assert mock_notification.notify.call_count == 1

        # 2回目: 同じイベントなので通知されない
        notifier.check_upcoming_events([event])
        assert mock_notification.notify.call_count == 1  # 変わらず1回

    @patch("src.notifier.notification")
    def test_same_event_three_calls_still_once(self, mock_notification):
        """同一イベントを3回チェックしても通知は1回のみ"""
        notifier = Notifier()
        event = _make_event(event_id="evt_dup_002", minutes_from_now=15)

        notifier.check_upcoming_events([event])
        notifier.check_upcoming_events([event])
        notifier.check_upcoming_events([event])

        assert mock_notification.notify.call_count == 1

    @patch("src.notifier.notification")
    def test_different_events_each_notified_once(self, mock_notification):
        """異なるイベントはそれぞれ1回ずつ通知される"""
        notifier = Notifier()
        event_a = _make_event(event_id="evt_a", summary="会議A", minutes_from_now=10)
        event_b = _make_event(event_id="evt_b", summary="会議B", minutes_from_now=15)

        # 1回目: event_a のみ
        notifier.check_upcoming_events([event_a])
        assert mock_notification.notify.call_count == 1

        # 2回目: event_a (通知済み) + event_b (新規)
        notifier.check_upcoming_events([event_a, event_b])
        assert mock_notification.notify.call_count == 2  # event_b の分だけ+1

    @patch("src.notifier.notification")
    def test_notified_ids_tracking(self, mock_notification):
        """通知済みイベントIDが正しく追跡される"""
        notifier = Notifier()
        event = _make_event(event_id="evt_track_001", minutes_from_now=10)

        notifier.check_upcoming_events([event])

        assert "evt_track_001" in notifier.notified_event_ids

    @patch("src.notifier.notification")
    def test_notified_ids_initially_empty(self, mock_notification):
        """初期状態では通知済みIDセットは空"""
        notifier = Notifier()

        assert hasattr(notifier, "notified_event_ids")
        assert len(notifier.notified_event_ids) == 0


# === 通知済みIDクリアのテスト ===

class TestNotifiedIdsClear:
    """通知済みIDのクリア機能テスト"""

    @patch("src.notifier.notification")
    def test_clear_notified_ids(self, mock_notification):
        """clear_notified_ids で通知済みIDをクリアできる"""
        notifier = Notifier()
        event = _make_event(event_id="evt_clear_001", minutes_from_now=10)

        notifier.check_upcoming_events([event])
        assert mock_notification.notify.call_count == 1
        assert "evt_clear_001" in notifier.notified_event_ids

        # クリア
        notifier.clear_notified_ids()
        assert len(notifier.notified_event_ids) == 0

        # クリア後は同じイベントでも再通知される
        notifier.check_upcoming_events([event])
        assert mock_notification.notify.call_count == 2

    @patch("src.notifier.notification")
    def test_clear_notified_ids_when_already_empty(self, mock_notification):
        """空の状態でクリアしてもエラーにならない"""
        notifier = Notifier()
        notifier.clear_notified_ids()

        assert len(notifier.notified_event_ids) == 0


# === _send_event_notification のテスト ===

class TestSendEventNotification:
    """_send_event_notification メソッドのフォーマットテスト"""

    @patch("src.notifier.notification")
    def test_notification_format_without_location(self, mock_notification):
        """場所なしイベントの通知フォーマット"""
        notifier = Notifier()
        event = _make_event(summary="チームMTG", location="")

        notifier._send_event_notification(event, 10)

        call_args = mock_notification.notify.call_args
        assert call_args.kwargs["title"] == "予定開始 10分前"
        assert "チームMTG" in call_args.kwargs["message"]
        assert "場所:" not in call_args.kwargs["message"]

    @patch("src.notifier.notification")
    def test_notification_format_with_location(self, mock_notification):
        """場所ありイベントの通知フォーマット"""
        notifier = Notifier()
        event = _make_event(summary="客先訪問", location="東京本社")

        notifier._send_event_notification(event, 5)

        call_args = mock_notification.notify.call_args
        assert call_args.kwargs["title"] == "予定開始 5分前"
        assert "客先訪問" in call_args.kwargs["message"]
        assert "場所: 東京本社" in call_args.kwargs["message"]


# === send_update_notification のテスト ===

class TestSendUpdateNotification:
    """send_update_notification メソッドのテスト"""

    @patch("src.notifier.notification")
    def test_sends_wallpaper_update_notification(self, mock_notification):
        """壁紙更新通知を送信する"""
        notifier = Notifier()
        notifier.send_update_notification()

        mock_notification.notify.assert_called_once_with(
            title="壁紙を更新しました",
            message="今日の予定が表示されています",
            app_name="カレンダー壁紙アプリ",
            timeout=5,
        )


# === エッジケースのテスト ===

class TestEdgeCases:
    """エッジケースの検証"""

    @patch("src.notifier.notification")
    def test_event_at_exact_boundary(self, mock_notification):
        """通知ウィンドウの境界ちょうどのイベント"""
        notifier = Notifier()
        # advance_minutes と同じ値 = ちょうど境界（<= なので通知される）
        event = _make_event(
            event_id="evt_boundary",
            minutes_from_now=notifier.advance_minutes,
        )

        notifier.check_upcoming_events([event])

        # advance_minutes 分後ちょうど = 通知ウィンドウ内
        mock_notification.notify.assert_called_once()

    @patch("src.notifier.notification")
    def test_event_just_past_zero(self, mock_notification):
        """開始時刻をちょうど過ぎたイベント（0分以下）は通知しない"""
        notifier = Notifier()
        event = _make_event(event_id="evt_past", minutes_from_now=0)

        notifier.check_upcoming_events([event])

        # time_until_event が 0 以下なので通知されない
        mock_notification.notify.assert_not_called()

    @patch("src.notifier.notification")
    def test_notification_failure_does_not_mark_as_notified(self, mock_notification):
        """通知送信失敗時は通知済みとしてマークしない"""
        mock_notification.notify.side_effect = Exception("通知失敗")
        notifier = Notifier()
        event = _make_event(event_id="evt_fail_001", minutes_from_now=10)

        notifier.check_upcoming_events([event])

        # 失敗したので通知済みに含まれない
        assert "evt_fail_001" not in notifier.notified_event_ids

    @patch("src.notifier.notification")
    def test_notification_failure_allows_retry(self, mock_notification):
        """通知失敗後、リトライで通知できる"""
        # 1回目: 失敗
        mock_notification.notify.side_effect = Exception("一時的エラー")
        notifier = Notifier()
        event = _make_event(event_id="evt_retry_001", minutes_from_now=10)

        notifier.check_upcoming_events([event])
        assert mock_notification.notify.call_count == 1
        assert "evt_retry_001" not in notifier.notified_event_ids

        # 2回目: 成功
        mock_notification.notify.side_effect = None
        notifier.check_upcoming_events([event])
        assert mock_notification.notify.call_count == 2
        assert "evt_retry_001" in notifier.notified_event_ids

    @patch("src.notifier.notification")
    def test_large_number_of_events(self, mock_notification):
        """大量のイベント(100件)を処理できる"""
        notifier = Notifier()
        events = [
            _make_event(
                event_id=f"evt_{i:03d}",
                summary=f"会議{i}",
                minutes_from_now=10,
            )
            for i in range(100)
        ]

        notifier.check_upcoming_events(events)

        assert mock_notification.notify.call_count == 100
        assert len(notifier.notified_event_ids) == 100

    @patch("src.notifier.notification")
    def test_special_characters_in_summary(self, mock_notification):
        """特殊文字を含むイベントでもエラーにならない"""
        notifier = Notifier()
        event = _make_event(
            event_id="evt_special",
            summary="会議 <script>alert('xss')</script> & 'quotes' \"double\"",
            minutes_from_now=10,
        )

        notifier.check_upcoming_events([event])

        assert mock_notification.notify.call_count == 1
