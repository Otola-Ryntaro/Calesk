# カレンダー壁紙アプリ - ユーザーガイド

**最終更新**: 2026-02-05
**対象バージョン**: 2.0（GUI版）

---

## 📋 目次

1. [はじめに](#はじめに)
2. [インストールと初期設定](#インストールと初期設定)
3. [基本的な使い方](#基本的な使い方)
4. [GUIモード詳細](#guiモード詳細)
5. [CLIモード詳細](#cliモード詳細)
6. [テーマのカスタマイズ](#テーマのカスタマイズ)
7. [設定のカスタマイズ](#設定のカスタマイズ)
8. [自動更新の設定](#自動更新の設定)
9. [トラブルシューティング](#トラブルシューティング)
10. [FAQ](#faq)

---

## はじめに

カレンダー壁紙アプリは、Google Calendarの予定をデスクトップ壁紙として表示するアプリケーションです。

### 対象読者

- デスクトップで予定を一目で確認したい方
- Google Calendarを使用している方
- Windows/Mac/Linuxユーザー

### 必要なもの

- Python 3.9以上（3.13推奨）
- Googleアカウント
- インターネット接続

---

## インストールと初期設定

### 1. Pythonのインストール確認

ターミナル/コマンドプロンプトで以下を実行：

```bash
python --version
# または
python3 --version
```

**Python 3.9以上**が表示されればOKです。

表示されない場合は、[Python公式サイト](https://www.python.org/)からダウンロードしてインストールしてください。

### 2. リポジトリのクローン

```bash
git clone <repository-url>
cd calender_desktop
```

### 3. 仮想環境の作成

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

仮想環境が有効化されると、プロンプトに `(venv)` が表示されます：

```
(venv) user@computer:~/calender_desktop$
```

### 4. 依存関係のインストール

```bash
pip install -r requirements.txt
```

インストールされるパッケージ：
- PyQt6 (GUI)
- Pillow (画像処理)
- google-api-python-client (Calendar API)
- plyer (通知)
- schedule (スケジューリング)

### 5. Google Calendar API設定

#### 5.1. Google Cloud Consoleでプロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 「プロジェクトを選択」→「新しいプロジェクト」をクリック
3. プロジェクト名を入力（例: `calendar-wallpaper`）
4. 「作成」をクリック

#### 5.2. Google Calendar APIの有効化

1. 左メニュー「APIとサービス」→「ライブラリ」を選択
2. 検索ボックスに「Google Calendar API」と入力
3. 「Google Calendar API」を選択
4. 「有効にする」をクリック

#### 5.3. OAuth 2.0認証情報の作成

1. 左メニュー「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「OAuth クライアントID」を選択
3. 同意画面の設定を求められた場合:
   - 「外部」を選択（個人利用の場合）
   - アプリ名、サポートメールを入力
   - 「保存して次へ」を3回クリック
4. アプリケーションの種類: **「デスクトップアプリ」**を選択
5. 名前を入力（例: `Calendar Wallpaper App`）
6. 「作成」をクリック

#### 5.4. 認証情報のダウンロード

1. 作成されたクライアントIDの右側の「↓」アイコンをクリック
2. JSONファイルがダウンロードされます
3. ダウンロードしたファイルを`credentials.json`にリネーム
4. プロジェクトの`credentials/`ディレクトリに配置

```bash
mkdir -p credentials
mv ~/Downloads/client_secret_*.json credentials/credentials.json
```

### 6. 初回認証

```bash
python main.py --auth
```

実行すると：
1. ブラウザが自動的に開きます
2. Googleアカウントでログイン
3. 「このアプリは確認されていません」と表示される場合:
   - 「詳細」をクリック
   - 「（アプリ名）に移動（安全ではないページ）」をクリック
4. 「Google Calendar APIへのアクセス許可」を確認
5. 「許可」をクリック

認証が完了すると、`credentials/token.json`が作成されます。

---

## 基本的な使い方

### GUIモード（推奨）

直感的な操作で壁紙を更新できます：

```bash
python gui.py
```

**画面構成**:
```
┌─────────────────────────────────────────────┐
│  カレンダー壁紙アプリ               [×]     │
├─────────────────────────────────────────────┤
│  テーマ: [Simple      ▼]  [壁紙を更新]    │
├─────────────────────────────────────────────┤
│                                              │
│            プレビューエリア                 │
│   （壁紙生成後に表示されます）             │
│                                              │
│                                              │
├─────────────────────────────────────────────┤
│  ████████████████████████ 75%               │  ← 進捗バー
├─────────────────────────────────────────────┤
│  壁紙を更新しています...                   │  ← ステータスバー
└─────────────────────────────────────────────┘
```

**操作方法**:
1. **テーマ選択**: ドロップダウンから好みのテーマを選択
2. **壁紙を更新**: ボタンをクリックして壁紙を生成・設定
3. **プレビュー**: 生成された壁紙をプレビュー表示

### CLIモード

#### 手動実行（テスト用）

壁紙を即座に更新：

```bash
python main.py --run-once
```

#### バックグラウンド実行

定期的に壁紙を更新：

```bash
python main.py --daemon
```

停止するには `Ctrl+C` を押してください。

---

## GUIモード詳細

### テーマ選択

5種類のテーマから選択できます：

1. **Simple**: シンプルな白背景
   - 見やすさ重視
   - ビジネス向け

2. **Modern**: グラデーション背景と角丸カード
   - おしゃれなデザイン
   - 視覚的に魅力的

3. **Pastel**: パステルカラーの優しいデザイン
   - 柔らかい色合い
   - 目に優しい

4. **Dark**: ダークモード対応
   - 暗い環境に最適
   - 目の疲れを軽減

5. **Vibrant**: 鮮やかな色彩
   - カラフル
   - 活気のあるデザイン

### 壁紙更新の流れ

1. **「壁紙を更新」ボタンをクリック**
   - ボタンが無効化されます（二重クリック防止）

2. **進捗バーが表示**
   - 0-50%: イベント取得・画像生成
   - 50-100%: 壁紙設定

3. **プレビュー表示**
   - 生成された壁紙がプレビューエリアに表示されます

4. **ステータスバーにメッセージ**
   - 成功: 「壁紙を更新しました」
   - エラー: エラーメッセージを表示

### エラー表示

エラーは3つのレベルで表示されます：

1. **INFO**: ステータスバーに表示
   - 例: 「イベントがありません」

2. **WARNING**: ステータスバーに表示（黄色）
   - 例: 「一部のイベントを取得できませんでした」

3. **CRITICAL**: ポップアップで表示
   - 例: 「認証エラーが発生しました」

---

## CLIモード詳細

### コマンドライン引数

```bash
python main.py [オプション]
```

| オプション | 説明 | 使用例 |
|-----------|------|--------|
| `--auth` | 認証のみ実行 | `python main.py --auth` |
| `--run-once` | 1回だけ実行 | `python main.py --run-once` |
| `--daemon` | バックグラウンド実行 | `python main.py --daemon` |
| `--log-level` | ログレベル指定 | `python main.py --log-level DEBUG` |

### ログレベル

| レベル | 説明 | 使用タイミング |
|--------|------|----------------|
| `DEBUG` | 詳細なデバッグ情報 | 問題調査時 |
| `INFO` | 一般的な情報 | 通常使用（デフォルト） |
| `WARNING` | 警告メッセージ | 軽微な問題 |
| `ERROR` | エラーメッセージのみ | エラー調査時 |

### デーモンモード

#### 起動

```bash
python main.py --daemon
```

#### 実行スケジュール

デフォルト設定：
- **壁紙更新**: 毎日6:00
- **通知チェック**: 5分ごと

#### 停止

`Ctrl+C` を押してください。

```
^C
スケジューラーを停止しています...
スケジューラーが停止しました。
```

---

## テーマのカスタマイズ

### テーマ定義ファイル

`src/themes.py`でテーマをカスタマイズできます。

### テーマ構造

```python
THEMES = {
    "custom": {
        # 背景設定
        "background_type": "gradient",  # solid / gradient / image
        "background_color": (255, 255, 255),  # RGB
        "gradient_start": (100, 150, 200),    # RGB
        "gradient_end": (200, 220, 255),      # RGB

        # カード設定
        "card_background": (255, 255, 255, 230),  # RGBA (alpha: 透明度)
        "card_text": (0, 0, 0),                   # RGB
        "card_radius": 15,                        # 角丸半径 (0で角丸なし)
        "card_shadow": True,                      # 影の有無

        # イベントカラー設定
        "event_colors": {
            "1": (255, 100, 100),  # カレンダーID 1の色
            "2": (100, 200, 255),  # カレンダーID 2の色
            # ...
        },
    }
}
```

### 新しいテーマの追加

1. `src/themes.py`を開く
2. `THEMES`辞書に新しいテーマを追加
3. GUI再起動で自動的に認識される

**例: Oceanテーマ**

```python
THEMES = {
    # ... existing themes ...
    "ocean": {
        "background_type": "gradient",
        "gradient_start": (30, 144, 255),  # 青
        "gradient_end": (0, 191, 255),     # 水色
        "card_background": (255, 255, 255, 200),
        "card_text": (0, 50, 100),
        "card_radius": 20,
        "card_shadow": True,
        "event_colors": {
            "1": (255, 165, 0),  # オレンジ
            "2": (255, 215, 0),  # ゴールド
        },
    }
}
```

---

## 設定のカスタマイズ

### config.py

`src/config.py`で以下の設定をカスタマイズできます。

### 画像設定

```python
# 壁紙サイズ
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# 背景色（Simple テーマ）
BACKGROUND_COLOR = (255, 255, 255)  # 白

# フォント設定
FONT_SIZE_TITLE = 60        # タイトルサイズ
FONT_SIZE_DATE = 40         # 日付サイズ
FONT_SIZE_EVENT = 30        # イベントサイズ
```

### スケジュール設定

```python
# 壁紙更新時刻（HH:MM形式）
UPDATE_TIME = '06:00'

# 通知タイミング（分）
NOTIFICATION_ADVANCE_MINUTES = 30  # 予定開始30分前
```

### カレンダー設定

```python
# カレンダーID
CALENDAR_IDS = [
    'primary',  # 主カレンダー
]

# 複数カレンダーの追加
CALENDAR_IDS = [
    'primary',
    'family@group.calendar.google.com',
    'work@group.calendar.google.com',
]
```

### 表示設定

```python
# 今日の予定の表示数
MAX_TODAY_EVENTS = 3

# 週の開始曜日（0=月曜、6=日曜）
WEEK_START_DAY = 6  # 日曜始まり

# 週の表示日数
WEEK_DAYS = 7
```

### フォントパス

システムに合わせてフォントパスを設定：

```python
FONT_PATHS = [
    # Mac
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/Helvetica.ttc",

    # Windows
    "C:/Windows/Fonts/msgothic.ttc",
    "C:/Windows/Fonts/arial.ttf",

    # Linux
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
```

---

## 自動更新の設定

### macOS: launchd

#### インストール

```bash
bash scripts/install_autostart_mac.sh
```

実行すると：
1. plistファイルを`~/Library/LaunchAgents/`にコピー
2. launchdサービスを起動
3. 次回ログイン時から自動起動

#### 確認

```bash
launchctl list | grep calendar-wallpaper
```

#### アンインストール

```bash
bash scripts/uninstall_autostart_mac.sh
```

#### ログ確認

```bash
tail -f launchd.log
tail -f launchd.error.log
```

### Windows: タスクスケジューラー

#### インストール

PowerShellを**管理者権限**で開いて実行：

```powershell
.\scripts\install_autostart_windows.ps1
```

実行すると：
1. タスクスケジューラーに登録
2. 毎日06:00に自動実行

#### 確認

PowerShellで：

```powershell
Get-ScheduledTask -TaskName "CalendarWallpaperUpdate"
```

またはGUIで：
1. `Win + R` → `taskschd.msc` を入力
2. タスクスケジューラライブラリで「CalendarWallpaperUpdate」を確認

#### アンインストール

```powershell
.\scripts\uninstall_autostart_windows.ps1
```

### 更新時刻の変更

#### macOS

1. `com.user.calendar-wallpaper.plist`を編集
2. サービスを再起動：
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.user.calendar-wallpaper.plist
   launchctl load ~/Library/LaunchAgents/com.user.calendar-wallpaper.plist
   ```

#### Windows

1. タスクスケジューラーを開く
2. 「CalendarWallpaperUpdate」をダブルクリック
3. 「トリガー」タブで時刻を変更

---

## トラブルシューティング

### 認証エラー

#### 症状

```
認証情報ファイルが見つかりません
```

#### 解決方法

1. `credentials/credentials.json`が存在するか確認：
   ```bash
   ls credentials/credentials.json
   ```

2. ファイルが存在しない場合、Google Cloud Consoleで再ダウンロード

3. ファイルが存在する場合、再認証を試す：
   ```bash
   rm credentials/token.json
   python main.py --auth
   ```

### 壁紙が設定されない

#### 症状

画像は生成されるが、壁紙が変更されない

#### 解決方法（Mac）

1. システム環境設定 → セキュリティとプライバシー
2. 「アクセシビリティ」または「フルディスクアクセス」を確認
3. ターミナル/Pythonに権限を付与

#### 解決方法（Windows）

1. 管理者権限で実行：
   ```bash
   # 管理者権限でコマンドプロンプトを開く
   python gui.py
   ```

2. Windows設定 → 個人用設定 → 背景
   - 「画像」が選択されているか確認

#### 解決方法（Linux）

1. デスクトップ環境を確認：
   ```bash
   echo $DESKTOP_SESSION
   ```

2. GNOME/KDE以外の場合、対応していない可能性があります

### GUIが起動しない

#### 症状

```
ModuleNotFoundError: No module named 'PyQt6'
```

#### 解決方法

1. PyQt6がインストールされているか確認：
   ```bash
   pip list | grep PyQt6
   ```

2. インストールされていない場合：
   ```bash
   pip install PyQt6
   ```

3. 仮想環境が有効化されているか確認：
   ```bash
   which python
   # → .../calender_desktop/venv/bin/python と表示されればOK
   ```

### フォントが表示されない

#### 症状

日本語が豆腐（□）で表示される

#### 解決方法

1. システムに日本語フォントをインストール：

   **Mac**: デフォルトでヒラギノがインストール済み

   **Windows**:
   ```
   設定 → 時刻と言語 → 言語
   「日本語」を追加
   ```

   **Linux (Ubuntu)**:
   ```bash
   sudo apt install fonts-noto-cjk
   ```

2. `src/config.py`のフォントパスを確認：
   ```python
   FONT_PATHS = [
       "/path/to/your/japanese/font.ttf",
   ]
   ```

### API制限エラー

#### 症状

```
API制限に達しました
```

#### 解決方法

1. しばらく時間を置いてから再実行（1時間程度）

2. Google Cloud Consoleで割り当てを確認：
   - APIとサービス → ダッシュボード
   - Google Calendar API → 割り当て

3. 通常の使用では1,000,000リクエスト/日の制限に達することはありません

### 画像が生成されない

#### 症状

エラーなく終了するが、`output/`に画像がない

#### 解決方法

1. ログファイルを確認：
   ```bash
   tail -50 calendar_app.log
   ```

2. DEBUGモードで実行：
   ```bash
   python main.py --run-once --log-level DEBUG
   ```

3. `output/`ディレクトリの権限を確認：
   ```bash
   ls -la output/
   chmod 755 output/
   ```

---

## FAQ

### Q1. 複数のGoogleアカウントを使用できますか？

**A**: 現在は1つのアカウントのみサポートしています。アカウントを切り替える場合は、`credentials/token.json`を削除して再認証してください。

```bash
rm credentials/token.json
python main.py --auth
```

### Q2. カレンダーIDはどこで確認できますか？

**A**: Google Calendarの設定から確認できます：

1. [Google Calendar](https://calendar.google.com/)にアクセス
2. 左側のカレンダー一覧で対象カレンダーの「⋮」をクリック
3. 「設定と共有」を選択
4. 「カレンダーの統合」セクションの「カレンダーID」をコピー

### Q3. 壁紙の解像度を変更できますか？

**A**: `src/config.py`で変更できます：

```python
IMAGE_WIDTH = 2560   # 4Kの場合: 3840
IMAGE_HEIGHT = 1440  # 4Kの場合: 2160
```

変更後、GUIまたはCLIを再起動してください。

### Q4. 特定のカレンダーのみ表示できますか？

**A**: `src/config.py`で`CALENDAR_IDS`を編集してください：

```python
CALENDAR_IDS = [
    'primary',  # 主カレンダーのみ
]

# または特定のカレンダー
CALENDAR_IDS = [
    'work@group.calendar.google.com',  # 仕事用カレンダーのみ
]
```

### Q5. 壁紙は自動的にデスクトップに設定されますか？

**A**: はい、`main.py`と`gui.py`の両方で自動的に設定されます。ただし、OS側の権限設定が必要な場合があります（トラブルシューティング参照）。

### Q6. 過去のイベントも表示されますか？

**A**: いいえ、今日以降の予定のみ表示されます：
- **今日の予定**: 本日の全予定
- **今週の予定**: 今日から7日間の予定

### Q7. プライベートイベント（予定あり）は表示されますか？

**A**: はい、表示されます。ただし、詳細が非公開の場合は「予定あり」と表示されます。

### Q8. 壁紙を手動で元に戻せますか？

**A**: はい、OS標準の壁紙設定から変更できます：

- **Mac**: システム環境設定 → デスクトップとスクリーンセーバ
- **Windows**: 設定 → 個人用設定 → 背景
- **Linux (GNOME)**: 設定 → 外観 → 背景

### Q9. オフラインで使用できますか？

**A**: 初回認証とイベント取得時にはインターネット接続が必要です。取得後は、キャッシュされたイベントで壁紙生成が可能です（ただし、最新のイベントは反映されません）。

### Q10. マルチディスプレイに対応していますか？

**A**: 現在は主ディスプレイのみ対応しています。マルチディスプレイ対応は将来のバージョンで計画中です。

---

## サポート

### バグ報告

GitHubのIssueで報告してください：
- エラーメッセージ
- `calendar_app.log`の内容
- 実行環境（OS、Pythonバージョン）

### 機能リクエスト

GitHubのIssueで機能リクエストを作成してください。

### コミュニティ

プルリクエストを歓迎します！

---

**作成者**: Claude Sonnet 4.5
**最終更新**: 2026-02-05
