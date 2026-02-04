"""
WallpaperSetter のセキュリティテスト
"""
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
import pytest

from src.wallpaper_setter import WallpaperSetter


class TestAppleScriptInjection:
    """AppleScript コマンドインジェクション脆弱性のテスト"""

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_mac_wallpaper_sanitizes_malicious_path(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        TDD: 悪意のあるファイルパスでコマンドインジェクションが発生しないことを確認

        セキュリティ要件:
        - AppleScript内に挿入されるパスは適切にエスケープされる必要がある
        - 引用符やセミコロンなどの特殊文字を含むパスでも安全に処理される
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True  # ファイルが存在すると仮定

        # 通常サイズのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024  # 5MB
        mock_stat.return_value = mock_stat_result

        setter = WallpaperSetter()

        # 悪意のあるパス（引用符とコマンド挿入を試みる）
        malicious_path = Path('/tmp/"; do shell script "rm -rf /"; ".png')

        # Execute
        result = setter.set_wallpaper(malicious_path)

        # Assert: メソッドが実行される
        assert result is True, "set_wallpaper が失敗した"

        # Assert: subprocess.run が呼ばれた
        assert mock_subprocess_run.called, "subprocess.run が呼ばれていない"

        # Assert: 渡されたスクリプトを確認
        call_args = mock_subprocess_run.call_args
        script_arg = call_args[0][0][2]  # ['osascript', '-e', script] の script部分

        # Assert: 悪意のあるコマンドがエスケープされている
        # 引用符がエスケープされていることを確認
        assert '\\"' in script_arg or '\\\\' in script_arg, \
            f"引用符がエスケープされていない。スクリプト: {script_arg}"

        # Assert: 元の悪意のある文字列がそのまま含まれていない
        assert 'do shell script "rm -rf /"' not in script_arg, \
            f"危険なコマンドがエスケープされていない。スクリプト: {script_arg}"

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_mac_wallpaper_handles_quotes_in_path(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        通常の引用符を含むパス（正当なファイル名）が正しく処理されることを確認
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True

        # 通常サイズのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024
        mock_stat.return_value = mock_stat_result

        setter = WallpaperSetter()

        # 引用符を含む正当なパス
        path_with_quotes = Path('/tmp/My "Vacation" Photo.png')

        # Execute
        result = setter.set_wallpaper(path_with_quotes)

        # Assert
        assert result is True
        assert mock_subprocess_run.called

        # スクリプトが正しくエスケープされている
        call_args = mock_subprocess_run.call_args
        script_arg = call_args[0][0][2]
        assert '\\"' in script_arg or '\\\\' in script_arg

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_mac_wallpaper_handles_normal_path(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        通常のパス（特殊文字なし）が正しく処理されることを確認
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True

        # 通常サイズのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024
        mock_stat.return_value = mock_stat_result

        setter = WallpaperSetter()

        # 通常のパス
        normal_path = Path('/tmp/wallpaper.png')

        # Execute
        result = setter.set_wallpaper(normal_path)

        # Assert
        assert result is True
        assert mock_subprocess_run.called


class TestKDEJavaScriptInjection:
    """KDE Plasma JavaScript コマンドインジェクション脆弱性のテスト"""

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_kde_wallpaper_sanitizes_malicious_path(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        TDD: KDE Plasma で悪意のあるファイルパスでJavaScript注入が発生しないことを確認

        セキュリティ要件:
        - JavaScript/QMLコード内に挿入されるパスは適切にエスケープされる必要がある
        - 引用符、バックスラッシュ、改行などの特殊文字を含むパスでも安全に処理される
        """
        # Setup - GNOME失敗、KDE成功のシミュレーション
        mock_system.return_value = 'Linux'
        mock_exists.return_value = True

        # 通常サイズのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024
        mock_stat.return_value = mock_stat_result

        # GNOME gsettingsは失敗
        gnome_error = subprocess.CalledProcessError(1, 'gsettings', stderr='command not found')
        # KDE qdbusは成功
        kde_success = Mock(returncode=0)

        # 最初の呼び出し（GNOME）は失敗、2回目（KDE）は成功
        mock_subprocess_run.side_effect = [gnome_error, kde_success]

        setter = WallpaperSetter()

        # 悪意のあるパス（JavaScriptインジェクションを試みる）
        malicious_path = Path('/tmp/"; eval("malicious code"); ".png')

        # Execute
        result = setter.set_wallpaper(malicious_path)

        # Assert: メソッドが実行される
        assert result is True, "set_wallpaper が失敗した"

        # Assert: subprocess.run が2回呼ばれた（GNOME失敗 → KDE成功）
        assert mock_subprocess_run.call_count == 2, "subprocess.run が2回呼ばれていない"

        # Assert: KDEコマンド（2回目の呼び出し）を確認
        kde_call_args = mock_subprocess_run.call_args_list[1]
        kde_script = kde_call_args[0][0][4]  # evaluateScript の引数（5番目の要素）

        # Assert: 悪意のあるコードがエスケープされている
        # 引用符がエスケープされていることを確認
        assert '\\"' in kde_script or '\\\\' in kde_script, \
            f"引用符がエスケープされていない。スクリプト: {kde_script}"

        # Assert: 元の悪意のあるコードがそのまま含まれていない
        assert 'eval("malicious code")' not in kde_script, \
            f"危険なコードがエスケープされていない。スクリプト: {kde_script}"

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_kde_wallpaper_handles_quotes_in_path(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        KDE: 引用符を含むパス（正当なファイル名）が正しく処理されることを確認
        """
        # Setup
        mock_system.return_value = 'Linux'
        mock_exists.return_value = True

        # 通常サイズのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024
        mock_stat.return_value = mock_stat_result

        gnome_error = subprocess.CalledProcessError(1, 'gsettings', stderr='command not found')
        kde_success = Mock(returncode=0)
        mock_subprocess_run.side_effect = [gnome_error, kde_success]

        setter = WallpaperSetter()

        # 引用符を含む正当なパス
        path_with_quotes = Path('/tmp/My "Vacation" Photo.png')

        # Execute
        result = setter.set_wallpaper(path_with_quotes)

        # Assert
        assert result is True
        assert mock_subprocess_run.call_count == 2

        # KDEスクリプトが正しくエスケープされている
        kde_call_args = mock_subprocess_run.call_args_list[1]
        kde_script = kde_call_args[0][0][4]  # evaluateScript の引数（5番目の要素）
        assert '\\"' in kde_script or '\\\\' in kde_script


class TestAppleScriptControlCharacters:
    """AppleScript 改行/制御文字対応のテスト"""

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_mac_wallpaper_handles_newline_in_path(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        TDD: 改行文字を含むパスでAppleScript文字列が壊れないことを確認

        セキュリティ要件:
        - AppleScript文字列リテラル内の改行（\n、\r）はエスケープされる必要がある
        - 改行があってもスクリプトが正常に実行される
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True

        # 通常サイズのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024
        mock_stat.return_value = mock_stat_result

        setter = WallpaperSetter()

        # 改行を含むパス（まれだが技術的に可能）
        path_with_newline = Path('/tmp/file\nwith\nnewline.png')

        # Execute
        result = setter.set_wallpaper(path_with_newline)

        # Assert
        assert result is True
        assert mock_subprocess_run.called

        # スクリプトに改行がエスケープされている
        call_args = mock_subprocess_run.call_args
        script_arg = call_args[0][0][2]

        # 生の改行文字がスクリプト内にないことを確認
        # （エスケープされた \\n または実際の改行がない）
        assert 'file\nwith\nnewline' not in script_arg or '\\n' in script_arg, \
            f"改行がエスケープされていない。スクリプト: {script_arg}"

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_mac_wallpaper_handles_carriage_return(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        TDD: キャリッジリターン（\r）を含むパスでAppleScript文字列が壊れないことを確認
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True

        # 通常サイズのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024
        mock_stat.return_value = mock_stat_result

        setter = WallpaperSetter()

        # キャリッジリターンを含むパス
        path_with_cr = Path('/tmp/file\rwith\rCR.png')

        # Execute
        result = setter.set_wallpaper(path_with_cr)

        # Assert
        assert result is True
        assert mock_subprocess_run.called

        call_args = mock_subprocess_run.call_args
        script_arg = call_args[0][0][2]

        # 生のキャリッジリターンがエスケープされている
        assert 'file\rwith\rCR' not in script_arg or '\\r' in script_arg, \
            f"キャリッジリターンがエスケープされていない。スクリプト: {script_arg}"


class TestPathValidation:
    """ファイルパス検証のテスト"""

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_rejects_non_image_file_extension(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        TDD: 画像ファイル以外の拡張子を拒否することを確認

        セキュリティ要件:
        - .png, .jpg, .jpeg, .bmp, .gif などの画像形式のみ許可
        - .exe, .sh, .bat などの実行ファイルは拒否
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_exists.return_value = True

        # 通常サイズのファイルをシミュレート（拡張子チェックで先に失敗するが）
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024
        mock_stat.return_value = mock_stat_result

        setter = WallpaperSetter()

        # 実行ファイル拡張子
        executable_path = Path('/tmp/malicious.exe')

        # Execute
        result = setter.set_wallpaper(executable_path)

        # Assert: 拒否される
        assert result is False, "実行ファイル拡張子が拒否されなかった"
        # subprocess.run は呼ばれない
        assert not mock_subprocess_run.called, "不正な拡張子でsubprocess.runが呼ばれた"

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_accepts_valid_image_extensions(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        TDD: 有効な画像拡張子を受け入れることを確認
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True

        # 通常サイズのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024  # 5MB
        mock_stat.return_value = mock_stat_result

        setter = WallpaperSetter()

        # 各種画像形式をテスト
        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.PNG', '.JPG']

        for ext in valid_extensions:
            mock_subprocess_run.reset_mock()
            image_path = Path(f'/tmp/wallpaper{ext}')

            # Execute
            result = setter.set_wallpaper(image_path)

            # Assert: 受け入れられる
            assert result is True, f"有効な拡張子 {ext} が拒否された"
            assert mock_subprocess_run.called, f"拡張子 {ext} でsubprocess.runが呼ばれなかった"

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_rejects_oversized_file(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        TDD: 過大なファイルサイズを拒否することを確認

        セキュリティ要件:
        - ファイルサイズに上限を設定（例: 50MB）
        - DoS攻撃や誤った巨大ファイルの設定を防止
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_exists.return_value = True

        # 100MBのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 100 * 1024 * 1024  # 100MB
        mock_stat.return_value = mock_stat_result

        setter = WallpaperSetter()
        large_file = Path('/tmp/huge_image.png')

        # Execute
        result = setter.set_wallpaper(large_file)

        # Assert: 拒否される
        assert result is False, "過大なファイルサイズが拒否されなかった"
        assert not mock_subprocess_run.called, "過大なファイルでsubprocess.runが呼ばれた"

    @patch('src.wallpaper_setter.subprocess.run')
    @patch('src.wallpaper_setter.platform.system')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_accepts_normal_sized_file(
        self,
        mock_stat,
        mock_exists,
        mock_system,
        mock_subprocess_run
    ):
        """
        TDD: 通常サイズのファイルを受け入れることを確認
        """
        # Setup
        mock_system.return_value = 'Darwin'
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_exists.return_value = True

        # 5MBのファイルをシミュレート
        mock_stat_result = Mock()
        mock_stat_result.st_size = 5 * 1024 * 1024  # 5MB
        mock_stat.return_value = mock_stat_result

        setter = WallpaperSetter()
        normal_file = Path('/tmp/wallpaper.png')

        # Execute
        result = setter.set_wallpaper(normal_file)

        # Assert: 受け入れられる
        assert result is True, "通常サイズのファイルが拒否された"
        assert mock_subprocess_run.called, "通常サイズのファイルでsubprocess.runが呼ばれなかった"
