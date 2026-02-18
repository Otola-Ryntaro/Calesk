# 003_multi_account_dataflow_fix

## 対応対象
- `src/calendar_client.py`
- `src/viewmodels/wallpaper_service.py`
- `src/ui/settings_dialog.py`

## 問題
- マルチアカウント追加後に `self.accounts` が即時反映されない。
- 起動時に `load_accounts()` が走らず、UI一覧と実データ取得が空になる。
- 壁紙生成経路が単一アカウント取得 (`get_today_events/get_week_events`) に固定されている。

## 修正方針（どう直すか）
- `CalendarClient` 初期化時または起動時フローで `load_accounts()` を必ず実行。
- `add_account()` 成功時に `self.accounts` を即時更新（再読み込みまたは直接追加）。
- `WallpaperService.generate_wallpaper()` を `get_all_events(days=7)` ベースへ統一し、today/weekを分割して描画へ渡す。

## 実装タスク
- [ ] `CalendarClient` のアカウントロード責務を明確化（初期化 or 明示呼び出し）
- [ ] `add_account/remove_account/update_account_color` 後の in-memory 同期実装
- [ ] `WallpaperService` で複数アカウント統合イベントを利用
- [ ] `SettingsDialog.refresh_account_list()` が常に最新状態を参照するよう補強

## 受け入れ条件
- [ ] 追加したアカウントが即時一覧に表示される
- [ ] 再起動後もアカウント一覧が復元される
- [ ] 複数アカウントの予定が壁紙に同時反映される

## テスト観点
- [ ] アカウント追加→即時一覧表示
- [ ] 追加後再起動→一覧再現
- [ ] 複数アカウント取得時の統合件数・色表示
