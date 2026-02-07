"""
テーマ設定定義
カレンダー壁紙のデザインテーマを定義
すべてのテーマで背景画像を流用し、UI要素のスタイルのみ変更
"""

THEMES = {
    # シンプル系テーマ（現在のデザイン）
    'simple': {
        'text_color': (0, 0, 0),  # 黒文字
        'card_bg': (255, 255, 255),  # カード背景（白）
        'card_alpha': 255,  # 不透明（0-255）
        'card_border': (200, 200, 200),  # カード枠（グレー）
        'card_border_width': 1,  # 枠線の太さ
        'card_radius': 0,  # 角丸なし
        'card_shadow': False,  # 影なし
        'grid_color': (220, 220, 220),  # グリッド線（薄いグレー）
        'accent_color': None,  # アクセントカラーなし
        'hour_label_color': (0, 0, 0),  # 時刻ラベル色（黒）
        'hour_label_bg': (255, 255, 255, 180),  # 時刻ラベル背景（半透明白）
        'active_card_bg': (255, 245, 245),  # 進行中カード背景（薄い赤）
        'active_card_border': (220, 50, 50),  # 進行中枠色（赤）
        'active_card_border_width': 3,  # 進行中枠線幅
        'active_text_color': (180, 30, 30),  # 進行中テキスト色（濃い赤）
        'current_time_highlight': (255, 255, 100, 60),  # 蛍光黄（半透明）
        'header_bg': (255, 255, 255, 160),  # ヘッダー背景（半透明白）
        'event_colors': {
            '1': (121, 134, 203),  # ラベンダー
            '2': (51, 182, 121),   # セージ
            '3': (142, 124, 195),  # ブドウ
            '4': (230, 124, 115),  # フラミンゴ
            '5': (246, 191, 38),   # バナナ
        }
    },

    # モダン系テーマ
    'modern': {
        'text_color': (51, 51, 51),  # ダークグレー
        'card_bg': (255, 255, 255),  # カード背景（白）
        'card_alpha': 217,  # 85%透明度（255 * 0.85 = 217）
        'card_border': (200, 200, 200),  # カード枠（グレー）
        'card_border_width': 1,  # 枠線の太さ
        'card_radius': 15,  # 大きめの角丸
        'card_shadow': True,  # 影あり
        'grid_color': (200, 200, 200),  # グリッド線
        'accent_color': (0, 122, 255),  # アクセント（Apple Blue）
        'hour_label_color': (51, 51, 51),  # 時刻ラベル色（ダークグレー）
        'hour_label_bg': (255, 255, 255, 200),  # 時刻ラベル背景（半透明白）
        'hour_label_radius': 8,  # 時刻ラベル背景の角丸
        'active_card_bg': (255, 240, 240),  # 進行中カード背景
        'active_card_border': (0, 122, 255),  # 進行中枠色（Apple Blue）
        'active_card_border_width': 3,
        'active_text_color': (0, 80, 180),  # 進行中テキスト色
        'current_time_highlight': (100, 200, 255, 50),  # 蛍光ブルー（半透明）
        'header_bg': (255, 255, 255, 180),  # ヘッダー背景（半透明白、すりガラス風）
        'glass_effect': True,  # ガラスモーフィズム有効
        'glass_blur_radius': 15,  # ぼかし半径
        'glass_tint': (255, 255, 255, 50),  # 白い着色（RGBA）
        'chromatic_offset': 1,  # RGB色相分離オフセット（控えめ）
        'event_colors': {
            '1': (66, 133, 244),   # Google Blue
            '2': (52, 168, 83),    # Google Green
            '3': (156, 39, 176),   # パープル
            '4': (234, 67, 53),    # Google Red
            '5': (251, 188, 4),    # Google Yellow
        }
    },

    # パステル系テーマ
    'pastel': {
        'text_color': (51, 51, 51),  # ダークグレー
        'event_text_color': (30, 30, 30),  # イベントブロック内テキスト（黒に近い）
        'card_bg': (255, 240, 245),  # カード背景（淡いピンク）
        'card_alpha': 230,  # 90%透明度
        'card_border': (255, 192, 203),  # カード枠（ピンク）
        'card_border_width': 2,  # 少し太めの枠線
        'card_radius': 10,  # 角丸あり
        'card_shadow': False,  # 影なし
        'grid_color': (200, 200, 200),  # グリッド線
        'accent_color': (255, 182, 193),  # アクセント（パステルピンク）
        'hour_label_color': (80, 60, 80),  # 時刻ラベル色（落ち着いたパープル系）
        'hour_label_bg': (255, 240, 245, 190),  # 時刻ラベル背景（半透明ピンク）
        'active_card_bg': (255, 228, 230),  # 進行中カード背景（パステルピンク）
        'active_card_border': (255, 105, 120),  # 進行中枠色（明るいコーラル）
        'active_card_border_width': 3,
        'active_text_color': (200, 50, 70),  # 進行中テキスト色
        'current_time_highlight': (255, 200, 220, 50),  # 蛍光ピンク（半透明）
        'header_bg': (255, 240, 245, 170),  # ヘッダー背景（半透明ピンク）
        # 週間カレンダーのイベントブロックもパステル調に
        'event_colors': {
            '1': (230, 230, 250),  # ラベンダー（薄く）
            '2': (176, 224, 230),  # パウダーブルー
            '3': (221, 160, 221),  # プラム
            '4': (255, 218, 185),  # ピーチパフ
            '5': (255, 250, 205),  # レモンシフォン
        }
    },

    # ダーク系テーマ
    'dark': {
        'text_color': (224, 224, 224),  # 白〜薄いグレー
        'card_bg': (45, 45, 45),  # カード背景（濃いグレー）
        'card_alpha': 179,  # 70%透明度（255 * 0.7 = 179）
        'card_border': (255, 215, 0),  # カード枠（ゴールド）
        'card_border_width': 2,  # 目立つ枠線
        'card_radius': 5,  # 小さい角丸
        'card_shadow': True,  # 影あり
        'grid_color': (100, 100, 100),  # グリッド線（ダークグレー）
        'accent_color': (255, 215, 0),  # アクセント（ゴールド）
        'hour_label_color': (200, 200, 200),  # 時刻ラベル色（明るいグレー）
        'hour_label_bg': (30, 30, 30, 200),  # 時刻ラベル背景（半透明ダーク）
        'active_card_bg': (80, 30, 30),  # 進行中カード背景（ダーク赤）
        'active_card_border': (255, 80, 80),  # 進行中枠色（明るい赤）
        'active_card_border_width': 3,
        'active_text_color': (255, 200, 200),  # 進行中テキスト色（薄いピンク）
        'current_time_highlight': (255, 200, 50, 40),  # 蛍光ゴールド（半透明）
        'header_bg': (30, 30, 30, 180),  # ヘッダー背景（半透明ダーク）
        'glass_effect': True,  # ガラスモーフィズム有効
        'glass_blur_radius': 12,  # ぼかし半径
        'glass_tint': (20, 20, 30, 60),  # 暗い着色（RGBA）
        'event_colors': {
            '1': (100, 149, 237),  # コーンフラワーブルー
            '2': (72, 209, 132),   # ミントグリーン
            '3': (186, 130, 245),  # ライトパープル
            '4': (255, 107, 107),  # サーモンレッド
            '5': (255, 215, 64),   # ゴールドイエロー
        }
    },

    # 鮮やか系テーマ
    'vibrant': {
        'text_color': (255, 255, 255),  # 白
        'card_bg': (25, 25, 50),  # カード背景（ダークネイビー、イベント色が映える）
        'card_alpha': 220,  # 86%透明度
        'card_border': (60, 60, 100),  # カード枠（暗いブルーグレー）
        'card_border_width': 2,  # 太めの枠線
        'card_radius': 12,  # 角丸あり
        'card_shadow': True,  # 影あり
        'grid_color': (70, 70, 100),  # グリッド線（ダークブルーグレー）
        'accent_color': (255, 149, 0),  # アクセント（オレンジ）
        'hour_label_color': (220, 220, 255),  # 時刻ラベル色（薄いブルーホワイト）
        'hour_label_bg': (30, 30, 60, 200),  # 時刻ラベル背景（半透明ダークネイビー）
        'active_card_bg': (200, 50, 0),  # 進行中カード背景（鮮やかなオレンジ赤）
        'active_card_border': (255, 100, 50),  # 進行中枠色（オレンジ）
        'active_card_border_width': 3,
        'active_text_color': (255, 255, 200),  # 進行中テキスト色（明るい黄）
        'current_time_highlight': (255, 149, 0, 50),  # 蛍光オレンジ（半透明）
        'header_bg': (20, 20, 45, 200),  # ヘッダー背景（半透明ダークネイビー）
        'chromatic_offset': 2,  # RGB色相分離オフセット（やや強め）
        'event_colors': {
            '1': (66, 165, 255),   # スカイブルー（明るく）
            '2': (0, 230, 118),    # ネオングリーン
            '3': (234, 128, 252),  # ネオンパープル
            '4': (255, 82, 82),    # ブライトレッド
            '5': (255, 213, 79),   # ブライトイエロー
        }
    }
}


