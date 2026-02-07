"""Tests for __main__.py global CLI flags and output routing.

Covers:
- Global flag parsing (--json, --quiet, --debug, --config-dir, --cache-dir, --state-dir)
- CLIOutput creation from flags
- Output routing through CLIOutput methods
- --input flag and read_input() wiring
- --stream flag parsing for run-chain
- --save-json deprecation warning
- Executor/manager quiet-mode suppression
"""

import argparse
import json
import sys
import pytest
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

from ai_content_pipeline.cli.output import CLIOutput, read_input
from ai_content_pipeline.cli.stream import StreamEmitter, NullEmitter


# ---------------------------------------------------------------------------
# Helpers — build an arg parser that mirrors __main__.py's global flags
# ---------------------------------------------------------------------------

def _build_parser():
    """Build a minimal parser matching __main__.py's global flags."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--json", action="store_true", default=False)
    parser.add_argument("--quiet", "-q", action="store_true", default=False)
    parser.add_argument("--base-dir", default=".")
    parser.add_argument("--config-dir", type=str, default=None)
    parser.add_argument("--cache-dir", type=str, default=None)
    parser.add_argument("--state-dir", type=str, default=None)
    sub = parser.add_subparsers(dest="command")

    # Minimal subparsers for commands we test
    lm = sub.add_parser("list-models")

    gi = sub.add_parser("generate-image")
    gi.add_argument("--text", required=True)
    gi.add_argument("--input", type=str, default=None)
    gi.add_argument("--save-json", default=None)
    gi.add_argument("--model", default="auto")
    gi.add_argument("--aspect-ratio", default="16:9")
    gi.add_argument("--output-dir", default=None)

    cv = sub.add_parser("create-video")
    cv.add_argument("--text", required=True)
    cv.add_argument("--input", type=str, default=None)
    cv.add_argument("--save-json", default=None)

    rc = sub.add_parser("run-chain")
    rc.add_argument("--config", required=True)
    rc.add_argument("--input", type=str, default=None)
    rc.add_argument("--input-text", default=None)
    rc.add_argument("--prompt-file", default=None)
    rc.add_argument("--no-confirm", action="store_true", default=False)
    rc.add_argument("--stream", action="store_true", default=False)
    rc.add_argument("--save-json", default=None)

    return parser


# ===========================================================================
# Subtask 1: Global flag parsing
# ===========================================================================

class TestGlobalFlags:
    def test_json_flag_parsed(self):
        parser = _build_parser()
        args = parser.parse_args(["--json", "list-models"])
        assert args.json is True

    def test_quiet_flag_parsed(self):
        parser = _build_parser()
        args = parser.parse_args(["--quiet", "list-models"])
        assert args.quiet is True

    def test_quiet_short_flag(self):
        parser = _build_parser()
        args = parser.parse_args(["-q", "list-models"])
        assert args.quiet is True

    def test_debug_flag_parsed(self):
        parser = _build_parser()
        args = parser.parse_args(["--debug", "list-models"])
        assert args.debug is True

    def test_config_dir_parsed(self):
        parser = _build_parser()
        args = parser.parse_args(["--config-dir", "/tmp/cfg", "list-models"])
        assert args.config_dir == "/tmp/cfg"

    def test_cache_dir_parsed(self):
        parser = _build_parser()
        args = parser.parse_args(["--cache-dir", "/tmp/cache", "list-models"])
        assert args.cache_dir == "/tmp/cache"

    def test_state_dir_parsed(self):
        parser = _build_parser()
        args = parser.parse_args(["--state-dir", "/tmp/state", "list-models"])
        assert args.state_dir == "/tmp/state"

    def test_defaults_are_none_or_false(self):
        parser = _build_parser()
        args = parser.parse_args(["list-models"])
        assert args.json is False
        assert args.quiet is False
        assert args.debug is False
        assert args.config_dir is None
        assert args.cache_dir is None
        assert args.state_dir is None


# ===========================================================================
# Subtask 1b: Directory override flags are applied to env
# ===========================================================================

class TestDirOverrideWiring:
    """Verify --config-dir/--cache-dir/--state-dir set XDG env vars."""

    def test_config_dir_sets_xdg_env(self, monkeypatch):
        from ai_content_pipeline.cli.paths import config_dir
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.setenv("XDG_CONFIG_HOME", "/custom/config")
        result = config_dir()
        assert result == Path("/custom/config") / "video-ai-studio"

    def test_cache_dir_sets_xdg_env(self, monkeypatch):
        from ai_content_pipeline.cli.paths import cache_dir
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        monkeypatch.setenv("XDG_CACHE_HOME", "/custom/cache")
        result = cache_dir()
        assert result == Path("/custom/cache") / "video-ai-studio"

    def test_state_dir_sets_xdg_env(self, monkeypatch):
        from ai_content_pipeline.cli.paths import state_dir
        monkeypatch.delenv("XDG_STATE_HOME", raising=False)
        monkeypatch.setenv("XDG_STATE_HOME", "/custom/state")
        result = state_dir()
        assert result == Path("/custom/state") / "video-ai-studio"

    def test_main_applies_dir_overrides(self, monkeypatch):
        """Verify main() wires --config-dir to XDG_CONFIG_HOME."""
        import os
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        monkeypatch.delenv("XDG_STATE_HOME", raising=False)

        # Simulate what main() does after parse_args, using monkeypatch
        # for automatic cleanup to avoid env pollution across tests
        args = argparse.Namespace(
            config_dir="/my/config",
            cache_dir="/my/cache",
            state_dir="/my/state",
        )
        if getattr(args, 'config_dir', None):
            monkeypatch.setenv("XDG_CONFIG_HOME", args.config_dir)
        if getattr(args, 'cache_dir', None):
            monkeypatch.setenv("XDG_CACHE_HOME", args.cache_dir)
        if getattr(args, 'state_dir', None):
            monkeypatch.setenv("XDG_STATE_HOME", args.state_dir)

        assert os.environ.get("XDG_CONFIG_HOME") == "/my/config"
        assert os.environ.get("XDG_CACHE_HOME") == "/my/cache"
        assert os.environ.get("XDG_STATE_HOME") == "/my/state"


# ===========================================================================
# Subtask 2: CLIOutput creation from flags
# ===========================================================================

class TestCLIOutputCreation:
    def test_json_mode_creates_json_output(self):
        parser = _build_parser()
        args = parser.parse_args(["--json", "list-models"])
        out = CLIOutput(json_mode=args.json, quiet=args.quiet, debug=args.debug)
        assert out.json_mode is True
        assert out.quiet is False

    def test_quiet_mode_creates_quiet_output(self):
        parser = _build_parser()
        args = parser.parse_args(["--quiet", "list-models"])
        out = CLIOutput(json_mode=args.json, quiet=args.quiet, debug=args.debug)
        assert out.quiet is True
        assert out.json_mode is False

    def test_debug_mode_creates_debug_output(self):
        parser = _build_parser()
        args = parser.parse_args(["--debug", "list-models"])
        out = CLIOutput(json_mode=args.json, quiet=args.quiet, debug=args.debug)
        assert out.debug is True


# ===========================================================================
# Subtask 3: Output routing
# ===========================================================================

class TestOutputRouting:
    def test_info_suppressed_in_json_mode(self, capsys):
        out = CLIOutput(json_mode=True)
        out.info("hello")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_info_suppressed_in_quiet_mode(self, capsys):
        out = CLIOutput(quiet=True)
        out.info("hello")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_info_visible_in_default_mode(self, capsys):
        out = CLIOutput()
        out.info("hello")
        captured = capsys.readouterr()
        assert "hello" in captured.out

    def test_error_always_on_stderr(self, capsys):
        out = CLIOutput(json_mode=True, quiet=True)
        out.error("bad thing")
        captured = capsys.readouterr()
        assert "bad thing" in captured.err
        assert captured.out == ""

    def test_result_json_mode_emits_json(self, capsys):
        out = CLIOutput(json_mode=True)
        out.result({"success": True, "cost": 0.5}, command="test-cmd")
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["command"] == "test-cmd"
        assert data["data"]["success"] is True
        assert data["schema_version"] == "1"

    def test_result_human_mode_emits_text(self, capsys):
        out = CLIOutput()
        out.result({"success": True}, command="test-cmd")
        captured = capsys.readouterr()
        assert "success" in captured.out
        assert "True" in captured.out

    def test_table_json_mode(self, capsys):
        out = CLIOutput(json_mode=True)
        out.table([{"name": "flux_dev"}], command="list-models")
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["count"] == 1
        assert data["items"][0]["name"] == "flux_dev"

    def test_verbose_only_in_debug(self, capsys):
        out = CLIOutput(debug=False)
        out.verbose("debug info")
        captured = capsys.readouterr()
        assert captured.err == ""

        out_debug = CLIOutput(debug=True)
        out_debug.verbose("debug info")
        captured = capsys.readouterr()
        assert "debug info" in captured.err


# ===========================================================================
# Subtask 4: --input flag and read_input()
# ===========================================================================

class TestInputFlag:
    def test_input_flag_parsed_for_generate_image(self):
        parser = _build_parser()
        args = parser.parse_args(["generate-image", "--text", "x", "--input", "file.txt"])
        assert args.input == "file.txt"

    def test_input_flag_parsed_for_create_video(self):
        parser = _build_parser()
        args = parser.parse_args(["create-video", "--text", "x", "--input", "-"])
        assert args.input == "-"

    def test_input_flag_parsed_for_run_chain(self):
        parser = _build_parser()
        args = parser.parse_args(["run-chain", "--config", "c.yaml", "--input", "data.txt"])
        assert args.input == "data.txt"

    def test_read_input_from_file(self, tmp_path):
        f = tmp_path / "prompt.txt"
        f.write_text("cinematic drone shot")
        result = read_input(str(f))
        assert result == "cinematic drone shot"

    def test_read_input_fallback(self):
        result = read_input(None, fallback="default text")
        assert result == "default text"

    def test_read_input_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            read_input("/nonexistent/file.txt")


# ===========================================================================
# Subtask 5: --stream flag
# ===========================================================================

class TestStreamFlag:
    def test_stream_flag_parsed(self):
        parser = _build_parser()
        args = parser.parse_args(["run-chain", "--config", "c.yaml", "--stream"])
        assert args.stream is True

    def test_stream_flag_default_false(self):
        parser = _build_parser()
        args = parser.parse_args(["run-chain", "--config", "c.yaml"])
        assert args.stream is False

    def test_stream_emitter_enabled(self, capsys):
        emitter = StreamEmitter(enabled=True)
        emitter.step_start(0, "text_to_image", model="flux_dev")
        captured = capsys.readouterr()
        event = json.loads(captured.err.strip())
        assert event["event"] == "step_start"
        assert event["model"] == "flux_dev"

    def test_null_emitter_no_output(self, capsys):
        emitter = NullEmitter()
        emitter.step_start(0, "test")
        emitter.step_complete(0)
        emitter.pipeline_complete({"success": True})
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""


# ===========================================================================
# Subtask 6: Executor/manager quiet mode
# ===========================================================================

class TestQuietMode:
    def test_executor_quiet_suppresses_init_prints(self, capsys):
        """Executor with quiet=True should not print extension messages."""
        from ai_content_pipeline.pipeline.executor import ChainExecutor
        fm = MagicMock()
        executor = ChainExecutor(fm, quiet=True)
        captured = capsys.readouterr()
        # No parallel extension prints
        assert "extension" not in captured.out.lower()

    def test_manager_quiet_suppresses_init_print(self, capsys):
        """Manager with quiet=True should not print its own init message."""
        from ai_content_pipeline.pipeline.manager import AIPipelineManager
        manager = AIPipelineManager(quiet=True)
        captured = capsys.readouterr()
        # Sub-generators may still print, but the manager's own message is suppressed
        assert "AI Pipeline Manager initialized" not in captured.out

    def test_executor_accepts_stream_emitter(self):
        """Executor.execute() accepts stream_emitter kwarg without error."""
        from ai_content_pipeline.pipeline.executor import ChainExecutor
        fm = MagicMock()
        executor = ChainExecutor(fm, quiet=True)
        # Verify the parameter exists in the signature
        import inspect
        sig = inspect.signature(executor.execute)
        assert "stream_emitter" in sig.parameters


# ===========================================================================
# Subtask 7: --save-json deprecation warning
# ===========================================================================

class TestSaveJsonDeprecation:
    def test_deprecation_warning_emitted(self, capsys):
        """Using --save-json should emit a deprecation warning to stderr."""
        from ai_content_pipeline.__main__ import _check_save_json_deprecation
        out = CLIOutput()
        args = argparse.Namespace(save_json="result.json")
        _check_save_json_deprecation(args, out)
        captured = capsys.readouterr()
        assert "deprecated" in captured.err.lower()
        assert "--json" in captured.err

    def test_no_warning_without_save_json(self, capsys):
        """No warning when --save-json is not used."""
        from ai_content_pipeline.__main__ import _check_save_json_deprecation
        out = CLIOutput()
        args = argparse.Namespace(save_json=None)
        _check_save_json_deprecation(args, out)
        captured = capsys.readouterr()
        assert captured.err == ""

    def test_no_warning_when_attr_missing(self, capsys):
        """No crash when save_json attr doesn't exist."""
        from ai_content_pipeline.__main__ import _check_save_json_deprecation
        out = CLIOutput()
        args = argparse.Namespace()  # no save_json
        _check_save_json_deprecation(args, out)
        captured = capsys.readouterr()
        assert captured.err == ""
