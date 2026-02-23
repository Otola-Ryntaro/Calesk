"""
時間外イベント表示テスト

_get_off_hours_events と _draw_off_hours_strip の動作を検証する。
早朝（0〜8時）および深夜（22時以降）のイベントが
正しく収集・描画されることを確認する。
"""
import pytest
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from src.models.event import CalendarEvent
from src.image_generator import ImageGenerator


def _make_event(
    event_id: str,
    summary: str,
    start_hour: int,
    start_min: int,
    end_hour: int,
    end_min: int,
    base_date: date = None,
    is_all_day: bool = False,
    account_color: str = "#4285f4"
) -> CalendarEvent:
    """テスト用イベントを生成するヘルパー"""
    bd = base_date or date(2026, 2, 5)
    base_dt = datetime(bd.year, bd.month, bd.day)
    return CalendarEvent(
        id=event_id,
        summary=summary,
        start_datetime=base_dt.replace(hour=start_hour, minute=start_min),
        end_datetime=base_dt.replace(hour=end_hour, minute=end_min),
        is_all_day=is_all_day,
        calendar_id="primary",
        color_id="1",
        account_color=account_color
    )


@pytest.fixture
def generator():
    """ImageGeneratorインスタンスを生成するフィクスチャ"""
    with patch('src.image_generator.AUTO_DETECT_RESOLUTION', False):
        gen = ImageGenerator()
    return gen


class TestGetOffHoursEvents:
    """_get_off_hours_events の動作テスト"""

    def test_no_events_returns_empty(self, generator):
        """イベントなしの場合、両辞書とも空リスト"""
        today = date(2026, 2, 5)
        before, after = generator._get_off_hours_events([], today)
        assert all(len(v) == 0 for v in before.values())
        assert all(len(v) == 0 for v in after.values())

    def test_in_range_event_not_collected(self, generator):
        """通常時間帯（8〜22時）のイベントは収集しない"""
        today = date(2026, 2, 5)
        event = _make_event("e1", "会議", 10, 0, 11, 0, today)
        before, after = generator._get_off_hours_events([event], today)
        assert all(len(v) == 0 for v in before.values())
        assert all(len(v) == 0 for v in after.values())

    def test_early_morning_event_collected(self, generator):
        """8時前に終了する早朝イベントは before_events に収集される"""
        today = date(2026, 2, 5)
        event = _make_event("e1", "朝ラン", 6, 0, 7, 30, today)
        before, after = generator._get_off_hours_events([event], today)
        assert len(before[0]) == 1
        assert before[0][0].summary == "朝ラン"
        assert all(len(v) == 0 for v in after.values())

    def test_late_night_event_collected(self, generator):
        """22時以降に開始する深夜イベントは after_events に収集される"""
        today = date(2026, 2, 5)
        event = _make_event("e1", "深夜勉強", 23, 0, 23, 59, today)
        before, after = generator._get_off_hours_events([event], today)
        assert all(len(v) == 0 for v in before.values())
        assert len(after[0]) == 1
        assert after[0][0].summary == "深夜勉強"

    def test_all_day_event_is_ignored(self, generator):
        """終日イベントは収集しない"""
        today = date(2026, 2, 5)
        event = _make_event("e1", "終日イベント", 0, 0, 23, 59, today, is_all_day=True)
        before, after = generator._get_off_hours_events([event], today)
        assert all(len(v) == 0 for v in before.values())
        assert all(len(v) == 0 for v in after.values())

    def test_events_on_different_days(self, generator):
        """異なる曜日のイベントが正しいday_offsetに格納される"""
        today = date(2026, 2, 5)
        day3 = date(2026, 2, 8)
        event_day0 = _make_event("e1", "早朝0", 5, 0, 6, 0, today)
        event_day3 = _make_event("e2", "早朝3", 5, 0, 6, 0, day3)
        before, _ = generator._get_off_hours_events(
            [event_day0, event_day3], today
        )
        assert len(before[0]) == 1
        assert len(before[3]) == 1
        assert before[0][0].summary == "早朝0"
        assert before[3][0].summary == "早朝3"

    def test_event_outside_7day_window_ignored(self, generator):
        """7日間の表示範囲外のイベントは収集しない"""
        today = date(2026, 2, 5)
        future = date(2026, 2, 13)  # 8日後（範囲外）
        event = _make_event("e1", "未来", 5, 0, 6, 0, future)
        before, after = generator._get_off_hours_events([event], today)
        assert all(len(v) == 0 for v in before.values())
        assert all(len(v) == 0 for v in after.values())

    def test_boundary_at_start_hour_is_not_early(self, generator):
        """開始時刻ちょうど8:00に終了するイベントは早朝として収集される（<= 境界）"""
        today = date(2026, 2, 5)
        # 7:00〜8:00: end_hour==8 なので before に入る（end_hour <= START_HOUR）
        event = _make_event("e1", "境界", 7, 0, 8, 0, today)
        before, _ = generator._get_off_hours_events([event], today)
        assert len(before[0]) == 1

    def test_boundary_at_end_hour_is_late(self, generator):
        """22:00ちょうどに開始するイベントは深夜として収集される（>= 境界）"""
        today = date(2026, 2, 5)
        # 22:00〜23:00: start_hour==22 なので after に入る（start_hour >= END_HOUR）
        event = _make_event("e1", "境界深夜", 22, 0, 23, 0, today)
        _, after = generator._get_off_hours_events([event], today)
        assert len(after[0]) == 1


