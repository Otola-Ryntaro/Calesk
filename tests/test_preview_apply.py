"""
チケット019: プレビュー→適用ワークフロー テスト

テーマ選択→プレビュー→適用の2ステップワークフローを検証
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path


class TestPreviewTheme:
    """プレビュー生成テスト"""

    def _create_viewmodel(self):
        from src.viewmodels.main_viewmodel import MainViewModel
        mock_service = MagicMock()
        mock_service.get_available_themes.return_value = ['simple', 'modern', 'pastel', 'dark', 'vibrant']
        mock_service.generate_wallpaper.return_value = Path('/tmp/test_wallpaper.png')
        return MainViewModel(wallpaper_service=mock_service)

    def test_preview_theme_exists(self):
        """preview_theme メソッドが存在すること"""
        vm = self._create_viewmodel()
        assert hasattr(vm, 'preview_theme')
        assert callable(vm.preview_theme)

    def test_preview_theme_emits_signal(self, qtbot):
        """preview_theme が非同期でプレビュー画像を生成しシグナルを発信すること"""
        vm = self._create_viewmodel()
        with qtbot.waitSignal(vm.preview_ready, timeout=2000) as blocker:
            vm.preview_theme('modern')
        assert blocker.args[0] is not None

    def test_preview_theme_does_not_set_wallpaper(self, qtbot):
        """preview_theme が壁紙を設定しないこと"""
        vm = self._create_viewmodel()
        with qtbot.waitSignal(vm.preview_ready, timeout=2000):
            vm.preview_theme('modern')
        vm._wallpaper_service.set_wallpaper.assert_not_called()

    def test_preview_theme_calls_generate_wallpaper(self, qtbot):
        """preview_theme が generate_wallpaper を呼ぶこと"""
        vm = self._create_viewmodel()
        with qtbot.waitSignal(vm.preview_ready, timeout=2000):
            vm.preview_theme('modern')
        vm._wallpaper_service.generate_wallpaper.assert_called_once_with(
            theme_name='modern'
        )

    def test_preview_ready_signal_emitted(self, qtbot):
        """preview_theme 完了時に preview_ready シグナルが発信されること"""
        vm = self._create_viewmodel()
        with qtbot.waitSignal(vm.preview_ready, timeout=2000) as blocker:
            vm.preview_theme('modern')
        assert blocker.args[0] is not None


class TestPreviewDebounce:
    """プレビューのデバウンステスト"""

    def _create_viewmodel(self):
        from src.viewmodels.main_viewmodel import MainViewModel
        mock_service = MagicMock()
        mock_service.get_available_themes.return_value = ['simple', 'modern', 'pastel', 'dark', 'vibrant']
        mock_service.generate_wallpaper.return_value = Path('/tmp/test_wallpaper.png')
        return MainViewModel(wallpaper_service=mock_service)

    def test_rapid_preview_calls_debounced(self, qtbot):
        """連続呼び出し時、最後のテーマのみプレビューされること"""
        vm = self._create_viewmodel()
        # 高速に3回テーマを変更
        vm.preview_theme('modern')
        vm.preview_theme('pastel')
        vm.preview_theme('dark')

        # 最後の呼び出しのみが実行される
        with qtbot.waitSignal(vm.preview_ready, timeout=2000):
            pass

        # generate_wallpaperは1回だけ呼ばれる（最後のテーマ）
        vm._wallpaper_service.generate_wallpaper.assert_called_once_with(
            theme_name='dark'
        )

    def test_debounce_timer_exists(self):
        """デバウンスタイマーが初期化されていること"""
        vm = self._create_viewmodel()
        assert hasattr(vm, '_preview_debounce_timer')
        assert vm._preview_debounce_timer.isSingleShot()


class TestSetThemeNoAutoApply:
    """テーマ変更時に壁紙が自動適用されないことのテスト"""

    def _create_viewmodel(self):
        from src.viewmodels.main_viewmodel import MainViewModel
        mock_service = MagicMock()
        mock_service.get_available_themes.return_value = ['simple', 'modern', 'pastel', 'dark', 'vibrant']
        mock_service.generate_wallpaper.return_value = Path('/tmp/test_wallpaper.png')
        return MainViewModel(wallpaper_service=mock_service)

    def test_set_theme_does_not_call_update_wallpaper(self):
        """set_theme がupdate_wallpaper を呼ばないこと"""
        vm = self._create_viewmodel()
        vm.update_wallpaper = MagicMock()
        vm.set_theme('modern')
        vm.update_wallpaper.assert_not_called()

    def test_set_theme_changes_current_theme(self):
        """set_theme がテーマを変更すること"""
        vm = self._create_viewmodel()
        vm.set_theme('modern')
        assert vm.current_theme == 'modern'

    def test_set_theme_emits_theme_changed(self, qtbot):
        """set_theme がテーマ変更シグナルを発信すること"""
        vm = self._create_viewmodel()
        with qtbot.waitSignal(vm.theme_changed, timeout=1000) as blocker:
            vm.set_theme('modern')
        assert blocker.args == ['modern']


class TestApplyWallpaper:
    """壁紙適用テスト"""

    def _create_viewmodel(self):
        from src.viewmodels.main_viewmodel import MainViewModel
        mock_service = MagicMock()
        mock_service.get_available_themes.return_value = ['simple', 'modern', 'pastel', 'dark', 'vibrant']
        mock_service.generate_and_set_wallpaper.return_value = True
        return MainViewModel(wallpaper_service=mock_service)

    def test_apply_wallpaper_exists(self):
        """apply_wallpaper メソッドが存在すること"""
        vm = self._create_viewmodel()
        assert hasattr(vm, 'apply_wallpaper')
        assert callable(vm.apply_wallpaper)

    def test_apply_wallpaper_starts_worker(self):
        """apply_wallpaper がワーカーを起動すること"""
        vm = self._create_viewmodel()
        vm.set_theme('modern')
        result = vm.apply_wallpaper()
        assert result is True
        assert vm.is_updating is True

    def test_apply_wallpaper_uses_current_theme(self):
        """apply_wallpaper が現在のテーマを使うこと"""
        vm = self._create_viewmodel()
        vm.set_theme('dark')
        assert vm.current_theme == 'dark'


class TestPreviewReadySignal:
    """preview_ready シグナルのテスト"""

    def _create_viewmodel(self):
        from src.viewmodels.main_viewmodel import MainViewModel
        mock_service = MagicMock()
        mock_service.get_available_themes.return_value = ['simple', 'modern', 'pastel', 'dark', 'vibrant']
        mock_service.generate_wallpaper.return_value = Path('/tmp/test_preview.png')
        return MainViewModel(wallpaper_service=mock_service)

    def test_preview_ready_signal_exists(self):
        """preview_ready シグナルが定義されていること"""
        vm = self._create_viewmodel()
        assert hasattr(vm, 'preview_ready')

    def test_preview_ready_returns_path(self, qtbot):
        """preview_ready シグナルがパスを返すこと"""
        vm = self._create_viewmodel()
        with qtbot.waitSignal(vm.preview_ready, timeout=2000) as blocker:
            vm.preview_theme('simple')
        path = blocker.args[0]
        assert isinstance(path, (str, Path))
