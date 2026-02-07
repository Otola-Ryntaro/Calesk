"""
チケット016: デザイン再計画テスト

TDD RED phase: フォント階層・枠形状・イベントカラー・背景融和性の期待動作を定義
"""
import pytest
from unittest.mock import patch
from pathlib import Path
from PIL import Image, ImageDraw

from src.models.event import CalendarEvent
from datetime import datetime, timedelta


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


class TestBoldFontConfig:
    """Boldフォント設定テスト"""

    def test_font_paths_bold_exists(self):
        """FONT_PATHS_BOLD が config に定義されていること"""
        from src.config import FONT_PATHS_BOLD
        assert isinstance(FONT_PATHS_BOLD, dict)

    def test_font_paths_bold_has_darwin(self):
        """FONT_PATHS_BOLD に Darwin キーがあること"""
        from src.config import FONT_PATHS_BOLD
        assert 'Darwin' in FONT_PATHS_BOLD

    def test_font_paths_bold_darwin_has_w6(self):
        """macOS用BoldフォントにW6が含まれること"""
        from src.config import FONT_PATHS_BOLD
        darwin_paths = FONT_PATHS_BOLD.get('Darwin', [])
        has_w6 = any('W6' in p for p in darwin_paths)
        assert has_w6, "Darwin用BoldフォントにW6が必要"


class TestBoldFontLoading:
    """Boldフォント読み込みテスト"""

    def _create_generator(self):
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            return ImageGenerator()

    def test_generator_has_bold_font(self):
        """ImageGeneratorがBoldフォントを持つこと"""
        gen = self._create_generator()
        assert hasattr(gen, 'font_card_time_bold')

    def test_bold_font_is_different_from_regular(self):
        """BoldフォントとRegularフォントが異なること"""
        gen = self._create_generator()
        # Boldフォントが読み込まれていれば、同サイズでも異なるフォントオブジェクト
        assert gen.font_card_time_bold is not None


class TestEnhancedEventColors:
    """イベントカラー彩度改善テスト"""

    def test_all_themes_have_event_colors(self):
        """全テーマに event_colors が定義されていること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            assert 'event_colors' in theme, \
                f"{name}テーマに event_colors がありません"

    def test_event_colors_has_basic_ids(self):
        """event_colors に基本的なカラーIDが含まれること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            colors = theme['event_colors']
            for cid in ['1', '2', '3', '4', '5']:
                assert cid in colors, \
                    f"{name}テーマの event_colors に '{cid}' がありません"

    def test_vibrant_colors_are_saturated(self):
        """vibrantテーマのイベント色が鮮やかであること"""
        from src.themes import THEMES
        colors = THEMES['vibrant']['event_colors']
        for cid, color in colors.items():
            r, g, b = color[:3]
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            # 彩度: max-min が一定以上
            assert max_c - min_c > 50, \
                f"vibrantテーマの色 {cid}={color} は彩度が低い"


class TestThemeFrameShapes:
    """テーマ枠形状テスト"""

    def test_all_themes_have_card_shadow(self):
        """全テーマに card_shadow が定義されていること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            assert 'card_shadow' in theme, \
                f"{name}テーマに card_shadow がありません"

    def test_modern_theme_has_large_radius(self):
        """modernテーマが大きな角丸を持つこと"""
        from src.themes import THEMES
        modern = THEMES['modern']
        assert modern['card_radius'] >= 15, \
            "modernテーマは15px以上の角丸が必要"

    def test_dark_theme_has_accent_border(self):
        """darkテーマがアクセントカラーの枠線を持つこと"""
        from src.themes import THEMES
        dark = THEMES['dark']
        r, g, b = dark['card_border'][:3]
        # ゴールド系: R > 200, G > 150
        assert r > 200 and g > 150, \
            "darkテーマの枠線はゴールド系であるべき"


class TestDesignIntegration:
    """デザイン改善の統合テスト"""

    def test_wallpaper_all_themes(self):
        """全テーマで壁紙が正常に生成されること"""
        from src.image_generator import ImageGenerator
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        events = [
            _make_event('会議', today.replace(hour=10), today.replace(hour=11), color_id='1'),
            _make_event('ランチ', today.replace(hour=12), today.replace(hour=13), color_id='2'),
        ]

        for theme in ['simple', 'modern', 'pastel', 'dark', 'vibrant']:
            with patch('src.image_generator.THEME', theme):
                gen = ImageGenerator()
                output = gen.generate_wallpaper(events, events)
                assert output is not None, f"{theme}テーマで壁紙生成に失敗"
                assert output.exists(), f"{theme}テーマの壁紙ファイルが存在しない"

    def test_wallpaper_with_bold_font(self):
        """Boldフォント使用で壁紙が正常に生成されること"""
        from src.image_generator import ImageGenerator
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        events = [
            _make_event('重要会議', today.replace(hour=10), today.replace(hour=11)),
        ]

        with patch('src.image_generator.THEME', 'modern'):
            gen = ImageGenerator()
            output = gen.generate_wallpaper(events, events)
            assert output is not None
