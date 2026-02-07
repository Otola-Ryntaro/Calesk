# カレンダー壁紙アプリの自動起動をインストール（Windows）
# PowerShellスクリプト

$ErrorActionPreference = "Stop"

Write-Host "=== カレンダー壁紙アプリ 自動起動インストール (Windows) ===" -ForegroundColor Green
Write-Host ""

# プロジェクトディレクトリの取得
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$PythonPath = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$MainScript = Join-Path $ProjectRoot "main.py"

# 仮想環境の確認
if (-not (Test-Path $PythonPath)) {
    Write-Host "❌ エラー: 仮想環境が見つかりません: $PythonPath" -ForegroundColor Red
    Write-Host "先に仮想環境を作成してください: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# タスクスケジューラーに登録
$TaskName = "CalendarWallpaperUpdate"
$TaskDescription = "カレンダー壁紙を毎日06:00に自動更新"

# 既存のタスクを削除
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "既存のタスクを削除しています..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# タスクアクション（実行するコマンド）
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "$MainScript --run-once" `
    -WorkingDirectory $ProjectRoot

# トリガー（毎日06:00）
$Trigger = New-ScheduledTaskTrigger -Daily -At "06:00"

# 設定
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

# タスクを登録
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -User $env:USERNAME

Write-Host ""
Write-Host "✅ インストール完了！" -ForegroundColor Green
Write-Host ""
Write-Host "📋 確認コマンド:" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host ""
Write-Host "📝 タスクスケジューラーで確認:" -ForegroundColor Cyan
Write-Host "  Win + R → taskschd.msc → タスクスケジューラライブラリ" -ForegroundColor White
Write-Host ""
Write-Host "🔄 毎日06:00に自動実行されます" -ForegroundColor Green
Write-Host ""
Write-Host "💡 手動でテストする場合:" -ForegroundColor Cyan
Write-Host "  cd $ProjectRoot" -ForegroundColor White
Write-Host "  venv\Scripts\python.exe main.py --run-once" -ForegroundColor White
