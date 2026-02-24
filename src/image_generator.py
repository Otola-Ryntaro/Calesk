"""
壁紙画像生成モジュール（新デザイン）
カレンダーイベントを基に壁紙画像を生成

描画処理はMixinクラスに分離:
- EffectsRendererMixin: 角丸矩形、影、ガラスモーフィズム、色相分離テキスト等
- CardRendererMixin: イベントカード描画（Zen/Hero/Compact/Single）
- CalendarRendererMixin: 週間カレンダー、時刻ラベル、イベント配置
"""
import gc
import platform
from collections import ChainMap
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from .models.event import CalendarEvent
from .config import (
    IMAGE_WIDTH, IMAGE_HEIGHT,
    BACKGROUND_COLOR, TEXT_COLOR,
    FONT_PATHS, FONT_PATHS_BOLD,
    DEFAULT_EVENT_COLORS,
    OUTPUT_DIR, WALLPAPER_FILENAME_TEMPLATE,
    # 新デザイン設定（最適化版）
    DESKTOP_ICON_AREA_HEIGHT,
    SPACING_TOP, SPACING_MIDDLE,
    CARD_WIDTH, CARD_HEIGHT, CARD_MARGIN, CARD_PADDING,
    FONT_SIZE_CARD_DATE, FONT_SIZE_CARD_TIME, FONT_SIZE_CARD_TITLE, FONT_SIZE_CARD_LOCATION,
    COMPACT_CARD_WIDTH, COMPACT_CARD_HEIGHT, COMPACT_CARD_MARGIN, COMPACT_CARD_PADDING,
    MAX_CARDS_PER_COLUMN, COLUMN_HEADER_HEIGHT, COLUMN_GAP,
    WEEK_CALENDAR_START_HOUR, WEEK_CALENDAR_END_HOUR,
    HOUR_HEIGHT, DAY_COLUMN_WIDTH,
    FONT_SIZE_HOUR_LABEL, FONT_SIZE_DAY_HEADER, FONT_SIZE_EVENT_BLOCK,
    # 背景画像設定
    BACKGROUND_IMAGE_PATH,
    # Google Calendar アイコン設定
    CALENDAR_ICON_PATH, CALENDAR_ICON_SIZE,
    ICON_MAC_POSITION, ICON_WINDOWS_POSITION, ICON_LINUX_POSITION,
    # テーマ設定
    THEME, CARD_SHADOW_ENABLED,
    # 時刻ラベル視認性設定
    LABEL_VISIBILITY_MODE,
    # マルチディスプレイ設定
    WALLPAPER_TARGET_DESKTOP, AUTO_DETECT_RESOLUTION
)
from . import themes
from .themes import DEFAULT_THEME
from .display_info import DisplayInfo
from .renderers import EffectsRendererMixin, CardRendererMixin, CalendarRendererMixin

logger = logging.getLogger(__name__)


