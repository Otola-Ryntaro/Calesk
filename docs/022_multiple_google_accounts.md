# チケット022: 複数Googleアカウント対応

## 概要

複数のGoogleアカウントに対応し、各アカウントの予定を統合表示する。
アカウントごとに色分けして表示し、色は設定で変更可能にする。

## 現状

- 1つのGoogleアカウントのみ対応（`credentials/token.json`）
- `CalendarClient` は単一サービスインスタンスのみ管理
- カレンダーIDはハードコード（`config.py` の `CALENDAR_IDS`）
- アカウント単位の色分けなし

## 要件

### ユースケース

**例**: 仕事用Googleアカウント（work@company.com）とプライベート用Googleアカウント（private@gmail.com）の両方を統合表示し、仕事の予定は青、プライベートの予定は赤で表示する。

### 機能要件

1. **複数アカウント認証**
   - 複数のGoogleアカウントでログイン可能
   - アカウントごとにOAuth2トークンを保存
   - アカウント追加/削除機能

2. **イベント統合表示**
   - すべての有効なアカウントから予定を取得
   - 時系列で統合して表示
   - イベントにアカウント情報を紐付け

3. **アカウント単位の色分け**
   - アカウントごとに固有の色を割り当て
   - カード背景色やカラーバーに反映
   - 設定で色を変更可能

4. **UI要件**
   - 設定ダイアログにアカウント管理タブ
   - アカウント一覧表示（メールアドレス、有効/無効、色）
   - アカウント追加ボタン（OAuth2フロー起動）
   - アカウント削除ボタン
   - 色選択ダイアログ

## 技術設計

### Phase 1: 複数アカウント認証基盤（TDD）

#### 設定ファイル構造

**ファイル**: `config/accounts.json`

```json
{
  "accounts": [
    {
      "id": "account_1",
      "email": "user1@gmail.com",
      "token_file": "token_account_1.json",
      "enabled": true,
      "color": "#4285f4",
      "display_name": "仕事用"
    },
    {
      "id": "account_2",
      "email": "user2@gmail.com",
      "token_file": "token_account_2.json",
      "enabled": true,
      "color": "#ea4335",
      "display_name": "プライベート"
    }
  ]
}
```

#### CalendarClient 改修

```python
class CalendarClient:
    def __init__(self):
        self.accounts = {}  # {account_id: service}
        self.load_accounts()

    def load_accounts(self):
        """accounts.json から設定を読み込み、有効なアカウントのサービスを初期化"""
        config = self._read_accounts_config()
        for account in config.get('accounts', []):
            if account['enabled']:
                service = self._build_service(account['token_file'])
                self.accounts[account['id']] = {
                    'service': service,
                    'email': account['email'],
                    'color': account['color'],
                    'display_name': account.get('display_name', account['email'])
                }

    def add_account(self, display_name: str = "") -> Dict:
        """新しいアカウントを追加（OAuth2フロー起動）"""
        # 1. OAuth2フロー実行
        # 2. トークンを新規ファイルに保存
        # 3. accounts.json に追加
        # 4. サービスインスタンス作成
        pass

    def remove_account(self, account_id: str):
        """アカウントを削除"""
        # 1. accounts.json から削除
        # 2. トークンファイル削除
        # 3. サービスインスタンス削除
        pass

    def get_all_events(self) -> List[CalendarEvent]:
        """すべての有効なアカウントからイベントを取得して統合"""
        all_events = []
        for account_id, account_data in self.accounts.items():
            events = self._get_events_from_service(
                account_data['service'],
                account_id,
                account_data['color']
            )
            all_events.extend(events)

        # 時系列でソート
        return sorted(all_events, key=lambda e: e.start_datetime)

    def _get_events_from_service(self, service, account_id: str, color: str) -> List[CalendarEvent]:
        """1つのアカウントからイベントを取得"""
        # 既存の get_today_events() ロジックを流用
        # イベントに account_id と color を付与
        pass
```

#### CalendarEvent 拡張

```python
@dataclass
class CalendarEvent:
    # 既存フィールド
    summary: str
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str] = None
    description: Optional[str] = None

    # 新規フィールド
    account_id: str = "default"  # アカウントID
    account_color: str = "#4285f4"  # アカウント色
    account_display_name: str = ""  # アカウント表示名
```

### Phase 2: イベント統合取得（TDD）

#### 変更内容

- `get_today_events()` → `get_all_events()` に移行
- 複数アカウントからの並行取得
- イベントへのアカウント情報付与
- 時系列統合ソート

### Phase 3: UI実装（TDD）

#### 設定ダイアログ拡張

**ファイル**: `src/ui/settings_dialog.py`

