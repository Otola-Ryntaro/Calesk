"""
チケット011: Weekly Calendar 時刻ラベルの視認性改善テスト

TDD RED phase: ラベル視認性改善機能の期待動作を定義
"""
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw, ImageFont


class TestLabelVisibilityConfig:
    """config.py の LABEL_VISIBILITY_MODE 設定テスト"""

    def test_label_visibility_mode_exists(self):
        """LABEL_VISIBILITY_MODE が config.py に定義されていること"""
        from src.config import LABEL_VISIBILITY_MODE
        assert LABEL_VISIBILITY_MODE is not None

    def test_label_visibility_mode_default_value(self):
        """デフォルト値が 'label_bg' であること"""
        from src.config import LABEL_VISIBILITY_MODE
        assert LABEL_VISIBILITY_MODE == 'label_bg'

    def test_label_visibility_mode_valid_values(self):
        """有効な値が定義されていること"""
        from src.config import LABEL_VISIBILITY_MODES
        expected = {'label_bg', 'full_bg', 'outline', 'none'}
        assert set(LABEL_VISIBILITY_MODES) == expected


class TestThemeHourLabelColors:
    """themes.py の時刻ラベル色設定テスト"""

    def test_all_themes_have_hour_label_color(self):
        """全テーマに hour_label_color が定義されていること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            assert 'hour_label_color' in theme, \
                f"{name}テーマに hour_label_color がありません"

    def test_all_themes_have_hour_label_bg(self):
        """全テーマに hour_label_bg が定義されていること"""
        from src.themes import THEMES
        for name, theme in THEMES.items():
            assert 'hour_label_bg' in theme, \
                f"{name}テーマに hour_label_bg がありません"

    def test_simple_theme_label_colors(self):
        """simpleテーマのラベル色が適切であること"""
        from src.themes import THEMES
        simple = THEMES['simple']
        # 黒文字テーマ → ラベルも黒系
        assert len(simple['hour_label_color']) >= 3
        # 半透明白背景
        assert len(simple['hour_label_bg']) == 4  # RGBA

    def test_dark_theme_label_colors(self):
        """darkテーマのラベル色が適切であること（明るい色）"""
        from src.themes import THEMES
        dark = THEMES['dark']
        r, g, b = dark['hour_label_color'][:3]
        # ダークテーマは明るいラベル色
        assert r > 150 or g > 150 or b > 150, \
            "darkテーマのラベル色は明るい色であるべき"

    def test_vibrant_theme_label_colors(self):
        """vibrantテーマのラベル色が適切であること（白系）"""
        from src.themes import THEMES
        vibrant = THEMES['vibrant']
        r, g, b = vibrant['hour_label_color'][:3]
        assert r > 200 and g > 200 and b > 200, \
            "vibrantテーマのラベル色は白系であるべき"


class TestLabelVisibilityDrawing:
    """描画ロジックのテスト"""

    def _create_generator(self, theme='simple'):
        """テスト用ImageGeneratorを作成"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', theme):
            gen = ImageGenerator()
        return gen

    def test_draw_hour_label_method_exists(self):
        """_draw_hour_label メソッドが存在すること"""
        gen = self._create_generator()
        assert hasattr(gen, '_draw_hour_label'), \
            "_draw_hour_label メソッドが必要"

    def test_draw_hour_label_with_label_bg_mode(self):
        """label_bg モード: ラベル背後に半透明矩形が描画されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (200, 50), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)

        # label_bg モードで描画（エラーなく完了すること）
        gen._draw_hour_label(draw, img, 10, 10, "08:00", mode='label_bg')

        # 描画後、ラベル位置付近のピクセルが変化していること
        pixel = img.getpixel((15, 15))
        assert pixel != (0, 0, 0, 255), "ラベル描画で画像が変更されるべき"

    def test_draw_hour_label_with_outline_mode(self):
        """outline モード: アウトライン付きテキストが描画されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (200, 50), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)

        # outline モードで描画（エラーなく完了すること）
        gen._draw_hour_label(draw, img, 10, 10, "08:00", mode='outline')

        # 描画後、ラベル位置付近のピクセルが変化していること
        pixel = img.getpixel((15, 15))
        assert pixel != (0, 0, 0, 255), "アウトライン描画で画像が変更されるべき"

    def test_draw_hour_label_with_none_mode(self):
        """none モード: プレーンテキストが描画されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (200, 50), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)

        # none モードで描画（エラーなく完了すること）
        gen._draw_hour_label(draw, img, 10, 10, "08:00", mode='none')

    def test_draw_calendar_full_bg_mode(self):
        """full_bg モード: カレンダー全体に半透明背景が追加されること"""
        gen = self._create_generator()
        img = Image.new('RGBA', (1920, 1080), (50, 50, 50, 255))
        draw = ImageDraw.Draw(img)

        # full_bg モードで週間カレンダーの背景描画
        assert hasattr(gen, '_draw_calendar_background'), \
            "_draw_calendar_background メソッドが必要"

        # エラーなく完了すること
        gen._draw_calendar_background(
            img, draw,
            start_x=100, y_start=200,
            total_width=840, total_height=400,
            mode='full_bg'
        )


class TestLabelVisibilityIntegration:
    """統合テスト: 各モードで壁紙生成が正常に動作すること"""

    def _generate_wallpaper(self, theme='simple', mode='label_bg'):
        """指定テーマ・モードで壁紙を生成"""
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', theme), \
             patch('src.image_generator.LABEL_VISIBILITY_MODE', mode):
            gen = ImageGenerator()
            return gen.generate_wallpaper([], [])

    def test_wallpaper_with_label_bg_mode(self):
        """label_bg モードで壁紙生成が成功すること"""
        output = self._generate_wallpaper(mode='label_bg')
        assert output is not None
        assert output.exists()
        img = Image.open(output)
        assert img.size[0] > 0

    def test_wallpaper_with_full_bg_mode(self):
        """full_bg モードで壁紙生成が成功すること"""
        output = self._generate_wallpaper(mode='full_bg')
        assert output is not None
        assert output.exists()

    def test_wallpaper_with_outline_mode(self):
        """outline モードで壁紙生成が成功すること"""
        output = self._generate_wallpaper(mode='outline')
        assert output is not None
        assert output.exists()

    def test_wallpaper_with_none_mode(self):
        """none モードで壁紙生成が成功すること"""
        output = self._generate_wallpaper(mode='none')
        assert output is not None
        assert output.exists()

    def test_wallpaper_all_themes_all_modes(self):
        """全テーマ × 全モードで壁紙生成が成功すること"""
        from src.config import LABEL_VISIBILITY_MODES
        theme_names = ['simple', 'modern', 'pastel', 'dark', 'vibrant']

        for theme in theme_names:
            for mode in LABEL_VISIBILITY_MODES:
                output = self._generate_wallpaper(theme=theme, mode=mode)
                assert output is not None, \
                    f"{theme}/{mode} で壁紙生成に失敗"
                assert output.exists(), \
                    f"{theme}/{mode} で出力ファイルが存在しません"
