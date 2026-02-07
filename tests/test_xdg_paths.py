"""Tests for XDG path resolution.

Tests the cli.paths module which provides:
- XDG-compliant config/cache/state directory resolution
- Platform-specific defaults (Windows APPDATA, Unix ~/.config)
- ensure_dir() helper for lazy directory creation
"""

import os
import sys
import pytest
from unittest.mock import patch
from pathlib import Path

from ai_content_pipeline.cli.paths import (
    config_dir, cache_dir, state_dir,
    default_config_path, ensure_dir, APP_NAME,
)


class TestAppName:
    def test_app_name_is_video_ai_studio(self):
        assert APP_NAME == "video-ai-studio"


class TestConfigDir:
    def test_uses_xdg_config_home(self):
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            result = config_dir()
            assert result == Path("/custom/config") / APP_NAME

    def test_xdg_takes_priority_over_platform_default(self):
        """XDG env var takes priority even on Windows."""
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/xdg/override"}):
            result = config_dir()
            assert result == Path("/xdg/override") / APP_NAME

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-only test")
    def test_unix_fallback(self):
        env = os.environ.copy()
        env.pop("XDG_CONFIG_HOME", None)
        with patch.dict(os.environ, env, clear=True):
            result = config_dir()
            assert result == Path.home() / ".config" / APP_NAME

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
    def test_windows_uses_appdata(self):
        env = os.environ.copy()
        env.pop("XDG_CONFIG_HOME", None)
        with patch.dict(os.environ, env, clear=True):
            result = config_dir()
            appdata = os.environ.get("APPDATA", str(Path.home()))
            assert result == Path(appdata) / APP_NAME


class TestCacheDir:
    def test_uses_xdg_cache_home(self):
        with patch.dict(os.environ, {"XDG_CACHE_HOME": "/custom/cache"}):
            result = cache_dir()
            assert result == Path("/custom/cache") / APP_NAME

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-only test")
    def test_unix_fallback(self):
        env = os.environ.copy()
        env.pop("XDG_CACHE_HOME", None)
        with patch.dict(os.environ, env, clear=True):
            result = cache_dir()
            assert result == Path.home() / ".cache" / APP_NAME

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
    def test_windows_uses_localappdata(self):
        env = os.environ.copy()
        env.pop("XDG_CACHE_HOME", None)
        with patch.dict(os.environ, env, clear=True):
            result = cache_dir()
            localappdata = os.environ.get("LOCALAPPDATA", str(Path.home()))
            assert result == Path(localappdata) / APP_NAME / "cache"


class TestStateDir:
    def test_uses_xdg_state_home(self):
        with patch.dict(os.environ, {"XDG_STATE_HOME": "/custom/state"}):
            result = state_dir()
            assert result == Path("/custom/state") / APP_NAME

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-only test")
    def test_unix_fallback(self):
        env = os.environ.copy()
        env.pop("XDG_STATE_HOME", None)
        with patch.dict(os.environ, env, clear=True):
            result = state_dir()
            assert result == Path.home() / ".local" / "state" / APP_NAME

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
    def test_windows_uses_localappdata(self):
        env = os.environ.copy()
        env.pop("XDG_STATE_HOME", None)
        with patch.dict(os.environ, env, clear=True):
            result = state_dir()
            localappdata = os.environ.get("LOCALAPPDATA", str(Path.home()))
            assert result == Path(localappdata) / APP_NAME / "state"


class TestDefaultConfigPath:
    def test_is_yaml_file(self):
        path = default_config_path()
        assert path.suffix == ".yaml"
        assert path.name == "config.yaml"

    def test_is_inside_config_dir(self):
        path = default_config_path()
        assert path.parent == config_dir()


class TestEnsureDir:
    def test_creates_directory(self, tmp_path):
        target = tmp_path / "a" / "b" / "c"
        assert not target.exists()
        result = ensure_dir(target)
        assert target.exists()
        assert result == target

    def test_existing_directory_no_error(self, tmp_path):
        result = ensure_dir(tmp_path)
        assert result == tmp_path

    def test_returns_same_path(self, tmp_path):
        target = tmp_path / "new_dir"
        result = ensure_dir(target)
        assert result == target
