# カレンダー壁紙アプリ

Google Calendarの予定をデスクトップ壁紙として表示するPythonアプリケーション

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6.1-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📋 概要

Google Calendarと連携し、今日と今週の予定を美しい壁紙として自動生成・設定するアプリケーションです。GUIとCLIの両方に対応し、定期的な壁紙更新やイベント通知機能を備えています。

## ✨ 主な機能

- 📅 **Google Calendar連携**: OAuth2認証で安全にカレンダーデータを取得
- 🎨 **5種類のテーマ**: simple, modern, pastel, dark, vibrantから選択可能
- 🖼️ **週間カレンダー表示**: 今日と1週間の予定を見やすく表示
- 🔔 **イベント通知**: 予定開始5分前に自動通知（デーモンモード）
- 🖥️ **マルチディスプレイ対応**: 複数モニター環境で柔軟に設定可能
- 🌐 **GUI/CLI両対応**: 使いやすいGUIインターフェースとコマンドライン操作
- ⏰ **自動更新**: スケジューラーで毎日自動的に壁紙を更新

## 🚀 クイックスタート

### 必要要件

- Python 3.13以上
- macOS / Linux / Windows
- Google Calendar アカウント

### インストール

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

### Google Calendar API設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Google Calendar APIを有効化
3. OAuth 2.0クライアントIDを作成（デスクトップアプリケーション）
4. `credentials.json`をダウンロードしてプロジェクトルートに配置

### 初回認証

```bash
# 認証フローを実行
python main.py --auth
```

ブラウザが開き、Googleアカウントでの認証を求められます。

## 📖 使い方

### GUI版（推奨）

```bash
# GUI起動
python run_gui.py
```

GUI画面で以下の操作が可能：
- テーマ選択（ドロップダウンメニュー）
- 壁紙プレビュー表示
- ワンクリックで壁紙更新

### CLI版

```bash
# 壁紙を即座に更新
python main.py --run-once

# デーモンモード（毎日6:00に自動更新 + 通知機能）
python main.py --daemon
```

## 🎨 テーマ

5種類のデザインテーマから選択可能：

| テーマ | 説明 |
|--------|------|
| **simple** | シンプル系（背景画像、黒文字、角丸なし） |
| **modern** | モダン系（半透明白カード、角丸、影付き） |
| **pastel** | パステル系（淡い色、優しい印象） |
| **dark** | ダーク系（半透明黒カード、ゴールドアクセント） |
| **vibrant** | 鮮やか系（鮮やかな色、元気な印象） |

テーマは`src/config.py`で変更するか、GUIで切り替え可能です。

## ⚙️ 設定

主な設定は`src/config.py`で変更できます：

```python
# 画像設定
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# テーマ
THEME = 'simple'

# マルチディスプレイ
WALLPAPER_TARGET_DESKTOP = 1  # 0=全て, 1=desktop1, 2=desktop2

# 通知設定
NOTIFICATION_ADVANCE_MINUTES = 5  # 予定開始何分前に通知
```

詳細は[USER_GUIDE.md](USER_GUIDE.md)を参照してください。

## 🧪 テスト

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジ付き
pytest tests/ --cov=src --cov-report=html
```

テスト結果: ✅ **235テスト全合格**

## 📚 ドキュメント

- [ユーザーガイド](USER_GUIDE.md) - 詳細な使い方とトラブルシューティング
- [開発ドキュメント](docs/) - 実装チケットと設計資料

## 🔧 トラブルシューティング

### 認証エラー

```bash
# 認証情報をリセット
rm token.json
python main.py --auth
```

### フォントエラー

日本語フォントが見つからない場合、`src/config.py`の`FONT_PATHS`を環境に合わせて修正してください。

### 詳細なトラブルシューティング

[USER_GUIDE.md](USER_GUIDE.md)の「トラブルシューティング」セクションを参照してください。

## 📄 ライセンス

MIT License

## 🤝 貢献

プルリクエストは歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📧 サポート

問題が発生した場合は、[Issues](../../issues)で報告してください。
