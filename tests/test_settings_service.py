"""
設定永続化サービスのテスト
ユーザー設定をJSONファイルに保存・読み込みする機能をテスト
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from src.viewmodels.settings_service import SettingsService


class TestSettingsServiceInit:
    """SettingsService 初期化テスト"""

    def test_settings_service_exists(self):
        """SettingsServiceクラスが存在すること"""
        assert SettingsService is not None

    def test_settings_service_initialization(self, tmp_path):
        """カスタムパスで初期化できること"""
        service = SettingsService(settings_dir=tmp_path)
        assert service.settings_dir == tmp_path

    def test_settings_file_path(self, tmp_path):
        """設定ファイルパスが正しいこと"""
        service = SettingsService(settings_dir=tmp_path)
        assert service.settings_file == tmp_path / "settings.json"


class TestSettingsServiceDefaults:
    """デフォルト設定テスト"""

    def test_default_theme(self, tmp_path):
        """デフォルトテーマがsimpleであること"""
        service = SettingsService(settings_dir=tmp_path)
        assert service.get("theme") == "simple"

    def test_default_auto_update_enabled(self, tmp_path):
        """デフォルトで自動更新が有効であること"""
        service = SettingsService(settings_dir=tmp_path)
        assert service.get("auto_update_enabled") is True

    def test_default_auto_update_interval(self, tmp_path):
        """デフォルト更新間隔が60分であること"""
        service = SettingsService(settings_dir=tmp_path)
        assert service.get("auto_update_interval_minutes") == 60

    def test_default_background_image(self, tmp_path):
        """デフォルト背景画像がpreset:形式であること"""
        from src.config import DEFAULT_PRESET_BACKGROUND
        service = SettingsService(settings_dir=tmp_path)
        expected = f"preset:{DEFAULT_PRESET_BACKGROUND}"
        assert service.get("background_image_path") == expected

    def test_default_auto_detect_resolution(self, tmp_path):
        """デフォルトで解像度自動検出が有効であること"""
        service = SettingsService(settings_dir=tmp_path)
        assert service.get("auto_detect_resolution") is True

    def test_get_unknown_key_returns_default(self, tmp_path):
        """未知のキーはdefault引数を返すこと"""
        service = SettingsService(settings_dir=tmp_path)
        assert service.get("nonexistent_key", "fallback") == "fallback"

    def test_get_unknown_key_returns_none(self, tmp_path):
        """未知のキーでdefault未指定はNoneを返すこと"""
        service = SettingsService(settings_dir=tmp_path)
        assert service.get("nonexistent_key") is None


class TestSettingsServiceSaveLoad:
    """設定の保存・読み込みテスト"""

    def test_set_and_get(self, tmp_path):
        """設定を書き込みして取得できること"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("theme", "dark")
        assert service.get("theme") == "dark"

    def test_save_creates_file(self, tmp_path):
        """保存でJSONファイルが作成されること"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("theme", "modern")
        service.save()
        assert (tmp_path / "settings.json").exists()

    def test_save_creates_directory(self, tmp_path):
        """保存時にディレクトリが自動作成されること"""
        nested = tmp_path / "subdir" / "config"
        service = SettingsService(settings_dir=nested)
        service.set("theme", "dark")
        service.save()
        assert nested.exists()
        assert (nested / "settings.json").exists()

    def test_save_and_load(self, tmp_path):
        """保存後に再読み込みで値が復元されること"""
        service1 = SettingsService(settings_dir=tmp_path)
        service1.set("theme", "vibrant")
        service1.set("auto_update_enabled", False)
        service1.set("auto_update_interval_minutes", 30)
        service1.save()

        service2 = SettingsService(settings_dir=tmp_path)
        service2.load()
        assert service2.get("theme") == "vibrant"
        assert service2.get("auto_update_enabled") is False
        assert service2.get("auto_update_interval_minutes") == 30

    def test_load_nonexistent_file(self, tmp_path):
        """存在しないファイルの読み込みでエラーにならないこと"""
        service = SettingsService(settings_dir=tmp_path)
        service.load()
        # デフォルト値が使われる
        assert service.get("theme") == "simple"

    def test_load_corrupted_file(self, tmp_path):
        """破損したJSONファイルでエラーにならないこと"""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("not valid json {{{")

        service = SettingsService(settings_dir=tmp_path)
        service.load()
        # デフォルト値が使われる
        assert service.get("theme") == "simple"

    def test_save_only_changed_values(self, tmp_path):
        """変更された値のみがJSONに保存されること"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("theme", "dark")
        service.save()

        data = json.loads((tmp_path / "settings.json").read_text())
        assert "theme" in data
        assert data["theme"] == "dark"

    def test_saved_json_is_valid(self, tmp_path):
        """保存されたJSONが正しいフォーマットであること"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("theme", "pastel")
        service.save()

        data = json.loads((tmp_path / "settings.json").read_text())
        assert isinstance(data, dict)


class TestSettingsServiceMultipleKeys:
    """複数設定値の操作テスト"""

    def test_get_all_settings(self, tmp_path):
        """全設定を辞書で取得できること"""
        service = SettingsService(settings_dir=tmp_path)
        all_settings = service.get_all()
        assert isinstance(all_settings, dict)
        assert "theme" in all_settings
        assert "auto_update_enabled" in all_settings

    def test_update_multiple(self, tmp_path):
        """複数設定を一括更新できること"""
        service = SettingsService(settings_dir=tmp_path)
        service.update({
            "theme": "dark",
            "auto_update_enabled": False,
            "auto_update_interval_minutes": 120,
        })
        assert service.get("theme") == "dark"
        assert service.get("auto_update_enabled") is False
        assert service.get("auto_update_interval_minutes") == 120

    def test_reset_to_defaults(self, tmp_path):
        """デフォルトにリセットできること"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("theme", "dark")
        service.reset()
        assert service.get("theme") == "simple"


