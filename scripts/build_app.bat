@echo off
REM CalendarWallpaper.exe ビルドスクリプト（Windows用）

echo =========================================
echo Calendar Wallpaper アプリケーションビルド
echo =========================================

REM プロジェクトルートに移動
cd /d "%~dp0\.."

REM 仮想環境のアクティベート確認
if "%VIRTUAL_ENV%"=="" (
    echo 仮想環境をアクティベート中...
    call venv\Scripts\activate.bat
)

REM 古いビルドファイルのクリーンアップ
echo.
echo [1/2] 古いビルドファイルをクリーンアップ中...
if exist build rd /s /q build
if exist dist rd /s /q dist

REM PyInstaller でビルド
echo.
echo [2/2] PyInstaller でビルド中...
echo 注: credentials\ はバンドルに含まれません。
echo     ユーザーは初回起動時に認証を行ってください。
pyinstaller CalendarWallpaper_windows.spec --clean --noconfirm

REM ビルド結果の確認
echo.
echo =========================================
echo ビルド完了
echo =========================================
if exist "dist\CalendarWallpaper\CalendarWallpaper.exe" (
    echo [OK] 実行ファイル: dist\CalendarWallpaper\CalendarWallpaper.exe
    echo.
    echo 起動テスト:
    echo   dist\CalendarWallpaper\CalendarWallpaper.exe
) else (
    echo [NG] ビルドに失敗しました
    exit /b 1
)
