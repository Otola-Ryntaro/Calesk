# チケット011: Weekly Calendar 時刻ラベルの視認性改善

## 概要

背景画像上で週間カレンダーの時刻ラベル（08:00, 09:00...）が見えない問題を解決する。
複数の視認性改善手法を実装し、設定で選択可能にする。

## 現状の問題

- 時刻ラベルが `text_color`（simpleテーマ: 黒）で直接描画されている
- 暗い背景画像では完全に見えない
- `src/image_generator.py:674` の `draw.text()` が該当

## 実装方法

### 方法A: 半透明背景（2パターン）

#### A-1: ラベル部分のみ半透明背景
- 各時刻ラベルの背後に小さな半透明矩形を描画
- 最小限の視覚的変更で済む

#### A-2: カレンダー全体に半透明背景
- カード全体およびカレンダーグリッド全体の背景に半透明レイヤーを追加
- より統一的な見た目になるが、背景画像が見えにくくなる

#### 選択方式
- `config.py` に `LABEL_VISIBILITY_MODE` を追加
  - `'label_bg'`: ラベル部分のみ半透明背景（A-1）
  - `'full_bg'`: 全体的に半透明背景（A-2）
  - `'outline'`: アウトライン付きテキスト（C）
  - `'none'`: エフェクトなし

### 方法B: テーマ別ラベル色
- `themes.py` に `hour_label_color` と `hour_label_bg` を追加
- テーマごとに最適な色を設定

### 方法C: アウトライン付きテキスト（stroke）
- Pillow 10.0+ の `stroke_width` / `stroke_fill` パラメータを使用
- テキストに白いアウトラインを追加

## タスク

- [x] `config.py` に `LABEL_VISIBILITY_MODE` 設定を追加 ✅
- [x] `themes.py` に `hour_label_color`, `hour_label_bg` を各テーマに追加 ✅
- [x] `image_generator.py` の `_draw_week_calendar()` に半透明背景描画を実装（A-1, A-2） ✅
- [x] アウトライン付きテキスト描画を実装（C） ✅
- [x] 設定に応じた描画切り替えロジック実装 ✅
- [x] テスト追加（18テスト） ✅
- [x] 各テーマで視覚確認 ✅

## 変更ファイル

- `src/config.py` - 設定値追加
- `src/themes.py` - テーマ別ラベル色追加
- `src/image_generator.py` - 描画ロジック変更

## 優先度: HIGH
## 工数: 小（2-3時間）
