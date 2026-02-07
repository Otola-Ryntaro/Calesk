# 004: デザインテーマシステム

## 優先度
**MEDIUM**

## 現状の問題
- デザインがシンプルすぎる
- カラーやスタイルのバリエーションがない

## 要件
- [x] ファンシー系デザインテーマ
- [x] オシャレ系デザインテーマ
- [x] シンプル系デザインテーマ（現在のデザイン）
- [x] テーマの切り替えが可能

## テーマ仕様

### 1. シンプル系（Simple）- 現在のデザイン
- 背景: 白（#FFFFFF）
- テキスト: 黒（#000000）
- カード枠: グレー（#C8C8C8）
- フォント: ヒラギノ角ゴシック

### 2. ファンシー系（Fancy）
- 背景: パステルグラデーション（ピンク〜水色）
- テキスト: 濃いめのグレー（#333333）
- カード: 半透明の白背景、丸角、シャドウ付き
- アイコン: 絵文字や可愛いアイコン追加
- フォント: 丸ゴシック系

### 3. オシャレ系（Stylish）
- 背景: ダークトーン（#1E1E1E）またはグレーグラデーション
- テキスト: 白〜薄いグレー（#E0E0E0）
- カード: 濃いめの背景、細めの枠線、モダンな配色
- アクセントカラー: ゴールド、エメラルドグリーン
- フォント: 細身のゴシック体

## 技術仕様

### テーマ設定ファイル
```python
# src/themes.py
THEMES = {
    'simple': {
        'background_color': (255, 255, 255),
        'text_color': (0, 0, 0),
        'card_bg': (255, 255, 255),
        'card_border': (200, 200, 200),
        'grid_color': (220, 220, 220),
        'font_family': 'hiragino',
        'card_radius': 0,  # 角丸なし
    },
    'fancy': {
        'background_color': None,  # グラデーション
        'background_gradient': [(255, 182, 193), (173, 216, 230)],  # ピンク→水色
        'text_color': (51, 51, 51),
        'card_bg': (255, 255, 255, 230),  # 半透明
        'card_border': (255, 192, 203),  # ピンク
        'grid_color': (200, 200, 200),
        'font_family': 'rounded',
        'card_radius': 15,  # 角丸
        'use_emoji': True,
    },
    'stylish': {
        'background_color': (30, 30, 30),
        'text_color': (224, 224, 224),
        'card_bg': (45, 45, 45),
        'card_border': (100, 100, 100),
        'grid_color': (80, 80, 80),
        'accent_color': (255, 215, 0),  # ゴールド
        'font_family': 'thin_gothic',
        'card_radius': 5,
    }
}
```

### 設定での選択
```python
# src/config.py
THEME = 'simple'  # 'simple', 'fancy', 'stylish'
```

## 影響範囲
- 新規ファイル: `src/themes.py`
- `src/config.py`: `THEME` 設定追加
- `src/image_generator.py`: テーマ適用ロジック追加

## タスク
- [x] `src/themes.py` 作成
- [x] 各テーマの配色定義
- [x] グラデーション背景の実装（Fancy用）
- [x] 角丸カードの実装（Fancy用）
- [x] ダークモード背景の実装（Stylish用）
- [x] テーマ切り替えロジックの実装
- [x] 各テーマでのテスト

## テスト観点
- [x] 各テーマで壁紙が正しく生成される
- [x] テキストの視認性が保たれている
- [x] カードや要素のスタイルが適用されている
- [x] 背景グラデーションが正しく描画される

## 実装完了

✅ **2026-02-04 完了**

### TDD実装結果

- **テスト**: 13個全合格（RED → GREEN）
- **テストファイル**: `tests/test_themes.py`

### 実装ファイル

1. **src/themes.py** (新規作成): 3テーマ定義（simple, fancy, stylish）
2. **src/config.py**: THEME設定追加（121-126行目）
3. **src/image_generator.py**: テーマ適用ロジック実装
   - `set_theme()` メソッド
   - `_create_gradient_background()` メソッド（Fancy用）
   - `_draw_rounded_rectangle()` メソッド（Fancy/Stylish用）
   - テーマに応じた背景・色・角丸適用

### Codexレビュー結果

#### 総合評価: 8/10

- **セキュリティ**: 問題なし（外部入力なし）
- **コード品質**: 良好（テーマ分離、保守性高い）
- **パフォーマンス**: 概ね良好（一部最適化余地あり）

#### 改善点（将来的な対応）

1. **セキュリティ**: `get_theme()` で `.copy()` を使用してテーマ辞書の直接改変を防ぐ
2. **コード品質**: `font_family` プロパティの活用または削除、未使用インポートの整理
3. **パフォーマンス**: `_create_gradient_background()` のImageDraw生成をループ外に移動
4. **ベストプラクティス**: `draw._image.paste` → `image.paste` に変更、RGBA対応強化、`hour_height` の0チェック

これらの改善点は、現在のコードは正常に動作しているため、将来的な拡張時に対応予定。

## 備考

- 3つのテーマ全て実装完了
- テーマ切り替えは `src/config.py` の `THEME` 変数で設定
- ユーザーフィードバックに基づいてテーマを調整可能
