"""
チケット022 Phase 4: アカウント色反映のテスト

ImageGeneratorでevent.account_colorをカラーバーに反映する
"""
import pytest
from datetime import datetime
from PIL import Image, ImageDraw

from src.models.event import CalendarEvent
from src.image_generator import ImageGenerator


def _make_event_with_account_color(summary, start_dt, end_dt, account_color='#4285f4'):
    """テスト用CalendarEvent（アカウント色付き）を作成"""
    return CalendarEvent(
        id=f'test_{summary}',
        summary=summary,
        start_datetime=start_dt,
        end_datetime=end_dt,
        is_all_day=False,
        calendar_id='primary',
        account_id='account_1',
        account_color=account_color,
        account_display_name='テストアカウント'
    )


class TestParseHexColor:
    """_parse_hex_color()メソッドのテスト"""

    def test_parse_hex_color_lowercase(self):
        """小文字の#RRGGBB形式をパースできる"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('#ff0000')
        assert result == (255, 0, 0)

    def test_parse_hex_color_uppercase(self):
        """大文字の#RRGGBB形式をパースできる"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('#00FF00')
        assert result == (0, 255, 0)

    def test_parse_hex_color_mixed_case(self):
        """大文字・小文字混在の#RRGGBB形式をパースできる"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('#aB12Cd')
        assert result == (171, 18, 205)

    def test_parse_hex_color_blue(self):
        """#0000FF（青）をパースできる"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('#0000ff')
        assert result == (0, 0, 255)

    def test_parse_hex_color_white(self):
        """#FFFFFF（白）をパースできる"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('#ffffff')
        assert result == (255, 255, 255)

    def test_parse_hex_color_black(self):
        """#000000（黒）をパースできる"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('#000000')
        assert result == (0, 0, 0)

    def test_parse_hex_color_google_blue(self):
        """#4285f4（Google Blue）をパースできる"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('#4285f4')
        assert result == (66, 133, 244)

    def test_parse_hex_color_invalid_format_returns_default(self):
        """無効な形式の場合、デフォルト色（Google Blue）を返す"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('invalid')
        assert result == (66, 133, 244)  # デフォルト: #4285f4

    def test_parse_hex_color_short_format_returns_default(self):
        """短縮形式（#RGB）の場合、デフォルト色を返す"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('#fff')
        assert result == (66, 133, 244)  # デフォルト: #4285f4

    def test_parse_hex_color_no_hash_returns_default(self):
        """#なしの場合、デフォルト色を返す"""
        gen = ImageGenerator()
        result = gen._parse_hex_color('ff0000')
        assert result == (66, 133, 244)  # デフォルト: #4285f4


class TestAccountColorReflection:
    """account_colorがカラーバーに反映されることのテスト"""

    def test_draw_card_with_red_account_color(self):
        """赤色のアカウントカラーがカラーバーに反映される"""
        gen = ImageGenerator()
        gen.set_theme('simple')

        # 赤色のアカウント
        event = _make_event_with_account_color(
            'ミーティング',
            datetime(2026, 2, 5, 14, 0),
            datetime(2026, 2, 5, 15, 0),
            account_color='#ff0000'
        )

        # カード描画
        image = Image.new('RGB', (400, 200), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        gen._draw_single_event_card(draw, event, 10, 10, is_finished=False, is_in_progress=False)

        # カラーバー領域のピクセル色を確認（赤であることを確認）
        # カラーバーの位置: (x + CARD_PADDING, y + FONT_SIZE_CARD_DATE + 10付近)
        # 期待: 赤色 (255, 0, 0) またはそれに近い色
        color_bar_x = 10 + 15  # x + CARD_PADDING
        color_bar_y = 10 + 24 + 10 + 10  # y + FONT_SIZE_CARD_DATE + 10 + α

        pixel_color = image.getpixel((color_bar_x, color_bar_y))
        # 赤色であることを確認（RGB値の赤成分が高い）
        assert pixel_color[0] > 200  # R成分が高い
        assert pixel_color[1] < 50   # G成分が低い
        assert pixel_color[2] < 50   # B成分が低い

    def test_draw_card_with_green_account_color(self):
        """緑色のアカウントカラーがカラーバーに反映される"""
        gen = ImageGenerator()
        gen.set_theme('simple')

        # 緑色のアカウント
        event = _make_event_with_account_color(
            'タスク',
            datetime(2026, 2, 5, 10, 0),
            datetime(2026, 2, 5, 11, 0),
            account_color='#00ff00'
        )

        # カード描画
        image = Image.new('RGB', (400, 200), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        gen._draw_single_event_card(draw, event, 10, 10, is_finished=False, is_in_progress=False)

        # カラーバー領域のピクセル色を確認（緑であることを確認）
        color_bar_x = 10 + 15
        color_bar_y = 10 + 24 + 10 + 10

        pixel_color = image.getpixel((color_bar_x, color_bar_y))
        # 緑色であることを確認
        assert pixel_color[0] < 50   # R成分が低い
        assert pixel_color[1] > 200  # G成分が高い
        assert pixel_color[2] < 50   # B成分が低い

    def test_draw_card_with_blue_account_color(self):
        """青色のアカウントカラーがカラーバーに反映される"""
        gen = ImageGenerator()
        gen.set_theme('simple')

        # 青色のアカウント（Google Blue）
        event = _make_event_with_account_color(
            'レビュー',
            datetime(2026, 2, 5, 16, 0),
            datetime(2026, 2, 5, 17, 0),
            account_color='#4285f4'
        )

        # カード描画
        image = Image.new('RGB', (400, 200), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        gen._draw_single_event_card(draw, event, 10, 10, is_finished=False, is_in_progress=False)

        # カラーバー領域のピクセル色を確認（青であることを確認）
        color_bar_x = 10 + 15
        color_bar_y = 10 + 24 + 10 + 10

        pixel_color = image.getpixel((color_bar_x, color_bar_y))
        # 青色であることを確認
        assert pixel_color[0] < 100  # R成分が低い
        assert pixel_color[1] > 100  # G成分が中程度
        assert pixel_color[2] > 200  # B成分が高い
