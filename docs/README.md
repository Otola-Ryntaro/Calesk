# カレンダー壁紙アプリ - 開発ドキュメント

## チケット一覧

### ✅ 完了 - HIGH優先度

- [001_event_card_improvement.md](001_event_card_improvement.md) - 予定カード表示改善 ✅ **2026-02-04完了**
- [002_weekly_calendar_resize.md](002_weekly_calendar_resize.md) - Weekly Calendar 縮小 ✅ **2026-02-04完了**

### ✅ 完了 - MEDIUM優先度

- [003_calendar_icon_integration.md](003_calendar_icon_integration.md) - Google Calendar アイコン統合 ✅ **2026-02-04完了**
- [004_design_theme_system.md](004_design_theme_system.md) - デザインテーマシステム ✅ **2026-02-04完了**
- [005_autostart_system.md](005_autostart_system.md) - 毎日自動更新システム（クロスプラットフォーム対応） ✅ **2026-02-04完了**
- [006_theme_system_improvement.md](006_theme_system_improvement.md) - テーマシステム改善（背景画像流用、半透明カード） ✅ **2026-02-04完了**
- [007_gui_application.md](007_gui_application.md) - GUIアプリケーション化 Phase 2 ✅ **2026-02-04完了**

### ✅ 完了 - HIGH優先度

- [008_gui_improvements_from_review.md](008_gui_improvements_from_review.md) - GUI改善（Codexレビュー指摘事項対応） ✅ **2026-02-05完了**
- [009_gui_core_implementation_fixes.md](009_gui_core_implementation_fixes.md) - GUIコア機能実装修正（Phase 1完了） 🚧 **進行中**

## 作業順序

1. ✅ レイアウト最適化（完了）
2. ✅ **001: 予定カード改善**（完了）
3. ✅ **002: Weekly Calendar縮小**（完了）
4. ✅ **003: Google Calendarアイコン**（完了）
5. ✅ **004: デザインテーマシステム**（完了）
6. ✅ **005: 毎日自動更新システム**（完了）
7. ✅ **006: テーマシステム改善**（完了）
8. ✅ **007: GUIアプリケーション化 Phase 2**（完了）
9. 🚧 **008: GUI改善（Codexレビュー対応）**（進行中）

## 完了済み

### Phase 1: セキュリティ強化（2026-02-03 完了）

- ✅ Token権限制限（0o600）
- ✅ AppleScriptコマンドインジェクション対策
- ✅ KDE JavaScriptインジェクション対策
- ✅ AppleScript改行文字対応
- ✅ ファイルパス検証（拡張子・サイズ）

### Phase 2: レイアウト最適化（2026-02-04 完了）

- ✅ 動的レイアウト計算実装
- ✅ 1080px以内に収まるよう調整
- ✅ multiline_text anchor エラー修正

### Phase 3: UI改善（2026-02-04 完了）

- ✅ 予定カード複数表示対応（最大3件）
- ✅ フォントサイズ最適化
- ✅ Weekly Calendar縮小

### Phase 4: アイコン統合（2026-02-04 完了）

- ✅ Google Calendarアイコン生成（40x40px）
- ✅ OS別アイコン配置（Mac: 上部、Windows: 右下）
- ✅ TDDテスト実装（6テスト全合格）
- ✅ Codexコードレビュー（評価: 8/10）

### Phase 5: デザインテーマシステム（2026-02-04 完了）

- ✅ 3テーマ実装（Simple/Fancy/Stylish）
- ✅ グラデーション背景（Fancy用）
- ✅ 角丸カード（Fancy/Stylish用）
- ✅ ダークモード（Stylish用）
- ✅ TDDテスト実装（13テスト全合格）
- ✅ Codexコードレビュー（評価: 8/10）

### Phase 6: 毎日自動更新システム（2026-02-04 完了）

- ✅ クロスプラットフォーム対応（macOS/Windows）
- ✅ macOS: launchd設定（毎日06:00実行）
- ✅ Windows: タスクスケジューラー設定（毎日06:00実行）
- ✅ インストール/アンインストールスクリプト
- ✅ ワンショットモード（`--run-once`）採用
- ✅ ドキュメント作成

### Phase 7: テーマシステム改善（2026-02-04 完了）

- ✅ 5テーマ実装（simple/modern/pastel/dark/vibrant）
- ✅ 全テーマで背景画像を流用
- ✅ 半透明カード対応（card_alpha）
- ✅ 角丸カード対応（card_radius）
- ✅ カード影機能（card_shadow、オン/オフ可能）
- ✅ パステルテーマのイベントカラー対応
- ✅ TDDテスト実装（17テスト全合格）

