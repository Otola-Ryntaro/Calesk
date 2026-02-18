# 000_project_review_summary

## 1. Summary（要約）
- **F-001 (High)**: マルチアカウント機能が実質未接続で、UI表示・実データ取得の両方で機能しない。
- **F-002 (High)**: イベント取得APIにページネーション未実装箇所があり、予定件数が多い環境で予定欠落が発生する。
- **F-003 (High)**: プレビュー/本適用ワーカーが同一Serviceインスタンスを共有し、並行実行でレースコンディションが起きうる。
- **F-004 (Medium)**: 設定の永続化は実装されているが、起動時ロード未実行のため保存値が反映されない。
- **F-005 (Medium)**: プレビュー生成ごとにOAuth認証・API取得・フル画像生成・ディスク書き込みを行い、UI遅延とAPI負荷が大きい。
- **F-006 (Medium)**: 設定/メタデータ保存ファイル（accounts/settings/cache）の権限保護が不足し、ローカル情報漏えいリスクがある。

## 2. Scope（対象範囲）
- ユーザー指定: プロジェクト全体の構造/アーキテクチャ/技術スタック/DB/FE-BE接続/リスク評価
- 主要確認対象:
  - エントリポイント: `main.py`, `run_gui.py`
  - 構成/設定: `README.md`, `requirements.txt`, `src/config.py`
  - コア: `src/calendar_client.py`, `src/image_generator.py`, `src/wallpaper_setter.py`, `src/wallpaper_cache.py`, `src/notifier.py`
  - 接続層: `src/viewmodels/main_viewmodel.py`, `src/viewmodels/wallpaper_service.py`, `src/viewmodels/wallpaper_worker.py`, `src/viewmodels/settings_service.py`
  - UI: `src/ui/main_window.py`, `src/ui/settings_dialog.py`, `src/ui/widgets/preview_widget.py`
  - 描画層: `src/renderers/*.py`, `src/models/event.py`
- 補足:
  - テスト実行は `./venv/bin/python -m pytest` が環境上の異常終了（exit code -1）で完走不可だったため、静的レビュー中心。

## 3. Findings（指摘一覧）

### F-001 / High / Logic
- **Location**: `src/calendar_client.py:401`, `src/calendar_client.py:603`, `src/calendar_client.py:666`, `src/ui/settings_dialog.py:331`, `src/viewmodels/wallpaper_service.py:61`
- **What**: マルチアカウント追加ロジックはあるが、追加後に `self.accounts` へ反映されず、起動時 `load_accounts()` 呼び出しも無い。さらに壁紙生成時は `get_today_events()/get_week_events()` の単一トークン経路のみ使用。
- **Why**: UI上で「アカウント追加/一覧」が期待どおり機能せず、実際の壁紙にも複数アカウント予定が反映されない。
- **How**: 起動時に `load_accounts()` を実行し、壁紙取得経路を `get_all_events()` ベースに統一。`add_account()` 成功時にインメモリ状態も即時更新する。
- **Confidence**: High

### F-002 / High / Bug
- **Location**: `src/calendar_client.py:152`, `src/calendar_client.py:261`
- **What**: `get_events()` と `get_today_events()` で `nextPageToken` を辿っておらず、1ページ目のみ取得。
- **Why**: 件数の多いカレンダー環境でイベントが欠落し、壁紙表示が不完全になる。
- **How**: `_get_events_from_service()` と同様にページネーションを共通化し、全イベント取得を保証する。
- **Confidence**: High

### F-003 / High / Concurrency
- **Location**: `src/viewmodels/main_viewmodel.py:345`, `src/viewmodels/main_viewmodel.py:187`, `src/viewmodels/wallpaper_worker.py:80`, `src/viewmodels/wallpaper_worker.py:141`, `src/viewmodels/wallpaper_service.py:32`
- **What**: プレビュー用と本適用用ワーカーが同一 `WallpaperService`（内部に可変状態の `ImageGenerator` を保持）を共有し、キャンセルも協調的で実処理中は止まらない。
- **Why**: テーマ切替連打時に描画状態の競合・不整合画像・予期せぬ失敗が発生しうる。
- **How**: ワーカーごとに独立Serviceを使用するか、排他制御（mutex）を導入。プレビューはキャンセル可能な軽量経路へ分離する。
- **Confidence**: High

### F-004 / Medium / Logic
- **Location**: `src/viewmodels/settings_service.py:104`, `src/ui/main_window.py:50`, `src/ui/main_window.py:367`
- **What**: `SettingsService.load()` がどこからも呼ばれておらず、起動時は常にデフォルト設定で動作。
- **Why**: ユーザーが保存した設定（自動更新間隔・背景設定など）が復元されず、UXと期待挙動が乖離する。
- **How**: `MainWindow` 初期化時に `settings_service.load()` を先行実行し、その値でUI/ViewModelを初期化する。
- **Confidence**: High

