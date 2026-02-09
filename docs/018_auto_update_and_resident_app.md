# チケット018: 自動更新機能 + 常駐アプリ化

## 概要

1時間ごとにスケジュールを再取得し壁紙を自動更新する機能を追加。
最終的にはシステムトレイ常駐アプリとして動作させる。

## 要件

### Phase 1: 自動更新（QTimer方式）
- GUIアプリ起動中、1時間に1回自動的に壁紙を更新
- Google Calendarからスケジュールを再取得
- 壁紙画像を再生成
- デスクトップ壁紙を更新
- 手動「今すぐ更新」も維持

### Phase 2: UI統合
- 自動更新ON/OFFチェックボックス
- 次回更新時刻の表示
- 更新間隔の設定（15分/30分/1時間/2時間/4時間）

### Phase 3: 堅牢性
- ネットワークエラー時のリトライ（最大3回、5分間隔）
- 認証失敗時の自動停止と通知
- macOSスリープ復帰検知（補助タイマーで経過時間チェック）

### Phase 4: 常駐アプリ化
- **macOS**: メニューバーアイコン（`QSystemTrayIcon`）
  - トレイアイコンクリックでメニュー表示
  - 「今すぐ更新」「設定」「終了」メニュー
  - ウィンドウを閉じてもバックグラウンド動作
- **Windows**: システムトレイアイコン
  - 右クリックメニュー
  - バルーン通知

### Phase 5: アプリケーション配布
- macOS: `.app` バンドル（PyInstaller or py2app）
- ログイン時自動起動（LaunchAgent / スタートアップ登録）

## 技術選定: QTimer方式（推奨）

### 選定理由
1. PyQt6のイベントループに完全統合、スレッド安全
2. 新規依存不要（既存のscheduleライブラリとは別用途）
3. 既存の `update_wallpaper()` をそのまま呼び出し可能
4. `_is_updating` フラグによる多重実行防止が既存コードで動作
5. `pytest-qt` でテスト容易

### 他方式との比較

| 評価軸 | QTimer（採用） | schedule+threading | APScheduler |
|---|---|---|---|
| 実装コスト | 低（約30行） | 中（約60行） | 低（約20行） |
| スレッド安全性 | 完全に安全 | 要対策 | 安全 |
| 新規依存 | なし | なし | 追加必要 |
| スリープ復帰 | 要追加実装 | 要追加実装 | 組み込み済み |

## 実装概要

### Phase 1: MainViewModel への追加

```python
from PyQt6.QtCore import QTimer

class MainViewModel(ViewModelBase):
    auto_update_status_changed = pyqtSignal(bool)
    next_update_time_changed = pyqtSignal(str)

    def __init__(self, ...):
        ...
        self._auto_update_timer = QTimer(self)
        self._auto_update_timer.timeout.connect(self._on_auto_update_timeout)
        self._update_interval_ms = AUTO_UPDATE_INTERVAL_MINUTES * 60 * 1000

    def start_auto_update(self):
        self._auto_update_timer.start(self._update_interval_ms)
        self.auto_update_status_changed.emit(True)

    def stop_auto_update(self):
        self._auto_update_timer.stop()
        self.auto_update_status_changed.emit(False)

    def _on_auto_update_timeout(self):
        self.update_wallpaper()  # 既存メソッド再利用
```

### Phase 4: システムトレイ

```python
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu

class TrayIcon(QSystemTrayIcon):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon('assets/tray_icon.png'))
        menu = QMenu()
        menu.addAction("今すぐ更新", viewmodel.update_wallpaper)
        menu.addAction("設定", self._show_settings)
        menu.addSeparator()
        menu.addAction("終了", QApplication.quit)
        self.setContextMenu(menu)
```

## タスク

### Phase 1: 自動更新 MVP ✅
- [x] `config.py` に `AUTO_UPDATE_INTERVAL_MINUTES`, `AUTO_UPDATE_ENABLED_DEFAULT` を追加 ✅
- [x] テスト作成（TDD） ✅
- [x] `MainViewModel` に QTimer、`start_auto_update()`, `stop_auto_update()` を追加 ✅
- [x] `MainWindow` 起動時に `start_auto_update()` 呼び出し ✅
- [x] `closeEvent` にタイマー停止追加 ✅

### Phase 2: UI統合 ✅
- [x] 自動更新ON/OFFチェックボックス追加（SettingsDialog内）
- [x] 次回更新時刻ラベル追加（MainWindow）
- [x] 更新間隔選択UI追加（SettingsDialog SpinBox: 15-480分）
- [x] 設定変更のリアクティブ反映（on_settings_changed）

### Phase 3: 堅牢性
- [x] リトライロジック実装（最大3回、5分間隔、config.pyで設定可能）
- [x] 認証失敗時の自動停止（認証エラーキーワード検出で自動停止＋通知）
- [x] スリープ復帰検知（補助タイマーで経過時間チェック、1分間隔/120秒閾値）

### Phase 4: 常駐アプリ化
- [x] `QSystemTrayIcon` 実装（システムトレイ利用可能チェック付き）
- [x] トレイメニュー実装（今すぐ更新/設定/表示/終了）
- [x] ウィンドウ非表示でバックグラウンド動作（closeEvent修正）
- [x] トレイアイコン（システムデフォルトアイコン使用）

### Phase 5: 配布
- [x] PyInstaller / py2app での `.app` バンドル
- [x] ログイン時自動起動設定

## 変更ファイル

- `src/config.py` - 自動更新設定
- `src/viewmodels/main_viewmodel.py` - QTimer追加
- `src/ui/main_window.py` - UI統合、トレイアイコン

## 新規ファイル（Phase 4以降）

- `src/ui/tray_icon.py` - システムトレイアイコン
- `assets/tray_icon.png` - トレイアイコン画像

## Phase 5 実装詳細

### ビルド設定

- **ツール**: PyInstaller 6.18.0
- **理由**: Python 3.13対応、PyQt6サポート、Apple Silicon対応、クロスプラットフォーム
- **設定ファイル**: `CalendarWallpaper.spec`
- **ビルドスクリプト**: `scripts/build_app.sh`
- **バンドルサイズ**: 約191MB

### ログイン時自動起動

- **方式**: macOS LaunchAgent
- **plistファイル**: `com.example.calendarwallpaper.plist`
- **配置先**: `~/Library/LaunchAgents/`
- **インストールスクリプト**: `scripts/install_app.sh`
- **アンインストールスクリプト**: `scripts/uninstall_app.sh`

### ドキュメント

詳細は [docs/BUILD.md](BUILD.md) を参照。

## 優先度: MEDIUM（Phase 1は HIGH）
## 工数: Phase 1: 小（2時間）、Phase 2-3: 中（3時間）、Phase 4-5: 大（6-8時間）
## ステータス: ✅ 全Phase完了
