"""
テーマ設定定義
Caleskのデザインテーマを定義
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
        'chromatic_offset': 0,  # RGB色相分離オフセット（無効化）
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
        'current_time_highlight': (255, 100, 140, 100),  # 濃いめのコーラルピンク（半透明）
        'header_bg': (255, 240, 245, 170),  # ヘッダー背景（半透明ピンク）
        # 週間カレンダーのイベントブロックもパステル調に（コントラスト改善版）
        'event_colors': {
            '1': (180, 180, 255),  # ラベンダー（濃いめ）
            '2': (120, 200, 230),  # スカイブルー（濃いめ）
            '3': (200, 130, 220),  # パープル（濃いめ）
            '4': (255, 180, 150),  # ピーチ（濃いめ）
            '5': (255, 220, 120),  # イエロー（濃いめ）
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
        'chromatic_offset': 0,  # RGB色相分離オフセット（無効化）
        'event_colors': {
            '1': (66, 165, 255),   # スカイブルー（明るく）
            '2': (0, 230, 118),    # ネオングリーン
            '3': (234, 128, 252),  # ネオンパープル
            '4': (255, 82, 82),    # ブライトレッド
            '5': (255, 213, 79),   # ブライトイエロー
        }
    },

    # Luxury系テーマ（高級感のあるミニマル）
    'luxury': {
        'text_color': (50, 40, 30),  # ディープブラウン（上品）
        'card_bg': (250, 248, 245),  # アイボリーホワイト
        'card_alpha': 240,  # 94%透明度（やや透け感）
        'card_border': (212, 175, 55),  # ゴールドアクセント
        'card_border_width': 1,  # 繊細な枠線
        'card_radius': 8,  # 控えめな角丸
        'card_shadow': True,  # 洗練された影
        'grid_color': (220, 210, 200),  # ベージュグレー
        'accent_color': (212, 175, 55),  # アクセント（ゴールド #D4AF37）
        'hour_label_color': (80, 70, 60),  # ディープブラウン
        'hour_label_bg': (250, 245, 240, 210),  # 半透明クリーム
        'hour_label_radius': 6,
        'active_card_bg': (255, 250, 240),  # クリーム
        'active_card_border': (212, 175, 55),  # ゴールド
        'active_card_border_width': 2,
        'active_text_color': (100, 80, 60),  # リッチブラウン
        'current_time_highlight': (212, 175, 55, 40),  # ゴールド（控えめ）
        'header_bg': (250, 245, 240, 200),  # クリーム背景
        'glass_effect': False,  # ガラス効果はオフ（マットな質感）
        'chromatic_offset': 0,  # 色相分離なし（シャープ）
        # グラデーション背景設定（無効化：背景は既存テーマと同じ）
        'background_gradient': {
            'enabled': False,
            'type': 'linear',
            'colors': [(250, 245, 240), (220, 200, 170)],
            'direction': 'vertical'
        },
        'event_colors': {
            '1': (100, 80, 150),   # ディープパープル
            '2': (50, 100, 80),    # フォレストグリーン
            '3': (120, 90, 70),    # チョコレートブラウン
            '4': (150, 50, 60),    # ワインレッド
            '5': (212, 175, 55),   # ゴールド
        }
    },

    # Playful系テーマ（遊び心のある柔らかさ）
    'playful': {
        'text_color': (60, 60, 80),  # ソフトネイビー
        'card_bg': (255, 250, 245),  # ウォームホワイト
        'card_alpha': 235,  # 92%透明度
        'card_border': (255, 140, 120),  # コーラルピンク
        'card_border_width': 2,  # やや太め
        'card_radius': 20,  # 大きめの角丸（柔らかさ）
        'card_shadow': True,  # ソフトな影
        'grid_color': (230, 220, 210),  # ウォームグレー
        'accent_color': (72, 209, 204),  # ターコイズ
        'hour_label_color': (80, 80, 100),  # ソフトグレー
        'hour_label_bg': (255, 245, 235, 200),  # 半透明ピーチ
        'hour_label_radius': 10,
        'active_card_bg': (255, 240, 230),  # ピーチ
        'active_card_border': (255, 140, 120),  # コーラル
        'active_card_border_width': 3,
        'active_text_color': (200, 80, 60),  # リッチコーラル
        'current_time_highlight': (72, 209, 204, 45),  # ターコイズ（明るく）
        'header_bg': (255, 250, 240, 190),  # ウォームホワイト背景
        'glass_effect': False,
        'chromatic_offset': 0,
        # グラデーション背景設定（無効化：背景は既存テーマと同じ）
        'background_gradient': {
            'enabled': False,
            'type': 'radial',
            'colors': [(255, 250, 240), (255, 220, 190), (255, 200, 170)],
            'direction': 'vertical'
        },
        'event_colors': {
            '1': (120, 180, 255),  # スカイブルー
            '2': (100, 200, 150),  # ミントグリーン
            '3': (200, 150, 220),  # ラベンダー
            '4': (255, 140, 120),  # コーラル
            '5': (255, 200, 100),  # サニーイエロー
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
