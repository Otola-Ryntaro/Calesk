# Calesk - ビルド・配布ガイド

## 📦 ビルド環境

- **Python**: 3.13.7
- **プラットフォーム**: macOS (Apple Silicon arm64 / Intel x86_64)
- **パッケージングツール**: PyInstaller 6.18.0

## 🔨 ビルド手順

### 1. 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone <repository-url>
cd calender_desktop

# 仮想環境の作成とアクティベート
python3.13 -m venv venv
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. アプリケーションのビルド

```bash
# ビルドスクリプトの実行
./scripts/build_app.sh
```

ビルドが成功すると、`dist/Calesk.app` が生成されます（約191MB）。

### 3. ビルド結果の確認

```bash
# アプリケーションバンドルのサイズ確認
du -sh dist/Calesk.app

# 起動テスト
open dist/Calesk.app
```

## 📥 インストール手順（ユーザー向け）

### 方法1: インストールスクリプト使用（推奨）

```bash
# インストール
./scripts/install_app.sh
```

このスクリプトは以下を実行します：
1. `Calesk.app` を `/Applications` にコピー
2. LaunchAgent を `~/Library/LaunchAgents` にコピー
3. ログイン時の自動起動を有効化

### 方法2: 手動インストール

```bash
# アプリケーションのコピー
cp -R dist/Calesk.app /Applications/

# （オプション）ログイン時自動起動の設定
cp com.example.calendarwallpaper.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.example.calendarwallpaper.plist
```

## 🗑️ アンインストール手順

```bash
# アンインストールスクリプトの実行
./scripts/uninstall_app.sh
```

手動でアンインストールする場合:

```bash
# LaunchAgentの無効化
launchctl unload ~/Library/LaunchAgents/com.example.calendarwallpaper.plist
rm ~/Library/LaunchAgents/com.example.calendarwallpaper.plist

# アプリケーションの削除
rm -rf /Applications/Calesk.app
```

## 🔧 トラブルシューティング

### ビルドエラー: "Module not found"

PyInstallerが特定のモジュールを検出できない場合、`Calesk.spec` の `hiddenimports` リストに追加してください。

```python
hiddenimports=[
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    # ... 追加のモジュール
],
```

### 起動エラー: "App is damaged"

macOSのセキュリティ設定により、署名されていないアプリがブロックされる場合があります。

```bash
# 署名の確認
codesign -dv --verbose=4 /Applications/Calesk.app

# ad-hoc署名の追加（PyInstallerが自動実行）
codesign --force --deep --sign - /Applications/Calesk.app
```

### Google認証エラー

初回起動時にGoogle認証が必要です。`credentials/credentials.json` が含まれていることを確認してください。

## 📦 配布パッケージの作成

### DMGイメージの作成（オプション）

```bash
# DMGイメージの作成
hdiutil create -volname "Calesk" \
  -srcfolder dist/Calesk.app \
  -ov -format UDZO \
  Calesk.dmg
```

## 🔐 コード署名（オプション）

Apple Developer Program に登録している場合、アプリケーションに署名できます。

```bash
# Developer ID Application証明書で署名
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  /Applications/Calesk.app

# 公証（Notarization）
xcrun notarytool submit Calesk.dmg \
  --apple-id "your@email.com" \
  --team-id "TEAM_ID" \
  --password "app-specific-password"
```

## 📝 ビルド設定ファイル

- `Calesk.spec`: PyInstaller設定ファイル
- `scripts/build_app.sh`: ビルド自動化スクリプト
- `com.example.calendarwallpaper.plist`: LaunchAgent設定ファイル

## 🎯 最適化オプション

### ファイルサイズの削減

```python
# Calesk.spec の excludes に不要なモジュールを追加
excludes=[
    'pytest',
    'pytest-qt',
    'tkinter',  # 使用していない場合
],
```

### ビルド速度の向上

```bash
# --noclean オプションでキャッシュを再利用
pyinstaller Calesk.spec --noconfirm
```

## 📊 ビルド情報

- **ビルドサイズ**: 約191MB（PyQt6、Python 3.13、依存ライブラリ含む）
- **対応アーキテクチャ**: arm64（Apple Silicon）、x86_64（Intel）はクロスビルド可能
- **最小macOSバージョン**: macOS 10.13（High Sierra）以降
