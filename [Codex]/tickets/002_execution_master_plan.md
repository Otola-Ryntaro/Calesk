# 002_execution_master_plan

## 目的
レビュー指摘（F-001〜F-009）を、Claude code が順番に実装できるように作業計画を固定する。

## 実行順（必須）
1. `003_multi_account_dataflow_fix.md`
2. `004_events_pagination_fix.md`
3. `005_service_concurrency_isolation.md`
4. `006_settings_bootstrap_load_fix.md`
5. `007_preview_pipeline_optimization.md`
6. `008_local_file_permission_hardening.md`
7. `009_apply_button_failure_recovery.md`
8. `010_token_dir_creation_fix.md`
9. `011_account_config_defensive_parsing.md`

## 依存関係
- `003` 完了前に `007` は着手しない（イベント取得経路が変わるため）。
- `004` は `003` の一部関数抽出と同時実施して良い。
- `005` 完了後に `007` を適用する（競合回避の土台）。
- `008` と `010` は並行実施可能。

## 完了定義
- [ ] すべてのチケットで「受け入れ条件」を満たす
- [ ] 回帰確認（壁紙適用・プレビュー・アカウント追加/削除・設定再起動復元）
- [ ] 変更内容を `USER_GUIDE.md` または開発ドキュメントへ追記
