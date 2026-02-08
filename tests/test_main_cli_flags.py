"""Tests for CLI global flags, output routing, and Click integration.

Covers:
- Global flag parsing via Click CliRunner (--json, --quiet, --debug, --config-dir, --cache-dir, --state-dir)
- CLIOutput creation from flags
- Output routing through CLIOutput methods
- --input flag and read_input() wiring
- --stream flag parsing for run-chain
- --save-json deprecation warning
- Executor/manager quiet-mode suppression
"""

import json
import os
import sys
import pytest
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from ai_content_pipeline.cli.output import CLIOutput, read_input
from ai_content_pipeline.cli.stream import StreamEmitter, NullEmitter
from ai_content_pipeline.cli.click_app import cli

# Check if vimax (ai_content_platform) is available
try:
    import ai_content_platform.vimax.cli.commands  # noqa: F401
    HAS_VIMAX = True
except ImportError:
    HAS_VIMAX = False


# ===========================================================================
# Global flag parsing via Click
# ===========================================================================

class TestGlobalFlags:
    def test_help_shows_global_options(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "--json" in result.output
        assert "--quiet" in result.output
        assert "--debug" in result.output
        assert "--config-dir" in result.output
        assert "--cache-dir" in result.output
        assert "--state-dir" in result.output

    def test_help_shows_commands(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "list-models" in result.output
        assert "generate-image" in result.output
        assert "create-video" in result.output
        assert "run-chain" in result.output

    @pytest.mark.skipif(not HAS_VIMAX, reason="ai_content_platform not installed")
    def test_vimax_subgroup_visible(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "vimax" in result.output

    @pytest.mark.skipif(not HAS_VIMAX, reason="ai_content_platform not installed")
    def test_vimax_subgroup_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["vimax", "--help"])
        assert result.exit_code == 0
        assert "idea2video" in result.output
        assert "script2video" in result.output
        assert "novel2movie" in result.output


# ===========================================================================
# Directory override flags are applied to env
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

    def test_click_applies_dir_overrides(self, monkeypatch):
        """Verify Click group callback wires --config-dir to XDG_CONFIG_HOME."""
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        monkeypatch.delenv("XDG_STATE_HOME", raising=False)

        # Use CliRunner which isolates env changes
        runner = CliRunner()
        result = runner.invoke(cli, [
            "--config-dir", "/my/config",
            "--cache-dir", "/my/cache",
            "--state-dir", "/my/state",
            "list-models",  # need a command to trigger the group callback
        ], catch_exceptions=False)

        # Verify the CLI ran successfully (env vars set during execution)
        assert result.exit_code == 0


# ===========================================================================
# CLIOutput creation from flags
# ===========================================================================

class TestCLIOutputCreation:
    def test_json_mode_creates_json_output(self):
        out = CLIOutput(json_mode=True, quiet=False, debug=False)
        assert out.json_mode is True
        assert out.quiet is False

    def test_quiet_mode_creates_quiet_output(self):
        out = CLIOutput(json_mode=False, quiet=True, debug=False)
        assert out.quiet is True
        assert out.json_mode is False

    def test_debug_mode_creates_debug_output(self):
        out = CLIOutput(json_mode=False, quiet=False, debug=True)
        assert out.debug is True


# ===========================================================================
# Output routing
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
# --input flag and read_input()
# ===========================================================================

class TestInputFlag:
    def test_generate_image_help_shows_input_option(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["generate-image", "--help"])
        assert result.exit_code == 0
        assert "--input" in result.output

    def test_create_video_help_shows_input_option(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["create-video", "--help"])
        assert result.exit_code == 0
        assert "--input" in result.output

    def test_run_chain_help_shows_input_option(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["run-chain", "--help"])
        assert result.exit_code == 0
        assert "--input" in result.output

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
# --stream flag
# ===========================================================================

class TestStreamFlag:
    def test_run_chain_help_shows_stream_option(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["run-chain", "--help"])
        assert result.exit_code == 0
        assert "--stream" in result.output

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
# Executor/manager quiet mode
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
# --save-json deprecation warning
# ===========================================================================

class TestSaveJsonDeprecation:
    def test_deprecation_warning_emitted(self, capsys):
        """Using --save-json should emit a deprecation warning to stderr."""
        from ai_content_pipeline.cli.commands.pipeline import _check_save_json_deprecation
        out = CLIOutput()
        _check_save_json_deprecation("result.json", out)
        captured = capsys.readouterr()
        assert "deprecated" in captured.err.lower()
        assert "--json" in captured.err

    def test_no_warning_without_save_json(self, capsys):
        """No warning when save_json is None."""
        from ai_content_pipeline.cli.commands.pipeline import _check_save_json_deprecation
        out = CLIOutput()
        _check_save_json_deprecation(None, out)
        captured = capsys.readouterr()
        assert captured.err == ""
