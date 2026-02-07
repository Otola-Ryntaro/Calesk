"""
デザインエフェクトテスト

Phase 1: イベント進行状況バー、Chromatic Layersテキスト効果
"""
import pytest
from PIL import Image, ImageDraw
from datetime import datetime, timedelta
from unittest.mock import patch

from src.image_generator import ImageGenerator
from src.models.event import CalendarEvent
from src import themes


class TestProgressBar:
    """進行中イベントのプログレスバーテスト"""

    def _create_generator(self, theme_name='modern'):
        gen = ImageGenerator()
        gen.set_theme(theme_name)
        return gen

    def _create_event(self, hours_ago=1, duration_hours=2):
        """hours_ago前に開始し、duration_hours時間続くイベント"""
        now = datetime.now()
        start = now - timedelta(hours=hours_ago)
        end = start + timedelta(hours=duration_hours)
        return CalendarEvent(
            id='test-prog-1',
            summary='進行中テスト会議',
            start_datetime=start,
            end_datetime=end,
            is_all_day=False,
            color_id='1',
            calendar_id='test'
        )

    def test_draw_event_progress_bar_method_exists(self):
        """_draw_event_progress_bar メソッドが存在すること"""
        gen = self._create_generator()
        assert hasattr(gen, '_draw_event_progress_bar')
        assert callable(gen._draw_event_progress_bar)

    def test_progress_bar_renders_without_error(self):
        """進行中イベントでプログレスバーがエラーなく描画できること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        event = self._create_event(hours_ago=1, duration_hours=2)
        gen._draw_event_progress_bar(draw, event, 50, 100, 200)

    def test_progress_bar_modifies_image(self):
        """プログレスバーが画像を変更すること"""
        from src.config import CARD_HEIGHT, CARD_PADDING
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        y = 100
        # バー位置: y + CARD_HEIGHT - CARD_PADDING - bar_height(4) - 5
        bar_y = y + CARD_HEIGHT - CARD_PADDING - 4 - 5
        original_region = image.crop((50, bar_y - 1, 250, bar_y + 6)).copy()
        event = self._create_event(hours_ago=1, duration_hours=2)
        gen._draw_event_progress_bar(draw, event, 50, y, 200)
        modified_region = image.crop((50, bar_y - 1, 250, bar_y + 6))
        assert original_region.tobytes() != modified_region.tobytes()

    def test_progress_bar_not_rendered_for_future_event(self):
        """未来イベントではプログレスバーが描画されないこと"""
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        future_event = CalendarEvent(
            id='test-future-1',
            summary='未来の会議',
            start_datetime=datetime.now() + timedelta(hours=2),
            end_datetime=datetime.now() + timedelta(hours=3),
            is_all_day=False, color_id='1', calendar_id='test'
        )
        original = image.copy()
        gen._draw_event_progress_bar(draw, future_event, 50, 100, 200)
        # 未来イベントでは画像が変更されない
        assert original.tobytes() == image.tobytes()

    def test_progress_bar_not_rendered_for_finished_event(self):
        """終了済みイベントではプログレスバーが描画されないこと"""
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        past_event = CalendarEvent(
            id='test-past-1',
            summary='過去の会議',
            start_datetime=datetime.now() - timedelta(hours=3),
            end_datetime=datetime.now() - timedelta(hours=1),
            is_all_day=False, color_id='1', calendar_id='test'
        )
        original = image.copy()
        gen._draw_event_progress_bar(draw, past_event, 50, 100, 200)
        assert original.tobytes() == image.tobytes()

    def test_progress_ratio_is_proportional(self):
        """プログレスバーの長さが経過時間に比例すること"""
        from src.config import CARD_HEIGHT, CARD_PADDING
        gen = self._create_generator()
        # 2時間のイベント、1時間経過 → 約50%
        image = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        y = 100
        bar_y = y + CARD_HEIGHT - CARD_PADDING - 4 - 5
        event = self._create_event(hours_ago=1, duration_hours=2)
        gen._draw_event_progress_bar(draw, event, 50, y, 200)
        # 50%進行なので中間点(150)にバーがある
        mid_pixel = image.getpixel((150, bar_y + 2))
        assert mid_pixel != (255, 255, 255, 255)


class TestChromaticText:
    """Chromatic Layers テキスト効果テスト"""

    def _create_generator(self, theme_name='modern'):
        gen = ImageGenerator()
        gen.set_theme(theme_name)
        return gen

    def test_draw_chromatic_text_method_exists(self):
        """_draw_chromatic_text メソッドが存在すること"""
        gen = self._create_generator()
        assert hasattr(gen, '_draw_chromatic_text')
        assert callable(gen._draw_chromatic_text)

    def test_chromatic_text_renders_without_error(self):
        """Chromaticテキストがエラーなく描画できること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        gen._draw_chromatic_text(
            draw, '09:00', (100, 100),
            gen.font_card_time_bold, (51, 51, 51)
        )

    def test_chromatic_text_modifies_image(self):
        """Chromaticテキストが画像を変更すること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
        original = image.crop((95, 95, 200, 130)).copy()
        draw = ImageDraw.Draw(image)
        gen._draw_chromatic_text(
            draw, '09:00', (100, 100),
            gen.font_card_time_bold, (51, 51, 51)
        )
        modified = image.crop((95, 95, 200, 130))
        assert original.tobytes() != modified.tobytes()

    def test_chromatic_offset_from_theme(self):
        """テーマからchromatic_offsetを取得できること"""
        modern = themes.THEMES['modern']
        assert 'chromatic_offset' in modern
        assert isinstance(modern['chromatic_offset'], int)

    def test_vibrant_has_larger_chromatic_offset(self):
        """vibrantテーマは大きいオフセットを持つこと"""
        modern = themes.THEMES['modern']
        vibrant = themes.THEMES['vibrant']
        assert vibrant.get('chromatic_offset', 0) >= modern.get('chromatic_offset', 0)

    def test_simple_theme_no_chromatic(self):
        """simpleテーマではchromatic_offsetが0であること"""
        simple = themes.THEMES['simple']
        assert simple.get('chromatic_offset', 0) == 0


class TestDynamicLayout:
    """Dynamic Layout（動的レイアウト）テスト"""

    def _create_generator(self, theme_name='modern'):
        gen = ImageGenerator()
        gen.set_theme(theme_name)
        return gen

    def _create_events(self, count, hours_from_now=1):
        """指定件数のイベントを生成"""
        events = []
        for i in range(count):
            now = datetime.now()
            start = now + timedelta(hours=hours_from_now + i)
            end = start + timedelta(hours=1)
            events.append(CalendarEvent(
                id=f'test-dyn-{i}',
                summary=f'テスト会議{i+1}',
                start_datetime=start,
                end_datetime=end,
                is_all_day=False,
                color_id=str((i % 5) + 1),
                calendar_id='test'
            ))
        return events

    def test_select_layout_mode_method_exists(self):
        """_select_layout_mode メソッドが存在すること"""
        gen = self._create_generator()
        assert hasattr(gen, '_select_layout_mode')

    def test_layout_mode_zen_for_zero_events(self):
        """0件の場合、zenモードを返すこと"""
        gen = self._create_generator()
        assert gen._select_layout_mode(0) == 'zen'

    def test_layout_mode_hero_for_one_event(self):
        """1件の場合、heroモードを返すこと"""
        gen = self._create_generator()
        assert gen._select_layout_mode(1) == 'hero'

    def test_layout_mode_card_for_few_events(self):
        """2-3件の場合、cardモードを返すこと"""
        gen = self._create_generator()
        assert gen._select_layout_mode(2) == 'card'
        assert gen._select_layout_mode(3) == 'card'

    def test_layout_mode_compact_for_many_events(self):
        """4件以上の場合、compactモードを返すこと"""
        gen = self._create_generator()
        assert gen._select_layout_mode(4) == 'compact'
        assert gen._select_layout_mode(6) == 'compact'

    def test_draw_zen_mode_renders(self):
        """Zenモードがエラーなく描画できること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        gen._draw_zen_mode(draw, 100, image)

    def test_draw_zen_mode_modifies_image(self):
        """Zenモードが画像を変更すること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        original = image.tobytes()
        draw = ImageDraw.Draw(image)
        gen._draw_zen_mode(draw, 100, image)
        assert image.tobytes() != original

    def test_draw_hero_mode_renders(self):
        """Heroモードがエラーなく描画できること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        event = self._create_events(1)[0]
        gen._draw_hero_mode(draw, event, 100, image)

    def test_draw_hero_mode_modifies_image(self):
        """Heroモードが画像を変更すること"""
        gen = self._create_generator()
        image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))
        original = image.tobytes()
        draw = ImageDraw.Draw(image)
        event = self._create_events(1)[0]
        gen._draw_hero_mode(draw, event, 100, image)
        assert image.tobytes() != original

    @patch('src.image_generator.BACKGROUND_IMAGE_PATH', None)
    def test_wallpaper_zen_mode_with_no_events(self):
        """イベント0件でZenモード壁紙が生成できること"""
        gen = ImageGenerator()
        gen.set_theme('modern')
        result = gen.generate_wallpaper([], [])
        assert result is not None
        assert result.exists()

    @patch('src.image_generator.BACKGROUND_IMAGE_PATH', None)
    def test_wallpaper_hero_mode_with_one_event(self):
        """イベント1件でHeroモード壁紙が生成できること"""
        event = self._create_events(1)[0]
        gen = ImageGenerator()
        gen.set_theme('modern')
        result = gen.generate_wallpaper([event], [event])
        assert result is not None
        assert result.exists()


