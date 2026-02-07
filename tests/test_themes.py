"""
テーマシステムのテスト

TDD RED phase: テーマ機能の期待動作を定義
"""
import pytest
from pathlib import Path
from PIL import Image, ImageDraw

from src.config import IMAGE_WIDTH, IMAGE_HEIGHT


class TestThemeDefinitions:
    """テーマ定義のテスト"""

    def test_themes_file_exists(self):
        """src/themes.py が存在すること"""
        themes_file = Path(__file__).parent.parent / 'src' / 'themes.py'
        assert themes_file.exists(), "src/themes.py が存在しません"

    def test_themes_has_all_required_themes(self):
        """THEMES辞書にsimple, modern, pastel, dark, vibrantが定義されていること"""
        from src.themes import THEMES

        assert 'simple' in THEMES, "simpleテーマが定義されていません"
        assert 'modern' in THEMES, "modernテーマが定義されていません"
        assert 'pastel' in THEMES, "pastelテーマが定義されていません"
        assert 'dark' in THEMES, "darkテーマが定義されていません"
        assert 'vibrant' in THEMES, "vibrantテーマが定義されていません"

    def test_simple_theme_structure(self):
        """simpleテーマが正しい構造を持つこと"""
        from src.themes import THEMES

        simple = THEMES['simple']
        # 背景画像を使用（background_color, background_gradientなし）
        assert 'background_color' not in simple or simple.get('background_color') is None
        assert 'background_gradient' not in simple or simple.get('background_gradient') is None
        # 必須キー
        assert 'text_color' in simple
        assert 'card_bg' in simple
        assert 'card_alpha' in simple
        assert 'card_border' in simple
        assert 'card_radius' in simple
        assert 'card_shadow' in simple
        # 値のチェック
        assert simple['text_color'] == (0, 0, 0), "黒文字"
        assert simple['card_alpha'] == 255, "不透明"
        assert simple['card_radius'] == 0, "角丸なし"
        assert simple['card_shadow'] is False, "影なし"

    def test_modern_theme_structure(self):
        """modernテーマが正しい構造を持つこと"""
        from src.themes import THEMES

        modern = THEMES['modern']
        # 背景画像を使用
        assert 'background_color' not in modern or modern.get('background_color') is None
        assert 'background_gradient' not in modern or modern.get('background_gradient') is None
        # 必須キー
        assert 'card_alpha' in modern, "半透明設定が必要"
        assert 'card_radius' in modern, "角丸設定が必要"
        assert 'card_shadow' in modern, "影設定が必要"
        # 値のチェック
        assert modern['card_alpha'] < 255, "半透明（85%）"
        assert modern['card_radius'] > 0, "角丸あり"
        assert modern['card_shadow'] is True, "影あり"

    def test_pastel_theme_structure(self):
        """pastelテーマが正しい構造を持つこと"""
        from src.themes import THEMES

        pastel = THEMES['pastel']
        # 背景画像を使用
        assert 'background_color' not in pastel or pastel.get('background_color') is None
        # パステルカラーの背景
        assert pastel['card_bg'] == (255, 240, 245), "淡いピンク背景"
        assert pastel['card_alpha'] < 255, "半透明"
        assert pastel['card_radius'] > 0, "角丸あり"
        # パステルイベントカラー
        assert 'event_colors' in pastel, "パステルイベントカラーが必要"

    def test_dark_theme_structure(self):
        """darkテーマが正しい構造を持つこと"""
        from src.themes import THEMES

        dark = THEMES['dark']
        # ダークモードの背景（濃いグレー）
        assert dark['card_bg'] == (45, 45, 45), "濃いグレー背景"
        assert dark['text_color'] == (224, 224, 224), "白〜薄いグレー"
        assert 'accent_color' in dark, "アクセントカラーが必要"
        # ゴールドアクセント
        assert dark['accent_color'] == (255, 215, 0), "ゴールドアクセント"

    def test_vibrant_theme_structure(self):
        """vibrantテーマが正しい構造を持つこと"""
        from src.themes import THEMES

        vibrant = THEMES['vibrant']
        # 鮮やかな色
        assert vibrant['text_color'] == (255, 255, 255), "白文字"
        assert vibrant['card_bg'] == (25, 25, 50), "ダークネイビー（イベント色が映える）"
        assert vibrant['card_shadow'] is True, "影あり"


