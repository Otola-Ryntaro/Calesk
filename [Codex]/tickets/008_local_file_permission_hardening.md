# 008_local_file_permission_hardening

## 対応対象
- `src/calendar_client.py`
- `src/viewmodels/settings_service.py`
- `src/wallpaper_cache.py`

## 問題
- `accounts.json` / `settings.json` / `cache_meta.json` の保存時に権限制御が弱い。

## 修正方針（どう直すか）
- 保存後に `chmod 0o600` を適用。
- ディレクトリ生成時に可能な範囲で `700` を維持（OS互換性に配慮）。
- 例外時は保存失敗としてログに明示。

## 実装タスク
- [ ] 共通の安全保存ヘルパー導入または各保存点で統一処理
- [ ] Windows系では `chmod` 制限を考慮したフォールバック実装
- [ ] 既存 `token.json` と同水準の保護方針へ整合

## 受け入れ条件
- [ ] macOS/Linuxで対象ファイルが 600 相当になる
- [ ] 権限設定失敗時もアプリが不整合状態にならない

## テスト観点
- [ ] 新規保存時/上書き時の権限
- [ ] 権限変更失敗時の挙動
