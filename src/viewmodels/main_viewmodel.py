"""
MainViewModel

メイン画面のビジネスロジックを管理するViewModel。
MVVMパターンにおけるViewModel層。
"""

from PyQt6.QtCore import pyqtSignal, QThreadPool, QTimer
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from src.viewmodels.base_viewmodel import ViewModelBase
from src.viewmodels.wallpaper_service import WallpaperService
from src.viewmodels.wallpaper_worker import WallpaperWorker, PreviewWorker

logger = logging.getLogger(__name__)


class MainViewModel(ViewModelBase):
    """
    メインViewModel

    アプリケーションのメイン画面の状態とロジックを管理します。
    テーマ選択、壁紙更新、プレビュー生成などの機能を提供します。
    """

    # シグナル定義
    theme_changed = pyqtSignal(str)  # テーマが変更されたとき
    wallpaper_updated = pyqtSignal(bool)  # 壁紙が更新されたとき（成功/失敗）
    update_started = pyqtSignal()  # 更新開始
    update_completed = pyqtSignal(bool)  # 更新完了（成功/失敗）
    progress_updated = pyqtSignal(int)  # 進捗更新（0-100）
    error_occurred = pyqtSignal(str)  # エラーが発生したとき
    auto_update_status_changed = pyqtSignal(bool)  # 自動更新状態変更
    preview_ready = pyqtSignal(object)  # プレビュー画像生成完了（Pathを通知）
    background_image_changed = pyqtSignal(object)  # 背景画像変更（Pathまたは None）

    def __init__(self, wallpaper_service: Optional[WallpaperService] = None, parent=None):
        """
        MainViewModelを初期化

        Args:
            wallpaper_service (WallpaperService, optional): 壁紙サービス。Noneの場合は自動生成。
            parent (QObject, optional): 親オブジェクト。デフォルトはNone。
        """
        super().__init__(parent)

        # WallpaperServiceの初期化
        self._wallpaper_service = wallpaper_service or WallpaperService()

        # 状態管理
        self._current_theme = "simple"
        self._is_updating = False
        self._current_worker = None
        self._preview_worker = None
        self._thread_pool = QThreadPool.globalInstance()
        self._background_image_path = None

        # プレビューデバウンスタイマー（300ms待ってから生成開始）
        self._preview_debounce_timer = QTimer(self)
        self._preview_debounce_timer.setSingleShot(True)
        self._preview_debounce_timer.setInterval(300)
        self._preview_debounce_timer.timeout.connect(self._on_preview_debounce_timeout)
        self._pending_preview_theme = None

        # 自動更新タイマー
        from src.config import AUTO_UPDATE_INTERVAL_MINUTES
        self._auto_update_timer = QTimer(self)
        self._auto_update_timer.setInterval(AUTO_UPDATE_INTERVAL_MINUTES * 60 * 1000)
        self._auto_update_timer.timeout.connect(self._on_auto_update_timeout)

        # リトライ設定
        from src.config import RETRY_MAX_COUNT, RETRY_INTERVAL_MINUTES
        self._retry_count = 0
        self._max_retries = RETRY_MAX_COUNT
        self._retry_timer = QTimer(self)
        self._retry_timer.setSingleShot(True)
        self._retry_timer.setInterval(RETRY_INTERVAL_MINUTES * 60 * 1000)
        self._retry_timer.timeout.connect(self._on_retry_timeout)

        # 認証エラー検出キーワード
        self._auth_error_keywords = ["認証", "401", "403", "unauthorized", "forbidden"]

        # スリープ復帰検知タイマー
        from src.config import SLEEP_CHECK_INTERVAL_SECONDS
        self._sleep_check_timer = QTimer(self)
        self._sleep_check_timer.setInterval(SLEEP_CHECK_INTERVAL_SECONDS * 1000)
        self._sleep_check_timer.timeout.connect(self._on_sleep_check)
        self._last_check_time = datetime.now()

        # 日付変更検知
        self._last_seen_date = datetime.now().date()
        self._midnight_timer = QTimer(self)
        self._midnight_timer.setSingleShot(True)
        self._midnight_timer.timeout.connect(self._on_midnight_timeout)

        # 現在時刻インジケーター更新タイマー（週間カレンダーの「今の時刻」ラインを定期更新）
        from src.config import TIME_INDICATOR_REFRESH_MINUTES
        self._time_indicator_timer = QTimer(self)
        self._time_indicator_timer.setInterval(TIME_INDICATOR_REFRESH_MINUTES * 60 * 1000)
        self._time_indicator_timer.timeout.connect(self._on_time_indicator_timeout)

        logger.info("MainViewModelを初期化しました")

    @property
    def retry_count(self) -> int:
        """現在のリトライ回数"""
        return self._retry_count

    @property
    def max_retries(self) -> int:
        """最大リトライ回数"""
        return self._max_retries

    @property
    def current_theme(self) -> str:
        """現在のテーマを取得"""
        return self._current_theme

    @property
    def is_updating(self) -> bool:
        """更新中かどうかを取得"""
        return self._is_updating

    def get_available_themes(self) -> List[str]:
        """
        利用可能なテーマのリストを取得

        Returns:
            List[str]: テーマ名のリスト
        """
        try:
            themes = self._wallpaper_service.get_available_themes()
            logger.debug(f"利用可能なテーマ: {themes}")
            return themes
        except Exception as e:
            logger.error(f"テーマ取得エラー: {e}")
            return []

    def set_theme(self, theme_name: str):
        """
        テーマを変更（壁紙は自動適用しない）

        プレビュー→適用ワークフロー対応: テーマ変更時は壁紙を即座に変更せず、
        ユーザーが明示的にapply_wallpaper()を呼ぶまで適用しない。

        Args:
            theme_name (str): 新しいテーマ名
        """
        # 入力検証: None チェック
        if theme_name is None:
            error_msg = "テーマ名が None です"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        # 入力検証: 空文字列チェック
        if not theme_name or theme_name.strip() == "":
            error_msg = "テーマ名が空です"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        # 入力検証: 利用可能なテーマかチェック
        available_themes = self.get_available_themes()
        if theme_name not in available_themes:
            error_msg = f"無効なテーマ名です: {theme_name}。利用可能なテーマ: {', '.join(available_themes)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        # テーマ変更（壁紙は自動適用しない）
        if self._current_theme != theme_name:
            self._current_theme = theme_name
            self.theme_changed.emit(theme_name)
            logger.info(f"テーマを変更しました: {theme_name}")

    def update_wallpaper(self) -> bool:
        """
        壁紙を更新（非同期実行）

        WallpaperServiceが内部でCalendarClientを使用してイベントを取得します。

        Returns:
            bool: ワーカーの起動に成功した場合True、失敗した場合False
        """
        # 同時更新の防止
        if self._is_updating:
            logger.warning("既に更新中です")
            return False

        try:
            self._is_updating = True
            worker_service = self._create_worker_service()

            # WallpaperWorkerを作成
            self._current_worker = WallpaperWorker(
                worker_service,
                self._current_theme
            )

            # シグナルを接続
            self._current_worker.signals.started.connect(self._on_worker_started)
            self._current_worker.signals.progress.connect(self._on_worker_progress)
            self._current_worker.signals.finished.connect(self._on_worker_finished)
            self._current_worker.signals.error.connect(self._on_worker_error)
            self._current_worker.signals.result.connect(self._on_worker_result)

            # QThreadPoolで実行
            self._thread_pool.start(self._current_worker)

            logger.info("壁紙更新ワーカーを起動しました")
            return True

        except Exception as e:
            logger.error(f"壁紙更新ワーカー起動エラー: {e}")
            self.error_occurred.emit(str(e))
            self._is_updating = False
            return False

    def cancel_update(self):
        """壁紙更新をキャンセル"""
        if self._current_worker:
            self._current_worker.cancel()
            logger.info("壁紙更新のキャンセルを要求しました")

    def _on_worker_started(self):
        """ワーカー開始時の処理"""
        self.update_started.emit()
        logger.debug("ワーカーが開始されました")

    def _on_worker_progress(self, value: int):
        """ワーカー進捗更新時の処理"""
        self.progress_updated.emit(value)
        logger.debug(f"進捗: {value}%")

    def _on_worker_finished(self):
        """ワーカー終了時の処理"""
        self._is_updating = False
        self._current_worker = None
        logger.debug("ワーカーが終了しました")

    def _on_worker_error(self, error_message: str):
        """ワーカーエラー時の処理"""
        self.error_occurred.emit(error_message)
        logger.error(f"ワーカーエラー: {error_message}")

        # 認証エラーの場合、キャッシュ壁紙にフォールバック＆自動更新停止
        if self._is_auth_error(error_message):
            self._fallback_to_cache()
            if self.is_auto_updating:
                self.stop_auto_update()
                logger.warning(f"認証エラーにより自動更新を停止しました: {error_message}")

    def _is_auth_error(self, error_message: str) -> bool:
        """エラーメッセージが認証エラーかどうかを判定"""
        lower_msg = error_message.lower()
        return any(keyword in lower_msg for keyword in self._auth_error_keywords)

    def _fallback_to_cache(self):
        """キャッシュ壁紙にフォールバック"""
        cached = self._wallpaper_service.get_cached_wallpaper()
        if cached:
            result = self._wallpaper_service.set_wallpaper(cached)
            if result:
                logger.info(f"キャッシュ壁紙にフォールバックしました: {cached}")
            else:
                logger.warning("キャッシュ壁紙の設定に失敗しました")
        else:
            logger.warning("キャッシュ壁紙が見つかりません")

    def _on_worker_result(self, success: bool):
        """ワーカー結果時の処理"""
        self.update_completed.emit(success)
        self.wallpaper_updated.emit(success)

        if success:
            self._retry_count = 0
            logger.info("壁紙を更新しました")
        else:
            logger.warning("壁紙の更新に失敗しました")
            self._schedule_retry()

    def _schedule_retry(self):
        """失敗時のリトライをスケジュール"""
        # 自動更新が無効の場合はリトライしない
        if not self.is_auto_updating:
            return

        if self._retry_count >= self._max_retries:
            self.error_occurred.emit(
                f"壁紙更新に{self._max_retries}回連続で失敗しました。次回の自動更新まで待機します。"
            )
            logger.error(f"リトライ上限到達: {self._retry_count}/{self._max_retries}")
            return

        self._retry_count += 1
        self._retry_timer.start()
        logger.info(f"リトライをスケジュールしました: {self._retry_count}/{self._max_retries}")

    def _on_retry_timeout(self):
        """リトライタイマー発火: 壁紙更新を再実行"""
        logger.info(f"リトライ実行: {self._retry_count}/{self._max_retries}")
        self.update_wallpaper()

    def generate_preview(self) -> Optional[Path]:
        """
        プレビュー画像を生成

        WallpaperServiceが内部でCalendarClientを使用してイベントを取得します。

        Returns:
            Optional[Path]: 生成されたプレビュー画像のパス。失敗した場合はNone。
        """
        try:
            # プレビュー画像を生成（壁紙は設定しない）
            # WallpaperServiceが内部でCalendarClientを使ってイベント取得
            if getattr(type(self._wallpaper_service), "generate_preview", None):
                preview_path = self._wallpaper_service.generate_preview(
                    theme_name=self._current_theme
                )
            else:
                preview_path = self._wallpaper_service.generate_wallpaper(
                    theme_name=self._current_theme
                )

            logger.info(f"プレビュー画像を生成しました: {preview_path}")
            return preview_path

        except Exception as e:
            logger.error(f"プレビュー生成エラー: {e}")
            self.error_occurred.emit(str(e))
            return None

    def preview_theme(self, theme_name: str):
        """
        指定テーマのプレビュー画像を非同期生成（壁紙は設定しない）

        デバウンス付き: 300ms以内の連続呼び出しは最後の1回のみ実行。
        UIスレッドをブロックしません。

        Args:
            theme_name (str): プレビューするテーマ名
        """
        # 実行中のプレビューワーカーをキャンセル
        if self._preview_worker:
            self._preview_worker.cancel()

        # デバウンス: テーマ名を保存してタイマーリスタート
        self._pending_preview_theme = theme_name
        self._preview_debounce_timer.start()

    def _on_preview_debounce_timeout(self):
        """デバウンスタイマー発火: 実際にプレビュー生成を開始"""
        theme_name = self._pending_preview_theme
        if not theme_name:
            return

        try:
            preview_service = self._create_worker_service()
            self._preview_worker = PreviewWorker(
                preview_service,
                theme_name
            )
            self._preview_worker.signals.preview_ready.connect(self._on_preview_result)
            self._preview_worker.signals.error.connect(self._on_preview_error)
            self._thread_pool.start(self._preview_worker)
            logger.info(f"プレビューワーカーを起動: {theme_name}")

        except Exception as e:
            logger.error(f"プレビューワーカー起動エラー: {e}")
            self.error_occurred.emit(str(e))

    def _on_preview_result(self, preview_path):
        """プレビュー生成完了時の処理"""
        self._preview_worker = None
        self.preview_ready.emit(preview_path)
        logger.info(f"プレビュー画像を生成しました: {preview_path}")

    def _on_preview_error(self, error_message: str):
        """プレビュー生成エラー時の処理"""
        self._preview_worker = None
        self.error_occurred.emit(error_message)
        logger.error(f"プレビュー生成エラー: {error_message}")

    def _create_worker_service(self):
        """
        ワーカー専用の WallpaperService を作成する。
        実サービス利用時はインスタンスを分離し、テスト用Mockでは既存参照を返す。
        """
        is_real_service = (
            self._wallpaper_service.__class__.__name__ == "WallpaperService"
            and self._wallpaper_service.__class__.__module__.endswith("viewmodels.wallpaper_service")
        )
        if not is_real_service:
            return self._wallpaper_service

        service = WallpaperService()
        try:
            if self._background_image_path:
                service.set_background_image(self._background_image_path)
            crop_position = getattr(self._wallpaper_service.image_generator, "crop_position", None)
            if crop_position:
                service.set_crop_position(crop_position)
        except Exception as e:
            logger.warning(f"ワーカー専用サービス初期化で一部設定を引き継げませんでした: {e}")
        return service

    def apply_wallpaper(self) -> bool:
        """
        現在のテーマで壁紙を生成して適用（非同期実行）

        プレビュー確認後にユーザーが明示的に呼び出すメソッド。

        Returns:
            bool: ワーカーの起動に成功した場合True、失敗した場合False
        """
        return self.update_wallpaper()

    # === 背景画像管理 ===

    @property
    def background_image_path(self) -> Optional[Path]:
        """カスタム背景画像パスを取得"""
        return self._background_image_path

    ALLOWED_BG_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
    MAX_BG_FILE_SIZE_MB = 50

    def set_background_image(self, path: Path):
        """
        カスタム背景画像パスを設定（バリデーション付き）

        Args:
            path: 背景画像のパス
        """
        # ファイル存在確認
        if not path.exists():
            error_msg = f"ファイルが見つかりません: {path}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        # 拡張子チェック
        if path.suffix.lower() not in self.ALLOWED_BG_EXTENSIONS:
            error_msg = f"非対応の画像形式です: {path.suffix}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        # ファイルサイズチェック
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.MAX_BG_FILE_SIZE_MB:
            error_msg = f"ファイルが大きすぎます: {file_size_mb:.1f}MB（上限: {self.MAX_BG_FILE_SIZE_MB}MB）"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        self._background_image_path = path
        self._wallpaper_service.set_background_image(path)
        self.background_image_changed.emit(path)
        logger.info(f"背景画像を設定しました: {path}")

    def set_preset_background(self, filename: str):
        """
        プリセット背景画像を設定

        Args:
            filename: プリセット画像のファイル名（例: 'sky.png'）
        """
        from src.config import BACKGROUNDS_DIR
        path = BACKGROUNDS_DIR / filename
        if not path.exists():
            error_msg = f"プリセット背景が見つかりません: {filename}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return

        self._background_image_path = path
        self._wallpaper_service.set_background_image(path)
        self.background_image_changed.emit(path)
        logger.info(f"プリセット背景画像を設定しました: {filename}")

    def reset_background_image(self):
        """背景画像をデフォルトプリセットに戻す"""
        from src.config import DEFAULT_PRESET_BACKGROUND
        self.set_preset_background(DEFAULT_PRESET_BACKGROUND)
        logger.info("背景画像をデフォルトプリセットに戻しました")

    def set_crop_position(self, position: str):
        """背景画像のクロップ位置を設定"""
        self._wallpaper_service.set_crop_position(position)
        logger.info(f"クロップ位置を '{position}' に設定しました")

    # === 自動更新機能 ===

    @property
    def is_auto_updating(self) -> bool:
        """自動更新が有効かどうかを取得"""
        return self._auto_update_timer.isActive()

    @property
    def auto_update_interval_minutes(self) -> int:
        """自動更新間隔（分）を取得"""
        return self._auto_update_timer.interval() // (60 * 1000)

    def start_auto_update(self):
        """自動更新を開始"""
        self._auto_update_timer.start()
        self._sleep_check_timer.start()
        self._time_indicator_timer.start()
        self._last_check_time = datetime.now()
        self._last_seen_date = datetime.now().date()
        self._schedule_midnight_timer()
        self.auto_update_status_changed.emit(True)
        logger.info("自動更新を開始しました")

    def stop_auto_update(self):
        """自動更新を停止"""
        self._auto_update_timer.stop()
        self._sleep_check_timer.stop()
        self._time_indicator_timer.stop()
        self._midnight_timer.stop()
        self.auto_update_status_changed.emit(False)
        logger.info("自動更新を停止しました")

    def set_auto_update_interval(self, minutes: int):
        """
        自動更新間隔を変更

        Args:
            minutes: 更新間隔（分）
        """
        interval_ms = minutes * 60 * 1000
        self._auto_update_timer.setInterval(interval_ms)
        logger.info(f"自動更新間隔を {minutes} 分に設定しました")

    def get_next_update_time(self) -> Optional[str]:
        """
        次回更新時刻を文字列で取得

        Returns:
            次回更新時刻の文字列（HH:MM形式）。停止中はNone。
        """
        if not self._auto_update_timer.isActive():
            return None

        from datetime import datetime, timedelta
        remaining_ms = self._auto_update_timer.remainingTime()
        next_time = datetime.now() + timedelta(milliseconds=remaining_ms)
        return next_time.strftime("%H:%M")

    def on_settings_changed(self, settings: dict):
        """
        設定変更を反映

        Args:
            settings: 変更された設定の辞書
        """
        if "auto_update_interval_minutes" in settings:
            self.set_auto_update_interval(settings["auto_update_interval_minutes"])

        if "auto_update_enabled" in settings:
            if settings["auto_update_enabled"]:
                self.start_auto_update()
            else:
                self.stop_auto_update()

    def _on_auto_update_timeout(self):
        """自動更新タイマーのタイムアウト処理"""
        logger.info("自動更新タイマーが発火しました")
        self.update_wallpaper()

    def _on_time_indicator_timeout(self):
        """現在時刻インジケーター更新タイマーのタイムアウト処理（週間カレンダーの時刻ラインを更新）"""
        logger.debug("現在時刻リフレッシュタイマーが発火しました")
        self.update_wallpaper()

    def _on_sleep_check(self):
        """
        スリープ復帰検知 + 日付変更検知のチェック処理

        前回チェック時刻から大幅に時間が経過している場合（>2分）、
        スリープから復帰したと判定し、即座に壁紙更新を実行する。
        また、日付が変わっていた場合もバックアップとして壁紙更新を行う。
        """
        from src.config import SLEEP_WAKE_THRESHOLD_SECONDS

        current_time = datetime.now()
        elapsed_seconds = (current_time - self._last_check_time).total_seconds()
        triggered = False

        if elapsed_seconds > SLEEP_WAKE_THRESHOLD_SECONDS:
            # スリープ復帰検知
            logger.info(f"スリープ復帰を検知しました（経過時間: {elapsed_seconds:.1f}秒）")
            if self.is_auto_updating:
                logger.info("スリープ復帰により即座に壁紙更新を実行します")
                self.update_wallpaper()
                triggered = True
                # スリープ復帰時はmidnight timerも再スケジュール
                self._schedule_midnight_timer()

        # 日付変更検知（バックアップ）
        current_date = current_time.date()
        if current_date != self._last_seen_date:
            logger.info(f"日付変更を検知: {self._last_seen_date} → {current_date}")
            self._last_seen_date = current_date
            if self.is_auto_updating:
                self._schedule_midnight_timer()
                if not triggered:
                    logger.info("日付変更により壁紙更新を実行します")
                    self.update_wallpaper()

        # 最後のチェック時刻を更新
        self._last_check_time = current_time

    def _schedule_midnight_timer(self):
        """次の0:00:01に発火するようmidnight timerをスケジュール

        0:00:00ではなく0:00:01にすることで、日付境界を確実に跨いだ後に
        datetime.now().date() が新しい日付を返すことを保証する。
        """
        now = datetime.now()
        tomorrow = now.replace(hour=0, minute=0, second=1, microsecond=0) + timedelta(days=1)
        ms_until_midnight = int((tomorrow - now).total_seconds() * 1000)
        # 異常値の防御: 最小1秒、最大24時間+1秒にclamp
        ms_until_midnight = max(1000, min(ms_until_midnight, 86_401_000))
        self._midnight_timer.start(ms_until_midnight)
        logger.debug(f"midnight timerをスケジュール: {ms_until_midnight}ms後")

    def _on_midnight_timeout(self):
        """midnight timer発火: 日付変更により壁紙更新"""
        logger.info("midnight timerが発火しました — 日付変更検知")
        self._last_seen_date = datetime.now().date()
        self._schedule_midnight_timer()

        if self.is_auto_updating:
            self.update_wallpaper()

    def cleanup(self):
        """リソースの解放（タイマー停止等）"""
        if self._auto_update_timer.isActive():
            self._auto_update_timer.stop()
        if self._retry_timer.isActive():
            self._retry_timer.stop()
        if self._sleep_check_timer.isActive():
            self._sleep_check_timer.stop()
        if self._time_indicator_timer.isActive():
            self._time_indicator_timer.stop()
        if self._midnight_timer.isActive():
            self._midnight_timer.stop()
        if self._preview_debounce_timer.isActive():
            self._preview_debounce_timer.stop()
        if self._current_worker:
            self._current_worker.cancel()
        if self._preview_worker:
            self._preview_worker.cancel()
        logger.info("MainViewModelのリソースを解放しました")
