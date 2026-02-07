"""
チケット015: 日をまたぐ予定の横バー表示テスト

TDD RED phase: 複数日イベント横バー描画の期待動作を定義
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from PIL import Image, ImageDraw

from src.models.event import CalendarEvent


def _make_event(summary, start_dt, end_dt, color_id='1', is_all_day=False):
    return CalendarEvent(
        id=f'test_{summary}',
        summary=summary,
        start_datetime=start_dt,
        end_datetime=end_dt,
        is_all_day=is_all_day,
        calendar_id='primary',
        location=None,
        description=None,
        color_id=color_id
    )


class TestMultiDayEventExtraction:
    """複数日イベントの抽出テスト"""

    def _create_generator(self):
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            return ImageGenerator()

    def test_get_multi_day_events_method_exists(self):
        """_get_multi_day_events メソッドが存在すること"""
        gen = self._create_generator()
        assert hasattr(gen, '_get_multi_day_events')

    def test_extract_all_day_event(self):
        """終日イベントが抽出されること"""
        gen = self._create_generator()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        events = [
            _make_event('終日イベント', today, today + timedelta(days=1), is_all_day=True),
            _make_event('通常会議', today.replace(hour=10), today.replace(hour=11)),
        ]

        multi_day = gen._get_multi_day_events(events, today.date())
        assert len(multi_day) == 1
        assert multi_day[0].summary == '終日イベント'

    def test_extract_multi_day_event(self):
        """複数日にまたがるイベントが抽出されること"""
        gen = self._create_generator()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        events = [
            _make_event('出張', today, today + timedelta(days=3)),
            _make_event('通常会議', today.replace(hour=10), today.replace(hour=11)),
        ]

        multi_day = gen._get_multi_day_events(events, today.date())
        assert len(multi_day) == 1
        assert multi_day[0].summary == '出張'

    def test_no_multi_day_events(self):
        """複数日イベントがない場合は空リストを返すこと"""
        gen = self._create_generator()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        events = [
            _make_event('通常会議', today.replace(hour=10), today.replace(hour=11)),
        ]

        multi_day = gen._get_multi_day_events(events, today.date())
        assert len(multi_day) == 0


class TestMultiDayBarDrawing:
    """横バー描画テスト"""

    def _create_generator(self):
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            return ImageGenerator()

    def test_draw_multi_day_event_bars_method_exists(self):
        """_draw_multi_day_event_bars メソッドが存在すること"""
        gen = self._create_generator()
        assert hasattr(gen, '_draw_multi_day_event_bars')

    def test_draw_multi_day_bars(self):
        """横バーが描画されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        events = [
            _make_event('出張', today, today + timedelta(days=3), color_id='2', is_all_day=True),
        ]

        start_x = 100
        y_start = 200

        # 描画実行（エラーなし）
        height = gen._draw_multi_day_event_bars(
            draw, events, start_x, y_start, today.date()
        )

        # 返り値は描画に使った高さ
        assert height > 0

    def test_draw_max_three_bars(self):
        """最大3本の横バーが描画されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        events = [
            _make_event(f'イベント{i}', today, today + timedelta(days=2), is_all_day=True)
            for i in range(5)
        ]

        height = gen._draw_multi_day_event_bars(
            draw, events, 100, 200, today.date()
        )
        # 最大3本分の高さ（各約20px + margin）
        assert height > 0
        assert height <= 80  # 3本分 + margin


class TestMultiDayIntegration:
    """横バー表示の統合テスト"""

    def test_wallpaper_with_multi_day_events(self):
        """複数日イベントがある壁紙が正常に生成されること"""
        from src.image_generator import ImageGenerator

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        events = [
            _make_event('出張', today, today + timedelta(days=3), is_all_day=True),
            _make_event('通常会議', today.replace(hour=10), today.replace(hour=11)),
        ]

        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            output = gen.generate_wallpaper(events, events)
            assert output is not None
            assert output.exists()

    def test_wallpaper_all_themes_with_multi_day(self):
        """全テーマで複数日イベント壁紙が生成されること"""
        from src.image_generator import ImageGenerator

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        events = [
            _make_event('出張', today, today + timedelta(days=3), is_all_day=True),
        ]

        for theme in ['simple', 'modern', 'pastel', 'dark', 'vibrant']:
            with patch('src.image_generator.THEME', theme):
                gen = ImageGenerator()
                output = gen.generate_wallpaper(events, events)
                assert output is not None, f"{theme}テーマで壁紙生成に失敗"
