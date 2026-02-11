"""
週間カレンダー描画Mixin
週間グリッド、時刻ラベル、イベントブロック、複数日イベントバー、イベント配置計算
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

from PIL import Image, ImageDraw

from ..models.event import CalendarEvent
from ..config import (
    DAY_COLUMN_WIDTH,
    WEEK_CALENDAR_START_HOUR, WEEK_CALENDAR_END_HOUR,
    DEFAULT_EVENT_COLORS,
    LABEL_VISIBILITY_MODE,
)


class CalendarRendererMixin:
    """週間カレンダー描画Mixin"""

    def _draw_hour_label(
        self,
        draw: ImageDraw.ImageDraw,
        image: Image.Image,
        x: int,
        y: int,
        text: str,
        mode: str = None
    ):
        """
        時刻ラベルを指定モードで描画

        Args:
            draw: ImageDraw オブジェクト
            image: 画像オブジェクト（半透明合成用）
            x: X座標
            y: Y座標
            text: ラベルテキスト（例: "08:00"）
            mode: 描画モード（None の場合は設定値を使用）
        """
        if mode is None:
            mode = LABEL_VISIBILITY_MODE

        label_color = self.theme.get('hour_label_color', self.theme.get('text_color', (0, 0, 0)))
        label_bg = self.theme.get('hour_label_bg', (255, 255, 255, 180))

        if mode == 'label_bg':
            # A-1: ラベル部分のみ半透明背景
            bbox = draw.textbbox((x, y), text, font=self.font_hour_label)
            pad = 3
            bg_rect = (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)

            # 半透明矩形をRGBAオーバーレイで描画（ラベル領域のみ）
            region_w = bg_rect[2] - bg_rect[0]
            region_h = bg_rect[3] - bg_rect[1]
            overlay = Image.new('RGBA', (region_w, region_h), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            label_radius = self.theme.get('hour_label_radius', 0)
            if label_radius > 0:
                overlay_draw.rounded_rectangle(
                    [(0, 0), (region_w - 1, region_h - 1)],
                    radius=label_radius, fill=label_bg
                )
            else:
                overlay_draw.rectangle(
                    [(0, 0), (region_w - 1, region_h - 1)],
                    fill=label_bg
                )
            image.alpha_composite(overlay, dest=(bg_rect[0], bg_rect[1]))
            del overlay_draw
            overlay.close()

            # テキスト描画（合成後のdrawを更新）
            draw = ImageDraw.Draw(image)
            draw.text((x, y), text, font=self.font_hour_label, fill=label_color)

        elif mode == 'outline':
            # C: アウトライン付きテキスト（Pillow 10.0+ stroke）
            # アウトライン色はラベル背景色のRGB部分を使用
            stroke_color = label_bg[:3] if len(label_bg) >= 3 else (255, 255, 255)
            draw.text(
                (x, y), text,
                font=self.font_hour_label,
                fill=label_color,
                stroke_width=2,
                stroke_fill=stroke_color
            )

        elif mode == 'none':
            # エフェクトなし
            draw.text((x, y), text, font=self.font_hour_label, fill=label_color)

        else:
            # フォールバック: label_bg と同じ
            draw.text((x, y), text, font=self.font_hour_label, fill=label_color)

    def _draw_calendar_background(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        start_x: int,
        y_start: int,
        total_width: int,
        total_height: int,
        mode: str = None
    ):
        """
        カレンダー全体の半透明背景を描画（full_bg モード用）

        Args:
            image: 画像オブジェクト
            draw: ImageDraw オブジェクト
            start_x: カレンダー開始X座標
            y_start: カレンダー開始Y座標
            total_width: カレンダー全体の幅
            total_height: カレンダー全体の高さ
            mode: 描画モード（None の場合は設定値を使用）
        """
        if mode is None:
            mode = LABEL_VISIBILITY_MODE

        if mode != 'full_bg':
            return

        label_bg = self.theme.get('hour_label_bg', (255, 255, 255, 180))
        # ラベル領域を含む余白を追加
        margin_left = 55
        pad = 5

        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(
            (start_x - margin_left - pad, y_start - pad,
             start_x + total_width + pad, y_start + total_height + pad),
            fill=label_bg
        )
        image.alpha_composite(overlay)
        del overlay_draw
        overlay.close()

    def _get_multi_day_events(
        self,
        events: List[CalendarEvent],
        today
    ) -> List[CalendarEvent]:
        """複数日にまたがるイベント・終日イベントを抽出

        Args:
            events: 全イベントリスト
            today: 基準日（date型）

        Returns:
            該当するイベントのリスト
        """
        multi_day = []
        for event in events:
            if event.is_all_day:
                multi_day.append(event)
            elif (event.end_datetime.date() - event.start_datetime.date()).days >= 1:
                multi_day.append(event)
        return multi_day

    def _draw_multi_day_event_bars(
        self,
        draw: ImageDraw.ImageDraw,
        events: List[CalendarEvent],
        start_x: int,
        y_start: int,
        today
    ) -> int:
        """複数日イベントの横バーを描画

        Args:
            draw: ImageDraw オブジェクト
            events: 複数日イベントのリスト
            start_x: 描画開始X座標
            y_start: 描画開始Y座標
            today: 基準日（date型）

        Returns:
            描画に使用した高さ（px）
        """
        max_bars = 3
        bar_height = 18
        bar_margin = 4
        total_width = DAY_COLUMN_WIDTH * 7

        display_events = events[:max_bars]
        total_height = 0

        for i, event in enumerate(display_events):
            y = y_start + i * (bar_height + bar_margin)

            # イベント色を取得
            color_id = event.color_id
            bar_color = self._get_event_color(color_id)

            # バーの開始・終了日を計算（表示範囲: today〜today+6）
            event_start = event.start_datetime.date()
            event_end = event.end_datetime.date()

            # 表示範囲にクリップ（today〜today+7）
            bar_start_day = max((event_start - today).days, 0)
            bar_end_day = min((event_end - today).days, 7)

            if bar_end_day <= bar_start_day:
                bar_end_day = bar_start_day + 1  # 最低1日分

            bar_x1 = start_x + bar_start_day * DAY_COLUMN_WIDTH + 2
            bar_x2 = start_x + bar_end_day * DAY_COLUMN_WIDTH - 2

            # 角丸バーを描画
            radius = self.theme.get('card_radius', 0)
            bar_radius = min(radius, bar_height // 2) if radius > 0 else 3
            draw.rounded_rectangle(
                [(bar_x1, y), (bar_x2, y + bar_height)],
                radius=bar_radius,
                fill=bar_color
            )

            # タイトルテキスト
            title = event.summary
            if len(title) > 15:
                title = title[:15] + '...'
            event_text_color = self.theme.get('event_text_color', (255, 255, 255))
            draw.text(
                (bar_x1 + 6, y + 2),
                title,
                font=self.font_event_block,
                fill=event_text_color
            )

            total_height = (i + 1) * (bar_height + bar_margin)

        return total_height

    def _draw_week_calendar(
        self,
        draw: ImageDraw.ImageDraw,
        all_events: List[CalendarEvent],
        y_start: int,
        image: Image.Image = None
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

        # 曜日ヘッダー領域に半透明背景を描画（2行分の高さを確保）
        header_bg = self.theme.get('header_bg')
        if image is not None and header_bg:
            header_height_px = self.layout['header_height']
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            pad = 4
            overlay_draw.rounded_rectangle(
                [(start_x - pad, y_start - pad),
                 (start_x + total_width + pad, y_start + header_height_px + pad)],
                radius=self.theme.get('card_radius', 0),
                fill=header_bg
            )
            image.alpha_composite(overlay)
            del overlay_draw
            overlay.close()
            draw = ImageDraw.Draw(image)

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
                font=self.font_day_header_bold,
                align='center'
            )
            text_width = bbox[2] - bbox[0]
            x_pos = x_center - text_width // 2

            draw.multiline_text(
                (x_pos, y_start),
                date_str,
                font=self.font_day_header_bold,
                fill=text_color,
                align='center'
            )

        # 動的レイアウト値を使用
        header_height = self.layout['header_height']
        grid_y_start = self.layout['grid_y_start']

        # 複数日イベント横バーを描画（グリッドの上部）
        multi_day_events = self._get_multi_day_events(all_events, today)
        if multi_day_events:
            bar_height = self._draw_multi_day_event_bars(
                draw, multi_day_events, start_x, grid_y_start, today
            )
            grid_y_start += bar_height

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

        # full_bg モード: カレンダー全体に半透明背景を追加
        if image is not None:
            self._draw_calendar_background(
                image, draw,
                start_x=start_x,
                y_start=grid_y_start,
                total_width=total_width,
                total_height=calendar_height
            )
            # alpha_composite後にdrawを再取得
            draw = ImageDraw.Draw(image)

        # グリッド線（横線：時間軸）
        for hour in range(total_hours + 1):
            y = grid_y_start + hour * hour_height
            draw.line(
                [(start_x, y), (start_x + total_width, y)],
                fill=grid_color,
                width=1
            )

            # 時間ラベル（視認性モードに応じた描画）
            if hour < total_hours:
                hour_value = WEEK_CALENDAR_START_HOUR + hour
                if image is not None:
                    self._draw_hour_label(
                        draw, image,
                        start_x - 45, y + 5,
                        f"{hour_value:02d}:00"
                    )
                    # alpha_composite後にdrawを再取得
                    draw = ImageDraw.Draw(image)
                else:
                    # imageが渡されない場合はフォールバック
                    label_color = self.theme.get('hour_label_color', text_color)
                    draw.text(
                        (start_x - 45, y + 5),
                        f"{hour_value:02d}:00",
                        font=self.font_hour_label,
                        fill=label_color
                    )

        # グリッド線（縦線：曜日）
        for i in range(8):
            x = start_x + i * DAY_COLUMN_WIDTH
            draw.line(
                [(x, grid_y_start), (x, grid_y_start + calendar_height)],
                fill=grid_color,
                width=1
            )

        # 現在時刻の蛍光ハイライトを描画（イベントブロックの前に描画して背面に配置）
        self._draw_current_time_arrow(
            draw,
            start_x,
            start_x + total_width,
            grid_y_start,
            hour_height,
            image=image
        )
        # alpha_composite後にdrawを再取得
        if image is not None:
            draw = ImageDraw.Draw(image)

        # イベントブロックを描画
        for day_offset in range(7):
            event_date = today + timedelta(days=day_offset)
            day_events = [e for e in all_events if e.start_datetime.date() == event_date]

            if day_events:
                column_x = start_x + day_offset * DAY_COLUMN_WIDTH
                self._draw_day_events(draw, day_events, column_x, grid_y_start)

    def _draw_day_events(
        self,
        draw: ImageDraw.ImageDraw,
        events: List[CalendarEvent],
        column_x: int,
        grid_y_start: int
    ):
        """1日分のイベントをブロック表示"""
        # 動的レイアウト値を使用
        hour_height = self.layout['hour_height']

        positions = self._calculate_event_positions(events, DAY_COLUMN_WIDTH)

        for pos in positions:
            event = pos['event']
            if event.is_all_day:
                continue  # 終日イベントはスキップ（簡略化のため）

            # 時刻から座標を計算
            start_hour = event.start_datetime.hour + event.start_datetime.minute / 60
            end_hour = event.end_datetime.hour + event.end_datetime.minute / 60

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
            color_id = event.color_id
            block_color = self._get_event_color(color_id)

            draw.rectangle(
                [(block_x, y1), (block_x + block_width, y2)],
                fill=block_color,
                outline=(255, 255, 255),
                width=1
            )

            # タイトルを表示（スペースがあれば）
            if y2 - y1 > 20:
                title = event.summary
                if len(title) > 10:
                    title = title[:10] + '...'
                event_text_color = self.theme.get('event_text_color', (255, 255, 255))
                draw.text(
                    (block_x + 4, y1 + 4),
                    title,
                    font=self.font_event_block,
                    fill=event_text_color
                )

    def _calculate_event_positions(
        self,
        events: List[CalendarEvent],
        column_width: int
    ) -> List[Dict]:
        """
        重複する予定の横並び配置を計算

        アルゴリズム:
        1. イベントを開始時刻順にソート
        2. 重複関係に基づく連結グループを構築
        3. 各グループ内で列割り当て（貪欲法）
        4. グループ内の最大列数を確定後、幅とオフセットを一括計算
        """
        if not events:
            return []

        sorted_events = sorted(events, key=lambda e: e.start_datetime)

        # Phase 1: 重複関係の連結グループを構築
        groups = self._build_overlap_groups(sorted_events)

        # Phase 2: 各グループ内で列割り当て + 幅計算
        positions = []
        for group in groups:
            group_positions = self._assign_columns_in_group(group, column_width)
            positions.extend(group_positions)

        return positions

    def _build_overlap_groups(
        self,
        sorted_events: List[CalendarEvent]
    ) -> List[List[CalendarEvent]]:
        """
        重複関係に基づく連結グループを構築

        連結成分: イベントAとBが重複し、BとCが重複する場合、
        A, B, C は同じグループとなる。

        Args:
            sorted_events: 開始時刻順にソート済みのイベントリスト

        Returns:
            List[List[CalendarEvent]]: イベントグループのリスト
        """
        if not sorted_events:
            return []

        groups: List[List[CalendarEvent]] = []
        current_group: List[CalendarEvent] = [sorted_events[0]]

        for event in sorted_events[1:]:
            # 現在のグループ内のいずれかのイベントと重複するか判定
            overlaps_with_group = any(
                self._is_overlapping(existing, event)
                for existing in current_group
            )

            if overlaps_with_group:
                current_group.append(event)
            else:
                groups.append(current_group)
                current_group = [event]

        # 最後のグループを追加
        groups.append(current_group)

        return groups

    def _assign_columns_in_group(
        self,
        group: List[CalendarEvent],
        column_width: int
    ) -> List[Dict]:
        """
        グループ内のイベントに列を割り当て、幅とオフセットを計算

        1. 貪欲法で各イベントに列番号を割り当て
        2. グループ内の最大列数を確定
        3. 全イベントの幅とオフセットを最大列数に基づいて一括計算

        Args:
            group: 同一重複グループのイベントリスト
            column_width: 1日分の列幅

        Returns:
            List[Dict]: 各イベントの配置情報
        """
        # 列割り当て（貪欲法）
        assignments: List[Dict] = []
        for event in group:
            # このイベントと重複する既配置イベントの列を取得
            used_columns = set()
            for assigned in assignments:
                if self._is_overlapping(assigned['event'], event):
                    used_columns.add(assigned['column'])

            # 空いている最小の列番号を使用
            column = 0
            while column in used_columns:
                column += 1

            assignments.append({
                'event': event,
                'column': column,
            })

        # グループ全体の最大列数を確定
        max_columns = max(a['column'] for a in assignments) + 1

        # 幅とオフセットを一括計算
        block_width = column_width // max_columns
        positions = []
        for assignment in assignments:
            positions.append({
                'event': assignment['event'],
                'column': assignment['column'],
                'width': block_width,
                'x_offset': assignment['column'] * block_width,
            })

        return positions

    def _is_overlapping(self, event1, event2) -> bool:
        """2つのイベントが時間的に重複しているか判定"""
        return (event1.start_datetime < event2.end_datetime and
                event2.start_datetime < event1.end_datetime)

    @staticmethod
    def _get_japanese_weekday(weekday: int) -> str:
        """曜日番号を日本語に変換"""
        weekdays = ['月', '火', '水', '木', '金', '土', '日']
        return weekdays[weekday]

    def _get_event_color(self, color_id: str) -> Tuple[int, int, int]:
        """テーマに応じたイベント色を取得

        Args:
            color_id: Google Calendarのカラー ID

        Returns:
            Tuple[int, int, int]: イベント色 (R, G, B)
        """
        if 'event_colors' in self.theme:
            return self.theme['event_colors'].get(
                color_id,
                self.theme['event_colors'].get('1', DEFAULT_EVENT_COLORS['1'])
            )
        return DEFAULT_EVENT_COLORS.get(color_id, DEFAULT_EVENT_COLORS['1'])
