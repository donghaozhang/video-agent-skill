"""Tests for the Click CLI application (root group + all commands + vimax subgroup).

Covers:
- Root group help and global options
- All 20 commands visible in help
- Vimax subgroup integration
- Command-level --help for each command
- Required option validation
- Vimax not in setup.py console_scripts
- PyInstaller hidden imports include new CLI modules
"""

import pytest
from click.testing import CliRunner

from ai_content_pipeline.cli.click_app import cli


@pytest.fixture
def runner():
    return CliRunner()


# ===========================================================================
# Root group
# ===========================================================================

class TestRootGroup:
    def test_help_exit_code(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_help_shows_description(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "AI Content Pipeline" in result.output

    def test_help_shows_all_global_options(self, runner):
        result = runner.invoke(cli, ["--help"])
        for opt in ["--json", "--quiet", "--debug", "--base-dir",
                     "--config-dir", "--cache-dir", "--state-dir"]:
            assert opt in result.output, f"{opt} missing from help"

    def test_short_help_flag(self, runner):
        result = runner.invoke(cli, ["-h"])
        assert result.exit_code == 0
        assert "list-models" in result.output

    def test_all_commands_visible(self, runner):
        result = runner.invoke(cli, ["--help"])
        expected_commands = [
            "list-models", "setup", "generate-image", "create-video",
            "run-chain", "create-examples", "generate-avatar",
            "list-avatar-models", "analyze-video", "list-video-models",
            "transfer-motion", "list-motion-models", "transcribe",
            "list-speech-models", "generate-grid", "upscale-image",
            "init-project", "organize-project", "structure-info",
            "vimax",
        ]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' missing from help"

    def test_no_command_shows_help(self, runner):
        """Invoking with no args exits 0 (Click group default)."""
        result = runner.invoke(cli, [])
        # Click groups show help and exit 0 when invoked without subcommand
        assert result.exit_code == 0


# ===========================================================================
# Vimax subgroup
# ===========================================================================

class TestVimaxSubgroup:
    def test_vimax_help(self, runner):
        result = runner.invoke(cli, ["vimax", "--help"])
        assert result.exit_code == 0
        assert "idea2video" in result.output
        assert "script2video" in result.output
        assert "novel2movie" in result.output

    def test_vimax_idea2video_help(self, runner):
        result = runner.invoke(cli, ["vimax", "idea2video", "--help"])
        assert result.exit_code == 0
        assert "--idea" in result.output
        assert "--duration" in result.output

    def test_vimax_idea2video_requires_idea(self, runner):
        result = runner.invoke(cli, ["vimax", "idea2video"])
        assert result.exit_code != 0
        assert "Missing" in result.output or "required" in result.output.lower()

    def test_vimax_generate_storyboard_help(self, runner):
        result = runner.invoke(cli, ["vimax", "generate-storyboard", "--help"])
        assert result.exit_code == 0
        assert "--script" in result.output
        assert "--portraits" in result.output

    def test_vimax_list_models(self, runner):
        result = runner.invoke(cli, ["vimax", "list-models"])
        assert result.exit_code == 0
        assert "aicp vimax" in result.output


# ===========================================================================
# Command-level --help
# ===========================================================================

class TestCommandHelp:
    """Each command should show help without error."""

    @pytest.mark.parametrize("cmd", [
        "list-models", "setup", "generate-image", "create-video",
        "run-chain", "create-examples", "generate-avatar",
        "list-avatar-models", "analyze-video", "list-video-models",
        "transfer-motion", "list-motion-models", "transcribe",
        "list-speech-models", "generate-grid", "upscale-image",
        "init-project", "organize-project", "structure-info",
    ])
    def test_command_help(self, runner, cmd):
        result = runner.invoke(cli, [cmd, "--help"])
        assert result.exit_code == 0, f"{cmd} --help failed: {result.output}"


# ===========================================================================
# Required option validation
# ===========================================================================

class TestRequiredOptions:
    def test_generate_image_requires_text(self, runner):
        result = runner.invoke(cli, ["generate-image"])
        assert result.exit_code != 0
        assert "text" in result.output.lower()

    def test_create_video_requires_text(self, runner):
        result = runner.invoke(cli, ["create-video"])
        assert result.exit_code != 0
        assert "text" in result.output.lower()

    def test_run_chain_requires_config(self, runner):
        result = runner.invoke(cli, ["run-chain"])
        assert result.exit_code != 0
        assert "config" in result.output.lower()

    def test_analyze_video_requires_input(self, runner):
        result = runner.invoke(cli, ["analyze-video"])
        assert result.exit_code != 0
        assert "input" in result.output.lower()

    def test_transfer_motion_requires_image_and_video(self, runner):
        result = runner.invoke(cli, ["transfer-motion"])
        assert result.exit_code != 0

    def test_transcribe_requires_input(self, runner):
        result = runner.invoke(cli, ["transcribe"])
        assert result.exit_code != 0
        assert "input" in result.output.lower()

    def test_generate_grid_requires_prompt_file(self, runner):
        result = runner.invoke(cli, ["generate-grid"])
        assert result.exit_code != 0
        assert "prompt-file" in result.output.lower()

    def test_upscale_image_requires_input(self, runner):
        result = runner.invoke(cli, ["upscale-image"])
        assert result.exit_code != 0
        assert "input" in result.output.lower()


# ===========================================================================
# setup.py no longer has standalone vimax
# ===========================================================================

class TestSetupPyVimax:
    def test_vimax_not_in_console_scripts(self):
        """Standalone vimax entry should not be in setup.py console_scripts."""
        from pathlib import Path
        setup_path = Path(__file__).parent.parent / "setup.py"
        content = setup_path.read_text()
        # The old entry was: "vimax=packages.core.ai_content_platform.vimax.cli.commands:main"
        assert "vimax=packages.core" not in content
        assert "vimax=" not in content or "aicp subgroup" in content


# ===========================================================================
# PyInstaller spec includes new CLI modules
# ===========================================================================

class TestPyInstallerSpec:
    def test_spec_includes_click_app(self):
        from pathlib import Path
        spec_path = Path(__file__).parent.parent / "aicp.spec"
        content = spec_path.read_text()
        assert "ai_content_pipeline.cli.click_app" in content

    def test_spec_includes_command_modules(self):
        from pathlib import Path
        spec_path = Path(__file__).parent.parent / "aicp.spec"
        content = spec_path.read_text()
        for module in [
            "ai_content_pipeline.cli.commands",
            "ai_content_pipeline.cli.commands.pipeline",
            "ai_content_pipeline.cli.commands.media",
            "ai_content_pipeline.cli.commands.motion",
            "ai_content_pipeline.cli.commands.audio",
            "ai_content_pipeline.cli.commands.imaging",
            "ai_content_pipeline.cli.commands.project",
        ]:
            assert module in content, f"{module} missing from aicp.spec"

    def test_spec_includes_vimax_modules(self):
        from pathlib import Path
        spec_path = Path(__file__).parent.parent / "aicp.spec"
        content = spec_path.read_text()
        assert "ai_content_platform.vimax.cli.commands" in content

    def test_spec_includes_click(self):
        from pathlib import Path
        spec_path = Path(__file__).parent.parent / "aicp.spec"
        content = spec_path.read_text()
        assert "'click'" in content