### F-005 / Medium / Performance
- **Location**: `src/viewmodels/main_viewmodel.py:320`, `src/viewmodels/wallpaper_service.py:57`, `src/viewmodels/wallpaper_service.py:61`, `src/image_generator.py:404`
- **What**: テーマプレビューごとに認証→API取得→フルサイズ壁紙生成→ファイル保存まで実施している。
- **Why**: UI応答性低下、Google API呼び出し過多、無駄なI/O増加（特に連続テーマ変更時）が起きる。
- **How**: プレビューは「最新イベントキャッシュ + 低解像度メモリ生成」に分離し、認証/API取得をデバウンス外へ移す。
- **Confidence**: High

### F-006 / Medium / Security
- **Location**: `src/calendar_client.py:348`, `src/viewmodels/settings_service.py:94`, `src/wallpaper_cache.py:51`
- **What**: `accounts.json` / `settings.json` / `cache_meta.json` 保存時にファイル権限の制限が無い。
- **Why**: 共有端末・マルチユーザー環境でメールアドレス、ローカルパス、利用状況が第三者に読まれるリスク。
- **How**: 保存直後に `chmod 0o600` を適用し、設定ディレクトリ権限も `700` に統一する。
- **Confidence**: Medium

### F-007 / Medium / UX
- **Location**: `src/ui/main_window.py:295`, `src/ui/main_window.py:299`
- **What**: 「壁紙に適用」クリック時にボタンを先に無効化し、`apply_wallpaper()` の起動失敗時ハンドリングが無い。
- **Why**: 起動失敗時にボタンが再有効化されず、UIが実質操作不能になる可能性がある。
- **How**: `apply_wallpaper()` 戻り値を判定し、失敗時は即座にボタン再有効化とエラーメッセージ表示を行う。
- **Confidence**: High

### F-008 / Medium / Robustness
- **Location**: `src/calendar_client.py:69`, `src/calendar_client.py:447`
- **What**: トークン保存時に親ディレクトリ作成保証がない箇所がある。
- **Why**: 初回環境やパッケージ実行環境でディレクトリ未作成だと認証成功後の保存で失敗し、次回以降の認証が不安定化する。
- **How**: トークン保存前に `TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)` を統一実施する。
- **Confidence**: Medium

### F-009 / Low / Maintainability
- **Location**: `src/calendar_client.py:614`, `src/calendar_client.py:362`, `src/calendar_client.py:496`
- **What**: 一部で `account['id']` の直接参照を使用し、設定ファイル異常時に `KeyError` を誘発する。
- **Why**: ユーザー編集や破損データ時の復旧性が低く、読み込み処理が途中停止する。
- **How**: `.get()` を使用した防御的パースに統一し、破損エントリをスキップして継続する。
- **Confidence**: Medium

## 4. Suggested Next Steps（次アクション案）
1. マルチアカウント系の接続を再設計し、`CalendarClient` の取得経路を単一責務に統一する（単一/複数の分岐を除去）。
2. イベント取得処理を共通関数化してページネーションを必須化し、件数上限に依存しない取得へ修正する。
3. `WallpaperService` をワーカー単位で分離し、プレビューと本適用の並列競合をなくす。
4. 起動シーケンスに `settings_service.load()` を組み込み、UI初期値とViewModelへ同期反映する。
5. プレビューの高速化（イベントキャッシュ・低解像度レンダリング・非保存）を先に実装し、API負荷を計測する。
6. JSON保存ファイルの権限管理を共通ユーティリティ化し、`accounts/settings/cache` へ適用する。
7. 失敗時UI復旧（applyボタン再有効化、具体エラー表示）を追加し、操作不能状態を排除する。
8. テスト実行環境の異常終了（pytest exit -1）を切り分け、CI/ローカル双方で再現可能なテスト導線を整備する。

## 5. Notes（備考）
- このプロジェクトはWebアプリ構成ではなく、**PyQt6デスクトップアプリ**（MVVM + Service）である。
- 永続化ストアはRDB/NoSQLではなく、`settings.json` / `accounts.json` / token JSON の**ファイルベース**。
- 「フロントエンド・バックエンド接続」は、Web APIではなく `UI(MainWindow)` → `MainViewModel` → `WallpaperService` → `CalendarClient/ImageGenerator/WallpaperSetter` の内部呼び出しで構成される。
