#!/bin/bash
# カレンダー壁紙アプリの自動起動をインストール（macOS）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PLIST_NAME="com.user.calendar-wallpaper.plist"
PLIST_SOURCE="$PROJECT_ROOT/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=== カレンダー壁紙アプリ 自動起動インストール (macOS) ==="
echo ""

# 1. plistファイルの存在確認
if [ ! -f "$PLIST_SOURCE" ]; then
    echo "❌ エラー: $PLIST_SOURCE が見つかりません"
    exit 1
fi

# 2. 仮想環境の確認
PYTHON_PATH="$PROJECT_ROOT/venv/bin/python"
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ エラー: 仮想環境が見つかりません: $PYTHON_PATH"
    echo "先に仮想環境を作成してください: python3 -m venv venv"
    exit 1
fi

# 3. LaunchAgentsディレクトリの作成
mkdir -p "$HOME/Library/LaunchAgents"

# 4. 既存のサービスを停止・アンロード
if launchctl list | grep -q "com.user.calendar-wallpaper"; then
    echo "既存のサービスを停止しています..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# 5. plistファイルをコピー
echo "plistファイルをコピーしています..."
cp "$PLIST_SOURCE" "$PLIST_DEST"

# 6. 権限設定
chmod 644 "$PLIST_DEST"

# 7. サービスをロード
echo "サービスを起動しています..."
launchctl load "$PLIST_DEST"

echo ""
echo "✅ インストール完了！"
echo ""
echo "📋 確認コマンド:"
echo "  launchctl list | grep calendar-wallpaper"
echo ""
echo "📝 ログ確認:"
echo "  tail -f $PROJECT_ROOT/launchd.log"
echo "  tail -f $PROJECT_ROOT/launchd.error.log"
echo ""
echo "🔄 毎日06:00に自動実行されます"
echo ""
echo "💡 手動でテストする場合:"
echo "  cd $PROJECT_ROOT && python main.py --run-once"
