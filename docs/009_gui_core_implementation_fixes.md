# 009: GUIコア機能実装修正

## 優先度
**CRITICAL**

## 概要
Codexレビューで指摘されたGUIの基本機能の実装不備を修正する。現在GUIが正常に動作しない原因となっている Critical/High 優先度の問題を解決する。

## 背景
チケット008でGUIの品質改善（非同期処理、メモリ最適化、入力検証など）を完了したが、Codexによる実装レビューで **GUIの基本機能が実装されていない** ことが判明した。

**主な問題:**
1. GUI経由の壁紙生成が必ず失敗する（`ImageGenerator.generate()`未実装）
2. GUIでGoogle Calendarからイベントを取得していない（常に空データ）
3. GUIとCLIでイベントスキーマが異なる（統合不可）
4. 「今日の予定」が期待と異なる動作をする

## ユーザー要求（review_notes.mdより）
- **GUIでもGoogle Calendarを取得したい**
  - 更新頻度: 1日1回は必須、可能ならリアルタイム（重くならない範囲）
- **「今日の予定」は当日全件**（過去分含む）
- **通知は1イベントにつき1回**

## 修正項目

### 🔴 CRITICAL優先度

#### C-1: GUIの壁紙生成が必ず失敗する
**症状:**
- GUI経由の壁紙更新で `ImageGenerator.generate()` が呼ばれるが、このメソッドが実装されていない
- GUIでの壁紙更新が完全に動作しない

**該当ファイル:**
- `src/viewmodels/wallpaper_service.py`
- `src/image_generator.py`

**影響:**
- GUIの主要機能（壁紙更新）が完全に動作不能

**訂正方針:**
以下のいずれかを実施:
1. `WallpaperService` から呼ぶAPIを `ImageGenerator.generate_wallpaper()` に揃える（推奨）
2. `ImageGenerator.generate()` を実装して互換を持たせる

**実装タスク:**
- [x] 現状調査: `wallpaper_service.py` の呼び出しコード確認 ✅ **2026-02-05完了**
- [x] 現状調査: `image_generator.py` の実装状況確認 ✅ **2026-02-05完了**
- [x] 設計: API統一方針の決定 ✅ **2026-02-05完了**
- [x] 実装: CalendarClient統合、API修正 ✅ **2026-02-05完了**
- [x] テスト: GUI経由の壁紙生成テスト ✅ **2026-02-05完了（34テスト全合格）**
- [ ] 動作確認: 実際にGUIから壁紙を生成できるか（要手動テスト）

### 🟡 HIGH優先度

#### ✅ H-1: GUI更新フローでカレンダー取得がない（C-1で解決済み）
**症状:**
- GUI更新時にイベント取得が走らず、常に空データで描画される
- `CalendarClient` がGUIフローに統合されていない

**該当ファイル:**
- `src/ui/main_window.py`
- `src/viewmodels/main_viewmodel.py`
- `src/calendar_client.py`

**影響:**
- GUIで実データが表示されない（空の壁紙が生成される）

**訂正方針:**
- GUIフローに `CalendarClient` を統合（ViewModelまたはService層で取得）
- **更新頻度の設計:**
  - 「1日1回の定期更新」を基本（CLIと同様）
  - 手動更新（ワンクリック）は即時取得
  - リアルタイム更新は「一定間隔の軽量ポーリング」または「次イベント前だけ更新」

**実装タスク:**
- [x] 現状調査: GUI更新フローの確認 ✅ **2026-02-05完了（C-1で実施）**
- [x] 設計: CalendarClient統合ポイントの決定 ✅ **2026-02-05完了（C-1で実施）**
- [x] 設計: 更新頻度の設計（1日1回 + 手動更新） ✅ **2026-02-05完了（C-1で実施）**
- [x] 実装: ViewModelまたはServiceへのCalendarClient統合 ✅ **2026-02-05完了（C-1で実施）**
- [x] 実装: 手動更新ボタンの動作修正 ✅ **2026-02-05完了（C-1で実施）**
- [x] テスト: カレンダー取得フローのテスト ✅ **2026-02-05完了（C-1で実施）**
- [ ] 動作確認: 実際にGoogle Calendarからイベントを取得できるか（要手動テスト）

