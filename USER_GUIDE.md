# Calendar Wallpaper Desktop - ユーザーガイド

詳細な使い方、設定、トラブルシューティングガイド

## 目次

1. [インストールと初期設定](#インストールと初期設定)
2. [基本的な使い方](#基本的な使い方)
3. [テーマのカスタマイズ](#テーマのカスタマイズ)
4. [詳細設定](#詳細設定)
5. [自動起動の設定](#自動起動の設定)
6. [トラブルシューティング](#トラブルシューティング)
7. [開発者向け情報](#開発者向け情報)

---

## インストールと初期設定

### システム要件

- **OS**: macOS 10.15以上 / Linux / Windows 10以上
- **Python**: 3.13以上
- **メモリ**: 512MB以上
- **ディスク**: 100MB以上の空き容量
- **インターネット**: Google Calendar API接続に必要

### 依存パッケージ

以下のパッケージが自動的にインストールされます（詳細は`requirements.txt`を参照）:

```text
google-api-python-client  # Google Calendar API
google-auth-oauthlib      # OAuth2認証
Pillow                    # 画像生成
PyQt6                     # GUIフレームワーク
plyer                     # 通知機能
schedule                  # スケジューラー
python-dotenv             # 環境変数管理
```

### Google Calendar API設定（詳細）

#### 1. Google Cloud Consoleでプロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 「プロジェクトを作成」をクリック
3. プロジェクト名を入力（例: "カレンダー壁紙アプリ"）

#### 2. Google Calendar APIを有効化

1. 「APIとサービス」→「ライブラリ」に移動
2. "Google Calendar API"を検索
3. 「有効にする」をクリック

#### 3. OAuth 2.0クライアントIDを作成

1. 「APIとサービス」→「認証情報」に移動
2. 「認証情報を作成」→「OAuth クライアント ID」を選択
3. アプリケーションの種類: **デスクトップアプリ**
4. 名前を入力（例: "カレンダー壁紙アプリクライアント"）
5. 「作成」をクリック

#### 4. credentials.jsonのダウンロード

1. 作成した認証情報の右側にあるダウンロードアイコンをクリック
2. ダウンロードしたファイルを`credentials.json`にリネーム
3. `credentials/`ディレクトリに配置

#### 5. 初回認証

```bash
# 認証フローを実行
python main.py --auth
```

ブラウザが開き、以下の手順が実行されます：
1. Googleアカウントでログイン
2. アプリにカレンダーへのアクセス許可を付与
3. `token.json`が自動生成される

---

## 基本的な使い方

### GUI版（推奨）

#### 起動方法

```bash
python run_gui.py
```

#### GUI画面の構成

```
┌─────────────────────────────────────────┐
│ カレンダー壁紙アプリ                     │
├─────────────────────────────────────────┤
│ テーマ: [simple ▼]  [今すぐ更新]         │
├─────────────────────────────────────────┤
│                                         │
│         壁紙プレビュー表示エリア          │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

#### 操作手順

1. **テーマ選択**: ドロップダウンから好きなテーマを選択
2. **更新ボタン**: 「今すぐ更新」をクリックで壁紙を生成
3. **プレビュー**: 生成された壁紙がプレビュー表示される
4. **自動適用**: 壁紙が自動的にデスクトップに設定される

### CLI版

#### ワンショットモード（即座に更新）

```bash
python main.py --run-once
```

- Google Calendarから予定を取得
- 壁紙を生成
- デスクトップに設定
- 完了通知を表示

#### デーモンモード（常駐・自動更新）

```bash
python main.py --daemon
```

**機能**:
- 毎日6:00に壁紙を自動更新
- 5分ごとにイベント通知をチェック
- 予定開始5分前にデスクトップ通知
- 重複通知を自動防止

**停止方法**:
```bash
# プロセスIDを確認
ps aux | grep "python main.py --daemon"

# プロセスを停止
kill <プロセスID>
```

---

## テーマのカスタマイズ

### 利用可能なテーマ

#### 1. simple（シンプル）

```python
THEME = 'simple'
```

- **特徴**: シンプルで見やすいデザイン
- **背景**: 背景画像を使用
- **カード**: 白背景、角丸なし、黒文字
- **用途**: 業務用、シンプルなデザインが好みの方向け

#### 2. modern（モダン）

```python
THEME = 'modern'
```

- **特徴**: 洗練された現代的なデザイン
- **背景**: 背景画像を使用
- **カード**: 半透明白カード、大きめの角丸、影付き
- **用途**: おしゃれなデスクトップ環境を求める方向け

#### 3. pastel（パステル）

```python
THEME = 'pastel'
```

- **特徴**: 優しく柔らかい印象
- **背景**: 背景画像を使用
- **カード**: 淡い色、角丸あり、パステルカラー
- **用途**: 柔らかい雰囲気が好みの方向け

#### 4. dark（ダーク）

```python
THEME = 'dark'
```

- **特徴**: 高級感のあるダークモード
- **背景**: 背景画像を使用
- **カード**: 半透明黒カード、ゴールドアクセント
- **用途**: ダークモード好きの方向け

#### 5. vibrant（鮮やか）

```python
THEME = 'vibrant'
```

- **特徴**: 元気で鮮やかなデザイン
- **背景**: 背景画像を使用
- **カード**: 鮮やかな色、角丸あり
- **用途**: ポップで明るい雰囲気が好みの方向け

#### 6. luxury（ラグジュアリー）

```python
THEME = 'luxury'
```

- **特徴**: 高級感のあるミニマルデザイン
- **背景**: アイボリーホワイト基調
- **カード**: ゴールドアクセント、繊細な枠線
- **用途**: 上品で落ち着いたデスクトップ環境向け

#### 7. playful（プレイフル）

```python
THEME = 'playful'
```

- **特徴**: 遊び心のある柔らかいデザイン
- **背景**: ウォームホワイト基調
- **カード**: コーラルピンク枠、大きめの角丸、ターコイズアクセント
- **用途**: 明るくカジュアルな雰囲気が好みの方向け

### テーマの変更方法

#### GUI経由（推奨）

1. GUIを起動
2. 「テーマ:」ドロップダウンから選択
3. 「今すぐ更新」をクリック
4. プレビューで確認

#### 設定ファイル経由

`src/config.py`を編集：

```python
# テーマ設定
THEME = 'modern'  # simple, modern, pastel, dark, vibrant, luxury, playful
```

---

## 詳細設定

### 画像設定

```python
# 解像度
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# 解像度の自動検出
AUTO_DETECT_RESOLUTION = True  # True推奨

# 背景色
BACKGROUND_COLOR = (255, 255, 255)  # RGB

# 文字色
TEXT_COLOR = (0, 0, 0)  # RGB
```

### マルチディスプレイ設定

```python
# 壁紙を適用するデスクトップ番号
# 0 = 全デスクトップ
# 1 = desktop 1のみ（現在の設定）
# 2 = desktop 2のみ
WALLPAPER_TARGET_DESKTOP = 1
```

**使用例**:
- メインディスプレイのみ: `WALLPAPER_TARGET_DESKTOP = 1`
- 外部ディスプレイのみ: `WALLPAPER_TARGET_DESKTOP = 2`
- 全ディスプレイ: `WALLPAPER_TARGET_DESKTOP = 0`

### フォント設定

```python
# システムにインストールされている日本語フォントのパス
FONT_PATHS = {
    'Darwin': '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
    'Windows': 'C:/Windows/Fonts/msgothic.ttc',
    'Linux': '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'
}

# フォントサイズ
FONT_SIZE_DATE = 24        # 日付ヘッダー
FONT_SIZE_TITLE = 20       # 予定タイトル
FONT_SIZE_TIME = 16        # 時刻
FONT_SIZE_DAY_HEADER = 16  # 曜日ヘッダー
FONT_SIZE_EVENT_BLOCK = 11 # イベントブロック内テキスト
```

### 通知設定

```python
# 予定開始何分前に通知
NOTIFICATION_ADVANCE_MINUTES = 5

# 通知チェック間隔（秒）
CHECK_INTERVAL_SECONDS = 300  # 5分
```

### スケジューラー設定

```python
# 壁紙更新時刻（HH:MM形式）
UPDATE_TIME = '06:00'
```

---

## 自動起動の設定

### macOS（launchd）

自動起動設定スクリプトが用意されています（別チケットで実装予定）。

手動設定の場合：

1. `~/Library/LaunchAgents/`に`.plist`ファイルを作成
2. デーモンモードで起動するように設定
3. `launchctl load`でサービスを登録

### Windows（タスクスケジューラー）

1. タスクスケジューラーを開く（`Win + R` → `taskschd.msc`）
2. 「タスクの作成」をクリック
3. トリガー: 毎日6:00
4. 操作: `python main.py --run-once`を実行

### Linux（systemd / cron）

#### cron（推奨）

```bash
# crontabを編集
crontab -e

# 毎日6:00に実行
0 6 * * * /path/to/venv/bin/python /path/to/calender_desktop/main.py --run-once
```

---

## トラブルシューティング

### 認証関連

#### エラー: `credentials.json not found`

**原因**: Google Cloud Consoleからダウンロードした認証ファイルが見つからない

**解決方法**:

1. `credentials.json`が`credentials/`ディレクトリに配置されているか確認
2. ファイル名が正確に`credentials.json`であることを確認

#### エラー: `The authentication token has expired`

**原因**: 認証トークンの有効期限切れ

**解決方法**:
```bash
rm credentials/token.json
python main.py --auth
```

### フォント関連

#### エラー: `Font not found`または文字化け

**原因**: 日本語フォントが見つからない

**解決方法**:

1. システムにインストールされている日本語フォントを確認:
   ```bash
   # macOS
   ls /System/Library/Fonts/

   # Linux
   fc-list :lang=ja
   ```

2. `src/config.py`の`FONT_PATHS`を実際のパスに修正

### 画像生成関連

#### エラー: `PIL.UnidentifiedImageError`

**原因**: 背景画像が破損しているか、サポートされていない形式

**解決方法**:
1. `assets/background.jpg`が存在するか確認
2. PNG、JPG、JPEG形式の画像を使用

#### 壁紙が更新されない

**原因**: 複数の可能性

**解決方法**:

1. **権限確認**: 壁紙変更の権限があるか確認
   ```bash
   # macOS: システム環境設定 → セキュリティとプライバシー
   ```

2. **ログ確認**:
   ```bash
   tail -f calendar_app.log
   ```

3. **手動実行でテスト**:
   ```bash
   python main.py --run-once
   ```

### Google Calendar関連

#### イベントが表示されない

**原因**: カレンダーへのアクセス権限、または時刻範囲の問題

**解決方法**:

1. **認証スコープ確認**: 再認証を実行
   ```bash
   rm credentials/token.json
   python main.py --auth
   ```

2. **カレンダーの確認**: Google Calendarで実際に予定が存在するか確認

3. **ログで詳細確認**:
   ```bash
   python main.py --run-once --log-level DEBUG
   ```

### GUIが起動しない

#### macOS: `ImportError: PyQt6`

**原因**: PyQt6が正しくインストールされていない

**解決方法**:
```bash
pip install --upgrade PyQt6
```

#### エラー: `QApplication: invalid style override`

**原因**: スタイル設定の問題（通常は警告で無視可能）

**解決方法**: 警告は無視して問題ありません

---

## 開発者向け情報

### テスト実行

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付き
pytest tests/ --cov=src --cov-report=html

# 特定のテストファイルのみ
pytest tests/test_calendar_client.py -v
```

テスト数: 614件

### ディレクトリ構造

```text
calender_desktop/
├── src/                          # ソースコード
│   ├── models/                   # データモデル
│   │   └── event.py              # CalendarEventモデル
│   ├── renderers/                # 描画Mixin
│   │   ├── effects.py            # エフェクト描画（ガラスモーフィズム等）
│   │   ├── card_renderer.py      # イベントカード描画
│   │   └── calendar_renderer.py  # 週間カレンダー描画
│   ├── ui/                       # GUI関連
│   │   ├── main_window.py        # メインウィンドウ
│   │   ├── settings_dialog.py    # 設定ダイアログ
│   │   └── widgets/              # カスタムウィジェット
│   ├── viewmodels/               # ViewModel層
│   │   ├── main_viewmodel.py     # メインViewModel
│   │   └── wallpaper_service.py  # 壁紙生成サービス
│   ├── calendar_client.py        # Google Calendar API（複数アカウント対応）
│   ├── image_generator.py        # 壁紙画像生成（省メモリ設計）
│   ├── display_info.py           # ディスプレイ情報取得
│   ├── wallpaper_cache.py        # 壁紙キャッシュ管理
│   ├── wallpaper_setter.py       # 壁紙設定
│   ├── notifier.py               # 通知機能
│   ├── scheduler.py              # スケジューラー
│   ├── themes.py                 # テーマ定義（7種）
│   └── config.py                 # 設定ファイル
├── tests/                        # テストコード（614件）
├── docs/                         # 開発ドキュメント
├── assets/                       # リソース（背景画像等）
├── credentials/                  # 認証情報（.gitignore対象）
├── main.py                       # CLIエントリーポイント
├── run_gui.py                    # GUIエントリーポイント
├── requirements.txt              # 依存パッケージ
├── README.md                     # プロジェクト概要
└── USER_GUIDE.md                 # このファイル
```

### アーキテクチャ

```text
MVVM + Service層

UI (PyQt6)  ->  ViewModel  ->  WallpaperService  ->  ImageGenerator / CalendarClient
                                                       |-- EffectsRendererMixin
                                                       |-- CardRendererMixin
                                                       +-- CalendarRendererMixin
```

### コーディング規約

- **命名**: PEP 8に準拠
- **型ヒント**: すべての関数に型ヒントを付与
- **docstring**: Google Style Docstring
- **テスト**: TDD（テスト駆動開発）
- **テストカバレッジ**: 80%以上を維持

### コントリビューション

1. Forkしてブランチを作成
2. TDDでテストを先に書く
3. コードを実装してテストをパス
4. プルリクエストを作成

---

## FAQ

### Q: 複数のGoogleアカウントで使用できますか？

A: 対応しています。GUI設定ダイアログの「アカウント管理」セクションから複数のGoogleアカウントを追加し、カレンダーごとに表示色を設定できます。

### Q: 壁紙の解像度を変更したい

A: `src/config.py`の`IMAGE_WIDTH`と`IMAGE_HEIGHT`を変更してください。または`AUTO_DETECT_RESOLUTION = True`で自動検出を有効にしてください。

### Q: 背景画像を変更したい

A: GUI設定ダイアログの「背景画像」セクションから画像をアップロードできます。PNG、JPG、JPEG形式に対応しています。また`assets/background.jpg`を直接置き換えることも可能です。

### Q: 通知を無効にしたい

A: デーモンモードを使用せず、ワンショットモード（`--run-once`）のみを使用してください。

### Q: テーマをカスタマイズしたい

A: `src/themes.py`に新しいテーマを追加できます。詳細は開発ドキュメントを参照してください。

---

## サポート

問題が発生した場合:

1. このガイドの「トラブルシューティング」セクションを確認
2. `calendar_app.log`でログを確認
3. [Issues](../../issues)で報告

---

**最終更新**: 2026-02-11
