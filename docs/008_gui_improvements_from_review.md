# 008: GUI改善（Codexレビュー指摘事項対応）

## 優先度
**HIGH**

## 概要
Phase 2のCodexレビュー（スコア: 7/10）で指摘された改善点に対応し、GUIの品質、パフォーマンス、UXを向上させる

## Codexレビュー結果
- **評価**: good
- **スコア**: 7/10
- **日付**: 2026-02-04
- **レビュー対象**: MainWindow, PreviewWidget, MainViewModel

## 改善項目

### 🔴 HIGH優先度

#### 1. UIスレッドブロック防止（非同期実行）
**現状の問題**:
- `MainViewModel.update_wallpaper()` が同期処理で、UIスレッドをブロックする
- 壁紙生成中にアプリケーションが応答しなくなる可能性

**対応方針**:
- QThread または QRunnable を使用して非同期実行
- シグナル/スロットで進捗とエラーを通知
- 更新中のキャンセル機能の追加

**実装タスク**:

- [x] `WallpaperWorker` クラスの作成（QRunnable継承） ✅ **2026-02-04完了**
- [x] MainViewModel での QThreadPool 使用 ✅ **2026-02-04完了**
- [x] 進捗シグナルの追加（`progress_updated(int)` 0-100%） ✅ **2026-02-04完了**
- [x] キャンセル機能の実装（`cancel_update()`） ✅ **2026-02-04完了**
- [x] テストの追加（非同期処理のテスト） ✅ **2026-02-04完了**
  - WallpaperWorker: 8テスト全合格
  - MainViewModel: 15テスト全合格
  - **Codexレビュー**: スコア8/10、評価"good"

**ファイル**:
- `src/viewmodels/main_viewmodel.py`
- `src/viewmodels/wallpaper_worker.py`（新規）
- `tests/test_main_viewmodel.py`

#### 2. 進捗表示の実装
**現状の問題**:
- 更新中の進捗が分からず、ユーザーに不安を与える
- ステータスバーのメッセージのみで視覚的フィードバックが不足

**対応方針**:
- QProgressBar の追加
- 更新中のステータス表示（「画像生成中...」「壁紙設定中...」）
- アニメーション付きのビジー表示

**実装タスク**:

- [x] MainWindow に QProgressBar を追加 ✅ **2026-02-04完了**
- [x] MainViewModel の `progress_updated` シグナルに接続 ✅ **2026-02-04完了**
- [ ] 不定進捗モード（indeterminate）のサポート
- [ ] 完了時のアニメーション（フェードアウト）
- [x] テストの追加 ✅ **2026-02-04完了**
  - MainWindow: 12テスト全合格（QProgressBar関連5テスト追加）

**ファイル**:
- `src/ui/main_window.py`
- `tests/test_main_window.py`

#### 3. 入力検証の強化
**現状の問題**:
- テーマ名の検証がない（存在しないテーマを設定可能）
- イベントデータの検証がない
- ファイルパスの検証が不十分

**対応方針**:
- テーマ名の検証（利用可能なテーマのチェック）
- イベントデータのスキーマ検証
- ファイルパスのサニタイゼーション
- 無効な入力時のエラーシグナル発火

**実装タスク**:

- [x] `MainViewModel.set_theme()` に検証ロジック追加 ✅ **2026-02-04完了**
- [x] イベントデータのバリデータ追加 ✅ **2026-02-04完了**
- [x] ファイルパス検証の強化（PreviewWidget） ✅ **2026-02-04完了**
- [x] 巨大ファイルのサイズチェック（10MB制限など） ✅ **2026-02-04完了**
- [x] テストの追加（無効入力ケース） ✅ **2026-02-04完了**
  - MainViewModel: 21テスト全合格（+6テスト追加）
  - PreviewWidget: 11テスト全合格（+4テスト追加）
  - 全体: 100テスト全合格
  - **Codexレビュー**: スコア6/10、評価"fair"

**ファイル**:
- `src/viewmodels/main_viewmodel.py`
- `src/ui/widgets/preview_widget.py`
- `tests/test_main_viewmodel.py`
- `tests/test_preview_widget.py`

**Codexレビュー指摘（2026-02-04）**:

- **強み**: テーマ/イベント/ファイルの基本検証、テストカバレッジ追加
- **改善点**: summary型チェック、厳密な日時解析、許可ディレクトリ制限、MIME検証、UIフィードバック強化
- **セキュリティ**: 任意パス読み込み、シンボリックリンク対策、ログインジェクション対策
- **推奨**: 許可ディレクトリ制限、is_file/MIME検証、datetime厳密解析、UIフィードバック改善

### 🟡 MEDIUM優先度

#### 4. メモリ管理の最適化
**現状の問題**:
- PreviewWidget が元画像をそのまま保持（`_original_pixmap`）
- 大きな画像（例: 4K、8K）でメモリ消費が大きい
- スケーリング前の画像がメモリに残り続ける

**対応方針**:
- プレビュー用に縮小版を生成（640x360など）
- 元画像はディスクに保持し、必要時のみ読み込み
- キャッシュ機構の導入
- メモリ使用量の監視

