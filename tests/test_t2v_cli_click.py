"""Click CliRunner tests for fal-text-to-video CLI."""

import pytest
from click.testing import CliRunner
from fal_text_to_video.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestTextToVideoCLI:
    """Test fal-text-to-video Click CLI."""

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "FAL Text-to-Video" in result.output

    def test_generate_help(self, runner):
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--prompt" in result.output
        assert "--model" in result.output
        assert "--duration" in result.output
        assert "--audio" in result.output
        assert "--mock" in result.output

    def test_list_models(self, runner):
        result = runner.invoke(cli, ["list-models"])
        assert result.exit_code == 0
        assert "Available Text-to-Video Models" in result.output

    def test_model_info(self, runner):
        result = runner.invoke(cli, ["model-info", "kling_2_6_pro"])
        assert result.exit_code == 0
        assert "Kling" in result.output

    def test_estimate_cost_help(self, runner):
        result = runner.invoke(cli, ["estimate-cost", "--help"])
        assert result.exit_code == 0
        assert "--model" in result.output
        assert "--duration" in result.output

    def test_generate_missing_prompt(self, runner):
        """Missing required --prompt should fail."""
        result = runner.invoke(cli, ["generate", "--model", "kling_2_6_pro"])
        assert result.exit_code != 0

    def test_generate_invalid_model(self, runner):
        """Invalid model name should fail."""
        result = runner.invoke(cli, ["generate", "--prompt", "test", "--model", "nonexistent"])
        assert result.exit_code != 0

    def test_no_command_shows_help(self, runner):
        """No subcommand should show help."""
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Usage" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