#### ✅ H-2: GUI/CLIでイベントスキーマが不整合（完了）
**症状:**
- GUIのバリデーションは `start` 文字列を要求
- `CalendarClient` は `start_datetime` などdatetimeを返す
- GUIにCalendarClientを接続するとバリデーションで失敗

**該当ファイル:**
- `src/viewmodels/main_viewmodel.py`
- `src/calendar_client.py`
- `src/image_generator.py`

**影響:**
- GUIとCLIの統合が不可能
- コードの重複、メンテナンス性の低下

**訂正方針:**
- 1つの Event モデルに統一（dataclass等を使用）
- 入力/描画/通知で共通化
- スキーマ: `start_datetime`, `end_datetime` などdatetime型を基本とする

**実装タスク:**
- [x] 現状調査: 現在のイベントスキーマ確認（GUI/CLI） ✅ **2026-02-05完了**
- [x] 設計: 統一Eventモデルの設計（dataclass） ✅ **2026-02-05完了**
- [x] 実装: Eventモデルの作成 ✅ **2026-02-05完了（12テスト）**
- [x] 修正: CalendarClientの返り値をEventモデルに変更 ✅ **2026-02-05完了（4テスト追加）**
- [x] 修正: GUIバリデーションをEventモデルに対応 ✅ **2026-02-05完了（不要メソッド削除）**
- [x] 修正: ImageGeneratorをEventモデルに対応 ✅ **2026-02-05完了**
- [x] テスト: 統一モデルのテスト ✅ **2026-02-05完了（180テスト全合格）**
- [x] 動作確認: GUI/CLIで共通のEventモデルが動作するか ✅ **2026-02-05完了**

#### ✅ H-3: 「今日の予定」が当日全件になっていない（完了）
**症状:**
- `timeMin=now` のため既に開始した予定や終日予定が落ちる
- ユーザーの期待（当日全件）と異なる

**該当ファイル:**
- `src/calendar_client.py`
- `tests/test_calendar_client.py`

**影響:**
- 期待する「当日全件」に一致しない
- 重要なイベントが見逃される

**訂正方針:**
- 日付の開始（00:00）〜終了（23:59）を範囲指定して取得
- `timeMin` を今日の00:00:00に設定（タイムゾーンaware）
- `timeMax` を翌日の00:00:00に設定
- イベント重なり判定で継続イベントも含む

**実装タスク:**
- [x] 現状調査: 現在のtimeMin/timeMaxの実装確認 ✅ **2026-02-05完了**
- [x] テスト追加: 既開始・終日・継続イベントの取得テスト ✅ **2026-02-05完了（18テスト）**
- [x] 修正: timeMinを今日の00:00に変更（タイムゾーンaware） ✅ **2026-02-05完了**
- [x] 修正: timeMaxを翌日の00:00に追加 ✅ **2026-02-05完了**
- [x] 修正: イベント重なり判定に変更 ✅ **2026-02-05完了**
- [x] Codexレビュー: good評価取得 ✅ **2026-02-05完了**
- [ ] 動作確認: 当日全件が取得できるか（要手動テスト）

### 🟢 MEDIUM優先度（将来対応）

#### ✅ M-1: 通知が重複送信される（完了）
- 症状: 5分ごとに同じイベントの通知が繰り返される
- 訂正方針: 通知済みイベントIDを保持し、同一イベントは1回のみ通知
- 実装: `notified_event_ids: Set[str]` で通知済みIDを追跡
- テスト: 25新規テスト（217テスト全合格、カバレッジ98%）
- Codexレビュー: **good** 評価取得 ✅ **2026-02-05完了**

#### ✅ M-2: 週間カレンダーの重複イベント配置が崩れる（完了）
- 症状: 後から重複が判明した場合、既存ブロックの幅が再計算されない
- 訂正方針: 同時間帯グループを先に構築し、列数を確定してから配置
- 実装: 3フェーズアルゴリズム（グループ化→列割当→位置計算）
- テスト: 18新規テスト（235テスト全合格）
- Codexレビュー: **good** 評価取得 ✅ **2026-02-05完了**

