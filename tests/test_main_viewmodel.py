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

            # WallpaperServiceが内部でCalendarClientを使用してイベント取得
            preview_path = viewmodel.generate_preview()

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

    def test_main_viewmodel_set_theme_does_not_auto_update(self, qtbot):
        """テーマ変更時に壁紙が自動更新されないこと（プレビュー→適用ワークフロー）"""
        from src.viewmodels.main_viewmodel import MainViewModel

        # モックサービスの設定
        mock_service = Mock()
        mock_service.get_available_themes.return_value = [
            "simple", "modern", "pastel", "dark", "vibrant"
        ]
        mock_service.generate_and_set_wallpaper.return_value = True

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()

            # update_startedシグナルをスパイ
            update_started_received = []
            viewmodel.update_started.connect(lambda: update_started_received.append(True))

            # テーマを変更
            viewmodel.set_theme("modern")

            # 少し待つ
            qtbot.wait(200)

            # update_startedシグナルが発火しないことを確認（壁紙は自動適用しない）
            assert len(update_started_received) == 0, \
                "テーマ変更時にupdate_startedが発火してはいけません（プレビュー→適用ワークフロー）"

            # テーマが変更されたことを確認
            assert viewmodel.current_theme == "modern"

    def test_theme_name_in_filename(self):
        """テーマ名がファイル名に含まれることを確認"""
        from src.image_generator import ImageGenerator
        from datetime import datetime
        from src.config import WALLPAPER_FILENAME_TEMPLATE

        # ImageGeneratorを初期化
        generator = ImageGenerator()

        # テーマを設定
        generator.set_theme("dark")

        # ファイル名を生成
        filename = WALLPAPER_FILENAME_TEMPLATE.format(
            theme="dark",
            date=datetime.now().strftime('%Y%m%d')
        )

        # テーマ名が含まれていることを確認
        assert "dark" in filename
        assert filename.startswith("wallpaper_dark_")


