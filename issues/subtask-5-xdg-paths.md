# Subtask 5: XDG Config/Cache/State Paths

**Parent**: [plan-unix-style-migration.md](plan-unix-style-migration.md)
**Depends on**: None (can be done in parallel with subtasks 1-4)
**Estimated Time**: 45 minutes

---

## Objective

Follow XDG Base Directory Specification for config, cache, and state directories. Provide sensible defaults on all platforms. Allow CLI overrides (`--config`, `--cache-dir`, `--state-dir`).

---

## Step-by-Step Implementation

### Step 1: Create `cli/paths.py`

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/cli/paths.py`

```python
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
```

### Step 2: Add CLI overrides to `__main__.py`

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

Add global arguments:

```python
parser.add_argument('--config-dir', default=None,
    help='Override config directory (default: XDG_CONFIG_HOME/video-ai-studio)')
parser.add_argument('--cache-dir', default=None,
    help='Override cache directory (default: XDG_CACHE_HOME/video-ai-studio)')
parser.add_argument('--state-dir', default=None,
    help='Override state directory (default: XDG_STATE_HOME/video-ai-studio)')
```

After parsing args, resolve paths:

```python
from .cli.paths import config_dir, cache_dir, state_dir

resolved_config_dir = Path(args.config_dir) if args.config_dir else config_dir()
resolved_cache_dir = Path(args.cache_dir) if args.cache_dir else cache_dir()
resolved_state_dir = Path(args.state_dir) if args.state_dir else state_dir()
```

### Step 3: Use XDG cache in pipeline manager

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py`

Currently temp files go to `./temp/`. Optionally use XDG cache:

```python
from ..cli.paths import cache_dir

class AIPipelineManager:
    def __init__(self, base_dir=None, use_xdg_cache=False):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.output_dir = self.base_dir / "output"

        if use_xdg_cache:
            self.temp_dir = cache_dir() / "temp"
        else:
            self.temp_dir = self.base_dir / "temp"
        # ...
```

### Step 4: Use XDG config for .env lookup

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

In the `setup_env()` function, suggest the XDG config location:

```python
from .cli.paths import config_dir

def setup_env(args, output):
    xdg_config = config_dir()
    output.info(f"Config directory: {xdg_config}")
    # ... create .env in project root (backward compatible) ...
    # ... but also mention XDG location for future use ...
```

### Step 5: Write tests

**File**: `tests/test_xdg_paths.py`

```python
"""Tests for XDG path resolution."""

import os
import sys
import pytest
from unittest.mock import patch
from pathlib import Path

from ai_content_pipeline.cli.paths import (
    config_dir, cache_dir, state_dir,
    default_config_path, ensure_dir, APP_NAME,
)


class TestConfigDir:
    def test_uses_xdg_config_home(self):
        with patch.dict(os.environ, {'XDG_CONFIG_HOME': '/custom/config'}):
            result = config_dir()
            assert result == Path('/custom/config') / APP_NAME

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-only test')
    def test_unix_fallback(self):
        env = {k: '' for k in ['XDG_CONFIG_HOME']}
        with patch.dict(os.environ, env, clear=False):
            with patch.dict(os.environ, {}, clear=False):
                # Force no XDG var
                os.environ.pop('XDG_CONFIG_HOME', None)
                result = config_dir()
                assert result == Path.home() / '.config' / APP_NAME

    @pytest.mark.skipif(sys.platform != 'win32', reason='Windows-only test')
    def test_windows_uses_appdata(self):
        result = config_dir()
        appdata = os.environ.get('APPDATA', str(Path.home()))
        assert result == Path(appdata) / APP_NAME


class TestCacheDir:
    def test_uses_xdg_cache_home(self):
        with patch.dict(os.environ, {'XDG_CACHE_HOME': '/custom/cache'}):
            result = cache_dir()
            assert result == Path('/custom/cache') / APP_NAME

    @pytest.mark.skipif(sys.platform == 'win32', reason='Unix-only test')
    def test_unix_fallback(self):
        os.environ.pop('XDG_CACHE_HOME', None)
        result = cache_dir()
        assert result == Path.home() / '.cache' / APP_NAME


class TestStateDir:
    def test_uses_xdg_state_home(self):
        with patch.dict(os.environ, {'XDG_STATE_HOME': '/custom/state'}):
            result = state_dir()
            assert result == Path('/custom/state') / APP_NAME


class TestDefaultConfigPath:
    def test_is_yaml_file(self):
        path = default_config_path()
        assert path.suffix == '.yaml'
        assert path.name == 'config.yaml'


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
```

---

## Verification

```bash
# Test XDG on Linux
XDG_CONFIG_HOME=/tmp/test-config ai-content-pipeline list-models --json

# Test default paths
python -c "from ai_content_pipeline.cli.paths import config_dir, cache_dir, state_dir; print(config_dir()); print(cache_dir()); print(state_dir())"

# Run tests
python -m pytest tests/test_xdg_paths.py -v
```

---

## Notes

- This subtask is **additive only**: existing code that uses `./output/` and `./temp/` is unaffected
- The XDG paths are opt-in via flags or environment variables
- Windows gets sensible defaults using `%APPDATA%` and `%LOCALAPPDATA%`
- `ensure_dir()` is safe to call multiple times (idempotent)
- The `APP_NAME` constant (`video-ai-studio`) matches the PyPI package name for consistency
