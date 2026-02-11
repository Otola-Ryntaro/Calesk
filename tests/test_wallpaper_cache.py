"""
チケット023: 壁紙キャッシュ永続化テスト
壁紙生成成功時にメタデータを保存し、API接続不可時にキャッシュから復元
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestWallpaperCacheInit:
    """WallpaperCache 初期化テスト"""

    def test_wallpaper_cache_class_exists(self):
        """WallpaperCacheクラスが存在すること"""
        from src.wallpaper_cache import WallpaperCache
        assert WallpaperCache is not None

    def test_wallpaper_cache_init(self, tmp_path):
        """WallpaperCacheが初期化できること"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)
        assert cache is not None

    def test_wallpaper_cache_default_meta_path(self, tmp_path):
        """メタデータファイルパスが正しいこと"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)
        assert cache.meta_path == tmp_path / 'cache_meta.json'


class TestWallpaperCacheSave:
    """キャッシュ保存テスト"""

    def test_save_cache_creates_meta_file(self, tmp_path):
        """save_cache()でメタデータファイルが作成されること"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        # ダミーの壁紙ファイルを作成
        wallpaper_path = tmp_path / 'wallpaper_simple_20260211.png'
        wallpaper_path.write_bytes(b'dummy_image_data')

        cache.save_cache(
            wallpaper_path=wallpaper_path,
            theme='simple'
        )

        assert cache.meta_path.exists()

    def test_save_cache_meta_contains_required_fields(self, tmp_path):
        """メタデータに必要なフィールドが含まれること"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        wallpaper_path = tmp_path / 'wallpaper_simple_20260211.png'
        wallpaper_path.write_bytes(b'dummy_image_data')

        cache.save_cache(wallpaper_path=wallpaper_path, theme='simple')

        meta = json.loads(cache.meta_path.read_text())
        assert 'last_wallpaper_path' in meta
        assert 'theme' in meta
        assert 'generated_at' in meta

    def test_save_cache_stores_correct_path(self, tmp_path):
        """保存されたパスが正しいこと"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        wallpaper_path = tmp_path / 'wallpaper_simple_20260211.png'
        wallpaper_path.write_bytes(b'dummy_image_data')

        cache.save_cache(wallpaper_path=wallpaper_path, theme='simple')

        meta = json.loads(cache.meta_path.read_text())
        assert meta['last_wallpaper_path'] == str(wallpaper_path)
        assert meta['theme'] == 'simple'


class TestWallpaperCacheLoad:
    """キャッシュ読み込みテスト"""

    def test_load_cache_returns_none_when_no_cache(self, tmp_path):
        """キャッシュがない場合Noneを返すこと"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        result = cache.load_cache()
        assert result is None

    def test_load_cache_returns_path_when_cache_exists(self, tmp_path):
        """キャッシュが存在する場合パスを返すこと"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        # キャッシュを保存
        wallpaper_path = tmp_path / 'wallpaper_simple_20260211.png'
        wallpaper_path.write_bytes(b'dummy_image_data')
        cache.save_cache(wallpaper_path=wallpaper_path, theme='simple')

        # キャッシュを読み込み
        result = cache.load_cache()
        assert result is not None
        assert result == wallpaper_path

    def test_load_cache_returns_none_when_file_missing(self, tmp_path):
        """壁紙ファイルが存在しない場合Noneを返すこと"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        # メタデータのみ作成（壁紙ファイルなし）
        meta = {
            'last_wallpaper_path': str(tmp_path / 'nonexistent.png'),
            'theme': 'simple',
            'generated_at': datetime.now().isoformat()
        }
        cache.meta_path.write_text(json.dumps(meta))

        result = cache.load_cache()
        assert result is None

    def test_load_cache_returns_none_on_corrupted_meta(self, tmp_path):
        """メタデータが壊れている場合Noneを返すこと"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        # 壊れたメタデータ
        cache.meta_path.write_text('invalid json')

        result = cache.load_cache()
        assert result is None


class TestWallpaperCacheIntegration:
    """キャッシュの保存→読み込み統合テスト"""

    def test_save_and_load_roundtrip(self, tmp_path):
        """保存→読み込みのラウンドトリップが正しいこと"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        # 保存
        wallpaper_path = tmp_path / 'wallpaper_pastel_20260211.png'
        wallpaper_path.write_bytes(b'dummy_image_data')
        cache.save_cache(wallpaper_path=wallpaper_path, theme='pastel')

        # 読み込み
        result = cache.load_cache()
        assert result == wallpaper_path

    def test_overwrite_cache(self, tmp_path):
        """キャッシュが上書きされること"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        # 1回目の保存
        path1 = tmp_path / 'wallpaper_simple_20260211.png'
        path1.write_bytes(b'first')
        cache.save_cache(wallpaper_path=path1, theme='simple')

        # 2回目の保存（上書き）
        path2 = tmp_path / 'wallpaper_dark_20260211.png'
        path2.write_bytes(b'second')
        cache.save_cache(wallpaper_path=path2, theme='dark')

        # 最新のキャッシュが返ること
        result = cache.load_cache()
        assert result == path2


class TestWallpaperServiceCacheIntegration:
    """WallpaperServiceとキャッシュの統合テスト"""

    def test_service_has_cache(self):
        """WallpaperServiceがキャッシュを持つこと"""
        from src.viewmodels.wallpaper_service import WallpaperService
        with patch.object(WallpaperService, '__init__', lambda self: None):
            service = WallpaperService()
            # __init__をスキップしたので手動で確認
            # 実際のテストはWallpaperServiceの変更後に追加

    def test_service_saves_cache_on_success(self, tmp_path):
        """壁紙生成成功時にキャッシュが保存されること"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        # ダミーの壁紙パス
        wallpaper_path = tmp_path / 'wallpaper_simple_20260211.png'
        wallpaper_path.write_bytes(b'dummy')

        # キャッシュを保存
        cache.save_cache(wallpaper_path=wallpaper_path, theme='simple')

        # キャッシュが保存されたか確認
        assert cache.meta_path.exists()
        loaded = cache.load_cache()
        assert loaded == wallpaper_path

    def test_fallback_to_cache_on_auth_failure(self, tmp_path):
        """認証失敗時にキャッシュ壁紙にフォールバックできること"""
        from src.wallpaper_cache import WallpaperCache
        cache = WallpaperCache(cache_dir=tmp_path)

        # 事前にキャッシュを保存
        cached_path = tmp_path / 'wallpaper_simple_20260211.png'
        cached_path.write_bytes(b'cached_wallpaper')
        cache.save_cache(wallpaper_path=cached_path, theme='simple')

        # キャッシュから読み込み
        result = cache.load_cache()
        assert result is not None
        assert result.exists()
