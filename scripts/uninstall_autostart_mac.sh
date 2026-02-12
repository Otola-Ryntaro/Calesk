#!/bin/bash
# Caleskの自動起動をアンインストール（macOS）

set -e

PLIST_NAME="com.user.calesk.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=== Calesk 自動起動アンインストール (macOS) ==="
echo ""

# 1. サービスの停止・アンロード
if launchctl list | grep -q "com.user.calesk"; then
    echo "サービスを停止しています..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
else
    echo "⚠️  サービスは実行されていません"
fi

# 2. plistファイルの削除
if [ -f "$PLIST_DEST" ]; then
    echo "plistファイルを削除しています..."
    rm "$PLIST_DEST"
    echo "✅ アンインストール完了！"
else
    echo "⚠️  plistファイルが見つかりません"
fi

echo ""
echo "自動起動が無効化されました"
