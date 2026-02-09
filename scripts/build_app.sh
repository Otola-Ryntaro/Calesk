#!/bin/bash
# CalendarWallpaper.app ビルドスクリプト

set -e  # エラー時に即座に終了

echo "========================================="
echo "Calendar Wallpaper アプリケーションビルド"
echo "========================================="

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# 仮想環境のアクティベート確認
if [ -z "$VIRTUAL_ENV" ]; then
    echo "仮想環境をアクティベート中..."
    source venv/bin/activate
fi

# 古いビルドファイルのクリーンアップ
echo ""
echo "[1/2] 古いビルドファイルをクリーンアップ中..."
rm -rf build/ dist/

# PyInstaller でビルド
echo ""
echo "[2/2] PyInstaller でビルド中..."
echo "注: credentials/ はバンドルに含まれません。"
echo "    ユーザーは初回起動時に認証を行ってください。"
pyinstaller CalendarWallpaper.spec --clean --noconfirm

# ビルド結果の確認
echo ""
echo "========================================="
echo "ビルド完了"
echo "========================================="
if [ -d "dist/CalendarWallpaper.app" ]; then
    echo "✅ アプリケーションバンドル: dist/CalendarWallpaper.app"
    echo ""
    echo "アプリケーション情報:"
    ls -lh dist/CalendarWallpaper.app
    du -sh dist/CalendarWallpaper.app
    echo ""
    echo "起動テスト:"
    echo "  open dist/CalendarWallpaper.app"
else
    echo "❌ ビルドに失敗しました"
    exit 1
fi
