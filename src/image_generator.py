"""
壁紙画像生成モジュール（新デザイン）
カレンダーイベントを基に壁紙画像を生成
"""
import platform
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

from PIL import Image, ImageDraw, ImageFont

from .config import (
    IMAGE_WIDTH, IMAGE_HEIGHT,
    BACKGROUND_COLOR, TEXT_COLOR,
    FONT_PATHS,
    DEFAULT_EVENT_COLORS,
    OUTPUT_DIR, WALLPAPER_FILENAME_TEMPLATE,
    # 新デザイン設定（最適化版）
    DESKTOP_ICON_AREA_HEIGHT,
    SPACING_TOP, SPACING_MIDDLE,
    CARD_WIDTH, CARD_HEIGHT, CARD_MARGIN, CARD_PADDING,
    FONT_SIZE_CARD_DATE, FONT_SIZE_CARD_TIME, FONT_SIZE_CARD_TITLE, FONT_SIZE_CARD_LOCATION,
    WEEK_CALENDAR_START_HOUR, WEEK_CALENDAR_END_HOUR,
    HOUR_HEIGHT, DAY_COLUMN_WIDTH,
    FONT_SIZE_HOUR_LABEL, FONT_SIZE_DAY_HEADER, FONT_SIZE_EVENT_BLOCK,
    # 背景画像設定
    BACKGROUND_IMAGE_PATH,
    # Google Calendar アイコン設定
    CALENDAR_ICON_PATH, CALENDAR_ICON_SIZE,
    ICON_MAC_POSITION, ICON_WINDOWS_POSITION, ICON_LINUX_POSITION,
    # テーマ設定
    THEME,
    # マルチディスプレイ設定
    WALLPAPER_TARGET_DESKTOP, AUTO_DETECT_RESOLUTION
)
from . import themes
from .display_info import DisplayInfo

logger = logging.getLogger(__name__)