#### ✅ M-3: API設計不一致（C-1で解決済み）
- 症状: `ImageGenerator.generate_wallpaper()` は today/week を要求、Service層は単一リスト前提
- 訂正方針: Service層で「today/week 分割」を行い、描画層は統一APIで受け取る
- 解決: **C-1実装時に解決済み** - WallpaperServiceが内部でget_today_events/get_week_eventsを呼び、ImageGeneratorに渡す構造に変更済み ✅ **2026-02-05確認**

### 🟤 LOW優先度（完了）

#### ✅ L-1: 設定コメントと実値が不一致（完了）

- 症状: `WALLPAPER_TARGET_DESKTOP` のコメントはデフォルト0だが、実値は1
- 訂正方針: コメントと実値を合わせる
- 修正内容: コメントを実値1に合わせて「現在の設定」と明記
- Codexレビュー: **承認** 評価取得 ✅ **2026-02-05完了**

#### ✅ L-2: Pillowの内部属性アクセス（完了）

- 症状: `draw._image.paste(...)` を直接呼んでいる
- 訂正方針: `image.paste(...)` を明示的に使う
- 修正内容: `_draw_calendar_icon()`に`image`引数を追加、公開APIを使用
- Codexレビュー: **承認** 評価取得 ✅ **2026-02-05完了**

## 実装順序

### Phase 1: Critical修正（GUIの基本動作を有効化）
1. **C-1**: ImageGenerator APIの統一（壁紙生成を動作させる）

### Phase 2: High修正（実データ表示と統合）
2. **H-2**: イベントスキーマの統一（統合の前提条件）
3. **H-3**: 「今日の予定」ロジックの修正（正しいデータ取得）
4. **H-1**: GUI更新フローへのCalendarClient統合（実データ表示）

### Phase 3: Medium/Low修正（将来拡張）
5. **M-1**: 通知重複防止
6. **M-2**: 週間カレンダー表示改善
7. **M-3**: API設計統一
8. **L-1, L-2**: 低優先度の整合性修正

## TDD実装方針
- 各修正項目で先にテストを追加
- テストが失敗することを確認
- 実装してテストを通す
- 動作確認で実際の動作を検証

## 成功基準
- [x] GUIから壁紙を生成できる（C-1解決） ✅ **2026-02-05完了**
- [x] GUIでGoogle Calendarからイベントを取得して表示できる（H-1解決） ✅ **2026-02-05完了**
- [x] GUI/CLIで共通のEventモデルが動作する（H-2解決） ✅ **2026-02-05完了（Codexレビュー対応済み）**
- [x] 「今日の予定」が当日全件（00:00-23:59）取得できる（H-3解決） ✅ **2026-02-05完了（Codex good評価）**
- [x] 通知重複防止が動作する（M-1解決） ✅ **2026-02-05完了（Codex good評価）**
- [x] 週間カレンダー重複配置が正しい（M-2解決） ✅ **2026-02-05完了（Codex good評価）**
- [x] 設定コメントと実値が一致（L-1解決） ✅ **2026-02-05完了（Codex承認）**
- [x] Pillow公開APIを使用（L-2解決） ✅ **2026-02-05完了（Codex承認）**
- [x] 既存テストがすべて合格 ✅ **235テスト全合格（2026-02-05）**
- [x] 新規テストがすべて合格 ✅ **CalendarEvent: 12, GetTodayEvents: 18, Notifier: 25, EventPositions: 18**
- [x] 手動テストで実際に動作確認 ✅ **2026-02-05完了**
  - ✅ 壁紙更新機能（C-1）
  - ✅ Google Calendar認証・イベント取得（H-1）
  - ✅ CalendarEventモデル統一（H-2）
  - ✅ 今日の予定取得（H-3）
  - ✅ 表示品質（M-2）
  - ✅ エラー発生なし（L-1, L-2）
  - ✅ テーマ切り替え機能実装済み（5種類: simple, modern, pastel, dark, vibrant）

