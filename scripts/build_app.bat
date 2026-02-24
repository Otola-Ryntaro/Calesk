@echo off
REM Calesk.exe ビルドスクリプト（Windows用）

echo =========================================
echo Calesk アプリケーションビルド
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
pyinstaller Calesk_windows.spec --clean --noconfirm

REM ビルド結果の確認
echo.
echo =========================================
echo ビルド完了
echo =========================================
if exist "dist\Calesk\Calesk.exe" (
    echo [OK] 実行ファイル: dist\Calesk\Calesk.exe
    echo.
    echo 起動テスト:
    echo   dist\Calesk\Calesk.exe
) else (
    echo [NG] ビルドに失敗しました
    exit /b 1
)