class TestDesignEffectsIntegration:
    """デザインエフェクトの統合テスト"""

    def _create_test_event(self, hours_from_now=1):
        now = datetime.now()
        start = now + timedelta(hours=hours_from_now)
        end = start + timedelta(hours=1)
        return CalendarEvent(
            id='test-design-1',
            summary='デザインテスト会議',
            start_datetime=start,
            end_datetime=end,
            is_all_day=False,
            color_id='1',
            calendar_id='test'
        )

    @patch('src.image_generator.BACKGROUND_IMAGE_PATH', None)
    def test_wallpaper_with_all_effects_modern(self):
        """modernテーマで全エフェクト付き壁紙を生成できること"""
        gen = ImageGenerator()
        gen.set_theme('modern')
        event = self._create_test_event()
        result = gen.generate_wallpaper([event], [event])
        assert result is not None
        assert result.exists()

    @patch('src.image_generator.BACKGROUND_IMAGE_PATH', None)
    def test_wallpaper_all_themes_with_effects(self):
        """全テーマでエフェクト付き壁紙を生成できること"""
        event = self._create_test_event()
        for theme_name in themes.THEMES:
            gen = ImageGenerator()
            gen.set_theme(theme_name)
            result = gen.generate_wallpaper([event], [event])
            assert result is not None, f"テーマ {theme_name} で壁紙生成失敗"
