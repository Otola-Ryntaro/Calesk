"""
設定ファイル
アプリケーションの動作を制御する設定値を定義
"""
import os
import sys
from pathlib import Path

# プロジェクトルートディレクトリ
# PyInstaller バンドル内の場合は _MEIPASS を使用
if getattr(sys, 'frozen', False):
    # PyInstaller バンドル内での実行
    BASE_DIR = Path(sys._MEIPASS)
else:
    # 通常のPython実行
    BASE_DIR = Path(__file__).parent.parent

# === 画像設定 ===
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080
BACKGROUND_COLOR = (255, 255, 255)  # 白背景（シンプル・ミニマル）
TEXT_COLOR = (0, 0, 0)  # 黒文字

# === マルチディスプレイ設定 ===
# 壁紙を適用するデスクトップ番号
# 0 = 全デスクトップ
# 1 = desktop 1のみ（現在の設定 - 内蔵ディスプレイ/メインディスプレイ）
# 2 = desktop 2のみ（外部ディスプレイ）
WALLPAPER_TARGET_DESKTOP = 1

# 解像度の自動検出（True推奨）
AUTO_DETECT_RESOLUTION = True

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

# Bold用フォントパス（時刻表示など強調部分に使用）
FONT_PATHS_BOLD = {
    'Darwin': [  # Mac
        '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
        '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
    ],
    'Windows': [  # Windows
        'C:\\Windows\\Fonts\\meiryob.ttc',
        'C:\\Windows\\Fonts\\YuGothB.ttc',
    ],
    'Linux': [  # Linux
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
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

# credentials は PyInstaller バンドルに含まれないため、
# ユーザーのホームディレクトリから読み込む
if getattr(sys, 'frozen', False):
    # PyInstaller バンドル内での実行 - ユーザーのホームディレクトリを使用
    CREDENTIALS_DIR = Path.home() / '.calendar_wallpaper' / 'credentials'
    CREDENTIALS_PATH = CREDENTIALS_DIR / 'credentials.json'
    TOKEN_PATH = CREDENTIALS_DIR / 'token.json'
    CONFIG_DIR = Path.home() / '.calendar_wallpaper' / 'config'
else:
    # 開発環境 - プロジェクトディレクトリを使用
    CREDENTIALS_PATH = BASE_DIR / 'credentials' / 'credentials.json'
    TOKEN_PATH = BASE_DIR / 'credentials' / 'token.json'
    CONFIG_DIR = BASE_DIR / 'config'

# 複数アカウント設定ファイルパス
ACCOUNTS_CONFIG_PATH = CONFIG_DIR / 'accounts.json'

# カレンダーID（複数指定可能）
# 'primary'は主カレンダー、その他のカレンダーIDも追加可能
CALENDAR_IDS = [
    'primary',
    # 'your-calendar-id@group.calendar.google.com',  # 追加のカレンダー
]

# === 出力設定 ===
OUTPUT_DIR = BASE_DIR / 'output'
WALLPAPER_FILENAME_TEMPLATE = 'wallpaper_{theme}_{date}.png'

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
DESKTOP_ICON_AREA_HEIGHT = 90   # 固定値、上部余白削減
DESKTOP_ICON_LEFT_WIDTH_PERCENT = 20   # 左上20%
DESKTOP_ICON_RIGHT_WIDTH_PERCENT = 20  # 右上20%

# スペーシング設定
SPACING_TOP = 25          # デスクトップエリア〜カード間
SPACING_MIDDLE = 35       # カード〜週間カレンダー間

# 予定カード設定（旧レイアウト用、互換性維持）
CARD_WIDTH = 300
CARD_HEIGHT = 200         # 150 → 200（複数予定表示対応）
CARD_MARGIN = 30
CARD_PADDING = 15         # 20 → 15（スペース効率化）
FONT_SIZE_CARD_DATE = 16       # 「今日の予定」ラベル（18→16）
FONT_SIZE_CARD_TIME = 16       # 時刻（24→16）
FONT_SIZE_CARD_TITLE = 14      # タイトル（20→14）
FONT_SIZE_CARD_LOCATION = 12   # 場所（16→12）

# 3列レイアウト用コンパクトカード設定
COMPACT_CARD_WIDTH = 260       # コンパクトカード幅
COMPACT_CARD_HEIGHT = 50       # コンパクトカード高さ
COMPACT_CARD_MARGIN = 5        # カード間余白
COMPACT_CARD_PADDING = 8       # カード内余白
MAX_CARDS_PER_COLUMN = 3       # 列あたり最大表示件数
COLUMN_HEADER_HEIGHT = 25      # 列ヘッダー高さ
COLUMN_GAP = 20                # 列間余白

# 週間カレンダー設定
WEEK_CALENDAR_START_HOUR = 8    # 8:00開始
WEEK_CALENDAR_END_HOUR = 22     # 22:00終了
HOUR_HEIGHT = 27                # 1時間あたりの高さ（18pxの1.5倍、視認性重視）
DAY_COLUMN_WIDTH = 120          # 1日の列幅
FONT_SIZE_HOUR_LABEL = 12       # 時間ラベル（視認性向上）
FONT_SIZE_DAY_HEADER = 16       # 曜日ヘッダー（視認性向上）
FONT_SIZE_EVENT_BLOCK = 11      # イベントブロック内テキスト（最初の文字が見えるように）

# === 時刻ラベル視認性設定 ===
# 週間カレンダーの時刻ラベルの描画モード
# 'label_bg': ラベル部分のみ半透明背景（デフォルト）
# 'full_bg': カレンダー全体に半透明背景
# 'outline': アウトライン付きテキスト（stroke）
# 'none': エフェクトなし（プレーンテキスト）
LABEL_VISIBILITY_MODES = ['label_bg', 'full_bg', 'outline', 'none']
LABEL_VISIBILITY_MODE = 'label_bg'

# === デザインテーマ設定 ===
# 利用可能なテーマ: 'simple', 'modern', 'pastel', 'dark', 'vibrant'
# - simple: シンプル系（背景画像使用、黒文字、角丸なし）
# - modern: モダン系（半透明白カード、大きめの角丸、影付き）
# - pastel: パステル系（淡い色、角丸あり、優しい印象）
# - dark: ダーク系（半透明黒カード、ゴールドアクセント、高級感）
# - vibrant: 鮮やか系（鮮やかな色、角丸あり、元気な印象）
THEME = 'simple'

# カードの影設定
CARD_SHADOW_ENABLED = True  # カードに影を表示するか（True: 表示、False: 非表示）

# === Google Calendar アイコン設定 ===
CALENDAR_ICON_PATH = BASE_DIR / 'assets' / 'google_calendar_icon.png'
CALENDAR_ICON_SIZE = (40, 40)  # アイコンサイズ（幅, 高さ）

# アイコン配置設定（OS別）
ICON_MAC_POSITION = (IMAGE_WIDTH - 60, 20)  # Mac: 上部右寄せ
ICON_WINDOWS_POSITION = (IMAGE_WIDTH - 60, IMAGE_HEIGHT - 60)  # Windows: 右下
ICON_LINUX_POSITION = (IMAGE_WIDTH - 60, 20)  # Linux: Mac同様

# === 背景画像設定 ===
# プリセット背景画像の定義（著作権フリー画像）
PRESET_BACKGROUNDS = [
    {"name": "青空", "file": "sky.png"},
    {"name": "ビーチ", "file": "beach.png"},
    {"name": "夕焼け", "file": "sunset.png"},
    {"name": "日本列島", "file": "japan.png"},
    {"name": "オーロラ", "file": "aurora.png"},
    {"name": "地球", "file": "earth.png"},
    {"name": "砂浜の夕日", "file": "beach_sunset.png"},
]
DEFAULT_PRESET_BACKGROUND = "sky.png"
BACKGROUNDS_DIR = BASE_DIR / 'backgrounds'
BACKGROUND_IMAGE_PATH = BACKGROUNDS_DIR / DEFAULT_PRESET_BACKGROUND

# 背景画像クロップ位置（center/top/bottom）
# center: 中央クロップ（デフォルト）
# top: 上寄せクロップ（空・風景向き）
# bottom: 下寄せクロップ（地面・水面向き）
BACKGROUND_CROP_POSITION = 'center'

# === 自動更新設定 ===
AUTO_UPDATE_INTERVAL_MINUTES = 60  # 自動更新間隔（分）
AUTO_UPDATE_ENABLED_DEFAULT = True  # デフォルトで自動更新を有効にする

# === リトライ設定 ===
RETRY_MAX_COUNT = 3       # 壁紙更新失敗時の最大リトライ回数
RETRY_INTERVAL_MINUTES = 5  # リトライ間隔（分）

# === スリープ復帰検知設定 ===
SLEEP_CHECK_INTERVAL_SECONDS = 60   # スリープ復帰チェック間隔（秒）
SLEEP_WAKE_THRESHOLD_SECONDS = 120  # スリープ復帰と判定する閾値（秒）

# === ログ設定 ===
LOG_LEVEL = 'INFO'
LOG_FILE = BASE_DIR / 'calendar_app.log'
