"""
チケット012: 上段カード - 今日・明日・明後日の3列レイアウト テスト

TDD RED phase: 3列レイアウト機能の期待動作を定義
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from PIL import Image, ImageDraw

from src.models.event import CalendarEvent


def _make_event(summary, start_dt, end_dt, color_id='1', is_all_day=False):
    """テスト用CalendarEventを作成"""
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


class TestCompactCardConfig:
    """config.py のコンパクトカード設定テスト"""

    def test_compact_card_height_exists(self):
        """COMPACT_CARD_HEIGHT が定義されていること"""
        from src.config import COMPACT_CARD_HEIGHT
        assert COMPACT_CARD_HEIGHT > 0
        assert COMPACT_CARD_HEIGHT < 100  # コンパクトなので100px未満

    def test_compact_card_width_exists(self):
        """COMPACT_CARD_WIDTH が定義されていること"""
        from src.config import COMPACT_CARD_WIDTH
        assert COMPACT_CARD_WIDTH > 0

    def test_max_cards_per_column(self):
        """MAX_CARDS_PER_COLUMN が定義されていること"""
        from src.config import MAX_CARDS_PER_COLUMN
        assert MAX_CARDS_PER_COLUMN >= 3

    def test_column_header_height(self):
        """COLUMN_HEADER_HEIGHT が定義されていること"""
        from src.config import COLUMN_HEADER_HEIGHT
        assert COLUMN_HEADER_HEIGHT > 0


class TestThreeColumnDrawing:
    """3列レイアウトの描画テスト"""

    def _create_generator(self, theme='simple'):
        """テスト用ImageGeneratorを作成"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', theme):
            gen = ImageGenerator()
        return gen

    def _make_events_for_days(self):
        """3日分のテストイベントを作成"""
        now = datetime.now()
        today = now.replace(hour=10, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)

        events = [
            # 今日のイベント
            _make_event('朝会', today.replace(hour=9), today.replace(hour=10), color_id='1'),
            _make_event('会議', today.replace(hour=14), today.replace(hour=15), color_id='2'),
            # 明日のイベント
            _make_event('ランチ', tomorrow.replace(hour=12), tomorrow.replace(hour=13), color_id='3'),
            # 明後日のイベント
            _make_event('打合せ', day_after.replace(hour=15), day_after.replace(hour=16), color_id='4'),
            _make_event('面談', day_after.replace(hour=17), day_after.replace(hour=18), color_id='5'),
        ]
        return events

    def test_draw_event_cards_accepts_week_events(self):
        """_draw_event_cards が week_events パラメータを受け付けること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        events = self._make_events_for_days()
        # week_events パラメータを渡して呼び出し（エラーなし）
        gen._draw_event_cards(draw, [], 100, week_events=events)

    def test_draw_compact_event_card_exists(self):
        """_draw_compact_event_card メソッドが存在すること"""
        gen = self._create_generator()
        assert hasattr(gen, '_draw_compact_event_card')

    def test_draw_compact_event_card_renders(self):
        """コンパクトカードが描画されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (400, 100), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        now = datetime.now()
        event = _make_event(
            '会議', now.replace(hour=10), now.replace(hour=11)
        )

        # エラーなく描画が完了すること
        gen._draw_compact_event_card(draw, event, 10, 10, is_finished=False)

    def test_three_column_layout_with_events(self):
        """3列にイベントが正しく配分されること"""
        gen = self._create_generator()
        events = self._make_events_for_days()

        days = gen._get_events_for_days(events)
        assert len(days['today']) == 2
        assert len(days['tomorrow']) == 1
        assert len(days['day_after']) == 2

    def test_three_column_layout_with_no_events(self):
        """イベント0件でもエラーなく描画されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        gen._draw_event_cards(draw, [], 100, week_events=[])

    def test_compact_card_shows_color_bar(self):
        """コンパクトカードにカラーバーが表示されること"""
        from src.config import COMPACT_CARD_PADDING
        gen = self._create_generator()
        img = Image.new('RGBA', (400, 100), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        now = datetime.now()
        event = _make_event(
            '会議', now.replace(hour=10), now.replace(hour=11),
            color_id='4'  # フラミンゴ色
        )

        gen._draw_compact_event_card(draw, event, 10, 10, is_finished=False)

        # カラーバー位置: x + COMPACT_CARD_PADDING + 1, y + 5〜y + COMPACT_CARD_HEIGHT - 5
        bar_x = 10 + COMPACT_CARD_PADDING + 1
        pixel = img.getpixel((bar_x, 20))
        assert pixel != (255, 255, 255, 255), "カラーバーが描画されるべき"

    def test_compact_card_finished_event_grayed(self):
        """終了済みイベントのコンパクトカードがグレーアウトされること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (400, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        now = datetime.now()
        event = _make_event(
            '終了会議', now.replace(hour=8), now.replace(hour=9)
        )

        gen._draw_compact_event_card(draw, event, 10, 10, is_finished=True)


class TestThreeColumnIntegration:
    """3列レイアウトの統合テスト"""

    def _make_events_for_days(self):
        """3日分のテストイベントを作成"""
        now = datetime.now()
        today = now.replace(hour=10, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)

        return [
            _make_event('朝会', today.replace(hour=9), today.replace(hour=10)),
            _make_event('会議', today.replace(hour=14), today.replace(hour=15)),
            _make_event('ランチ', tomorrow.replace(hour=12), tomorrow.replace(hour=13)),
            _make_event('打合せ', day_after.replace(hour=15), day_after.replace(hour=16)),
        ]

    def test_wallpaper_with_three_column_layout(self):
        """3列レイアウトで壁紙が正常に生成されること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            events = self._make_events_for_days()
            output = gen.generate_wallpaper(events, events)
            assert output is not None
            assert output.exists()
            img = Image.open(output)
            assert img.size[0] > 0

    def test_wallpaper_all_themes_with_events(self):
        """全テーマで3列レイアウトが動作すること"""
        from src.image_generator import ImageGenerator
        events = self._make_events_for_days()

        for theme_name in ['simple', 'modern', 'pastel', 'dark', 'vibrant']:
            with patch('src.image_generator.THEME', theme_name):
                gen = ImageGenerator()
                output = gen.generate_wallpaper(events, events)
                assert output is not None, f"{theme_name}テーマで壁紙生成に失敗"

    def test_wallpaper_with_empty_events(self):
        """イベント0件で壁紙が正常に生成されること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            output = gen.generate_wallpaper([], [])
            assert output is not None
            assert output.exists()

    def test_wallpaper_with_many_events(self):
        """大量のイベントでも壁紙が正常に生成されること"""
        from src.image_generator import ImageGenerator
        now = datetime.now()
        today = now.replace(hour=8, minute=0, second=0, microsecond=0)

        events = []
        for i in range(10):
            events.append(_make_event(
                f'イベント{i}',
                today.replace(hour=8 + i),
                today.replace(hour=9 + i),
                color_id=str((i % 5) + 1)
            ))

        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            output = gen.generate_wallpaper(events, events)
            assert output is not None
