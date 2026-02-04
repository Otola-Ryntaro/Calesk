# 007: GUIアプリケーション化

## 優先度
**MEDIUM**

## 概要
現在のCLIベースのカレンダー壁紙アプリをGUIアプリケーション化し、ユーザーフレンドリーな操作を実現する

## 現状
- [ ] CLIでのみ操作可能（`python main.py`）
- [ ] 設定変更にはconfig.pyの直接編集が必要
- [ ] テーマの視覚的なプレビューがない
- [ ] 一般ユーザーには使いづらい

## 目標
- [ ] GUIで全ての操作が完結する
- [ ] テーマの視覚的なプレビューが可能
- [ ] 設定変更が簡単にできる
- [ ] 一般ユーザーでも簡単に使える

## UI設計案

### メイン画面
```
┌─────────────────────────────────────────┐
│  カレンダー壁紙アプリ              [×]  │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │      壁紙プレビュー              │   │
│  │      (640x360)                  │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  テーマ: [▼ simple]  🎨               │
│  ┌───┬───┬───┬───┬───┐              │
│  │sim│mod│pas│dar│vib│              │
│  └───┴───┴───┴───┴───┘              │
│                                         │
│  ディスプレイ: [▼ Desktop 1]           │
│  自動更新: [✓] 毎日 06:00              │
│                                         │
│  [今すぐ更新]  [設定]  [カレンダー連携] │
│                                         │
└─────────────────────────────────────────┘
```

### 設定画面
```
┌─────────────────────────────────────────┐
│  設定                              [×]  │
├─────────────────────────────────────────┤
│                                         │
│  【表示設定】                            │
│  解像度: [1920] × [1080]               │
│  フォントサイズ:                         │
│    タイトル: [60]  イベント: [32]       │
│                                         │
│  【テーマ設定】                          │
│  カードの影: [✓] 有効                   │
│  背景画像: [参照...]                    │
│                                         │
│  【自動更新設定】                        │
│  自動更新: [✓] 有効                     │
│  更新時刻: [06]:[00]                    │
│  起動時に自動更新: [✓]                  │
│                                         │
│  【マルチディスプレイ】                  │
│  対象ディスプレイ: [▼ Desktop 1]        │
│  解像度自動検出: [✓] 有効               │
│                                         │
│  [保存]  [キャンセル]                   │
│                                         │
└─────────────────────────────────────────┘
```

### カレンダー連携画面
```
┌─────────────────────────────────────────┐
│  Google Calendar連携           [×]      │
├─────────────────────────────────────────┤
│                                         │
│  状態: ✓ 接続済み                       │
│  アカウント: user@gmail.com             │
│                                         │
│  カレンダーID:                          │
│  ┌───────────────────────────────────┐  │
│  │ [✓] primary (主カレンダー)         │  │
│  │ [ ] work@group.calendar.google.com│  │
│  │ [ ] personal@...                  │  │
│  └───────────────────────────────────┘  │
│                                         │
│  [再接続]  [認証解除]                   │
│                                         │
└─────────────────────────────────────────┘
```

## 技術スタック決定

### ✅ 採用: PyQt6（Codex推奨）

**選定理由**:
- プレビュー機能に必要な高度な画像表示機能
- システムトレイ統合が標準サポート
- QListWidget、QComboBox等のリッチなウィジェット
- クロスプラットフォーム対応が成熟
- Qt Designerによる効率的なUI設計

**トレードオフ**:
- 依存関係の追加（PyQt6パッケージ）
- アプリサイズ増加（約50-80MB）
- ライセンス: GPL v3（個人利用・オープンソースは問題なし）

### 却下した選択肢

**Tkinter**:
- ❌ プレビュー機能の実装が複雑
- ❌ システムトレイのサポートが限定的
- ❌ モダンなUIデザインに制約

**Electron**:
- ❌ アプリサイズが大きすぎる（100MB+）
- ❌ Python統合の複雑さ
- ❌ リソース消費が多い

## アーキテクチャ設計（MVVM）

Codex推奨のMVVMアーキテクチャを採用：

```
core/           # 既存のCLIロジック（変更なし）
├── calendar_fetcher.py
├── image_generator.py
├── themes.py
└── ...

ui/             # PyQt6 Views（UI層）
├── main_window.py
├── settings_dialog.py
├── calendar_dialog.py
└── widgets/
    ├── preview_widget.py
    └── theme_gallery.py

viewmodels/     # ビジネスロジック（UI ↔ Core の橋渡し）
├── main_viewmodel.py
├── settings_viewmodel.py
└── wallpaper_service.py
```