## Phase 1: Critical修正（完了）

### ✅ C-1完了: ImageGenerator APIの統一（2026-02-05）

**修正内容:**
- WallpaperServiceに`CalendarClient`を統合
- `generate()` → `generate_wallpaper(today_events, week_events)`に統一
- `events`引数を削除（内部でCalendarClient使用）

**修正ファイル:**
- `src/viewmodels/wallpaper_service.py`
- `src/viewmodels/main_viewmodel.py`
- `src/viewmodels/wallpaper_worker.py`
- `tests/test_wallpaper_service.py` (+3テスト)
- `tests/test_wallpaper_worker.py`
- `tests/test_main_viewmodel.py`

**テスト結果:**
- ✅ 34テスト全合格（7.08秒）
- WallpaperService: 9テスト
- WallpaperWorker: 8テスト
- MainViewModel: 17テスト

**詳細レポート:**
- [claudedocs/C-1_gui_wallpaper_fix_summary.md](../claudedocs/C-1_gui_wallpaper_fix_summary.md)

## Phase 2: High修正（進行中）

### ✅ H-2完了: イベントスキーマの統一（2026-02-05）

**修正内容:**
- CalendarEventモデルを作成（dataclass、イミュータブル）
- CalendarClientをCalendarEvent返却に変更
- ImageGeneratorをCalendarEvent対応に変更
- MainViewModelの不要な`_validate_events()`を削除

**新規ファイル:**
- `src/models/event.py` - CalendarEventモデル
- `src/models/__init__.py` - パッケージ初期化
- `tests/test_event_model.py` - 12テスト

**修正ファイル:**
- `src/calendar_client.py` - CalendarEvent返却（4テスト追加）
- `src/image_generator.py` - プロパティアクセスに変更
- `src/viewmodels/main_viewmodel.py` - `_validate_events()` 削除

**テスト結果:**
- ✅ 180テスト全合格（14.66秒）
- CalendarEvent: 12テスト
- CalendarClient: 6テスト（4テスト追加）

**詳細レポート:**
- [claudedocs/H-2_event_schema_unification_summary.md](../claudedocs/H-2_event_schema_unification_summary.md)

## 関連チケット
- [008_gui_improvements_from_review.md](008_gui_improvements_from_review.md): GUI品質改善（完了）
- このチケットはGUIの**基本機能の実装**に焦点

## テーマ切り替え時の自動更新（追加修正）

### ✅ 完了: 2026-02-05

#### 問題

- GUIでテーマを変更しても壁紙の見た目が変わらない
- ユーザーは手動で「更新」ボタンを押す必要がある

#### 根本原因

- `MainViewModel.set_theme()` がテーマを変更するだけで、壁紙の再生成をトリガーしていなかった
- `update_wallpaper()` を明示的に呼び出さない限り、新しいテーマは適用されない

#### 修正内容

- `src/viewmodels/main_viewmodel.py:82-118` - `set_theme()` メソッドを修正
  - テーマ変更後に `self.update_wallpaper()` を自動的に呼び出す
  - ユーザーが期待する動作（テーマ変更→即座に壁紙更新）を実現
- `tests/test_main_viewmodel.py:365-390` - 新しいテストケースを追加
  - `test_main_viewmodel_set_theme_triggers_update()` でテーマ変更時の自動更新を確認

#### テスト結果

- ✅ 236テスト全合格（15.14秒）
  - 既存の235テストが全て合格
  - 新規テスト1件追加（テーマ変更時の自動更新確認）

#### 動作確認

- テーマを変更すると、自動的に壁紙が再生成される
- 5つのテーマ（simple, modern, pastel, dark, vibrant）それぞれで視覚的な違いが確認できる

## 参考資料
- Codexレビュー結果: `Codex/review_notes.md`
- 既存実装: `src/calendar_client.py`, `src/image_generator.py`
- GUI実装: `src/ui/main_window.py`, `src/viewmodels/main_viewmodel.py`