class ImageGenerator(EffectsRendererMixin, CardRendererMixin, CalendarRendererMixin):
    """壁紙画像生成クラス（新デザイン対応）"""

    # フォント定義（属性名 → (サイズ設定値, bold)）
    _FONT_DEFS = {
        'font_card_date': (FONT_SIZE_CARD_DATE, False),
        'font_card_time': (FONT_SIZE_CARD_TIME, False),
        'font_card_title': (FONT_SIZE_CARD_TITLE, False),
        'font_card_location': (FONT_SIZE_CARD_LOCATION, False),
        'font_hour_label': (FONT_SIZE_HOUR_LABEL, False),
        'font_day_header': (FONT_SIZE_DAY_HEADER, False),
        'font_event_block': (FONT_SIZE_EVENT_BLOCK, False),
        'font_card_time_bold': (FONT_SIZE_CARD_TIME, True),
        'font_day_header_bold': (FONT_SIZE_DAY_HEADER, True),
    }

    # クロップ位置の定義
    CROP_POSITIONS = ['center', 'top', 'bottom']

    def __init__(self):
        self.system = platform.system()
        self._custom_background_path = None
        self._crop_position = 'center'

        # 解像度の自動検出
        if AUTO_DETECT_RESOLUTION and WALLPAPER_TARGET_DESKTOP > 0:
            display_info = DisplayInfo()
            self.width, self.height = display_info.get_target_display_resolution(WALLPAPER_TARGET_DESKTOP)
            logger.info(f"解像度を自動検出しました: {self.width}x{self.height}")
        else:
            self.width = IMAGE_WIDTH
            self.height = IMAGE_HEIGHT
            logger.info(f"デフォルト解像度を使用: {self.width}x{self.height}")

        # フォントキャッシュ（遅延ロード用）
        self._font_cache = {}

        # 背景画像キャッシュ
        self._cached_background = None
        self._cached_background_path = None

        # アイコン画像キャッシュ
        self._cached_icon = None

        # レイアウト計算（動的）
        self.layout = self._calculate_layout()

        # テーマ初期化（ChainMapでDEFAULT_THEMEをフォールバックに）
        self.theme_name = THEME
        self.theme = ChainMap(themes.get_theme(THEME), DEFAULT_THEME)

    def __getattr__(self, name):
        """フォント属性の遅延ロード"""
        if name in ImageGenerator._FONT_DEFS:
            size, bold = ImageGenerator._FONT_DEFS[name]
            if name not in self._font_cache:
                if bold:
                    self._font_cache[name] = self._get_font_bold(size)
                else:
                    self._font_cache[name] = self._get_font(size)
            return self._font_cache[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """システムに応じた日本語フォントを取得"""
        font_paths = FONT_PATHS.get(self.system, [])

        for font_path in font_paths:
            try:
                if Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)
            except Exception as e:
                logger.warning(f"フォント読み込みエラー ({font_path}): {e}")

        logger.warning(f"日本語フォントが見つかりません。デフォルトフォントを使用します")
        return ImageFont.load_default()

    def _get_font_bold(self, size: int) -> ImageFont.FreeTypeFont:
        """システムに応じた日本語Boldフォントを取得（見つからない場合はRegularにフォールバック）"""
        font_paths = FONT_PATHS_BOLD.get(self.system, [])

        for font_path in font_paths:
            try:
                if Path(font_path).exists():
                    return ImageFont.truetype(font_path, size)
            except Exception as e:
                logger.warning(f"Boldフォント読み込みエラー ({font_path}): {e}")

        # Bold が見つからない場合は Regular にフォールバック
        return self._get_font(size)

    def _calculate_layout(self) -> Dict[str, int]:
        """
        動的レイアウト計算（1080px以内に収める）

        Returns:
            Dict: レイアウトパラメータ
        """
        # 固定値
        desktop_h = DESKTOP_ICON_AREA_HEIGHT
        card_h = CARD_HEIGHT
        spacing_top = SPACING_TOP
        spacing_middle = SPACING_MIDDLE
        # 曜日ヘッダーは2行表示（"Mon\n2/7"）なので2行分の高さを確保
        header_h = FONT_SIZE_DAY_HEADER * 2 + 15

        # 時間範囲
        total_hours = WEEK_CALENDAR_END_HOUR - WEEK_CALENDAR_START_HOUR + 1

        # 1時間あたりの高さ（固定値を使用、視認性より高さ削減優先）
        hour_height = HOUR_HEIGHT

        # 実際のカレンダー高さ
        calendar_height = hour_height * total_hours

        # 各要素のY座標
        card_y = desktop_h + spacing_top
        week_cal_y = card_y + card_h + spacing_middle
        grid_y = week_cal_y + header_h

        return {
            'card_y_start': card_y,
            'week_calendar_y_start': week_cal_y,
            'grid_y_start': grid_y,
            'hour_height': hour_height,
            'calendar_height': calendar_height,
            'header_height': header_h
        }

    def release_resources(self):
        """
        メモリ上のリソースを解放（背景画像・アイコンキャッシュ）
        バックグラウンド待機時のメモリ消費を削減
        フォントキャッシュは再生成コストが高いため保持する
        """
        if self._cached_background:
            self._cached_background.close()
        self._cached_background = None
        self._cached_background_path = None
        if self._cached_icon:
            self._cached_icon.close()
        self._cached_icon = None
        gc.collect()
        logger.debug("ImageGeneratorリソースを解放しました（GC実行）")

    def set_theme(self, theme_name: str):
        """
        テーマを切り替える

        Args:
            theme_name: テーマ名（'simple', 'modern', 'pastel', 'dark', 'vibrant'）
        """
        self.theme_name = theme_name
        self.theme = ChainMap(themes.get_theme(theme_name), DEFAULT_THEME)
        logger.info(f"テーマを '{theme_name}' に切り替えました")

    @property
    def custom_background_path(self):
        """カスタム背景画像パスを取得"""
        return self._custom_background_path

    def set_background_image(self, path):
        """カスタム背景画像パスを設定"""
        self._custom_background_path = path
        logger.info(f"カスタム背景画像を設定: {path}")

    def reset_background_image(self):
        """背景画像をデフォルトに戻す"""
        self._custom_background_path = None
        logger.info("背景画像をデフォルトに戻しました")

    @property
    def crop_position(self):
        """クロップ位置を取得"""
        return self._crop_position

    def set_crop_position(self, position: str):
        """クロップ位置を設定（center/top/bottom）"""
        if position in self.CROP_POSITIONS:
            self._crop_position = position
            # クロップ位置変更時はキャッシュをクリア
            if self._cached_background:
                self._cached_background.close()
            self._cached_background = None
            self._cached_background_path = None
            logger.info(f"クロップ位置を '{position}' に設定しました")

    def _resize_cover(self, img: Image.Image, crop_position: str = None) -> Image.Image:
        """アスペクト比を維持したままスクリーンを覆うリサイズ+クロップ

        余白なし・はみ出し部分をクロップ（CSS background-size: cover相当）
        """
        position = crop_position or self._crop_position
        src_w, src_h = img.size
        target_w, target_h = self.width, self.height

        # スケール計算: 大きい方の比率を採用（画面を完全に覆う）
        scale = max(target_w / src_w, target_h / src_h)
        new_w = max(target_w, int(src_w * scale + 0.5))
        new_h = max(target_h, int(src_h * scale + 0.5))

        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # クロップ位置を計算
        # 横方向は常に中央
        left = (new_w - target_w) // 2
        # 縦方向はcrop_positionに従う
        if position == 'top':
            top = 0
        elif position == 'bottom':
            top = new_h - target_h
        else:  # center
            top = (new_h - target_h) // 2

        cropped = resized.crop((left, top, left + target_w, top + target_h))
        resized.close()
        return cropped

    def _get_icon_position(self) -> Tuple[int, int]:
        """
        OS別のアイコン配置座標を取得（動的解像度対応）

        Returns:
            Tuple[int, int]: (x, y) 座標
        """
        if self.system == 'Darwin':  # Mac: 上部右寄せ
            return (self.width - 60, 20)
        elif self.system == 'Windows':  # Windows: 右下
            return (self.width - 60, self.height - 60)
        else:  # Linux その他: Mac同様
            return (self.width - 60, 20)

    def _get_icon_size(self) -> Tuple[int, int]:
        """
        アイコンサイズを取得

        Returns:
            Tuple[int, int]: (width, height)
        """
        return CALENDAR_ICON_SIZE

    def _draw_calendar_icon(self, image: Image.Image, draw: ImageDraw.ImageDraw):
        """
        Google Calendarアイコンを描画

        Args:
            image: Imageオブジェクト
            draw: ImageDrawオブジェクト
        """
        try:
            if CALENDAR_ICON_PATH and Path(CALENDAR_ICON_PATH).exists():
                # キャッシュがない場合のみ読み込み
                if self._cached_icon is None:
                    icon_img = Image.open(CALENDAR_ICON_PATH)
                    icon_size = self._get_icon_size()
                    if icon_img.size != icon_size:
                        resized = icon_img.resize(icon_size, Image.Resampling.LANCZOS)
                        icon_img.close()
                        icon_img = resized
                    self._cached_icon = icon_img

                x, y = self._get_icon_position()

                if self._cached_icon.mode == 'RGBA':
                    image.paste(self._cached_icon, (x, y), self._cached_icon)
                else:
                    image.paste(self._cached_icon, (x, y))

                logger.debug(f"アイコンを配置しました: ({x}, {y})")
            else:
                logger.warning(f"アイコン画像が見つかりません: {CALENDAR_ICON_PATH}")

        except Exception as e:
            logger.error(f"アイコン描画エラー: {e}", exc_info=True)

    def generate_wallpaper(
        self,
        today_events: List[CalendarEvent],
        week_events: List[CalendarEvent],
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """壁紙画像を生成"""
        try:
            # グラデーション背景設定を確認
            gradient_config = self.theme.get('background_gradient', {})
            gradient_enabled = gradient_config.get('enabled', False)

            if gradient_enabled:
                # グラデーション背景を生成
                logger.info("グラデーション背景を生成します")
                gradient_type = gradient_config.get('type', 'linear')
                colors = gradient_config.get('colors', None)
                direction = gradient_config.get('direction', 'vertical')

                image = self._create_gradient_background(
                    width=self.width,
                    height=self.height,
                    gradient_type=gradient_type,
                    colors=colors,
                    direction=direction
                )
            else:
                # カスタム背景画像が設定されている場合はそちらを優先
                bg_path = self._custom_background_path or BACKGROUND_IMAGE_PATH
                if bg_path and Path(bg_path).exists():
                    # 背景画像キャッシュ: 同じパスなら再読み込みしない
                    if self._cached_background and self._cached_background_path == str(bg_path):
                        logger.info("キャッシュ済み背景画像を使用します")
                        image = self._cached_background.copy()
                    else:
                        logger.info(f"背景画像を読み込んでいます: {bg_path}")
                        raw = Image.open(bg_path)
                        background = self._resize_cover(raw)
                        raw.close()
                        if background.mode != 'RGBA':
                            converted = background.convert('RGBA')
                            background.close()
                            background = converted
                        # キャッシュに保存
                        self._cached_background = background
                        self._cached_background_path = str(bg_path)
                        image = background.copy()
                else:
                    # デフォルト背景（白、RGBAモード）
                    logger.info("デフォルト背景を生成します")
                    image = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))

            draw = ImageDraw.Draw(image)

            # 動的レイアウト値を使用
            card_y_start = self.layout['card_y_start']
            week_calendar_y_start = self.layout['week_calendar_y_start']

            # 予定カード描画（3列レイアウト: 今日・明日・明後日）
            self._draw_event_cards(draw, today_events, card_y_start, week_events=week_events, image=image)
            draw = ImageDraw.Draw(image)  # alpha_composite後にdrawを再取得

            # 週間カレンダー描画
            self._draw_week_calendar(draw, week_events, week_calendar_y_start, image=image)

            # RGBAからRGBに変換（PNG保存用）
            if image.mode == 'RGBA':
                rgb_image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
                rgb_image.paste(image, mask=image.getchannel('A'))
                image.close()  # RGBA画像を明示的に解放
                image = rgb_image

            # 画像を保存
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            final_output_path = output_path
            if final_output_path is None:
                filename = WALLPAPER_FILENAME_TEMPLATE.format(
                    theme=self.theme_name,
                    date=datetime.now().strftime('%Y%m%d')
                )
                final_output_path = OUTPUT_DIR / filename
            image.save(final_output_path)
            image.close()  # 保存後は不要なので即座に解放

            logger.info(f"壁紙画像を生成しました: {final_output_path}")
            return final_output_path

        except Exception as e:
            logger.error(f"画像生成エラー: {e}", exc_info=True)
            return None
