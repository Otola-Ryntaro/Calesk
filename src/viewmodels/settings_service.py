"""
設定永続化サービス
ユーザー設定をJSONファイルに保存・読み込みする
config.pyのデフォルト値をベースに、ユーザー変更分を上書き保存
"""
import json
import logging
from pathlib import Path
from typing import Any, Optional

from ..config import (
    THEME, AUTO_UPDATE_INTERVAL_MINUTES, AUTO_UPDATE_ENABLED_DEFAULT,
    AUTO_DETECT_RESOLUTION, WALLPAPER_TARGET_DESKTOP,
    CARD_SHADOW_ENABLED, DEFAULT_PRESET_BACKGROUND,
)

logger = logging.getLogger(__name__)

# デフォルトの設定ディレクトリ
DEFAULT_SETTINGS_DIR = Path.home() / ".calendar_wallpaper"


class SettingsService:
    """ユーザー設定の永続化を管理するサービス"""

    # config.pyの値をデフォルトとして定義
    DEFAULTS = {
        "theme": THEME,
        "auto_update_enabled": AUTO_UPDATE_ENABLED_DEFAULT,
        "auto_update_interval_minutes": AUTO_UPDATE_INTERVAL_MINUTES,
        "background_image_path": f"preset:{DEFAULT_PRESET_BACKGROUND}",
        "auto_detect_resolution": AUTO_DETECT_RESOLUTION,
        "wallpaper_target_desktop": WALLPAPER_TARGET_DESKTOP,
        "card_shadow_enabled": CARD_SHADOW_ENABLED,
    }

    # 設定値の型スキーマ
    _SCHEMA = {
        "theme": str,
        "auto_update_enabled": bool,
        "auto_update_interval_minutes": int,
        "background_image_path": (str, type(None)),
        "auto_detect_resolution": bool,
        "wallpaper_target_desktop": int,
        "card_shadow_enabled": bool,
    }

    def __init__(self, settings_dir: Optional[Path] = None):
        self.settings_dir = settings_dir or DEFAULT_SETTINGS_DIR
        self.settings_file = self.settings_dir / "settings.json"
        self._settings = dict(self.DEFAULTS)

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """既知のキーのみ設定値を更新"""
        if key not in self.DEFAULTS:
            logger.warning(f"不明な設定キー: {key}")
            return
        if not self._validate_type(key, value):
            logger.warning(f"設定値の型が不正です: {key}={value!r} (期待: {self._SCHEMA.get(key)})")
            return
        self._settings[key] = value

    def get_all(self) -> dict:
        """全設定を辞書で取得"""
        return dict(self._settings)

    def update(self, settings: dict) -> None:
        """複数設定を一括更新（既知のキーのみ）"""
        for key, value in settings.items():
            self.set(key, value)

    def reset(self) -> None:
        """デフォルトにリセット"""
        self._settings = dict(self.DEFAULTS)

    def save(self) -> bool:
        """設定をJSONファイルに保存。成功時True、失敗時Falseを返す"""
        try:
            self.settings_dir.mkdir(parents=True, exist_ok=True)

            # デフォルトから変更された値のみ保存
            changed = {
                k: v for k, v in self._settings.items()
                if k in self.DEFAULTS and v != self.DEFAULTS.get(k)
            }

            self.settings_file.write_text(
                json.dumps(changed, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.info(f"設定を保存しました: {self.settings_file}")
            return True
        except Exception as e:
            logger.error(f"設定の保存に失敗: {e}", exc_info=True)
            return False

    def load(self) -> None:
        """JSONファイルから設定を読み込み"""
        self._settings = dict(self.DEFAULTS)

        if not self.settings_file.exists():
            logger.info("設定ファイルが見つかりません。デフォルト設定を使用します")
            return

        try:
            data = json.loads(self.settings_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # 既知のキーのみ取り込み
                valid_data = {k: v for k, v in data.items() if k in self.DEFAULTS}
                unknown_keys = set(data.keys()) - set(self.DEFAULTS.keys())
                if unknown_keys:
                    logger.warning(f"不明な設定キーを無視しました: {unknown_keys}")
                self._settings.update(valid_data)
                logger.info(f"設定を読み込みました: {self.settings_file}")
            else:
                logger.warning(f"設定ファイルのフォーマットが不正です (type={type(data).__name__})")
        except Exception as e:
            logger.warning(f"設定ファイルの読み込みに失敗: {e}")

    def _validate_type(self, key: str, value: Any) -> bool:
        """設定値の型を検証"""
        expected_type = self._SCHEMA.get(key)
        if expected_type is None:
            return False
        return isinstance(value, expected_type)
