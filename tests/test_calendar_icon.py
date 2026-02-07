"""
Google Calendar アイコン統合のテスト（TDD）
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PIL import Image, ImageDraw

from src.image_generator import ImageGenerator
from src.config import IMAGE_WIDTH, IMAGE_HEIGHT


class TestCalendarIconPlacement:
    """Google Calendar アイコン配置のテスト"""

    @patch('src.image_generator.platform.system')
    @patch('pathlib.Path.exists')
    def test_mac_icon_placement_top_right(self, mock_exists, mock_system):
        """
        TDD: Mac環境でアイコンが上部右寄せに配置されることを確認

        要件:
        - Mac: 画像上部（Y: 10-30px）、右寄せ（X: IMAGE_WIDTH - 60px）
        - アイコンサイズ: 40x40px
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_exists.return_value = True

        generator = ImageGenerator()

        # アイコン配置座標を取得するメソッドをテスト
        x, y = generator._get_icon_position()

        # Assert: Mac環境での配置
        expected_x = IMAGE_WIDTH - 60
        assert x == expected_x, f"X座標が期待値と異なる: {x} != {expected_x}"
        assert 10 <= y <= 30, f"Y座標が範囲外: {y}"

    @patch('src.image_generator.platform.system')
    @patch('pathlib.Path.exists')
    def test_windows_icon_placement_bottom_right(self, mock_exists, mock_system):
        """
        TDD: Windows環境でアイコンが右下に配置されることを確認

        要件:
        - Windows: 画像下部（Y: IMAGE_HEIGHT - 60px）、右寄せ（X: IMAGE_WIDTH - 60px）
        - アイコンサイズ: 40x40px
        """
        # Setup
        mock_system.return_value = 'Windows'
        mock_exists.return_value = True

        generator = ImageGenerator()

        # アイコン配置座標を取得
        x, y = generator._get_icon_position()

        # Assert: Windows環境での配置
        expected_x = IMAGE_WIDTH - 60
        expected_y = IMAGE_HEIGHT - 60
        assert x == expected_x, f"X座標が期待値と異なる: {x} != {expected_x}"
        assert y == expected_y, f"Y座標が期待値と異なる: {y} != {expected_y}"

    @patch('src.image_generator.platform.system')
    @patch('pathlib.Path.exists')
    def test_linux_icon_placement_defaults_to_top_right(self, mock_exists, mock_system):
        """
        TDD: Linux環境ではMac同様に上部右寄せに配置されることを確認

        要件:
        - Linux: デフォルトでMac同様の配置
        """
        # Setup
        mock_system.return_value = 'Linux'
        mock_exists.return_value = True

        generator = ImageGenerator()

        # アイコン配置座標を取得
        x, y = generator._get_icon_position()

        # Assert: Linux環境での配置（Mac同様）
        expected_x = IMAGE_WIDTH - 60
        assert x == expected_x
        assert 10 <= y <= 30

    @patch('src.image_generator.platform.system')
    @patch('pathlib.Path.exists')
    def test_icon_size_is_40x40(self, mock_exists, mock_system):
        """
        TDD: アイコンサイズが40x40pxであることを確認

        要件:
        - アイコンサイズ: 40x40px
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_exists.return_value = True

        generator = ImageGenerator()

        # アイコンサイズを取得
        icon_size = generator._get_icon_size()

        # Assert: サイズが40x40px
        assert icon_size == (40, 40), f"アイコンサイズが期待値と異なる: {icon_size}"


class TestCalendarIconDrawing:
    """Google Calendar アイコン描画のテスト"""

    @patch('src.image_generator.platform.system')
    @patch('pathlib.Path.exists')
    def test_draw_calendar_icon_called_in_generation(self, mock_exists, mock_system):
        """
        TDD: 壁紙生成時にアイコン描画メソッドが呼ばれることを確認

        要件:
        - generate_wallpaper()内で_draw_calendar_icon()が呼ばれる
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_exists.return_value = True

        generator = ImageGenerator()

        # _draw_calendar_iconメソッドをモック化
        with patch.object(generator, '_draw_calendar_icon') as mock_draw_icon:
            # 壁紙生成（最小限のイベントデータ）
            generator.generate_wallpaper(
                today_events=[],
                week_events=[]
            )

            # Assert: _draw_calendar_iconが呼ばれた
            assert mock_draw_icon.called, "_draw_calendar_icon()が呼ばれていない"

    @patch('src.image_generator.platform.system')
    @patch('pathlib.Path.exists')
    def test_icon_does_not_overlap_other_elements(self, mock_exists, mock_system):
        """
        TDD: アイコンが他の要素と重ならないことを確認

        要件:
        - アイコンは独立した領域に配置される
        - 予定カードやカレンダーと重ならない
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_exists.return_value = True

        generator = ImageGenerator()

        # アイコン配置位置
        icon_x, icon_y = generator._get_icon_position()
        icon_size = generator._get_icon_size()

        # アイコン領域
        icon_area = {
            'x1': icon_x,
            'y1': icon_y,
            'x2': icon_x + icon_size[0],
            'y2': icon_y + icon_size[1]
        }

        # 予定カード領域（レイアウトから取得）
        card_y = generator.layout['card_y_start']

        # Assert: アイコンがカードより上にある（Mac）またはカレンダーより下にある（Windows）
        if generator.system == 'Darwin':
            assert icon_area['y2'] < card_y, "アイコンが予定カードと重なっている"
        elif generator.system == 'Windows':
            week_cal_y = generator.layout['week_calendar_y_start']
            calendar_height = generator.layout['calendar_height']
            assert icon_area['y1'] > week_cal_y + calendar_height, "アイコンがカレンダーと重なっている"
