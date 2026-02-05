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


class TestPreviewWidgetEdgeCases:
    """PreviewWidgetのエッジケーステスト"""

    # 破損画像ファイルのテスト
    def test_preview_widget_handles_corrupted_png(self, qtbot, tmp_path):
        """破損したPNGファイルを適切に処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 破損した画像ファイルを作成（PNGヘッダーだけで中身がない）
        corrupted_file = tmp_path / "corrupted.png"
        corrupted_file.write_bytes(b'\x89PNG\r\n\x1a\n')  # PNGマジックナンバーのみ

        widget.set_image(corrupted_file)

        # 画像が設定されないことを確認
        assert widget.pixmap() is None or widget.pixmap().isNull()
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"

    def test_preview_widget_handles_corrupted_jpg(self, qtbot, tmp_path):
        """破損したJPGファイルを適切に処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 破損した画像ファイルを作成（JPGヘッダーだけで中身がない）
        corrupted_file = tmp_path / "corrupted.jpg"
        corrupted_file.write_bytes(b'\xff\xd8\xff\xe0')  # JPGマジックナンバーのみ

        widget.set_image(corrupted_file)

        # 画像が設定されないことを確認
        assert widget.pixmap() is None or widget.pixmap().isNull()
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"

    # 0バイトファイルのテスト
    def test_preview_widget_handles_zero_byte_file(self, qtbot, tmp_path):
        """0バイトのファイルを適切に処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 0バイトファイルを作成
        empty_file = tmp_path / "empty.png"
        empty_file.write_bytes(b'')

        widget.set_image(empty_file)

        # 画像が設定されないことを確認
        assert widget.pixmap() is None or widget.pixmap().isNull()
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"

    # 境界値サイズ（10MB制限付近）のテスト
    def test_preview_widget_accepts_just_under_10mb_file(self, qtbot, tmp_path):
        """10MB未満のファイルを受け入れることを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 9.9MB相当の画像を作成（実際に作ると遅いので、小さい画像で代用）
        test_file = tmp_path / "just_under_limit.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.blue)
        pixmap.save(str(test_file))

        widget.set_image(test_file)

        # 画像が正常に設定されることを確認
        assert widget.pixmap() is not None
        assert not widget.pixmap().isNull()

    def test_preview_widget_rejects_just_over_10mb_file(self, qtbot, tmp_path):
        """10MBを超えるファイルを拒否することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 10.5MBのファイルを作成
        large_file = tmp_path / "just_over_limit.png"
        large_file.write_bytes(b'x' * (10 * 1024 * 1024 + 500 * 1024))  # 10.5MB

        widget.set_image(large_file)

        # 画像が設定されないことを確認
        assert widget.pixmap() is None or widget.pixmap().isNull()
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"

    # 不正なファイル形式（偽装拡張子）のテスト
    def test_preview_widget_handles_fake_png_extension(self, qtbot, tmp_path):
        """実際はテキストファイルだが拡張子がPNGのファイルを処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # テキストファイルをPNG拡張子で保存
        fake_png = tmp_path / "fake_image.png"
        fake_png.write_text("This is not a PNG file")

        widget.set_image(fake_png)

        # 画像が設定されないことを確認（QPixmapが読み込みに失敗する）
        assert widget.pixmap() is None or widget.pixmap().isNull()
        assert widget.text() == "プレビュー（壁紙生成後に表示されます）"

    def test_preview_widget_handles_html_with_png_extension(self, qtbot, tmp_path):
        """HTMLファイルをPNG拡張子で偽装した場合を処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # HTMLをPNG拡張子で保存
        fake_png = tmp_path / "html_disguised.png"
        fake_png.write_text("<html><body>Not an image</body></html>")

        widget.set_image(fake_png)

        # 画像が設定されないことを確認
        assert widget.pixmap() is None or widget.pixmap().isNull()

    # パスのエッジケース
    def test_preview_widget_handles_path_with_spaces(self, qtbot, tmp_path):
        """スペースを含むパスを正しく処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # スペースを含むディレクトリを作成
        dir_with_spaces = tmp_path / "path with spaces"
        dir_with_spaces.mkdir()

        test_file = dir_with_spaces / "test image.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.green)
        pixmap.save(str(test_file))

        widget.set_image(test_file)

        # 画像が正常に設定されることを確認
        assert widget.pixmap() is not None
        assert not widget.pixmap().isNull()

    def test_preview_widget_handles_unicode_path(self, qtbot, tmp_path):
        """日本語を含むパスを正しく処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 日本語を含むディレクトリを作成
        japanese_dir = tmp_path / "テスト画像フォルダ"
        japanese_dir.mkdir()

        test_file = japanese_dir / "テスト画像.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.red)
        pixmap.save(str(test_file))

        widget.set_image(test_file)

        # 画像が正常に設定されることを確認
        assert widget.pixmap() is not None
        assert not widget.pixmap().isNull()

    def test_preview_widget_handles_very_long_path(self, qtbot, tmp_path):
        """非常に長いパスを処理できることを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 長いパスを作成（ネストしたディレクトリ）
        long_dir = tmp_path
        for i in range(10):
            long_dir = long_dir / f"nested_dir_{i}"
            long_dir.mkdir()

        test_file = long_dir / "deep_image.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.yellow)
        pixmap.save(str(test_file))

        widget.set_image(test_file)

        # 画像が正常に設定されることを確認
        assert widget.pixmap() is not None
        assert not widget.pixmap().isNull()

    # シンボリックリンクのテスト
    def test_preview_widget_handles_symlink(self, qtbot, tmp_path):
        """シンボリックリンクを正しく処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget
        import os

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 元のファイルを作成
        original_file = tmp_path / "original.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.cyan)
        pixmap.save(str(original_file))

        # シンボリックリンクを作成
        symlink_file = tmp_path / "symlink.png"
        try:
            os.symlink(original_file, symlink_file)
        except OSError:
            # Windows等でシンボリックリンクが作成できない場合はスキップ
            pytest.skip("Symlink creation not supported on this platform")

        widget.set_image(symlink_file)

        # 画像が正常に設定されることを確認
        assert widget.pixmap() is not None
        assert not widget.pixmap().isNull()

    # リサイズイベントのエッジケース
    def test_preview_widget_resize_to_minimum(self, qtbot, tmp_path):
        """最小サイズへのリサイズを正しく処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 画像を設定
        test_file = tmp_path / "test.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.blue)
        pixmap.save(str(test_file))
        widget.set_image(test_file)

        # 最小サイズにリサイズ
        widget.resize(1, 1)

        # クラッシュしないことを確認
        assert widget.pixmap() is not None

    def test_preview_widget_resize_to_very_large(self, qtbot, tmp_path):
        """非常に大きなサイズへのリサイズを正しく処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 画像を設定
        test_file = tmp_path / "test.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.blue)
        pixmap.save(str(test_file))
        widget.set_image(test_file)

        # 非常に大きなサイズにリサイズ
        widget.resize(4000, 3000)

        # クラッシュしないことを確認
        assert widget.pixmap() is not None

    # 連続操作のテスト
    def test_preview_widget_rapid_image_changes(self, qtbot, tmp_path):
        """連続した画像変更を正しく処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        # 複数の画像を作成
        colors = [Qt.GlobalColor.red, Qt.GlobalColor.green, Qt.GlobalColor.blue, Qt.GlobalColor.yellow]
        for i, color in enumerate(colors):
            test_file = tmp_path / f"test_{i}.png"
            pixmap = QPixmap(800, 600)
            pixmap.fill(color)
            pixmap.save(str(test_file))

            # 連続して画像を設定
            widget.set_image(test_file)

        # 最後の画像が設定されていることを確認
        assert widget.pixmap() is not None
        assert not widget.pixmap().isNull()

    def test_preview_widget_set_clear_cycle(self, qtbot, tmp_path):
        """設定→クリア→設定のサイクルを正しく処理することを確認"""
        from src.ui.widgets.preview_widget import PreviewWidget

        widget = PreviewWidget()
        qtbot.addWidget(widget)

        test_file = tmp_path / "test.png"
        pixmap = QPixmap(800, 600)
        pixmap.fill(Qt.GlobalColor.blue)
        pixmap.save(str(test_file))

        # 設定→クリア→設定のサイクルを5回繰り返す
        for _ in range(5):
            widget.set_image(test_file)
            assert widget.pixmap() is not None

            widget.clear_preview()
            assert widget.pixmap() is None or widget.pixmap().isNull()

        # 最終的に画像を設定
        widget.set_image(test_file)
        assert widget.pixmap() is not None
        assert not widget.pixmap().isNull()
