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
        card_region.close()

        # 半透明着色レイヤーを重ねる
        tint_layer = Image.new('RGBA', blurred.size, glass_tint)
        composited = Image.alpha_composite(blurred, tint_layer)
        blurred.close()
        tint_layer.close()

        # 角丸マスクを作成
        if radius > 0:
            mask = Image.new('L', (x2 - x1, y2 - y1), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (x2 - x1 - 1, y2 - y1 - 1)],
                radius=radius,
                fill=255
            )
            image.paste(composited, (x1, y1), mask)
            del mask_draw
            mask.close()
        else:
            image.paste(composited, (x1, y1))
        composited.close()

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

    @staticmethod
    def _parse_hex_color(hex_color: str) -> Tuple[int, int, int]:
        """16進数カラーコード（#RRGGBB）をRGBタプルに変換

        Args:
            hex_color: 16進数カラーコード（例: "#ff0000", "#4285f4"）

        Returns:
            Tuple[int, int, int]: RGB色 (R, G, B)
                                  無効な形式の場合はデフォルト色 #4285f4 を返す
        """
        # デフォルト色（Google Blue）
        default_color = (66, 133, 244)

        # 基本的なバリデーション
        if not hex_color or not isinstance(hex_color, str):
            return default_color

        # #RRGGBB形式をチェック
        if not hex_color.startswith('#') or len(hex_color) != 7:
            return default_color

        try:
            # #を除いて16進数としてパース
            hex_value = hex_color[1:]
            r = int(hex_value[0:2], 16)
            g = int(hex_value[2:4], 16)
            b = int(hex_value[4:6], 16)
            return (r, g, b)
        except ValueError:
            # パースエラーの場合はデフォルト色を返す
            return default_color

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

            region_w = DAY_COLUMN_WIDTH
            region_h = slot_y_end - slot_y_start
            overlay = Image.new('RGBA', (region_w, region_h), highlight_color)
            image.alpha_composite(overlay, dest=(grid_x_start, slot_y_start))
            overlay.close()
            draw = ImageDraw.Draw(image)

    def _create_gradient_background(
        self,
        width: int,
        height: int,
        gradient_type: str = 'linear',
        colors: List[Tuple[int, int, int]] = None,
        direction: str = 'vertical'
    ) -> Image.Image:
        """グラデーション背景画像を生成（高速版：rectangleを使用）

        Args:
            width: 画像幅
            height: 画像高さ
            gradient_type: グラデーションタイプ（'linear', 'radial'）
            colors: グラデーション色のリスト [(R,G,B), ...]
                    Noneの場合はデフォルト色（白系グラデーション）
            direction: 線形グラデーションの方向（'vertical', 'horizontal', 'diagonal'）

        Returns:
            Image.Image: RGBA形式のグラデーション背景画像
        """
        # デフォルト色（クリーム系の白グラデーション）
        if colors is None:
            colors = [(255, 255, 255), (245, 245, 240)]

        # 背景画像を作成
        image = Image.new('RGBA', (width, height))
        draw = ImageDraw.Draw(image)

        if gradient_type == 'radial':
            # 放射状グラデーション（簡易版：同心円状に描画）
            center_x, center_y = width / 2, height / 2
            max_radius = ((width / 2) ** 2 + (height / 2) ** 2) ** 0.5

            # 最初に全体を一番外側の色で塗りつぶし
            outer_color = self._interpolate_gradient_color(colors, 1.0)
            draw.rectangle([(0, 0), (width, height)], fill=outer_color + (255,))

            # 半径方向に段階的に描画（200ステップで十分滑らか）
            steps = min(200, int(max_radius))
            for i in range(steps, 0, -1):
                ratio = i / steps
                color = self._interpolate_gradient_color(colors, ratio)
                radius = int(max_radius * ratio)

                # 円を描画
                bbox = [
                    int(center_x - radius), int(center_y - radius),
                    int(center_x + radius), int(center_y + radius)
                ]
                draw.ellipse(bbox, fill=color + (255,))

        else:
            # 線形グラデーション（高速版：1行ずつrectangle）
            if direction == 'horizontal':
                # 水平方向
                for x in range(width):
                    ratio = x / width
                    color = self._interpolate_gradient_color(colors, ratio)
                    draw.rectangle([(x, 0), (x, height)], fill=color + (255,))
            elif direction == 'diagonal':
                # 斜め方向（Y方向で描画）
                for y in range(height):
                    # 斜め方向の平均的な比率
                    ratio = y / height
                    color = self._interpolate_gradient_color(colors, ratio)
                    draw.rectangle([(0, y), (width, y)], fill=color + (255,))
            else:  # vertical（デフォルト）
                # 垂直方向
                for y in range(height):
                    ratio = y / height
                    color = self._interpolate_gradient_color(colors, ratio)
                    draw.rectangle([(0, y), (width, y)], fill=color + (255,))

        return image

    def _interpolate_gradient_color(
        self,
        colors: List[Tuple[int, int, int]],
        ratio: float
    ) -> Tuple[int, int, int]:
        """グラデーション色を補間

        複数色のグラデーションに対応（2色以上）

        Args:
            colors: 色のリスト [(R,G,B), ...]
            ratio: 補間位置（0.0 ~ 1.0）

        Returns:
            Tuple[int, int, int]: 補間された色 (R, G, B)
        """
        if len(colors) == 1:
            return colors[0]

        # 補間位置を計算
        segment_count = len(colors) - 1
        segment_ratio = ratio * segment_count
        segment_index = int(segment_ratio)

        # 最後のセグメントを超えないようにクリップ
        if segment_index >= segment_count:
            return colors[-1]

        # セグメント内の補間率
        local_ratio = segment_ratio - segment_index

        # 2色間を線形補間
        color1 = colors[segment_index]
        color2 = colors[segment_index + 1]
        return self._interpolate_color(color1, color2, local_ratio)
