"""
チケット022 Phase 5: 複数Googleアカウント - エッジケースのテスト
- 同じアカウントの重複追加防止
- トークン期限切れ時の検出
- アカウント0件時の動作
"""
import json
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
from datetime import datetime, timezone, timedelta

from src.calendar_client import CalendarClient
from src.models.event import CalendarEvent


@pytest.fixture
def tmp_config_dir(tmp_path):
    """一時的なconfig/ディレクトリを作成"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def accounts_json(tmp_config_dir):
    """accounts.jsonのパス"""
    return tmp_config_dir / "accounts.json"


def _write_accounts(accounts_json, accounts_list):
    """accounts.jsonにアカウントリストを書き込むヘルパー"""
    accounts_json.write_text(
        json.dumps({"accounts": accounts_list}, ensure_ascii=False),
        encoding="utf-8"
    )


class TestAccountDuplication:
    """同じアカウントの重複追加防止"""

    def test_add_duplicate_account_returns_none(self, tmp_config_dir, accounts_json):
        """既存メールアドレスと同じアカウント追加でNoneが返る"""
        # 既存アカウントをセットアップ
        existing_account = {
            "id": "account_1",
            "email": "user@gmail.com",
            "token_file": "token_account_1.json",
            "enabled": True,
            "color": "#4285f4",
            "display_name": "既存アカウント"
        }
        _write_accounts(accounts_json, [existing_account])

        client = CalendarClient.__new__(CalendarClient)
        client.creds = None
        client.service = None
        client.accounts = {}
        client._expired_accounts = {}

        # OAuth2フローをモック
        mock_creds = MagicMock()
        mock_service = MagicMock()
        mock_service.calendarList().list().execute.return_value = {
            'items': [{'id': 'user@gmail.com', 'summary': 'user@gmail.com', 'primary': True}]
        }

        with patch('src.calendar_client.CREDENTIALS_PATH', tmp_config_dir / "credentials.json"), \
             patch('src.calendar_client.CONFIG_DIR', tmp_config_dir), \
             patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_json), \
             patch('src.calendar_client.InstalledAppFlow') as mock_flow, \
             patch('src.calendar_client.build', return_value=mock_service):

            # credentials.jsonのダミーを作成
            (tmp_config_dir / "credentials.json").write_text('{}')

            mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds

            result = client.add_account("テスト")

        assert result is None

    def test_add_duplicate_account_does_not_modify_config(self, tmp_config_dir, accounts_json):
        """重複追加でaccounts.jsonが変更されない"""
        existing_account = {
            "id": "account_1",
            "email": "user@gmail.com",
            "token_file": "token_account_1.json",
            "enabled": True,
            "color": "#4285f4",
            "display_name": "既存アカウント"
        }
        _write_accounts(accounts_json, [existing_account])
        original_content = accounts_json.read_text()

        client = CalendarClient.__new__(CalendarClient)
        client.creds = None
        client.service = None
        client.accounts = {}
        client._expired_accounts = {}

        mock_creds = MagicMock()
        mock_service = MagicMock()
        mock_service.calendarList().list().execute.return_value = {
            'items': [{'id': 'user@gmail.com', 'summary': 'user@gmail.com', 'primary': True}]
        }

        with patch('src.calendar_client.CREDENTIALS_PATH', tmp_config_dir / "credentials.json"), \
             patch('src.calendar_client.CONFIG_DIR', tmp_config_dir), \
             patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_json), \
             patch('src.calendar_client.InstalledAppFlow') as mock_flow, \
             patch('src.calendar_client.build', return_value=mock_service):

            (tmp_config_dir / "credentials.json").write_text('{}')
            mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds
            client.add_account("テスト")

        # accounts.jsonの内容が変更されていないこと
        after_content = json.loads(accounts_json.read_text())
        assert len(after_content['accounts']) == 1
        assert after_content['accounts'][0]['email'] == "user@gmail.com"

    def test_add_unique_account_succeeds(self, tmp_config_dir, accounts_json):
        """異なるメールアドレスのアカウントは正常に追加できる"""
        existing_account = {
            "id": "account_1",
            "email": "user1@gmail.com",
            "token_file": "token_account_1.json",
            "enabled": True,
            "color": "#4285f4",
            "display_name": "アカウント1"
        }
        _write_accounts(accounts_json, [existing_account])

        client = CalendarClient.__new__(CalendarClient)
        client.creds = None
        client.service = None
        client.accounts = {}
        client._expired_accounts = {}

        mock_creds = MagicMock()
        mock_creds.to_json.return_value = '{"token": "test"}'
        mock_service = MagicMock()
        mock_service.calendarList().list().execute.return_value = {
            'items': [{'id': 'user2@gmail.com', 'summary': 'user2@gmail.com', 'primary': True}]
        }

        with patch('src.calendar_client.CREDENTIALS_PATH', tmp_config_dir / "credentials.json"), \
             patch('src.calendar_client.CONFIG_DIR', tmp_config_dir), \
             patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_json), \
             patch('src.calendar_client.InstalledAppFlow') as mock_flow, \
             patch('src.calendar_client.build', return_value=mock_service), \
             patch('os.chmod'):

            (tmp_config_dir / "credentials.json").write_text('{}')
            mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds
            result = client.add_account("アカウント2")

        assert result is not None
        assert result['email'] == "user2@gmail.com"


class TestTokenExpiration:
    """トークン期限切れ時の処理"""

    def test_expired_token_tracked_in_expired_accounts(self, tmp_config_dir, accounts_json):
        """期限切れトークンのアカウントが_expired_accountsに記録される"""
        account = {
            "id": "account_expired",
            "email": "expired@gmail.com",
            "token_file": "token_expired.json",
            "enabled": True,
            "color": "#ff0000",
            "display_name": "期限切れ"
        }
        _write_accounts(accounts_json, [account])

        # 期限切れトークンファイルを作成
        token_path = tmp_config_dir / "token_expired.json"
        token_path.write_text('{"token": "expired", "refresh_token": null}')

        client = CalendarClient.__new__(CalendarClient)
        client.creds = None
        client.service = None
        client.accounts = {}
        client._expired_accounts = {}

        # 期限切れクレデンシャルをモック
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = None  # リフレッシュ不可

        with patch('src.calendar_client.CONFIG_DIR', tmp_config_dir), \
             patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_json), \
             patch('src.calendar_client.Credentials.from_authorized_user_file', return_value=mock_creds):

            client.load_accounts()

        # アクティブには含まれない
        assert "account_expired" not in client.accounts
        # 期限切れリストに含まれる
        assert "account_expired" in client._expired_accounts
        assert client._expired_accounts["account_expired"]["email"] == "expired@gmail.com"

    def test_get_expired_account_ids(self, tmp_config_dir):
        """get_expired_account_ids()が期限切れアカウントIDを返す"""
        client = CalendarClient.__new__(CalendarClient)
        client._expired_accounts = {
            "acc_1": {"email": "a@gmail.com"},
            "acc_2": {"email": "b@gmail.com"},
        }

        expired_ids = client.get_expired_account_ids()

        assert set(expired_ids) == {"acc_1", "acc_2"}

    def test_valid_token_not_in_expired(self, tmp_config_dir, accounts_json):
        """有効なトークンのアカウントは_expired_accountsに含まれない"""
        account = {
            "id": "account_valid",
            "email": "valid@gmail.com",
            "token_file": "token_valid.json",
            "enabled": True,
            "color": "#00ff00",
            "display_name": "有効"
        }
        _write_accounts(accounts_json, [account])

        token_path = tmp_config_dir / "token_valid.json"
        token_path.write_text('{"token": "valid"}')

        client = CalendarClient.__new__(CalendarClient)
        client.creds = None
        client.service = None
        client.accounts = {}
        client._expired_accounts = {}

        mock_creds = MagicMock()
        mock_creds.valid = True

        mock_service = MagicMock()

        with patch('src.calendar_client.CONFIG_DIR', tmp_config_dir), \
             patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_json), \
             patch('src.calendar_client.Credentials.from_authorized_user_file', return_value=mock_creds), \
             patch('src.calendar_client.build', return_value=mock_service):

            client.load_accounts()

        assert "account_valid" in client.accounts
        assert "account_valid" not in client._expired_accounts


class TestZeroAccounts:
    """アカウント0件時の動作"""

    def test_get_all_events_with_no_accounts(self):
        """アカウント0件でget_all_eventsが空リストを返す"""
        client = CalendarClient.__new__(CalendarClient)
        client.accounts = {}
        client._expired_accounts = {}

        result = client.get_all_events(days=1)

        assert result == []

    def test_get_all_events_with_no_accounts_week(self):
        """アカウント0件でget_all_events(days=7)が空リストを返す"""
        client = CalendarClient.__new__(CalendarClient)
        client.accounts = {}
        client._expired_accounts = {}

        result = client.get_all_events(days=7)

        assert result == []

    def test_empty_accounts_json(self, tmp_config_dir, accounts_json):
        """空のaccounts.jsonでload_accountsが正常に動作する"""
        _write_accounts(accounts_json, [])

        client = CalendarClient.__new__(CalendarClient)
        client.creds = None
        client.service = None
        client.accounts = {}
        client._expired_accounts = {}

        with patch('src.calendar_client.CONFIG_DIR', tmp_config_dir), \
             patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_json):

            client.load_accounts()

        assert client.accounts == {}
        assert client._expired_accounts == {}

    def test_no_accounts_json_file(self, tmp_config_dir):
        """accounts.jsonが存在しない場合でもload_accountsが正常に動作する"""
        nonexistent = tmp_config_dir / "accounts.json"

        client = CalendarClient.__new__(CalendarClient)
        client.creds = None
        client.service = None
        client.accounts = {}
        client._expired_accounts = {}

        with patch('src.calendar_client.CONFIG_DIR', tmp_config_dir), \
             patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', nonexistent):

            client.load_accounts()

        assert client.accounts == {}
