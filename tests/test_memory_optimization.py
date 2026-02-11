"""
チケット024: メモリ消費削減テスト
フォント遅延ロード、リソース解放、背景画像キャッシュ
"""
import pytest
from unittest.mock import patch, MagicMock
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
