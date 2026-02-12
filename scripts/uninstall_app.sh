#!/bin/bash
# Calesk.app アンインストールスクリプト

set -e  # エラー時に即座に終了

echo "========================================="
echo "Calesk アンインストール"
echo "========================================="

# アンインストール確認
echo ""
echo "以下の操作を実行します:"
echo "  1. /Applications/Calesk.app を削除"
echo "  2. LaunchAgent を削除"
echo "  3. ログイン時自動起動を無効化"
echo ""
read -p "続行しますか? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "アンインストールをキャンセルしました"
    exit 0
fi

# [1] LaunchAgent の無効化
echo ""
echo "[1/3] ログイン時自動起動を無効化中..."
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="com.tkojima.calesk.plist"

if [ -f "$LAUNCH_AGENTS_DIR/$PLIST_FILE" ]; then
    launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_FILE" 2>/dev/null || true
    rm -f "$LAUNCH_AGENTS_DIR/$PLIST_FILE"
    echo "✅ 自動起動を無効化しました"
else
    echo "⚠️  LaunchAgent が見つかりませんでした（スキップ）"
fi

# [2] アプリケーションの削除
echo ""
echo "[2/3] アプリケーションを削除中..."
if [ -d "/Applications/Calesk.app" ]; then
    rm -rf "/Applications/Calesk.app"
    echo "✅ アプリケーションを削除しました"
else
    echo "⚠️  アプリケーションが見つかりませんでした（スキップ）"
fi

# [3] ユーザーデータの確認
echo ""
echo "[3/3] ユーザーデータの確認..."
echo ""
echo "以下のユーザーデータは保持されています:"
echo "  - Google認証情報 (プロジェクト内の credentials/)"
echo "  - 設定ファイル (プロジェクト内)"
echo ""
echo "これらのデータを削除する場合は、手動で削除してください。"

# 完了メッセージ
echo ""
echo "========================================="
echo "アンインストール完了"
echo "========================================="