```python
class SettingsDialog(QDialog):
    def __init__(self):
        # 既存タブ
        self.theme_tab = ThemeTab()
        self.google_account_tab = GoogleAccountTab()  # 既存

        # 新規タブ
        self.accounts_tab = AccountsManagementTab()  # 複数アカウント管理

        self.tabs.addTab(self.accounts_tab, "アカウント管理")

class AccountsManagementTab(QWidget):
    """複数アカウント管理タブ"""

    def __init__(self):
        self.account_list_widget = QListWidget()  # アカウント一覧
        self.add_account_button = QPushButton("アカウント追加")
        self.remove_account_button = QPushButton("削除")
        self.change_color_button = QPushButton("色変更")

        # シグナル接続
        self.add_account_button.clicked.connect(self.on_add_account)
        self.remove_account_button.clicked.connect(self.on_remove_account)
        self.change_color_button.clicked.connect(self.on_change_color)

    def on_add_account(self):
        """アカウント追加ボタンクリック"""
        display_name, ok = QInputDialog.getText(
            self, "アカウント追加", "アカウント名:"
        )
        if ok and display_name:
            # OAuth2フロー起動
            account = self.calendar_client.add_account(display_name)
            self.refresh_account_list()

    def on_remove_account(self):
        """削除ボタンクリック"""
        selected = self.account_list_widget.currentItem()
        if selected:
            account_id = selected.data(Qt.UserRole)
            self.calendar_client.remove_account(account_id)
            self.refresh_account_list()

    def on_change_color(self):
        """色変更ボタンクリック"""
        selected = self.account_list_widget.currentItem()
        if selected:
            account_id = selected.data(Qt.UserRole)
            color = QColorDialog.getColor()
            if color.isValid():
                self.calendar_client.update_account_color(
                    account_id, color.name()
                )
                self.refresh_account_list()
```

### Phase 4: 色分け表示（TDD）

#### ImageGenerator 改修

```python
class ImageGenerator:
    def _draw_single_event_card(self, draw, event, x, y, width, height):
        # アカウント色を使用
        account_color = self._parse_color(event.account_color)

        # カラーバー描画（アカウント色）
        self._draw_color_bar(draw, x, y, width, bar_height, account_color)

        # カード背景にアカウント色のティント追加（オプション）
        if self.theme['use_account_tint']:
            self._draw_account_tint(draw, x, y, width, height, account_color)
```

## タスク

### Phase 1: 複数アカウント認証基盤（TDD）
- [ ] `config/accounts.json` 設定ファイル構造設計
- [ ] `CalendarEvent` にアカウント情報フィールド追加
- [ ] `CalendarClient.load_accounts()` 実装（テスト先行）
- [ ] `CalendarClient.add_account()` 実装（テスト先行）
- [ ] `CalendarClient.remove_account()` 実装（テスト先行）
- [ ] `CalendarClient.update_account_color()` 実装（テスト先行）

### Phase 2: イベント統合取得（TDD）
- [ ] `CalendarClient.get_all_events()` 実装（テスト先行）
- [ ] `CalendarClient._get_events_from_service()` 実装（テスト先行）
- [ ] 時系列統合ソートのテスト
- [ ] `MainViewModel` の `get_all_events()` 移行

### Phase 3: UI実装（TDD）
- [ ] `AccountsManagementTab` ウィジェット実装（テスト先行）
- [ ] アカウント一覧表示UI
- [ ] アカウント追加ダイアログ
- [ ] アカウント削除確認ダイアログ
- [ ] 色選択ダイアログ
- [ ] 設定ダイアログへのタブ追加

### Phase 4: 色分け表示（TDD）
- [ ] `ImageGenerator._draw_single_event_card()` でアカウント色使用（テスト先行）
- [ ] アカウントティント機能（オプション）
- [ ] デフォルト色の自動割り当てロジック
- [ ] 統合テスト（複数アカウント × 複数イベント）

### Phase 5: エッジケースとエラーハンドリング
- [ ] アカウント0件時の動作
- [ ] 認証失敗時のエラーハンドリング
- [ ] トークン期限切れ時の再認証フロー
- [ ] 同じアカウントの重複追加防止

## 新規ファイル

- `config/accounts.json` - アカウント設定
- `src/ui/accounts_management_tab.py` - アカウント管理タブ

## 変更ファイル

- `src/calendar_client.py` - 複数アカウント管理
- `src/models/calendar_event.py` - アカウント情報フィールド追加
- `src/ui/settings_dialog.py` - アカウント管理タブ追加
- `src/viewmodels/main_viewmodel.py` - `get_all_events()` 使用
- `src/image_generator.py` - アカウント色反映
- `src/config.py` - アカウント設定パス追加

## 依存関係

- チケット017（カレンダー管理）とは独立
- チケット007（GUI実装）の設定ダイアログを拡張

## 優先度: HIGH
## 工数: 大（12-16時間）
## ステータス: ❌ 未着手

## 実装方針

1. **TDD厳守**: テストファースト、段階的実装
2. **段階的リリース**: Phase 1完了時点でコミット、Phase 2完了時点でコミット...
3. **後方互換性**: 既存の単一アカウント設定も引き続きサポート
4. **セキュリティ**: トークンファイルは `.gitignore` に追加済み

## 次のステップ

Phase 1のタスクから開始し、TDD方式で実装を進める。
