"""Tests for stdin/stdout input support.

Tests the read_input() function which provides:
- Reading from stdin via '-'
- Reading from file paths
- Fallback values
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from ai_content_pipeline.cli.output import read_input


class TestReadInputFromFile:
    def test_reads_file_contents(self, tmp_path):
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("cinematic drone shot over mountains")
        result = read_input(str(prompt_file))
        assert result == "cinematic drone shot over mountains"

    def test_strips_whitespace(self, tmp_path):
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("  hello world  \n")
        result = read_input(str(prompt_file))
        assert result == "hello world"

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            read_input("/nonexistent/prompt.txt")


class TestReadInputFromStdin:
    def test_reads_from_stdin(self):
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "hello from pipe\n"
        with patch("ai_content_pipeline.cli.output.sys") as mock_sys:
            mock_sys.stdin = mock_stdin
            result = read_input("-")
        assert result == "hello from pipe"

    def test_raises_on_tty_stdin(self):
        mock_stdin = MagicMock()
        mock_stdin.isatty.return_value = True
        with patch("ai_content_pipeline.cli.output.sys") as mock_sys:
            mock_sys.stdin = mock_stdin
            with pytest.raises(ValueError, match="requires piped input"):
                read_input("-")


class TestReadInputFallback:
    def test_returns_fallback_when_none(self):
        result = read_input(None, fallback="default prompt")
        assert result == "default prompt"

    def test_returns_none_when_no_input_and_no_fallback(self):
        result = read_input(None)
        assert result is None

    def test_file_takes_priority_over_fallback(self, tmp_path):
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("from file")
        result = read_input(str(prompt_file), fallback="from fallback")
        assert result == "from file"
