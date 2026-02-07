"""
カード描画Mixin
Zenモード、Heroモード、コンパクトカード、シングルカード、空カード
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from PIL import Image, ImageDraw

from ..models.event import CalendarEvent
from ..config import (
    CARD_WIDTH, CARD_HEIGHT, CARD_MARGIN, CARD_PADDING,
    FONT_SIZE_CARD_DATE, FONT_SIZE_CARD_TITLE,
    COMPACT_CARD_WIDTH, COMPACT_CARD_HEIGHT, COMPACT_CARD_MARGIN, COMPACT_CARD_PADDING,
    MAX_CARDS_PER_COLUMN, COLUMN_HEADER_HEIGHT, COLUMN_GAP,
    CARD_SHADOW_ENABLED,
)


class CardRendererMixin:
    """カード描画Mixin"""

    def _get_events_for_days(self, all_events: List[CalendarEvent]) -> Dict[str, List[CalendarEvent]]:
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
            event_date = event.start_datetime.date()
            if event_date == today:
                result['today'].append(event)
            elif event_date == tomorrow:
                result['tomorrow'].append(event)
            elif event_date == day_after:
                result['day_after'].append(event)

        # 各日の予定を時刻順にソート
        for key in result:
            result[key].sort(key=lambda e: e.start_datetime)

        return result

    def _select_layout_mode(self, today_event_count: int) -> str:
        """イベント数に応じたレイアウトモードを選択

        Args:
            today_event_count: 今日のイベント数

        Returns:
            str: レイアウトモード ('zen', 'hero', 'card', 'compact')
        """
        if today_event_count == 0:
            return 'zen'
        elif today_event_count == 1:
            return 'hero'
        elif today_event_count <= 3:
            return 'card'
        else:
            return 'compact'

    def _draw_zen_mode(
        self,
        draw: ImageDraw.ImageDraw,
        y_start: int,
        image: Image.Image = None
    ):
        """予定なし時のZenモード描画

        中央に美しい「予定なし」メッセージを表示。
        """
        text_color = self.theme.get('text_color', (0, 0, 0))
        accent = self.theme.get('accent_color', (100, 100, 100))

        center_x = self.width // 2
        y = y_start + 40

        # メインメッセージ
        main_text = '今日は予定なし'
        bbox = draw.textbbox((0, 0), main_text, font=self.font_card_time_bold)
        text_w = bbox[2] - bbox[0]
        self._draw_chromatic_text(
            draw, main_text,
            (center_x - text_w // 2, y),
            self.font_card_time_bold, text_color
        )

        # サブテキスト
        y += 40
        sub_text = 'Time for yourself'
        bbox_sub = draw.textbbox((0, 0), sub_text, font=self.font_card_location)
        sub_w = bbox_sub[2] - bbox_sub[0]
        sub_color = accent if accent else (150, 150, 150)
        draw.text(
            (center_x - sub_w // 2, y),
            sub_text,
            font=self.font_card_location,
            fill=sub_color
        )

        # 装飾ライン
        y += 30
        line_w = 120
        if accent:
            draw.line(
                [(center_x - line_w // 2, y), (center_x + line_w // 2, y)],
                fill=accent, width=2
            )

    def _draw_hero_mode(
        self,
        draw: ImageDraw.ImageDraw,
        event: CalendarEvent,
        y_start: int,
        image: Image.Image = None
    ):
        """1件のイベントをHeroモードで大きく表示

        大きなカード + カウントダウンを表示。
        """
        text_color = self.theme.get('text_color', (0, 0, 0))
        card_bg = self.theme.get('card_bg', (255, 255, 255))
        card_alpha = self.theme.get('card_alpha', 255)
        card_radius = self.theme.get('card_radius', 0)
        glass_effect = self.theme.get('glass_effect', False)

        # ヒーローカードのサイズ（画面幅の60%、高さ160px）
        hero_width = int(self.width * 0.6)
        hero_height = 160
        hero_x = (self.width - hero_width) // 2
        hero_y = y_start + 10

        # 進行中判定
        now = datetime.now()
        is_in_progress = (
            not event.is_all_day
            and event.start_datetime <= now <= event.end_datetime
        )

        is_finished = (
            not event.is_all_day
            and event.end_datetime < now
        )

        if is_in_progress:
            card_bg = self.theme.get('active_card_bg', (255, 245, 245))
            text_color = self.theme.get('active_text_color', (180, 30, 30))
        elif is_finished:
            card_bg = tuple(min(c + 80, 255) for c in card_bg[:3])
            card_alpha = max(card_alpha - 50, 100)
            text_color = tuple(min(c + 100, 200) for c in text_color[:3])

        # カード背景
        if glass_effect and image is not None:
            self._draw_glass_card(
                draw, image, hero_x, hero_y,
                hero_width, hero_height,
                radius=card_radius
            )
        else:
            self._draw_card_background(
                draw, hero_x, hero_y, hero_width, hero_height,
                card_bg=card_bg, card_alpha=card_alpha,
                card_border=self.theme.get('card_border', (200, 200, 200)),
                card_border_width=self.theme.get('card_border_width', 1),
                card_radius=card_radius
            )

        # カラーバー（左端、大きめ）
        bar_color = self._get_event_color(event.color_id)
        draw.rectangle(
            [(hero_x + 12, hero_y + 15),
             (hero_x + 18, hero_y + hero_height - 15)],
            fill=bar_color
        )

        # 時刻（大きく）
        content_x = hero_x + 30
        if event.is_all_day:
            time_text = '終日'
        else:
            time_text = event.start_datetime.strftime('%H:%M')

        self._draw_chromatic_text(
            draw, time_text,
            (content_x, hero_y + 20),
            self.font_card_time_bold, text_color
        )

        # タイトル
        title = event.summary
        if len(title) > 40:
            title = title[:40] + '...'
        draw.text(
            (content_x, hero_y + 55),
            title,
            font=self.font_card_title,
            fill=text_color
        )

        # カウントダウン / ステータス
        if is_in_progress:
            remaining = event.end_datetime - now
            mins = int(remaining.total_seconds() // 60)
            status_text = f'進行中 - 残り{mins}分'
        elif event.is_all_day:
            status_text = '終日イベント'
        else:
            until = event.start_datetime - now
            total_mins = int(until.total_seconds() // 60)
            if total_mins < 0:
                status_text = '終了済み'
            elif total_mins < 60:
                status_text = f'あと{total_mins}分で開始'
            else:
                hours = total_mins // 60
                mins = total_mins % 60
                status_text = f'あと{hours}時間{mins}分で開始'

        accent = self.theme.get('accent_color', (100, 100, 100))
        draw.text(
            (content_x, hero_y + 90),
            status_text,
            font=self.font_card_location,
            fill=accent if accent else text_color
        )

        # 進行中の場合はプログレスバー
        if is_in_progress:
            self._draw_event_progress_bar(
                draw, event,
                hero_x + 12, hero_y,
                hero_width - 24,
                card_height=hero_height
            )

    def _draw_event_cards(
        self,
        draw: ImageDraw.ImageDraw,
        today_events: List[CalendarEvent],
        y_start: int,
        week_events: List[CalendarEvent] = None,
        image: Image.Image = None
    ):
        """今日・明日・明後日の予定を動的レイアウトで描画"""
        now = datetime.now()

        # 今日のイベント数でレイアウトモードを決定
        today_count = len(today_events)
        mode = self._select_layout_mode(today_count)

        if mode == 'zen':
            self._draw_zen_mode(draw, y_start, image)
            return
        elif mode == 'hero':
            self._draw_hero_mode(draw, today_events[0], y_start, image)
            return

        # week_events がある場合は3日分に振り分け
        if week_events:
            days = self._get_events_for_days(week_events)
        else:
            days = {
                'today': sorted(today_events, key=lambda e: e.start_datetime),
                'tomorrow': [],
                'day_after': []
            }

        column_labels = [
            ('today', '今日の予定'),
            ('tomorrow', '明日の予定'),
            ('day_after', '明後日の予定')
        ]

        # 3列全体の幅を計算して中央配置
        total_width = COMPACT_CARD_WIDTH * 3 + COLUMN_GAP * 2
        start_x = (self.width - total_width) // 2

        text_color = self.theme.get('text_color', (0, 0, 0))

        # 列ヘッダー領域に半透明背景を描画
        header_bg = self.theme.get('header_bg')
        if image is not None and header_bg:
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            pad = 6
            overlay_draw.rounded_rectangle(
                [(start_x - pad, y_start - pad),
                 (start_x + total_width + pad, y_start + COLUMN_HEADER_HEIGHT)],
                radius=self.theme.get('card_radius', 0),
                fill=header_bg
            )
            image.alpha_composite(overlay)
            draw = ImageDraw.Draw(image)

        for col_idx, (day_key, label) in enumerate(column_labels):
            col_x = start_x + col_idx * (COMPACT_CARD_WIDTH + COLUMN_GAP)
            events = days[day_key]

            # 列ヘッダー描画（Boldフォント使用）
            draw.text(
                (col_x, y_start),
                label,
                font=self.font_card_time_bold,
                fill=text_color
            )

            card_y = y_start + COLUMN_HEADER_HEIGHT

            if not events:
                # 予定なしの場合は小さなテキスト表示
                draw.text(
                    (col_x + 10, card_y + 10),
                    '予定なし',
                    font=self.font_card_location,
                    fill=(180, 180, 180)
                )
                continue

            # 最大件数分のカードを描画
            for i, event in enumerate(events[:MAX_CARDS_PER_COLUMN]):
                is_finished = False
                is_in_progress = False
                if not event.is_all_day:
                    is_finished = event.end_datetime < now
                    is_in_progress = (event.start_datetime <= now <= event.end_datetime)

                self._draw_compact_event_card(
                    draw, event,
                    col_x, card_y,
                    is_finished=is_finished,
                    is_in_progress=is_in_progress,
                    image=image
                )
                card_y += COMPACT_CARD_HEIGHT + COMPACT_CARD_MARGIN

            # 表示しきれない件数がある場合
            remaining = len(events) - MAX_CARDS_PER_COLUMN
            if remaining > 0:
                draw.text(
                    (col_x + 10, card_y + 2),
                    f'+{remaining}件',
                    font=self.font_card_location,
                    fill=text_color
                )

    def _draw_compact_event_card(
        self,
        draw: ImageDraw.ImageDraw,
        event: CalendarEvent,
        x: int,
        y: int,
        is_finished: bool = False,
        is_in_progress: bool = False,
        image: Image.Image = None
    ):
        """コンパクトな1行カードを描画（3列レイアウト用）"""
        card_bg = self.theme.get('card_bg', (255, 255, 255))
        card_alpha = self.theme.get('card_alpha', 255)
        card_border = self.theme.get('card_border', (200, 200, 200))
        card_border_width = self.theme.get('card_border_width', 1)
        card_radius = self.theme.get('card_radius', 0)
        text_color = self.theme.get('text_color', (0, 0, 0))
        glass_effect = self.theme.get('glass_effect', False)

        # 進行中イベントの強調
        if is_in_progress:
            card_bg = self.theme.get('active_card_bg', (255, 245, 245))
            card_border = self.theme.get('active_card_border', (220, 50, 50))
            card_border_width = self.theme.get('active_card_border_width', 3)
            text_color = self.theme.get('active_text_color', (180, 30, 30))
            glass_effect = False  # 進行中カードはガラス効果なし
        elif is_finished:
            card_bg = tuple(min(c + 80, 255) for c in card_bg[:3])
            card_alpha = max(card_alpha - 50, 100)
            text_color = tuple(min(c + 100, 200) for c in text_color[:3])
            glass_effect = False  # 終了済みカードはガラス効果なし

        # ガラスモーフィズムカード背景
        if glass_effect and image is not None:
            self._draw_glass_card(
                draw, image, x, y,
                COMPACT_CARD_WIDTH, COMPACT_CARD_HEIGHT,
                radius=min(card_radius, 8)
            )
        else:
            self._draw_card_background(
                draw, x, y, COMPACT_CARD_WIDTH, COMPACT_CARD_HEIGHT,
                card_bg=card_bg, card_alpha=card_alpha,
                card_border=card_border, card_border_width=card_border_width,
                card_radius=min(card_radius, 8)
            )

        # カラーバー（左端、縦方向）
        color_id = event.color_id
        bar_color = self._get_event_color(color_id)

        if is_finished:
            bar_color = tuple(min(c + 80, 255) for c in bar_color)

        bar_x = x + COMPACT_CARD_PADDING
        draw.rectangle(
            [(bar_x, y + 5), (bar_x + 3, y + COMPACT_CARD_HEIGHT - 5)],
            fill=bar_color
        )

        # 時刻テキスト
        text_x = bar_x + 8
        if event.is_all_day:
            time_text = '終日'
        else:
            time_text = event.start_datetime.strftime('%H:%M')

        self._draw_chromatic_text(
            draw, time_text,
            (text_x, y + COMPACT_CARD_PADDING),
            self.font_card_time_bold, text_color
        )

        # タイトル（時刻の右に配置）
        title_x = text_x + 45
        title = event.summary
        max_len = 15
        if len(title) > max_len:
            title = title[:max_len] + '..'

        draw.text(
            (title_x, y + COMPACT_CARD_PADDING),
            title,
            font=self.font_card_title,
            fill=text_color
        )

        # 終了済みバッジ
        if is_finished:
            badge_x = x + COMPACT_CARD_WIDTH - COMPACT_CARD_PADDING - 25
            badge_y = y + COMPACT_CARD_PADDING
            draw.rectangle(
                [(badge_x, badge_y), (badge_x + 22, badge_y + 14)],
                fill=(180, 180, 180, 200)
            )
            draw.text(
                (badge_x + 2, badge_y + 1),
                "終了",
                font=self.font_event_block,
                fill=(255, 255, 255)
            )

    def _draw_single_event_card(
        self,
        draw: ImageDraw.ImageDraw,
        event: CalendarEvent,
        x: int,
        y: int,
        is_finished: bool = False,
        is_in_progress: bool = False
    ):
        """1つのイベントを1枚のカードに描画"""
        # テーマから色と設定を取得
        card_bg = self.theme.get('card_bg', (255, 255, 255))
        card_alpha = self.theme.get('card_alpha', 255)
        card_border = self.theme.get('card_border', (200, 200, 200))
        card_border_width = self.theme.get('card_border_width', 1)
        card_radius = self.theme.get('card_radius', 0)
        card_shadow = self.theme.get('card_shadow', False)
        text_color = self.theme.get('text_color', (0, 0, 0))

        # 進行中イベントの強調
        if is_in_progress:
            card_bg = self.theme.get('active_card_bg', (255, 245, 245))
            card_border = self.theme.get('active_card_border', (220, 50, 50))
            card_border_width = self.theme.get('active_card_border_width', 3)
            text_color = self.theme.get('active_text_color', (180, 30, 30))
        # 終了済みの場合、背景色を薄くする
        elif is_finished:
            # 背景色をグレーアウト（元の色に対して50%の明度）
            card_bg = tuple(min(c + 80, 255) for c in card_bg[:3])
            card_alpha = max(card_alpha - 50, 100)  # 透明度を上げる
            text_color = tuple(min(c + 100, 200) for c in text_color[:3])  # テキストも薄くする

        # カードの影を描画（終了済みでない場合のみ）
        if CARD_SHADOW_ENABLED and card_shadow and not is_finished:
            self._draw_card_shadow(draw, x, y, CARD_WIDTH, CARD_HEIGHT, card_radius)

        # カード背景
        self._draw_card_background(
            draw, x, y, CARD_WIDTH, CARD_HEIGHT,
            card_bg=card_bg, card_alpha=card_alpha,
            card_border=card_border, card_border_width=card_border_width,
            card_radius=card_radius
        )

        # 時刻表示
        current_y = y + CARD_PADDING

        if event.is_all_day:
            time_text = '終日'
        else:
            time_text = event.start_datetime.strftime('%H:%M')

        self._draw_chromatic_text(
            draw, time_text,
            (x + CARD_PADDING, current_y),
            self.font_card_time_bold, text_color
        )

        current_y += FONT_SIZE_CARD_DATE + 10

        # カラーバー
        color_id = event.color_id
        bar_color = self._get_event_color(color_id)

        # 終了済みの場合、カラーバーも薄くする
        if is_finished:
            bar_color = tuple(min(c + 80, 255) for c in bar_color)

        draw.rectangle(
            [(x + CARD_PADDING, current_y), (x + CARD_PADDING + 3, y + CARD_HEIGHT - CARD_PADDING - 10)],
            fill=bar_color
        )

        text_x = x + CARD_PADDING + 10

        # タイトル
        title = event.summary
        max_title_length = 22
        if len(title) > max_title_length:
            title = title[:max_title_length] + '...'

        draw.text(
            (text_x, current_y),
            title,
            font=self.font_card_title,
            fill=text_color
        )

        current_y += FONT_SIZE_CARD_TITLE + 5

        # 場所
        if event.location:
            location = event.location
            max_location_length = 20
            if len(location) > max_location_length:
                location = location[:max_location_length] + '...'

            location_color = tuple(min(c + 50, 255) for c in text_color[:3])
            draw.text(
                (text_x, current_y),
                f"@ {location}",
                font=self.font_card_location,
                fill=location_color
            )

        # 終了済みの場合、「終了」バッジを表示
        if is_finished:
            badge_text = "終了"
            badge_x = x + CARD_WIDTH - CARD_PADDING - 35
            badge_y = y + CARD_PADDING
            badge_bg = (180, 180, 180, 200)

            draw.rectangle(
                [(badge_x, badge_y), (badge_x + 30, badge_y + 18)],
                fill=badge_bg
            )
            draw.text(
                (badge_x + 3, badge_y + 2),
                badge_text,
                font=self.font_card_location,
                fill=(255, 255, 255)
            )

        # 進行中の場合、プログレスバーを表示
        if not is_finished:
            self._draw_event_progress_bar(
                draw,
                event,
                x + CARD_PADDING,
                y,
                CARD_WIDTH - CARD_PADDING * 2
            )

    def _draw_empty_card(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int
    ):
        """予定なしカードを描画"""
        # テーマから色と設定を取得
        card_bg = self.theme.get('card_bg', (255, 255, 255))
        card_alpha = self.theme.get('card_alpha', 255)
        card_border = self.theme.get('card_border', (200, 200, 200))
        card_border_width = self.theme.get('card_border_width', 1)
        card_radius = self.theme.get('card_radius', 0)
        card_shadow = self.theme.get('card_shadow', False)

        # カードの影を描画
        if CARD_SHADOW_ENABLED and card_shadow:
            self._draw_card_shadow(draw, x, y, CARD_WIDTH, CARD_HEIGHT, card_radius)

        # カード背景（共通メソッド使用）
        self._draw_card_background(
            draw, x, y, CARD_WIDTH, CARD_HEIGHT,
            card_bg=card_bg, card_alpha=card_alpha,
            card_border=card_border, card_border_width=card_border_width,
            card_radius=card_radius
        )

        # 「予定なし」テキスト
        text_y = y + CARD_HEIGHT // 2 - 10
        draw.text(
            (x + CARD_WIDTH // 2 - 40, text_y),
            '今日の予定なし',
            font=self.font_card_title,
            fill=(150, 150, 150)
        )
