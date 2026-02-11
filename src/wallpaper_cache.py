"""
壁紙キャッシュ管理
壁紙生成成功時にメタデータを保存し、API接続不可時にキャッシュから復元
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class WallpaperCache:
    """壁紙キャッシュ管理クラス"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        初期化

        Args:
            cache_dir: キャッシュディレクトリ。Noneの場合はデフォルトパスを使用。
        """
        if cache_dir is None:
            from .config import CONFIG_DIR
            self._cache_dir = CONFIG_DIR
        else:
            self._cache_dir = cache_dir

        self._cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def meta_path(self) -> Path:
        """キャッシュメタデータのパス"""
        return self._cache_dir / 'cache_meta.json'

    def save_cache(self, wallpaper_path: Path, theme: str) -> None:
        """
        壁紙キャッシュのメタデータを保存

        Args:
            wallpaper_path: 壁紙画像のパス
            theme: テーマ名
        """
        meta = {
            'last_wallpaper_path': str(wallpaper_path),
            'theme': theme,
            'generated_at': datetime.now().isoformat(),
        }
        try:
            self.meta_path.write_text(json.dumps(meta, ensure_ascii=False))
            logger.info(f"壁紙キャッシュを保存しました: {wallpaper_path}")
        except Exception as e:
            logger.error(f"キャッシュ保存エラー: {e}")

    def load_cache(self) -> Optional[Path]:
        """
        キャッシュから壁紙パスを読み込み

        Returns:
            壁紙画像のPath。キャッシュがない、またはファイルが存在しない場合はNone。
        """
        if not self.meta_path.exists():
            return None

        try:
            meta = json.loads(self.meta_path.read_text())
            wallpaper_path = Path(meta['last_wallpaper_path'])

            if not wallpaper_path.exists():
                logger.warning(f"キャッシュ壁紙が見つかりません: {wallpaper_path}")
                return None

            logger.info(f"キャッシュ壁紙を読み込みました: {wallpaper_path}")
            return wallpaper_path

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"キャッシュメタデータの読み込みに失敗: {e}")
            return None
