"""
Google Calendar API連携モジュール
OAuth2認証とカレンダーイベントの取得を担当
"""
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config import SCOPES, CREDENTIALS_PATH, TOKEN_PATH, CALENDAR_IDS, ACCOUNTS_CONFIG_PATH, CONFIG_DIR
from .models.event import CalendarEvent

logger = logging.getLogger(__name__)


class CalendarClient:
    """Google Calendar APIクライアント"""

    def __init__(self):
        self.service = None
        self.creds = None

    @property
    def is_authenticated(self) -> bool:
        """認証済みかどうかを返す"""
        return (
            self.creds is not None
            and self.creds.valid
            and self.service is not None
        )

    def authenticate(self) -> bool:
        """
        Google Calendar APIの認証を実行

        Returns:
            bool: 認証成功でTrue、失敗でFalse
        """
        try:
            # 既存のトークンをロード（JSONベース）
            if TOKEN_PATH.exists():
                self.creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

            # トークンが無効な場合はリフレッシュまたは再認証
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("トークンをリフレッシュしています...")
                    self.creds.refresh(Request())
                else:
                    logger.info("新規認証を開始します...")
                    if not CREDENTIALS_PATH.exists():
                        logger.error(f"認証情報ファイルが見つかりません: {CREDENTIALS_PATH}")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(CREDENTIALS_PATH), SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)

                # トークンを保存（JSONベース）
                with open(TOKEN_PATH, 'w') as token:
                    token.write(self.creds.to_json())

                # セキュリティ: ファイルパーミッションを所有者のみ読み書き可能に制限
                os.chmod(TOKEN_PATH, 0o600)
                logger.info("認証情報を保存しました")

            # Calendar APIサービスを構築
            self.service = build('calendar', 'v3', credentials=self.creds)
            logger.info("Google Calendar APIに接続しました")
            return True

        except Exception as e:
            logger.error(f"認証エラー: {e}")
            return False

    def get_calendar_list(self) -> List[Dict]:
        """
        利用可能なカレンダー一覧を取得

        Returns:
            List[Dict]: カレンダー情報のリスト（id, summary, backgroundColor, selected）
        """
        if not self.service:
            logger.error("APIサービスが初期化されていません。先にauthenticate()を呼び出してください")
            return []

        try:
            result = self.service.calendarList().list().execute()
            return [{
                'id': cal.get('id', ''),
                'summary': cal.get('summary', '（名称なし）'),
                'backgroundColor': cal.get('backgroundColor', '#4285f4'),
                'selected': cal.get('selected', True)
            } for cal in result.get('items', []) if cal.get('id')]

        except HttpError as error:
            logger.error(f"カレンダー一覧取得APIエラー: {error}")
            return []
        except Exception as e:
            logger.error(f"カレンダー一覧取得エラー: {e}")
            return []

    def logout(self):
        """ログアウト（認証情報とトークンファイルを削除）"""
        self.creds = None
        self.service = None

        try:
            if TOKEN_PATH.exists():
                TOKEN_PATH.unlink()
                logger.info("トークンファイルを削除しました")
        except Exception as e:
            logger.warning(f"トークンファイル削除エラー: {e}")

        logger.info("ログアウトしました")

    def get_events(self, days: int = 7) -> List[CalendarEvent]:
        """
        指定された日数分のイベントを取得

        Args:
            days: 今日から何日後までのイベントを取得するか（デフォルト: 7日）

        Returns:
            List[CalendarEvent]: イベント情報のリスト
        """
        if not self.service:
            logger.error("APIサービスが初期化されていません。先にauthenticate()を呼び出してください")
            return []

        try:
            # 時刻範囲の設定
            now = datetime.now(timezone.utc)
            time_min = now.isoformat()  # タイムゾーン情報が自動的に付加される
            time_max = (now + timedelta(days=days)).isoformat()

            all_events = []

            # 複数のカレンダーからイベントを取得
            for calendar_id in CALENDAR_IDS:
                logger.info(f"カレンダー '{calendar_id}' からイベントを取得中...")

                events_result = self.service.events().list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,  # 繰り返しイベントを展開
                    orderBy='startTime'
                ).execute()

                events = events_result.get('items', [])

                # イベント情報を整形
                for event in events:
                    event_info = self._parse_event(event, calendar_id)
                    if event_info:
                        all_events.append(event_info)

                logger.info(f"  → {len(events)}件のイベントを取得")

            # 開始時刻でソート
            all_events.sort(key=lambda x: x.start_datetime)

            logger.info(f"合計 {len(all_events)}件のイベントを取得しました")
            return all_events

        except HttpError as error:
            logger.error(f"APIエラー: {error}")
            return []
        except Exception as e:
            logger.error(f"イベント取得エラー: {e}")
            return []

    def _parse_event(self, event: Dict, calendar_id: str) -> Optional[CalendarEvent]:
        """
        イベント情報を解析して必要な情報を抽出

        Args:
            event: Google Calendar APIから取得したイベント
            calendar_id: カレンダーID

        Returns:
            CalendarEvent: 整形されたイベント情報
        """
        try:
            # 開始時刻の取得
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # 終日イベントの判定
            is_all_day = 'date' in event['start']

            # datetime オブジェクトに変換
            if is_all_day:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
            else:
                # タイムゾーン情報を含む場合は現地時間に変換
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                # 現地時間に変換してタイムゾーン情報を削除
                start_dt = start_dt.astimezone().replace(tzinfo=None)
                end_dt = end_dt.astimezone().replace(tzinfo=None)

            # CalendarEventオブジェクトを構築
            return CalendarEvent(
                id=event['id'],
                summary=event.get('summary', '（タイトルなし）'),
                start_datetime=start_dt,
                end_datetime=end_dt,
                is_all_day=is_all_day,
                location=event.get('location', ''),
                description=event.get('description', ''),
                calendar_id=calendar_id,
                color_id=event.get('colorId', '1')  # デフォルトカラー
            )

        except Exception as e:
            logger.warning(f"イベント解析エラー ({event.get('summary', 'Unknown')}): {e}")
            return None

    def get_today_events(self) -> List[CalendarEvent]:
        """
        今日のイベントのみを取得（当日全件: 00:00~翌日00:00）

        既に開始済みのイベントや終日イベントも含め、
        当日に属する全てのイベントを返す。

        Returns:
            List[CalendarEvent]: 今日のイベント情報のリスト
        """
        if not self.service:
            logger.error("APIサービスが初期化されていません。先にauthenticate()を呼び出してください")
            return []

        try:
            # 当日の時刻範囲: 今日の00:00:00 ~ 翌日の00:00:00（ローカルタイムゾーンaware）
            today = datetime.now().date()
            local_tz = datetime.now(timezone.utc).astimezone().tzinfo
            day_start = datetime.combine(today, datetime.min.time(), tzinfo=local_tz)
            day_end = datetime.combine(today + timedelta(days=1), datetime.min.time(), tzinfo=local_tz)

            # ISO 8601形式に変換（タイムゾーンオフセット付き）
            time_min = day_start.isoformat()
            time_max = day_end.isoformat()

            all_events = []

            for calendar_id in CALENDAR_IDS:
                logger.info(f"カレンダー '{calendar_id}' から今日のイベントを取得中...")

                events_result = self.service.events().list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()

                logger.debug(f"取得したイベント数: {len(events_result.get('items', []))}")

                events = events_result.get('items', [])

                for event in events:
                    event_info = self._parse_event(event, calendar_id)
                    if event_info:
                        all_events.append(event_info)
                        if event_info.is_all_day:
                            logger.debug(f"終日イベント: {event_info.summary}, 開始: {event_info.start_datetime}")

                logger.info(f"  → {len(events)}件のイベントを取得")

            # 開始時刻でソート
            all_events.sort(key=lambda x: x.start_datetime)

            # 今日のイベントのみフィルタリング（APIが範囲外を返す可能性への防御）
            # 重なり判定: イベントが当日の時間帯と重なるかどうか
            # - 前日開始・当日継続イベントも含める
            day_start_naive = day_start.replace(tzinfo=None)
            day_end_naive = day_end.replace(tzinfo=None)
            today_events = [
                event for event in all_events
                if event.start_datetime < day_end_naive and event.end_datetime > day_start_naive
            ]

            logger.info(f"今日のイベント: {len(today_events)}件")
            return today_events

        except HttpError as error:
            logger.error(f"APIエラー: {error}")
            return []
        except Exception as e:
            logger.error(f"今日のイベント取得エラー: {e}")
            return []

    def get_week_events(self) -> List[CalendarEvent]:
        """
        今週（7日間）のイベントを取得

        Returns:
            List[CalendarEvent]: 今週のイベント情報のリスト
        """
        return self.get_events(days=7)

    def _load_accounts_config(self) -> Dict:
        """
        accounts.json からアカウント設定を読み込む

        Returns:
            Dict: アカウント設定（{"accounts": [...]}}）
        """
        import json

        # ファイルが存在しない場合はデフォルト設定を返す
        if not ACCOUNTS_CONFIG_PATH.exists():
            return {"accounts": []}

        try:
            with open(ACCOUNTS_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"アカウント設定の読み込みエラー: {e}")
            return {"accounts": []}

    def _save_accounts_config(self, config: Dict):
        """
        accounts.json にアカウント設定を保存

        Args:
            config: アカウント設定（{"accounts": [...]}}）
        """
        import json

        # ディレクトリが存在しない場合は作成
        ACCOUNTS_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(ACCOUNTS_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"アカウント設定を保存しました: {ACCOUNTS_CONFIG_PATH}")
        except Exception as e:
            logger.error(f"アカウント設定の保存エラー: {e}")

    def _generate_account_id(self) -> str:
        """
        一意のaccount_idを生成

        Returns:
            str: 一意のaccount_id（例: "account_1", "account_2"）
        """
        config = self._load_accounts_config()
        existing_ids = [acc['id'] for acc in config.get('accounts', [])]

        # account_1, account_2, ... の形式で採番
        counter = 1
        while f"account_{counter}" in existing_ids:
            counter += 1

        return f"account_{counter}"

    def _get_next_default_color(self) -> str:
        """
        次のデフォルト色を取得

        Returns:
            str: デフォルト色（例: "#4285f4"）
        """
        # Google Material Design カラーパレット
        default_colors = [
            "#4285f4",  # Blue
            "#ea4335",  # Red
            "#fbbc04",  # Yellow
            "#34a853",  # Green
            "#ff6d01",  # Orange
            "#46bdc6",  # Cyan
            "#7baaf7",  # Light Blue
            "#f07b72",  # Light Red
        ]

        config = self._load_accounts_config()
        used_colors = [acc.get('color', '') for acc in config.get('accounts', [])]

        # 未使用の色を返す
        for color in default_colors:
            if color not in used_colors:
                return color

        # 全て使用済みの場合は最初の色を返す
        return default_colors[0]

    def add_account(self, display_name: str = "") -> Optional[Dict]:
        """
        新しいGoogleアカウントを追加

        Args:
            display_name: アカウントの表示名（オプション）

        Returns:
            Dict: 追加されたアカウント情報、失敗時はNone
        """
        try:
            # 1. OAuth2フローを実行
            if not CREDENTIALS_PATH.exists():
                logger.error(f"認証情報ファイルが見つかりません: {CREDENTIALS_PATH}")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)

            # 2. サービスを構築してメールアドレスを取得
            service = build('calendar', 'v3', credentials=creds)
            calendar_list = service.calendarList().list().execute()

            # プライマリカレンダーからメールアドレスを取得
            email = None
            for cal in calendar_list.get('items', []):
                if cal.get('id') == 'primary':
                    email = cal.get('summary', 'unknown@gmail.com')
                    break

            if not email:
                email = 'unknown@gmail.com'

            # 3. 一意のaccount_idを生成
            account_id = self._generate_account_id()

            # 4. トークンファイル名を決定
            token_filename = f"token_{account_id}.json"
            token_path = CONFIG_DIR / token_filename

            # ディレクトリ作成
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            # トークンを保存
            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())

            # セキュリティ: パーミッション制限
            os.chmod(token_path, 0o600)

            # 5. デフォルト色を割り当て
            color = self._get_next_default_color()

            # 6. アカウント情報を作成
            account_info = {
                'id': account_id,
                'email': email,
                'token_file': token_filename,
                'enabled': True,
                'color': color,
                'display_name': display_name or email
            }

            # 7. accounts.jsonに追加
            config = self._load_accounts_config()
            config['accounts'].append(account_info)
            self._save_accounts_config(config)

            logger.info(f"新しいアカウントを追加しました: {email} (ID: {account_id})")
            return account_info

        except Exception as e:
            logger.error(f"アカウント追加エラー: {e}")
            return None

    def remove_account(self, account_id: str) -> bool:
        """
        アカウントを削除

        Args:
            account_id: 削除するアカウントのID

        Returns:
            bool: 削除成功でTrue、失敗でFalse
        """
        try:
            # 1. accounts.jsonからアカウント情報を取得
            config = self._load_accounts_config()
            accounts = config.get('accounts', [])

            # 削除対象のアカウントを検索
            target_account = None
            for account in accounts:
                if account['id'] == account_id:
                    target_account = account
                    break

            if not target_account:
                logger.warning(f"アカウントが見つかりません: {account_id}")
                return False

            # 2. トークンファイルを削除
            token_filename = target_account.get('token_file', '')
            if token_filename:
                token_path = CONFIG_DIR / token_filename
                if token_path.exists():
                    token_path.unlink()
                    logger.info(f"トークンファイルを削除しました: {token_filename}")

            # 3. accounts.jsonから削除
            config['accounts'] = [acc for acc in accounts if acc['id'] != account_id]
            self._save_accounts_config(config)

            logger.info(f"アカウントを削除しました: {account_id}")
            return True

        except Exception as e:
            logger.error(f"アカウント削除エラー: {e}")
            return False