**実装タスク**:
- [ ] プレビュー画像の最大サイズ設定（640x360）
- [ ] `PreviewWidget.set_image()` で自動縮小
- [ ] 元画像の保持を最小限に（パスのみ保持）
- [ ] キャッシュディレクトリの作成（`~/.calendar_wallpaper/cache/`）
- [ ] メモリ使用量のテスト

**ファイル**:
- `src/ui/widgets/preview_widget.py`
- `tests/test_preview_widget.py`

#### 5. テーマ管理の単一ソース化
**現状の問題**:
- MainWindow でテーマ一覧をハードコード（68-74行目）
- その後 ViewModel で上書き（117-121行目）
- 二重管理でメンテナンス性が低い

**対応方針**:
- テーマ一覧は ViewModel が唯一のソース
- MainWindow は ViewModel からのみ取得
- ハードコードを削除

**実装タスク**:
- [x] MainWindow のテーマハードコード削除 ✅ **2026-02-04完了**
- [x] `_setup_control_area()` で空の ComboBox を作成 ✅ **2026-02-04完了**
- [x] `_connect_viewmodel()` でテーマ一覧を設定 ✅ **2026-02-04完了**
- [x] テストの更新 ✅ **2026-02-04完了**
  - MainWindow: 12テスト全合格
  - 全体: 100テスト全合格
  - **コードレビュー**: スコア10/10、評価"APPROVED"

**ファイル**:
- `src/ui/main_window.py`
- `tests/test_main_window.py`

#### 6. エラーフィードバックの改善
**現状の問題**:
- エラーメッセージがステータスバーのみ
- ユーザーが気づきにくい
- 詳細情報が不足

**対応方針**:
- QMessageBox でエラーダイアログ表示
- エラーの重要度に応じた表示方法の変更
- ログファイルへの記録とログ表示機能

**実装タスク**:
- [x] 重大なエラー時に QMessageBox 表示 ✅ **2026-02-04完了**
- [x] エラーレベルの分類（ERROR, WARNING, CRITICAL） ✅ **2026-02-04完了**
- [ ] ログビューアーの追加（オプション）
- [x] テストの追加 ✅ **2026-02-04完了**
  - MainWindow: 15テスト全合格（+3エラーフィードバックテスト追加）
  - 全体: 103テスト全合格
  - **コードレビュー**: スコア10/10、評価"APPROVED"

**ファイル**:
- `src/ui/main_window.py`
- `tests/test_main_window.py`

### 🟢 LOW優先度

#### 7. テストの改善
**現状の問題**:
- MainWindow のテストで ViewModel をモックしていない
- pytest-qt の `waitSignal` タイムアウトを一般 Exception で受けている
- エッジケースのカバレッジが不足

**対応方針**:
- MainWindow テストで ViewModel を注入・モック
- `TimeoutError` で明示的に検証
- エッジケースの追加（ネットワークエラー、権限エラーなど）

**実装タスク**:
- [ ] MainWindow テストで ViewModel モックを注入
- [ ] `waitSignal` タイムアウトの明示的処理
- [ ] エッジケーステストの追加
- [ ] カバレッジ 90% 以上を目標

**ファイル**:
- `tests/test_main_window.py`
- `tests/test_main_viewmodel.py`
- `tests/test_preview_widget.py`

#### 8. UI状態の一貫性
**現状の問題**:
- PreviewWidget で存在しないファイル時に状態が曖昧
- エラー時の UI リセットが不完全

**対応方針**:
- エラー時に明示的に `clear_preview()` を呼ぶ
- UI 状態の明確な定義（Initial, Loading, Loaded, Error）
- 状態遷移の可視化

**実装タスク**:
- [ ] PreviewWidget に状態管理を追加
- [ ] エラー時の自動クリア
- [ ] 状態遷移のテスト
- [ ] 状態図のドキュメント作成

**ファイル**:
- `src/ui/widgets/preview_widget.py`
- `tests/test_preview_widget.py`
- `docs/` （状態図）

## 実装順序

### Phase 1: パフォーマンスとUX（HIGH）
1. UIスレッドブロック防止（非同期実行）
2. 進捗表示の実装
3. 入力検証の強化

### Phase 2: コード品質（MEDIUM）
4. メモリ管理の最適化
5. テーマ管理の単一ソース化
6. エラーフィードバックの改善

### Phase 3: テストと保守性（LOW）
7. テストの改善
8. UI状態の一貫性

## 成功基準
- [ ] すべての HIGH 優先度項目の完了
- [ ] Codex レビュースコア 8/10 以上
- [ ] テストカバレッジ 90% 以上
- [ ] 大きな画像（4K）での応答性確認
- [ ] エラーケースの適切なハンドリング

## 関連チケット
- [007_gui_application.md](007_gui_application.md): Phase 2 完了
- Phase 3 以降の機能実装はこのチケット完了後に実施

## 参考資料
- Codexレビュー結果: `/tmp/claude/phase2-codex-review-result.json`
- PyQt6 非同期処理: QThread, QRunnable, QThreadPool
- PyQt6 プログレス表示: QProgressBar, QProgressDialog
