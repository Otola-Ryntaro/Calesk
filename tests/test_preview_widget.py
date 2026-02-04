"""
PreviewWidgetのテスト

壁紙プレビュー表示ウィジェットをテストします。
"""

import pytest
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path


class TestPreviewWidget:
    """PreviewWidgetの基本機能をテストする"""

    def test_preview_widget_exists(self, qtbot):
        """PreviewWidgetクラスが存在することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        assert PreviewWidget is not None
        assert issubclass(PreviewWidget, QLabel)

    def test_preview_widget_initialization(self, qtbot):
        """PreviewWidgetが正しく初期化されることを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        assert widget is not None
        assert isinstance(widget, QLabel)
        assert widget.alignment() == Qt.AlignmentFlag.AlignCenter

    def test_preview_widget_has_placeholder(self, qtbot):
        """初期状態でプレースホルダーテキストが表示されることを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # プレースホルダーテキストが表示されている
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"

    def test_preview_widget_set_image(self, qtbot, tmp_path):
        """画像を設定できることを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # テスト用の画像を作成
        test_image_path = tmp_path / "test_wallpaper.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.blue)
        pixmap.save(str(test_image_path))

        # 画像を設定
        widget.set_image(test_image_path)

        # プレースホルダーテキストが消えて画像が表示される
        assert widget.text() == ""
        assert widget.pixmap() is not None
        assert not widget.pixmap().isNull()

    def test_preview_widget_set_image_with_scaling(self, qtbot, tmp_path):
        """画像がスケーリングされて表示されることを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        widget.resize(400, 300)  # ウィジェットサイズを設定
        qtbot.addWidget(widget)

        # 大きな画像を作成
        test_image_path = tmp_path / "large_wallpaper.png"
        pixmap = QPixmap(1920, 1080)
        pixmap.fill(Qt.GlobalColor.red)
        pixmap.save(str(test_image_path))

        # 画像を設定
        widget.set_image(test_image_path)

        # 画像が表示される
        assert widget.pixmap() is not None
        # スケーリングされている（元のサイズより小さい）
        displayed_pixmap = widget.pixmap()
        assert displayed_pixmap.width() <= 400
        assert displayed_pixmap.height() <= 300

    def test_preview_widget_set_nonexistent_image(self, qtbot):
        """存在しない画像を設定した場合の動作を確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 存在しないパスを指定
        nonexistent_path = Path("/tmp/nonexistent_image.png")
        widget.set_image(nonexistent_path)

        # プレースホルダーテキストが維持される
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"
        # 画像は設定されない
        assert widget.pixmap() is None or widget.pixmap().isNull()

    def test_preview_widget_clear(self, qtbot, tmp_path):
        """画像をクリアできることを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # まず画像を設定
        test_image_path = tmp_path / "test_wallpaper.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.green)
        pixmap.save(str(test_image_path))
        widget.set_image(test_image_path)

        # クリア
        widget.clear_preview()

        # プレースホルダーテキストに戻る
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"
        assert widget.pixmap() is None or widget.pixmap().isNull()

    # HIGH-3: ファイルパス検証テスト
    def test_preview_widget_reject_directory_traversal(self, qtbot, tmp_path):
        """ディレクトリトラバーサル攻撃を防ぐことを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # ディレクトリトラバーサルを試みる
        malicious_path = tmp_path / ".." / ".." / "etc" / "passwd"
        widget.set_image(malicious_path)

        # 画像が設定されないことを確認
        assert widget.pixmap() is None or widget.pixmap().isNull()
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"

    def test_preview_widget_reject_invalid_extension(self, qtbot, tmp_path):
        """許可されていない拡張子を拒否することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 許可されていない拡張子のファイル
        invalid_file = tmp_path / "malicious.exe"
        invalid_file.write_bytes(b"dummy content")

        widget.set_image(invalid_file)

        # 画像が設定されないことを確認
        assert widget.pixmap() is None or widget.pixmap().isNull()
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"

    def test_preview_widget_reject_large_file(self, qtbot, tmp_path):
        """10MB以上のファイルを拒否することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 10MB以上のファイルを作成（実際には小さいファイルをモック）
        large_file = tmp_path / "large_image.png"
        # 実際に10MBのファイルを作成するのは時間がかかるため、
        # ファイルサイズチェックをモック可能にする必要がある
        # ここでは一旦小さいファイルを作成し、実装側でサイズチェックロジックを確認
        large_file.write_bytes(b"x" * (11 * 1024 * 1024))  # 11MB

        widget.set_image(large_file)

        # 画像が設定されないことを確認（ファイルサイズ超過）
        assert widget.pixmap() is None or widget.pixmap().isNull()
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"

    def test_preview_widget_accept_valid_extensions(self, qtbot, tmp_path):
        """許可された拡張子を受け入れることを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 許可された拡張子のファイル（PNG, JPG, JPEG）
        valid_extensions = [".png", ".jpg", ".jpeg"]

        for ext in valid_extensions:
            test_file = tmp_path / f"test{ext}"
            pixmap = QPixmap(800, 600)
            pixmap.fill(Qt.GlobalColor.blue)
            pixmap.save(str(test_file))

            widget.set_image(test_file)

            # 画像が正常に設定されることを確認
            assert widget.pixmap() is not None
            assert not widget.pixmap().isNull()

            # クリアして次のテスト
            widget.clear_preview()

    # MEDIUM-4: メモリ管理最適化テスト
    def test_preview_widget_creates_thumbnail_for_large_images(self, qtbot, tmp_path):
        """大きな画像がサムネイル化されることを確認（最大640x360）"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 4K画像を作成（3840x2160）
        large_image_path = tmp_path / "4k_image.png"
        pixmap = QPixmap(3840, 2160)
        pixmap.fill(Qt.GlobalColor.cyan)
        pixmap.save(str(large_image_path))

        # 画像を設定
        widget.set_image(large_image_path)

        # 内部で保持しているプレビューPixmapが640x360以下であることを確認
        # _preview_pixmap が存在し、元画像より小さいことを確認
        assert hasattr(widget, '_preview_pixmap')
        assert widget._preview_pixmap is not None
        assert widget._preview_pixmap.width() <= 640
        assert widget._preview_pixmap.height() <= 360

    def test_preview_widget_stores_path_not_full_pixmap(self, qtbot, tmp_path):
        """元画像のPixmapではなくパスのみ保持することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # テスト画像を作成
        test_image_path = tmp_path / "test_image.png"
        pixmap = QPixmap(1920, 1080)
        pixmap.fill(Qt.GlobalColor.magenta)
        pixmap.save(str(test_image_path))

        # 画像を設定
        widget.set_image(test_image_path)

        # _original_pixmap は存在しないか None であることを確認
        # 代わりに _image_path が保持されていることを確認
        assert not hasattr(widget, '_original_pixmap') or widget._original_pixmap is None
        assert hasattr(widget, '_image_path')
        assert widget._image_path == test_image_path

    def test_preview_widget_memory_efficiency(self, qtbot, tmp_path):
        """メモリ効率が向上していることを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 8K画像を作成（7680x4320）
        large_image_path = tmp_path / "8k_image.png"
        pixmap = QPixmap(7680, 4320)
        pixmap.fill(Qt.GlobalColor.yellow)
        pixmap.save(str(large_image_path))

        # 画像を設定
        widget.set_image(large_image_path)

        # プレビューPixmapのサイズが元画像より大幅に小さいことを確認
        # 8K (7680x4320) → 最大640x360
        preview_pixmap = widget._preview_pixmap
        assert preview_pixmap.width() <= 640
        assert preview_pixmap.height() <= 360

        # プレビューPixmapのメモリ使用量が元画像の10%以下であることを確認
        # (面積比較: 640x360 = 230,400ピクセル vs 7680x4320 = 33,177,600ピクセル)
        preview_area = preview_pixmap.width() * preview_pixmap.height()
        original_area = 7680 * 4320
        efficiency_ratio = preview_area / original_area

        assert efficiency_ratio < 0.1  # 10%以下
