# 006_settings_bootstrap_load_fix

## 対応対象
- `src/ui/main_window.py`
- `src/viewmodels/settings_service.py`
- （必要なら）`run_gui.py`

## 問題
- `SettingsService.load()` が起動時に呼ばれておらず、保存済み設定が復元されない。

## 修正方針（どう直すか）
- `MainWindow` 初期化の早い段階で `settings_service.load()` を実行。
- 読み込み結果を UI と ViewModel の両方へ反映する初期化順に変更。

## 実装タスク
- [ ] 起動時ロード処理を追加
- [ ] テーマ/自動更新/背景設定/クロップ位置の初期反映順を固定
- [ ] 既存 `_restore_background_setting` と二重適用しないよう整理

## 受け入れ条件
- [ ] 設定保存後に再起動して値が復元される
- [ ] 復元直後のUI表示と実際動作が一致する

## テスト観点
- [ ] 自動更新ON/OFF・間隔復元
- [ ] 背景/クロップ位置復元