# テーマのデフォルト値（全テーマ共通のフォールバック）
# 各テーマで未定義のキーはこの値が使用される
DEFAULT_THEME = {
    'text_color': (0, 0, 0),
    'card_bg': (255, 255, 255),
    'card_alpha': 255,
    'card_border': (200, 200, 200),
    'card_border_width': 1,
    'card_radius': 0,
    'card_shadow': False,
    'grid_color': (220, 220, 220),
    'accent_color': None,
    'hour_label_color': (0, 0, 0),
    'hour_label_bg': (255, 255, 255, 180),
    'hour_label_radius': 0,
    'active_card_bg': (255, 245, 245),
    'active_card_border': (220, 50, 50),
    'active_card_border_width': 3,
    'active_text_color': (180, 30, 30),
    'current_time_highlight': (255, 255, 100, 60),
    'header_bg': None,
    'glass_effect': False,
    'glass_blur_radius': 15,
    'glass_tint': (255, 255, 255, 50),
    'glass_border_color': (255, 255, 255, 77),
    'chromatic_offset': 0,
    'event_text_color': (255, 255, 255),
    'event_colors': {
        '1': (121, 134, 203),
        '2': (51, 182, 121),
        '3': (142, 124, 195),
        '4': (230, 124, 115),
        '5': (246, 191, 38),
    }
}


def get_theme(theme_name: str) -> dict:
    """
    テーマ名からテーマ設定を取得

    Args:
        theme_name: テーマ名（'simple', 'modern', 'pastel', 'dark', 'vibrant'）

    Returns:
        dict: テーマ設定辞書

    Raises:
        ValueError: 存在しないテーマ名の場合
    """
    if theme_name not in THEMES:
        raise ValueError(
            f"テーマ '{theme_name}' は存在しません。"
            f"利用可能なテーマ: {', '.join(THEMES.keys())}"
        )
    return THEMES[theme_name]


def list_themes() -> list:
    """
    利用可能なテーマの一覧を取得

    Returns:
        list: テーマ名のリスト
    """
    return list(THEMES.keys())