class ImageGenerator:
    """壁紙画像生成クラス（新デザイン対応）"""

    def __init__(self):
        self.system = platform.system()

        # 解像度の自動検出
        if AUTO_DETECT_RESOLUTION and WALLPAPER_TARGET_DESKTOP > 0:
            display_info = DisplayInfo()
            self.width, self.height = display_info.get_target_display_resolution(WALLPAPER_TARGET_DESKTOP)
            logger.info(f"解像度を自動検出しました: {self.width}x{self.height}")
        else:
            self.width = IMAGE_WIDTH
            self.height = IMAGE_HEIGHT
            logger.info(f"デフォルト解像度を使用: {self.width}x{self.height}")

        # 各種フォントを読み込み
        self.font_card_date = self._get_font(FONT_SIZE_CARD_DATE)
        self.font_card_time = self._get_font(FONT_SIZE_CARD_TIME)
        self.font_card_title = self._get_font(FONT_SIZE_CARD_TITLE)
        self.font_card_location = self._get_font(FONT_SIZE_CARD_LOCATION)
        self.font_hour_label = self._get_font(FONT_SIZE_HOUR_LABEL)
        self.font_day_header = self._get_font(FONT_SIZE_DAY_HEADER)
        self.font_event_block = self._get_font(FONT_SIZE_EVENT_BLOCK)

        # レイアウト計算（動的）
        self.layout = self._calculate_layout()

        # テーマ初期化
        self.theme = themes.get_theme(THEME)

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """システムに応じた日本語フォントを取得"""
        font_paths = FONT_PATHS.get(self.system, [])

        for font_path in font_paths:
            try:
                if Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)
            except Exception as e:
                logger.warning(f"フォント読み込みエラー ({font_path}): {e}")

        logger.warning(f"日本語フォントが見つかりません。デフォルトフォントを使用します")
        return ImageFont.load_default()

    def _calculate_layout(self) -> Dict[str, int]:
        """
        動的レイアウト計算（1080px以内に収める）

        Returns:
            Dict: レイアウトパラメータ
        """
        # 固定値
        desktop_h = DESKTOP_ICON_AREA_HEIGHT
        card_h = CARD_HEIGHT
        spacing_top = SPACING_TOP
        spacing_middle = SPACING_MIDDLE
        header_h = FONT_SIZE_DAY_HEADER + 10

        # 時間範囲
        total_hours = WEEK_CALENDAR_END_HOUR - WEEK_CALENDAR_START_HOUR + 1

        # 1時間あたりの高さ（固定値を使用、視認性より高さ削減優先）
        hour_height = HOUR_HEIGHT

        # 実際のカレンダー高さ
        calendar_height = hour_height * total_hours

        # 各要素のY座標
        card_y = desktop_h + spacing_top
        week_cal_y = card_y + card_h + spacing_middle
        grid_y = week_cal_y + header_h

        return {
            'card_y_start': card_y,
            'week_calendar_y_start': week_cal_y,
            'grid_y_start': grid_y,
            'hour_height': hour_height,
            'calendar_height': calendar_height,
            'header_height': header_h
        }

    def set_theme(self, theme_name: str):
        """
        テーマを切り替える

        Args:
            theme_name: テーマ名（'simple', 'fancy', 'stylish'）
        """
        self.theme = themes.get_theme(theme_name)
        logger.info(f"テーマを '{theme_name}' に切り替えました")

    def _create_gradient_background(self, gradient_colors: List[Tuple[int, int, int]]) -> Image.Image:
        """
        グラデーション背景画像を生成（Fancy用）

        Args:
            gradient_colors: グラデーションカラーのリスト [(R,G,B), (R,G,B), ...]

        Returns:
            Image.Image: グラデーション背景画像
        """
        if len(gradient_colors) < 2:
            raise ValueError("グラデーションには最低2色必要です")

        # 新しい画像を作成
        img = Image.new('RGB', (self.width, self.height))

        # 開始色と終了色
        start_color = gradient_colors[0]
        end_color = gradient_colors[1]

        # 垂直グラデーション（上から下へ）
        for y in range(self.height):
            # 現在の位置の割合（0.0〜1.0）
            ratio = y / self.height

            # 色を補間
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)

            # 1行分の色で塗りつぶし
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, y), (self.width, y + 1)], fill=(r, g, b))

        return img

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
        角丸矩形を描画（Fancy用）

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

    def _get_icon_position(self) -> Tuple[int, int]:
        """
        OS別のアイコン配置座標を取得（動的解像度対応）

        Returns:
            Tuple[int, int]: (x, y) 座標
        """
        if self.system == 'Darwin':  # Mac: 上部右寄せ
            return (self.width - 60, 20)
        elif self.system == 'Windows':  # Windows: 右下
            return (self.width - 60, self.height - 60)
        else:  # Linux その他: Mac同様
            return (self.width - 60, 20)

    def _get_icon_size(self) -> Tuple[int, int]:
        """
        アイコンサイズを取得

        Returns:
            Tuple[int, int]: (width, height)
        """
        return CALENDAR_ICON_SIZE

    def _draw_calendar_icon(self, draw: ImageDraw.ImageDraw):
        """
        Google Calendarアイコンを描画

        Args:
            draw: ImageDrawオブジェクト
        """
        try:
            # アイコン画像を読み込み
            if CALENDAR_ICON_PATH and Path(CALENDAR_ICON_PATH).exists():
                icon_img = Image.open(CALENDAR_ICON_PATH)

                # サイズ調整（必要に応じて）
                icon_size = self._get_icon_size()
                if icon_img.size != icon_size:
                    icon_img = icon_img.resize(icon_size, Image.Resampling.LANCZOS)

                # 配置位置を取得
                x, y = self._get_icon_position()

                # アイコンを貼り付け（透過対応）
                if icon_img.mode == 'RGBA':
                    # 透過画像の場合
                    draw._image.paste(icon_img, (x, y), icon_img)
                else:
                    # 不透明画像の場合
                    draw._image.paste(icon_img, (x, y))

                logger.debug(f"アイコンを配置しました: ({x}, {y})")
            else:
                logger.warning(f"アイコン画像が見つかりません: {CALENDAR_ICON_PATH}")

        except Exception as e:
            logger.error(f"アイコン描画エラー: {e}", exc_info=True)

    def generate_wallpaper(
        self,
        today_events: List[Dict],
        week_events: List[Dict]
    ) -> Optional[Path]:
        """壁紙画像を生成"""
        try:
            # テーマに応じた背景生成
            if 'background_gradient' in self.theme and self.theme['background_gradient']:
                # グラデーション背景（Fancy用）
                logger.info("グラデーション背景を生成します")
                image = self._create_gradient_background(self.theme['background_gradient'])
            elif self.theme.get('background_color'):
                # 単色背景
                bg_color = self.theme['background_color']
                logger.info(f"単色背景を生成します: {bg_color}")
                image = Image.new('RGB', (self.width, self.height), bg_color)
            elif BACKGROUND_IMAGE_PATH and Path(BACKGROUND_IMAGE_PATH).exists():
                # 背景画像を読み込んでリサイズ（後方互換性）
                logger.info(f"背景画像を読み込んでいます: {BACKGROUND_IMAGE_PATH}")
                background = Image.open(BACKGROUND_IMAGE_PATH)
                background = background.resize((self.width, self.height), Image.Resampling.LANCZOS)
                # RGBモードに変換（透明度を削除）
                if background.mode == 'RGBA':
                    rgb_background = Image.new('RGB', (self.width, self.height), (255, 255, 255))
                    rgb_background.paste(background, mask=background.split()[3])
                    image = rgb_background
                else:
                    image = background.convert('RGB')
            else:
                # デフォルト背景（白）
                logger.info("デフォルト背景を生成します")
                image = Image.new('RGB', (self.width, self.height), (255, 255, 255))

            draw = ImageDraw.Draw(image)

            # 動的レイアウト値を使用
            card_y_start = self.layout['card_y_start']
            week_calendar_y_start = self.layout['week_calendar_y_start']

            # 予定カード描画
            self._draw_event_cards(draw, week_events, card_y_start)

            # 週間カレンダー描画
            self._draw_week_calendar(draw, week_events, week_calendar_y_start)

            # Google Calendarアイコン描画
            self._draw_calendar_icon(draw)

            # 画像を保存
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            filename = WALLPAPER_FILENAME_TEMPLATE.format(
                date=datetime.now().strftime('%Y%m%d')
            )
            output_path = OUTPUT_DIR / filename
            image.save(output_path)

            logger.info(f"壁紙画像を生成しました: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"画像生成エラー: {e}", exc_info=True)
            return None

    def _get_events_for_days(self, all_events: List[Dict]) -> Dict[str, List[Dict]]:
        """今日・明日・明後日の予定を抽出"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)

        result = {
            'today': [],
            'tomorrow': [],
            'day_after': []
        }

        for event in all_events:
            event_date = event['start_datetime'].date()
            if event_date == today:
                result['today'].append(event)
            elif event_date == tomorrow:
                result['tomorrow'].append(event)
            elif event_date == day_after:
                result['day_after'].append(event)

        # 各日の予定を時刻順にソート
        for key in result:
            result[key].sort(key=lambda e: e['start_datetime'])

        return result

    def _draw_event_cards(self, draw: ImageDraw.ImageDraw, all_events: List[Dict], y_start: int):
        """3日分の予定カードを描画"""
        events_by_day = self._get_events_for_days(all_events)

        # カードを中央に配置
        total_width = CARD_WIDTH * 3 + CARD_MARGIN * 2
        start_x = (self.width - total_width) // 2

        cards = [
            ('今日の予定', events_by_day['today'], start_x),
            ('明日の予定', events_by_day['tomorrow'], start_x + CARD_WIDTH + CARD_MARGIN),
            ('明後日の予定', events_by_day['day_after'], start_x + (CARD_WIDTH + CARD_MARGIN) * 2)
        ]

        for label, events, x in cards:
            self._draw_single_card(draw, label, events, x, y_start)

    def _draw_single_card(
        self,
        draw: ImageDraw.ImageDraw,
        label: str,
        events: List[Dict],
        x: int,
        y: int
    ):
        """個別の予定カードを描画"""
        # テーマから色と角丸設定を取得
        card_bg = self.theme.get('card_bg', (255, 255, 255))
        card_border = self.theme.get('card_border', (200, 200, 200))
        card_radius = self.theme.get('card_radius', 0)
        text_color = self.theme.get('text_color', (0, 0, 0))

        # カード背景（テーマに応じて角丸または通常の矩形）
        if card_radius > 0:
            # 角丸矩形（Fancy/Stylish用）
            self._draw_rounded_rectangle(
                draw,
                [(x, y), (x + CARD_WIDTH, y + CARD_HEIGHT)],
                radius=card_radius,
                fill=card_bg,
                outline=card_border,
                width=2
            )
        else:
            # 通常の矩形（Simple用）
            draw.rectangle(
                [(x, y), (x + CARD_WIDTH, y + CARD_HEIGHT)],
                fill=card_bg,
                outline=card_border,
                width=2
            )

        # 日付ラベル
        draw.text(
            (x + CARD_PADDING, y + CARD_PADDING),
            label,
            font=self.font_card_date,
            fill=text_color
        )

        current_y = y + CARD_PADDING + FONT_SIZE_CARD_DATE + 10

        if not events:
            # 予定なし
            draw.text(
                (x + CARD_PADDING, current_y),
                '予定なし',
                font=self.font_card_title,
                fill=(150, 150, 150)
            )
        else:
            # 最大3件まで表示
            max_display = min(3, len(events))
            event_height = 45  # 各予定の高さ

            for i in range(max_display):
                event = events[i]

                # カラーバー
                color_id = event.get('color_id', '1')
                bar_color = DEFAULT_EVENT_COLORS.get(color_id, DEFAULT_EVENT_COLORS['1'])
                draw.rectangle(
                    [(x + CARD_PADDING, current_y), (x + CARD_PADDING + 3, current_y + event_height - 5)],
                    fill=bar_color
                )

                text_x = x + CARD_PADDING + 10

                # 時刻
                if event['is_all_day']:
                    time_text = '終日'
                else:
                    time_text = event['start_datetime'].strftime('%H:%M')

                draw.text(
                    (text_x, current_y),
                    time_text,
                    font=self.font_card_time,
                    fill=text_color
                )

                # タイトル
                title = event['summary']
                if len(title) > 18:
                    title = title[:18] + '...'
                draw.text(
                    (text_x, current_y + FONT_SIZE_CARD_TIME + 2),
                    title,
                    font=self.font_card_title,
                    fill=text_color
                )

                # 場所（スペースがあれば）
                if event.get('location') and i < 2:  # 最初の2件のみ場所表示
                    location = event['location']
                    if len(location) > 15:
                        location = location[:15] + '...'
                    # 場所は少し薄めの色で表示
                    location_color = tuple(min(c + 50, 255) for c in text_color[:3])
                    draw.text(
                        (text_x, current_y + FONT_SIZE_CARD_TIME + FONT_SIZE_CARD_TITLE + 4),
                        f"@ {location}",
                        font=self.font_card_location,
                        fill=location_color
                    )

                current_y += event_height

            # 4件目以降の件数表示
            if len(events) > 3:
                remaining_text = f"+{len(events) - 3}件"
                draw.text(
                    (x + CARD_WIDTH - CARD_PADDING - 45, y + CARD_HEIGHT - CARD_PADDING - 15),
                    remaining_text,
                    font=self.font_card_location,
                    fill=(100, 100, 100)
                )

    def _draw_week_calendar(
        self,
        draw: ImageDraw.ImageDraw,
        all_events: List[Dict],
        y_start: int
    ):
        """週間カレンダーを描画"""
        # テーマから色を取得
        text_color = self.theme.get('text_color', (0, 0, 0))
        grid_color = self.theme.get('grid_color', (220, 220, 220))
        card_bg = self.theme.get('card_bg', (255, 255, 255))

        # カレンダーの幅と開始位置
        total_width = DAY_COLUMN_WIDTH * 7
        start_x = (self.width - total_width) // 2

        # 動的レイアウト値を使用
        hour_height = self.layout['hour_height']
        calendar_height = self.layout['calendar_height']

        # 時間範囲
        total_hours = WEEK_CALENDAR_END_HOUR - WEEK_CALENDAR_START_HOUR + 1

        # 曜日ヘッダー（今日から7日分）
        today = datetime.now().date()
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        for i in range(7):
            target_date = today + timedelta(days=i)
            day_name = weekday_names[target_date.weekday()]
            # 日付も表示
            date_str = f"{day_name}\n{target_date.month}/{target_date.day}"

            # textbbox を使って中央揃え位置を計算
            x_center = start_x + i * DAY_COLUMN_WIDTH + DAY_COLUMN_WIDTH // 2
            bbox = draw.multiline_textbbox(
                (0, 0),
                date_str,
                font=self.font_day_header,
                align='center'
            )
            text_width = bbox[2] - bbox[0]
            x_pos = x_center - text_width // 2

            draw.multiline_text(
                (x_pos, y_start),
                date_str,
                font=self.font_day_header,
                fill=text_color,
                align='center'
            )

        # 動的レイアウト値を使用
        header_height = self.layout['header_height']
        grid_y_start = self.layout['grid_y_start']

        # カレンダーグリッドの背景（テーマに応じた色）
        # card_bgがRGBAの場合、RGBのみ使用
        if isinstance(card_bg, tuple) and len(card_bg) == 4:
            grid_bg = card_bg[:3]  # RGB部分のみ
        else:
            grid_bg = card_bg
        draw.rectangle(
            [(start_x, grid_y_start), (start_x + total_width, grid_y_start + calendar_height)],
            fill=grid_bg
        )

        # グリッド線（横線：時間軸）
        for hour in range(total_hours + 1):
            y = grid_y_start + hour * hour_height
            draw.line(
                [(start_x, y), (start_x + total_width, y)],
                fill=grid_color,
                width=1
            )

            # 時間ラベル
            if hour < total_hours:
                hour_value = WEEK_CALENDAR_START_HOUR + hour
                draw.text(
                    (start_x - 45, y + 5),
                    f"{hour_value:02d}:00",
                    font=self.font_hour_label,
                    fill=text_color
                )

        # グリッド線（縦線：曜日）
        for i in range(8):
            x = start_x + i * DAY_COLUMN_WIDTH
            draw.line(
                [(x, grid_y_start), (x, grid_y_start + calendar_height)],
                fill=grid_color,
                width=1
            )

        # イベントブロックを描画
        for day_offset in range(7):
            event_date = today + timedelta(days=day_offset)
            day_events = [e for e in all_events if e['start_datetime'].date() == event_date]

            if day_events:
                column_x = start_x + day_offset * DAY_COLUMN_WIDTH
                self._draw_day_events(draw, day_events, column_x, grid_y_start)

    def _draw_day_events(
        self,
        draw: ImageDraw.ImageDraw,
        events: List[Dict],
        column_x: int,
        grid_y_start: int
    ):
        """1日分のイベントをブロック表示"""
        # 動的レイアウト値を使用
        hour_height = self.layout['hour_height']

        positions = self._calculate_event_positions(events, DAY_COLUMN_WIDTH)

        for pos in positions:
            event = pos['event']
            if event['is_all_day']:
                continue  # 終日イベントはスキップ（簡略化のため）

            # 時刻から座標を計算
            start_hour = event['start_datetime'].hour + event['start_datetime'].minute / 60
            end_hour = event['end_datetime'].hour + event['end_datetime'].minute / 60

            # 表示範囲内かチェック
            if start_hour >= WEEK_CALENDAR_END_HOUR or end_hour <= WEEK_CALENDAR_START_HOUR:
                continue

            # 範囲をクリップ
            start_hour = max(start_hour, WEEK_CALENDAR_START_HOUR)
            end_hour = min(end_hour, WEEK_CALENDAR_END_HOUR)

            # Y座標計算（動的 hour_height を使用）
            y1 = grid_y_start + int((start_hour - WEEK_CALENDAR_START_HOUR) * hour_height)
            y2 = grid_y_start + int((end_hour - WEEK_CALENDAR_START_HOUR) * hour_height)

            # X座標（重複対応）
            block_x = column_x + pos['x_offset'] + 2
            block_width = pos['width'] - 4

            # イベントブロック描画
            color_id = event.get('color_id', '1')
            block_color = DEFAULT_EVENT_COLORS.get(color_id, DEFAULT_EVENT_COLORS['1'])

            draw.rectangle(
                [(block_x, y1), (block_x + block_width, y2)],
                fill=block_color,
                outline=(255, 255, 255),
                width=1
            )

            # タイトルを表示（スペースがあれば）
            if y2 - y1 > 20:
                title = event['summary']
                if len(title) > 10:
                    title = title[:10] + '...'
                draw.text(
                    (block_x + 4, y1 + 4),
                    title,
                    font=self.font_event_block,
                    fill=(255, 255, 255)
                )

    def _calculate_event_positions(
        self,
        events: List[Dict],
        column_width: int
    ) -> List[Dict]:
        """重複する予定の横並び配置を計算"""
        sorted_events = sorted(events, key=lambda e: e['start_datetime'])

        positions = []
        for event in sorted_events:
            # 同じ時間帯に既に配置されているイベントを探す
            overlapping = [p for p in positions if self._is_overlapping(p['event'], event)]

            # 空いている列を探す
            used_columns = set(p['column'] for p in overlapping)
            column = 0
            while column in used_columns:
                column += 1

            # 列数に応じてブロック幅を調整
            max_columns = max(column + 1, max((p['column'] + 1 for p in overlapping), default=1))
            block_width = column_width // max_columns

            positions.append({
                'event': event,
                'column': column,
                'width': block_width,
                'x_offset': column * block_width
            })

        return positions

    def _is_overlapping(self, event1: Dict, event2: Dict) -> bool:
        """2つのイベントが時間的に重複しているか判定"""
        return (event1['start_datetime'] < event2['end_datetime'] and
                event2['start_datetime'] < event1['end_datetime'])

    @staticmethod
    def _get_japanese_weekday(weekday: int) -> str:
        """曜日番号を日本語に変換"""
        weekdays = ['月', '火', '水', '木', '金', '土', '日']
        return weekdays[weekday]
