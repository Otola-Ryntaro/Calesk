#!/bin/bash
# CalendarWallpaper.app インストールスクリプト

set -e  # エラー時に即座に終了

echo "========================================="
echo "Calendar Wallpaper インストール"
echo "========================================="

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# アプリケーションバンドルの存在確認
if [ ! -d "dist/CalendarWallpaper.app" ]; then
    echo "❌ エラー: dist/CalendarWallpaper.app が見つかりません"
    echo "先に scripts/build_app.sh を実行してビルドしてください"
    exit 1
fi

# インストール確認
echo ""
echo "以下の操作を実行します:"
echo "  1. CalendarWallpaper.app を /Applications にコピー"
echo "  2. LaunchAgent を ~/Library/LaunchAgents にコピー"
echo "  3. ログイン時自動起動を有効化"
echo ""
read -p "続行しますか? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "インストールをキャンセルしました"
    exit 0
fi

# [1] アプリケーションのコピー
echo ""
echo "[1/3] アプリケーションを /Applications にコピー中..."
if [ -d "/Applications/CalendarWallpaper.app" ]; then
    echo "既存のアプリケーションを削除します..."
    rm -rf "/Applications/CalendarWallpaper.app"
fi
cp -R "dist/CalendarWallpaper.app" "/Applications/"
echo "✅ アプリケーションをコピーしました"

# [2] LaunchAgent のコピー
echo ""
echo "[2/3] LaunchAgent を設定中..."
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="com.tkojima.calendarwallpaper.plist"

if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

if [ -f "$LAUNCH_AGENTS_DIR/$PLIST_FILE" ]; then
    echo "既存のLaunchAgentを削除します..."
    launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_FILE" 2>/dev/null || true
    rm -f "$LAUNCH_AGENTS_DIR/$PLIST_FILE"
fi

cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"
echo "✅ LaunchAgent をコピーしました"

# [3] LaunchAgent の有効化
echo ""
echo "[3/3] ログイン時自動起動を有効化中..."
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"
echo "✅ 自動起動を有効化しました"

# 完了メッセージ
echo ""
echo "========================================="
echo "インストール完了"
echo "========================================="
echo ""
echo "✅ CalendarWallpaper が /Applications にインストールされました"
echo "✅ ログイン時に自動起動するように設定されました"
echo ""
echo "📝 次のステップ:"
echo "  1. /Applications/CalendarWallpaper.app をダブルクリックして起動"
echo "  2. 初回起動時にGoogleアカウント認証を行ってください"
echo "  3. 設定から自動更新の間隔を調整できます"
echo ""
echo "🔧 アンインストール方法:"
echo "  scripts/uninstall_app.sh を実行してください"