class TestThemeApplication:
    """テーマ適用のテスト"""

    def test_image_generator_has_theme_support(self):
        """ImageGeneratorがテーマをサポートすること"""
        from src.image_generator import ImageGenerator

        generator = ImageGenerator()
        assert hasattr(generator, 'theme'), "themeプロパティが必要"
        from collections.abc import Mapping
        assert isinstance(generator.theme, Mapping), "themeはMapping型"

    def test_can_switch_themes(self):
        """テーマを切り替えられること"""
        from src.image_generator import ImageGenerator
        from src.themes import THEMES

        generator = ImageGenerator()

        # デフォルトはsimpleテーマ（ChainMapでラップされているのでキー比較）
        for key, value in THEMES['simple'].items():
            assert generator.theme[key] == value

        # テーマ切り替え機能があること
        assert hasattr(generator, 'set_theme'), "set_themeメソッドが必要"

    def test_rounded_card_drawing(self):
        """角丸カードを描画できること"""
        from src.image_generator import ImageGenerator

        generator = ImageGenerator()

        # 角丸矩形描画メソッドがあること
        assert hasattr(generator, '_draw_rounded_rectangle'), \
            "_draw_rounded_rectangleメソッドが必要"

        # テスト用画像で描画確認（RGBAモード）
        test_img = Image.new('RGBA', (200, 100), (255, 255, 255, 255))
        draw = ImageDraw.Draw(test_img)

        # 角丸矩形を描画（エラーが出ないこと）
        generator._draw_rounded_rectangle(
            draw,
            [(10, 10), (190, 90)],
            radius=15,
            fill=(255, 255, 255, 200),  # RGBA
            outline=(200, 200, 200)
        )

    def test_card_shadow_drawing(self):
        """カードの影を描画できること"""
        from src.image_generator import ImageGenerator

        generator = ImageGenerator()

        # 影描画メソッドがあること
        assert hasattr(generator, '_draw_card_shadow'), \
            "_draw_card_shadowメソッドが必要"

        # テスト用画像で描画確認（RGBAモード）
        test_img = Image.new('RGBA', (200, 100), (255, 255, 255, 255))
        draw = ImageDraw.Draw(test_img)

        # 影を描画（エラーが出ないこと）
        generator._draw_card_shadow(draw, 10, 10, 180, 80, radius=15)

    def test_dark_mode_colors(self):
        """ダークモードの色設定が適用されること（Dark用）"""
        from src.image_generator import ImageGenerator
        from src.themes import THEMES
        from unittest.mock import patch

        # darkテーマで初期化
        with patch('src.image_generator.THEME', 'dark'):
            generator = ImageGenerator()

            # ダークモード用の色が設定されていること（ChainMapでラップ）
            for key, value in THEMES['dark'].items():
                assert generator.theme[key] == value
            bg = generator.theme['card_bg']
            assert all(c < 50 for c in bg), "ダークトーン背景"


class TestThemeIntegration:
    """テーマの統合テスト"""

    def test_generate_wallpaper_with_simple_theme(self, tmp_path):
        """simpleテーマで壁紙を生成できること"""
        from src.image_generator import ImageGenerator
        from unittest.mock import patch

        with patch('src.image_generator.THEME', 'simple'):
            generator = ImageGenerator()

            # 空のイベントリストで壁紙生成
            today_events = []
            week_events = []

            # 壁紙生成（エラーが出ないこと）
            output_path = generator.generate_wallpaper(today_events, week_events)

            # ファイルが生成されていること
            assert output_path is not None
            assert output_path.exists()

            # 画像として読み込めること
            img = Image.open(output_path)
            assert img.size[0] > 0 and img.size[1] > 0

    def test_generate_wallpaper_with_modern_theme(self, tmp_path):
        """modernテーマで壁紙を生成できること"""
        from src.image_generator import ImageGenerator
        from unittest.mock import patch

        with patch('src.image_generator.THEME', 'modern'):
            generator = ImageGenerator()

            # 空のイベントリストで壁紙生成
            today_events = []
            week_events = []

            output_path = generator.generate_wallpaper(today_events, week_events)

            assert output_path is not None
            assert output_path.exists()
            img = Image.open(output_path)
            assert img.size[0] > 0 and img.size[1] > 0

    def test_generate_wallpaper_with_pastel_theme(self, tmp_path):
        """pastelテーマで壁紙を生成できること"""
        from src.image_generator import ImageGenerator
        from unittest.mock import patch

        with patch('src.image_generator.THEME', 'pastel'):
            generator = ImageGenerator()

            # 空のイベントリストで壁紙生成
            today_events = []
            week_events = []

            output_path = generator.generate_wallpaper(today_events, week_events)

            assert output_path is not None
            assert output_path.exists()
            img = Image.open(output_path)
            assert img.size[0] > 0 and img.size[1] > 0

    def test_generate_wallpaper_with_dark_theme(self, tmp_path):
        """darkテーマで壁紙を生成できること"""
        from src.image_generator import ImageGenerator
        from unittest.mock import patch

        with patch('src.image_generator.THEME', 'dark'):
            generator = ImageGenerator()

            # 空のイベントリストで壁紙生成
            today_events = []
            week_events = []

            output_path = generator.generate_wallpaper(today_events, week_events)

            assert output_path is not None
            assert output_path.exists()
            img = Image.open(output_path)
            assert img.size[0] > 0 and img.size[1] > 0

    def test_generate_wallpaper_with_vibrant_theme(self, tmp_path):
        """vibrantテーマで壁紙を生成できること"""
        from src.image_generator import ImageGenerator
        from unittest.mock import patch

        with patch('src.image_generator.THEME', 'vibrant'):
            generator = ImageGenerator()

            # 空のイベントリストで壁紙生成
            today_events = []
            week_events = []

            output_path = generator.generate_wallpaper(today_events, week_events)

            assert output_path is not None
            assert output_path.exists()
            img = Image.open(output_path)
            assert img.size[0] > 0 and img.size[1] > 0
