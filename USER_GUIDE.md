# Calesk（カレスク） - ユーザーガイド

Google Calendarの予定をデスクトップ壁紙に表示するアプリの、セットアップから使い方まで。

## 目次

1. [インストール手順](#インストール手順)
   - [macOS の場合](#macos-の場合)
   - [Windows の場合](#windows-の場合)
2. [Google Calendar API設定（全員必須）](#google-calendar-api設定全員必須)
3. [アプリの起動方法](#アプリの起動方法)
4. [複数Googleアカウントの設定](#複数googleアカウントの設定)
5. [テーマのカスタマイズ](#テーマのカスタマイズ)
6. [自動起動の設定](#自動起動の設定)
7. [トラブルシューティング](#トラブルシューティング)
8. [開発者向け情報](#開発者向け情報)

---

## インストール手順

Caleskは**Pythonで動作します**。以下の手順でセットアップしてください。
所要時間の目安：15〜20分程度（初回のみ）

---

### macOS の場合

1. **Python をインストールする** — ターミナルを開いて（`Cmd + スペース` → 「ターミナル」で検索）、以下を実行します。

   ```bash
   python3 --version
   ```

   `Python 3.11.x` 以上が表示されれば、このステップはスキップできます。
   表示されない場合は [python.org](https://www.python.org/downloads/) からインストーラーをダウンロードしてください。

   > ヒント: Homebrew を使っている場合は `brew install python` でもインストールできます。

2. **Git をインストールする** — 以下を実行して確認します。

   ```bash
   git --version
   ```

   インストールされていない場合は Xcode コマンドラインツールをインストールします：

   ```bash
   xcode-select --install
   ```

   ダイアログが表示されたら「インストール」をクリックしてください。

3. **リポジトリをクローンする** — ホームフォルダに移動して実行します：

   ```bash
   cd ~
   git clone https://github.com/Otola-Ryntaro/Calesk.git
   cd Calesk
   ```

4. **仮想環境を作成してパッケージをインストールする:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   インストールには1〜3分かかります。

   > 注意: ターミナルを閉じるたびに仮想環境が無効になります。次回起動前に `source venv/bin/activate` を実行してください。

5. **アプリを起動する:**

   ```bash
   python run_gui.py
   ```

   GUIウィンドウが開けばセットアップ成功です。次に [Google Calendar API設定](#google-calendar-api設定全員必須) を行ってください。

---

### Windows の場合

1. **Python をインストールする** — コマンドプロンプトを開いて（`Win + R` → `cmd` → Enter）、以下を実行します：

   ```cmd
   python --version
   ```

   `Python 3.11.x` 以上が表示されれば、このステップはスキップできます。
   表示されない場合は [python.org](https://www.python.org/downloads/) からインストーラーをダウンロードしてください。

   > 重要: インストール時に「**Add Python to PATH**」のチェックボックスを必ずONにしてください。

2. **Git をインストールする** — [git-scm.com](https://git-scm.com/download/win) からインストーラーをダウンロードしてインストールします（オプションはすべてデフォルトでOK）。インストール後、コマンドプロンプトを開き直して確認します：

   ```cmd
   git --version
   ```

3. **リポジトリをクローンする:**

   ```cmd
   cd %USERPROFILE%
   git clone https://github.com/Otola-Ryntaro/Calesk.git
   cd Calesk
   ```

4. **仮想環境を作成してパッケージをインストールする:**

   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

   インストールには1〜3分かかります。

   > 注意: コマンドプロンプトを閉じるたびに仮想環境が無効になります。次回起動前に `venv\Scripts\activate` を実行してください。

5. **アプリを起動する:**

   ```cmd
   python run_gui.py
   ```

   GUIウィンドウが開けばセットアップ成功です。次に [Google Calendar API設定](#google-calendar-api設定全員必須) を行ってください。

---

## Google Calendar API設定（全員必須）

Caleskはご自身のGoogleアカウントを使ってカレンダーデータを取得します。
そのために、Google Cloud上でAPI設定が1度だけ必要です。

**所要時間**: 初回のみ10〜15分程度
**必要なもの**: Googleアカウント（Gmailアドレス）、Webブラウザ

### ステップ1：Google Cloud Console にアクセス

1. ブラウザで [Google Cloud Console](https://console.cloud.google.com/) を開く
2. Googleアカウントでログインする

> 初めてGoogle Cloud Consoleを使う場合、利用規約への同意画面が表示されます。
> 「同意して続行」をクリックしてください。**料金は一切かかりません。**

### ステップ2：プロジェクトを作成

1. 画面上部の「プロジェクトを選択」をクリック
2. 右上にある「新しいプロジェクト」をクリック
3. **プロジェクト名**に `calesk`（任意の名前でOK）を入力
4. 「作成」をクリック
5. 作成完了の通知が出たら「プロジェクトを選択」をクリック

### ステップ3：Google Calendar API を有効にする

1. 左側メニューの「APIとサービス」→「ライブラリ」をクリック
2. 検索欄に `Google Calendar API` と入力
3. 「**Google Calendar API**」をクリック
4. 「**有効にする**」ボタンをクリック

### ステップ4：OAuth 同意画面を設定する

1. 左側メニューの「APIとサービス」→「OAuth同意画面」をクリック
2. 「外部」を選択して「作成」をクリック
3. 以下を入力：
   - **アプリ名**: `Calesk`
   - **ユーザーサポートメール**: 自分のGmailアドレス
   - **デベロッパーの連絡先情報**: 自分のGmailアドレス
4. 「保存して次へ」をクリック
5. 「スコープ」画面：
   - 「スコープを追加または削除」をクリック
   - `calendar` で検索し、`calendar.readonly` にチェック
   - 「更新」→「保存して次へ」
6. 「テストユーザー」画面：
   - 「**+ ADD USERS**」をクリック
   - **自分のGmailアドレス**を入力して「追加」→「保存して次へ」
7. 「ダッシュボードに戻る」をクリック

> **重要**: テストユーザーに自分のアドレスを追加しないと、認証時に「アクセスがブロックされました」と表示されます。

### ステップ5：OAuth クライアント ID を作成する

1. 「APIとサービス」→「認証情報」→「認証情報を作成」をクリック
2. 「**OAuthクライアントID**」を選択
3. **アプリケーションの種類**：「**デスクトップアプリ**」を選択
4. 名前：`Calesk Client`（任意）
5. 「作成」をクリック
6. 「**JSONをダウンロード**」をクリック（`client_secret_XXXXX.json` がダウンロードされる）

### ステップ6：credentials.json を配置する

ダウンロードしたファイルを `credentials/credentials.json` として配置します。

**macOS / Linux の場合（ターミナル）**:

```bash
cd ~/Calesk
cp ~/Downloads/client_secret_XXXXX.json credentials/credentials.json
```

> `client_secret_XXXXX.json` の部分は実際にダウンロードされたファイル名に置き換えてください。

**Windowsの場合（コマンドプロンプト）**:

```cmd
cd %USERPROFILE%\Calesk
copy %USERPROFILE%\Downloads\client_secret_XXXXX.json credentials\credentials.json
```

配置後の確認 — 以下の構成になっていればOKです：

```text
Calesk/
├── credentials/
│   └── credentials.json    ← このファイルがあればOK
├── src/
├── run_gui.py
...
```

### ステップ7：初回認証を実行する

仮想環境を有効化してアプリを起動してください：

```bash
python run_gui.py
```

ブラウザが自動的に開き、Googleアカウントの認証画面が表示されます。

1. カレンダーを使いたいGoogleアカウントを選択
2. 「このアプリはGoogleで確認されていません」と表示された場合：
   - 「**詳細**」をクリック
   - 「**Calesk（安全ではないページ）に移動**」をクリック
3. 「**許可**」をクリック
4. 「認証が完了しました」と表示されたらブラウザを閉じてOK

> 認証は初回のみです。次回以降は自動的にログインします。

### よくあるエラーと対処法

| エラー | 原因 | 対処法 |
| ------ | ---- | ------ |
| `credentials.json not found` | ファイルの場所またはファイル名が違う | ステップ6を再確認 |
| `アクセスがブロックされました` | テストユーザー未追加 | ステップ4-6で自分のアドレスを追加 |
| `redirect_uri_mismatch` | アプリの種類が「デスクトップアプリ」以外 | ステップ5でクライアントIDを作り直す |
| ブラウザが開かない | 環境の問題 | ターミナルに表示されるURLを手動でブラウザに貼り付け |

---

## アプリの起動方法

毎回の起動手順です。

### macOS で起動する

```bash
cd ~/Calesk
source venv/bin/activate
python run_gui.py
```

### Windows で起動する

```cmd
cd %USERPROFILE%\Calesk
venv\Scripts\activate
python run_gui.py
```

### GUI 画面の操作

起動するとメインウィンドウが開きます。

| 操作 | 方法 |
| ---- | ---- |
| テーマを変える | 「テーマ:」ドロップダウンから選択 |
| 壁紙を今すぐ更新 | 「今すぐ更新」ボタンをクリック |
| 設定を開く | 「設定」ボタン（⚙）をクリック |
| アカウントを追加 | 設定 → 「Googleアカウント」タブ |

### コマンドライン版（上級者向け）

```bash
# 壁紙を1回更新して終了
python main.py --run-once

# 常駐モード（毎朝6時に自動更新）
python main.py --daemon
```

---

## 複数Googleアカウントの設定

仕事用・プライベート用など、複数のGoogleアカウントのカレンダーを1枚の壁紙にまとめて表示できます。

追加したいすべてのGmailアドレスを、[ステップ4のテストユーザー](#ステップ4oauth-同意画面を設定する) に事前登録してください。

### アカウントの追加手順

1. アプリを起動して「設定」ボタンをクリック
2. 「Googleアカウント」タブを選択
3. 「アカウント追加」をクリック
4. アカウント名を入力（例：「仕事用」「プライベート」）
5. ブラウザが開くので、追加したいGoogleアカウントでログインして「許可」
6. アカウント一覧に追加されたことを確認

### 表示色の変更

壁紙上でアカウントを色で区別できます。設定 → 「Googleアカウント」タブ → アカウントを選択 → 「色変更」。

---

## テーマのカスタマイズ

7種類のテーマから選択できます。

| テーマ名 | 雰囲気 |
| -------- | ------ |
| **simple** | シンプル・ビジネス向け |
| **modern** | 半透明カード・スタイリッシュ |
| **pastel** | 淡い色・優しい印象 |
| **dark** | ダーク系・ゴールドアクセント |
| **vibrant** | 鮮やか・元気な印象 |
| **luxury** | アイボリー・上品 |
| **playful** | コーラルピンク・カジュアル |

テーマはGUI画面のドロップダウンからいつでも変更できます。

---

## 自動起動の設定

> アプリが起動していない状態では、日付が変わっても壁紙は更新されません。
> ログイン時に自動起動するよう設定しておくことをおすすめします。

### macOS でログイン時に自動起動する

以下の内容で `~/start_calesk.sh` を作成し、実行権限を付与します：

```bash
#!/bin/bash
cd ~/Calesk
source venv/bin/activate
python run_gui.py
```

```bash
chmod +x ~/start_calesk.sh
```

その後、「システム設定」→「一般」→「ログイン項目」→「+」→ このスクリプトを追加します。

### Windows でスタートアップに登録する

`Win + R` → `shell:startup` → Enter で開いたフォルダに、以下の内容で `start_calesk.bat` を作成します：

```bat
@echo off
cd %USERPROFILE%\Calesk
call venv\Scripts\activate
start pythonw run_gui.py
```

---

## トラブルシューティング

### 「仮想環境が有効化できない」（Windows）

PowerShell を管理者として開き、以下を実行してください：

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 「pip install でエラーになる」

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 「credentials.json not found」

```bash
ls credentials/
# credentials.json が表示されればOK
```

### 「The authentication token has expired」

```bash
rm credentials/token.json
python run_gui.py
```

### 「アクセスがブロックされました」

Google Cloud Console → 「APIとサービス」→「OAuth同意画面」→「テストユーザー」に、
ログインしようとしているGmailアドレスが追加されているか確認してください。

### 「Font not found」または文字化け

`src/config.py` の `FONT_PATHS` を、システムにインストールされている日本語フォントのパスに修正してください。

```bash
# macOSでフォントを確認
ls /System/Library/Fonts/ | grep ヒラギノ
```

### 壁紙が更新されない

```bash
tail -f calendar_app.log
python main.py --run-once
```

---

## 開発者向け情報

### テスト実行

```bash
source venv/bin/activate
python -m pytest tests/ -v --tb=short
python -m pytest tests/ --cov=src --cov-report=html
```

### ディレクトリ構造

```text
Calesk/
├── src/
│   ├── models/              # データモデル
│   ├── renderers/           # 描画Mixin（エフェクト・カード・カレンダー）
│   ├── ui/                  # PyQt6 GUI
│   ├── viewmodels/          # ViewModel層
│   ├── calendar_client.py   # Google Calendar API
│   ├── image_generator.py   # 壁紙生成
│   ├── themes.py            # テーマ定義（7種）
│   └── config.py            # 設定
├── tests/                   # テストコード
├── assets/                  # 背景画像等
├── credentials/             # 認証情報（.gitignore対象）
├── main.py                  # CLIエントリーポイント
├── run_gui.py               # GUIエントリーポイント
└── requirements.txt
```

### アーキテクチャ

```text
MVVM + Service層

UI (PyQt6) → ViewModel → WallpaperService → ImageGenerator / CalendarClient
                                              |-- EffectsRendererMixin
                                              |-- CardRendererMixin
                                              +-- CalendarRendererMixin
```

---

## サポート

問題が解決しない場合：

1. `calendar_app.log` の内容を確認する
2. [Issues](https://github.com/Otola-Ryntaro/Calesk/issues) で報告する

---

**作者**: [音良林太郎](https://x.com/Otola_ryntaro) | **最終更新**: 2026-02-24
