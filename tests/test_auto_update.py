"""
チケット018 Phase 1: 自動更新（QTimer方式）テスト

TDD RED phase: 自動更新機能の期待動作を定義
"""
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QTimer


class TestAutoUpdateConfig:
    """自動更新設定テスト"""

    def test_auto_update_interval_exists(self):
        """AUTO_UPDATE_INTERVAL_MINUTES が定義されていること"""
        from src.config import AUTO_UPDATE_INTERVAL_MINUTES
        assert isinstance(AUTO_UPDATE_INTERVAL_MINUTES, (int, float))

    def test_auto_update_interval_default(self):
        """自動更新間隔のデフォルトが60分であること"""
        from src.config import AUTO_UPDATE_INTERVAL_MINUTES
        assert AUTO_UPDATE_INTERVAL_MINUTES == 60

    def test_auto_update_enabled_default_exists(self):
        """AUTO_UPDATE_ENABLED_DEFAULT が定義されていること"""
        from src.config import AUTO_UPDATE_ENABLED_DEFAULT
        assert isinstance(AUTO_UPDATE_ENABLED_DEFAULT, bool)

    def test_auto_update_enabled_default_is_true(self):
        """デフォルトで自動更新が有効であること"""
        from src.config import AUTO_UPDATE_ENABLED_DEFAULT
        assert AUTO_UPDATE_ENABLED_DEFAULT is True


class TestAutoUpdateViewModel:
    """MainViewModelの自動更新機能テスト"""

    def _create_viewmodel(self):
        from src.viewmodels.main_viewmodel import MainViewModel
        mock_service = MagicMock()
        mock_service.get_available_themes.return_value = ['simple', 'modern']
        return MainViewModel(wallpaper_service=mock_service)

    def test_viewmodel_has_auto_update_timer(self):
        """ViewModelが自動更新タイマーを持つこと"""
        vm = self._create_viewmodel()
        assert hasattr(vm, '_auto_update_timer')
        assert isinstance(vm._auto_update_timer, QTimer)

    def test_start_auto_update(self, qtbot):
        """自動更新を開始できること"""
        vm = self._create_viewmodel()
        vm.start_auto_update()
        assert vm._auto_update_timer.isActive()

    def test_stop_auto_update(self, qtbot):
        """自動更新を停止できること"""
        vm = self._create_viewmodel()
        vm.start_auto_update()
        vm.stop_auto_update()
        assert not vm._auto_update_timer.isActive()

    def test_is_auto_updating_property(self, qtbot):
        """is_auto_updating プロパティが機能すること"""
        vm = self._create_viewmodel()
        assert vm.is_auto_updating is False
        vm.start_auto_update()
        assert vm.is_auto_updating is True
        vm.stop_auto_update()
        assert vm.is_auto_updating is False

    def test_auto_update_signal_emitted_on_start(self, qtbot):
        """自動更新開始時にシグナルが発信されること"""
        vm = self._create_viewmodel()
        with qtbot.waitSignal(vm.auto_update_status_changed, timeout=1000) as blocker:
            vm.start_auto_update()
        assert blocker.args == [True]

    def test_auto_update_signal_emitted_on_stop(self, qtbot):
        """自動更新停止時にシグナルが発信されること"""
        vm = self._create_viewmodel()
        vm.start_auto_update()
        with qtbot.waitSignal(vm.auto_update_status_changed, timeout=1000) as blocker:
            vm.stop_auto_update()
        assert blocker.args == [False]

    def test_timer_interval_matches_config(self):
        """タイマー間隔がconfig設定と一致すること"""
        from src.config import AUTO_UPDATE_INTERVAL_MINUTES
        vm = self._create_viewmodel()
        expected_ms = AUTO_UPDATE_INTERVAL_MINUTES * 60 * 1000
        assert vm._auto_update_timer.interval() == expected_ms

    def test_cleanup_stops_timer(self):
        """cleanupで自動更新タイマーが停止されること"""
        vm = self._create_viewmodel()
        vm.start_auto_update()
        assert vm._auto_update_timer.isActive()
        vm.cleanup()
        assert not vm._auto_update_timer.isActive()
