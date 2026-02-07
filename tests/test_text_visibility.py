"""
テキスト視認性改善テスト

曜日ヘッダー・列ヘッダーの半透明背景による視認性向上を検証
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from PIL import Image, ImageDraw

from src.models.event import CalendarEvent


def _make_event(summary, start_dt, end_dt, color_id='1'):
    return CalendarEvent(
        id=f'test_{summary}',
        summary=summary,
        start_datetime=start_dt,
        end_datetime=end_dt,
        is_all_day=False,
        calendar_id='primary',
        location=None,
        description=None,
        color_id=color_id
    )


class TestHeaderBackgroundTheme:
    """テーマの header_bg 設定テスト"""

    def test_all_themes_have_header_bg(self):
        """全テーマに header_bg が定義されていること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            assert 'header_bg' in theme, \
                f"{name}テーマに header_bg がありません"

    def test_header_bg_has_alpha(self):
        """header_bg がRGBA（4要素）であること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            color = theme['header_bg']
            assert len(color) == 4, \
                f"{name}テーマの header_bg はRGBA（4要素）であるべき"

    def test_header_bg_alpha_range(self):
        """header_bg のアルファ値が適度であること（80-220）"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            alpha = theme['header_bg'][3]
            assert 80 <= alpha <= 220, \
                f"{name}テーマの header_bg アルファ値 {alpha} は80-220の範囲であるべき"


class TestWeekdayHeaderBackground:
    """曜日ヘッダー半透明背景テスト"""

    def _create_generator(self, theme='simple'):
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', theme):
            return ImageGenerator()

    def test_draw_week_calendar_with_header_bg(self):
        """曜日ヘッダー背景付きで週間カレンダーが描画されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (1920, 1080), (100, 150, 200, 255))
        draw = ImageDraw.Draw(img)

        gen._draw_week_calendar(draw, [], 50, image=img)
        # エラーなく描画完了すればOK

    def test_header_bg_changes_pixels(self):
        """曜日ヘッダー領域のピクセルが半透明背景により変化すること"""
        gen = self._create_generator()

        # 色付き背景で比較
        img1 = Image.new('RGBA', (1920, 1080), (100, 150, 200, 255))
        draw1 = ImageDraw.Draw(img1)
        gen._draw_week_calendar(draw1, [], 50, image=img1)

        # 曜日ヘッダー領域のピクセルは背景色から変化しているはず
        total_width = 120 * 7  # DAY_COLUMN_WIDTH * 7
        start_x = (1920 - total_width) // 2
        # ヘッダー領域中央のピクセル
        pixel = img1.getpixel((start_x + 60, 60))
        # 完全に元の背景色ではない
        assert pixel != (100, 150, 200, 255), \
            "曜日ヘッダー領域に半透明背景が適用されるべき"


class TestColumnHeaderBackground:
    """上段カード列ヘッダー半透明背景テスト"""

    def _create_generator(self, theme='simple'):
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', theme):
            return ImageGenerator()

    def test_draw_event_cards_with_header_bg(self):
        """列ヘッダー背景付きでイベントカードが描画されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (1920, 1080), (100, 150, 200, 255))
        draw = ImageDraw.Draw(img)

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        events = [
            _make_event('会議', today.replace(hour=10), today.replace(hour=11)),
        ]

        gen._draw_event_cards(draw, events, 50, week_events=events, image=img)
        # エラーなく描画完了すればOK


class TestVisibilityIntegration:
    """視認性改善の統合テスト"""

    def test_wallpaper_all_themes_with_header_bg(self):
        """全テーマで半透明背景付き壁紙が生成されること"""
        from src.image_generator import ImageGenerator
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        events = [
            _make_event('会議', today.replace(hour=10), today.replace(hour=11)),
        ]

        for theme in ['simple', 'modern', 'pastel', 'dark', 'vibrant']:
            with patch('src.image_generator.THEME', theme):
                gen = ImageGenerator()
                output = gen.generate_wallpaper(events, events)
                assert output is not None, f"{theme}テーマで壁紙生成に失敗"
