"""
CalendarClient のテスト
セキュリティ・イベント解析・今日の予定取得に関するテスト
"""
import os
import stat
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import pytest

from src.calendar_client import CalendarClient
from src.config import TOKEN_PATH
from src.models.event import CalendarEvent
from datetime import datetime, timezone, timedelta


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


class TestEventParsing:
    """イベント解析に関するテスト"""

    def test_parse_event_returns_calendar_event(self):
        """_parse_eventがCalendarEventオブジェクトを返すことを確認"""
        client = CalendarClient()

        # Google Calendar APIから取得されるイベントデータのモック
        api_event = {
            'id': 'event123',
            'summary': 'ミーティング',
            'start': {
                'dateTime': '2026-02-05T14:00:00+09:00'
            },
            'end': {
                'dateTime': '2026-02-05T15:00:00+09:00'
            },
            'location': 'オンライン',
            'description': '定例会議',
            'colorId': '5'
        }

        result = client._parse_event(api_event, 'primary')

        # CalendarEventオブジェクトが返される
        assert isinstance(result, CalendarEvent)
        assert result.id == 'event123'
        assert result.summary == 'ミーティング'
        assert result.calendar_id == 'primary'
        assert result.location == 'オンライン'
        assert result.description == '定例会議'
        assert result.color_id == '5'
        assert result.is_all_day is False

    def test_parse_all_day_event(self):
        """終日イベントを正しく解析できることを確認"""
        client = CalendarClient()

        api_event = {
            'id': 'event456',
            'summary': '休暇',
            'start': {
                'date': '2026-02-07'
            },
            'end': {
                'date': '2026-02-08'
            }
        }

        result = client._parse_event(api_event, 'personal')

        assert isinstance(result, CalendarEvent)
        assert result.summary == '休暇'
        assert result.is_all_day is True

    def test_parse_event_with_missing_optional_fields(self):
        """オプションフィールドが欠けているイベントを解析できることを確認"""
        client = CalendarClient()

        api_event = {
            'id': 'event789',
            'summary': 'タスク',
            'start': {
                'dateTime': '2026-02-05T09:00:00+09:00'
            },
            'end': {
                'dateTime': '2026-02-05T10:00:00+09:00'
            }
        }

        result = client._parse_event(api_event, 'work')

        assert isinstance(result, CalendarEvent)
        assert result.summary == 'タスク'
        assert result.location == ''
        assert result.description == ''
        assert result.color_id == '1'  # デフォルト値

    def test_get_events_returns_list_of_calendar_events(self):
        """get_eventsがCalendarEventのリストを返すことを確認"""
        client = CalendarClient()

        # serviceを直接Mockに置き換え
        client.service = Mock()

        # APIレスポンスのモック
        mock_events_result = {
            'items': [
                {
                    'id': 'event1',
                    'summary': 'イベント1',
                    'start': {'dateTime': '2026-02-05T10:00:00+09:00'},
                    'end': {'dateTime': '2026-02-05T11:00:00+09:00'}
                },
                {
                    'id': 'event2',
                    'summary': 'イベント2',
                    'start': {'dateTime': '2026-02-05T14:00:00+09:00'},
                    'end': {'dateTime': '2026-02-05T15:00:00+09:00'}
                }
            ]
        }

        mock_list = Mock()
        mock_list.execute.return_value = mock_events_result
        client.service.events.return_value.list.return_value = mock_list

        with patch('src.calendar_client.CALENDAR_IDS', ['primary']):
            result = client.get_events(days=7)

        # CalendarEventのリストが返される
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(event, CalendarEvent) for event in result)
        assert result[0].summary == 'イベント1'
        assert result[1].summary == 'イベント2'


