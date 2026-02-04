"""
PreviewWidget

壁紙プレビュー表示ウィジェット。
QPixmapを使用して画像を表示します。
"""

from pathlib import Path
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)


class PreviewWidget(QLabel):
    """
    壁紙プレビューウィジェット

    QLabel を継承し、壁紙画像のプレビュー表示を行います。
    画像はウィジェットサイズに合わせて自動的にスケーリングされます。
    """

    def __init__(self, parent=None):
        """
        PreviewWidgetを初期化

        Args:
            parent (QWidget, optional): 親ウィジェット。デフォルトはNone。
        """
        super().__init__(parent)

        # 初期設定
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.setMinimumSize(400, 300)

        # スケーリング設定
        self.setScaledContents(False)  # カスタムスケーリングを使用

        # プレースホルダーテキスト
        self._placeholder_text = "プレビュー（壁紙生成後に表示されます）"
        self.setText(self._placeholder_text)

        # プレビュー画像の最大サイズ（メモリ効率化）
        self._max_preview_width = 640
        self._max_preview_height = 360

        # プレビュー用の縮小画像を保持（リサイズ時の再描画用）
        self._preview_pixmap = None

        # 元画像のパスのみ保持（メモリ効率化）
        self._image_path = None

        logger.info("PreviewWidgetを初期化しました")

    def set_image(self, image_path: Path):
        """
        画像を設定して表示

        画像はウィジェットサイズに合わせて自動的にスケーリングされます。

        Args:
            image_path (Path): 画像ファイルのパス
        """
        try:
            # パスの正規化（ディレクトリトラバーサル防止）
            try:
                normalized_path = image_path.resolve()
            except (OSError, RuntimeError) as e:
                logger.error(f"パスの正規化に失敗しました: {e}")
                return

            # パスの存在確認
            if not normalized_path.exists():
                logger.warning(f"画像ファイルが見つかりません: {normalized_path}")
                return

            # 許可された拡張子のチェック
            allowed_extensions = {'.png', '.jpg', '.jpeg'}
            if normalized_path.suffix.lower() not in allowed_extensions:
                logger.error(f"許可されていない拡張子です: {normalized_path.suffix}。許可されている拡張子: {', '.join(allowed_extensions)}")
                return

            # ファイルサイズチェック（10MB制限）
            max_size_bytes = 10 * 1024 * 1024  # 10MB
            file_size = normalized_path.stat().st_size
            if file_size > max_size_bytes:
                logger.error(f"ファイルサイズが大きすぎます: {file_size / (1024 * 1024):.2f}MB（制限: 10MB）")
                return

            # 以降は正規化されたパスを使用
            image_path = normalized_path

            # 画像を読み込み
            pixmap = QPixmap(str(image_path))

            if pixmap.isNull():
                logger.error(f"画像の読み込みに失敗しました: {image_path}")
                return

            # プレビュー用のサムネイルを作成（最大640x360）
            # メモリ効率化: 元画像ではなく縮小版のみ保持
            scaled_pixmap = pixmap.scaled(
                self._max_preview_width,
                self._max_preview_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # プレビュー画像を保持
            self._preview_pixmap = scaled_pixmap

            # 元画像のパスのみ保持（元画像Pixmapは保持しない）
            self._image_path = image_path

            # スケーリングして表示
            self._display_scaled_image()

            # プレースホルダーテキストをクリア
            self.setText("")

            logger.info(f"画像を設定しました: {image_path}（サムネイル: {scaled_pixmap.width()}x{scaled_pixmap.height()}）")

        except Exception as e:
            logger.error(f"画像設定エラー: {e}")

    def _display_scaled_image(self):
        """
        プレビュー画像をウィジェットサイズに合わせてスケーリングして表示
        """
        if self._preview_pixmap is None or self._preview_pixmap.isNull():
            return

        # ウィジェットサイズに合わせてスケーリング（アスペクト比維持）
        scaled_pixmap = self._preview_pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)

    def clear_preview(self):
        """
        プレビューをクリアしてプレースホルダーテキストに戻す
        """
        self._preview_pixmap = None
        self._image_path = None
        self.clear()
        self.setText(self._placeholder_text)
        logger.info("プレビューをクリアしました")

    def resizeEvent(self, event):
        """
        リサイズイベント

        ウィジェットがリサイズされたときに画像を再スケーリングします。

        Args:
            event: リサイズイベント
        """
        super().resizeEvent(event)

        # プレビュー画像が設定されている場合は再スケーリング
        if self._preview_pixmap is not None and not self._preview_pixmap.isNull():
            self._display_scaled_image()
