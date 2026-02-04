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

### 🚧 計画中 - MEDIUM優先度

- [007_gui_application.md](007_gui_application.md) - GUIアプリケーション化 📋 **計画中**

## 作業順序

1. ✅ レイアウト最適化（完了）
2. ✅ **001: 予定カード改善**（完了）
3. ✅ **002: Weekly Calendar縮小**（完了）
4. ✅ **003: Google Calendarアイコン**（完了）
5. ✅ **004: デザインテーマシステム**（完了）
6. ✅ **005: 毎日自動更新システム**（完了）
7. ✅ **006: テーマシステム改善**（完了）
8. 🚧 **007: GUIアプリケーション化**（計画中）

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

## 作業ルール

- 各チケット内のタスクを `- [ ]` → `- [x]` で管理
- TDD（テスト駆動開発）で実装
- エージェントを活用
- Codexによるコードレビュー実施

## 次のステップ

### Phase 8: GUIアプリケーション化（計画中）

**目標**: CLIベースからGUIアプリケーションへの移行

#### Phase 8.1: 基本UI（Tkinter）
- [ ] メインウィンドウの作成
- [ ] テーマ選択ドロップダウン
- [ ] 「今すぐ更新」ボタン
- [ ] 設定画面（基本項目のみ）
- [ ] 既存のCLI機能との統合

#### Phase 8.2: プレビュー機能
- [ ] 壁紙プレビューの実装
- [ ] テーマ変更時のリアルタイムプレビュー
- [ ] テーマギャラリー（サムネイル表示）

#### Phase 8.3: 高度な設定
- [ ] カレンダー連携UI
- [ ] 自動更新設定UI
- [ ] マルチディスプレイ設定UI
- [ ] カスタムテーマの作成機能

#### Phase 8.4: システム統合
- [ ] システムトレイアイコン
- [ ] 右クリックメニュー
- [ ] 通知機能
- [ ] アプリケーションのパッケージング（.app、.exe）

詳細は [007_gui_application.md](007_gui_application.md) を参照
