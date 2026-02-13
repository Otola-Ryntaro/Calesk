"""
Google Calendar API連携モジュール
OAuth2認証とカレンダーイベントの取得を担当
"""
import os
from dataclasses import replace
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
        self.accounts = {}  # {account_id: {'service': service, 'email': str, 'color': str, 'display_name': str}}
        self._expired_accounts = {}  # {account_id: {'email': str, ...}} トークン期限切れアカウント
        self._local_tz = datetime.now(timezone.utc).astimezone().tzinfo

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
            # 時刻範囲の設定（今日の00:00から起算し、当日分の全イベントを含める）
            local_tz = self._local_tz
            today_start = datetime.combine(
                datetime.now().date(), datetime.min.time(), tzinfo=local_tz
            )
            time_min = today_start.isoformat()
            time_max = (today_start + timedelta(days=days)).isoformat()

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
            local_tz = self._local_tz
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
            # primary=Trueのカレンダーのidがメールアドレス
            email = None
            for cal in calendar_list.get('items', []):
                if cal.get('primary'):
                    email = cal.get('id', 'unknown@gmail.com')
                    break

            if not email:
                email = 'unknown@gmail.com'

            # 重複チェック: 同じメールアドレスが既に登録されていないか
            config = self._load_accounts_config()
            existing_emails = [a['email'] for a in config.get('accounts', [])]
            if email in existing_emails:
                logger.warning(f"アカウント {email} は既に登録されています")
                return None

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

    def update_account_color(self, account_id: str, color: str) -> bool:
        """
        アカウントの色を変更

        Args:
            account_id: アカウントID
            color: 新しい色（16進数カラーコード、例: "#ff0000"）

        Returns:
            bool: 変更成功時True、失敗時False
        """
        import re

        try:
            # 色形式のバリデーション（#RRGGBB形式）
            if not re.match(r'^#[0-9a-fA-F]{6}$', color):
                logger.warning(f"無効な色形式です: {color}（#RRGGBB形式である必要があります）")
                return False

            config = self._load_accounts_config()
            accounts = config.get('accounts', [])

            # 対象アカウントを検索
            target_account = None
            for account in accounts:
                # KeyError保護: account.get('id')を使用
                if account.get('id') == account_id:
                    target_account = account
                    break

            if not target_account:
                logger.warning(f"アカウントが見つかりません: {account_id}")
                return False

            # 色を変更
            target_account['color'] = color

            # 保存
            self._save_accounts_config(config)
            logger.info(f"アカウント {account_id} の色を変更しました: {color}")
            return True

        except Exception as e:
            logger.error(f"アカウント色変更エラー: {e}")
            return False

    def _validate_token_file_path(self, token_file: str) -> bool:
        """
        トークンファイルパスを検証（セキュリティ対策）

        Args:
            token_file: トークンファイル名

        Returns:
            bool: パスが安全な場合True、そうでない場合False
        """
        # 1. ファイル名がtoken_*.json形式であることを確認（ホワイトリスト）
        import re
        if not re.match(r'^token_[a-zA-Z0-9_]+\.json$', token_file):
            logger.warning(f"不正なトークンファイル名形式: {token_file}")
            return False

        # 2. パストラバーサル攻撃を検出
        if '..' in token_file or token_file.startswith('/'):
            logger.warning(f"パストラバーサル攻撃を検出: {token_file}")
            return False

        # 3. パスがCONFIG_DIR配下であることを確認
        try:
            token_path = (CONFIG_DIR / token_file).resolve()
            config_dir_resolved = CONFIG_DIR.resolve()

            # relative_to()で相対パスを計算できない場合、CONFIG_DIR配下でない
            token_path.relative_to(config_dir_resolved)
        except ValueError:
            logger.warning(f"トークンファイルがCONFIG_DIR配下にありません: {token_file}")
            return False

        return True

    def load_accounts(self):
        """
        accounts.jsonから有効なアカウントを読み込み、サービスインスタンスを初期化
        """
        config = self._load_accounts_config()
        self.accounts = {}
        self._expired_accounts = {}

        for account in config.get('accounts', []):
            if not account.get('enabled', False):
                continue

            account_id = account['id']
            token_file = account.get('token_file', '')

            if not token_file:
                logger.warning(f"アカウント {account_id} のトークンファイルが設定されていません")
                continue

            # トークンファイルパスの検証（セキュリティ対策）
            if not self._validate_token_file_path(token_file):
                logger.warning(f"アカウント {account_id} のトークンファイルパスが無効です: {token_file}")
                continue

            token_path = CONFIG_DIR / token_file

            if not token_path.exists():
                logger.warning(f"トークンファイルが見つかりません: {token_path}")
                continue

            try:
                # トークンを読み込み
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

                # トークンが無効な場合はスキップ
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                        # 更新したトークンを保存
                        with open(token_path, 'w') as token:
                            token.write(creds.to_json())
                        # トークンファイルの権限を600に設定
                        os.chmod(token_path, 0o600)
                    else:
                        logger.warning(f"アカウント {account_id} のトークンが無効です")
                        # 期限切れアカウントとして記録
                        self._expired_accounts[account_id] = {
                            'email': account.get('email', ''),
                            'color': account.get('color', '#4285f4'),
                            'display_name': account.get('display_name', account.get('email', ''))
                        }
                        continue

                # サービスを構築
                service = build('calendar', 'v3', credentials=creds)

                # アカウント情報を保存
                self.accounts[account_id] = {
                    'service': service,
                    'email': account.get('email', ''),
                    'color': account.get('color', '#4285f4'),
                    'display_name': account.get('display_name', account.get('email', ''))
                }

                logger.info(f"アカウントを読み込みました: {account['email']} (ID: {account_id})")

            except Exception as e:
                logger.error(f"アカウント {account_id} の読み込みエラー: {e}")
                continue

    def get_expired_account_ids(self) -> List[str]:
        """
        トークンが無効なアカウントIDのリストを返す

        Returns:
            List[str]: 期限切れアカウントIDのリスト
        """
        return list(self._expired_accounts.keys())

    def get_all_events(self, days: int = 1) -> List[CalendarEvent]:
        """
        すべての有効なアカウントからイベントを取得して統合

        Args:
            days: 取得する日数（デフォルト: 1 = 今日のみ）

        Returns:
            List[CalendarEvent]: 統合されたイベント情報のリスト（時系列ソート済み）
        """
        all_events = []

        for account_id, account_data in self.accounts.items():
            service = account_data['service']
            color = account_data['color']
            display_name = account_data['display_name']

            try:
                # このアカウントからイベントを取得
                events = self._get_events_from_service(
                    service,
                    account_id,
                    color,
                    display_name,
                    days
                )
                all_events.extend(events)

            except Exception as e:
                logger.error(f"アカウント {account_id} からのイベント取得エラー: {e}")
                continue

        # 時系列でソート
        all_events.sort(key=lambda e: e.start_datetime)

        logger.info(f"統合イベント取得: {len(all_events)}件（{len(self.accounts)}アカウント）")
        return all_events

    def _get_events_from_service(
        self,
        service,
        account_id: str,
        account_color: str,
        account_display_name: str,
        days: int = 1
    ) -> List[CalendarEvent]:
        """
        1つのサービスインスタンスからイベントを取得

        Args:
            service: Google Calendar APIサービスインスタンス
            account_id: アカウントID
            account_color: アカウント色
            account_display_name: アカウント表示名
            days: 取得する日数

        Returns:
            List[CalendarEvent]: イベント情報のリスト
        """
        all_events = []

        # 日時範囲を設定（ローカルタイムゾーン基準）
        today = datetime.now().date()
        local_tz = self._local_tz
        day_start = datetime.combine(today, datetime.min.time(), tzinfo=local_tz)
        day_end = datetime.combine(today + timedelta(days=days), datetime.min.time(), tzinfo=local_tz)

        for calendar_id in CALENDAR_IDS:
            try:
                # ページネーション処理
                page_token = None
                while True:
                    events_result = service.events().list(
                        calendarId=calendar_id,
                        timeMin=day_start.isoformat(),
                        timeMax=day_end.isoformat(),
                        singleEvents=True,
                        orderBy='startTime',
                        pageToken=page_token
                    ).execute()

                    for item in events_result.get('items', []):
                        # イベントをパース
                        event = self._parse_event(item, calendar_id)

                        if event:
                            # アカウント情報を付与（dataclassは不変なので新しいインスタンスを作成）
                            event = replace(
                                event,
                                account_id=account_id,
                                account_color=account_color,
                                account_display_name=account_display_name
                            )
                            all_events.append(event)

                    # 次のページがあるか確認
                    page_token = events_result.get('nextPageToken')
                    if not page_token:
                        break

            except HttpError as error:
                logger.error(f"カレンダー {calendar_id} のAPIエラー: {error}")
                continue
            except Exception as e:
                logger.error(f"カレンダー {calendar_id} のイベント取得エラー: {e}")
                continue

        return all_events
