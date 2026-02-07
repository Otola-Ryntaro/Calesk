# チケット015: 日をまたぐ予定の横バー表示

## 概要

複数日にわたる予定（終日イベント含む）を、週間カレンダー上部に横バーで表示する。
参考: `Screenshots/スクリーンショット 2026-02-07 午後3.14.55.png`

## 現状の問題

- 終日イベントは `_draw_day_events()` でスキップされている（`if event.is_all_day: continue`）
- 複数日にわたるイベントは各日に個別表示されるのみ
- 参考画像のような横バー（日をまたいで伸びる）がない

## 実装方法

### 週間カレンダー構造の拡張

```
| 曜日ヘッダー |  Wed  |  Thu  |  Fri  |  Sat  |  Sun  |  Mon  |  Tue  |
|============|=======|=======|=======|=======|=======|=======|=======|
| ██████████ 冬休み ███████████████████████████████████████ |       |
| ████████ 会議 ██████████████ |       |       |       |       |       |
|------------|-------|-------|-------|-------|-------|-------|-------|
| 08:00      |       |       |       |       |       |       |       |
| 09:00      |       |  ██   |       |       |       |       |       |
| ...        |       |       |       |       |       |       |       |
```

### 複数日イベントの検出

```python
def _get_multi_day_events(self, events, today):
    """複数日/終日イベントを抽出"""
    multi_day = []
    for event in events:
        if event.is_all_day:
            multi_day.append(event)
        elif (event.end_datetime.date() - event.start_datetime.date()).days >= 1:
            multi_day.append(event)
    return multi_day
```

### 横バー描画

```python
def _draw_multi_day_event_bars(self, draw, events, start_x, y_start, today):
    """複数日イベントを横バーで描画"""
    bar_height = 18
    bar_margin = 2
    current_y = y_start

    for event in events[:3]:  # 最大3行
        # 開始日と終了日の列を特定
        start_col = max(0, (event.start_datetime.date() - today).days)
        end_col = min(6, (event.end_datetime.date() - today).days)

        # 横バーを描画
        bar_x_start = start_x + start_col * DAY_COLUMN_WIDTH + 2
        bar_x_end = start_x + (end_col + 1) * DAY_COLUMN_WIDTH - 2

        color = self._get_event_color(event)
        draw.rectangle(
            [(bar_x_start, current_y), (bar_x_end, current_y + bar_height)],
            fill=color
        )

        # タイトル
        draw.text(
            (bar_x_start + 4, current_y + 2),
            event.summary[:15],
            font=self.font_event_block,
            fill=(255, 255, 255)
        )

        current_y += bar_height + bar_margin
```

### レイアウト調整

- 横バー行のスペース確保: グリッド開始位置を下にずらす
- 最大3行分のスペース（約60px）を確保
- 複数日イベントがない場合はスペースを確保しない

## タスク

- [x] `_get_multi_day_events()` メソッドを実装 ✅
- [x] `_draw_multi_day_event_bars()` メソッドを実装 ✅
- [x] `_draw_week_calendar()` のレイアウト調整（横バー行のスペース確保） ✅
- [x] `_draw_day_events()` で終日イベントのスキップ処理を維持 ✅
- [x] イベント色の取得を共通化 ✅
- [x] テスト追加（複数日イベントの描画テスト） ✅
- [x] 視覚確認 ✅

## 変更ファイル

- `src/image_generator.py` - 横バー描画ロジック、レイアウト調整

## 依存関係

- CalendarClient.get_week_events() は既に複数日イベントを返しているため変更不要

## 優先度: MEDIUM
## 工数: 中〜大（4-6時間）
