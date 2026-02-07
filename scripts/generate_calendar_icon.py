"""
シンプルなGoogle Calendarアイコンを生成するスクリプト
40x40pxのPNG形式で出力
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# プロジェクトルート
BASE_DIR = Path(__file__).parent.parent
OUTPUT_PATH = BASE_DIR / 'assets' / 'google_calendar_icon.png'

def generate_calendar_icon(size=(40, 40)):
    """
    シンプルなカレンダーアイコンを生成

    Args:
        size: アイコンサイズ（幅, 高さ）
    """
    # 白背景の画像を作成
    img = Image.new('RGBA', size, (255, 255, 255, 0))  # 透明背景
    draw = ImageDraw.Draw(img)

    # カレンダーの枠（青色）
    calendar_color = (66, 133, 244)  # Google Blue
    border_width = 2

    # 外枠
    draw.rectangle(
        [(border_width, 6), (size[0] - border_width, size[1] - border_width)],
        fill=(255, 255, 255),
        outline=calendar_color,
        width=border_width
    )

    # 上部バー（ヘッダー）
    draw.rectangle(
        [(border_width, 6), (size[0] - border_width, 12)],
        fill=calendar_color
    )

    # カレンダーのリング（2つ）
    ring_radius = 2
    ring_y = 4
    left_ring_x = int(size[0] * 0.3)
    right_ring_x = int(size[0] * 0.7)

    draw.ellipse(
        [(left_ring_x - ring_radius, ring_y - ring_radius),
         (left_ring_x + ring_radius, ring_y + ring_radius)],
        fill=calendar_color
    )

    draw.ellipse(
        [(right_ring_x - ring_radius, ring_y - ring_radius),
         (right_ring_x + ring_radius, ring_y + ring_radius)],
        fill=calendar_color
    )

    # 日付部分（簡略化: 数字を描画）
    # 大きめのフォントで日付を表示
    try:
        # デフォルトフォント使用
        font = ImageFont.load_default()
    except:
        font = None

    # 数字 "31" を描画（カレンダーらしく）
    date_text = "31"
    text_bbox = draw.textbbox((0, 0), date_text, font=font) if font else (0, 0, 10, 10)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    text_x = (size[0] - text_width) // 2
    text_y = 16

    draw.text(
        (text_x, text_y),
        date_text,
        fill=(66, 133, 244),
        font=font
    )

    # 保存
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT_PATH, 'PNG')
    print(f"アイコンを生成しました: {OUTPUT_PATH}")


if __name__ == '__main__':
    generate_calendar_icon()
