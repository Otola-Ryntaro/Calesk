# カレンダー壁紙アプリ - 開発ドキュメント

## チケット一覧

### ✅ 完了 - HIGH優先度
- [001_event_card_improvement.md](001_event_card_improvement.md) - 予定カード表示改善 ✅ **2026-02-04完了**
- [002_weekly_calendar_resize.md](002_weekly_calendar_resize.md) - Weekly Calendar 縮小 ✅ **2026-02-04完了**

### 🟡 MEDIUM優先度（未着手）
- [003_calendar_icon_integration.md](003_calendar_icon_integration.md) - Google Calendar アイコン統合
- [004_design_theme_system.md](004_design_theme_system.md) - デザインテーマシステム

## 作業順序
1. ✅ レイアウト最適化（完了）
2. ✅ **001: 予定カード改善**（完了）
3. ✅ **002: Weekly Calendar縮小**（完了）
4. ⏳ 003: Google Calendarアイコン ← 次はこれ
5. ⏳ 004: デザインテーマシステム

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

## 作業ルール
- 各チケット内のタスクを `- [ ]` → `- [x]` で管理
- TDD（テスト駆動開発）で実装
- エージェントを活用
- Codexによるコードレビュー実施

## 次のステップ
003と004の実装は、ユーザーからの追加要望を待ってから進めます。
