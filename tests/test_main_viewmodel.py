"""
MainViewModelのテスト

メインウィンドウのビジネスロジックをテストします。
"""

import pytest
from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from pytestqt.exceptions import TimeoutError


class TestMainViewModel:
    """MainViewModelの基本機能をテストする"""

    def test_main_viewmodel_exists(self, qapp):
        """MainViewModelクラスが存在することを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel
        from src.viewmodels.base_viewmodel import ViewModelBase

        assert MainViewModel is not None
        assert issubclass(MainViewModel, ViewModelBase)

    def test_main_viewmodel_initialization(self, qapp):
        """MainViewModelが正しく初期化されることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()

            assert viewmodel is not None
            assert isinstance(viewmodel, QObject)
            assert hasattr(viewmodel, 'current_theme')
            assert hasattr(viewmodel, 'is_updating')

    def test_main_viewmodel_default_theme(self, qapp):
        """デフォルトテーマが'simple'であることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()

            assert viewmodel.current_theme == "simple"
            assert viewmodel.is_updating is False

    def test_main_viewmodel_has_signals(self, qapp):
        """MainViewModelが必要なシグナルを持つことを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()

            # シグナルの存在確認
            assert hasattr(viewmodel, 'theme_changed')
            assert hasattr(viewmodel, 'wallpaper_updated')
            assert hasattr(viewmodel, 'update_started')
            assert hasattr(viewmodel, 'update_completed')
            assert hasattr(viewmodel, 'error_occurred')

    def test_main_viewmodel_get_available_themes(self, qapp):
        """利用可能なテーマのリストを取得できることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()
        mock_service.get_available_themes.return_value = [
            "simple", "modern", "pastel", "dark", "vibrant"
        ]

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            themes = viewmodel.get_available_themes()

            assert isinstance(themes, list)
            assert len(themes) == 5
            assert "simple" in themes
            assert "modern" in themes

    def test_main_viewmodel_set_theme(self, qtbot):
        """テーマを変更できることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # モックサービスの設定
        mock_service = Mock()
        mock_service.get_available_themes.return_value = [
            "simple", "modern", "pastel", "dark", "vibrant"
        ]

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # シグナル受信用
            with qtbot.waitSignal(viewmodel.theme_changed, timeout=1000) as blocker:
                viewmodel.set_theme("modern")

            assert viewmodel.current_theme == "modern"
            assert blocker.args == ["modern"]

    def test_main_viewmodel_set_same_theme_no_signal(self, qtbot):
        """同じテーマを設定してもシグナルが発火しないことを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()

            # 同じテーマを設定
            viewmodel.set_theme("simple")

            # シグナルが発火しないことを確認（タイムアウトを期待）
            with pytest.raises(TimeoutError):  # waitSignalがタイムアウトすることを期待
                with qtbot.waitSignal(viewmodel.theme_changed, timeout=100):
                    pass

    def test_main_viewmodel_update_wallpaper(self, qtbot):
        """壁紙を更新できることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # モックサービスの設定
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # シグナル受信用
            with qtbot.waitSignal(viewmodel.update_started, timeout=1000):
                with qtbot.waitSignal(viewmodel.update_completed, timeout=1000):
                    result = viewmodel.update_wallpaper()

            assert result is True
            assert viewmodel.is_updating is False  # 更新完了後はFalse
            mock_service.generate_and_set_wallpaper.assert_called_once()

    def test_main_viewmodel_update_wallpaper_with_events(self, qtbot, qapp):
        """イベントを指定して壁紙を更新できることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # モックサービスの設定
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            events = [
                {"start": "2024-01-15 10:00", "summary": "ミーティング"}
            ]

            result = viewmodel.update_wallpaper(events=events)

            assert result is True

            # 非同期実行完了を待つ
            qtbot.wait(1000)

            # eventsが渡されたことを確認
            call_args = mock_service.generate_and_set_wallpaper.call_args
            assert call_args[1]['events'] == events

    def test_main_viewmodel_update_wallpaper_error(self, qtbot):
        """壁紙更新時のエラーハンドリングを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # モックサービスでエラーを発生させる
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.side_effect = Exception("Test error")

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # エラーシグナル受信用
            error_received = []
            completed_received = []

            viewmodel.error_occurred.connect(lambda msg: error_received.append(msg))
            viewmodel.update_completed.connect(lambda success: completed_received.append(success))

            # ワーカー起動は成功する
            result = viewmodel.update_wallpaper()
            assert result is True

            # 非同期実行完了を待つ
            qtbot.wait(1000)

            # エラーが通知されたことを確認
            assert len(error_received) == 1
            assert "Test error" in error_received[0]
            assert len(completed_received) == 1
            assert completed_received[0] is False
            assert viewmodel.is_updating is False  # エラー後もFalse

    def test_main_viewmodel_generate_preview(self, qapp):
        """プレビュー画像を生成できることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # モックサービスの設定
        mock_service = Mock()
        mock_path = Path("/tmp/preview.png")
        mock_service.generate_wallpaper.return_value = mock_path

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            events = [{"start": "2024-01-15 10:00", "summary": "テスト"}]
            preview_path = viewmodel.generate_preview(events=events)

            assert preview_path == mock_path
            mock_service.generate_wallpaper.assert_called_once()

    def test_main_viewmodel_concurrent_updates_prevented(self, qapp):
        """同時更新が防止されることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # 長時間かかる更新をモック
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # 更新中フラグを手動で設定（内部変数に直接アクセス）
            viewmodel._is_updating = True

            # 2回目の更新は拒否される
            result = viewmodel.update_wallpaper()

            assert result is False
            # generate_and_set_wallpaperは呼ばれない
            mock_service.generate_and_set_wallpaper.assert_not_called()

    def test_main_viewmodel_async_update_wallpaper(self, qtbot, qapp):
        """壁紙更新が非同期で実行されることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # モックサービスの設定
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # シグナル受信用
            started_received = []
            completed_received = []

            viewmodel.update_started.connect(lambda: started_received.append(True))
            viewmodel.update_completed.connect(lambda success: completed_received.append(success))

            # 非同期更新を実行
            viewmodel.update_wallpaper()

            # 少し待つ
            qtbot.wait(1000)

            # シグナルが発火されたことを確認
            assert len(started_received) == 1
            assert len(completed_received) == 1
            assert completed_received[0] is True

    def test_main_viewmodel_progress_signal(self, qtbot, qapp):
        """進捗シグナルが発火されることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # モックサービスの設定
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # 進捗シグナルが存在することを確認
            assert hasattr(viewmodel, 'progress_updated')

            # 進捗シグナル受信用
            progress_values = []
            viewmodel.progress_updated.connect(lambda value: progress_values.append(value))

            # 非同期更新を実行
            viewmodel.update_wallpaper()

            # 少し待つ
            qtbot.wait(1000)

            # 進捗シグナルが発火されたことを確認
            assert len(progress_values) > 0

    def test_main_viewmodel_cancel_update(self, qtbot, qapp):
        """壁紙更新をキャンセルできることを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel
        import time

        # 長時間かかる更新をモック
        def slow_process(*args, **kwargs):
            time.sleep(0.5)
            return True

        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.side_effect = slow_process

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # 結果受信用
            completed_received = []
            viewmodel.update_completed.connect(lambda success: completed_received.append(success))

            # 非同期更新を実行
            viewmodel.update_wallpaper()

            # 少し待ってからキャンセル
            qtbot.wait(100)
            viewmodel.cancel_update()

            # 完了を待つ
            qtbot.wait(1000)

            # キャンセルされたため、結果はFalse
            assert len(completed_received) == 1
            assert completed_received[0] is False

    # HIGH-3: 入力検証テスト
    def test_main_viewmodel_set_theme_invalid_theme_name(self, qtbot):
        """無効なテーマ名を設定した場合にエラーシグナルが発火することを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # モックサービスで利用可能なテーマを設定
        mock_service = Mock()
        mock_service.get_available_themes.return_value = [
            "simple", "modern", "pastel", "dark", "vibrant"
        ]

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # エラーシグナル受信用
            error_received = []
            viewmodel.error_occurred.connect(lambda msg: error_received.append(msg))

            # 無効なテーマを設定
            viewmodel.set_theme("invalid_theme")

            # エラーシグナルが発火したことを確認
            assert len(error_received) == 1
            assert "無効なテーマ" in error_received[0] or "invalid" in error_received[0].lower()

            # current_themeが変更されていないことを確認
            assert viewmodel.current_theme == "simple"

    def test_main_viewmodel_set_theme_empty_string(self, qtbot):
        """空文字列のテーマ名を拒否することを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()

            # エラーシグナル受信用
            error_received = []
            viewmodel.error_occurred.connect(lambda msg: error_received.append(msg))

            # 空文字列を設定
            viewmodel.set_theme("")

            # エラーシグナルが発火したことを確認
            assert len(error_received) == 1

            # current_themeが変更されていないことを確認
            assert viewmodel.current_theme == "simple"

    def test_main_viewmodel_set_theme_none(self, qtbot):
        """Noneのテーマ名を拒否することを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()

            # エラーシグナル受信用
            error_received = []
            viewmodel.error_occurred.connect(lambda msg: error_received.append(msg))

            # Noneを設定
            viewmodel.set_theme(None)

            # エラーシグナルが発火したことを確認
            assert len(error_received) == 1

            # current_themeが変更されていないことを確認
            assert viewmodel.current_theme == "simple"

    def test_main_viewmodel_update_wallpaper_invalid_events_structure(self, qtbot, qapp):
        """無効なイベントデータ構造を拒否することを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # エラーシグナル受信用
            error_received = []
            viewmodel.error_occurred.connect(lambda msg: error_received.append(msg))

            # 無効な構造（dictではなくstring）
            invalid_events = ["not a dict"]

            # 更新を実行
            viewmodel.update_wallpaper(events=invalid_events)

            # 少し待つ
            qtbot.wait(500)

            # エラーが通知されたことを確認
            assert len(error_received) >= 1

    def test_main_viewmodel_update_wallpaper_missing_required_fields(self, qtbot, qapp):
        """必須フィールドがないイベントデータを拒否することを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # エラーシグナル受信用
            error_received = []
            viewmodel.error_occurred.connect(lambda msg: error_received.append(msg))

            # 必須フィールド（start, summary）がない
            invalid_events = [
                {"end": "2024-01-15 11:00"}  # startとsummaryがない
            ]

            # 更新を実行
            viewmodel.update_wallpaper(events=invalid_events)

            # 少し待つ
            qtbot.wait(500)

            # エラーが通知されたことを確認
            assert len(error_received) >= 1

    def test_main_viewmodel_update_wallpaper_invalid_datetime_format(self, qtbot, qapp):
        """不正な日時フォーマットを拒否することを確認"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # エラーシグナル受信用
            error_received = []
            viewmodel.error_occurred.connect(lambda msg: error_received.append(msg))

            # 不正な日時フォーマット
            invalid_events = [
                {"start": "invalid-date-format", "summary": "テスト"}
            ]

            # 更新を実行
            viewmodel.update_wallpaper(events=invalid_events)

            # 少し待つ
            qtbot.wait(500)

            # エラーが通知されたことを確認
            assert len(error_received) >= 1
