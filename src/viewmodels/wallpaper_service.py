"""
WallpaperService

ViewModelとcore/を橋渡しするService層。
壁紙の生成と設定を担当します。
"""

from pathlib import Path
from typing import List, Dict, Optional
import logging

from ..calendar_client import CalendarClient
from ..image_generator import ImageGenerator
from ..wallpaper_setter import WallpaperSetter
from .. import themes

logger = logging.getLogger(__name__)


class WallpaperService:
    """
    壁紙生成・設定サービス

    ImageGeneratorとWallpaperSetterを使用して、
    壁紙の生成と設定を行います。
    """

    def __init__(self):
        """WallpaperServiceを初期化"""
        self.calendar_client = CalendarClient()
        self.image_generator = ImageGenerator()
        self.wallpaper_setter = WallpaperSetter()
        logger.info("WallpaperServiceを初期化しました")

    def generate_wallpaper(
        self,
        theme_name: str
    ) -> Path:
        """
        壁紙画像を生成

        Args:
            theme_name: テーマ名（例: "simple", "modern"）

        Returns:
            Path: 生成された壁紙画像のパス

        Raises:
            Exception: 認証失敗またはイベント取得失敗時
        """
        try:
            logger.info(f"壁紙生成を開始: theme={theme_name}")

            # Google Calendar認証
            if not self.calendar_client.authenticate():
                raise Exception("Google Calendar API認証に失敗しました")

            # イベント取得
            today_events = self.calendar_client.get_today_events()
            week_events = self.calendar_client.get_week_events()
            logger.info(f"今日の予定: {len(today_events)}件、今週の予定: {len(week_events)}件")

            # テーマの設定
            self.image_generator.set_theme(theme_name)

            # 壁紙生成
            image_path = self.image_generator.generate_wallpaper(today_events, week_events)

            if not image_path:
                raise Exception("壁紙画像の生成に失敗しました")

            logger.info(f"壁紙生成完了: {image_path}")
            return image_path

        except Exception as e:
            logger.error(f"壁紙生成エラー: {e}")
            raise

    def set_wallpaper(self, image_path: Path) -> bool:
        """
        壁紙を設定

        Args:
            image_path: 壁紙画像のパス

        Returns:
            bool: 設定成功でTrue、失敗でFalse
        """
        try:
            logger.info(f"壁紙設定を開始: {image_path}")
            result = self.wallpaper_setter.set_wallpaper(image_path)

            if result:
                logger.info("壁紙設定完了")
            else:
                logger.error("壁紙設定失敗")

            return result

        except Exception as e:
            logger.error(f"壁紙設定エラー: {e}")
            return False

    def generate_and_set_wallpaper(
        self,
        theme_name: str
    ) -> bool:
        """
        壁紙を生成して設定

        Args:
            theme_name: テーマ名

        Returns:
            bool: 生成と設定が成功でTrue、失敗でFalse
        """
        try:
            # 壁紙生成
            image_path = self.generate_wallpaper(theme_name)

            # 壁紙設定
            result = self.set_wallpaper(image_path)

            return result

        except Exception as e:
            logger.error(f"壁紙生成・設定エラー: {e}")
            return False

    def set_background_image(self, path: Path):
        """
        カスタム背景画像パスを設定

        Args:
            path: 背景画像のパス
        """
        self.image_generator.set_background_image(path)
        logger.info(f"背景画像を設定しました: {path}")

    def reset_background_image(self):
        """背景画像をデフォルトに戻す"""
        self.image_generator.reset_background_image()
        logger.info("背景画像をデフォルトに戻しました")

    def get_available_themes(self) -> List[str]:
        """
        利用可能なテーマ一覧を取得

        Returns:
            List[str]: テーマ名のリスト
        """
        return list(themes.THEMES.keys())
