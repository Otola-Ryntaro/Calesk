# チケット014: 現在時刻表示 - 蛍光色で時間帯塗りつぶし

## 概要

週間カレンダーの現在時刻を、蛍光色の黄色で1時間枠を塗りつぶして表示する。
既存の赤い矢印に加えて、より目立つ視覚的な強調を追加。

## 現状

- 赤い線 + 三角形の矢印（`_draw_current_time_arrow()`）
- 矢印が小さく見にくい

## 実装方法

### 蛍光塗りつぶし

1. 現在時刻が含まれる1時間枠を特定（例: 15:00-16:00）
2. 今日の列のその時間帯を蛍光黄色 `(255, 255, 100, 60)` で塗りつぶし
3. 既存の赤い線も残す（蛍光塗り + 赤線の組合せ）

### `_draw_current_time_arrow()` の拡張

```python
def _draw_current_time_highlight(self, draw, start_x, total_width,
                                  grid_y_start, hour_height):
    now = datetime.now()
    if not (WEEK_CALENDAR_START_HOUR <= now.hour <= WEEK_CALENDAR_END_HOUR):
        return

    # 1. 現在の1時間枠を蛍光色で塗りつぶし（今日の列のみ）
    current_hour = now.hour
    slot_y_start = grid_y_start + (current_hour - WEEK_CALENDAR_START_HOUR) * hour_height
    slot_y_end = slot_y_start + hour_height
    today_column_x = start_x  # 今日は最初の列

    highlight_color = self.theme.get('current_time_highlight',
                                      (255, 255, 100, 60))
    draw.rectangle(
        [(today_column_x, slot_y_start),
         (today_column_x + DAY_COLUMN_WIDTH, slot_y_end)],
        fill=highlight_color
    )

    # 2. 赤い線（現在時刻の正確な位置）
    now_y = grid_y_start + (now.hour - WEEK_CALENDAR_START_HOUR + now.minute / 60) * hour_height
    draw.line(
        [(start_x, now_y), (start_x + total_width, now_y)],
        fill=(255, 59, 48), width=2
    )
```

### テーマ拡張

`themes.py` に `current_time_highlight` を追加:

```python
'simple': { 'current_time_highlight': (255, 255, 100, 60) },  # 薄い蛍光黄
'dark':   { 'current_time_highlight': (255, 200, 50, 40) },   # ダーク用
```

## タスク

- [x] `_draw_current_time_arrow()` を `_draw_current_time_highlight()` にリネーム・拡張 ✅
- [x] 1時間枠の蛍光塗りつぶし描画を実装 ✅
- [x] 赤い線を維持（蛍光塗り + 赤線の組合せ） ✅
- [x] `themes.py` に `current_time_highlight` 色を追加 ✅
- [x] テスト追加 ✅
- [x] 視覚確認 ✅

## 変更ファイル

- `src/image_generator.py` - 描画ロジック変更
- `src/themes.py` - ハイライト色追加

## 依存関係

- チケット018（自動更新）と連携（1時間ごとに更新されることでハイライト位置が移動）

## 優先度: MEDIUM
## 工数: 小（1時間）
