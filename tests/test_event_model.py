"""
CalendarEventモデルのテスト
"""
import pytest
from datetime import datetime
from src.models.event import CalendarEvent


class TestCalendarEvent:
    """CalendarEventモデルのテストクラス"""

    def test_create_event_with_required_fields(self):
        """必須フィールドのみでイベントを作成できる"""
        event = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary"
        )

        assert event.id == "event123"
        assert event.summary == "ミーティング"
        assert event.start_datetime == datetime(2026, 2, 5, 14, 0)
        assert event.end_datetime == datetime(2026, 2, 5, 15, 0)
        assert event.is_all_day is False
        assert event.calendar_id == "primary"
        # デフォルト値
        assert event.location == ""
        assert event.description == ""
        assert event.color_id == "1"

    def test_create_event_with_all_fields(self):
        """全フィールドでイベントを作成できる"""
        event = CalendarEvent(
            id="event456",
            summary="プレゼンテーション",
            start_datetime=datetime(2026, 2, 6, 10, 0),
            end_datetime=datetime(2026, 2, 6, 11, 30),
            is_all_day=False,
            calendar_id="work",
            location="会議室A",
            description="四半期報告",
            color_id="5"
        )

        assert event.location == "会議室A"
        assert event.description == "四半期報告"
        assert event.color_id == "5"

    def test_create_all_day_event(self):
        """終日イベントを作成できる"""
        event = CalendarEvent(
            id="event789",
            summary="休暇",
            start_datetime=datetime(2026, 2, 7),
            end_datetime=datetime(2026, 2, 8),
            is_all_day=True,
            calendar_id="personal"
        )

        assert event.is_all_day is True
        assert event.summary == "休暇"

    def test_to_dict(self):
        """to_dict()でDict形式に変換できる"""
        event = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary",
            location="オンライン",
            description="定例会議",
            color_id="3"
        )

        result = event.to_dict()

        assert result['id'] == "event123"
        assert result['summary'] == "ミーティング"
        assert result['start_datetime'] == datetime(2026, 2, 5, 14, 0)
        assert result['end_datetime'] == datetime(2026, 2, 5, 15, 0)
        assert result['is_all_day'] is False
        assert result['calendar_id'] == "primary"
        assert result['location'] == "オンライン"
        assert result['description'] == "定例会議"
        assert result['color_id'] == "3"

    def test_from_dict(self):
        """from_dict()でDict形式から変換できる"""
        data = {
            'id': 'event999',
            'summary': 'ランチ',
            'start_datetime': datetime(2026, 2, 5, 12, 0),
            'end_datetime': datetime(2026, 2, 5, 13, 0),
            'is_all_day': False,
            'calendar_id': 'personal',
            'location': 'レストラン',
            'description': 'チームランチ',
            'color_id': '2'
        }

        event = CalendarEvent.from_dict(data)

        assert event.id == 'event999'
        assert event.summary == 'ランチ'
        assert event.start_datetime == datetime(2026, 2, 5, 12, 0)
        assert event.end_datetime == datetime(2026, 2, 5, 13, 0)
        assert event.location == 'レストラン'

    def test_from_dict_with_defaults(self):
        """from_dict()でデフォルト値を使用できる"""
        data = {
            'id': 'event111',
            'summary': 'タスク',
            'start_datetime': datetime(2026, 2, 5, 9, 0),
            'end_datetime': datetime(2026, 2, 5, 10, 0),
            'is_all_day': False,
            'calendar_id': 'work'
        }

        event = CalendarEvent.from_dict(data)

        assert event.location == ""
        assert event.description == ""
        assert event.color_id == "1"

    def test_start_time_str(self):
        """start_time_str()で時刻文字列を取得できる"""
        event = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 30),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary"
        )

        assert event.start_time_str() == "14:30"

    def test_end_time_str(self):
        """end_time_str()で時刻文字列を取得できる"""
        event = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 45),
            is_all_day=False,
            calendar_id="primary"
        )

        assert event.end_time_str() == "15:45"

    def test_date_str(self):
        """date_str()で日付文字列を取得できる"""
        event = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary"
        )

        assert event.date_str() == "2026-02-05"

    def test_event_immutability(self):
        """イベントがイミュータブルであることを確認"""
        event = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary"
        )

        with pytest.raises(AttributeError):
            event.summary = "新しいタイトル"

    def test_event_equality(self):
        """同じ内容のイベントは等しい"""
        event1 = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary"
        )

        event2 = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary"
        )

        assert event1 == event2

    def test_event_hash(self):
        """イベントをsetやdictのキーとして使用できる"""
        event = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary"
        )

        events_set = {event}
        assert event in events_set

        events_dict = {event: "value"}
        assert events_dict[event] == "value"

    def test_account_fields_with_defaults(self):
        """アカウント情報フィールドがデフォルト値で作成できる"""
        event = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary"
        )

        # デフォルト値
        assert event.account_id == "default"
        assert event.account_color == "#4285f4"
        assert event.account_display_name == ""

    def test_account_fields_with_values(self):
        """アカウント情報フィールドを指定して作成できる"""
        event = CalendarEvent(
            id="event123",
            summary="仕事のミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="work",
            account_id="account_work",
            account_color="#ea4335",
            account_display_name="仕事用アカウント"
        )

        assert event.account_id == "account_work"
        assert event.account_color == "#ea4335"
        assert event.account_display_name == "仕事用アカウント"

    def test_to_dict_with_account_fields(self):
        """to_dict()でアカウント情報フィールドが含まれる"""
        event = CalendarEvent(
            id="event123",
            summary="ミーティング",
            start_datetime=datetime(2026, 2, 5, 14, 0),
            end_datetime=datetime(2026, 2, 5, 15, 0),
            is_all_day=False,
            calendar_id="primary",
            account_id="account_1",
            account_color="#00ff00",
            account_display_name="プライベート"
        )

        result = event.to_dict()

        assert result['account_id'] == "account_1"
        assert result['account_color'] == "#00ff00"
        assert result['account_display_name'] == "プライベート"

    def test_from_dict_with_account_fields(self):
        """from_dict()でアカウント情報フィールドを読み込める"""
        data = {
            'id': 'event999',
            'summary': 'ランチ',
            'start_datetime': datetime(2026, 2, 5, 12, 0),
            'end_datetime': datetime(2026, 2, 5, 13, 0),
            'is_all_day': False,
            'calendar_id': 'personal',
            'account_id': 'account_private',
            'account_color': '#ff0000',
            'account_display_name': 'プライベート用'
        }

        event = CalendarEvent.from_dict(data)

        assert event.account_id == 'account_private'
        assert event.account_color == '#ff0000'
        assert event.account_display_name == 'プライベート用'

    def test_from_dict_with_account_defaults(self):
        """from_dict()でアカウント情報フィールドのデフォルト値を使用できる"""
        data = {
            'id': 'event111',
            'summary': 'タスク',
            'start_datetime': datetime(2026, 2, 5, 9, 0),
            'end_datetime': datetime(2026, 2, 5, 10, 0),
            'is_all_day': False,
            'calendar_id': 'work'
        }

        event = CalendarEvent.from_dict(data)

        assert event.account_id == "default"
        assert event.account_color == "#4285f4"
        assert event.account_display_name == ""
