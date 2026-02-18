"""
壁紙設定モジュール
OS別に壁紙を設定する機能を提供
"""
import platform
import ctypes
import re
import subprocess
import logging
from pathlib import Path
from typing import Optional
from . import config

logger = logging.getLogger(__name__)

# セキュリティ: 許可する画像ファイル拡張子のホワイトリスト
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.PNG', '.JPG', '.JPEG', '.BMP', '.GIF'}

# セキュリティ: 最大ファイルサイズ（50MB）
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024

# セキュリティ: パスに含まれてはならない制御文字（NULL、改行以外の制御文字）
# AppleScript/KDE evaluateScript へのインジェクション防止
_DANGEROUS_PATH_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')


class WallpaperSetter:
    """壁紙設定クラス"""

    def __init__(self):
        self.system = platform.system()
        logger.info(f"検出されたOS: {self.system}")

    def _validate_wallpaper_path(self, path: Path) -> bool:
        """
        壁紙パスに危険な文字が含まれていないことを一元検証

        AppleScript/KDE evaluateScript へのインジェクションを防ぐため、
        制御文字（NULLバイト等）を事前に弾く。

        Args:
            path: 検証対象パス（resolve済みの絶対パス）

        Returns:
            bool: 安全なパスはTrue、危険な文字を含む場合はFalse
        """
        path_str = str(path)
        if _DANGEROUS_PATH_RE.search(path_str):
            logger.error("壁紙パスに不正な制御文字が含まれています（インジェクション防止）")
            return False
        return True

    def set_wallpaper(self, image_path: Path) -> bool:
        """
        壁紙を設定

        Args:
            image_path: 壁紙画像のパス

        Returns:
            bool: 設定成功でTrue、失敗でFalse
        """
        if not image_path.exists():
            logger.error(f"画像ファイルが見つかりません: {image_path}")
            return False

        # セキュリティ: 画像ファイル拡張子の検証
        file_extension = image_path.suffix
        if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
            logger.error(f"サポートされていないファイル形式: {file_extension}")
            return False

        # セキュリティ: ファイルサイズの検証
        file_size = image_path.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            logger.error(f"ファイルサイズが大きすぎます: {file_size / (1024*1024):.2f}MB (上限: {MAX_FILE_SIZE_BYTES / (1024*1024):.0f}MB)")
            return False

        # 絶対パスに変換
        abs_path = image_path.resolve()

        # セキュリティ: 制御文字によるインジェクション防止（一元検証）
        if not self._validate_wallpaper_path(abs_path):
            return False

        try:
            if self.system == 'Windows':
                return self._set_wallpaper_windows(abs_path)
            elif self.system == 'Darwin':  # Mac
                return self._set_wallpaper_mac(abs_path)
            elif self.system == 'Linux':
                return self._set_wallpaper_linux(abs_path)
            else:
                logger.error(f"サポートされていないOS: {self.system}")
                return False

        except Exception as e:
            logger.error(f"壁紙設定エラー: {e}")
            return False

    def _set_wallpaper_windows(self, image_path: Path) -> bool:
        """
        Windows用の壁紙設定

        Args:
            image_path: 壁紙画像のパス

        Returns:
            bool: 設定成功でTrue、失敗でFalse
        """
        try:
            # SystemParametersInfoW APIを使用
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02

            result = ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                str(image_path),
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )

            if result:
                logger.info(f"壁紙を設定しました (Windows): {image_path}")
                return True
            else:
                logger.error("SystemParametersInfoW が失敗しました")
                return False

        except Exception as e:
            logger.error(f"Windows壁紙設定エラー: {e}")
            return False

    def _set_wallpaper_mac(self, image_path: Path) -> bool:
        """
        Mac用の壁紙設定

        Args:
            image_path: 壁紙画像のパス

        Returns:
            bool: 設定成功でTrue、失敗でFalse
        """
        try:
            # セキュリティ: パス内の引用符とバックスラッシュ、改行文字をエスケープしてコマンドインジェクションを防止
            safe_path = str(image_path).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')

            # osascriptでAppleScriptを実行
            # WALLPAPER_TARGET_DESKTOPに応じて適用範囲を変更
            target_desktop = getattr(config, 'WALLPAPER_TARGET_DESKTOP', 0)

            if target_desktop == 0:
                # 全デスクトップに適用
                script = f'''
                    tell application "System Events"
                        tell every desktop
                            set picture to POSIX file "{safe_path}"
                        end tell
                    end tell
                '''
            else:
                # 指定されたデスクトップのみに適用
                script = f'''
                    tell application "System Events"
                        tell desktop {target_desktop}
                            set picture to POSIX file "{safe_path}"
                        end tell
                    end tell
                '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"壁紙を設定しました (Mac): {image_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"osascript実行エラー: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Mac壁紙設定エラー: {e}")
            return False

    def _set_wallpaper_linux(self, image_path: Path) -> bool:
        """
        Linux用の壁紙設定（GNOME環境）

        Args:
            image_path: 壁紙画像のパス

        Returns:
            bool: 設定成功でTrue、失敗でFalse
        """
        try:
            # GNOME環境の場合
            result = subprocess.run(
                [
                    'gsettings', 'set',
                    'org.gnome.desktop.background', 'picture-uri',
                    f'file://{image_path}'
                ],
                capture_output=True,
                text=True,
                check=True
            )

            logger.info(f"壁紙を設定しました (Linux/GNOME): {image_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.warning(f"GNOME壁紙設定失敗: {e.stderr}")

            # KDE Plasma環境を試す
            try:
                # セキュリティ: JavaScript/QMLコード内の危険な文字をエスケープ
                safe_kde_path = str(image_path).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')

                result = subprocess.run(
                    [
                        'qdbus', 'org.kde.plasmashell', '/PlasmaShell',
                        'org.kde.PlasmaShell.evaluateScript',
                        f'''
                        var allDesktops = desktops();
                        for (i=0;i<allDesktops.length;i++) {{
                            d = allDesktops[i];
                            d.wallpaperPlugin = "org.kde.image";
                            d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                            d.writeConfig("Image", "file://{safe_kde_path}");
                        }}
                        '''
                    ],
                    capture_output=True,
                    text=True,
                    check=True
                )

                logger.info(f"壁紙を設定しました (Linux/KDE): {image_path}")
                return True

            except Exception as kde_error:
                logger.error(f"KDE壁紙設定も失敗: {kde_error}")
                return False

        except Exception as e:
            logger.error(f"Linux壁紙設定エラー: {e}")
            return False
