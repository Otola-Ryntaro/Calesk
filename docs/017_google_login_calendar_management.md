# チケット017: GUI内Googleログイン・カレンダー管理

## 概要

アプリ内でGoogleアカウントにログインし、カレンダーの追加・管理ができるようにする。
各カレンダーごとにカード色が変わるようにする。

## 現状

- Google Calendar認証は `CalendarClient.authenticate()` でOAuth2フローを実行
- ブラウザが起動して認証 → トークン保存
- カレンダーIDは `config.py` の `CALENDAR_IDS` にハードコード
- カレンダーごとの色分けなし（`color_id` はイベント単位）

## 要件

### Phase 1: GUI内認証フロー
- アプリ内に「Googleログイン」ボタンを追加
- 認証状態の表示（ログイン済み/未ログイン）
- ログアウト機能

### Phase 2: カレンダー管理
- ログイン後、利用可能なカレンダー一覧を表示
- チェックボックスで表示するカレンダーを選択
- 選択状態を設定ファイルに保存

### Phase 3: カレンダーごとの色分け
- 各カレンダーに固有の色を割り当て
- Google Calendar APIから取得したカレンダーのカラーを使用
- カード背景色やカラーバーに反映

## 実装方法

### GUI内認証

```python
# src/ui/settings_dialog.py (新規)
class SettingsDialog(QDialog):
    def __init__(self):
        # Googleログインボタン
        # カレンダー一覧チェックボックス
        # 色設定
```

### カレンダー一覧取得

```python
# CalendarClient に追加
def get_calendar_list(self) -> List[Dict]:
    """利用可能なカレンダー一覧を取得"""
    result = self.service.calendarList().list().execute()
    return [{
        'id': cal['id'],
        'summary': cal['summary'],
        'backgroundColor': cal.get('backgroundColor', '#4285f4'),
        'selected': cal.get('selected', True)
    } for cal in result.get('items', [])]
```

### 設定保存

```python
# カレンダー選択状態をJSON設定ファイルに保存
# config/calendar_settings.json
{
    "calendars": [
        {"id": "primary", "enabled": true, "color": "#4285f4"},
        {"id": "xxx@group.calendar.google.com", "enabled": true, "color": "#ff6d01"}
    ]
}
```

## タスク

- [x] Phase 1: 設定ダイアログの作成（007-P3で完了済み）
- [x] Phase 1: GUI内認証フロー実装（is_authenticated, authenticate, logout）
- [x] Phase 1: 認証状態の表示（Googleアカウントタブ: ログイン/ログアウト/状態表示）
- [x] Phase 1: カレンダー一覧取得API実装（get_calendar_list）
- [ ] Phase 2: カレンダー選択UI実装
- [ ] Phase 2: 選択状態の保存・読み込み
- [ ] Phase 3: カレンダーごとの色マッピング
- [ ] Phase 3: カード描画への色反映
- [x] テスト追加（CalendarClient 17件 + SettingsDialog 15件 = 32件）
- [ ] 統合テスト

## 新規ファイル

- `src/ui/settings_dialog.py` - 設定ダイアログ
- `config/calendar_settings.json` - カレンダー設定

## 変更ファイル

- `src/calendar_client.py` - カレンダー一覧取得
- `src/ui/main_window.py` - 設定ボタン追加
- `src/image_generator.py` - カレンダー色反映

## 依存関係

- チケット016（デザイン再計画）の色分け部分と連携

## 優先度: LOW（将来実装）
## 工数: 大（8-12時間）
