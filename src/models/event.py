"""
カレンダーイベントモデル

GUI/CLI共通で使用する統一イベントモデル。
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict


@dataclass(frozen=True)
class CalendarEvent:
    """
    カレンダーイベントの統一モデル

    Args:
        id: イベントID
        summary: イベントタイトル
        start_datetime: 開始日時
        end_datetime: 終了日時
        is_all_day: 終日イベントかどうか
        calendar_id: カレンダーID
        location: 場所（オプション）
        description: 説明（オプション）
        color_id: カラーID（オプション、デフォルト: "1"）
        account_id: アカウントID（オプション、デフォルト: "default"）
        account_color: アカウント色（オプション、デフォルト: "#4285f4"）
        account_display_name: アカウント表示名（オプション、デフォルト: ""）
    """
    id: str
    summary: str
    start_datetime: datetime
    end_datetime: datetime
    is_all_day: bool
    calendar_id: str
    location: str = ""
    description: str = ""
    color_id: str = "1"
    account_id: str = "default"
    account_color: str = "#4285f4"
    account_display_name: str = ""

    def to_dict(self) -> Dict:
        """
        Dict形式に変換

        Returns:
            Dict: イベント情報の辞書
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CalendarEvent':
        """
        Dict形式から変換

        Args:
            data: イベント情報の辞書

        Returns:
            CalendarEvent: イベントオブジェクト
        """
        return cls(
            id=data['id'],
            summary=data['summary'],
            start_datetime=data['start_datetime'],
            end_datetime=data['end_datetime'],
            is_all_day=data['is_all_day'],
            calendar_id=data['calendar_id'],
            location=data.get('location', ''),
            description=data.get('description', ''),
            color_id=data.get('color_id', '1'),
            account_id=data.get('account_id', 'default'),
            account_color=data.get('account_color', '#4285f4'),
            account_display_name=data.get('account_display_name', '')
        )

    def start_time_str(self) -> str:
        """
        開始時刻の文字列を取得（HH:MM形式）

        Returns:
            str: 開始時刻文字列（例: "14:30"）
        """
        return self.start_datetime.strftime('%H:%M')

    def end_time_str(self) -> str:
        """
        終了時刻の文字列を取得（HH:MM形式）

        Returns:
            str: 終了時刻文字列（例: "15:45"）
        """
        return self.end_datetime.strftime('%H:%M')

    def date_str(self) -> str:
        """
        日付の文字列を取得（YYYY-MM-DD形式）

        Returns:
            str: 日付文字列（例: "2026-02-05"）
        """
        return self.start_datetime.strftime('%Y-%m-%d')