class TestSettingsServiceValidation:
    """設定値のバリデーションテスト"""

    def test_set_unknown_key_ignored(self, tmp_path):
        """未知のキーはset()で無視されること"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("unknown_key", "value")
        assert service.get("unknown_key") is None

    def test_update_unknown_key_ignored(self, tmp_path):
        """update()で未知のキーが無視されること"""
        service = SettingsService(settings_dir=tmp_path)
        service.update({"unknown_key": "value", "theme": "dark"})
        assert service.get("unknown_key") is None
        assert service.get("theme") == "dark"

    def test_set_wrong_type_ignored(self, tmp_path):
        """型が不正な値はset()で無視されること"""
        service = SettingsService(settings_dir=tmp_path)
        original = service.get("auto_update_interval_minutes")
        service.set("auto_update_interval_minutes", "not_a_number")
        assert service.get("auto_update_interval_minutes") == original

    def test_set_bool_as_int_ignored(self, tmp_path):
        """bool型の設定にint値は無視されること"""
        service = SettingsService(settings_dir=tmp_path)
        original = service.get("auto_update_enabled")
        service.set("auto_update_enabled", 1)
        # Pythonではboolはintのサブクラスだが、intはboolではない
        # isinstance(1, bool) is Falseなので無視される
        assert service.get("auto_update_enabled") == original

    def test_load_ignores_unknown_keys(self, tmp_path):
        """load()で未知のキーが無視されること"""
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({
            "theme": "dark",
            "malicious_key": "evil_value",
            "another_unknown": 42,
        }))
        service = SettingsService(settings_dir=tmp_path)
        service.load()
        assert service.get("theme") == "dark"
        assert service.get("malicious_key") is None
        assert service.get("another_unknown") is None

    def test_save_returns_true_on_success(self, tmp_path):
        """save()が成功時にTrueを返すこと"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("theme", "dark")
        assert service.save() is True

    def test_save_returns_false_on_failure(self, tmp_path, monkeypatch):
        """save()が失敗時にFalseを返すこと"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("theme", "dark")

        # write_textを例外にモック
        monkeypatch.setattr(Path, "write_text", lambda *a, **kw: (_ for _ in ()).throw(PermissionError("denied")))
        assert service.save() is False

    def test_background_image_path_accepts_none(self, tmp_path):
        """background_image_pathにNoneを設定できること"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("background_image_path", None)
        assert service.get("background_image_path") is None

    def test_background_image_path_accepts_string(self, tmp_path):
        """background_image_pathに文字列を設定できること"""
        service = SettingsService(settings_dir=tmp_path)
        service.set("background_image_path", "/path/to/image.png")
        assert service.get("background_image_path") == "/path/to/image.png"
