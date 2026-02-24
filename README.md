# Calesk（カレスク）

Google Calendarの予定をデスクトップ壁紙として表示するPythonアプリケーション

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.7.x-green.svg)
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
- **macOS / Windows 対応**: Python 環境で動作（macOS・Windows・Linux）
- **マルチディスプレイ対応**: 解像度自動検出、複数モニター環境で柔軟に設定可能
- **GUI/CLI 両対応**: 設定ダイアログ付きGUIとコマンドライン操作
- **自動更新**: 常駐アプリとして定期的に壁紙を自動更新（**アプリが起動していない場合、日付が変わっても壁紙は更新されません**）
- **省メモリ設計**: フォント遅延ロード・画像キャッシュ・リソース自動解放

## クイックスタート

**必要要件**: Python 3.11 以上 / Googleアカウント

```bash
# 1. リポジトリをクローン
git clone https://github.com/Otola-Ryntaro/Calesk.git
cd Calesk

# 2. 仮想環境を作成・有効化
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. パッケージをインストール
pip install -r requirements.txt

# 4. アプリを起動
python run_gui.py
```

初回起動前に [Google Calendar API 設定](USER_GUIDE.md#google-calendar-api設定全員必須) が必要です（約10〜15分）。

詳細なセットアップ手順は [USER_GUIDE.md](USER_GUIDE.md) を参照してください。

## 使い方

### GUI版（推奨）

```bash
python run_gui.py
```

GUI画面で以下の操作が可能:

- テーマ選択とリアルタイムプレビュー
- 背景画像のアップロード
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
| ------ | ---- |
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
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
THEME = 'simple'
WALLPAPER_TARGET_DESKTOP = 1  # 0=全て, 1=desktop1, 2=desktop2
AUTO_DETECT_RESOLUTION = True
```

詳細は[USER_GUIDE.md](USER_GUIDE.md)を参照してください。

## テスト

```bash
source venv/bin/activate && python -m pytest tests/ -v --tb=short
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
Calesk/
├── src/                          # ソースコード
│   ├── models/                   # データモデル
│   ├── renderers/                # 描画Mixin
│   ├── ui/                       # GUI関連
│   ├── viewmodels/               # ViewModel層
│   ├── calendar_client.py        # Google Calendar API
│   ├── image_generator.py        # 壁紙画像生成
│   ├── themes.py                 # テーマ定義（7種）
│   └── config.py                 # 設定ファイル
├── tests/                        # テストコード（669件）
├── assets/                       # リソース（背景画像等）
├── credentials/                  # 認証情報（.gitignore対象）
├── main.py                       # CLIエントリーポイント
├── run_gui.py                    # GUIエントリーポイント
├── requirements.txt              # 依存パッケージ
├── README.md                     # このファイル
└── USER_GUIDE.md                 # ユーザーガイド
```

## セキュリティとプライバシー

本アプリが外部と通信するのは **Google Calendar API のみ** です。それ以外のサーバーへのデータ送信は一切行いません。

- **スコープ**: `calendar.readonly`（カレンダーの読み取り専用）
- **認証情報の保管**: `credentials/` ディレクトリにローカル保存（`.gitignore` 対象）
- **トークンファイル**: `token.json` はパーミッション `600`（所有者のみ読み書き可能）で保存

## 作者

**音良林太郎** - [@Otola_ryntaro](https://x.com/Otola_ryntaro)

## ライセンス

MIT License © 2026 音良林太郎

## 貢献

プルリクエストは歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## サポート

問題が発生した場合は、[Issues](https://github.com/Otola-Ryntaro/Calesk/issues) で報告してください。

---

## English

### What is Calesk?

**Calesk** automatically generates your desktop wallpaper from Google Calendar events — showing today's schedule and the week ahead, updated in the background.

### Requirements

- Python 3.11 or later
- macOS / Windows / Linux
- Google account

### Quick Start

```bash
git clone https://github.com/Otola-Ryntaro/Calesk.git
cd Calesk
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run_gui.py
```

See [USER_GUIDE.md](USER_GUIDE.md) for step-by-step setup instructions including Google Calendar API configuration.

### Features

- Syncs with Google Calendar via OAuth2 (read-only, multiple accounts supported)
- 7 visual themes: simple, modern, pastel, dark, vibrant, luxury, playful
- Weekly calendar grid with current-time indicator
- Custom background images or gradient backgrounds
- Auto-refresh as a resident app

### Google Calendar Setup (required)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project
2. Enable the **Google Calendar API**
3. Configure the OAuth consent screen; add your Gmail address as a test user
4. Create an **OAuth 2.0 Client ID** (Desktop application type)
5. Download `credentials.json` and place it in the `credentials/` directory
6. Launch the app — a browser window will open for authentication

See [USER_GUIDE.md](USER_GUIDE.md) for detailed instructions.

### Privacy

Calesk only communicates with **Google Calendar API**. No data is sent to any other server.
The OAuth scope is `calendar.readonly` — the app cannot create, edit, or delete events.

### License

MIT License © 2026 [音良林太郎](https://x.com/Otola_ryntaro)
