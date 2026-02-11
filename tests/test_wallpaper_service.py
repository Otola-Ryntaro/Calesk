"""
WallpaperServiceのテスト

ViewModelとcore/を橋渡しするWallpaperServiceをテストします。
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestWallpaperService:
    """WallpaperServiceの基本機能をテストする"""

    def test_wallpaper_service_exists(self):
        """WallpaperServiceクラスが存在することを確認"""
        from src.viewmodels.wallpaper_service import WallpaperService

        assert WallpaperService is not None

    def test_wallpaper_service_initialization(self):
        """WallpaperServiceが正しく初期化されることを確認"""
        from src.viewmodels.wallpaper_service import WallpaperService

        service = WallpaperService()
        assert service is not None

    @patch('src.viewmodels.wallpaper_service.CalendarClient')
    @patch('src.viewmodels.wallpaper_service.ImageGenerator')
    def test_generate_wallpaper(self, mock_image_generator, mock_calendar_client):
        """壁紙生成が正しく動作することを確認（API1回呼び出し）"""
        from datetime import datetime, timedelta
        from src.viewmodels.wallpaper_service import WallpaperService

        # 今日と明日のイベントをMockオブジェクトで作成
        today = datetime.now().date()
        today_event = Mock()
        today_event.start_datetime = datetime.combine(today, datetime.min.time().replace(hour=10))
        today_event.end_datetime = datetime.combine(today, datetime.min.time().replace(hour=11))

        week_event = Mock()
        week_event.start_datetime = datetime.combine(today + timedelta(days=2), datetime.min.time().replace(hour=14))
        week_event.end_datetime = datetime.combine(today + timedelta(days=2), datetime.min.time().replace(hour=15))

        mock_client = Mock()
        mock_client.authenticate.return_value = True
        mock_client.get_week_events.return_value = [today_event, week_event]
        mock_calendar_client.return_value = mock_client

        # モックの設定（ImageGenerator）
        mock_generator = Mock()
        mock_generator.generate_wallpaper.return_value = Path("/tmp/test_wallpaper.png")
        mock_image_generator.return_value = mock_generator

        service = WallpaperService()
        result_path = service.generate_wallpaper(theme_name="simple")

        # 検証
        assert result_path == Path("/tmp/test_wallpaper.png")
        mock_client.authenticate.assert_called_once()
        mock_client.get_week_events.assert_called_once()
        # get_today_eventsは呼ばれない（API統合済み）
        mock_client.get_today_events.assert_not_called()
        # generate_wallpaperの引数: today_eventsは今日分のみ、week_eventsは全件
        call_args = mock_generator.generate_wallpaper.call_args
        assert call_args[0][0] == [today_event]  # today_events
        assert call_args[0][1] == [today_event, week_event]  # week_events

    @patch('src.viewmodels.wallpaper_service.WallpaperSetter')
    def test_set_wallpaper(self, mock_wallpaper_setter):
        """壁紙設定が正しく動作することを確認"""
        from src.viewmodels.wallpaper_service import WallpaperService

        # モックの設定
        mock_setter = Mock()
        mock_setter.set_wallpaper.return_value = True
        mock_wallpaper_setter.return_value = mock_setter

        service = WallpaperService()
        test_path = Path("/tmp/test_wallpaper.png")
        result = service.set_wallpaper(test_path)

        # 検証
        assert result is True
        mock_setter.set_wallpaper.assert_called_once_with(test_path)

    @patch('src.viewmodels.wallpaper_service.CalendarClient')
    @patch('src.viewmodels.wallpaper_service.WallpaperSetter')
    @patch('src.viewmodels.wallpaper_service.ImageGenerator')
    def test_generate_and_set_wallpaper_success(self, mock_image_generator, mock_wallpaper_setter, mock_calendar_client):
        """壁紙生成と設定が一度に実行されることを確認（成功ケース）"""
        from src.viewmodels.wallpaper_service import WallpaperService

        # モックの設定（CalendarClient）
        mock_client = Mock()
        mock_client.authenticate.return_value = True
        mock_client.get_today_events.return_value = []
        mock_client.get_week_events.return_value = []
        mock_calendar_client.return_value = mock_client

        # モックの設定（ImageGenerator）
        mock_generator = Mock()
        mock_generator.generate_wallpaper.return_value = Path("/tmp/test_wallpaper.png")
        mock_image_generator.return_value = mock_generator

        # モックの設定（WallpaperSetter）
        mock_setter = Mock()
        mock_setter.set_wallpaper.return_value = True
        mock_wallpaper_setter.return_value = mock_setter

        service = WallpaperService()
        result = service.generate_and_set_wallpaper(theme_name="simple")

        # 検証
        assert result is True
        mock_generator.generate_wallpaper.assert_called_once()
        mock_setter.set_wallpaper.assert_called_once_with(Path("/tmp/test_wallpaper.png"))

    @patch('src.viewmodels.wallpaper_service.CalendarClient')
    @patch('src.viewmodels.wallpaper_service.WallpaperSetter')
    @patch('src.viewmodels.wallpaper_service.ImageGenerator')
    def test_generate_and_set_wallpaper_failure(self, mock_image_generator, mock_wallpaper_setter, mock_calendar_client):
        """壁紙設定が失敗した場合の動作を確認"""
        from src.viewmodels.wallpaper_service import WallpaperService

        # モックの設定（CalendarClient）
        mock_client = Mock()
        mock_client.authenticate.return_value = True
        mock_client.get_today_events.return_value = []
        mock_client.get_week_events.return_value = []
        mock_calendar_client.return_value = mock_client

        # モックの設定（ImageGenerator）
        mock_generator = Mock()
        mock_generator.generate_wallpaper.return_value = Path("/tmp/test_wallpaper.png")
        mock_image_generator.return_value = mock_generator

        # モックの設定（WallpaperSetter）
        mock_setter = Mock()
        mock_setter.set_wallpaper.return_value = False  # 失敗
        mock_wallpaper_setter.return_value = mock_setter

        service = WallpaperService()
        result = service.generate_and_set_wallpaper(theme_name="simple")

        # 検証
        assert result is False
        mock_generator.generate_wallpaper.assert_called_once()
        mock_setter.set_wallpaper.assert_called_once()

    @patch('src.viewmodels.wallpaper_service.themes')
    def test_get_available_themes(self, mock_themes):
        """利用可能なテーマ一覧を取得できることを確認"""
        from src.viewmodels.wallpaper_service import WallpaperService

        # モックの設定
        mock_themes.THEMES = {
            "simple": Mock(),
            "modern": Mock(),
            "pastel": Mock(),
            "dark": Mock(),
            "vibrant": Mock()
        }

        service = WallpaperService()
        themes_list = service.get_available_themes()

        # 検証
        assert len(themes_list) == 5
        assert "simple" in themes_list
        assert "modern" in themes_list
        assert "pastel" in themes_list
        assert "dark" in themes_list
        assert "vibrant" in themes_list

    @patch('src.viewmodels.wallpaper_service.CalendarClient')
    @patch('src.viewmodels.wallpaper_service.ImageGenerator')
    def test_generate_wallpaper_authentication_failure(self, mock_image_generator, mock_calendar_client):
        """CalendarClient認証失敗時の動作を確認"""
        from src.viewmodels.wallpaper_service import WallpaperService

        # モックの設定（CalendarClient認証失敗）
        mock_client = Mock()
        mock_client.authenticate.return_value = False
        mock_calendar_client.return_value = mock_client

        # モックの設定（ImageGenerator - 呼ばれないはず）
        mock_generator = Mock()
        mock_image_generator.return_value = mock_generator

        service = WallpaperService()

        # 認証失敗時は例外が発生するはず
        with pytest.raises(Exception):
            service.generate_wallpaper(theme_name="simple")

        # CalendarClientは呼ばれるが、ImageGeneratorは呼ばれない
        mock_client.authenticate.assert_called_once()
        mock_generator.generate_wallpaper.assert_not_called()

    @patch('src.viewmodels.wallpaper_service.CalendarClient')
    @patch('src.viewmodels.wallpaper_service.ImageGenerator')
    def test_generate_wallpaper_with_events(self, mock_image_generator, mock_calendar_client):
        """複数イベントで壁紙生成が動作することを確認（API1回呼び出し）"""
        from datetime import datetime, timedelta
        from src.viewmodels.wallpaper_service import WallpaperService

        today = datetime.now().date()

        # 今日のイベント2件
        event_morning = Mock(summary="朝のミーティング")
        event_morning.start_datetime = datetime.combine(today, datetime.min.time().replace(hour=9))
        event_morning.end_datetime = datetime.combine(today, datetime.min.time().replace(hour=10))

        event_lunch = Mock(summary="昼食")
        event_lunch.start_datetime = datetime.combine(today, datetime.min.time().replace(hour=12))
        event_lunch.end_datetime = datetime.combine(today, datetime.min.time().replace(hour=13))

        # 週のイベント（今日以外）
        event_tue = Mock(summary="火曜プレゼン")
        event_tue.start_datetime = datetime.combine(today + timedelta(days=1), datetime.min.time().replace(hour=14))
        event_tue.end_datetime = datetime.combine(today + timedelta(days=1), datetime.min.time().replace(hour=15))

        event_wed = Mock(summary="水曜レビュー")
        event_wed.start_datetime = datetime.combine(today + timedelta(days=2), datetime.min.time().replace(hour=15))
        event_wed.end_datetime = datetime.combine(today + timedelta(days=2), datetime.min.time().replace(hour=16))

        all_week_events = [event_morning, event_lunch, event_tue, event_wed]

        mock_client = Mock()
        mock_client.authenticate.return_value = True
        mock_client.get_week_events.return_value = all_week_events
        mock_calendar_client.return_value = mock_client

        # モックの設定（ImageGenerator）
        mock_generator = Mock()
        mock_generator.generate_wallpaper.return_value = Path("/tmp/test_wallpaper.png")
        mock_image_generator.return_value = mock_generator

        service = WallpaperService()
        result_path = service.generate_wallpaper(theme_name="modern")

        # 検証
        assert result_path == Path("/tmp/test_wallpaper.png")
        call_args = mock_generator.generate_wallpaper.call_args
        assert call_args[0][0] == [event_morning, event_lunch]  # today_events
        assert call_args[0][1] == all_week_events  # week_events
