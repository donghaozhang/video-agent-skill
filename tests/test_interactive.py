"""Tests for non-interactive mode detection and confirm().

Tests the cli.interactive module which provides:
- CI environment auto-detection
- Safe confirm() that returns default in non-interactive mode
- is_interactive() TTY check
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

from ai_content_pipeline.cli.interactive import (
    is_interactive,
    confirm,
    _CI_ENV_VARS,
)


class TestIsInteractive:
    def test_returns_false_when_ci_env_set(self):
        with patch.dict(os.environ, {"CI": "true"}):
            assert is_interactive() is False

    def test_returns_false_when_github_actions_set(self):
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            assert is_interactive() is False

    def test_returns_false_when_jenkins_url_set(self):
        with patch.dict(os.environ, {"JENKINS_URL": "http://jenkins.local"}):
            assert is_interactive() is False

    def test_returns_false_when_stdin_not_tty(self):
        env = os.environ.copy()
        for var in _CI_ENV_VARS:
            env.pop(var, None)
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = False
        with patch.dict(os.environ, env, clear=True), \
             patch.object(sys, "stdin", mock_stdin):
            assert is_interactive() is False

    def test_returns_true_when_tty_and_no_ci(self):
        env = os.environ.copy()
        for var in _CI_ENV_VARS:
            env.pop(var, None)
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = True
        with patch.dict(os.environ, env, clear=True), \
             patch.object(sys, "stdin", mock_stdin):
            assert is_interactive() is True

    def test_all_ci_vars_are_checked(self):
        """Every CI env var in the list causes non-interactive mode."""
        for var in _CI_ENV_VARS:
            env = {var: "1"}
            with patch.dict(os.environ, env):
                assert is_interactive() is False, f"{var} should disable interactive mode"


class TestConfirm:
    def test_returns_default_in_non_interactive(self):
        with patch("ai_content_pipeline.cli.interactive.is_interactive", return_value=False):
            assert confirm("Continue?", default=False) is False
            assert confirm("Continue?", default=True) is True

    def test_returns_true_on_y_input(self):
        with patch("ai_content_pipeline.cli.interactive.is_interactive", return_value=True), \
             patch("builtins.input", return_value="y"):
            assert confirm("Continue?") is True

    def test_returns_true_on_yes_input(self):
        with patch("ai_content_pipeline.cli.interactive.is_interactive", return_value=True), \
             patch("builtins.input", return_value="yes"):
            assert confirm("Continue?") is True

    def test_returns_false_on_n_input(self):
        with patch("ai_content_pipeline.cli.interactive.is_interactive", return_value=True), \
             patch("builtins.input", return_value="n"):
            assert confirm("Continue?") is False

    def test_returns_false_on_empty_input_default_false(self):
        with patch("ai_content_pipeline.cli.interactive.is_interactive", return_value=True), \
             patch("builtins.input", return_value=""):
            assert confirm("Continue?", default=False) is False

    def test_returns_true_on_empty_input_default_true(self):
        with patch("ai_content_pipeline.cli.interactive.is_interactive", return_value=True), \
             patch("builtins.input", return_value=""):
            assert confirm("Continue?", default=True) is True

    def test_handles_eof_error(self):
        with patch("ai_content_pipeline.cli.interactive.is_interactive", return_value=True), \
             patch("builtins.input", side_effect=EOFError):
            assert confirm("Continue?", default=False) is False

    def test_prompt_suffix_for_default_false(self):
        with patch("ai_content_pipeline.cli.interactive.is_interactive", return_value=True), \
             patch("builtins.input", return_value="y") as mock_input:
            confirm("Continue?", default=False)
            mock_input.assert_called_once_with("Continue? (y/N): ")

    def test_prompt_suffix_for_default_true(self):
        with patch("ai_content_pipeline.cli.interactive.is_interactive", return_value=True), \
             patch("builtins.input", return_value="n") as mock_input:
            confirm("Continue?", default=True)
            mock_input.assert_called_once_with("Continue? (Y/n): ")
