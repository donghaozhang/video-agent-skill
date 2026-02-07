"""
XDG-compliant path resolution for AI Content Pipeline.

Follows the XDG Base Directory Specification on Linux/Mac.
Uses %APPDATA% / %LOCALAPPDATA% on Windows.

Hierarchy (highest priority first):
1. CLI flags (--config, --cache-dir, --state-dir)
2. Environment variables (XDG_CONFIG_HOME, XDG_CACHE_HOME, XDG_STATE_HOME)
3. Platform defaults (~/.config, ~/.cache, ~/.local/state on Unix)
"""

import os
import sys
from pathlib import Path

APP_NAME = "video-ai-studio"


def config_dir() -> Path:
    """Return the configuration directory.

    Resolution order:
    - $XDG_CONFIG_HOME/video-ai-studio (if set)
    - %APPDATA%/video-ai-studio (Windows)
    - ~/.config/video-ai-studio (Unix)
    """
    if xdg := os.environ.get("XDG_CONFIG_HOME"):
        return Path(xdg) / APP_NAME
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", str(Path.home()))
        return Path(base) / APP_NAME
    return Path.home() / ".config" / APP_NAME


def cache_dir() -> Path:
    """Return the cache directory.

    Resolution order:
    - $XDG_CACHE_HOME/video-ai-studio (if set)
    - %LOCALAPPDATA%/video-ai-studio/cache (Windows)
    - ~/.cache/video-ai-studio (Unix)
    """
    if xdg := os.environ.get("XDG_CACHE_HOME"):
        return Path(xdg) / APP_NAME
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", str(Path.home()))
        return Path(base) / APP_NAME / "cache"
    return Path.home() / ".cache" / APP_NAME


def state_dir() -> Path:
    """Return the state directory (logs, history, runtime data).

    Resolution order:
    - $XDG_STATE_HOME/video-ai-studio (if set)
    - %LOCALAPPDATA%/video-ai-studio/state (Windows)
    - ~/.local/state/video-ai-studio (Unix)
    """
    if xdg := os.environ.get("XDG_STATE_HOME"):
        return Path(xdg) / APP_NAME
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", str(Path.home()))
        return Path(base) / APP_NAME / "state"
    return Path.home() / ".local" / "state" / APP_NAME


def default_config_path() -> Path:
    """Return the default config file path."""
    return config_dir() / "config.yaml"


def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist, return path."""
    path.mkdir(parents=True, exist_ok=True)
    return path
