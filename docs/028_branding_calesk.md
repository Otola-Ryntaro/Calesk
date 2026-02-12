# 028: ブランディング — Calesk（カレスク）

## 概要

アプリ名を「カレンダー壁紙アプリ」から「Calesk（カレスク）」に統一し、アイコン・ビルド成果物を含むブランド資産を整備する。

## アプリ名

- 英語: **Calesk**
- カタカナ: **カレスク**
- 由来: calendar + desk
- 競合: ソフトウェア分野での同名なし（調査済み 2026-02-12）

## タスク

### Phase 1: アプリ名リネーム

対象ファイルと変更箇所:

| ファイル | 変更内容 |
|---------|---------|
| `src/ui/main_window.py` | `setWindowTitle("Calesk")` |
| `src/notifier.py` | `app_name='Calesk'` |
| `run_gui.py` | `setApplicationName("Calesk")` |
| `main.py` | ログメッセージ |
| `CalendarWallpaper.spec` | name, CFBundleDisplayName, CFBundleName → Calesk |
| `CalendarWallpaper_windows.spec` | name → Calesk |
| `README.md` | タイトル、ダウンロードファイル名 |
| `USER_GUIDE.md` | アプリ名・ファイル名の参照 |
| `tests/test_notifier.py` | app_name の期待値 |

- [ ] 上記ファイルのアプリ名を一括置換
- [ ] spec ファイル名を `Calesk.spec` / `Calesk_windows.spec` にリネーム
- [ ] テスト全件パスを確認

### Phase 2: アイコン作成

- [ ] アプリアイコンのデザイン（カレンダー + デスクトップモチーフ）
- [ ] macOS用: `assets/Calesk.icns`（1024x1024 元画像から生成）
- [ ] Windows用: `assets/Calesk.ico`（256x256, 128, 64, 48, 32, 16px）
- [ ] メニューバー用: `assets/tray_icon.png`（22x22 @2x、モノクロ推奨）
- [ ] spec ファイルにアイコンパスを設定

### Phase 3: ビルド成果物のリネーム

- [ ] macOS: `Calesk.app` / `Calesk-macOS.zip`
- [ ] Windows: `Calesk.exe` / `Calesk-Windows.zip`
- [ ] GitHub Actions のビルドワークフローを更新（あれば）
- [ ] Releasesページの説明を更新

### 注意事項

- Google Cloud Console の OAuth 同意画面のアプリ名も「Calesk」に変更推奨
- credentials.json 内のプロジェクト名は変更不要（クライアントIDに影響しない）