**メリット**:
- 既存コードの再利用（core/は変更不要）
- UIとビジネスロジックの分離
- テストしやすい構造
- 将来的なCLI維持が容易

## 実装計画

### Phase 1: 環境構築とアーキテクチャ基盤 ✅
- [x] PyQt6のインストール（requirements.txt更新）
- [x] MVVMディレクトリ構造の作成（ui/, viewmodels/）
- [x] 基本的なViewModelベースクラスの実装
- [x] WallpaperServiceの実装（core/との連携）
- [x] pytest-qtのセットアップ
- [x] Codexコードレビュー実施（評価: good, スコア: 7/10）

### Phase 2: メインウィンドウとプレビュー
- [ ] MainWindowの作成（PyQt6）
- [ ] PreviewWidgetの実装（QLabel/QPixmap使用）
- [ ] テーマ選択ComboBoxの実装
- [ ] テーマギャラリー（QListWidget）
- [ ] リアルタイムプレビュー機能
- [ ] 「今すぐ更新」ボタンと進捗表示

### Phase 3: 設定ダイアログ
- [ ] SettingsDialogの作成
- [ ] 表示設定タブ（解像度、フォントサイズ）
- [ ] テーマ設定タブ（影、背景画像選択）
- [ ] 自動更新設定タブ（時刻、有効/無効）
- [ ] マルチディスプレイ設定タブ
- [ ] 設定の永続化（config.py更新）

### Phase 4: カレンダー連携UI
- [ ] CalendarDialogの作成
- [ ] Google Calendar認証状態表示
- [ ] カレンダーID選択（QCheckBox）
- [ ] 再接続/認証解除ボタン
- [ ] 認証フローのエラーハンドリング

### Phase 5: システム統合
- [ ] QSystemTrayIconの実装
- [ ] システムトレイメニュー（更新、設定、終了）
- [ ] QNotificationの実装（更新完了通知）
- [ ] 自動起動連携（既存スクリプト統合）
- [ ] クロスプラットフォームテスト（macOS/Windows）

### Phase 6: パッケージング
- [ ] PyInstallerセットアップ
- [ ] .app作成（macOS）
- [ ] .exe作成（Windows）
- [ ] アイコンファイルの作成
- [ ] インストーラーの検討（オプション）

## 実装ファイル構成（MVVM）

```
src/
├── core/                    # 既存のCLIロジック（変更なし）
│   ├── __init__.py
│   ├── calendar_fetcher.py
│   ├── image_generator.py
│   ├── themes.py
│   ├── wallpaper_setter.py
│   ├── scheduler.py
│   └── display_info.py
│
├── viewmodels/              # ビジネスロジック層（新規）
│   ├── __init__.py
│   ├── main_viewmodel.py    # メイン画面のロジック
│   ├── settings_viewmodel.py # 設定画面のロジック
│   ├── calendar_viewmodel.py # カレンダー連携のロジック
│   └── wallpaper_service.py  # 壁紙生成サービス
│
├── ui/                      # PyQt6 UI層（新規）
│   ├── __init__.py
│   ├── main_window.py       # メインウィンドウ
│   ├── settings_dialog.py   # 設定ダイアログ
│   ├── calendar_dialog.py   # カレンダー連携ダイアログ
│   ├── system_tray.py       # システムトレイ
│   └── widgets/
│       ├── __init__.py
│       ├── preview_widget.py    # プレビュー表示
│       └── theme_gallery.py     # テーマギャラリー
│
├── main.py                  # CLIエントリーポイント（既存）
└── main_gui.py              # GUIエントリーポイント（新規）
```

## 使用ライブラリ（追加）

### 必須
- `PyQt6==6.6.1`: GUIフレームワーク
- `PyQt6-Qt6==6.6.1`: Qt6ライブラリ
- `Pillow`: 画像処理（既存）

### 開発・テスト
- `pytest-qt==4.3.1`: PyQt6のテストフレームワーク
- `pytest`: テストランナー（既存）

### パッケージング
- `pyinstaller==6.3.0`: .app/.exe作成

## テスト戦略（pytest-qt）

