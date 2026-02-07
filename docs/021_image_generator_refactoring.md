# チケット021: image_generator.py リファクタリング（ファイル分割・コード品質改善）

## 概要

`image_generator.py` が1848行・45メソッドに肥大化しており、保守性・可読性が低下。
Mixinパターンでファイルを分割し、テーマデフォルト値の集約・共通メソッド抽出も行う。

## 現状の問題

- **CRITICAL**: `image_generator.py` が1848行（目安300行超過）
- **HIGH**: テーマデフォルト値が各メソッドに `.get('key', default)` で散在
- **MEDIUM**: カード背景描画が複数メソッドで重複

## 改善項目

### 1. ファイル分割（Mixinパターン）

**方針**: ImageGeneratorクラスをMixinに分解し、インポートパスは変更しない（テスト互換）

```
src/
├── image_generator.py          ← 統合クラス・初期化・メイン処理 (~250行)
│   └ ImageGenerator(CardRendererMixin, CalendarRendererMixin, EffectsRendererMixin)
│
├── renderers/
│   ├── __init__.py
│   ├── card_renderer.py        ← カード描画 (~500行)
│   │   └ CardRendererMixin
│   ├── calendar_renderer.py    ← 週間カレンダー描画 (~500行)
│   │   └ CalendarRendererMixin
│   └── effects.py              ← ビジュアルエフェクト (~300行)
│       └ EffectsRendererMixin
```

### 2. テーマデフォルト値の集約

`themes.py` に `DEFAULT_THEME` 定数を追加し、`.get('key', default)` のデフォルト値を一元管理。

### 3. カード背景描画の共通メソッド抽出

`_draw_card_background()` メソッドを作成し、compact/single/hero カード間で共通化。

## タスク

- [x] `src/renderers/` ディレクトリ作成
- [x] `src/renderers/effects.py` 抽出（EffectsRendererMixin）
- [x] `src/renderers/card_renderer.py` 抽出（CardRendererMixin）
- [x] `src/renderers/calendar_renderer.py` 抽出（CalendarRendererMixin）
- [x] `src/image_generator.py` をMixin統合クラスに簡素化
- [x] `themes.py` に DEFAULT_THEME 追加
- [x] 散在する `.get()` デフォルト値を DEFAULT_THEME 参照に変更（ChainMap使用）
- [x] `_draw_card_background()` 共通メソッド抽出（4箇所共通化）
- [x] 全テスト回帰確認（402テスト全合格）
- [x] コードレビュー（Approve: CRITICAL 0件, WARNING 4件, SUGGESTION 4件）

## 変更ファイル

- `src/image_generator.py` - Mixin継承に変更、大幅削減
- `src/renderers/__init__.py` - 新規
- `src/renderers/card_renderer.py` - 新規
- `src/renderers/calendar_renderer.py` - 新規
- `src/renderers/effects.py` - 新規
- `src/themes.py` - DEFAULT_THEME追加

## 制約

- `from src.image_generator import ImageGenerator` のインポートパスは変更しない
- 全402テストが変更なしで合格すること
- 機能変更なし（純粋リファクタリング）

## 優先度: HIGH
## 工数: 中（3-4時間）
