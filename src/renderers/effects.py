"""
ビジュアルエフェクトMixin
角丸矩形、影、ガラスモーフィズム、色相分離テキスト、プログレスバー、現在時刻ハイライト
"""
from datetime import datetime
from typing import List, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from ..models.event import CalendarEvent
from ..config import (
    CARD_HEIGHT, CARD_PADDING,
    WEEK_CALENDAR_START_HOUR, WEEK_CALENDAR_END_HOUR,
    DAY_COLUMN_WIDTH,
)


class EffectsRendererMixin:
    """ビジュアルエフェクト描画Mixin"""

    def _draw_rounded_rectangle(
        self,
        draw: ImageDraw.ImageDraw,
        xy: List[Tuple[int, int]],
        radius: int,
        fill: Optional[Tuple[int, ...]] = None,
        outline: Optional[Tuple[int, ...]] = None,
        width: int = 1
    ):
        """
        角丸矩形を描画

        Args:
            draw: ImageDrawオブジェクト
            xy: 矩形の座標 [(x1, y1), (x2, y2)]
            radius: 角丸の半径
            fill: 塗りつぶし色（RGBA対応）
            outline: 枠線色
            width: 枠線の幅
        """
        x1, y1 = xy[0]
        x2, y2 = xy[1]

        # 角丸矩形を描画
        draw.rounded_rectangle(
            [(x1, y1), (x2, y2)],
            radius=radius,
            fill=fill,
            outline=outline,
            width=width
        )

    def _draw_card_shadow(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        height: int,
        radius: int = 0,
        offset: int = 3
    ):
        """
        カードの影を描画

        Args:
            draw: ImageDrawオブジェクト
            x: カードのX座標
            y: カードのY座標
            width: カードの幅
            height: カードの高さ
            radius: 角丸の半径（0の場合は通常の矩形）
            offset: 影のオフセット（ピクセル）
        """
        # 影の色（黒で透明度40%）
        shadow_color = (0, 0, 0, 102)  # RGBA: 102 = 255 * 0.4

        # 影の座標（カードより少しずれた位置）
        shadow_x = x + offset
        shadow_y = y + offset

        if radius > 0:
            # 角丸の影
            draw.rounded_rectangle(
                [(shadow_x, shadow_y), (shadow_x + width, shadow_y + height)],
                radius=radius,
                fill=shadow_color
            )
        else:
            # 通常の矩形の影
            draw.rectangle(
                [(shadow_x, shadow_y), (shadow_x + width, shadow_y + height)],
                fill=shadow_color
            )

    def _draw_card_background(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        height: int,
        card_bg: Tuple,
        card_alpha: int = 255,
        card_border: Tuple = (200, 200, 200),
        card_border_width: int = 1,
        card_radius: int = 0
    ):
        """カード背景の共通描画処理

        Args:
            draw: ImageDrawオブジェクト
            x, y: カードの座標
            width, height: カードのサイズ
            card_bg: 背景色 (R, G, B) or (R, G, B, A)
            card_alpha: 透明度 (0-255)
            card_border: 枠線色
            card_border_width: 枠線の幅
            card_radius: 角丸の半径
        """
        card_bg_rgba = card_bg + (card_alpha,) if len(card_bg) == 3 else card_bg

        if card_radius > 0:
            self._draw_rounded_rectangle(
                draw,
                [(x, y), (x + width, y + height)],
                radius=card_radius,
                fill=card_bg_rgba,
                outline=card_border,
                width=card_border_width
            )
        else:
            draw.rectangle(
                [(x, y), (x + width, y + height)],
                fill=card_bg_rgba,
                outline=card_border,
                width=card_border_width
            )

    def _draw_glass_card(
        self,
        draw: ImageDraw.ImageDraw,
        image: Image.Image,
        x: int,
        y: int,
        width: int,
        height: int,
        radius: int = 0
    ):
        """
        ガラスモーフィズムカードを描画

        背景をクロップ→ぼかし→半透明着色→合成で、すりガラス効果を実現。

        Args:
            draw: ImageDrawオブジェクト
            image: 背景画像（RGBA）
            x: カードのX座標
            y: カードのY座標
            width: カードの幅
            height: カードの高さ
            radius: 角丸の半径
        """
        blur_radius = self.theme.get('glass_blur_radius', 15)
        glass_tint = self.theme.get('glass_tint', (255, 255, 255, 50))

        # 座標をクリップ（画像範囲外を防止）
        img_w, img_h = image.size
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(img_w, x + width)
        y2 = min(img_h, y + height)

        if x2 <= x1 or y2 <= y1:
            return

        # カード領域をクロップしてぼかし
        card_region = image.crop((x1, y1, x2, y2))
        blurred = card_region.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # 半透明着色レイヤーを重ねる
        tint_layer = Image.new('RGBA', blurred.size, glass_tint)
        blurred = Image.alpha_composite(blurred, tint_layer)

        # 角丸マスクを作成
        if radius > 0:
            mask = Image.new('L', (x2 - x1, y2 - y1), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (x2 - x1 - 1, y2 - y1 - 1)],
                radius=radius,
                fill=255
            )
            image.paste(blurred, (x1, y1), mask)
        else:
            image.paste(blurred, (x1, y1))

        # 枠線（半透明白）
        border_color = self.theme.get('glass_border_color', (255, 255, 255, 77))
        if radius > 0:
            draw.rounded_rectangle(
                [(x1, y1), (x2 - 1, y2 - 1)],
                radius=radius,
                outline=border_color,
                width=1
            )
        else:
            draw.rectangle(
                [(x1, y1), (x2 - 1, y2 - 1)],
                outline=border_color,
                width=1
            )

    @staticmethod
    def _interpolate_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
        """2色間を線形補間する

        Args:
            color1: 開始色 (R, G, B)
            color2: 終了色 (R, G, B)
            ratio: 補間率 (0.0 ~ 1.0)

        Returns:
            Tuple[int, int, int]: 補間された色 (R, G, B)
        """
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        return (r, g, b)

    def _draw_event_progress_bar(
        self,
        draw: ImageDraw.ImageDraw,
        event: CalendarEvent,
        x: int,
        y: int,
        width: int,
        card_height: int = None
    ):
        """現在進行中のイベントに進行状況バーを描画

        Args:
            draw: ImageDraw オブジェクト
            event: カレンダーイベント
            x: バーのX座標
            y: バーのY座標
            width: バーの幅
            card_height: カードの高さ（Noneの場合はデフォルトCARD_HEIGHT）
        """
        if card_height is None:
            card_height = CARD_HEIGHT

        # 進行中かチェック
        now = datetime.now()
        if event.is_all_day:
            return  # 終日イベントにはプログレスバーを表示しない

        if not (event.start_datetime <= now <= event.end_datetime):
            return  # 進行中でない場合は描画しない

        # 進行率計算
        total_duration = (event.end_datetime - event.start_datetime).total_seconds()
        elapsed = (now - event.start_datetime).total_seconds()
        progress_ratio = min(elapsed / total_duration, 1.0) if total_duration > 0 else 0

        # バーの設定
        bar_height = 4
        bar_y = y + card_height - CARD_PADDING - bar_height - 5

        # 背景バー（薄いグレー）
        draw.rectangle(
            [(x, bar_y), (x + width, bar_y + bar_height)],
            fill=(220, 220, 220)
        )

        # 進行バー（グラデーション画像を生成してpaste）
        accent = self.theme.get('accent_color', None)
        start_color = accent if accent else (0, 122, 255)
        end_color = (0, 200, 100)
        progress_width = int(width * progress_ratio)
        if progress_width > 0:
            for i in range(progress_width):
                ratio = i / width
                color = self._interpolate_color(start_color, end_color, ratio)
                draw.line(
                    [(x + i, bar_y), (x + i, bar_y + bar_height)],
                    fill=color
                )

    def _draw_chromatic_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        pos: Tuple[int, int],
        font,
        base_color: Tuple[int, int, int],
        offset: int = None
    ):
        """RGB色相分離効果付きテキスト描画

        各RGBチャンネルを微妙にずらして描画し、独特な視覚効果を生む。

        Args:
            draw: ImageDraw オブジェクト
            text: 描画テキスト
            pos: (x, y) 座標
            font: フォント
            base_color: ベース色 (R, G, B)
            offset: ピクセルオフセット（Noneの場合テーマから取得）
        """
        if offset is None:
            offset = self.theme.get('chromatic_offset', 0)

        if offset <= 0:
            # オフセットなしの場合は通常描画
            draw.text(pos, text, font=font, fill=base_color)
            return

        x, y = pos
        # 赤チャンネル（左上シフト）
        draw.text(
            (x - offset, y - offset), text, font=font,
            fill=(base_color[0], 0, 0, 120)
        )
        # 緑チャンネル（中央）
        draw.text(
            (x, y), text, font=font,
            fill=(0, base_color[1], 0, 140)
        )
        # 青チャンネル（右下シフト）
        draw.text(
            (x + offset, y + offset), text, font=font,
            fill=(0, 0, base_color[2], 120)
        )

    def _draw_current_time_arrow(
        self,
        draw: ImageDraw.ImageDraw,
        grid_x_start: int,
        grid_x_end: int,
        grid_y_start: int,
        hour_height: float,
        image: Image.Image = None
    ):
        """週間カレンダーに現在時刻の蛍光ハイライトを描画

        Args:
            draw: ImageDraw オブジェクト
            grid_x_start: グリッドの開始X座標
            grid_x_end: グリッドの終了X座標
            grid_y_start: グリッドの開始Y座標
            hour_height: 1時間あたりの高さ（ピクセル）
            image: 画像オブジェクト（蛍光塗りつぶし用、Noneで省略可）
        """
        now = datetime.now()

        # 週間カレンダーの表示時間範囲内かチェック
        if not (WEEK_CALENDAR_START_HOUR <= now.hour <= WEEK_CALENDAR_END_HOUR):
            return  # 表示範囲外の場合は描画しない

        # 蛍光色で現在の1時間枠を塗りつぶし（今日の列のみ）
        if image is not None:
            highlight_color = self.theme.get(
                'current_time_highlight', (255, 255, 100, 60)
            )
            slot_y_start = grid_y_start + int((now.hour - WEEK_CALENDAR_START_HOUR) * hour_height)
            slot_y_end = slot_y_start + int(hour_height)

            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [(grid_x_start, slot_y_start),
                 (grid_x_start + DAY_COLUMN_WIDTH, slot_y_end)],
                fill=highlight_color
            )
            image.alpha_composite(overlay)
            draw = ImageDraw.Draw(image)
