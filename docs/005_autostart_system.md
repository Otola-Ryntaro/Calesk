# 005: 毎日自動更新システム

## 優先度
**MEDIUM**

## 概要
カレンダー壁紙を毎日06:00に自動更新するシステム（クロスプラットフォーム対応）

## 要件
- [x] macOS対応（launchd）
- [x] Windows対応（タスクスケジューラー）
- [x] 毎日06:00に自動更新
- [x] 1日1回実行（リソース効率重視）
- [x] インストール/アンインストールスクリプト

## システム仕様

### 実行モード
- **ワンショットモード**: `python main.py --run-once`
- OSのスケジューラーで毎日06:00に起動
- 1回実行して終了（プロセス常駐なし）
- リソース効率が良い

### 対応OS

| OS | スケジューラー | 実行時刻 | 状態 |
|----|--------------|---------|------|
| **macOS** | launchd | 毎日06:00 | ✅ 実装済み |
| **Windows** | タスクスケジューラー | 毎日06:00 | ✅ 実装済み |
| **Linux** | systemd/cron | 毎日06:00 | ⏳ 将来対応 |

---

## macOS: インストール手順

### 1. インストール

```bash
cd /path/to/calender_desktop
bash scripts/install_autostart_mac.sh
```

### 2. 確認

```bash
# サービス確認
launchctl list | grep calendar-wallpaper

# ログ確認
tail -f launchd.log
tail -f launchd.error.log
```

### 3. 手動テスト

```bash
# 手動で壁紙更新をテスト
python main.py --run-once
```

### 4. アンインストール

```bash
bash scripts/uninstall_autostart_mac.sh
```

---

## Windows: インストール手順

### 1. インストール

PowerShellを**管理者として実行**し、以下を実行：

```powershell
cd C:\path\to\calender_desktop
.\scripts\install_autostart_windows.ps1
```

### 2. 確認

```powershell
# タスク確認
Get-ScheduledTask -TaskName "CalendarWallpaperUpdate"

# タスクスケジューラーGUIで確認
# Win + R → taskschd.msc
```

### 3. 手動テスト

```powershell
# 手動で壁紙更新をテスト
venv\Scripts\python.exe main.py --run-once
```

### 4. アンインストール

```powershell
.\scripts\uninstall_autostart_windows.ps1
```

---

## 設定変更

### 更新時刻の変更

更新時刻を変更する場合は、[src/config.py](../src/config.py) を編集し、サービスを再起動します：

```python
# src/config.py
UPDATE_TIME = '08:00'  # 06:00 → 08:00 に変更
```

**macOS**: サービスを再起動

```bash
bash scripts/uninstall_autostart_mac.sh
bash scripts/install_autostart_mac.sh
```

**Windows**: タスクを再登録

```powershell
.\scripts\uninstall_autostart_windows.ps1
.\scripts\install_autostart_windows.ps1
```

---

## トラブルシューティング

### macOS: サービスが起動しない

```bash
# エラーログ確認
tail -f launchd.error.log

# サービス状態確認
launchctl list | grep calendar-wallpaper

# 手動でアンロード→ロード
launchctl unload ~/Library/LaunchAgents/com.user.calendar-wallpaper.plist
launchctl load ~/Library/LaunchAgents/com.user.calendar-wallpaper.plist
```

### macOS: 権限エラー

```bash
# plistファイルの権限確認
ls -l ~/Library/LaunchAgents/com.user.calendar-wallpaper.plist

# 権限修正
chmod 644 ~/Library/LaunchAgents/com.user.calendar-wallpaper.plist
```

### Windows: タスクが実行されない

```powershell
# タスク履歴確認
# タスクスケジューラー → CalendarWallpaperUpdate → 履歴タブ

# 手動実行テスト
venv\Scripts\python.exe main.py --run-once

# タスクを手動実行
Start-ScheduledTask -TaskName "CalendarWallpaperUpdate"
```

### Windows: 権限エラー

PowerShellを**管理者として実行**していることを確認してください。

---

## ログファイル

| ファイル | 説明 | OS |
|---------|------|------|
| `calendar_app.log` | アプリケーションログ | 共通 |
| `launchd.log` | launchd標準出力 | macOS |
| `launchd.error.log` | launchdエラー出力 | macOS |

---

## 技術仕様

### macOS: launchd

**設定ファイル**: `com.user.calendar-wallpaper.plist`
**配置場所**: `~/Library/LaunchAgents/`
**実行タイミング**: `StartCalendarInterval`（毎日06:00）

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>6</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

### Windows: タスクスケジューラー

**タスク名**: `CalendarWallpaperUpdate`
**トリガー**: 毎日06:00
**アクション**: `venv\Scripts\python.exe main.py --run-once`

---

## 実装完了

✅ **2026-02-04 完了**

### 実装ファイル

**macOS**:
1. `com.user.calendar-wallpaper.plist` - launchd設定
2. `scripts/install_autostart_mac.sh` - インストールスクリプト
3. `scripts/uninstall_autostart_mac.sh` - アンインストールスクリプト

**Windows**:
4. `scripts/install_autostart_windows.ps1` - インストールスクリプト
5. `scripts/uninstall_autostart_windows.ps1` - アンインストールスクリプト

### テスト結果

- [x] macOS: インストール成功
- [x] macOS: サービス確認
- [x] macOS: 手動実行成功
- [ ] Windows: インストール（要Windows環境でテスト）

---

## 備考

- 既存のコードは変更なし（後方互換性維持）
- `--run-once` モードで1日1回実行（リソース効率重視）
- Linux対応は将来的な拡張として予定
