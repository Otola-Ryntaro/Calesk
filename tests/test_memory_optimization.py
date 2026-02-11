"""
チケット024: メモリ消費削減テスト
Phase 1: フォント遅延ロード、リソース解放、背景画像キャッシュ
Phase 2: 中間Image即時解放、アイコンキャッシュ、gc.collect()
"""
import gc
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
from PIL import Image


class TestResourceRelease:
    """リソース解放テスト"""

    def test_release_resources_method_exists(self):
        """release_resources()メソッドが存在すること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            assert hasattr(gen, 'release_resources')

    def test_release_resources_clears_fonts(self):
        """release_resources()でフォントキャッシュがクリアされること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            gen.release_resources()
            # フォントキャッシュがクリアされていること
            assert gen._font_cache == {}

    def test_fonts_reload_after_release(self):
        """リソース解放後に再生成できること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            gen.release_resources()
            # 再生成
            output = gen.generate_wallpaper([], [])
            assert output is not None
            assert output.exists()


class TestFontLazyLoading:
    """フォント遅延ロードテスト"""

    def test_font_cache_exists(self):
        """フォントキャッシュ辞書が存在すること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            assert hasattr(gen, '_font_cache')

    def test_font_property_returns_font(self):
        """フォントプロパティがフォントオブジェクトを返すこと"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            font = gen.font_card_date
            assert font is not None

    def test_font_cached_after_first_access(self):
        """初回アクセス後にキャッシュされること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            font1 = gen.font_card_date
            font2 = gen.font_card_date
            assert font1 is font2


class TestBackgroundImageCache:
    """背景画像キャッシュテスト"""

    def test_cached_background_exists(self):
        """背景画像キャッシュ属性が存在すること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            assert hasattr(gen, '_cached_background')

    def test_release_clears_background_cache(self):
        """release_resources()で背景キャッシュもクリアされること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            gen._cached_background = Image.new('RGBA', (100, 100))
            gen._cached_background_path = '/test'
            gen.release_resources()
            assert gen._cached_background is None
            assert gen._cached_background_path is None


class TestGenerateWallpaperMemory:
    """壁紙生成時のメモリ最適化テスト"""

    def test_generate_wallpaper_still_works(self):
        """最適化後も壁紙生成が正常に動作すること"""
        from src.image_generator import ImageGenerator
        for theme in ['simple', 'modern', 'pastel', 'dark', 'vibrant']:
            with patch('src.image_generator.THEME', theme):
                gen = ImageGenerator()
                output = gen.generate_wallpaper([], [])
                assert output is not None, f"{theme}テーマで壁紙生成に失敗"
                assert output.exists()

    def test_release_after_generate(self):
        """生成→リリース→再生成が正常動作すること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            # 1回目の生成
            output1 = gen.generate_wallpaper([], [])
            assert output1 is not None
            # リソース解放
            gen.release_resources()
            # 2回目の生成
            output2 = gen.generate_wallpaper([], [])
            assert output2 is not None


# ============================================================
# Phase 2: 中間Image即時解放、アイコンキャッシュ、gc.collect()
# ============================================================

class TestGcCollectOnRelease:
    """gc.collect()がrelease_resources()で呼ばれること"""

    def test_gc_collect_called(self):
        """release_resources()でgc.collect()が呼ばれること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            with patch('src.image_generator.gc.collect') as mock_gc:
                gen.release_resources()
                mock_gc.assert_called_once()


class TestIconCache:
    """アイコンキャッシュテスト"""

    def test_icon_cache_attribute_exists(self):
        """_cached_icon属性が存在すること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            assert hasattr(gen, '_cached_icon')
            assert gen._cached_icon is None

    def test_icon_cache_cleared_on_release(self):
        """release_resources()でアイコンキャッシュが解放されること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'simple'):
            gen = ImageGenerator()
            gen._cached_icon = Image.new('RGBA', (40, 40))
            gen.release_resources()
            assert gen._cached_icon is None


class TestPhase2GenerateWallpaper:
    """Phase 2最適化後の壁紙生成テスト"""

    def test_all_themes_still_work(self):
        """Phase 2最適化後も全テーマで壁紙生成が正常動作すること"""
        from src.image_generator import ImageGenerator
        for theme in ['simple', 'modern', 'pastel', 'dark', 'vibrant', 'luxury', 'playful']:
            with patch('src.image_generator.THEME', theme):
                gen = ImageGenerator()
                output = gen.generate_wallpaper([], [])
                assert output is not None, f"{theme}テーマで壁紙生成に失敗"
                assert output.exists()

    def test_multiple_generate_cycles(self):
        """生成→解放を3回繰り返しても正常動作すること"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', 'modern'):
            gen = ImageGenerator()
            for i in range(3):
                output = gen.generate_wallpaper([], [])
                assert output is not None, f"{i+1}回目の壁紙生成に失敗"
                gen.release_resources()
