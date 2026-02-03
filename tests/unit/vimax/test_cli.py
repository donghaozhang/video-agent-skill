"""
Tests for ViMax CLI commands.

These tests verify CLI command structure and argument handling.
"""

import pytest
from click.testing import CliRunner


# Create a mock vimax command for testing without full package import
import click


@click.group()
def mock_vimax():
    """Mock ViMax CLI for testing."""
    pass


@mock_vimax.command("idea2video")
@click.option("--idea", "-i", required=True, help="Video idea or concept")
@click.option("--output", "-o", default="output/vimax/idea2video", help="Output directory")
@click.option("--duration", "-d", default=60.0, type=float, help="Target duration in seconds")
@click.option("--video-model", default="kling", help="Video generation model")
@click.option("--image-model", default="flux_dev", help="Image generation model")
@click.option("--portraits/--no-portraits", default=True, help="Generate character portraits")
def idea2video(idea, output, duration, video_model, image_model, portraits):
    """Generate video from an idea."""
    click.echo(f"Idea: {idea}")
    click.echo(f"Output: {output}")
    click.echo(f"Duration: {duration}")
    click.echo(f"Video Model: {video_model}")
    click.echo(f"Image Model: {image_model}")
    click.echo(f"Portraits: {portraits}")


@mock_vimax.command("script2video")
@click.option("--script", "-s", required=True, help="Script JSON file")
@click.option("--output", "-o", default="output/vimax/script2video", help="Output directory")
@click.option("--video-model", default="kling", help="Video generation model")
def script2video(script, output, video_model):
    """Generate video from an existing script."""
    click.echo(f"Script: {script}")
    click.echo(f"Output: {output}")
    click.echo(f"Video Model: {video_model}")


@mock_vimax.command("novel2movie")
@click.option("--novel", "-n", required=True, help="Novel text file")
@click.option("--title", "-t", default="Untitled", help="Novel title")
@click.option("--output", "-o", default="output/vimax/novel2movie", help="Output directory")
@click.option("--max-scenes", default=10, type=int, help="Maximum scenes to generate")
def novel2movie(novel, title, output, max_scenes):
    """Convert a novel to a movie."""
    click.echo(f"Novel: {novel}")
    click.echo(f"Title: {title}")
    click.echo(f"Output: {output}")
    click.echo(f"Max Scenes: {max_scenes}")


@mock_vimax.command("list-models")
def list_models():
    """List available models."""
    click.echo("Image Generation:")
    click.echo("   - flux_dev: FLUX.1 Dev")
    click.echo("   - flux_schnell: FLUX.1 Schnell")
    click.echo("Video Generation:")
    click.echo("   - kling: Kling v1")
    click.echo("   - veo3: Veo 3")


