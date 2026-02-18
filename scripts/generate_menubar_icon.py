#!/usr/bin/env python3
"""
Calesk メニューバーアイコン生成スクリプト

デザイン: C字型カレンダー
  - 角丸矩形のアウトライン → 右辺中央を欠いてC字に
  - 内部: ヘッダーバー（塗り） + 3×3グリッド（ドット）

出力:
  assets/icon_menubar@2x.png  44×44px (Retina)
  assets/icon_menubar.png     22×22px (1x)

macOSテンプレートイメージ方式:
  黒 + 透過のPNGをアプリに登録するだけで
  ライト/ダークモード両対応になる。
"""

from pathlib import Path
from PIL import Image, ImageDraw

ASSET_DIR = Path(__file__).parent.parent / 'assets'
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def generate_icon(size: int = 44, color: tuple = BLACK) -> Image.Image:
    """C字型カレンダーアイコンを生成する。

    Args:
        size: 出力サイズ（px）。44=Retina@2x、22=通常。

    Returns:
        RGBA画像
    """
    img = Image.new('RGBA', (size, size), CLEAR)
    draw = ImageDraw.Draw(img)

    s = size
    pad    = round(s * 0.09)   # 外余白       (4px @ 44)
    radius = round(s * 0.16)   # 角丸半径      (7px @ 44)
    stroke = round(s * 0.114)  # 枠線太さ      (5px @ 44)

    # ── C外形：角丸矩形の枠線 ───────────────────────────
    draw.rounded_rectangle(
        [(pad, pad), (s - pad, s - pad)],
        radius=radius,
        outline=color,
        width=stroke,
    )

    # ── Cの開口部：右辺の中央を透明で消去 ───────────────
    open_top = round(s * 0.27)      # 上端 (12px @ 44)
    open_bot = round(s * 0.73)      # 下端 (32px @ 44)
    erase_x1 = s - pad - stroke     # 右辺内側の左端
    erase_x2 = s - pad + 1          # 右辺外側の右端（1px余分に消す）
    draw.rectangle(
        [(erase_x1, open_top), (erase_x2, open_bot)],
        fill=CLEAR,
    )

    # ── カレンダー内部領域 ────────────────────────────────
    ix1 = pad + stroke + 1
    ix2 = s - pad - stroke - 1
    iy1 = pad + stroke + 1
    iy2 = s - pad - stroke - 1

    # ヘッダーバー（塗り）
    hdr_h  = round(s * 0.18)   # 8px @ 44
    hdr_y2 = iy1 + hdr_h
    draw.rectangle([(ix1, iy1), (ix2, hdr_y2)], fill=color)

    # グリッド：3列 × 3行 の小さな正方形ドット
    gx1  = ix1 + 1
    gx2  = ix2 - 1
    gy1  = hdr_y2 + round(s * 0.07)   # ヘッダー下の余白 (3px @ 44)
    gy2  = iy2 - 1
    gw   = gx2 - gx1
    gh   = gy2 - gy1
    dot  = max(2, round(s * 0.05))    # ドット半径 (2px @ 44)

    cols, rows = 3, 3
    for row in range(rows):
        for col in range(cols):
            dx = gx1 + int(gw * (col + 0.5) / cols)
            dy = gy1 + int(gh * (row + 0.5) / rows)
            draw.rectangle(
                [(dx - dot, dy - dot), (dx + dot, dy + dot)],
                fill=color,
            )

    return img


def _save_pair(color: tuple, suffix: str) -> None:
    """指定カラーで1x/2x/previewを生成・保存"""
    img_2x = generate_icon(44, color)
    img_2x.save(ASSET_DIR / f'icon_menubar{suffix}@2x.png')
    print(f"✓ icon_menubar{suffix}@2x.png  (44×44)")

    img_1x = img_2x.resize((22, 22), Image.LANCZOS)
    img_1x.save(ASSET_DIR / f'icon_menubar{suffix}.png')
    print(f"✓ icon_menubar{suffix}.png  (22×22)")

    # プレビュー用（×10 拡大）
    img_preview = img_2x.resize((440, 440), Image.NEAREST)
    img_preview.save(ASSET_DIR / f'icon_menubar{suffix}_preview.png')
    print(f"✓ icon_menubar{suffix}_preview.png  (440×440 preview)")


def main() -> None:
    ASSET_DIR.mkdir(exist_ok=True)

    print("── 黒版（ライトモード用）──")
    _save_pair(BLACK, '')          # icon_menubar.png / @2x

    print("\n── 白版（ダークモード用）──")
    _save_pair(WHITE, '_white')    # icon_menubar_white.png / @2x

    print("\n完了！")


if __name__ == '__main__':
    main()
