# 007_preview_pipeline_optimization

## 対応対象
- `src/viewmodels/main_viewmodel.py`
- `src/viewmodels/wallpaper_service.py`
- `src/image_generator.py`

## 問題
- プレビュー生成が毎回「認証→API取得→フルサイズ生成→保存」を実行し、UI遅延/負荷が高い。

## 修正方針（どう直すか）
- プレビュー専用経路を追加し、低解像度・非保存・可能ならイベントキャッシュ利用に分離。
- 本適用経路のみフルサイズ保存と壁紙適用を実行。

## 実装タスク
- [ ] `WallpaperService` に preview専用メソッドを追加
- [ ] `ImageGenerator` に previewモード（サイズ縮小/保存スキップ）を導入
- [ ] `MainViewModel.preview_theme()` を preview専用経路へ差し替え

## 受け入れ条件
- [ ] テーマ切替時の体感待ち時間が改善
- [ ] プレビュー操作で `output/` に不要ファイルを増やさない

## テスト観点
- [ ] 連続テーマ切替時の処理時間
- [ ] preview後にapplyした際の結果整合性