### Phase 8: GUIアプリケーション化 Phase 2（2026-02-04 完了）

- ✅ PyQt6のインストールと環境構築
- ✅ MVVMアーキテクチャの実装（View/ViewModel/Service層）
- ✅ MainWindow実装（テーマ選択、更新ボタン、ステータスバー）
- ✅ PreviewWidget実装（画像表示、自動スケーリング）
- ✅ MainViewModel実装（状態管理、シグナル発火）
- ✅ ViewModelとViewの連携（シグナル/スロット）
- ✅ TDDテスト実装（26テスト全合格）
- ✅ Codexコードレビュー（評価: good、スコア: 7/10）

## 作業ルール

- 各チケット内のタスクを `- [ ]` → `- [x]` で管理
- TDD（テスト駆動開発）で実装
- エージェントを活用
- Codexによるコードレビュー実施

## 次のステップ

### Phase 9: GUI改善（完了）

**目標**: Codexレビュー指摘事項への対応とUX向上

✅ **2026-02-05完了**: 全タスク完了（180テスト、カバレッジ91%）

詳細は [008_gui_improvements_from_review.md](008_gui_improvements_from_review.md) を参照

### Phase 10: GUIコア機能実装修正（進行中）

**目標**: Codexレビューで指摘されたGUIの基本機能実装不備の修正

#### Phase 1: Critical修正（完了）

- [x] **C-1**: ImageGenerator APIの統一 ✅ **2026-02-05完了**
  - WallpaperServiceにCalendarClient統合
  - GUI/CLI APIの統一
  - 34テスト全合格

#### Phase 2: High修正（一部完了）

- [x] **H-2**: イベントスキーマの統一 ✅ **2026-02-05完了**
  - CalendarEventモデル作成（dataclass）
  - CalendarClient/ImageGenerator対応
  - 180テスト全合格（12テスト追加）
- [ ] **H-3**: 「今日の予定」ロジックの修正（未着手）

詳細は [009_gui_core_implementation_fixes.md](009_gui_core_implementation_fixes.md) を参照

#### HIGH優先度

- [ ] UIスレッドブロック防止（非同期実行）
- [ ] 進捗表示の実装（QProgressBar）
- [ ] 入力検証の強化

#### MEDIUM優先度

- [ ] メモリ管理の最適化
- [ ] テーマ管理の単一ソース化
- [ ] エラーフィードバックの改善

#### LOW優先度

- [ ] テストの改善
- [ ] UI状態の一貫性

### Phase 11: デザイン改善・機能拡張（2026-02-07〜）

**目標**: デザインの根本的改善と新機能追加

#### HIGH優先度

- [x] [011: Weekly Calendar 時刻ラベルの視認性改善](011_weekly_calendar_visibility.md) ✅
- [x] [012: 上段カード - 今日・明日・明後日の3列レイアウト](012_three_column_card_layout.md) ✅
- [x] [016: デザイン再計画 - 背景融和性・枠形・フォント・色分け](016_design_overhaul.md) ✅

#### MEDIUM優先度

- [x] [013: 進行中イベントの強調強化](013_in_progress_event_emphasis.md) ✅
- [x] [014: 現在時刻表示 - 蛍光色で時間帯塗りつぶし](014_current_time_highlight.md) ✅
- [x] [015: 日をまたぐ予定の横バー表示](015_multi_day_events.md) ✅
- [x] [018: 自動更新機能 + 常駐アプリ化](018_auto_update_and_resident_app.md) Phase 1 ✅（Phase 2-5は未実装）

#### LOW優先度（将来実装）

- [ ] [017: GUI内Googleログイン・カレンダー管理](017_google_login_calendar_management.md)

### 作業順序（推奨）

1. **011**: Weekly Calendar時刻ラベルの視認性（即効性 HIGH）
2. **012**: 上段カード3列レイアウト（構造変更 HIGH）
3. **013**: 進行中イベントの強調（012と連携）
4. **014**: 現在時刻の蛍光塗りつぶし（小工数）
5. **016**: デザイン再計画（フォント・色分け改善）
6. **018-Phase1**: 自動更新MVP（QTimer方式）
7. **015**: 日をまたぐ予定の横バー表示
8. **018-Phase2〜5**: 常駐アプリ化
9. **017**: GUI内Googleログイン（将来）
