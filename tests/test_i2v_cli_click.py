"""Click CliRunner tests for fal-image-to-video CLI."""

import pytest
from click.testing import CliRunner
from fal_image_to_video.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestImageToVideoCLI:
    """Test fal-image-to-video Click CLI."""

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "FAL Image-to-Video" in result.output

    def test_generate_help(self, runner):
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--image" in result.output
        assert "--prompt" in result.output
        assert "--model" in result.output

    def test_list_models(self, runner):
        result = runner.invoke(cli, ["list-models"])
        assert result.exit_code == 0
        assert "Available Image-to-Video Models" in result.output

    def test_model_info(self, runner):
        result = runner.invoke(cli, ["model-info", "kling_2_6_pro"])
        assert result.exit_code == 0

    def test_interpolate_help(self, runner):
        result = runner.invoke(cli, ["interpolate", "--help"])
        assert result.exit_code == 0
        assert "--start-frame" in result.output
        assert "--end-frame" in result.output

    def test_generate_missing_image(self, runner):
        """Missing required --image should fail."""
        result = runner.invoke(cli, ["generate", "--prompt", "test", "--model", "hailuo"])
        assert result.exit_code != 0

    def test_generate_missing_prompt(self, runner):
        """Missing required --prompt should fail."""
        result = runner.invoke(cli, ["generate", "--image", "test.png", "--model", "hailuo"])
        assert result.exit_code != 0

    def test_no_command_shows_help(self, runner):
        """No subcommand should show help."""
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Usage" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
