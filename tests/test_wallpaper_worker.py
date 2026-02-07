"""
WallpaperWorkerのテスト

非同期壁紙更新ワーカーをテストします。
"""

import pytest
from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import time


class TestWallpaperWorker:
    """WallpaperWorkerの基本機能をテストする"""

    def test_wallpaper_worker_exists(self, qapp):
        """WallpaperWorkerクラスが存在することを確認"""
        from src.viewmodels.wallpaper_worker import WallpaperWorker
        from PyQt6.QtCore import QRunnable

        assert WallpaperWorker is not None
        # QRunnableは直接継承チェックができないため、インスタンス作成で確認

    def test_wallpaper_worker_initialization(self, qapp):
        """WallpaperWorkerが正しく初期化されることを確認"""
        from src.viewmodels.wallpaper_worker import WallpaperWorker

        mock_service = Mock()
        theme_name = "simple"

        worker = WallpaperWorker(mock_service, theme_name)

        assert worker is not None
        assert hasattr(worker, 'signals')

    def test_wallpaper_worker_has_signals(self, qapp):
        """WallpaperWorkerが必要なシグナルを持つことを確認"""
        from src.viewmodels.wallpaper_worker import WallpaperWorker

        mock_service = Mock()
        worker = WallpaperWorker(mock_service, "simple")

        # シグナルの存在確認
        assert hasattr(worker.signals, 'started')
        assert hasattr(worker.signals, 'progress')
        assert hasattr(worker.signals, 'finished')
        assert hasattr(worker.signals, 'error')
        assert hasattr(worker.signals, 'result')

    def test_wallpaper_worker_run_success(self, qtbot, qapp):
        """壁紙更新が成功することを確認"""
        from src.viewmodels.wallpaper_worker import WallpaperWorker

        # モックサービスの設定
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        worker = WallpaperWorker(mock_service, "simple")

        # シグナル受信用
        started_received = []
        finished_received = []
        result_received = []

        worker.signals.started.connect(lambda: started_received.append(True))
        worker.signals.finished.connect(lambda: finished_received.append(True))
        worker.signals.result.connect(lambda success: result_received.append(success))

        # ワーカーを実行
        thread_pool = QThreadPool.globalInstance()
        thread_pool.start(worker)

        # 完了を待つ（最大5秒）
        thread_pool.waitForDone(5000)

        # イベントループを回してシグナルを処理
        qtbot.wait(100)

        # シグナルが発火されたことを確認
        assert len(started_received) == 1
        assert len(finished_received) == 1
        assert len(result_received) == 1
        assert result_received[0] is True

        # サービスが呼ばれたことを確認
        mock_service.generate_and_set_wallpaper.assert_called_once()

    def test_wallpaper_worker_run_with_progress(self, qtbot, qapp):
        """進捗シグナルが発火されることを確認"""
        from src.viewmodels.wallpaper_worker import WallpaperWorker

        # モックサービスの設定
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        worker = WallpaperWorker(mock_service, "simple")

        # 進捗シグナル受信用
        progress_values = []
        worker.signals.progress.connect(lambda value: progress_values.append(value))

        # ワーカーを実行
        thread_pool = QThreadPool.globalInstance()
        thread_pool.start(worker)
        thread_pool.waitForDone(5000)

        # イベントループを回してシグナルを処理
        qtbot.wait(100)

        # 進捗シグナルが発火されたことを確認
        assert len(progress_values) > 0
        # 最終的に100になることを確認
        assert 100 in progress_values

    def test_wallpaper_worker_run_error(self, qtbot, qapp):
        """エラーハンドリングを確認"""
        from src.viewmodels.wallpaper_worker import WallpaperWorker

        # モックサービスでエラーを発生させる
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.side_effect = Exception("Test error")

        worker = WallpaperWorker(mock_service, "simple")

        # エラーシグナル受信用
        error_received = []
        result_received = []

        worker.signals.error.connect(lambda msg: error_received.append(msg))
        worker.signals.result.connect(lambda success: result_received.append(success))

        # ワーカーを実行
        thread_pool = QThreadPool.globalInstance()
        thread_pool.start(worker)
        thread_pool.waitForDone(5000)

        # イベントループを回してシグナルを処理
        qtbot.wait(100)

        # エラーシグナルが発火されたことを確認
        assert len(error_received) == 1
        assert "Test error" in error_received[0]
        assert len(result_received) == 1
        assert result_received[0] is False

    def test_wallpaper_worker_cancel(self, qtbot, qapp):
        """キャンセル機能を確認"""
        from src.viewmodels.wallpaper_worker import WallpaperWorker

        # 長時間かかる処理をモック
        def slow_process(*args, **kwargs):
            time.sleep(0.5)
            return True

        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.side_effect = slow_process

        worker = WallpaperWorker(mock_service, "simple")

        # 結果受信用
        result_received = []
        worker.signals.result.connect(lambda success: result_received.append(success))

        # ワーカーを実行
        thread_pool = QThreadPool.globalInstance()
        thread_pool.start(worker)

        # 少し待ってからキャンセル
        qtbot.wait(100)
        worker.cancel()

        # 完了を待つ
        thread_pool.waitForDone(5000)

        # イベントループを回してシグナルを処理
        qtbot.wait(100)

        # キャンセルされたため、結果はFalse
        assert len(result_received) == 1
        assert result_received[0] is False

    def test_wallpaper_worker_with_different_theme(self, qtbot, qapp):
        """異なるテーマで壁紙を更新できることを確認"""
        from src.viewmodels.wallpaper_worker import WallpaperWorker

        # モックサービスの設定
        mock_service = Mock()
        mock_service.generate_and_set_wallpaper.return_value = True

        worker = WallpaperWorker(mock_service, "modern")

        # 結果受信用
        result_received = []
        worker.signals.result.connect(lambda success: result_received.append(success))

        # ワーカーを実行
        thread_pool = QThreadPool.globalInstance()
        thread_pool.start(worker)
        thread_pool.waitForDone(5000)

        # イベントループを回してシグナルを処理
        qtbot.wait(100)

        # 成功
        assert len(result_received) == 1
        assert result_received[0] is True

        # テーマ名が渡されたことを確認
        call_args = mock_service.generate_and_set_wallpaper.call_args
        assert call_args[1]['theme_name'] == "modern"
