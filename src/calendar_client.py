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

from .config import SCOPES, CREDENTIALS_PATH, TOKEN_PATH, CALENDAR_IDS

logger = logging.getLogger(__name__)


class CalendarClient:
    """Google Calendar APIクライアント"""

    def __init__(self):
        self.service = None
        self.creds = None

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

    def get_events(self, days: int = 7) -> List[Dict]:
        """
        指定された日数分のイベントを取得

        Args:
            days: 今日から何日後までのイベントを取得するか（デフォルト: 7日）

        Returns:
            List[Dict]: イベント情報のリスト
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
            all_events.sort(key=lambda x: x['start_datetime'])

            logger.info(f"合計 {len(all_events)}件のイベントを取得しました")
            return all_events

        except HttpError as error:
            logger.error(f"APIエラー: {error}")
            return []
        except Exception as e:
            logger.error(f"イベント取得エラー: {e}")
            return []

    def _parse_event(self, event: Dict, calendar_id: str) -> Optional[Dict]:
        """
        イベント情報を解析して必要な情報を抽出

        Args:
            event: Google Calendar APIから取得したイベント
            calendar_id: カレンダーID

        Returns:
            Dict: 整形されたイベント情報
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

            # イベント情報を構築
            event_info = {
                'id': event['id'],
                'summary': event.get('summary', '（タイトルなし）'),
                'start_datetime': start_dt,
                'end_datetime': end_dt,
                'is_all_day': is_all_day,
                'location': event.get('location', ''),
                'description': event.get('description', ''),
                'calendar_id': calendar_id,
                'color_id': event.get('colorId', '1'),  # デフォルトカラー
            }

            return event_info

        except Exception as e:
            logger.warning(f"イベント解析エラー ({event.get('summary', 'Unknown')}): {e}")
            return None

    def get_today_events(self) -> List[Dict]:
        """
        今日のイベントのみを取得

        Returns:
            List[Dict]: 今日のイベント情報のリスト
        """
        all_events = self.get_events(days=1)
        today = datetime.now().date()

        # 今日のイベントをフィルタリング
        today_events = [
            event for event in all_events
            if event['start_datetime'].date() == today
        ]

        return today_events

    def get_week_events(self) -> List[Dict]:
        """
        今週（7日間）のイベントを取得

        Returns:
            List[Dict]: 今週のイベント情報のリスト
        """
        return self.get_events(days=7)
