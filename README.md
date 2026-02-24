# Calesk（カレスク）

Google Calendarの予定をデスクトップ壁紙として表示するPythonアプリケーション

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

> 🇬🇧 **English summary below** · [Jump to English section](#english)

---

## 概要

Google Calendarと連携し、今日と今週の予定を壁紙として自動生成・設定するデスクトップアプリケーションです。7種類のテーマ、複数Googleアカウント対応、自動更新、カスタム背景画像など多彩な機能を備えています。

## 主な機能

- **Google Calendar連携**: OAuth2認証でカレンダーデータを取得（複数アカウント対応）
- **7種類のテーマ**: simple, modern, pastel, dark, vibrant, luxury, playful
- **週間カレンダー表示**: 今日と1週間の予定を見やすく表示
- **カスタム背景**: 背景画像のアップロードまたはグラデーション背景に対応
- **macOS / Windows対応**: ビルド済みバイナリで即利用可能（GitHub Actions自動ビルド）
- **マルチディスプレイ対応**: 解像度自動検出、複数モニター環境で柔軟に設定可能
- **GUI/CLI両対応**: 設定ダイアログ付きGUIとコマンドライン操作
- **自動更新**: 常駐アプリとして定期的に壁紙を自動更新（**アプリが起動していない場合、日付が変わっても壁紙は更新されません**）
- **省メモリ設計**: フォント遅延ロード・画像キャッシュ・リソース自動解放

## クイックスタート

### かんたんインストール（Python不要）

[Releases](https://github.com/Otola-Ryntaro/Calesk/releases) ページからダウンロードしてすぐに使えます。

| OS | ダウンロードファイル | 起動方法 |
| --- | --- | --- |
| macOS (Apple Silicon) | `Calesk-macOS-AppleSilicon.dmg` | DMGをマウント → Calesk.app を Applications にドラッグ |
| macOS (Intel) | `Calesk-macOS-Intel.dmg` | DMGをマウント → Calesk.app を Applications にドラッグ |
| macOS (互換用) | `Calesk-macOS.dmg` | 既存リンク互換（Intel版） |
| Windows | `Calesk-Windows.zip` | 展開 → `Calesk.exe` をダブルクリック |

> 詳細は [USER_GUIDE.md](USER_GUIDE.md) を参照してください。

#### macOS：初回起動時の警告について

コード署名なしのため、初回起動時に「開発元を確認できない」と表示される場合があります。

```text
右クリック（または Control+クリック）→「開く」→「開く」ボタンをクリック
```

または、ターミナルで以下を実行:

```bash
xattr -cr /Applications/Calesk.app
```

#### Windows：SmartScreen 警告について

初回実行時に「Windows によって PC が保護されました」と表示される場合があります。

```text
「詳細情報」→「実行」をクリック
```

### 開発者向けインストール（Python環境）

**必要要件**: Python 3.13以上 / macOS・Linux・Windows / Googleアカウント

```bash
# リポジトリのクローン
git clone <repository-url>
cd calender_desktop

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### Google Calendar API設定（全員必須）

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Google Calendar APIを有効化
3. OAuth同意画面を設定し、テストユーザーに自分のGmailアドレスを追加
4. OAuthクライアントID（デスクトップアプリ）を作成
5. `credentials.json`をダウンロードして`credentials/`ディレクトリに配置

> 初めての方向けに、画面ごとの詳細な手順を [USER_GUIDE.md](USER_GUIDE.md#google-calendar-api設定全員必須) に記載しています。

### 初回認証

```bash
python main.py --auth
```

ブラウザが開き、Googleアカウントでの認証を求められます。

## 使い方

### GUI版（推奨）

```bash
python run_gui.py
```

GUI画面で以下の操作が可能:

- テーマ選択とリアルタイムプレビュー
- 背景画像のアップロード
- 自動更新の間隔設定
- 複数Googleアカウントの管理

### CLI版

```bash
# 壁紙を即座に更新
python main.py --run-once

# デーモンモード（定期的に自動更新 + 通知機能）
python main.py --daemon
```

## テーマ

7種類のデザインテーマから選択可能:

| テーマ | 説明 |
|--------|------|
| **simple** | シンプル系（白背景、黒文字、角丸なし） |
| **modern** | モダン系（半透明白カード、角丸、影付き） |
| **pastel** | パステル系（淡い色、優しい印象） |
| **dark** | ダーク系（半透明黒カード、ゴールドアクセント） |
| **vibrant** | 鮮やか系（鮮やかな色、元気な印象） |
| **luxury** | ラグジュアリー系（アイボリー、ゴールドアクセント） |
| **playful** | プレイフル系（コーラルピンク、ターコイズ） |

テーマはGUIの設定ダイアログまたは`src/config.py`で変更できます。

## 設定

主な設定は`src/config.py`で変更できます:

```python
# 画像設定
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# テーマ
THEME = 'simple'

# マルチディスプレイ
WALLPAPER_TARGET_DESKTOP = 1  # 0=全て, 1=desktop1, 2=desktop2

# 解像度の自動検出
AUTO_DETECT_RESOLUTION = True
```

詳細は[USER_GUIDE.md](USER_GUIDE.md)を参照してください。

## テスト

```bash
# 全テスト実行
source venv/bin/activate && python -m pytest tests/ -v --tb=short

# カバレッジ付き
python -m pytest tests/ --cov=src --cov-report=html
```

テスト数: 669件

## アーキテクチャ

```text
MVVM + Service層

UI (PyQt6)  ->  ViewModel  ->  WallpaperService  ->  ImageGenerator / CalendarClient
                                                       |-- EffectsRendererMixin
                                                       |-- CardRendererMixin
                                                       +-- CalendarRendererMixin
```

## ディレクトリ構造

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
│   ├── calendar_client.py        # Google Calendar API
│   ├── image_generator.py        # 壁紙画像生成
│   ├── display_info.py           # ディスプレイ情報取得
│   ├── wallpaper_cache.py        # 壁紙キャッシュ管理
│   ├── wallpaper_setter.py       # 壁紙設定
│   ├── themes.py                 # テーマ定義（7種）
│   └── config.py                 # 設定ファイル
├── tests/                        # テストコード（614件）
├── docs/                         # 開発ドキュメント（チケット管理）
├── assets/                       # リソース（背景画像等）
├── credentials/                  # 認証情報（.gitignore対象）
├── main.py                       # CLIエントリーポイント
├── run_gui.py                    # GUIエントリーポイント
├── requirements.txt              # 依存パッケージ
├── README.md                     # このファイル
└── USER_GUIDE.md                 # ユーザーガイド
```

## ドキュメント

- [ユーザーガイド](USER_GUIDE.md) - 詳細な使い方とトラブルシューティング
- [開発ドキュメント](docs/) - 実装チケットと設計資料

## トラブルシューティング

### 認証エラー

```bash
# 認証情報をリセット
rm credentials/token.json
python main.py --auth
```

### フォントエラー

日本語フォントが見つからない場合、`src/config.py`の`FONT_PATHS`を環境に合わせて修正してください。

詳細なトラブルシューティングは[USER_GUIDE.md](USER_GUIDE.md)を参照してください。

## セキュリティとプライバシー

本アプリが外部と通信するのは **Google Calendar API のみ** です。それ以外のサーバーへのデータ送信は一切行いません。

- **スコープ**: `calendar.readonly`（カレンダーの読み取り専用）。予定の作成・変更・削除はできません。
- **認証情報の保管**: `credentials/` ディレクトリにOAuthクライアント情報とトークンをローカル保存します。このディレクトリは `.gitignore` 対象であり、リポジトリには含まれません。
- **トークンファイル**: `token.json` はファイルパーミッション `600`（所有者のみ読み書き可能）で保存されます。
- **データの保存先**: 取得した予定データはメモリ上でのみ使用し、ローカルファイルへの永続化は行いません。生成された壁紙画像のみ `output/` に保存されます。

## 作者

**音良林太郎** - [@Otola_ryntaro](https://x.com/Otola_ryntaro)

## ライセンス

MIT License © 2026 音良林太郎

## 貢献

プルリクエストは歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## サポート

問題が発生した場合は、[Issues](../../issues)で報告してください。

---

## English

### What is Calesk?

**Calesk** automatically generates your desktop wallpaper from Google Calendar events — showing today's schedule and the week ahead, updated in the background.

### Features

- Syncs with Google Calendar via OAuth2 (read-only, multiple accounts supported)
- 7 visual themes: simple, modern, pastel, dark, vibrant, luxury, playful
- Weekly calendar grid with current-time indicator
- Custom background images or gradient backgrounds
- Auto-refresh as a menu bar / system tray resident app
- macOS & Windows support

### Installation (no Python required)

Download the latest release from the [Releases](https://github.com/Otola-Ryntaro/Calesk/releases) page.

| OS | File | How to open |
| --- | --- | --- |
| macOS (Apple Silicon) | `Calesk-macOS-AppleSilicon.dmg` | Mount DMG → drag Calesk.app to Applications |
| macOS (Intel) | `Calesk-macOS-Intel.dmg` | Mount DMG → drag Calesk.app to Applications |
| macOS (legacy) | `Calesk-macOS.dmg` | Backward-compatible alias (Intel build) |
| Windows | `Calesk-Windows.zip` | Extract → double-click `Calesk.exe` |

#### macOS: Security warning (Gatekeeper)

Because this app is not code-signed, macOS may show *"cannot be opened because the developer cannot be verified"*.

**Fix:** Right-click (or Control+click) the app → **Open** → click **Open**.

Or run this in Terminal:

```bash
xattr -cr /Applications/Calesk.app
```

#### Windows: SmartScreen warning

Windows may show *"Windows protected your PC"* on first launch.

**Fix:** Click **More info** → **Run anyway**.

### Google Calendar Setup (required for all users)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project
2. Enable the **Google Calendar API**
3. Configure the OAuth consent screen; add your Gmail address as a test user
4. Create an **OAuth 2.0 Client ID** (Desktop application type)
5. Download `credentials.json` and place it in the `credentials/` directory
6. On first run, authenticate via the browser

> See [USER_GUIDE.md](USER_GUIDE.md) for step-by-step screenshots.

### Privacy

Calesk only communicates with **Google Calendar API**. No data is sent to any other server.
The OAuth scope is `calendar.readonly` — the app cannot create, edit, or delete events.

### License

MIT License © 2026 [音良林太郎](https://x.com/Otola_ryntaro)