class TestDrawOffHoursStrip:
    """_draw_off_hours_strip の描画テスト"""

    def test_empty_events_no_drawing(self, generator):
        """イベントなしの場合、drawが呼ばれない"""
        mock_draw = MagicMock()
        events_by_day = {i: [] for i in range(7)}
        # エラーが発生しないことを確認
        generator._draw_off_hours_strip(mock_draw, events_by_day, 100, 500)
        mock_draw.ellipse.assert_not_called()

    def test_single_event_draws_one_dot(self, generator):
        """1件のイベントで1つのドットが描画される"""
        today = date(2026, 2, 5)
        event = _make_event("e1", "早朝", 6, 0, 7, 0, today, account_color="#ff0000")
        events_by_day = {i: [] for i in range(7)}
        events_by_day[0] = [event]

        mock_draw = MagicMock()
        generator._draw_off_hours_strip(mock_draw, events_by_day, 100, 500)
        assert mock_draw.ellipse.call_count == 1

    def test_multiple_events_draws_multiple_dots(self, generator):
        """3件のイベントで3つのドットが描画される"""
        today = date(2026, 2, 5)
        events = [
            _make_event(f"e{i}", f"早朝{i}", 5+i, 0, 6+i, 0, today)
            for i in range(3)
        ]
        events_by_day = {i: [] for i in range(7)}
        events_by_day[0] = events

        mock_draw = MagicMock()
        generator._draw_off_hours_strip(mock_draw, events_by_day, 100, 500)
        assert mock_draw.ellipse.call_count == 3

    def test_excess_events_shows_plus_n_text(self, generator):
        """5件のイベントで最大4ドット + "+1" テキストが表示される"""
        today = date(2026, 2, 5)
        events = [
            _make_event(f"e{i}", f"早朝{i}", 1+i, 0, 2+i, 0, today)
            for i in range(5)
        ]
        events_by_day = {i: [] for i in range(7)}
        events_by_day[0] = events

        mock_draw = MagicMock()
        generator._draw_off_hours_strip(mock_draw, events_by_day, 100, 500)
        assert mock_draw.ellipse.call_count == 4
        mock_draw.text.assert_called_once()
        # "+1" が描画されていることを確認
        call_args = mock_draw.text.call_args
        assert "+1" in call_args[0]

    def test_events_in_different_columns(self, generator):
        """複数日のイベントがそれぞれの列に描画される"""
        today = date(2026, 2, 5)
        events_by_day = {i: [] for i in range(7)}
        events_by_day[0] = [_make_event("e1", "早朝0", 5, 0, 6, 0, today)]
        events_by_day[3] = [_make_event("e2", "早朝3", 5, 0, 6, 0, date(2026, 2, 8))]

        mock_draw = MagicMock()
        generator._draw_off_hours_strip(mock_draw, events_by_day, 100, 500)
        assert mock_draw.ellipse.call_count == 2


class TestWeekCalendarWithOffHours:
    """週間カレンダー描画の時間外イベント統合テスト"""

    def test_draw_week_calendar_with_before_events(self, generator):
        """早朝イベントがある場合でも _draw_week_calendar が正常に完了する"""
        from PIL import Image, ImageDraw
        image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)

        today = datetime.now().date()
        early_event = CalendarEvent(
            id="e1",
            summary="早朝ラン",
            start_datetime=datetime(today.year, today.month, today.day, 5, 30),
            end_datetime=datetime(today.year, today.month, today.day, 6, 30),
            is_all_day=False,
            calendar_id="primary",
            color_id="1",
            account_color="#4285f4"
        )

        # エラーなく完了することを確認
        generator._draw_week_calendar(draw, [early_event], 400, image=image)
        image.close()

    def test_draw_week_calendar_with_after_events(self, generator):
        """深夜イベントがある場合でも _draw_week_calendar が正常に完了する"""
        from PIL import Image, ImageDraw
        image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)

        today = datetime.now().date()
        late_event = CalendarEvent(
            id="e1",
            summary="深夜作業",
            start_datetime=datetime(today.year, today.month, today.day, 23, 0),
            end_datetime=datetime(today.year, today.month, today.day, 23, 59),
            is_all_day=False,
            calendar_id="primary",
            color_id="1",
            account_color="#ea4335"
        )

        generator._draw_week_calendar(draw, [late_event], 400, image=image)
        image.close()
