"""Tests for the CLI credential storage feature (set-key / get-key / check-keys).

Covers:
- Credential store module (save, load, delete, inject)
- CLI commands via Click CliRunner
- Security: file permissions, no positional value arg, masked output
"""

import os
import sys
import stat

import pytest
from click.testing import CliRunner

from ai_content_pipeline.cli.click_app import cli
from ai_content_pipeline.cli.credentials import (
    KNOWN_KEYS,
    credentials_path,
    delete_key,
    inject_keys,
    load_all_keys,
    load_key,
    save_key,
)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Redirect config_dir to a temp directory for every test."""
    monkeypatch.setattr(
        "ai_content_pipeline.cli.credentials.config_dir",
        lambda: tmp_path,
    )
    # Also patch the import used in keys.py for credentials_path display
    monkeypatch.setattr(
        "ai_content_pipeline.cli.commands.keys.credentials_path",
        lambda: tmp_path / "credentials.env",
    )


# ===========================================================================
# Credential store module tests
# ===========================================================================


class TestCredentialStore:
    def test_save_and_load_key(self):
        """Save a key, load it back — values should match."""
        save_key("FAL_KEY", "fal_test_123")
        assert load_key("FAL_KEY") == "fal_test_123"

    def test_load_missing_key(self):
        """Loading a key that doesn't exist returns None."""
        assert load_key("NONEXISTENT_KEY") is None

    def test_delete_key(self):
        """Save a key, delete it, verify it's gone."""
        save_key("FAL_KEY", "fal_test_123")
        assert delete_key("FAL_KEY") is True
        assert load_key("FAL_KEY") is None

    def test_delete_missing_key(self):
        """Deleting a key that doesn't exist returns False."""
        assert delete_key("NONEXISTENT_KEY") is False

    def test_save_overwrites_existing(self):
        """Saving the same key twice overwrites the first value."""
        save_key("FAL_KEY", "old_value")
        save_key("FAL_KEY", "new_value")
        assert load_key("FAL_KEY") == "new_value"
        # Should not duplicate entries
        all_keys = load_all_keys()
        assert len([k for k in all_keys if k == "FAL_KEY"]) == 1

    def test_load_all_keys(self):
        """Multiple keys can be stored and loaded."""
        save_key("FAL_KEY", "fal_123")
        save_key("GEMINI_API_KEY", "gem_456")
        keys = load_all_keys()
        assert keys == {"FAL_KEY": "fal_123", "GEMINI_API_KEY": "gem_456"}

    def test_inject_keys_fills_missing(self, monkeypatch):
        """inject_keys sets env vars that are not already present."""
        save_key("FAL_KEY", "fal_injected")
        monkeypatch.delenv("FAL_KEY", raising=False)

        count = inject_keys()

        assert count >= 1
        assert os.environ["FAL_KEY"] == "fal_injected"

    def test_inject_keys_respects_env(self, monkeypatch):
        """inject_keys does NOT overwrite existing env vars."""
        save_key("FAL_KEY", "from_credentials")
        monkeypatch.setenv("FAL_KEY", "from_environment")

        inject_keys()

        assert os.environ["FAL_KEY"] == "from_environment"

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions only")
    def test_credentials_file_permissions(self):
        """Credentials file should have 0o600 permissions on Unix."""
        save_key("FAL_KEY", "test")
        path = credentials_path()
        mode = stat.S_IMODE(path.stat().st_mode)
        assert mode == 0o600, f"Expected 0o600, got {oct(mode)}"


# ===========================================================================
# CLI command tests
# ===========================================================================


