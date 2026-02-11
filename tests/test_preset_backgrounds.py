"""
プリセット背景画像システムのテスト
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.config import PRESET_BACKGROUNDS, DEFAULT_PRESET_BACKGROUND, BACKGROUNDS_DIR


class TestPresetBackgroundsConfig:
    """config.pyのプリセット背景設定テスト"""

    def test_preset_backgrounds_is_list(self):
        """PRESET_BACKGROUNDSがリスト型であること"""
        assert isinstance(PRESET_BACKGROUNDS, list)

    def test_preset_backgrounds_has_items(self):
        """プリセットが1つ以上あること"""
        assert len(PRESET_BACKGROUNDS) >= 1

    def test_preset_backgrounds_have_required_keys(self):
        """各プリセットにnameとfileキーがあること"""
        for preset in PRESET_BACKGROUNDS:
            assert "name" in preset, f"nameキーがない: {preset}"
            assert "file" in preset, f"fileキーがない: {preset}"

    def test_preset_backgrounds_files_exist(self):
        """プリセット画像ファイルが実際に存在すること"""
        for preset in PRESET_BACKGROUNDS:
            path = BACKGROUNDS_DIR / preset["file"]
            assert path.exists(), f"プリセット画像が存在しない: {path}"

    def test_default_preset_is_valid(self):
        """デフォルトプリセットがプリセット一覧に含まれること"""
        files = [p["file"] for p in PRESET_BACKGROUNDS]
        assert DEFAULT_PRESET_BACKGROUND in files

    def test_preset_names_are_unique(self):
        """プリセット名が重複しないこと"""
        names = [p["name"] for p in PRESET_BACKGROUNDS]
        assert len(names) == len(set(names))

    def test_preset_files_are_unique(self):
        """プリセットファイル名が重複しないこと"""
        files = [p["file"] for p in PRESET_BACKGROUNDS]
        assert len(files) == len(set(files))


class TestMainViewModelPresetBackground:
    """MainViewModelのプリセット背景メソッドテスト"""

    @pytest.fixture
    def viewmodel(self):
        """テスト用ViewModelを作成"""
        with patch('src.viewmodels.main_viewmodel.QTimer'), \
             patch('src.viewmodels.main_viewmodel.QThreadPool'):
            from src.viewmodels.main_viewmodel import MainViewModel
            mock_service = MagicMock()
            vm = MainViewModel(wallpaper_service=mock_service)
            return vm

    def test_set_preset_background_sets_path(self, viewmodel):
        """プリセット背景設定でパスが正しく設定されること"""
        viewmodel.set_preset_background(DEFAULT_PRESET_BACKGROUND)
        expected = BACKGROUNDS_DIR / DEFAULT_PRESET_BACKGROUND
        assert viewmodel.background_image_path == expected

    def test_set_preset_background_calls_service(self, viewmodel):
        """プリセット背景設定でWallpaperServiceに通知されること"""
        viewmodel.set_preset_background(DEFAULT_PRESET_BACKGROUND)
        viewmodel._wallpaper_service.set_background_image.assert_called_once()

    def test_set_preset_background_nonexistent_file(self, viewmodel):
        """存在しないプリセットファイルでパスが変わらないこと"""
        original_path = viewmodel.background_image_path
        viewmodel.set_preset_background("nonexistent.png")
        # エラー時はパスが変更されない
        assert viewmodel.background_image_path == original_path

    def test_reset_background_sets_default_preset(self, viewmodel):
        """リセットでデフォルトプリセットに戻ること"""
        viewmodel.reset_background_image()
        expected = BACKGROUNDS_DIR / DEFAULT_PRESET_BACKGROUND
        assert viewmodel.background_image_path == expected


class TestSettingsServiceBackground:
    """SettingsServiceの背景画像永続化テスト"""

    @pytest.fixture
    def settings_service(self, tmp_path):
        """テスト用SettingsServiceを作成"""
        from src.viewmodels.settings_service import SettingsService
        return SettingsService(settings_dir=tmp_path)

    def test_default_background_is_preset_format(self, settings_service):
        """デフォルト背景設定がpreset:形式であること"""
        value = settings_service.get("background_image_path")
        assert value.startswith("preset:")

    def test_save_and_load_preset_background(self, settings_service):
        """プリセット背景の保存と読み込みが正しく動作すること"""
        settings_service.set("background_image_path", "preset:beach.png")
        settings_service.save()

        # 新しいインスタンスで読み込み
        from src.viewmodels.settings_service import SettingsService
        loaded = SettingsService(settings_dir=settings_service.settings_dir)
        loaded.load()
        assert loaded.get("background_image_path") == "preset:beach.png"

    def test_save_and_load_custom_background(self, settings_service):
        """カスタム背景パスの保存と読み込みが正しく動作すること"""
        custom_path = "/Users/test/custom.png"
        settings_service.set("background_image_path", custom_path)
        settings_service.save()

        from src.viewmodels.settings_service import SettingsService
        loaded = SettingsService(settings_dir=settings_service.settings_dir)
        loaded.load()
        assert loaded.get("background_image_path") == custom_path
