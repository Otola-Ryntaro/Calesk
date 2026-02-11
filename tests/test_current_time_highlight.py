"""
チケット014: 現在時刻表示 - 蛍光色で時間帯塗りつぶし テスト

TDD RED phase: 現在時刻ハイライト機能の期待動作を定義
"""
import pytest
from unittest.mock import patch
from PIL import Image, ImageDraw


class TestCurrentTimeHighlightTheme:
    """テーマの current_time_highlight 設定テスト"""

    def test_all_themes_have_current_time_highlight(self):
        """全テーマに current_time_highlight が定義されていること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            assert 'current_time_highlight' in theme, \
                f"{name}テーマに current_time_highlight がありません"

    def test_highlight_color_has_alpha(self):
        """ハイライト色がRGBA（4要素）であること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            color = theme['current_time_highlight']
            assert len(color) == 4, \
                f"{name}テーマの current_time_highlight はRGBA（4要素）であるべき"

    def test_highlight_alpha_is_subtle(self):
        """ハイライトのアルファ値が控えめ（100以下）であること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            alpha = theme['current_time_highlight'][3]
            assert alpha <= 100, \
                f"{name}テーマのハイライトアルファ値 {alpha} は控えめであるべき（<=100）"


class TestCurrentTimeHighlightDrawing:
    """蛍光塗りつぶし描画テスト"""

    def _create_generator(self, theme='simple'):
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', theme):
            return ImageGenerator()

    def test_draw_current_time_arrow_accepts_image(self):
        """_draw_current_time_arrow が image パラメータを受け付けること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        # image パラメータ付きで呼び出し（エラーなし）
        gen._draw_current_time_arrow(
            draw, 100, 940, 300, 27,
            image=img
        )

    def test_draw_current_time_arrow_still_works_without_image(self):
        """image なしでも後方互換性があること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        # image パラメータなしで呼び出し（エラーなし）
        gen._draw_current_time_arrow(
            draw, 100, 940, 300, 27
        )


class TestCurrentTimeHighlightIntegration:
    """蛍光塗りつぶしの統合テスト"""

    def test_wallpaper_with_highlight(self):
        """蛍光ハイライト付きの壁紙が正常に生成されること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            output = gen.generate_wallpaper([], [])
            assert output is not None
            assert output.exists()

    def test_wallpaper_all_themes_with_highlight(self):
        """全テーマで蛍光ハイライト付き壁紙が生成されること"""
        from src.image_generator import ImageGenerator
        for theme in ['simple', 'modern', 'pastel', 'dark', 'vibrant']:
            with patch('src.image_generator.THEME', theme):
                gen = ImageGenerator()
                output = gen.generate_wallpaper([], [])
                assert output is not None, f"{theme}テーマで壁紙生成に失敗"
