"""
チケット013: 進行中イベントの強調強化テスト

TDD RED phase: 進行中イベント強調機能の期待動作を定義
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from PIL import Image, ImageDraw

from src.models.event import CalendarEvent


def _make_event(summary, start_dt, end_dt, color_id='1'):
    """テスト用CalendarEventを作成"""
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


class TestActiveThemeProperties:
    """themes.py の進行中スタイル設定テスト"""

    def test_all_themes_have_active_card_bg(self):
        """全テーマに active_card_bg が定義されていること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            assert 'active_card_bg' in theme, \
                f"{name}テーマに active_card_bg がありません"

    def test_all_themes_have_active_card_border(self):
        """全テーマに active_card_border が定義されていること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            assert 'active_card_border' in theme, \
                f"{name}テーマに active_card_border がありません"

    def test_all_themes_have_active_text_color(self):
        """全テーマに active_text_color が定義されていること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            assert 'active_text_color' in theme, \
                f"{name}テーマに active_text_color がありません"

    def test_simple_theme_active_colors_are_red_toned(self):
        """simpleテーマの進行中カラーが赤系であること"""
        from src.themes import THEMES
        simple = THEMES['simple']
        r, g, b = simple['active_card_border'][:3]
        assert r > g and r > b, "進行中枠色は赤系であるべき"

    def test_dark_theme_active_colors_bright(self):
        """darkテーマの進行中カラーが明るい赤系であること"""
        from src.themes import THEMES
        dark = THEMES['dark']
        r, g, b = dark['active_card_border'][:3]
        assert r > 150, "darkテーマの進行中枠色は明るい赤であるべき"


class TestInProgressEmphasis:
    """進行中イベントの強調描画テスト"""

    def _create_generator(self, theme='simple'):
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', theme):
            return ImageGenerator()

    def _make_in_progress_event(self):
        """現在進行中のイベントを作成"""
        now = datetime.now()
        return _make_event(
            '進行中会議',
            now - timedelta(minutes=30),
            now + timedelta(minutes=30)
        )

    def _make_future_event(self):
        """未来のイベントを作成"""
        now = datetime.now()
        return _make_event(
            '未来の会議',
            now + timedelta(hours=2),
            now + timedelta(hours=3)
        )

    def test_compact_card_in_progress_has_different_border(self):
        """進行中のコンパクトカードが通常と異なる枠色で描画されること"""
        gen = self._create_generator()
        event = self._make_in_progress_event()

        # 進行中カードの描画
        img1 = Image.new('RGBA', (400, 100), (255, 255, 255, 255))
        draw1 = ImageDraw.Draw(img1)
        gen._draw_compact_event_card(draw1, event, 10, 10, is_finished=False, is_in_progress=True)

        # 通常カードの描画
        img2 = Image.new('RGBA', (400, 100), (255, 255, 255, 255))
        draw2 = ImageDraw.Draw(img2)
        gen._draw_compact_event_card(draw2, event, 10, 10, is_finished=False, is_in_progress=False)

        # 描画結果が異なること（枠色・背景が変わっている）
        assert img1.tobytes() != img2.tobytes(), \
            "進行中カードと通常カードの見た目が異なるべき"

    def test_single_card_in_progress_has_different_border(self):
        """進行中のフルカードが通常と異なる枠色で描画されること"""
        gen = self._create_generator()
        event = self._make_in_progress_event()

        img1 = Image.new('RGBA', (400, 300), (255, 255, 255, 255))
        draw1 = ImageDraw.Draw(img1)
        gen._draw_single_event_card(draw1, event, 10, 10, is_finished=False, is_in_progress=True)

        img2 = Image.new('RGBA', (400, 300), (255, 255, 255, 255))
        draw2 = ImageDraw.Draw(img2)
        gen._draw_single_event_card(draw2, event, 10, 10, is_finished=False, is_in_progress=False)

        assert img1.tobytes() != img2.tobytes(), \
            "進行中カードと通常カードの見た目が異なるべき"


class TestInProgressIntegration:
    """進行中イベント強調の統合テスト"""

    def test_wallpaper_with_in_progress_event(self):
        """進行中イベントがある状態で壁紙生成が成功すること"""
        from src.image_generator import ImageGenerator
        now = datetime.now()

        events = [
            _make_event('進行中', now - timedelta(minutes=30), now + timedelta(minutes=30)),
            _make_event('今後', now + timedelta(hours=2), now + timedelta(hours=3)),
        ]

        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            output = gen.generate_wallpaper(events, events)
            assert output is not None
            assert output.exists()

    def test_wallpaper_all_themes_with_in_progress(self):
        """全テーマで進行中イベントの壁紙生成が成功すること"""
        from src.image_generator import ImageGenerator
        now = datetime.now()

        events = [
            _make_event('進行中', now - timedelta(minutes=30), now + timedelta(minutes=30)),
        ]

        for theme in ['simple', 'modern', 'pastel', 'dark', 'vibrant']:
            with patch('src.image_generator.THEME', theme):
                gen = ImageGenerator()
                output = gen.generate_wallpaper(events, events)
                assert output is not None, f"{theme}テーマで壁紙生成に失敗"