class TestSetKeyCLI:
    def test_set_key_interactive(self, runner):
        """set-key with interactive prompt stores the key."""
        result = runner.invoke(
            cli, ["set-key", "FAL_KEY"],
            input="fal_secret_value\n",
        )
        assert result.exit_code == 0
        assert "FAL_KEY" in result.output
        assert "saved" in result.output
        assert load_key("FAL_KEY") == "fal_secret_value"

    def test_set_key_stdin(self, runner, tmp_path, monkeypatch):
        """set-key --stdin reads value from piped input."""
        result = runner.invoke(
            cli, ["set-key", "FAL_KEY", "--stdin"],
            input="fal_piped_value\n",
        )
        assert result.exit_code == 0
        assert load_key("FAL_KEY") == "fal_piped_value"

    def test_set_key_unknown_warns(self, runner):
        """Setting an unknown key name prints a warning."""
        result = runner.invoke(
            cli, ["set-key", "MY_CUSTOM_KEY"],
            input="custom_value\n",
        )
        assert result.exit_code == 0
        assert "not a recognised key name" in result.output
        # But it should still save
        assert load_key("MY_CUSTOM_KEY") == "custom_value"

    def test_set_key_no_positional_value(self, runner):
        """Passing extra positional arguments should fail."""
        result = runner.invoke(
            cli, ["set-key", "FAL_KEY", "leaked_value"],
        )
        # Click should reject the extra argument
        assert result.exit_code != 0

    def test_set_key_json_output(self, runner):
        """set-key with --json emits structured output."""
        result = runner.invoke(
            cli, ["--json", "set-key", "FAL_KEY"],
            input="fal_json_test\n",
        )
        assert result.exit_code == 0
        assert '"saved": true' in result.output


class TestGetKeyCLI:
    def test_get_key_masked(self, runner, monkeypatch):
        """get-key masks the value by default."""
        monkeypatch.delenv("FAL_KEY", raising=False)
        save_key("FAL_KEY", "fal_abcdefghijklmnop")
        result = runner.invoke(cli, ["get-key", "FAL_KEY"])
        assert result.exit_code == 0
        assert "fal_ab" in result.output
        assert "nop" in result.output
        # The full value should NOT appear
        assert "fal_abcdefghijklmnop" not in result.output

    def test_get_key_reveal(self, runner, monkeypatch):
        """get-key --reveal shows the full value."""
        monkeypatch.delenv("FAL_KEY", raising=False)
        save_key("FAL_KEY", "fal_abcdefghijklmnop")
        result = runner.invoke(cli, ["get-key", "FAL_KEY", "--reveal"])
        assert result.exit_code == 0
        assert "fal_abcdefghijklmnop" in result.output

    def test_get_key_not_set(self, runner, monkeypatch):
        """get-key for a missing key reports not set."""
        monkeypatch.delenv("FAL_KEY", raising=False)
        result = runner.invoke(cli, ["get-key", "FAL_KEY"])
        assert result.exit_code == 0
        assert "not set" in result.output

    def test_get_key_json(self, runner, monkeypatch):
        """get-key --json emits structured output."""
        monkeypatch.delenv("FAL_KEY", raising=False)
        save_key("FAL_KEY", "fal_test")
        result = runner.invoke(cli, ["--json", "get-key", "FAL_KEY"])
        assert result.exit_code == 0
        assert '"source": "credentials"' in result.output


class TestCheckKeysCLI:
    def test_check_keys_shows_all_known(self, runner):
        """check-keys lists all known API keys."""
        result = runner.invoke(cli, ["check-keys"])
        assert result.exit_code == 0
        for key in KNOWN_KEYS:
            assert key in result.output

    def test_check_keys_json(self, runner):
        """check-keys --json emits structured output."""
        save_key("FAL_KEY", "fal_test")
        result = runner.invoke(cli, ["--json", "check-keys"])
        assert result.exit_code == 0
        assert '"keys"' in result.output
        assert '"FAL_KEY"' in result.output

    def test_check_keys_shows_source(self, runner):
        """check-keys shows correct source for stored keys."""
        save_key("FAL_KEY", "fal_test")
        result = runner.invoke(cli, ["check-keys"])
        assert result.exit_code == 0
        assert "credentials" in result.output


class TestDeleteKeyCLI:
    def test_delete_key_removes(self, runner):
        """delete-key removes a stored key."""
        save_key("FAL_KEY", "fal_test")
        result = runner.invoke(cli, ["delete-key", "FAL_KEY"])
        assert result.exit_code == 0
        assert "removed" in result.output
        assert load_key("FAL_KEY") is None

    def test_delete_key_missing(self, runner):
        """delete-key for a missing key reports not found."""
        result = runner.invoke(cli, ["delete-key", "FAL_KEY"])
        assert result.exit_code == 0
        assert "not found" in result.output