class TestGetTodayEvents:
    """
    H-3: 「今日の予定」が当日全件になっていない問題のテスト

    問題: timeMin=now のため、既に開始した予定や終日予定が取得されない
    期待: 当日00:00~23:59:59の全予定を取得する
    """

    def _make_mock_client_with_events(self, api_events):
        """テスト用ヘルパー: APIレスポンスをモックしたクライアントを作成"""
        client = CalendarClient()
        client.service = Mock()

        mock_events_result = {'items': api_events}
        mock_list = Mock()
        mock_list.execute.return_value = mock_events_result
        client.service.events.return_value.list.return_value = mock_list

        return client

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    @patch('src.calendar_client.datetime')
    def test_today_events_includes_already_started_events(self, mock_datetime):
        """
        既に開始済みのイベントが取得できることを確認

        シナリオ: 現在15:00、10:00-11:00のミーティングが取得されるべき
        """
        # 現在時刻を2026-02-05 15:00:00 JSTに固定
        mock_now = datetime(2026, 2, 5, 15, 0, 0)
        mock_now_utc = datetime(2026, 2, 5, 6, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.min = datetime.min
        mock_datetime.max = datetime.max
        mock_datetime.fromisoformat = datetime.fromisoformat

        # 10:00-11:00の既に終了したイベント（取得されるべき）
        api_events = [
            {
                'id': 'past_event',
                'summary': '朝のミーティング',
                'start': {'dateTime': '2026-02-05T10:00:00+09:00'},
                'end': {'dateTime': '2026-02-05T11:00:00+09:00'}
            },
            {
                'id': 'future_event',
                'summary': '夕方の会議',
                'start': {'dateTime': '2026-02-05T17:00:00+09:00'},
                'end': {'dateTime': '2026-02-05T18:00:00+09:00'}
            }
        ]

        client = self._make_mock_client_with_events(api_events)
        result = client.get_today_events()

        # 既に開始済みのイベントも含め、2件取得されるべき
        assert len(result) == 2
        summaries = [e.summary for e in result]
        assert '朝のミーティング' in summaries
        assert '夕方の会議' in summaries

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    @patch('src.calendar_client.datetime')
    def test_today_events_includes_all_day_events(self, mock_datetime):
        """
        終日イベントが取得できることを確認

        シナリオ: 今日が休暇の終日イベントが設定されている
        """
        mock_now = datetime(2026, 2, 5, 15, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.min = datetime.min
        mock_datetime.max = datetime.max
        mock_datetime.fromisoformat = datetime.fromisoformat

        api_events = [
            {
                'id': 'allday_event',
                'summary': '休暇',
                'start': {'date': '2026-02-05'},
                'end': {'date': '2026-02-06'}
            }
        ]

        client = self._make_mock_client_with_events(api_events)
        result = client.get_today_events()

        # 終日イベントが取得されるべき
        assert len(result) == 1
        assert result[0].summary == '休暇'
        assert result[0].is_all_day is True

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    @patch('src.calendar_client.datetime')
    def test_today_events_api_called_with_day_start(self, mock_datetime):
        """
        APIが当日00:00:00をtimeMinとして呼び出されることを確認

        これが修正の核心: timeMinがnow()ではなく、当日の00:00:00であるべき
        """
        mock_now = datetime(2026, 2, 5, 15, 30, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.min = datetime.min
        mock_datetime.max = datetime.max
        mock_datetime.fromisoformat = datetime.fromisoformat

        client = CalendarClient()
        client.service = Mock()

        mock_list = Mock()
        mock_list.execute.return_value = {'items': []}
        client.service.events.return_value.list.return_value = mock_list

        client.get_today_events()

        # API呼び出しのtimeMin/timeMaxパラメータを検証
        call_kwargs = client.service.events.return_value.list.call_args
        time_min_arg = call_kwargs.kwargs.get('timeMin') or call_kwargs[1].get('timeMin')
        time_max_arg = call_kwargs.kwargs.get('timeMax') or call_kwargs[1].get('timeMax')

        # timeMinは当日の00:00:00を含むべき（時刻部分の検証）
        assert '00:00:00' in time_min_arg, \
            f"timeMinが当日の00:00:00ではない: {time_min_arg}"

        # timeMaxは当日の23:59:59または翌日00:00:00を含むべき
        assert '2026-02-05' in time_min_arg, \
            f"timeMinの日付が今日(2026-02-05)ではない: {time_min_arg}"

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    @patch('src.calendar_client.datetime')
    def test_today_events_excludes_tomorrow_events(self, mock_datetime):
        """
        翌日のイベントが除外されることを確認
        """
        mock_now = datetime(2026, 2, 5, 15, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.min = datetime.min
        mock_datetime.max = datetime.max
        mock_datetime.fromisoformat = datetime.fromisoformat

        api_events = [
            {
                'id': 'today_event',
                'summary': '今日の予定',
                'start': {'dateTime': '2026-02-05T10:00:00+09:00'},
                'end': {'dateTime': '2026-02-05T11:00:00+09:00'}
            },
            {
                'id': 'tomorrow_event',
                'summary': '明日の予定',
                'start': {'dateTime': '2026-02-06T10:00:00+09:00'},
                'end': {'dateTime': '2026-02-06T11:00:00+09:00'}
            }
        ]

        client = self._make_mock_client_with_events(api_events)
        result = client.get_today_events()

        # 今日のイベントのみが取得されるべき
        summaries = [e.summary for e in result]
        assert '今日の予定' in summaries
        assert '明日の予定' not in summaries

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    @patch('src.calendar_client.datetime')
    def test_today_events_returns_empty_when_no_events(self, mock_datetime):
        """
        今日のイベントがない場合、空リストを返すことを確認
        """
        mock_now = datetime(2026, 2, 5, 15, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.min = datetime.min
        mock_datetime.max = datetime.max
        mock_datetime.fromisoformat = datetime.fromisoformat

        client = self._make_mock_client_with_events([])
        result = client.get_today_events()

        assert result == []

    def test_today_events_returns_empty_when_service_not_initialized(self):
        """
        サービス未初期化時に空リストを返すことを確認
        """
        client = CalendarClient()
        # service = None の状態

        result = client.get_today_events()

        assert result == []

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    def test_today_events_returns_empty_on_http_error(self):
        """
        API通信エラー時に空リストを返すことを確認
        """
        from googleapiclient.errors import HttpError

        client = CalendarClient()
        client.service = Mock()

        # HttpErrorをシミュレート
        mock_response = Mock()
        mock_response.status = 403
        mock_response.reason = 'Forbidden'
        client.service.events.return_value.list.return_value.execute.side_effect = \
            HttpError(mock_response, b'Access denied')

        result = client.get_today_events()

        assert result == []

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    def test_today_events_returns_empty_on_general_exception(self):
        """
        予期しない例外時に空リストを返すことを確認
        """
        client = CalendarClient()
        client.service = Mock()

        # 一般的な例外をシミュレート
        client.service.events.return_value.list.return_value.execute.side_effect = \
            RuntimeError('ネットワーク接続エラー')

        result = client.get_today_events()

        assert result == []

    @patch('src.calendar_client.CALENDAR_IDS', ['primary', 'work@group.calendar.google.com'])
    @patch('src.calendar_client.datetime')
    def test_today_events_from_multiple_calendars(self, mock_datetime):
        """
        複数カレンダーからの今日のイベントが統合されることを確認
        """
        mock_now = datetime(2026, 2, 5, 10, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.min = datetime.min
        mock_datetime.max = datetime.max
        mock_datetime.fromisoformat = datetime.fromisoformat

        client = CalendarClient()
        client.service = Mock()

        # カレンダーごとに異なるレスポンスを返す
        primary_response = {
            'items': [
                {
                    'id': 'personal_event',
                    'summary': '個人の予定',
                    'start': {'dateTime': '2026-02-05T09:00:00+09:00'},
                    'end': {'dateTime': '2026-02-05T10:00:00+09:00'}
                }
            ]
        }
        work_response = {
            'items': [
                {
                    'id': 'work_event',
                    'summary': '仕事の予定',
                    'start': {'dateTime': '2026-02-05T14:00:00+09:00'},
                    'end': {'dateTime': '2026-02-05T15:00:00+09:00'}
                }
            ]
        }

        # 呼び出しごとに異なるレスポンスを返す
        mock_list = Mock()
        mock_list.execute.side_effect = [primary_response, work_response]
        client.service.events.return_value.list.return_value = mock_list

        result = client.get_today_events()

        assert len(result) == 2
        summaries = [e.summary for e in result]
        assert '個人の予定' in summaries
        assert '仕事の予定' in summaries

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    @patch('src.calendar_client.datetime')
    def test_today_events_includes_overnight_event_from_previous_day(self, mock_datetime):
        """
        前日開始・当日継続イベントが取得されることを確認

        シナリオ: 前日23:00に開始し、当日01:00に終了するイベント
        期待: start_datetime < day_end かつ end_datetime > day_start なので含まれるべき

        Codex指摘: event.start_datetime.date() == today では
        前日開始の継続中イベントが除外される
        """
        mock_now = datetime(2026, 2, 5, 10, 0, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.min = datetime.min
        mock_datetime.max = datetime.max
        mock_datetime.fromisoformat = datetime.fromisoformat
        mock_datetime.side_effect = lambda *a, **kw: datetime(*a, **kw)

        # 前日23:00開始、当日01:00終了のイベント
        # Google Calendar APIは timeMin/timeMax の範囲と重なるイベントを返す
        api_events = [
            {
                'id': 'overnight_event',
                'summary': '深夜作業',
                'start': {'dateTime': '2026-02-04T23:00:00+09:00'},
                'end': {'dateTime': '2026-02-05T01:00:00+09:00'}
            },
            {
                'id': 'normal_event',
                'summary': '朝のミーティング',
                'start': {'dateTime': '2026-02-05T09:00:00+09:00'},
                'end': {'dateTime': '2026-02-05T10:00:00+09:00'}
            }
        ]

        client = self._make_mock_client_with_events(api_events)
        result = client.get_today_events()

        # 前日開始だが当日に跨がるイベントも含まれるべき
        assert len(result) == 2, \
            f"前日開始の継続イベントが除外されている: {[e.summary for e in result]}"
        summaries = [e.summary for e in result]
        assert '深夜作業' in summaries, \
            "前日開始・当日跨ぎのイベントが含まれていない"
        assert '朝のミーティング' in summaries

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    @patch('src.calendar_client.datetime')
    def test_today_events_timemax_is_next_day_midnight(self, mock_datetime):
        """
        timeMaxパラメータが翌日00:00:00であることを検証

        Codex指摘: timeMaxパラメータが未検証だった
        期待: timeMaxは翌日の00:00:00（2026-02-06T00:00:00）にタイムゾーンオフセット付き
        """
        mock_now = datetime(2026, 2, 5, 15, 30, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.min = datetime.min
        mock_datetime.max = datetime.max
        mock_datetime.fromisoformat = datetime.fromisoformat

        client = CalendarClient()
        client.service = Mock()

        mock_list = Mock()
        mock_list.execute.return_value = {'items': []}
        client.service.events.return_value.list.return_value = mock_list

        client.get_today_events()

        # API呼び出しのtimeMaxパラメータを検証
        call_kwargs = client.service.events.return_value.list.call_args
        time_max_arg = call_kwargs.kwargs.get('timeMax') or call_kwargs[1].get('timeMax')

        # timeMaxは翌日(2026-02-06)の00:00:00を含むべき
        assert '2026-02-06' in time_max_arg, \
            f"timeMaxが翌日ではない: {time_max_arg}"
        assert '00:00:00' in time_max_arg, \
            f"timeMaxが00:00:00ではない: {time_max_arg}"

    @patch('src.calendar_client.CALENDAR_IDS', ['primary'])
    @patch('src.calendar_client.datetime')
    def test_today_events_timezone_aware_api_params(self, mock_datetime):
        """
        APIパラメータがタイムゾーンawareであることを検証

        Codex指摘: ローカルナイーブに'Z'付与でUTC扱いになるバグ
        期待: isoformat()でローカルタイムゾーンのオフセットが保持される
              'Z'サフィックスではなく'+09:00'等のオフセット形式であること
        """
        mock_now = datetime(2026, 2, 5, 15, 30, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.combine = datetime.combine
        mock_datetime.min = datetime.min
        mock_datetime.max = datetime.max
        mock_datetime.fromisoformat = datetime.fromisoformat

        client = CalendarClient()
        client.service = Mock()

        mock_list = Mock()
        mock_list.execute.return_value = {'items': []}
        client.service.events.return_value.list.return_value = mock_list

        client.get_today_events()

        # API呼び出しパラメータを取得
        call_kwargs = client.service.events.return_value.list.call_args
        time_min_arg = call_kwargs.kwargs.get('timeMin') or call_kwargs[1].get('timeMin')
        time_max_arg = call_kwargs.kwargs.get('timeMax') or call_kwargs[1].get('timeMax')

        # ナイーブdatetime + 'Z' の形式ではないことを確認
        # 正しいISO 8601形式: オフセット付き（例: +09:00, +00:00）
        # 不正な形式: ナイーブローカル時刻 + 'Z'（例: 2026-02-05T00:00:00Z）
        assert not time_min_arg.endswith('Z'), \
            f"timeMinがナイーブ+Z形式で不正: {time_min_arg}（ローカル時刻にZを付けるとUTC扱いになる）"
        assert not time_max_arg.endswith('Z'), \
            f"timeMaxがナイーブ+Z形式で不正: {time_max_arg}（ローカル時刻にZを付けるとUTC扱いになる）"

        # タイムゾーンオフセットが含まれていることを確認（+HH:MM または -HH:MM）
        import re
        tz_pattern = r'[+-]\d{2}:\d{2}$'
        assert re.search(tz_pattern, time_min_arg), \
            f"timeMinにタイムゾーンオフセットがない: {time_min_arg}"
        assert re.search(tz_pattern, time_max_arg), \
            f"timeMaxにタイムゾーンオフセットがない: {time_max_arg}"


class TestIsAuthenticated:
    """認証状態チェックのテスト"""

    def test_is_authenticated_false_when_no_creds(self):
        """認証情報がない場合Falseを返す"""
        client = CalendarClient()
        assert client.is_authenticated is False

    def test_is_authenticated_false_when_no_service(self):
        """serviceがない場合Falseを返す"""
        client = CalendarClient()
        client.creds = MagicMock()
        client.creds.valid = True
        # service is None
        assert client.is_authenticated is False

    def test_is_authenticated_false_when_creds_invalid(self):
        """認証情報が無効な場合Falseを返す"""
        client = CalendarClient()
        client.creds = MagicMock()
        client.creds.valid = False
        client.service = MagicMock()
        assert client.is_authenticated is False

    def test_is_authenticated_true_when_valid(self):
        """認証情報が有効でserviceがある場合Trueを返す"""
        client = CalendarClient()
        client.creds = MagicMock()
        client.creds.valid = True
        client.service = MagicMock()
        assert client.is_authenticated is True


class TestGetCalendarList:
    """カレンダー一覧取得のテスト"""

    def test_get_calendar_list_returns_list(self):
        """カレンダー一覧がリストで返される"""
        client = CalendarClient()
        client.service = MagicMock()

        mock_response = {
            'items': [
                {
                    'id': 'primary',
                    'summary': 'メインカレンダー',
                    'backgroundColor': '#4285f4',
                    'selected': True
                },
                {
                    'id': 'work@group.calendar.google.com',
                    'summary': '仕事用',
                    'backgroundColor': '#ff6d01',
                    'selected': True
                }
            ]
        }
        client.service.calendarList.return_value.list.return_value.execute.return_value = mock_response

        result = client.get_calendar_list()

        assert isinstance(result, list)
        assert len(result) == 2

    def test_get_calendar_list_has_required_fields(self):
        """各カレンダーにid, summary, backgroundColor, selectedが含まれる"""
        client = CalendarClient()
        client.service = MagicMock()

        mock_response = {
            'items': [
                {
                    'id': 'primary',
                    'summary': 'メインカレンダー',
                    'backgroundColor': '#4285f4',
                    'selected': True
                }
            ]
        }
        client.service.calendarList.return_value.list.return_value.execute.return_value = mock_response

        result = client.get_calendar_list()

        assert len(result) == 1
        cal = result[0]
        assert cal['id'] == 'primary'
        assert cal['summary'] == 'メインカレンダー'
        assert cal['backgroundColor'] == '#4285f4'
        assert cal['selected'] is True

    def test_get_calendar_list_default_values(self):
        """オプションフィールドが欠けている場合、デフォルト値が使われる"""
        client = CalendarClient()
        client.service = MagicMock()

        mock_response = {
            'items': [
                {
                    'id': 'primary',
                    'summary': 'マイカレンダー',
                    # backgroundColor, selected が欠けている
                }
            ]
        }
        client.service.calendarList.return_value.list.return_value.execute.return_value = mock_response

        result = client.get_calendar_list()

        cal = result[0]
        assert cal['backgroundColor'] == '#4285f4'  # デフォルト色
        assert cal['selected'] is True  # デフォルトで選択

    def test_get_calendar_list_empty_when_no_service(self):
        """サービス未初期化時に空リストを返す"""
        client = CalendarClient()
        result = client.get_calendar_list()
        assert result == []

    def test_get_calendar_list_empty_on_api_error(self):
        """APIエラー時に空リストを返す"""
        from googleapiclient.errors import HttpError

        client = CalendarClient()
        client.service = MagicMock()

        mock_response = MagicMock()
        mock_response.status = 403
        mock_response.reason = 'Forbidden'
        client.service.calendarList.return_value.list.return_value.execute.side_effect = \
            HttpError(mock_response, b'Access denied')

        result = client.get_calendar_list()
        assert result == []

    def test_get_calendar_list_empty_items(self):
        """itemsが空の場合、空リストを返す"""
        client = CalendarClient()
        client.service = MagicMock()

        mock_response = {'items': []}
        client.service.calendarList.return_value.list.return_value.execute.return_value = mock_response

        result = client.get_calendar_list()
        assert result == []

    def test_get_calendar_list_skips_no_id(self):
        """idがないカレンダーは除外される"""
        client = CalendarClient()
        client.service = MagicMock()

        mock_response = {
            'items': [
                {'id': 'valid', 'summary': '有効'},
                {'summary': 'IDなし'},  # idが欠けている
            ]
        }
        client.service.calendarList.return_value.list.return_value.execute.return_value = mock_response

        result = client.get_calendar_list()
        assert len(result) == 1
        assert result[0]['id'] == 'valid'

    def test_get_calendar_list_missing_summary_uses_default(self):
        """summaryがないカレンダーにはデフォルト名が付く"""
        client = CalendarClient()
        client.service = MagicMock()

        mock_response = {
            'items': [
                {'id': 'no_name'},  # summaryが欠けている
            ]
        }
        client.service.calendarList.return_value.list.return_value.execute.return_value = mock_response

        result = client.get_calendar_list()
        assert len(result) == 1
        assert result[0]['summary'] == '（名称なし）'


class TestLogout:
    """ログアウト機能のテスト"""

    def test_logout_clears_creds(self):
        """ログアウト後にcredsがNoneになる"""
        client = CalendarClient()
        client.creds = MagicMock()
        client.service = MagicMock()

        client.logout()

        assert client.creds is None

    def test_logout_clears_service(self):
        """ログアウト後にserviceがNoneになる"""
        client = CalendarClient()
        client.creds = MagicMock()
        client.service = MagicMock()

        client.logout()

        assert client.service is None

    def test_logout_deletes_token_file(self, tmp_path):
        """ログアウト時にトークンファイルが削除される"""
        token_file = tmp_path / "token.json"
        token_file.write_text('{"token": "test"}')
        assert token_file.exists()

        client = CalendarClient()
        client.creds = MagicMock()
        client.service = MagicMock()

        with patch('src.calendar_client.TOKEN_PATH', token_file):
            client.logout()

        assert not token_file.exists()

    def test_logout_no_error_when_no_token_file(self, tmp_path):
        """トークンファイルが存在しない場合もエラーにならない"""
        token_file = tmp_path / "nonexistent_token.json"

        client = CalendarClient()
        client.creds = MagicMock()
        client.service = MagicMock()

        with patch('src.calendar_client.TOKEN_PATH', token_file):
            client.logout()  # 例外が発生しないことを確認

        assert client.creds is None
        assert client.service is None

    def test_logout_when_not_authenticated(self):
        """未認証状態でlogoutしてもエラーにならない"""
        client = CalendarClient()
        # creds=None, service=None の状態

        client.logout()  # 例外が発生しないことを確認

        assert client.creds is None
        assert client.service is None


class TestAccountsConfiguration:
    """複数アカウント設定の管理に関するテスト"""

    def test_load_accounts_config_returns_dict(self):
        """_load_accounts_config()がdict形式のアカウント設定を返す"""
        client = CalendarClient()

        # accounts.json が存在しない場合
        with patch('pathlib.Path.exists', return_value=False):
            config = client._load_accounts_config()

        assert isinstance(config, dict)
        assert 'accounts' in config

    def test_load_accounts_config_default_structure(self):
        """accounts.json が存在しない場合、デフォルトのアカウント設定を返す"""
        client = CalendarClient()

        with patch('pathlib.Path.exists', return_value=False):
            config = client._load_accounts_config()

        assert config['accounts'] == []

    def test_load_accounts_config_reads_json_file(self, tmp_path):
        """accounts.json ファイルが存在する場合、その内容を読み込む"""
        # テスト用のaccounts.jsonを作成
        accounts_file = tmp_path / "accounts.json"
        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user1@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "仕事用"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            config = client._load_accounts_config()

        assert len(config['accounts']) == 1
        assert config['accounts'][0]['id'] == "account_1"
        assert config['accounts'][0]['email'] == "user1@gmail.com"
        assert config['accounts'][0]['enabled'] is True

    def test_save_accounts_config_writes_json_file(self, tmp_path):
        """_save_accounts_config()がaccounts.jsonにアカウント設定を保存する"""
        accounts_file = tmp_path / "accounts.json"
        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user1@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "仕事用"
                }
            ]
        }

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            client._save_accounts_config(accounts_data)

        # ファイルが作成されたことを確認
        assert accounts_file.exists()

        # 内容を確認
        import json
        with open(accounts_file, 'r') as f:
            saved_data = json.load(f)

        assert len(saved_data['accounts']) == 1
        assert saved_data['accounts'][0]['id'] == "account_1"

    def test_load_enabled_accounts_only(self, tmp_path):
        """有効なアカウントのみをロードする"""
        accounts_file = tmp_path / "accounts.json"
        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user1@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "仕事用"
                },
                {
                    "id": "account_2",
                    "email": "user2@gmail.com",
                    "token_file": "token_account_2.json",
                    "enabled": False,  # 無効
                    "color": "#ea4335",
                    "display_name": "プライベート"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            # load_accounts() は有効なアカウントのみロードする
            # （実装後にこのテストを完成させる）
            config = client._load_accounts_config()

        # 設定ファイル自体には2つのアカウントが含まれる
        assert len(config['accounts']) == 2

        # 有効なアカウントは1つのみ
        enabled_accounts = [acc for acc in config['accounts'] if acc['enabled']]
        assert len(enabled_accounts) == 1
        assert enabled_accounts[0]['id'] == "account_1"

    @patch('src.calendar_client.InstalledAppFlow')
    @patch('src.calendar_client.build')
    def test_add_account_creates_new_account(self, mock_build, mock_flow_class, tmp_path):
        """add_account()で新しいアカウントを追加できる"""
        # テスト用のaccounts.jsonを作成
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        accounts_data = {"accounts": []}

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        # Mock OAuth2フロー
        mock_flow = MagicMock()
        mock_flow_class.from_client_secrets_file.return_value = mock_flow

        mock_creds = MagicMock()
        mock_creds.to_json.return_value = '{"token": "test_token"}'
        mock_creds.valid = True
        mock_flow.run_local_server.return_value = mock_creds

        # Mock service
        mock_service = MagicMock()
        mock_service.calendarList().list().execute.return_value = {
            'items': [{'id': 'user@gmail.com', 'summary': 'user@gmail.com', 'primary': True}]
        }
        mock_build.return_value = mock_service

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CREDENTIALS_PATH', tmp_path / 'credentials.json'), \
             patch('src.calendar_client.CONFIG_DIR', token_dir):

            # credentials.jsonをモック
            (tmp_path / 'credentials.json').write_text('{"installed": {}}')

            result = client.add_account(display_name="仕事用")

        # 結果を確認
        assert result is not None
        assert 'id' in result
        assert result['email'] == 'user@gmail.com'
        assert result['display_name'] == '仕事用'
        assert result['enabled'] is True

        # accounts.jsonが更新されたことを確認
        with open(accounts_file, 'r') as f:
            saved_config = json.load(f)

        assert len(saved_config['accounts']) == 1
        assert saved_config['accounts'][0]['email'] == 'user@gmail.com'
        assert saved_config['accounts'][0]['display_name'] == '仕事用'

    def test_add_account_generates_unique_id(self, tmp_path):
        """add_account()が一意のaccount_idを生成する"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        # 既存アカウント1件
        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user1@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "既存アカウント"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir):

            # _generate_account_id() をテスト
            account_id = client._generate_account_id()

        # 新しいIDが生成される
        assert account_id == "account_2"

    def test_add_account_assigns_default_color(self, tmp_path):
        """add_account()がデフォルトの色を割り当てる"""
        accounts_file = tmp_path / "accounts.json"
        accounts_data = {"accounts": []}

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            # デフォルト色のリストを確認
            color = client._get_next_default_color()

        # デフォルト色が返される（例: #4285f4, #ea4335, #fbbc04 など）
        assert color.startswith('#')
        assert len(color) == 7  # #RRGGBB形式

    def test_remove_account_deletes_account(self, tmp_path):
        """remove_account()でアカウントを削除できる"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        # テスト用のトークンファイル作成
        token_file = token_dir / "token_account_1.json"
        token_file.write_text('{"token": "test"}')

        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user1@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "テスト用"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir):

            result = client.remove_account("account_1")

        # 削除成功
        assert result is True

        # accounts.jsonから削除されたことを確認
        with open(accounts_file, 'r') as f:
            saved_config = json.load(f)

        assert len(saved_config['accounts']) == 0

        # トークンファイルが削除されたことを確認
        assert not token_file.exists()

    def test_remove_account_nonexistent_id(self, tmp_path):
        """remove_account()で存在しないaccount_idを指定した場合、Falseを返す"""
        accounts_file = tmp_path / "accounts.json"
        accounts_data = {"accounts": []}

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            result = client.remove_account("nonexistent_id")

        # 削除失敗
        assert result is False

    def test_remove_account_preserves_other_accounts(self, tmp_path):
        """remove_account()で1つのアカウントを削除しても、他のアカウントは残る"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        # テスト用のトークンファイル作成
        (token_dir / "token_account_1.json").write_text('{"token": "test1"}')
        (token_dir / "token_account_2.json").write_text('{"token": "test2"}')

        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user1@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "アカウント1"
                },
                {
                    "id": "account_2",
                    "email": "user2@gmail.com",
                    "token_file": "token_account_2.json",
                    "enabled": True,
                    "color": "#ea4335",
                    "display_name": "アカウント2"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir):

            result = client.remove_account("account_1")

        assert result is True

        # account_2が残っていることを確認
        with open(accounts_file, 'r') as f:
            saved_config = json.load(f)

        assert len(saved_config['accounts']) == 1
        assert saved_config['accounts'][0]['id'] == "account_2"

        # account_2のトークンファイルは残っている
        assert (token_dir / "token_account_2.json").exists()

    def test_update_account_color(self, tmp_path):
        """update_account_color()がアカウントの色を変更する"""
        accounts_file = tmp_path / "accounts.json"
        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "アカウント1"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            result = client.update_account_color("account_1", "#ff0000")

        assert result is True

        # 色が変更されていることを確認
        with open(accounts_file, 'r') as f:
            saved_config = json.load(f)

        assert saved_config['accounts'][0]['color'] == "#ff0000"

    def test_update_account_color_nonexistent_id(self, tmp_path):
        """update_account_color()が存在しないアカウントIDを拒否する"""
        accounts_file = tmp_path / "accounts.json"
        accounts_data = {"accounts": []}

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            result = client.update_account_color("nonexistent", "#ff0000")

        assert result is False

    def test_update_account_color_invalid_format(self, tmp_path):
        """update_account_color()が無効な色形式を拒否する"""
        accounts_file = tmp_path / "accounts.json"
        accounts_data = {
            "accounts": [{
                "id": "account_1",
                "email": "user@gmail.com",
                "token_file": "token_account_1.json",
                "enabled": True,
                "color": "#4285f4",
                "display_name": "アカウント1"
            }]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            # 無効な形式（名前指定）
            result1 = client.update_account_color("account_1", "red")
            assert result1 is False

            # 無効な形式（短縮形）
            result2 = client.update_account_color("account_1", "#fff")
            assert result2 is False

            # 無効な形式（空文字）
            result3 = client.update_account_color("account_1", "")
            assert result3 is False

            # 無効な形式（#なし）
            result4 = client.update_account_color("account_1", "4285f4")
            assert result4 is False

            # 元の色が変わっていないことを確認
            with open(accounts_file, 'r') as f:
                config = json.load(f)
            assert config['accounts'][0]['color'] == "#4285f4"

    def test_update_account_color_valid_format(self, tmp_path):
        """update_account_color()が有効な#RRGGBB形式を受け入れる"""
        accounts_file = tmp_path / "accounts.json"
        accounts_data = {
            "accounts": [{
                "id": "account_1",
                "email": "user@gmail.com",
                "token_file": "token_account_1.json",
                "enabled": True,
                "color": "#4285f4",
                "display_name": "アカウント1"
            }]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            # 小文字
            result1 = client.update_account_color("account_1", "#ff0000")
            assert result1 is True

            # 大文字
            result2 = client.update_account_color("account_1", "#00FF00")
            assert result2 is True

            # 混在
            result3 = client.update_account_color("account_1", "#aB12Cd")
            assert result3 is True

            # 最終的な色を確認
            with open(accounts_file, 'r') as f:
                config = json.load(f)
            assert config['accounts'][0]['color'] == "#aB12Cd"

    def test_update_account_color_missing_id_key(self, tmp_path):
        """update_account_color()がidキーのないアカウントレコードを安全に処理する"""
        accounts_file = tmp_path / "accounts.json"
        # idキーが欠けたアカウントレコード（破損データ）
        accounts_data = {
            "accounts": [{
                "email": "user@gmail.com",
                "token_file": "token_account_1.json",
                "enabled": True,
                "color": "#4285f4",
                "display_name": "アカウント1"
                # "id"キーが存在しない
            }]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file):
            # KeyErrorを発生させずにFalseを返すべき
            result = client.update_account_color("account_1", "#ff0000")

        assert result is False


class TestMultipleAccountsEvents:
    """複数アカウントからのイベント統合取得に関するテスト"""

    @patch('src.calendar_client.build')
    @patch('src.calendar_client.Credentials')
    def test_load_accounts_creates_services(self, mock_creds_class, mock_build, tmp_path):
        """load_accounts()が有効なアカウントのサービスを初期化する"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        # トークンファイル作成
        (token_dir / "token_account_1.json").write_text('{"token": "test1", "refresh_token": "refresh1"}')
        (token_dir / "token_account_2.json").write_text('{"token": "test2", "refresh_token": "refresh2"}')

        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user1@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "アカウント1"
                },
                {
                    "id": "account_2",
                    "email": "user2@gmail.com",
                    "token_file": "token_account_2.json",
                    "enabled": False,  # 無効
                    "color": "#ea4335",
                    "display_name": "アカウント2"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        # Mock credentials
        mock_creds1 = MagicMock()
        mock_creds1.valid = True
        mock_creds_class.from_authorized_user_file.return_value = mock_creds1

        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir):

            client.load_accounts()

        # 有効なアカウント（account_1）のみサービスが初期化される
        assert hasattr(client, 'accounts')
        assert len(client.accounts) == 1
        assert 'account_1' in client.accounts
        assert client.accounts['account_1']['email'] == 'user1@gmail.com'
        assert client.accounts['account_1']['color'] == '#4285f4'

    @patch('src.calendar_client.build')
    @patch('src.calendar_client.Credentials')
    def test_get_all_events_from_multiple_accounts(self, mock_creds_class, mock_build, tmp_path):
        """get_all_events()が複数アカウントからイベントを統合して取得する"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        # トークンファイル作成
        (token_dir / "token_account_1.json").write_text('{"token": "test1"}')
        (token_dir / "token_account_2.json").write_text('{"token": "test2"}')

        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "work@company.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "仕事用"
                },
                {
                    "id": "account_2",
                    "email": "private@gmail.com",
                    "token_file": "token_account_2.json",
                    "enabled": True,
                    "color": "#ea4335",
                    "display_name": "プライベート"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        # Mock credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds_class.from_authorized_user_file.return_value = mock_creds

        # Mock service - 異なるイベントを返す
        mock_service1 = MagicMock()
        mock_service2 = MagicMock()

        # account_1のイベント
        mock_service1.events().list().execute.return_value = {
            'items': [
                {
                    'id': 'event1',
                    'summary': '仕事ミーティング',
                    'start': {'dateTime': '2026-02-09T10:00:00+09:00'},
                    'end': {'dateTime': '2026-02-09T11:00:00+09:00'},
                }
            ]
        }

        # account_2のイベント
        mock_service2.events().list().execute.return_value = {
            'items': [
                {
                    'id': 'event2',
                    'summary': 'ランチ',
                    'start': {'dateTime': '2026-02-09T12:00:00+09:00'},
                    'end': {'dateTime': '2026-02-09T13:00:00+09:00'},
                }
            ]
        }

        # buildが呼ばれるたびに異なるserviceを返す
        mock_build.side_effect = [mock_service1, mock_service2]

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir), \
             patch('src.calendar_client.CALENDAR_IDS', ['primary']):

            client.load_accounts()
            events = client.get_all_events()

        # 2つのアカウントからイベントが統合されている
        assert len(events) == 2

        # イベントにアカウント情報が付与されている
        work_event = [e for e in events if e.summary == '仕事ミーティング'][0]
        assert work_event.account_id == 'account_1'
        assert work_event.account_color == '#4285f4'
        assert work_event.account_display_name == '仕事用'

        private_event = [e for e in events if e.summary == 'ランチ'][0]
        assert private_event.account_id == 'account_2'
        assert private_event.account_color == '#ea4335'
        assert private_event.account_display_name == 'プライベート'

        # 時系列でソートされている
        assert events[0].start_datetime < events[1].start_datetime

    @patch('src.calendar_client.build')
    @patch('src.calendar_client.Credentials')
    def test_load_accounts_refresh_token_chmod(self, mock_creds_class, mock_build, tmp_path):
        """load_accounts()でトークンリフレッシュ後にchmod 600が設定される"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        # トークンファイル作成（緩い権限で）
        token_file = token_dir / "token_account_1.json"
        token_file.write_text('{"token": "test1", "refresh_token": "refresh1"}')
        token_file.chmod(0o644)  # 意図的に緩い権限

        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user1@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "アカウント1"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        # Mock credentials - expired and requires refresh
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh1"

        # refresh()後にvalidになる
        def refresh_side_effect(request):
            mock_creds.valid = True

        mock_creds.refresh = MagicMock(side_effect=refresh_side_effect)
        mock_creds.to_json.return_value = '{"token": "refreshed", "refresh_token": "refresh1"}'

        mock_creds_class.from_authorized_user_file.return_value = mock_creds

        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir):

            client.load_accounts()

        # トークンファイルの権限が600になっていることを確認
        import stat
        file_stat = token_file.stat()
        file_mode = stat.filemode(file_stat.st_mode)
        # 600 = rw-------
        assert oct(file_stat.st_mode & 0o777) == '0o600', f"Expected 0o600, got {oct(file_stat.st_mode & 0o777)}"

    @patch('src.calendar_client.build')
    @patch('src.calendar_client.Credentials')
    def test_load_accounts_rejects_path_traversal(self, mock_creds_class, mock_build, tmp_path):
        """load_accounts()がパストラバーサル攻撃を拒否する"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        # 正常なトークンファイル
        (token_dir / "token_account_1.json").write_text('{"token": "test1"}')

        # 攻撃的なパスを含むaccounts.json
        accounts_data = {
            "accounts": [
                {
                    "id": "account_safe",
                    "email": "safe@gmail.com",
                    "token_file": "token_account_1.json",  # 正常
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "安全"
                },
                {
                    "id": "account_traversal",
                    "email": "attack1@gmail.com",
                    "token_file": "../../../etc/passwd",  # パストラバーサル
                    "enabled": True,
                    "color": "#ea4335",
                    "display_name": "攻撃1"
                },
                {
                    "id": "account_absolute",
                    "email": "attack2@gmail.com",
                    "token_file": "/etc/passwd",  # 絶対パス
                    "enabled": True,
                    "color": "#fbbc04",
                    "display_name": "攻撃2"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        # Mock credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds_class.from_authorized_user_file.return_value = mock_creds

        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir):

            client.load_accounts()

        # 安全なアカウントのみロードされる
        assert len(client.accounts) == 1
        assert 'account_safe' in client.accounts
        assert 'account_traversal' not in client.accounts
        assert 'account_absolute' not in client.accounts

    @patch('src.calendar_client.build')
    @patch('src.calendar_client.Credentials')
    def test_load_accounts_rejects_invalid_filename(self, mock_creds_class, mock_build, tmp_path):
        """load_accounts()が不正なファイル名を拒否する"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        # 正常なトークンファイル
        (token_dir / "token_account_1.json").write_text('{"token": "test1"}')

        accounts_data = {
            "accounts": [
                {
                    "id": "account_safe",
                    "email": "safe@gmail.com",
                    "token_file": "token_account_1.json",  # 正常（token_*.json形式）
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "安全"
                },
                {
                    "id": "account_invalid",
                    "email": "invalid@gmail.com",
                    "token_file": "malicious.json",  # token_*.json形式ではない
                    "enabled": True,
                    "color": "#ea4335",
                    "display_name": "不正"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        # Mock credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds_class.from_authorized_user_file.return_value = mock_creds

        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir):

            client.load_accounts()

        # 正しい形式のファイル名のアカウントのみロードされる
        assert len(client.accounts) == 1
        assert 'account_safe' in client.accounts
        assert 'account_invalid' not in client.accounts

    @patch('src.calendar_client.build')
    @patch('src.calendar_client.Credentials')
    def test_get_events_handles_pagination(self, mock_creds_class, mock_build, tmp_path):
        """_get_events_from_service()がページネーションを処理する"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        (token_dir / "token_account_1.json").write_text('{"token": "test1"}')

        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "アカウント1"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds_class.from_authorized_user_file.return_value = mock_creds

        # Mock service - ページネーションを返す
        mock_list_call = MagicMock()

        # 1ページ目
        page1 = {
            'items': [
                {
                    'id': 'event1',
                    'summary': 'イベント1',
                    'start': {'dateTime': '2026-02-09T10:00:00+09:00'},
                    'end': {'dateTime': '2026-02-09T11:00:00+09:00'},
                }
            ],
            'nextPageToken': 'token_page2'
        }

        # 2ページ目
        page2 = {
            'items': [
                {
                    'id': 'event2',
                    'summary': 'イベント2',
                    'start': {'dateTime': '2026-02-09T12:00:00+09:00'},
                    'end': {'dateTime': '2026-02-09T13:00:00+09:00'},
                }
            ],
            'nextPageToken': 'token_page3'
        }

        # 3ページ目（最終）
        page3 = {
            'items': [
                {
                    'id': 'event3',
                    'summary': 'イベント3',
                    'start': {'dateTime': '2026-02-09T14:00:00+09:00'},
                    'end': {'dateTime': '2026-02-09T15:00:00+09:00'},
                }
            ]
        }

        mock_list_call.execute.side_effect = [page1, page2, page3]

        mock_service = MagicMock()
        mock_service.events().list.return_value = mock_list_call
        mock_build.return_value = mock_service

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir), \
             patch('src.calendar_client.CALENDAR_IDS', ['primary']):

            client.load_accounts()
            events = client.get_all_events()

        # 全ページのイベントが取得されている
        assert len(events) == 3
        assert events[0].summary == 'イベント1'
        assert events[1].summary == 'イベント2'
        assert events[2].summary == 'イベント3'

    @patch('src.calendar_client.build')
    @patch('src.calendar_client.Credentials')
    def test_get_all_events_uses_local_timezone(self, mock_creds_class, mock_build, tmp_path):
        """get_all_events()がローカルタイムゾーンの日付境界を使用する"""
        accounts_file = tmp_path / "accounts.json"
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        (token_dir / "token_account_1.json").write_text('{"token": "test1"}')

        accounts_data = {
            "accounts": [
                {
                    "id": "account_1",
                    "email": "user@gmail.com",
                    "token_file": "token_account_1.json",
                    "enabled": True,
                    "color": "#4285f4",
                    "display_name": "アカウント1"
                }
            ]
        }

        import json
        with open(accounts_file, 'w') as f:
            json.dump(accounts_data, f)

        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds_class.from_authorized_user_file.return_value = mock_creds

        # Mock service
        mock_service = MagicMock()
        mock_service.events().list().execute.return_value = {'items': []}

        mock_build.return_value = mock_service

        client = CalendarClient()

        with patch('src.calendar_client.ACCOUNTS_CONFIG_PATH', accounts_file), \
             patch('src.calendar_client.CONFIG_DIR', token_dir), \
             patch('src.calendar_client.CALENDAR_IDS', ['primary']):

            client.load_accounts()

            # get_all_events()を呼び出し
            from datetime import datetime, timezone, timedelta

            # 今日の日付をローカルTZで計算
            today = datetime.now().date()
            local_tz = datetime.now(timezone.utc).astimezone().tzinfo
            expected_start = datetime.combine(today, datetime.min.time(), tzinfo=local_tz)
            expected_end = datetime.combine(today + timedelta(days=1), datetime.min.time(), tzinfo=local_tz)

            client.get_all_events(days=1)

        # list()が呼ばれた引数を確認
        call_args = mock_service.events().list.call_args
        assert call_args is not None

        # timeMinとtimeMaxがローカルTZの日付境界になっていることを確認
        time_min = call_args[1]['timeMin']
        time_max = call_args[1]['timeMax']

        # ISO形式の文字列をdatetimeに変換して比較
        from datetime import datetime as dt
        time_min_dt = dt.fromisoformat(time_min)
        time_max_dt = dt.fromisoformat(time_max)

        # ローカルTZの00:00であることを確認
        assert time_min_dt.hour == 0
        assert time_min_dt.minute == 0
        assert time_min_dt.second == 0

        assert time_max_dt.hour == 0
        assert time_max_dt.minute == 0
        assert time_max_dt.second == 0

        # 日付が今日と明日であることを確認
        assert time_min_dt.date() == today
        assert time_max_dt.date() == today + timedelta(days=1)
