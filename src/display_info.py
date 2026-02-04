"""
ディスプレイ情報取得モジュール
各ディスプレイの解像度やメタデータを取得
"""
import platform
import subprocess
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class DisplayInfo:
    """ディスプレイ情報取得クラス"""

    def __init__(self):
        self.system = platform.system()

    def get_display_resolutions(self) -> List[Tuple[int, int]]:
        """
        すべてのディスプレイの解像度を取得

        Returns:
            List[Tuple[int, int]]: [(width1, height1), (width2, height2), ...]
        """
        try:
            if self.system == 'Darwin':  # macOS
                return self._get_resolutions_mac()
            elif self.system == 'Windows':
                return self._get_resolutions_windows()
            elif self.system == 'Linux':
                return self._get_resolutions_linux()
            else:
                logger.warning(f"サポートされていないOS: {self.system}")
                return [(1920, 1080)]  # デフォルト値

        except Exception as e:
            logger.error(f"解像度取得エラー: {e}")
            return [(1920, 1080)]  # デフォルト値

    def get_target_display_resolution(self, target_desktop: int) -> Tuple[int, int]:
        """
        指定されたデスクトップの解像度を取得

        Args:
            target_desktop: デスクトップ番号（1始まり）

        Returns:
            Tuple[int, int]: (width, height)
        """
        resolutions = self.get_display_resolutions()

        if target_desktop <= 0 or target_desktop > len(resolutions):
            logger.warning(f"無効なデスクトップ番号: {target_desktop}、デフォルト解像度を使用")
            return (1920, 1080)

        resolution = resolutions[target_desktop - 1]  # 0-indexに変換
        logger.info(f"desktop {target_desktop} の解像度: {resolution[0]}x{resolution[1]}")
        return resolution

    def _get_resolutions_mac(self) -> List[Tuple[int, int]]:
        """
        macOS用の解像度取得

        Returns:
            List[Tuple[int, int]]: 解像度のリスト
        """
        try:
            # system_profilerで全ディスプレイ情報を取得
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType'],
                capture_output=True,
                text=True,
                check=True
            )

            resolutions = []
            lines = result.stdout.split('\n')

            for line in lines:
                if 'Resolution:' in line:
                    # "Resolution: 1920 x 1080" のような形式を解析
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        resolution_str = parts[1].strip()
                        # "1920 x 1080" を解析
                        dimensions = resolution_str.split('x')
                        if len(dimensions) >= 2:
                            try:
                                width = int(dimensions[0].strip())
                                height = int(dimensions[1].strip())
                                resolutions.append((width, height))
                            except ValueError:
                                continue

            if not resolutions:
                logger.warning("解像度が取得できませんでした。デフォルト値を使用")
                resolutions = [(1920, 1080)]

            logger.info(f"検出されたディスプレイ: {len(resolutions)}台")
            for i, (w, h) in enumerate(resolutions, 1):
                logger.info(f"  desktop {i}: {w}x{h}")

            return resolutions

        except subprocess.CalledProcessError as e:
            logger.error(f"system_profiler実行エラー: {e}")
            return [(1920, 1080)]
        except Exception as e:
            logger.error(f"macOS解像度取得エラー: {e}")
            return [(1920, 1080)]

    def _get_resolutions_windows(self) -> List[Tuple[int, int]]:
        """
        Windows用の解像度取得

        Returns:
            List[Tuple[int, int]]: 解像度のリスト
        """
        try:
            import ctypes

            resolutions = []

            # プライマリモニターの解像度を取得
            user32 = ctypes.windll.user32
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            resolutions.append((width, height))

            logger.info(f"検出されたディスプレイ: {len(resolutions)}台（プライマリのみ）")
            logger.info(f"  desktop 1: {width}x{height}")

            return resolutions

        except Exception as e:
            logger.error(f"Windows解像度取得エラー: {e}")
            return [(1920, 1080)]

    def _get_resolutions_linux(self) -> List[Tuple[int, int]]:
        """
        Linux用の解像度取得

        Returns:
            List[Tuple[int, int]]: 解像度のリスト
        """
        try:
            # xrandrコマンドで解像度を取得
            result = subprocess.run(
                ['xrandr'],
                capture_output=True,
                text=True,
                check=True
            )

            resolutions = []
            lines = result.stdout.split('\n')

            for line in lines:
                if ' connected' in line and '*' in line:
                    # "1920x1080" のようなパターンを検索
                    parts = line.split()
                    for part in parts:
                        if 'x' in part and part[0].isdigit():
                            dimensions = part.split('x')
                            if len(dimensions) >= 2:
                                try:
                                    width = int(dimensions[0])
                                    height = int(dimensions[1].split('+')[0])  # "+0+0" を除去
                                    resolutions.append((width, height))
                                    break
                                except ValueError:
                                    continue

            if not resolutions:
                logger.warning("解像度が取得できませんでした。デフォルト値を使用")
                resolutions = [(1920, 1080)]

            logger.info(f"検出されたディスプレイ: {len(resolutions)}台")
            for i, (w, h) in enumerate(resolutions, 1):
                logger.info(f"  desktop {i}: {w}x{h}")

            return resolutions

        except subprocess.CalledProcessError as e:
            logger.error(f"xrandr実行エラー: {e}")
            return [(1920, 1080)]
        except Exception as e:
            logger.error(f"Linux解像度取得エラー: {e}")
            return [(1920, 1080)]
