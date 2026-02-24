"""
ファイル/ディレクトリの最小権限ユーティリティ
Unix系では600/700を適用し、Windowsではベストエフォートで継続する。
"""
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_private_dir(path: Path) -> None:
    """ディレクトリを作成し、可能な環境では 700 相当に制限する。"""
    path.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        try:
            os.chmod(path, 0o700)
        except PermissionError:
            # 既存の共有ディレクトリ（例: /tmp）では権限変更できない場合がある
            pass


def secure_file_permissions(path: Path) -> None:
    """可能な環境ではファイル権限を 600 に制限する。"""
    if os.name != "nt":
        try:
            os.chmod(path, 0o600)
        except PermissionError:
            pass
