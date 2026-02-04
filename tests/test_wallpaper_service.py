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

    @patch('src.viewmodels.wallpaper_service.ImageGenerator')
    def test_generate_wallpaper(self, mock_image_generator):
        """壁紙生成が正しく動作することを確認"""
        from src.viewmodels.wallpaper_service import WallpaperService

        # モックの設定
        mock_generator = Mock()
        mock_generator.generate.return_value = Path("/tmp/test_wallpaper.png")
        mock_image_generator.return_value = mock_generator

        service = WallpaperService()
        result_path = service.generate_wallpaper(theme_name="simple", events=[])

        # 検証
        assert result_path == Path("/tmp/test_wallpaper.png")
        mock_generator.generate.assert_called_once()

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

    @patch('src.viewmodels.wallpaper_service.WallpaperSetter')
    @patch('src.viewmodels.wallpaper_service.ImageGenerator')
    def test_generate_and_set_wallpaper_success(self, mock_image_generator, mock_wallpaper_setter):
        """壁紙生成と設定が一度に実行されることを確認（成功ケース）"""
        from src.viewmodels.wallpaper_service import WallpaperService

        # モックの設定
        mock_generator = Mock()
        mock_generator.generate.return_value = Path("/tmp/test_wallpaper.png")
        mock_image_generator.return_value = mock_generator

        mock_setter = Mock()
        mock_setter.set_wallpaper.return_value = True
        mock_wallpaper_setter.return_value = mock_setter

        service = WallpaperService()
        result = service.generate_and_set_wallpaper(theme_name="simple", events=[])

        # 検証
        assert result is True
        mock_generator.generate.assert_called_once()
        mock_setter.set_wallpaper.assert_called_once_with(Path("/tmp/test_wallpaper.png"))

    @patch('src.viewmodels.wallpaper_service.WallpaperSetter')
    @patch('src.viewmodels.wallpaper_service.ImageGenerator')
    def test_generate_and_set_wallpaper_failure(self, mock_image_generator, mock_wallpaper_setter):
        """壁紙設定が失敗した場合の動作を確認"""
        from src.viewmodels.wallpaper_service import WallpaperService

        # モックの設定
        mock_generator = Mock()
        mock_generator.generate.return_value = Path("/tmp/test_wallpaper.png")
        mock_image_generator.return_value = mock_generator

        mock_setter = Mock()
        mock_setter.set_wallpaper.return_value = False  # 失敗
        mock_wallpaper_setter.return_value = mock_setter

        service = WallpaperService()
        result = service.generate_and_set_wallpaper(theme_name="simple", events=[])

        # 検証
        assert result is False
        mock_generator.generate.assert_called_once()
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
