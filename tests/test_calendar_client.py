"""
CalendarClient のセキュリティテスト
"""
import os
import stat
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.calendar_client import CalendarClient
from src.config import TOKEN_PATH


class TestTokenSecurity:
    """OAuth token のセキュリティに関するテスト"""

    @patch('src.calendar_client.InstalledAppFlow')
    @patch('src.calendar_client.build')
    @patch('src.calendar_client.CREDENTIALS_PATH')
    def test_token_file_permissions_are_restricted(
        self,
        mock_creds_path,
        mock_build,
        mock_flow_class
    ):
        """
        TDD: token.json ファイルが 0o600 (owner read/write only) で作成されることを確認

        セキュリティ要件:
        - OAuth token は機密情報
        - 他のユーザーから読み取り不可にする必要がある
        - POSIX パーミッション 0o600 (rw-------) が必要
        """
        # Setup
        temp_token_path = Path('/tmp/test_token.json')
        if temp_token_path.exists():
            temp_token_path.unlink()

        # Mock credentials path to exist
        mock_creds_path.exists.return_value = True

        # Mock flow and credentials
        mock_flow = MagicMock()
        mock_flow_class.from_client_secrets_file.return_value = mock_flow

        mock_creds = MagicMock()
        mock_creds.to_json.return_value = '{"token": "test_token"}'
        mock_creds.valid = True
        mock_flow.run_local_server.return_value = mock_creds

        # Mock build to return service
        mock_build.return_value = MagicMock()

        # Execute
        client = CalendarClient()

        with patch('src.calendar_client.TOKEN_PATH', temp_token_path):
            result = client.authenticate()

        # Assert: ファイルが作成された
        assert temp_token_path.exists(), "token.json ファイルが作成されていない"

        # Assert: パーミッションが 0o600 である
        file_stat = os.stat(temp_token_path)
        file_permissions = stat.S_IMODE(file_stat.st_mode)

        assert file_permissions == 0o600, \
            f"token.json のパーミッションが不適切: {oct(file_permissions)} (期待値: 0o600)"

        # Cleanup
        if temp_token_path.exists():
            temp_token_path.unlink()

        # Assert: 認証が成功
        assert result is True, "認証が失敗した"

    def test_existing_token_file_permissions_are_checked(self):
        """
        既存の token.json ファイルのパーミッションが緩い場合、警告またはエラーを出すべき

        現在は実装されていないが、将来的に追加すべき機能
        """
        # TODO: 既存ファイルのパーミッションチェック機能を実装する場合のテスト
        pass
