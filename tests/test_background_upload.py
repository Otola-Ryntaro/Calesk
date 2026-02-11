"""
チケット020: 背景画像アップロード機能 テスト

TDD RED phase: GUI から背景画像を選択し壁紙に反映する機能を検証
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


class TestViewModelBackgroundImage:
    """MainViewModel の背景画像管理テスト"""

    def _create_viewmodel(self):
        from src.viewmodels.main_viewmodel import MainViewModel
        mock_service = MagicMock()
        mock_service.get_available_themes.return_value = ['simple', 'modern', 'pastel', 'dark', 'vibrant']
        mock_service.generate_wallpaper.return_value = Path('/tmp/test_wallpaper.png')
        return MainViewModel(wallpaper_service=mock_service)

    def _create_test_image(self, tmp_path, name="test_bg.png", size_bytes=1024):
        """テスト用の画像ファイルを作成"""
        test_file = tmp_path / name
        test_file.write_bytes(b'\x89PNG' + b'\x00' * (size_bytes - 4))
        return test_file

    def test_has_background_image_path_property(self):
        """background_image_path プロパティが存在すること"""
        vm = self._create_viewmodel()
        assert hasattr(vm, 'background_image_path')

    def test_default_background_image_path(self):
        """デフォルトの背景画像パスが None であること"""
        vm = self._create_viewmodel()
        assert vm.background_image_path is None

    def test_set_background_image(self, tmp_path):
        """背景画像パスを設定できること"""
        vm = self._create_viewmodel()
        test_path = self._create_test_image(tmp_path)
        vm.set_background_image(test_path)
        assert vm.background_image_path == test_path

    def test_reset_background_image(self, tmp_path):
        """背景画像をデフォルトプリセットに戻せること"""
        from src.config import BACKGROUNDS_DIR, DEFAULT_PRESET_BACKGROUND
        vm = self._create_viewmodel()
        test_path = self._create_test_image(tmp_path)
        vm.set_background_image(test_path)
        vm.reset_background_image()
        assert vm.background_image_path == BACKGROUNDS_DIR / DEFAULT_PRESET_BACKGROUND

    def test_background_image_changed_signal(self, qtbot, tmp_path):
        """背景画像変更時にシグナルが発信されること"""
        vm = self._create_viewmodel()
        test_path = self._create_test_image(tmp_path)
        with qtbot.waitSignal(vm.background_image_changed, timeout=1000) as blocker:
            vm.set_background_image(test_path)
        assert blocker.args[0] is not None

    def test_reset_emits_signal(self, qtbot, tmp_path):
        """背景画像リセット時にシグナルが発信されること"""
        from src.config import BACKGROUNDS_DIR, DEFAULT_PRESET_BACKGROUND
        vm = self._create_viewmodel()
        test_path = self._create_test_image(tmp_path)
        vm.set_background_image(test_path)
        with qtbot.waitSignal(vm.background_image_changed, timeout=1000) as blocker:
            vm.reset_background_image()
        assert blocker.args[0] == BACKGROUNDS_DIR / DEFAULT_PRESET_BACKGROUND

    def test_set_background_passes_to_service(self, tmp_path):
        """背景画像パスがWallpaperServiceに渡されること"""
        vm = self._create_viewmodel()
        test_path = self._create_test_image(tmp_path)
        vm.set_background_image(test_path)
        vm._wallpaper_service.set_background_image.assert_called_once_with(test_path)


class TestViewModelBackgroundImageValidation:
    """MainViewModel の背景画像バリデーションテスト"""

    def _create_viewmodel(self):
        from src.viewmodels.main_viewmodel import MainViewModel
        mock_service = MagicMock()
        mock_service.get_available_themes.return_value = ['simple', 'modern', 'pastel', 'dark', 'vibrant']
        return MainViewModel(wallpaper_service=mock_service)

    def test_rejects_nonexistent_file(self, qtbot):
        """存在しないファイルを拒否すること"""
        vm = self._create_viewmodel()
        error_received = []
        vm.error_occurred.connect(lambda msg: error_received.append(msg))

        vm.set_background_image(Path('/tmp/nonexistent_image.png'))

        assert vm.background_image_path is None
        assert len(error_received) == 1
        assert "ファイルが見つかりません" in error_received[0]

    def test_rejects_invalid_extension(self, tmp_path):
        """非対応の拡張子を拒否すること"""
        vm = self._create_viewmodel()
        error_received = []
        vm.error_occurred.connect(lambda msg: error_received.append(msg))

        test_file = tmp_path / "test.bmp"
        test_file.write_bytes(b'\x00' * 100)
        vm.set_background_image(test_file)

        assert vm.background_image_path is None
        assert len(error_received) == 1
        assert "非対応の画像形式" in error_received[0]

    def test_rejects_oversized_file(self, tmp_path):
        """サイズ超過ファイルを拒否すること"""
        vm = self._create_viewmodel()
        error_received = []
        vm.error_occurred.connect(lambda msg: error_received.append(msg))

        # 51MBのファイルを作成（上限50MB）
        test_file = tmp_path / "large.png"
        test_file.write_bytes(b'\x89PNG' + b'\x00' * (51 * 1024 * 1024))
        vm.set_background_image(test_file)

        assert vm.background_image_path is None
        assert len(error_received) == 1
        assert "大きすぎます" in error_received[0]

    def test_accepts_valid_jpg(self, tmp_path):
        """JPG形式を受け入れること"""
        vm = self._create_viewmodel()
        test_file = tmp_path / "test.jpg"
        test_file.write_bytes(b'\xff\xd8\xff' + b'\x00' * 100)
        vm.set_background_image(test_file)
        assert vm.background_image_path == test_file

    def test_accepts_valid_jpeg(self, tmp_path):
        """JPEG形式を受け入れること"""
        vm = self._create_viewmodel()
        test_file = tmp_path / "test.jpeg"
        test_file.write_bytes(b'\xff\xd8\xff' + b'\x00' * 100)
        vm.set_background_image(test_file)
        assert vm.background_image_path == test_file


class TestWallpaperServiceBackgroundImage:
    """WallpaperService の背景画像設定テスト"""

    def test_service_has_set_background_image(self):
        """WallpaperService に set_background_image メソッドがあること"""
        from src.viewmodels.wallpaper_service import WallpaperService
        assert hasattr(WallpaperService, 'set_background_image')

    def test_service_has_reset_background_image(self):
        """WallpaperService に reset_background_image メソッドがあること"""
        from src.viewmodels.wallpaper_service import WallpaperService
        assert hasattr(WallpaperService, 'reset_background_image')


class TestImageGeneratorCustomBackground:
    """ImageGenerator のカスタム背景画像テスト"""

    def _create_generator(self, theme='simple'):
        from src.image_generator import ImageGenerator
        with patch('src.image_generator.THEME', theme):
            return ImageGenerator()

    def test_generator_has_set_background(self):
        """ImageGenerator に set_background_image メソッドがあること"""
        gen = self._create_generator()
        assert hasattr(gen, 'set_background_image')

    def test_generator_has_reset_background(self):
        """ImageGenerator に reset_background_image メソッドがあること"""
        gen = self._create_generator()
        assert hasattr(gen, 'reset_background_image')

    def test_generator_custom_background_property(self):
        """ImageGenerator に custom_background_path プロパティがあること"""
        gen = self._create_generator()
        assert hasattr(gen, 'custom_background_path')
        assert gen.custom_background_path is None