### ユニットテスト（ViewModels）
- [ ] WallpaperServiceのテスト（core/との連携）
- [ ] MainViewModelのテスト（状態管理）
- [ ] SettingsViewModelのテスト（設定の読み書き）
- [ ] CalendarViewModelのテスト（認証状態管理）

### UIテスト（pytest-qt）
- [ ] MainWindowの表示テスト（qtbot.addWidget）
- [ ] テーマ選択の動作テスト
- [ ] 「今すぐ更新」ボタンのクリックテスト
- [ ] プレビュー表示のテスト
- [ ] SettingsDialogの開閉テスト
- [ ] システムトレイアイコンのテスト

### 統合テスト
- [ ] 壁紙生成からプレビュー表示までの流れ
- [ ] 設定変更の永続化
- [ ] マルチディスプレイ対応の動作確認
- [ ] クロスプラットフォーム動作確認（macOS/Windows）

## クロスプラットフォーム考慮事項

### 壁紙設定
- **macOS**: `osascript` (AppleScript) - 既存実装を流用
- **Windows**: `ctypes.windll.user32.SystemParametersInfoW` - 既存実装を流用
- **Linux**: 複数のDE対応（GNOME、KDE、XFCE等） - 既存実装を流用

### フォント
- **デフォルトフォント**: OS標準フォントを使用
- **日本語フォント**: 既存のヒラギノ/Notoフォント検出ロジックを流用
- **フォールバック**: システムデフォルトフォント

### スケジューラー統合
- **macOS**: launchd設定の読み書き
- **Windows**: タスクスケジューラー設定の読み書き
- **GUI統合**: 自動更新ON/OFFをGUIから制御

## 成功基準
- [ ] GUIで全ての基本操作が完結する
- [ ] 設定ファイルを直接編集する必要がない
- [ ] テーマのビジュアルプレビューが見られる
- [ ] 一般ユーザーが直感的に使える
- [ ] macOS/Windowsで動作する（Linux対応は将来）
- [ ] CLIモードも引き続き利用可能
- [ ] 既存のcore/ロジックは変更なし（再利用）

## Codexレビュー結果と対応

### 総合評価
**`needs_improvement`** （改善が必要） / 承認: **`with_modifications`** （修正を加えて実装可）

### 🔴 HIGH優先度の対応

#### 1. ViewModelの責務分離（アーキテクチャ）
**懸念**: ViewModelとcore/の境界が曖昧で、UIイベント処理が肥大化するリスク

**対応方針**:
- ViewModelは状態管理とコマンド実行のみに限定
- core/との橋渡しはService層（WallpaperService等）に集約
- ViewModel → Service → Core の明確な依存関係を定義

**実装ルール**:
```python
# ViewModel: 状態管理のみ
class MainViewModel:
    def __init__(self, wallpaper_service: WallpaperService):
        self.service = wallpaper_service
        self.current_theme = "simple"
        self.is_updating = False

    def update_wallpaper(self):
        self.is_updating = True
        result = self.service.generate_and_set_wallpaper(self.current_theme)
        self.is_updating = False
        return result

# Service: core/との橋渡し
class WallpaperService:
    def generate_and_set_wallpaper(self, theme_name: str):
        # core/のImageGeneratorを使用
        generator = ImageGenerator()
        generator.set_theme(theme_name)
        # ...
```

#### 2. ライセンス方針の明確化（技術選定）
**懸念**: PyQt6のGPLライセンスは配布形態によって制約が強くなる可能性

**対応方針**:
- **現在の方針**: 個人利用・オープンソースプロジェクトとして PyQt6 GPL v3 で実装
- **将来の選択肢**: 商用配布が必要になった場合は PySide6 (LGPL) への移行を検討
- **移行容易性**: PyQt6とPySide6のAPIは99%互換性があり、移行コストは低い

**配布形態の定義**:
- ✅ 個人利用: GPL v3 問題なし
- ✅ オープンソース公開（MIT/Apache等）: GPL v3 問題なし（アプリ全体がGPL互換）
- ⚠️ クローズドソース配布: PySide6への移行が必要

### 🟡 MEDIUM優先度の対応

#### 3. Pillow/QPixmap変換の最適化
**対応方針**:
- Pillow Image → 一時ファイル → QPixmap のパスを採用（メモリ効率重視）
- プレビュー用サムネイルは縮小版をキャッシュ（640x360固定）
- テーマギャラリーは起動時に軽量サムネイルを事前生成（160x90）

