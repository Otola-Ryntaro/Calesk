"""
グラデーション背景システムのテスト
Phase 1: 基盤改善の一環
"""
import pytest
from PIL import Image
from src.image_generator import ImageGenerator


class TestGradientBackground:
    """グラデーション背景生成のテスト"""

    def test_linear_gradient_vertical(self):
        """垂直方向の線形グラデーション生成"""
        gen = ImageGenerator()
        width, height = 200, 100
        colors = [(255, 0, 0), (0, 0, 255)]  # 赤→青

        image = gen._create_gradient_background(
            width=width,
            height=height,
            gradient_type='linear',
            colors=colors,
            direction='vertical'
        )

        # サイズ確認
        assert image.size == (width, height)

        # 上端（赤に近い）
        top_pixel = image.getpixel((width // 2, 0))
        assert top_pixel[0] > 200  # 赤成分が強い
        assert top_pixel[2] < 100  # 青成分が弱い

        # 下端（青に近い）
        bottom_pixel = image.getpixel((width // 2, height - 1))
        assert bottom_pixel[0] < 100  # 赤成分が弱い
        assert bottom_pixel[2] > 200  # 青成分が強い

    def test_linear_gradient_horizontal(self):
        """水平方向の線形グラデーション生成"""
        gen = ImageGenerator()
        width, height = 200, 100
        colors = [(0, 255, 0), (255, 255, 0)]  # 緑→黄

        image = gen._create_gradient_background(
            width=width,
            height=height,
            gradient_type='linear',
            colors=colors,
            direction='horizontal'
        )

        # 左端（緑に近い）
        left_pixel = image.getpixel((0, height // 2))
        assert left_pixel[1] > 200  # 緑成分が強い
        assert left_pixel[0] < 100  # 赤成分が弱い（黄色ではない）

        # 右端（黄色に近い）
        right_pixel = image.getpixel((width - 1, height // 2))
        assert right_pixel[0] > 200  # 赤成分が強い（黄色）
        assert right_pixel[1] > 200  # 緑成分も強い（黄色）

    def test_linear_gradient_diagonal(self):
        """斜め方向の線形グラデーション生成"""
        gen = ImageGenerator()
        width, height = 200, 200
        colors = [(255, 255, 255), (0, 0, 0)]  # 白→黒

        image = gen._create_gradient_background(
            width=width,
            height=height,
            gradient_type='linear',
            colors=colors,
            direction='diagonal'
        )

        # 左上（白に近い）
        top_left = image.getpixel((0, 0))
        assert all(c > 200 for c in top_left[:3])  # 明るい

        # 右下（黒に近い）
        bottom_right = image.getpixel((width - 1, height - 1))
        assert all(c < 100 for c in bottom_right[:3])  # 暗い

    def test_radial_gradient(self):
        """放射状グラデーション生成"""
        gen = ImageGenerator()
        width, height = 200, 200
        colors = [(255, 255, 0), (128, 0, 128)]  # 黄色→紫

        image = gen._create_gradient_background(
            width=width,
            height=height,
            gradient_type='radial',
            colors=colors
        )

        # 中心（黄色に近い）
        center_pixel = image.getpixel((width // 2, height // 2))
        assert center_pixel[0] > 200  # 赤成分が強い（黄色）
        assert center_pixel[1] > 200  # 緑成分も強い（黄色）

        # 四隅（紫に近い）
        corner_pixel = image.getpixel((0, 0))
        assert corner_pixel[0] > 100  # 赤成分がある（紫）
        assert corner_pixel[2] > 100  # 青成分がある（紫）
        assert corner_pixel[1] < 50   # 緑成分が少ない

    def test_multi_color_gradient(self):
        """3色以上のグラデーション"""
        gen = ImageGenerator()
        width, height = 300, 100
        colors = [
            (255, 0, 0),    # 赤
            (0, 255, 0),    # 緑
            (0, 0, 255)     # 青
        ]

        image = gen._create_gradient_background(
            width=width,
            height=height,
            gradient_type='linear',
            colors=colors,
            direction='horizontal'
        )

        # 左端（赤）
        left = image.getpixel((0, height // 2))
        assert left[0] > 200 and left[1] < 100 and left[2] < 100

        # 中央（緑に近い）
        center = image.getpixel((width // 2, height // 2))
        assert center[1] > 150  # 緑成分が強い

        # 右端（青）
        right = image.getpixel((width - 1, height // 2))
        assert right[2] > 200 and right[0] < 100 and right[1] < 100

    def test_gradient_default_colors(self):
        """デフォルト色（colors=Noneの場合）"""
        gen = ImageGenerator()
        width, height = 100, 100

        image = gen._create_gradient_background(
            width=width,
            height=height,
            gradient_type='linear',
            colors=None,  # デフォルト色を使用
            direction='vertical'
        )

        # サイズ確認のみ（デフォルト色は白系グラデーション）
        assert image.size == (width, height)
        assert image.mode == 'RGBA'

    def test_gradient_invalid_type(self):
        """不正なグラデーションタイプ"""
        gen = ImageGenerator()

        # デフォルト（linear）にフォールバック
        image = gen._create_gradient_background(
            width=100,
            height=100,
            gradient_type='invalid',
            colors=[(255, 0, 0), (0, 0, 255)]
        )

        assert image.size == (100, 100)

    def test_gradient_rgba_mode(self):
        """RGBA形式で生成されることを確認"""
        gen = ImageGenerator()

        image = gen._create_gradient_background(
            width=100,
            height=100,
            gradient_type='linear',
            colors=[(255, 255, 255), (0, 0, 0)]
        )

        assert image.mode == 'RGBA'

        # アルファチャンネルが完全不透明
        pixel = image.getpixel((50, 50))
        assert len(pixel) == 4
        assert pixel[3] == 255  # アルファ値が255