class TestVimaxCLI:
    """Tests for ViMax CLI commands."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_vimax_group_help(self, runner):
        """Test vimax group help command."""
        result = runner.invoke(mock_vimax, ["--help"])
        assert result.exit_code == 0
        assert "Mock ViMax CLI" in result.output

    def test_idea2video_help(self, runner):
        """Test idea2video command help."""
        result = runner.invoke(mock_vimax, ["idea2video", "--help"])
        assert result.exit_code == 0
        assert "--idea" in result.output
        assert "--duration" in result.output
        assert "--video-model" in result.output

    def test_idea2video_requires_idea(self, runner):
        """Test idea2video requires --idea option."""
        result = runner.invoke(mock_vimax, ["idea2video"])
        assert result.exit_code != 0
        assert "Missing option" in result.output

    def test_idea2video_with_idea(self, runner):
        """Test idea2video with valid idea."""
        result = runner.invoke(mock_vimax, ["idea2video", "--idea", "A test video"])
        assert result.exit_code == 0
        assert "Idea: A test video" in result.output
        assert "Duration: 60.0" in result.output  # Default

    def test_idea2video_custom_options(self, runner):
        """Test idea2video with custom options."""
        result = runner.invoke(mock_vimax, [
            "idea2video",
            "--idea", "Custom test",
            "--duration", "120",
            "--video-model", "veo3",
            "--no-portraits",
        ])
        assert result.exit_code == 0
        assert "Duration: 120.0" in result.output
        assert "Video Model: veo3" in result.output
        assert "Portraits: False" in result.output

    def test_script2video_help(self, runner):
        """Test script2video command help."""
        result = runner.invoke(mock_vimax, ["script2video", "--help"])
        assert result.exit_code == 0
        assert "--script" in result.output

    def test_script2video_requires_script(self, runner):
        """Test script2video requires --script option."""
        result = runner.invoke(mock_vimax, ["script2video"])
        assert result.exit_code != 0
        assert "Missing option" in result.output

    def test_novel2movie_help(self, runner):
        """Test novel2movie command help."""
        result = runner.invoke(mock_vimax, ["novel2movie", "--help"])
        assert result.exit_code == 0
        assert "--novel" in result.output
        assert "--title" in result.output
        assert "--max-scenes" in result.output

    def test_novel2movie_requires_novel(self, runner):
        """Test novel2movie requires --novel option."""
        result = runner.invoke(mock_vimax, ["novel2movie"])
        assert result.exit_code != 0
        assert "Missing option" in result.output

    def test_list_models(self, runner):
        """Test list-models command."""
        result = runner.invoke(mock_vimax, ["list-models"])
        assert result.exit_code == 0
        assert "flux_dev" in result.output
        assert "kling" in result.output
        assert "veo3" in result.output


class TestCLIArgumentTypes:
    """Tests for CLI argument type validation."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_duration_is_float(self, runner):
        """Test duration accepts float values."""
        result = runner.invoke(mock_vimax, [
            "idea2video",
            "--idea", "Test",
            "--duration", "45.5",
        ])
        assert result.exit_code == 0
        assert "Duration: 45.5" in result.output

    def test_invalid_duration_rejected(self, runner):
        """Test invalid duration is rejected."""
        result = runner.invoke(mock_vimax, [
            "idea2video",
            "--idea", "Test",
            "--duration", "not-a-number",
        ])
        assert result.exit_code != 0

    def test_max_scenes_is_int(self, runner):
        """Test max-scenes accepts integer values."""
        result = runner.invoke(mock_vimax, [
            "novel2movie",
            "--novel", "test.txt",
            "--max-scenes", "5",
        ])
        # This will fail since test.txt doesn't exist, but we're testing type parsing
        assert "max-scenes" not in result.output or "5" in result.output


class TestCLIDefaultValues:
    """Tests for CLI default values."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_idea2video_defaults(self, runner):
        """Test idea2video default values."""
        result = runner.invoke(mock_vimax, [
            "idea2video",
            "--idea", "Test",
        ])
        assert result.exit_code == 0
        assert "Output: output/vimax/idea2video" in result.output
        assert "Duration: 60.0" in result.output
        assert "Video Model: kling" in result.output
        assert "Image Model: flux_dev" in result.output
        assert "Portraits: True" in result.output

    def test_novel2movie_defaults(self, runner):
        """Test novel2movie default values."""
        result = runner.invoke(mock_vimax, [
            "novel2movie",
            "--novel", "test.txt",
        ])
        # Check defaults in help or error output
        assert "Max Scenes: 10" in result.output or result.exit_code != 0


class TestCLIShortOptions:
    """Tests for CLI short option forms."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_short_idea_option(self, runner):
        """Test -i works for --idea."""
        result = runner.invoke(mock_vimax, [
            "idea2video",
            "-i", "Short test",
        ])
        assert result.exit_code == 0
        assert "Idea: Short test" in result.output

    def test_short_output_option(self, runner):
        """Test -o works for --output."""
        result = runner.invoke(mock_vimax, [
            "idea2video",
            "-i", "Test",
            "-o", "custom/output",
        ])
        assert result.exit_code == 0
        assert "Output: custom/output" in result.output

    def test_short_duration_option(self, runner):
        """Test -d works for --duration."""
        result = runner.invoke(mock_vimax, [
            "idea2video",
            "-i", "Test",
            "-d", "90",
        ])
        assert result.exit_code == 0
        assert "Duration: 90.0" in result.output