#### 4. 設定の永続化方法の変更
**対応方針**:
- `config.py` は読み込み専用のデフォルト設定として維持
- ユーザー設定は `~/.calendar_wallpaper/settings.json` に保存
- GUI起動時: settings.json → config.py の順でマージ読み込み

**実装例**:
```python
# src/viewmodels/settings_service.py
class SettingsService:
    def load_settings(self):
        defaults = vars(config)  # config.pyから読み込み
        user_settings = self._load_json("~/.calendar_wallpaper/settings.json")
        return {**defaults, **user_settings}

    def save_settings(self, settings: dict):
        self._save_json("~/.calendar_wallpaper/settings.json", settings)
```

#### 5. システムトレイのOS別対応
**対応方針**:
- **macOS**: QSystemTrayIcon動作確認、非対応の場合はメニューバーアプリとして実装
- **Windows**: QSystemTrayIcon標準動作
- **代替UI**: トレイが使えない場合はメインウィンドウを常に表示

#### 6. PyInstallerビルドの検証項目
**Phase 6に追加**:
- [ ] macOS用specファイル作成（Qtプラグイン、Pillow含む）
- [ ] Windows用specファイル作成（同上）
- [ ] ビルド後スモークテスト（起動、プレビュー表示、壁紙生成）
- [ ] 各OSでの動作確認チェックリスト

#### 7. テスト戦略の見直し
**対応方針**:
- UIテストは可視UI（MainWindow、SettingsDialog）のみを対象
- システムトレイ・通知機能はViewModel単体テストと手動検証に分離
- 不安定なUIテストは `@pytest.mark.manual` でマーク

#### 8. リアルタイムプレビューの非同期化
**Phase 2に追加**:
- [ ] QThread または QtConcurrent でプレビュー生成を非同期化
- [ ] UI更新はメインスレッド（Qt Signal/Slot）で実行
- [ ] プレビュー生成中は進捗インジケーター表示

### 💡 追加提案の反映

#### 9. CLI/GUI共通の設定API
**Phase 1に追加**:
- [ ] `src/core/settings_manager.py` を作成（CLI/GUI共通）
- [ ] config.py と settings.json の統合読み込み
- [ ] 設定変更の永続化API

#### 10. テーマギャラリーの最適化
**Phase 2に追加**:
- [ ] テーマサムネイル事前生成（起動時、非同期）
- [ ] サムネイルキャッシュ（`~/.calendar_wallpaper/thumbnails/`）
- [ ] ギャラリー表示時はキャッシュから読み込み

#### 11. 技術検証の早期化
**Phase 2の最優先タスク**:
- [ ] 最小プレビュー実装（Pillow → QPixmap変換検証）
- [ ] テーマ切り替え動作確認
- [ ] メモリ使用量・パフォーマンス測定

#### 12. Google Calendar認証フローの早期試作
**Phase 4の前に検証フェーズを追加**:
- [ ] GUIでのブラウザ起動（`webbrowser.open()`）
- [ ] OAuthリダイレクトURL受信（ローカルサーバー起動）
- [ ] 認証トークン保存・復元

#### 13. Linux対応の明示
**現時点の方針**:
- ❌ Linux対応は Phase 8 では実装しない
- 📋 将来対応予定として記載
- 🔧 LinuxでGUIを起動した場合は「未対応」メッセージを表示

## Codexレビュー完了チェックリスト
- [x] MVVMアーキテクチャの採用
- [x] PyQt6の選定理由と正当化
- [x] 既存コード（core/）の再利用計画
- [x] クロスプラットフォーム考慮事項の明示
- [x] テスト戦略（pytest-qt）の策定
- [x] Codexによる実装計画レビュー
- [x] HIGH優先度の懸念事項への対応方針策定
- [x] MEDIUM優先度の懸念事項への対応方針策定
- [x] 追加提案の実装計画への組み込み

## 備考
- Phase 1から段階的に実装（TDD原則に従う）
- 既存のCLI機能は維持（main.pyは変更なし）
- パッケージング（.app、.exe化）はPhase 6で対応
- システムトレイ統合はOSごとに動作が異なるため、慎重に実装
- ライセンス: PyQt6はGPL v3（個人利用・オープンソースOK）

## 関連チケット
- [005_autostart_system.md](005_autostart_system.md): 自動起動システム（GUIから設定変更可能にする）
- [006_theme_system_improvement.md](006_theme_system_improvement.md): テーマシステム改善（GUIでテーマプレビュー）