class TestAutoUpdateSettings:
    """自動更新設定のリアクティブ反映テスト"""

    def test_set_auto_update_interval(self, qapp):
        """自動更新間隔を変更できること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            viewmodel.set_auto_update_interval(30)
            assert viewmodel.auto_update_interval_minutes == 30

    def test_set_auto_update_interval_updates_timer(self, qapp):
        """間隔変更がタイマーに反映されること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            viewmodel.set_auto_update_interval(45)
            # タイマーのインターバルがミリ秒で反映されている
            assert viewmodel._auto_update_timer.interval() == 45 * 60 * 1000

    def test_get_next_update_time_when_active(self, qapp):
        """自動更新がアクティブ時に次回更新時刻を取得できること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            viewmodel.start_auto_update()
            next_time = viewmodel.get_next_update_time()
            assert next_time is not None
            assert isinstance(next_time, str)
            assert next_time != ""
            viewmodel.stop_auto_update()

    def test_get_next_update_time_when_inactive(self, qapp):
        """自動更新が停止中はNoneを返すこと"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            assert viewmodel.get_next_update_time() is None

    def test_on_settings_changed_updates_auto_update(self, qapp):
        """設定変更で自動更新状態が更新されること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            viewmodel.start_auto_update()
            assert viewmodel.is_auto_updating is True

            # 設定変更で自動更新を無効化
            viewmodel.on_settings_changed({
                "auto_update_enabled": False,
                "auto_update_interval_minutes": 30,
            })
            assert viewmodel.is_auto_updating is False

    def test_on_settings_changed_updates_interval(self, qapp):
        """設定変更で更新間隔が変更されること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            viewmodel.on_settings_changed({
                "auto_update_enabled": True,
                "auto_update_interval_minutes": 120,
            })
            assert viewmodel.auto_update_interval_minutes == 120
            assert viewmodel.is_auto_updating is True

    def test_on_settings_changed_enables_auto_update(self, qapp):
        """設定変更で自動更新を有効化できること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            assert viewmodel.is_auto_updating is False

            viewmodel.on_settings_changed({
                "auto_update_enabled": True,
                "auto_update_interval_minutes": 60,
            })
            assert viewmodel.is_auto_updating is True
            viewmodel.stop_auto_update()

    def test_auto_update_interval_property(self, qapp):
        """auto_update_interval_minutesプロパティがデフォルト値を返すこと"""
        from src.viewmodels.main_viewmodel import MainViewModel
        from src.config import AUTO_UPDATE_INTERVAL_MINUTES

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            assert viewmodel.auto_update_interval_minutes == AUTO_UPDATE_INTERVAL_MINUTES


class TestRetryLogic:
    """壁紙更新リトライロジックのテスト"""

    def test_retry_count_initial_zero(self, qapp):
        """初期状態でリトライカウントが0であること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            assert viewmodel.retry_count == 0

    def test_max_retries_default(self, qapp):
        """デフォルトの最大リトライ回数が3であること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        with patch('src.viewmodels.main_viewmodel.WallpaperService'):
            viewmodel = MainViewModel()
            assert viewmodel.max_retries == 3

    def test_retry_on_failure(self, qtbot, qapp):
        """壁紙更新失敗時にリトライがスケジュールされること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = False

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()
            viewmodel.start_auto_update()

            # 失敗をシミュレート
            viewmodel._on_worker_result(False)

            assert viewmodel.retry_count == 1
            assert viewmodel._retry_timer.isActive()

            viewmodel.stop_auto_update()
            viewmodel._retry_timer.stop()

    def test_retry_resets_on_success(self, qtbot, qapp):
        """壁紙更新成功時にリトライカウントがリセットされること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()
            viewmodel._retry_count = 2  # 2回失敗した状態

            # 成功をシミュレート
            viewmodel._on_worker_result(True)

            assert viewmodel.retry_count == 0

    def test_retry_stops_at_max(self, qtbot, qapp):
        """最大リトライ回数に達した場合、リトライを停止すること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()
            viewmodel.start_auto_update()
            viewmodel._retry_count = 3  # 既に最大回数

            # エラーシグナル受信用
            error_received = []
            viewmodel.error_occurred.connect(lambda msg: error_received.append(msg))

            # 失敗をシミュレート
            viewmodel._on_worker_result(False)

            # リトライタイマーは起動しない
            assert not viewmodel._retry_timer.isActive()
            # エラー通知が発火される
            assert len(error_received) >= 1

            viewmodel.stop_auto_update()

    def test_retry_not_triggered_without_auto_update(self, qapp):
        """自動更新が無効の場合、手動失敗ではリトライしないこと"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()
            # 自動更新は無効（デフォルト）

            viewmodel._on_worker_result(False)

            assert viewmodel.retry_count == 0
            assert not viewmodel._retry_timer.isActive()


class TestAuthFailureAutoStop:
    """認証失敗時の自動更新停止テスト"""

    def test_auth_error_stops_auto_update(self, qapp):
        """認証エラーで自動更新が停止されること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()
            viewmodel.start_auto_update()
            assert viewmodel.is_auto_updating is True

            # 認証エラーをシミュレート
            viewmodel._on_worker_error("認証エラー: トークンが無効です")

            assert viewmodel.is_auto_updating is False

    def test_auth_error_emits_signal(self, qapp):
        """認証エラーでエラーシグナルが発火されること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()
            viewmodel.start_auto_update()

            error_received = []
            viewmodel.error_occurred.connect(lambda msg: error_received.append(msg))

            viewmodel._on_worker_error("認証エラー: 401 Unauthorized")

            assert len(error_received) >= 1
            viewmodel.stop_auto_update()

    def test_non_auth_error_does_not_stop_auto_update(self, qapp):
        """認証以外のエラーでは自動更新が停止されないこと"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()
            viewmodel.start_auto_update()

            # ネットワークエラー（認証エラーではない）
            viewmodel._on_worker_error("ネットワーク接続エラー")

            # 自動更新は停止されない
            assert viewmodel.is_auto_updating is True

            viewmodel.stop_auto_update()

    def test_http_403_stops_auto_update(self, qapp):
        """HTTP 403エラーで自動更新が停止されること"""
        from src.viewmodels.main_viewmodel import MainViewModel

        mock_service = Mock()

        with patch('src.viewmodels.main_viewmodel.WallpaperService', return_value=mock_service):
            viewmodel = MainViewModel()
            viewmodel.start_auto_update()

            viewmodel._on_worker_error("HttpError 403: Forbidden")

            assert viewmodel.is_auto_updating is False


