# Calesk（カレスク） - ユーザーガイド

詳細な使い方、設定、トラブルシューティングガイド

## 目次

1. [かんたんインストール（Python不要）](#かんたんインストールpython不要)
2. [開発者向けインストール（Python環境）](#開発者向けインストールpython環境)
3. [Google Calendar API設定（全員必須）](#google-calendar-api設定全員必須)
4. [基本的な使い方](#基本的な使い方)
5. [複数Googleアカウントの設定](#複数googleアカウントの設定)
6. [テーマのカスタマイズ](#テーマのカスタマイズ)
7. [詳細設定](#詳細設定)
8. [自動起動の設定](#自動起動の設定)
9. [トラブルシューティング](#トラブルシューティング)
10. [開発者向け情報](#開発者向け情報)

---

## かんたんインストール（Python不要）

プログラミングの知識がなくても使えるインストール方法です。
Pythonのインストールは不要です。

### macOS

1. [Releases](https://github.com/Otola-Ryntaro/Calesk/releases) ページから自分のMacに合うDMGをダウンロード
   - Apple Silicon（M1/M2/M3）: `Calesk-macOS-AppleSilicon.dmg`
   - Intel Mac: `Calesk-macOS-Intel.dmg`
   - `Calesk-macOS.dmg` は互換用（Intel版）
2. DMGファイルをダブルクリックしてマウント
3. `Calesk.app` を「アプリケーション」フォルダにドラッグ&ドロップ

**初回起動時の注意（macOS Gatekeeper）**:

macOSのセキュリティ機能により、初回起動時にブロックされることがあります。

1. `Calesk.app` を右クリック（またはControlキーを押しながらクリック）
2. メニューから「開く」を選択
3. 「開く」ボタンをクリック（「開発元を検証できません」と表示されますが問題ありません）

> 2回目以降はダブルクリックで普通に起動できます。

### 自分でビルドする場合

ソースコードからmacOSアプリをビルドすることもできます。
Python環境が必要です（[開発者向けインストール](#開発者向けインストールpython環境)を先に完了してください）。

```bash
# ビルドスクリプトを実行
bash scripts/build_app.sh
```

ビルドが完了すると `dist/Calesk.app` が生成されます。

### Windows

1. [Releases](https://github.com/Otola-Ryntaro/Calesk/releases) ページから最新の `Calesk-Windows.zip` をダウンロード
2. ZIPファイルを右クリック →「すべて展開」
3. 展開されたフォルダ内の `Calesk.exe` をダブルクリックで起動

**初回起動時の注意（Windows SmartScreen）**:

Windows Defenderの SmartScreen により、初回起動時に警告が表示されることがあります。

1. 「WindowsによってPCが保護されました」と表示される
2. 「**詳細情報**」をクリック
3. 「**実行**」をクリック

> 2回目以降は警告なしで起動できます。

**推奨**: `Calesk` フォルダごと好きな場所（例: `C:\Users\ユーザー名\Apps\`）に移動して使用してください。

### Linux

現在、ビルド済みバイナリはmacOSとWindowsのみ提供しています。
Linuxでは [開発者向けインストール](#開発者向けインストールpython環境) の手順でPython環境からご利用ください。

---

## 開発者向けインストール（Python環境）

### システム要件

- **OS**: macOS 10.15以上 / Linux / Windows 10以上
- **Python**: 3.13以上
- **メモリ**: 512MB以上
- **ディスク**: 100MB以上の空き容量
- **インターネット**: Google Calendar API接続に必要

### インストール手順

```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd calender_desktop

# 2. 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存パッケージのインストール
pip install -r requirements.txt
```

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

---

## Google Calendar API設定（全員必須）

このアプリはGoogleカレンダーから予定を取得するため、Google Cloud上でAPI設定が必要です。
初回のみ10〜15分ほどかかりますが、一度設定すれば以降は自動で動作します。

> **必要なもの**: Googleアカウント（Gmailアドレス）、Webブラウザ

### ステップ1: Google Cloud Consoleにアクセス

1. ブラウザで [Google Cloud Console](https://console.cloud.google.com/) を開く
2. Googleアカウントでログインする（普段使っているGmailアカウントでOK）

> 初めてGoogle Cloud Consoleを使う場合、利用規約への同意画面が表示されます。
> 「同意して続行」をクリックしてください。
> **料金は一切かかりません**。Google Calendar APIは無料で利用できます。

### ステップ2: プロジェクトを作成

Google Cloud上に「プロジェクト」という入れ物を作ります。

1. 画面上部の「プロジェクトを選択」をクリック
   - 初めての場合は「My First Project」と表示されているかもしれません
2. 開いたダイアログの右上にある「新しいプロジェクト」をクリック
3. 以下を入力:
   - **プロジェクト名**: `calesk`（好きな名前でOK）
   - **場所**: 「組織なし」のままでOK
4. 「作成」をクリック
5. 数秒待つと作成完了の通知が表示される
6. 通知の「プロジェクトを選択」をクリック（または画面上部のプロジェクト名をクリックして切り替え）

### ステップ3: Google Calendar APIを有効にする

1. 左側メニューの「APIとサービス」をクリック
   - メニューが見えない場合は、左上の「三（ハンバーガーメニュー）」をクリック
2. 「ライブラリ」をクリック
3. 検索欄に `Google Calendar API` と入力
4. 検索結果から「**Google Calendar API**」をクリック（「Google Calendar」ではなく「Google Calendar **API**」を選択）
5. 青い「**有効にする**」ボタンをクリック
6. 有効化が完了すると、APIの詳細ページに移動する

### ステップ4: OAuth同意画面を設定する

アプリがGoogleアカウントにアクセスする際の許可画面を設定します。
**これを設定しないと、次のステップでOAuthクライアントIDを作成できません。**

1. 左側メニューの「APIとサービス」→「OAuth同意画面」をクリック
2. 「**アプリ情報を編集する**」または「**はじめに**」をクリック

   **ユーザーの種類を選択する画面が表示された場合**:

   - 「**外部**」を選択して「作成」をクリック
   - （「内部」はGoogle Workspace組織専用なので、個人利用では「外部」を選択）

3. 以下を入力:
   - **アプリ名**: `Calesk`（好きな名前でOK）
   - **ユーザーサポートメール**: 自分のGmailアドレスを選択
   - **デベロッパーの連絡先情報**: 自分のGmailアドレスを入力
   - それ以外の項目（アプリのロゴ、アプリのホームページなど）は**空欄のまま**でOK
4. 「**保存して次へ**」をクリック

5. 「スコープ」画面:
   - 「**スコープを追加または削除**」をクリック
   - フィルタに `calendar` と入力
   - 「**Google Calendar API**」の `.../auth/calendar.readonly`（カレンダーの読み取り）にチェック
   - 「**更新**」をクリック
   - 「**保存して次へ**」をクリック

   > スコープを追加しなくても動作しますが、設定しておくと認証画面でどの権限を要求しているか明示されます。

6. 「テストユーザー」画面:
   - 「**+ ADD USERS**」をクリック
   - **自分のGmailアドレス**を入力して「**追加**」をクリック
   - 「**保存して次へ**」をクリック

   > **重要**: テストユーザーに自分のメールアドレスを追加しないと、認証時に「アクセスがブロックされました」というエラーが表示されます。
   > 家族や友人に配布する場合は、その人のGmailアドレスもここに追加してください。

7. 「概要」画面で内容を確認し、「**ダッシュボードに戻る**」をクリック

### ステップ5: OAuthクライアントIDを作成する

1. 左側メニューの「APIとサービス」→「認証情報」をクリック
2. 画面上部の「**+ 認証情報を作成**」をクリック
3. 「**OAuthクライアントID**」を選択
4. 以下を入力:
   - **アプリケーションの種類**: 「**デスクトップアプリ**」を選択
   - **名前**: `Calesk Client`（好きな名前でOK）
5. 「**作成**」をクリック

6. 「OAuthクライアントを作成しました」というダイアログが表示される
   - **「JSONをダウンロード」をクリック**
   - JSONファイルがダウンロードされる（`client_secret_XXXXX.json` のような名前）

> ダウンロードし忘れた場合は、「認証情報」ページで作成したクライアントIDの右にあるダウンロードアイコン（下矢印マーク）をクリックすると再ダウンロードできます。

### ステップ6: credentials.jsonを配置する

ダウンロードしたJSONファイルをアプリが読み取れる場所に配置します。

#### アプリ版（macOS .app）の場合

```bash
# 1. ホームディレクトリに設定フォルダを作成
mkdir -p ~/.calesk/credentials

# 2. ダウンロードしたファイルをコピー&リネーム
cp ~/Downloads/client_secret_XXXXX.json ~/.calesk/credentials/credentials.json
```

> `client_secret_XXXXX.json` の部分は実際にダウンロードされたファイル名に置き換えてください。

#### アプリ版（Windows .exe）の場合

1. エクスプローラーで `C:\Users\ユーザー名\.calesk\credentials\` フォルダを作成
   - `Win + R` → `%USERPROFILE%` と入力して Enter
   - `.calesk` フォルダを新規作成 → その中に `credentials` フォルダを新規作成
2. ダウンロードした `client_secret_XXXXX.json` を上記フォルダにコピー
3. ファイル名を `credentials.json` に変更

> フォルダが見えない場合は、エクスプローラーの「表示」→「隠しファイル」にチェックを入れてください。

#### Python版の場合

```bash
# 1. プロジェクト内にcredentialsフォルダを作成（既にある場合は不要）
mkdir -p credentials

# 2. ダウンロードしたファイルをコピー&リネーム
cp ~/Downloads/client_secret_XXXXX.json credentials/credentials.json
```

**確認**: 以下のようなフォルダ構成になっていればOKです。

```text
calender_desktop/
├── credentials/
│   └── credentials.json    <-- このファイルがあればOK
├── src/
├── main.py
...
```

### ステップ7: 初回認証を実行する

アプリを起動すると、ブラウザが自動的に開きます。

#### Python版で認証する場合

```bash
python main.py --auth
```

#### アプリ版で認証する場合

Calesk.appをダブルクリックして起動してください。

#### ブラウザでの認証手順

1. ブラウザが開き、Googleアカウントの選択画面が表示される
2. カレンダーを使いたいGoogleアカウントを選択

3. **「このアプリはGoogleで確認されていません」** という警告画面が表示される

   > これは自分で作成したアプリなので正常な表示です。心配ありません。

   - 「**詳細**」をクリック（画面下部の小さいリンク）
   - 「**Calesk（安全ではないページ）に移動**」をクリック

4. 「CaleskがGoogleアカウントへのアクセスをリクエストしています」という画面が表示される
   - 「**許可**」をクリック

5. 「認証が完了しました」というメッセージが表示される（またはブラウザタブを閉じてOK）

6. `credentials/token.json` が自動生成される

> 認証は初回のみ必要です。2回目以降はtoken.jsonを使って自動的にログインします。
> トークンの有効期限が切れた場合も自動更新されるため、通常は再認証不要です。

### よくあるエラーと対処法

| エラーメッセージ | 原因 | 対処法 |
| --- | --- | --- |
| `credentials.json not found` | JSONファイルが正しい場所にない | ステップ6を確認。ファイル名が`credentials.json`であることも確認 |
| `アクセスがブロックされました` | テストユーザーに未追加 | ステップ4の手順6でGmailアドレスを追加 |
| `redirect_uri_mismatch` | アプリケーションの種類が違う | ステップ5で「デスクトップアプリ」を選択し直す |
| `invalid_client` | credentials.jsonの中身が壊れている | ステップ5からJSONを再ダウンロード |
| ブラウザが開かない | ネットワークまたは環境の問題 | ターミナルに表示されるURLを手動でブラウザに貼り付け |

---

## 基本的な使い方

### GUI版（推奨）

#### 起動方法

```bash
# Python版
python run_gui.py

# アプリ版: Calesk.appをダブルクリック
```

#### GUI画面の構成

```text
+---------------------------------------------+
| カレンダー壁紙アプリ                          |
+---------------------------------------------+
| テーマ: [simple ▼]  [今すぐ更新]              |
+---------------------------------------------+
|                                             |
|         壁紙プレビュー表示エリア              |
|                                             |
|                                             |
+---------------------------------------------+
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

## 複数Googleアカウントの設定

仕事用・プライベート用など、複数のGoogleアカウントのカレンダーを1枚の壁紙にまとめて表示できます。

### 事前準備（Google Cloud Console側）

複数アカウントを使う場合、**追加するすべてのGmailアドレスをGoogle Cloud Consoleのテストユーザーに登録する**必要があります。
これを忘れると「アクセスがブロックされました」エラーが出ます。

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 左側メニューの「APIとサービス」→「OAuth同意画面」をクリック
3. 画面下部の「テストユーザー」セクションを探す
4. 「**+ ADD USERS**」をクリック
5. 追加したいGoogleアカウントのGmailアドレスを入力して「**追加**」をクリック
6. **登録するアカウントの数だけこの操作を繰り返す**

> 例: 仕事用 `work@gmail.com` とプライベート用 `personal@gmail.com` の2つを使いたい場合、
> 両方のアドレスをテストユーザーに追加してください。
> `credentials.json`（OAuth設定ファイル）は1つで全アカウント共通です。追加でダウンロードする必要はありません。

### アカウントの追加手順

1. アプリのGUIを起動
2. メニューまたは設定ボタンから「**設定ダイアログ**」を開く
3. 「**Googleアカウント**」タブをクリック
4. 「**アカウント追加**」ボタンをクリック
5. アカウント名を入力（例: 「仕事用」「プライベート」など。あとで一覧に表示される名前）
6. ブラウザが自動的に開く
7. 追加したいGoogleアカウントでログイン
8. 「このアプリはGoogleで確認されていません」が表示された場合:
   - 「**詳細**」→「**Calesk（安全ではないページ）に移動**」をクリック
9. 「**許可**」をクリック
10. アプリに戻ると、アカウント一覧に新しいアカウントが追加される

> 2つ目以降のアカウントを追加する場合は、手順4〜10を繰り返してください。
> 追加ごとにブラウザの認証画面が開きます。

### アカウントごとの表示色を変更する

壁紙上でどのアカウントの予定かを区別するため、アカウントごとに色を設定できます。

1. 設定ダイアログの「Googleアカウント」タブを開く
2. 色を変更したいアカウントをクリックして選択
3. 「**色変更**」ボタンをクリック
4. カラーピッカーで好きな色を選択して「OK」

### アカウントの削除

1. 設定ダイアログの「Googleアカウント」タブを開く
2. 削除したいアカウントをクリックして選択
3. 「**削除**」ボタンをクリック

> 削除してもGoogleアカウント自体には影響しません。このアプリからの連携が解除されるだけです。

### 仕組みの補足

| 項目 | 説明 |
| --- | --- |
| credentials.json | OAuthクライアント設定。**全アカウント共通で1つだけ** |
| token_{id}.json | アカウントごとの認証トークン。アカウント追加時に自動生成 |
| accounts.json | アカウント一覧の管理ファイル（表示名・色・有効/無効） |
| 保存場所（Python版） | `config/` ディレクトリ |
| 保存場所（アプリ版） | `~/.calesk/config/` |

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

> **⚠️ 重要**: Caleskは常駐中のみ壁紙を自動更新します。
> アプリが起動していない状態では、**日付が変わっても壁紙は更新されません**。
> ログイン時に自動起動するよう設定することを推奨します。

### macOS（launchd）

手動設定の場合:

1. `~/Library/LaunchAgents/`に`.plist`ファイルを作成
2. デーモンモードで起動するように設定
3. `launchctl load`でサービスを登録

### Windows（スタートアップ / タスクスケジューラー）

#### アプリ版: スタートアップに登録（推奨）

1. `Win + R` → `shell:startup` と入力して Enter
2. 開いたフォルダに `Calesk.exe` のショートカットを作成
   - `Calesk.exe` を右クリック →「ショートカットの作成」
   - 作成したショートカットをスタートアップフォルダに移動

> PC起動時に自動的にアプリが立ち上がります。

#### Python版: タスクスケジューラー

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
3. ダウンロードしたファイル名が`client_secret_XXXXX.json`のままになっていないか確認

#### エラー: `The authentication token has expired`

**原因**: 認証トークンの有効期限切れ

**解決方法**:

```bash
rm credentials/token.json
python main.py --auth
```

#### エラー: `アクセスがブロックされました`

**原因**: Google Cloud ConsoleのOAuth同意画面で「テストユーザー」に自分のアドレスを追加していない

**解決方法**:

1. [Google Cloud Console](https://console.cloud.google.com/) → 「APIとサービス」→「OAuth同意画面」を開く
2. 「テストユーザー」セクションを確認
3. 自分のGmailアドレスが追加されていなければ「+ ADD USERS」で追加
4. 再度認証を実行:

```bash
rm credentials/token.json
python main.py --auth
```

#### エラー: `redirect_uri_mismatch`

**原因**: OAuthクライアントIDの「アプリケーションの種類」が「デスクトップアプリ」以外になっている

**解決方法**:

1. Google Cloud Console → 「認証情報」で既存のクライアントIDを削除
2. 新しいOAuthクライアントIDを「デスクトップアプリ」として作成し直す
3. 新しいcredentials.jsonをダウンロードして配置し直す

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

### アプリケーションのビルド

#### macOSビルド

```bash
source venv/bin/activate
bash scripts/build_app.sh
```

ビルド成果物: `dist/Calesk.app`

#### Windowsビルド

```cmd
venv\Scripts\activate.bat
scripts\build_app.bat
```

ビルド成果物: `dist\Calesk\Calesk.exe`

#### GitHub Actions（自動ビルド）

タグを push すると GitHub Actions が macOS / Windows 両方を自動ビルドし、GitHub Release にアップロードします。

```bash
git tag v1.0.0
git push origin v1.0.0
```

ビルド設定は `Calesk.spec`（macOS）と `Calesk_windows.spec`（Windows）で管理しています。
`credentials/` はバンドルに含まれないため、ユーザーは初回起動時に自分で配置する必要があります。

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
├── scripts/                      # ビルドスクリプト
├── assets/                       # リソース（背景画像等）
├── credentials/                  # 認証情報（.gitignore対象）
├── main.py                       # CLIエントリーポイント
├── run_gui.py                    # GUIエントリーポイント
├── Calesk.spec        # PyInstallerビルド設定
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

A: 対応しています。詳しい手順は [複数Googleアカウントの設定](#複数googleアカウントの設定) を参照してください。事前にGoogle Cloud Consoleで全アカウントをテストユーザーに追加する必要がある点にご注意ください。

### Q: 壁紙の解像度を変更したい

A: `src/config.py`の`IMAGE_WIDTH`と`IMAGE_HEIGHT`を変更してください。または`AUTO_DETECT_RESOLUTION = True`で自動検出を有効にしてください。

### Q: 背景画像を変更したい

A: GUI設定ダイアログの「背景画像」セクションから画像をアップロードできます。PNG、JPG、JPEG形式に対応しています。また`assets/background.jpg`を直接置き換えることも可能です。

### Q: 通知を無効にしたい

A: デーモンモードを使用せず、ワンショットモード（`--run-once`）のみを使用してください。

### Q: テーマをカスタマイズしたい

A: `src/themes.py`に新しいテーマを追加できます。既存テーマの辞書構造をコピーして、色やスタイルの値を変更してください。

### Q: Google Cloud Consoleの設定が難しい

A: [Google Calendar API設定](#google-calendar-api設定全員必須)セクションの手順に沿って進めてください。特にステップ4（OAuth同意画面）のテストユーザー追加を忘れやすいのでご注意ください。

### Q: アプリ版とPython版の違いは？

A: 機能は同じです。アプリ版はPythonのインストールが不要で、ダブルクリックで起動できます。Python版はソースコードを直接編集してカスタマイズできます。

---

## サポート

問題が発生した場合:

1. このガイドの「トラブルシューティング」セクションを確認
2. `calendar_app.log`でログを確認
3. [Issues](../../issues)で報告

---

**作者**: [音良林太郎](https://x.com/Otola_ryntaro) | **最終更新**: 2026-02-18
