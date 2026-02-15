"""
Persistent credential storage for API keys.

Stores keys in ``~/.config/video-ai-studio/credentials.env`` (XDG-compliant)
so that binary users can configure API keys without needing a ``.env`` file
in the working directory.

Key resolution order (env vars always win):
1. Environment variable (``FAL_KEY``, etc.) — set by shell or CI
2. Credentials file — set by ``aicp set-key``
3. ``.env`` in working directory — existing dotenv behaviour
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

from .paths import config_dir, ensure_dir

# Canonical list of supported API keys and their fallback names.
KNOWN_KEYS = [
    "FAL_KEY",
    "GEMINI_API_KEY",
    "OPENROUTER_API_KEY",
    "ELEVENLABS_API_KEY",
]


def credentials_path() -> Path:
    """Return the path to the credentials file.

    Returns:
        Path: ``<config_dir>/credentials.env``
    """
    return config_dir() / "credentials.env"


def _read_lines() -> list[str]:
    """Read raw lines from the credentials file."""
    path = credentials_path()
    if not path.exists():
        return []
    return path.read_text().splitlines()


def _write_lines(lines: list[str]) -> None:
    """Write lines to the credentials file with restricted permissions."""
    path = credentials_path()
    ensure_dir(path.parent)
    path.write_text("\n".join(lines) + "\n" if lines else "")
    # Reason: restrict to owner-only on Unix to prevent other users reading keys.
    if sys.platform != "win32":
        path.chmod(0o600)


def load_all_keys() -> Dict[str, str]:
    """Load all key-value pairs from the credentials file.

    Returns:
        dict: Mapping of key names to values.
    """
    pairs: Dict[str, str] = {}
    for line in _read_lines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        name, _, value = line.partition("=")
        pairs[name.strip()] = value.strip()
    return pairs


def load_key(key_name: str) -> Optional[str]:
    """Load a single key from the credentials file.

    Args:
        key_name: The environment variable name (e.g. ``FAL_KEY``).

    Returns:
        The stored value, or ``None`` if not found.
    """
    return load_all_keys().get(key_name)


def save_key(key_name: str, key_value: str) -> Path:
    """Save or update a key in the credentials file.

    Args:
        key_name: The environment variable name.
        key_value: The secret value.

    Returns:
        Path to the credentials file.
    """
    lines = _read_lines()
    new_lines: list[str] = []
    found = False
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            name, _, _ = stripped.partition("=")
            if name.strip() == key_name:
                new_lines.append(f"{key_name}={key_value}")
                found = True
                continue
        new_lines.append(line)
    if not found:
        new_lines.append(f"{key_name}={key_value}")
    _write_lines(new_lines)
    return credentials_path()


def delete_key(key_name: str) -> bool:
    """Remove a key from the credentials file.

    Args:
        key_name: The environment variable name.

    Returns:
        True if the key was found and removed, False otherwise.
    """
    lines = _read_lines()
    new_lines: list[str] = []
    found = False
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            name, _, _ = stripped.partition("=")
            if name.strip() == key_name:
                found = True
                continue
        new_lines.append(line)
    if found:
        _write_lines(new_lines)
    return found


def inject_keys() -> int:
    """Inject stored credentials into ``os.environ``.

    Only sets variables that are **not** already present so that
    environment variables from the shell always take priority.

    Returns:
        int: Number of keys injected.
    """
    injected = 0
    for name, value in load_all_keys().items():
        if name not in os.environ:
            os.environ[name] = value
            injected += 1
    return injected
