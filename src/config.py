"""
設定ファイル
アプリケーションの動作を制御する設定値を定義
"""
import os
from pathlib import Path

# プロジェクトルートディレクトリ
BASE_DIR = Path(__file__).parent.parent

# === 画像設定 ===
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
BACKGROUND_COLOR = (255, 255, 255)  # 白背景（シンプル・ミニマル）
TEXT_COLOR = (0, 0, 0)  # 黒文字

# === フォント設定 ===
# システムにインストールされている日本語フォントのパスを指定
# 見つからない場合はデフォルトフォントが使用されます
FONT_PATHS = {
    'Darwin': [  # Mac
        '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
        '/System/Library/Fonts/Hiragino Sans GB.ttc',
    ],
    'Windows': [  # Windows
        'C:\\Windows\\Fonts\\meiryo.ttc',
        'C:\\Windows\\Fonts\\YuGothM.ttc',
    ],
    'Linux': [  # Linux
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    ]
}

# フォントサイズ
FONT_SIZE_TITLE = 60  # タイトル（日付）
FONT_SIZE_SECTION = 40  # セクション見出し
FONT_SIZE_EVENT = 32  # イベント詳細

# === カラー設定 ===
# Google Calendarのカラーマッピング（色分け表示用）
DEFAULT_EVENT_COLORS = {
    '1': (121, 134, 203),  # ラベンダー
    '2': (51, 182, 121),   # セージ
    '3': (142, 124, 195),  # ブドウ
    '4': (230, 124, 115),  # フラミンゴ
    '5': (246, 191, 38),   # バナナ
    '6': (244, 145, 65),   # タンジェリン
    '7': (3, 155, 229),    # ピーコック
    '8': (97, 97, 97),     # グラファイト
    '9': (63, 81, 181),    # ブルーベリー
    '10': (11, 128, 67),   # バジル
    '11': (213, 0, 0),     # トマト
}

# === Google Calendar API設定 ===
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CREDENTIALS_PATH = BASE_DIR / 'credentials' / 'credentials.json'
TOKEN_PATH = BASE_DIR / 'credentials' / 'token.json'

# カレンダーID（複数指定可能）
# 'primary'は主カレンダー、その他のカレンダーIDも追加可能
CALENDAR_IDS = [
    'primary',
    # 'your-calendar-id@group.calendar.google.com',  # 追加のカレンダー
]

# === 出力設定 ===
OUTPUT_DIR = BASE_DIR / 'output'
WALLPAPER_FILENAME_TEMPLATE = 'wallpaper_{date}.png'

# === スケジュール設定 ===
# 壁紙更新時刻（24時間形式）
UPDATE_TIME = '06:00'

# 通知設定
NOTIFICATION_ADVANCE_MINUTES = 30  # 予定開始何分前に通知するか

# === レイアウト設定 ===
# 余白とレイアウト
MARGIN_TOP = 100
MARGIN_LEFT = 100
MARGIN_RIGHT = 100
LINE_HEIGHT = 50
SECTION_SPACING = 80

# カラーバーの設定
COLOR_BAR_WIDTH = 6
COLOR_BAR_HEIGHT = 30
COLOR_BAR_OFFSET = 20

# === 新デザイン: レイアウト設定（最適化版） ===

# 空白エリア（デスクトップアイコン用）
DESKTOP_ICON_AREA_HEIGHT = 180  # 固定値（パーセント指定から変更）
DESKTOP_ICON_LEFT_WIDTH_PERCENT = 20   # 左上20%
DESKTOP_ICON_RIGHT_WIDTH_PERCENT = 20  # 右上20%

# スペーシング設定
SPACING_TOP = 25          # デスクトップエリア〜カード間
SPACING_MIDDLE = 35       # カード〜週間カレンダー間

# 予定カード設定
CARD_WIDTH = 300
CARD_HEIGHT = 200         # 150 → 200（複数予定表示対応）
CARD_MARGIN = 30
CARD_PADDING = 15         # 20 → 15（スペース効率化）
FONT_SIZE_CARD_DATE = 16       # 「今日の予定」ラベル（18→16）
FONT_SIZE_CARD_TIME = 16       # 時刻（24→16）
FONT_SIZE_CARD_TITLE = 14      # タイトル（20→14）
FONT_SIZE_CARD_LOCATION = 12   # 場所（16→12）

# 週間カレンダー設定
WEEK_CALENDAR_START_HOUR = 7    # 7:00開始（6:00から変更）
WEEK_CALENDAR_END_HOUR = 23     # 23:00終了
HOUR_HEIGHT = 25                # 1時間あたりの高さ（38→25、動的計算の初期値）
DAY_COLUMN_WIDTH = 120          # 1日の列幅
FONT_SIZE_HOUR_LABEL = 11       # 時間ラベル（14→11）
FONT_SIZE_DAY_HEADER = 14       # 曜日ヘッダー（18→14）
FONT_SIZE_EVENT_BLOCK = 10      # イベントブロック内テキスト（12→10）

# カラーテーマ（将来的な拡張用）
THEME = 'white'  # 'white', 'light_grey', 'pastel_blue'

# === 背景画像設定 ===
# 背景画像を使用する場合は、画像ファイルのパスを指定
# None の場合は透明背景、パスを指定すると背景画像の上にカレンダーを描画
BACKGROUND_IMAGE_PATH = BASE_DIR / 'backgrounds' / 'default_background.png'
# BACKGROUND_IMAGE_PATH = None  # 透明背景の場合

# === ログ設定 ===
LOG_LEVEL = 'INFO'
LOG_FILE = BASE_DIR / 'calendar_app.log'
