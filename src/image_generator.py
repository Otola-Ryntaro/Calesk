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
    BACKGROUND_IMAGE_PATH
)

logger = logging.getLogger(__name__)


class ImageGenerator:
    """壁紙画像生成クラス（新デザイン対応）"""

    def __init__(self):
        self.system = platform.system()
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

        # カレンダー用の残り高さを計算
        remaining_height = IMAGE_HEIGHT - desktop_h - card_h - spacing_top - spacing_middle - header_h

        # 1時間あたりの高さ（動的）
        hour_height = remaining_height // total_hours

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

    def generate_wallpaper(
        self,
        today_events: List[Dict],
        week_events: List[Dict]
    ) -> Optional[Path]:
        """壁紙画像を生成"""
        try:
            # 背景画像の読み込みまたは透明背景の作成
            if BACKGROUND_IMAGE_PATH and Path(BACKGROUND_IMAGE_PATH).exists():
                # 背景画像を読み込んでリサイズ
                logger.info(f"背景画像を読み込んでいます: {BACKGROUND_IMAGE_PATH}")
                background = Image.open(BACKGROUND_IMAGE_PATH)
                background = background.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)
                # RGBモードに変換（透明度を削除）
                if background.mode == 'RGBA':
                    rgb_background = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), (255, 255, 255))
                    rgb_background.paste(background, mask=background.split()[3])
                    image = rgb_background
                else:
                    image = background.convert('RGB')
            else:
                # 透明背景
                logger.info("透明背景で画像を生成します")
                image = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (255, 255, 255, 0))

            draw = ImageDraw.Draw(image)

            # 動的レイアウト値を使用
            card_y_start = self.layout['card_y_start']
            week_calendar_y_start = self.layout['week_calendar_y_start']

            # 予定カード描画
            self._draw_event_cards(draw, week_events, card_y_start)

            # 週間カレンダー描画
            self._draw_week_calendar(draw, week_events, week_calendar_y_start)

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
        start_x = (IMAGE_WIDTH - total_width) // 2

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
        # カード背景（白塗り + 薄いグレーの枠）
        draw.rectangle(
            [(x, y), (x + CARD_WIDTH, y + CARD_HEIGHT)],
            fill=(255, 255, 255, 255),
            outline=(200, 200, 200),
            width=2
        )

        # 日付ラベル
        draw.text(
            (x + CARD_PADDING, y + CARD_PADDING),
            label,
            font=self.font_card_date,
            fill=TEXT_COLOR
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
                    fill=TEXT_COLOR
                )

                # タイトル
                title = event['summary']
                if len(title) > 18:
                    title = title[:18] + '...'
                draw.text(
                    (text_x, current_y + FONT_SIZE_CARD_TIME + 2),
                    title,
                    font=self.font_card_title,
                    fill=TEXT_COLOR
                )

                # 場所（スペースがあれば）
                if event.get('location') and i < 2:  # 最初の2件のみ場所表示
                    location = event['location']
                    if len(location) > 15:
                        location = location[:15] + '...'
                    draw.text(
                        (text_x, current_y + FONT_SIZE_CARD_TIME + FONT_SIZE_CARD_TITLE + 4),
                        f"@ {location}",
                        font=self.font_card_location,
                        fill=(100, 100, 100)
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
        # カレンダーの幅と開始位置
        total_width = DAY_COLUMN_WIDTH * 7
        start_x = (IMAGE_WIDTH - total_width) // 2

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
                fill=TEXT_COLOR,
                align='center'
            )

        # 動的レイアウト値を使用
        header_height = self.layout['header_height']
        grid_y_start = self.layout['grid_y_start']

        # カレンダーグリッドの白背景
        draw.rectangle(
            [(start_x, grid_y_start), (start_x + total_width, grid_y_start + calendar_height)],
            fill=(255, 255, 255, 255)
        )

        # グリッド線（横線：時間軸）
        for hour in range(total_hours + 1):
            y = grid_y_start + hour * hour_height
            draw.line(
                [(start_x, y), (start_x + total_width, y)],
                fill=(220, 220, 220),
                width=1
            )

            # 時間ラベル
            if hour < total_hours:
                hour_value = WEEK_CALENDAR_START_HOUR + hour
                draw.text(
                    (start_x - 45, y + 5),
                    f"{hour_value:02d}:00",
                    font=self.font_hour_label,
                    fill=(120, 120, 120)
                )

        # グリッド線（縦線：曜日）
        for i in range(8):
            x = start_x + i * DAY_COLUMN_WIDTH
            draw.line(
                [(x, grid_y_start), (x, grid_y_start + calendar_height)],
                fill=(220, 220, 220),
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
