"""
Calesk - メインプログラム
Google Calendarの予定をデスクトップ壁紙として表示
"""
import sys
import logging
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.calendar_client import CalendarClient
from src.image_generator import ImageGenerator
from src.wallpaper_setter import WallpaperSetter
from src.notifier import Notifier
from src.scheduler import Scheduler
from src.config import LOG_FILE, LOG_LEVEL


def setup_logging(log_level: str = None) -> None:
    """
    ログ設定を初期化

    Args:
        log_level: ログレベル（DEBUG, INFO, WARNING, ERROR）
    """
    level = log_level or LOG_LEVEL

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logging.info("=== Calesk を起動 ===")


def update_wallpaper() -> bool:
    """
    壁紙を更新

    Returns:
        bool: 成功でTrue、失敗でFalse
    """
    try:
        # カレンダークライアントを初期化
        calendar_client = CalendarClient()

        # 認証
        if not calendar_client.authenticate():
            logging.error("Google Calendar API認証に失敗しました")
            return False

        # イベント取得
        today_events = calendar_client.get_today_events()
        week_events = calendar_client.get_week_events()

        logging.info(f"今日の予定: {len(today_events)}件")
        logging.info(f"今週の予定: {len(week_events)}件")

        # 画像生成
        generator = ImageGenerator()
        image_path = generator.generate_wallpaper(today_events, week_events)

        if not image_path:
            logging.error("壁紙画像の生成に失敗しました")
            return False

        # 壁紙設定
        setter = WallpaperSetter()
        if not setter.set_wallpaper(image_path):
            logging.error("壁紙の設定に失敗しました")
            return False

        # 更新通知
        notifier = Notifier()
        notifier.send_update_notification()

        logging.info("壁紙更新が完了しました")
        return True

    except Exception as e:
        logging.error(f"壁紙更新でエラーが発生: {e}", exc_info=True)
        return False


def check_notifications() -> None:
    """
    通知チェック
    """
    try:
        # カレンダークライアントを初期化
        calendar_client = CalendarClient()

        # 認証
        if not calendar_client.authenticate():
            return

        # 今日のイベント取得
        today_events = calendar_client.get_today_events()

        # 通知チェック
        notifier = Notifier()
        notifier.check_upcoming_events(today_events)

    except Exception as e:
        logging.error(f"通知チェックでエラーが発生: {e}")


def authenticate_only() -> bool:
    """
    認証のみを実行

    Returns:
        bool: 成功でTrue、失敗でFalse
    """
    logging.info("Google Calendar API認証を開始します...")

    calendar_client = CalendarClient()
    if calendar_client.authenticate():
        logging.info("認証が完了しました！")
        return True
    else:
        logging.error("認証に失敗しました")
        return False


def run_once() -> bool:
    """
    スケジュール実行せずに1回だけ実行

    Returns:
        bool: 成功でTrue、失敗でFalse
    """
    logging.info("手動実行モード: 壁紙を更新します...")
    success = update_wallpaper()

    if success:
        logging.info("手動実行が完了しました")
    else:
        logging.error("手動実行に失敗しました")

    return success


def run_daemon() -> None:
    """
    デーモンモードで実行（スケジュール実行）
    """
    logging.info("デーモンモード: スケジューラーを起動します...")

    # スケジューラーを初期化
    scheduler = Scheduler()
    scheduler.set_update_callback(update_wallpaper)
    scheduler.set_notification_callback(check_notifications)
    scheduler.schedule_tasks()

    # スケジューラーを開始（ブロッキング）
    scheduler.start()


def main() -> int:
    """
    メイン関数

    Returns:
        int: 終了コード（0=成功、1=失敗）
    """
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(
        description='Google Calendarの予定をデスクトップ壁紙として表示'
    )
    parser.add_argument(
        '--auth',
        action='store_true',
        help='Google Calendar API認証のみを実行'
    )
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='スケジュール実行せずに1回だけ実行'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='デーモンモードで実行（バックグラウンド定期実行）'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='ログレベルを指定'
    )

    args = parser.parse_args()

    # ログ設定
    setup_logging(args.log_level)

    try:
        # 認証のみ
        if args.auth:
            return 0 if authenticate_only() else 1

        # 1回のみ実行
        elif args.run_once:
            return 0 if run_once() else 1

        # デーモンモード
        elif args.daemon:
            run_daemon()
            return 0

        # 引数なし: デフォルトで1回実行
        else:
            logging.info("引数なしで実行されました。--help でヘルプを表示できます")
            logging.info("壁紙を更新します...")
            return 0 if run_once() else 1

    except KeyboardInterrupt:
        logging.info("\nプログラムを中断しました")
        return 0
    except Exception as e:
        logging.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
