# 005_service_concurrency_isolation

## 対応対象
- `src/viewmodels/main_viewmodel.py`
- `src/viewmodels/wallpaper_worker.py`
- `src/viewmodels/wallpaper_service.py`

## 問題
- プレビュー用/適用用ワーカーが同一 `WallpaperService` インスタンス（可変状態を持つ `ImageGenerator`）を共有し競合リスクがある。

## 修正方針（どう直すか）
- ワーカーごとに独立した Service/Generator を使う構造へ変更。
- 共有が必要な情報は immutable な設定値のみに限定。
- キャンセル要求時の後処理を明確化（結果シグナルの扱い統一）。

## 実装タスク
- [ ] `WallpaperWorker` / `PreviewWorker` の依存注入を見直し（共有Service排除）
- [ ] `MainViewModel` でワーカー生成時に独立インスタンスを渡す
- [ ] 並行実行時の `_is_updating` / preview状態遷移を再確認

## 受け入れ条件
- [ ] テーマ連打中でも適用処理が壊れない
- [ ] 競合による画像不整合/クラッシュが発生しない

## テスト観点
- [ ] preview連打 + apply同時操作
- [ ] cancel直後の状態復旧
