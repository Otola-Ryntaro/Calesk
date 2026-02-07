# カレンダー壁紙アプリの自動起動をアンインストール（Windows）
$ErrorActionPreference = "Stop"

Write-Host "=== カレンダー壁紙アプリ 自動起動アンインストール (Windows) ===" -ForegroundColor Green
Write-Host ""

$TaskName = "CalendarWallpaperUpdate"

# タスクの削除
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Write-Host "タスクを削除しています..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "✅ アンインストール完了！" -ForegroundColor Green
} else {
    Write-Host "⚠️  タスクが見つかりません" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "自動起動が無効化されました" -ForegroundColor White
