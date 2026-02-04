# カレンダー壁紙アプリ

Google Calendarの予定をデスクトップ壁紙として表示するクロスプラットフォームアプリケーション

## 📋 概要

このアプリケーションは、Google Calendarから予定を取得して、デスクトップの壁紙画像として自動生成・設定します。今日の予定と今週の予定を一目で確認できる、シンプルでミニマルなデザインです。

### 主な機能

- ✅ Google Calendarとの連携（複数カレンダー対応）
- ✅ 今日の予定 + 今週の予定を壁紙として表示
- ✅ 予定の色分け表示
- ✅ 予定開始30分前のデスクトップ通知
- ✅ 1日1回自動更新（デフォルト: 朝6時）
- ✅ Windows/Mac/Linux対応

## 🚀 セットアップ

### 必要要件

- Python 3.9 以上
- Google アカウント
- インターネット接続

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd calender_desktop
```

### 2. 仮想環境の作成と有効化

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. Google Calendar API設定

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. 「APIとサービス」→「ライブラリ」から「Google Calendar API」を有効化
4. 「APIとサービス」→「認証情報」から OAuth 2.0 クライアントIDを作成
   - アプリケーションの種類: デスクトップアプリ
5. `credentials.json` をダウンロード
6. ダウンロードしたファイルを `credentials/credentials.json` に配置

### 5. 初回認証

```bash
python main.py --auth
```

ブラウザが開き、Googleアカウントでの認証を求められます。許可すると認証情報が保存されます。

## 💻 使い方

### 手動実行（テスト用）

壁紙を即座に更新します：

```bash
python main.py --run-once
```

### バックグラウンド実行

定期的に壁紙を更新し、通知を送信します：

```bash
python main.py --daemon
```

デフォルトでは以下のスケジュールで実行されます：
- 壁紙更新: 毎日6:00
- 通知チェック: 5分ごと

停止するには `Ctrl+C` を押してください。

### コマンドライン引数

```bash
python main.py [オプション]
```

| オプション | 説明 |
|-----------|------|
| `--auth` | Google Calendar API認証のみを実行 |
| `--run-once` | スケジュール実行せずに1回だけ実行 |
| `--daemon` | デーモンモードで実行（バックグラウンド定期実行） |
| `--log-level` | ログレベルを指定（DEBUG, INFO, WARNING, ERROR） |

## ⚙️ 設定のカスタマイズ

[src/config.py](src/config.py) を編集して、以下の設定をカスタマイズできます：

### 画像設定

```python
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
BACKGROUND_COLOR = (255, 255, 255)  # 白背景
```

### スケジュール設定

```python
UPDATE_TIME = '06:00'  # 壁紙更新時刻
NOTIFICATION_ADVANCE_MINUTES = 30  # 通知タイミング（予定開始何分前）
```

### カレンダー設定

```python
CALENDAR_IDS = [
    'primary',  # 主カレンダー
    'your-calendar-id@group.calendar.google.com',  # 追加のカレンダー
]
```

## 📁 プロジェクト構成

```
calender_desktop/
├── src/
│   ├── calendar_client.py      # Google Calendar API連携
│   ├── image_generator.py      # 壁紙画像生成
│   ├── wallpaper_setter.py     # OS別壁紙設定
│   ├── notifier.py             # 通知機能
│   ├── scheduler.py            # 定期実行管理
│   └── config.py               # 設定ファイル
├── credentials/
│   └── credentials.json        # Google API認証情報
├── output/                     # 生成された壁紙画像
├── main.py                     # エントリーポイント
├── requirements.txt            # 依存関係
└── README.md
```

## 🔧 トラブルシューティング

### 認証エラー

**症状**: `認証情報ファイルが見つかりません` エラー

**解決方法**:
1. `credentials/credentials.json` が存在することを確認
2. Google Cloud Consoleで正しくOAuth 2.0クライアントIDを作成したか確認

### 壁紙が設定されない

**症状**: 画像は生成されるが壁紙が変更されない

**解決方法**:
- **Mac**: システム環境設定 → セキュリティとプライバシー でアプリに権限を付与
- **Windows**: 管理者権限で実行してみる
- **Linux**: GNOME/KDE以外のデスクトップ環境では動作しない可能性があります

### フォントが表示されない

**症状**: 日本語テキストが豆腐（□）で表示される

**解決方法**:
1. システムに日本語フォントがインストールされているか確認
2. `src/config.py` の `FONT_PATHS` を編集して、正しいフォントパスを指定

### API制限エラー

**症状**: `API制限に達しました` エラー

**解決方法**:
- Google Calendar APIには1日あたり1,000,000リクエストの制限があります
- 通常の使用では問題ありませんが、短時間に大量のリクエストを送信した場合に発生します
- しばらく時間を置いてから再実行してください

## 🖥️ システム要件

### 対応OS

- Windows 10/11
- macOS 10.14 (Mojave) 以降
- Linux (GNOME/KDE デスクトップ環境)

### 推奨スペック

- CPU: デュアルコア以上
- RAM: 2GB以上
- ディスク空き容量: 500MB以上

## 📝 ログファイル

アプリケーションのログは `calendar_app.log` に保存されます。

問題が発生した場合は、このログファイルを確認してください。

## 🤝 貢献

プルリクエストを歓迎します！

バグ報告や機能リクエストは、Issueを作成してください。

## 📄 ライセンス

MIT License

## 🙏 謝辞

このプロジェクトは以下のライブラリを使用しています：

- [google-api-python-client](https://github.com/googleapis/google-api-python-client)
- [Pillow](https://python-pillow.org/)
- [plyer](https://github.com/kivy/plyer)
- [schedule](https://github.com/dbader/schedule)
