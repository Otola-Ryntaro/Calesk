# チケット013: 進行中イベントの強調強化

## 概要

現在進行中のイベントカードを、カード色・枠色・文字色の変更で強調表示する。
既存のプログレスバーに加えて、より目立つ視覚的な強調を追加。

## 現状

- プログレスバー（青→緑グラデーション）のみ
- カード自体の見た目は通常イベントと同じ

## 実装方法

### 進行中イベントの判定

```python
is_in_progress = (not event.is_all_day and
                  event.start_datetime <= now <= event.end_datetime)
```

### 強調表示の内容

| 要素 | 通常時 | 進行中 |
|---|---|---|
| カード背景色 | テーマの `card_bg` | テーマの `active_card_bg` |
| カード枠線色 | テーマの `card_border` | `(220, 50, 50)` 赤系 |
| カード枠線幅 | テーマの `card_border_width` | 3px |
| テキスト色 | テーマの `text_color` | テーマの `active_text_color` |
| プログレスバー | 現状維持 | 現状維持 |

### テーマ拡張

`themes.py` に各テーマごとの進行中スタイルを追加:

```python
'simple': {
    ...
    'active_card_bg': (255, 245, 245),      # 薄い赤
    'active_card_border': (220, 50, 50),     # 赤枠
    'active_card_border_width': 3,
    'active_text_color': (180, 30, 30),      # 濃い赤
},
'dark': {
    ...
    'active_card_bg': (80, 30, 30),          # ダーク赤
    'active_card_border': (255, 80, 80),     # 明るい赤枠
    'active_card_border_width': 3,
    'active_text_color': (255, 200, 200),    # 薄いピンク
},
```

## タスク

- [x] `themes.py` に `active_card_bg`, `active_card_border`, `active_card_border_width`, `active_text_color` を全テーマに追加 ✅
- [x] `_draw_single_event_card()` に進行中判定と強調描画を実装 ✅
- [x] `_draw_compact_event_card()`（チケット012で新規作成）にも同様の強調を適用 ✅
- [x] テスト追加 ✅
- [x] 各テーマで視覚確認 ✅

## 変更ファイル

- `src/themes.py` - 進行中スタイル追加
- `src/image_generator.py` - 強調描画ロジック

## 依存関係

- チケット012（3列レイアウト）のコンパクトカードにも適用

## 優先度: MEDIUM
## 工数: 小（1-2時間）
