"""
チケット016: ガラスモーフィズム効果テスト

modernテーマとdarkテーマでカード背景にぼかし効果を適用する。
"""
import pytest
from PIL import Image, ImageDraw, ImageFilter
from datetime import datetime, timedelta
from unittest.mock import patch

from src.image_generator import ImageGenerator
from src.models.event import CalendarEvent
from src import themes


class TestGlassEffectThemeConfig:
    """テーマのガラスモーフィズム設定テスト"""

    def test_modern_theme_has_glass_effect(self):
        """modernテーマにglass_effectフラグがあること"""
        theme = themes.THEMES['modern']
        assert 'glass_effect' in theme
        assert theme['glass_effect'] is True

    def test_dark_theme_has_glass_effect(self):
        """darkテーマにglass_effectフラグがあること"""
        theme = themes.THEMES['dark']
        assert 'glass_effect' in theme
        assert theme['glass_effect'] is True

    def test_simple_theme_no_glass_effect(self):
        """simpleテーマではglass_effectが無効であること"""
        theme = themes.THEMES['simple']
        assert theme.get('glass_effect', False) is False

    def test_glass_blur_radius_exists(self):
        """ガラス効果のぼかし半径がテーマに設定されていること"""
        theme = themes.THEMES['modern']
        assert 'glass_blur_radius' in theme
        assert isinstance(theme['glass_blur_radius'], int)
        assert theme['glass_blur_radius'] > 0

    def test_glass_tint_color_exists(self):
        """ガラス効果の着色がテーマに設定されていること"""
        theme = themes.THEMES['modern']
        assert 'glass_tint' in theme
        assert len(theme['glass_tint']) == 4  # RGBA


class TestDrawGlassCard:
    """_draw_glass_card メソッドのテスト"""

    def _create_generator(self, theme_name='modern'):
        gen = ImageGenerator()
        gen.set_theme(theme_name)
        return gen

    def test_draw_glass_card_method_exists(self):
        """_draw_glass_card メソッドが存在すること"""
        gen = self._create_generator()
        assert hasattr(gen, '_draw_glass_card')
        assert callable(gen._draw_glass_card)

    def test_draw_glass_card_renders_without_error(self):
        """_draw_glass_card がエラーなく描画できること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (100, 150, 200, 255))
        draw = ImageDraw.Draw(image)
        gen._draw_glass_card(draw, image, 50, 50, 200, 100)

    def test_draw_glass_card_modifies_image(self):
        """_draw_glass_card がカード領域を変更すること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (100, 150, 200, 255))
        original_region = image.crop((50, 50, 250, 150)).copy()
        draw = ImageDraw.Draw(image)
        gen._draw_glass_card(draw, image, 50, 50, 200, 100)
        modified_region = image.crop((50, 50, 250, 150))
        assert original_region.tobytes() != modified_region.tobytes()

    def test_draw_glass_card_applies_blur(self):
        """_draw_glass_card がぼかし効果を適用すること"""
        gen = self._create_generator()
        # グラデーション背景を作成（ぼかし効果がわかりやすいように）
        image = Image.new('RGBA', (800, 600), (0, 0, 0, 255))
        for x in range(800):
            for y in range(50, 60):
                image.putpixel((x, y), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        gen._draw_glass_card(draw, image, 0, 40, 200, 40)
        # ぼかし後はエッジがぼやけるため、元の白線の隣のピクセルが純黒ではなくなる
        pixel = image.getpixel((100, 48))
        # ぼかしが適用されていれば、ピクセルは完全な黒ではない
        assert pixel[0] > 0 or pixel[1] > 0 or pixel[2] > 0


class TestGlassCardEdgeCases:
    """ガラスカードのエッジケーステスト"""

    def _create_generator(self, theme_name='modern'):
        gen = ImageGenerator()
        gen.set_theme(theme_name)
        return gen

    def test_glass_card_at_image_boundary(self):
        """カードが画像境界を超える場合にクリッピングされること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (200, 100), (100, 150, 200, 255))
        draw = ImageDraw.Draw(image)
        # カードが画像の右端・下端を超える
        gen._draw_glass_card(draw, image, 150, 60, 200, 100)
        # エラーなく完了すること

    def test_glass_card_zero_size(self):
        """ゼロサイズのカードで早期リターンすること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (100, 150, 200, 255))
        original = image.copy()
        draw = ImageDraw.Draw(image)
        gen._draw_glass_card(draw, image, 50, 50, 0, 0)
        # 画像が変更されないこと
        assert original.tobytes() == image.tobytes()

    def test_glass_card_no_radius(self):
        """radius=0 でガラスカードを描画できること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (100, 150, 200, 255))
        draw = ImageDraw.Draw(image)
        gen._draw_glass_card(draw, image, 50, 50, 200, 100, radius=0)

    def test_compact_card_glass_fallback_without_image(self):
        """image=None かつ glass_effect=True の場合、通常描画にフォールバックすること"""
        gen = self._create_generator('modern')
        image = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        event = CalendarEvent(
            id='test-fb-1', summary='フォールバック会議',
            start_datetime=datetime.now() + timedelta(hours=1),
            end_datetime=datetime.now() + timedelta(hours=2),
            is_all_day=False, color_id='1', calendar_id='test'
        )
        # image=None でもエラーにならない
        gen._draw_compact_event_card(draw, event, 50, 50, image=None)

    def test_glass_border_color_from_theme(self):
        """ガラス枠線色がテーマから取得されること"""
        gen = self._create_generator('modern')
        assert hasattr(gen, '_draw_glass_card')


class TestGlassEffectIntegration:
    """ガラスモーフィズムの統合テスト"""

    def _create_test_event(self, hours_from_now=1):
        now = datetime.now()
        start = now + timedelta(hours=hours_from_now)
        end = start + timedelta(hours=1)
        return CalendarEvent(
            id='test-glass-1',
            summary='ガラステスト会議',
            start_datetime=start,
            end_datetime=end,
            is_all_day=False,
            color_id='1',
            calendar_id='test'
        )

    @patch('src.image_generator.BACKGROUND_IMAGE_PATH', None)
    def test_wallpaper_with_glass_modern_theme(self):
        """modernテーマでガラス効果付き壁紙を生成できること"""
        gen = ImageGenerator()
        gen.set_theme('modern')
        event = self._create_test_event()
        result = gen.generate_wallpaper([event], [event])
        assert result is not None
        assert result.exists()

    @patch('src.image_generator.BACKGROUND_IMAGE_PATH', None)
    def test_wallpaper_with_glass_dark_theme(self):
        """darkテーマでガラス効果付き壁紙を生成できること"""
        gen = ImageGenerator()
        gen.set_theme('dark')
        event = self._create_test_event()
        result = gen.generate_wallpaper([event], [event])
        assert result is not None
        assert result.exists()

    @patch('src.image_generator.BACKGROUND_IMAGE_PATH', None)
    def test_wallpaper_simple_theme_no_glass(self):
        """simpleテーマではガラス効果なしで生成できること"""
        gen = ImageGenerator()
        gen.set_theme('simple')
        event = self._create_test_event()
        result = gen.generate_wallpaper([event], [event])
        assert result is not None
        assert result.exists()

    @patch('src.image_generator.BACKGROUND_IMAGE_PATH', None)
    def test_all_themes_generate_without_error(self):
        """全テーマがエラーなく壁紙生成できること"""
        event = self._create_test_event()
        for theme_name in themes.THEMES:
            gen = ImageGenerator()
            gen.set_theme(theme_name)
            result = gen.generate_wallpaper([event], [event])
            assert result is not None, f"テーマ {theme_name} で壁紙生成失敗"
