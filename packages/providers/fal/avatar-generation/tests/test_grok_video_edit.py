"""
Tests for xAI Grok Imagine Video Edit model.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fal_avatar.models.grok import GrokVideoEditModel
from fal_avatar.config.constants import (
    MODEL_ENDPOINTS,
    MODEL_PRICING,
    MODEL_DEFAULTS,
    SUPPORTED_RESOLUTIONS,
    MAX_DURATIONS,
    INPUT_REQUIREMENTS,
    MODEL_CATEGORIES,
    MODEL_DISPLAY_NAMES,
)


class TestGrokVideoEditModel:
    """Tests for xAI Grok Video Edit model."""

    def test_init(self):
        """Test model initialization."""
        model = GrokVideoEditModel()
        assert model.model_name == "grok_video_edit"
        assert model.endpoint == "xai/grok-imagine-video/edit-video"
        assert model.max_duration == 8
        assert model.max_prompt_length == 4096

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid inputs."""
        model = GrokVideoEditModel()
        params = model.validate_parameters(
            video_url="https://example.com/video.mp4",
            prompt="Colorize this black and white video"
        )

        assert params["video_url"] == "https://example.com/video.mp4"
        assert params["prompt"] == "Colorize this black and white video"
        assert params["resolution"] == "auto"  # default

    def test_validate_parameters_custom_resolution(self):
        """Test parameter validation with custom resolution."""
        model = GrokVideoEditModel()
        params = model.validate_parameters(
            video_url="https://example.com/video.mp4",
            prompt="Apply vintage filter",
            resolution="720p"
        )

        assert params["resolution"] == "720p"

    def test_validate_parameters_480p_resolution(self):
        """Test 480p resolution is valid."""
        model = GrokVideoEditModel()
        params = model.validate_parameters(
            video_url="https://example.com/video.mp4",
            prompt="Add cinematic color grading",
            resolution="480p"
        )
        assert params["resolution"] == "480p"

    def test_validate_parameters_missing_video_url(self):
        """Test validation fails when video_url is missing."""
        model = GrokVideoEditModel()
        with pytest.raises(ValueError, match="video_url is required"):
            model.validate_parameters(
                video_url="",
                prompt="Test prompt"
            )

    def test_validate_parameters_missing_prompt(self):
        """Test validation fails when prompt is missing."""
        model = GrokVideoEditModel()
        with pytest.raises(ValueError, match="prompt is required"):
            model.validate_parameters(
                video_url="https://example.com/video.mp4",
                prompt=""
            )

    def test_validate_parameters_prompt_too_long(self):
        """Test validation fails when prompt exceeds max length."""
        model = GrokVideoEditModel()
        long_prompt = "x" * 4097  # Exceeds 4096 character limit
        with pytest.raises(ValueError, match="exceeds maximum length"):
            model.validate_parameters(
                video_url="https://example.com/video.mp4",
                prompt=long_prompt
            )

    def test_validate_parameters_max_prompt_length(self):
        """Test validation passes at exact max prompt length."""
        model = GrokVideoEditModel()
        max_prompt = "x" * 4096  # Exactly at limit
        params = model.validate_parameters(
            video_url="https://example.com/video.mp4",
            prompt=max_prompt
        )
        assert len(params["prompt"]) == 4096

    def test_validate_parameters_invalid_resolution(self):
        """Test validation fails for invalid resolution."""
        model = GrokVideoEditModel()
        with pytest.raises(ValueError, match="Unsupported resolution"):
            model.validate_parameters(
                video_url="https://example.com/video.mp4",
                prompt="Test",
                resolution="1080p"
            )

    def test_estimate_cost_base(self):
        """Test cost estimation for 6-second video."""
        model = GrokVideoEditModel()
        # 6s: $0.01*6 input + $0.05*6 output = $0.06 + $0.30 = $0.36
        assert model.estimate_cost(duration=6) == pytest.approx(0.36)

    def test_estimate_cost_short_video(self):
        """Test cost estimation for short video."""
        model = GrokVideoEditModel()
        # 3s: $0.01*3 input + $0.05*3 output = $0.03 + $0.15 = $0.18
        assert model.estimate_cost(duration=3) == pytest.approx(0.18)

    def test_estimate_cost_max_duration(self):
        """Test cost estimation for max 8-second input."""
        model = GrokVideoEditModel()
        # 8s: $0.01*8 input + $0.05*8 output = $0.08 + $0.40 = $0.48
        assert model.estimate_cost(duration=8) == pytest.approx(0.48)

    def test_estimate_cost_input_capped_at_8_seconds(self):
        """Test that input cost is capped at 8 seconds."""
        model = GrokVideoEditModel()
        # 10s output but input capped at 8s:
        # $0.01*8 input + $0.05*10 output = $0.08 + $0.50 = $0.58
        cost = model.estimate_cost(duration=10, input_duration=10)
        assert cost == pytest.approx(0.58)

    def test_estimate_cost_custom_input_duration(self):
        """Test cost estimation with custom input duration."""
        model = GrokVideoEditModel()
        # 6s output, 4s input:
        # $0.01*4 input + $0.05*6 output = $0.04 + $0.30 = $0.34
        cost = model.estimate_cost(duration=6, input_duration=4)
        assert cost == pytest.approx(0.34)

    def test_get_model_info(self):
        """Test model info contains expected fields."""
        model = GrokVideoEditModel()
        info = model.get_model_info()

        assert info["name"] == "xAI Grok Video Edit"
        assert info["provider"] == "xAI (via FAL)"
        assert info["max_duration"] == 8
        assert info["max_prompt_length"] == 4096
        assert "video_editing" in info["features"]
        assert "colorization" in info["features"]
        assert "style_transfer" in info["features"]
        assert info["endpoint"] == "xai/grok-imagine-video/edit-video"

    def test_get_model_info_pricing(self):
        """Test model info includes correct pricing."""
        model = GrokVideoEditModel()
        info = model.get_model_info()

        assert "pricing" in info
        assert info["pricing"]["input_per_second"] == 0.01
        assert info["pricing"]["output_per_second"] == 0.05

    def test_get_model_info_input_constraints(self):
        """Test model info includes input constraints."""
        model = GrokVideoEditModel()
        info = model.get_model_info()

        assert "input_constraints" in info
        assert info["input_constraints"]["max_resolution"] == "854x480"
        assert "8 seconds" in info["input_constraints"]["max_duration"]


class TestGrokVideoEditConstants:
    """Tests for Grok Video Edit constants integration."""

    def test_model_has_endpoint(self):
        """Verify grok_video_edit has endpoint defined."""
        assert "grok_video_edit" in MODEL_ENDPOINTS
        assert MODEL_ENDPOINTS["grok_video_edit"] == "xai/grok-imagine-video/edit-video"

    def test_model_has_display_name(self):
        """Verify grok_video_edit has display name."""
        assert "grok_video_edit" in MODEL_DISPLAY_NAMES
        assert MODEL_DISPLAY_NAMES["grok_video_edit"] == "xAI Grok Video Edit"

    def test_model_has_pricing(self):
        """Verify grok_video_edit has pricing defined."""
        assert "grok_video_edit" in MODEL_PRICING
        pricing = MODEL_PRICING["grok_video_edit"]
        assert pricing["input_per_second"] == 0.01
        assert pricing["output_per_second"] == 0.05

    def test_model_has_defaults(self):
        """Verify grok_video_edit has defaults defined."""
        assert "grok_video_edit" in MODEL_DEFAULTS
        defaults = MODEL_DEFAULTS["grok_video_edit"]
        assert defaults["resolution"] == "auto"

    def test_model_has_resolutions(self):
        """Verify grok_video_edit has supported resolutions."""
        assert "grok_video_edit" in SUPPORTED_RESOLUTIONS
        resolutions = SUPPORTED_RESOLUTIONS["grok_video_edit"]
        assert "auto" in resolutions
        assert "480p" in resolutions
        assert "720p" in resolutions

    def test_model_has_max_duration(self):
        """Verify grok_video_edit has max duration."""
        assert "grok_video_edit" in MAX_DURATIONS
        assert MAX_DURATIONS["grok_video_edit"] == 8

    def test_model_has_input_requirements(self):
        """Verify grok_video_edit has input requirements."""
        assert "grok_video_edit" in INPUT_REQUIREMENTS
        requirements = INPUT_REQUIREMENTS["grok_video_edit"]
        assert "video_url" in requirements["required"]
        assert "prompt" in requirements["required"]
        assert "resolution" in requirements["optional"]

    def test_model_in_video_to_video_category(self):
        """Verify grok_video_edit is in video_to_video category."""
        assert "video_to_video" in MODEL_CATEGORIES
        assert "grok_video_edit" in MODEL_CATEGORIES["video_to_video"]


class TestGrokVideoEditGenerator:
    """Tests for Grok Video Edit generator integration."""

    def test_generator_lists_model(self):
        """Verify generator lists grok_video_edit."""
        from fal_avatar.generator import FALAvatarGenerator

        generator = FALAvatarGenerator()
        models = generator.list_models()
        assert "grok_video_edit" in models

    def test_generator_model_info(self):
        """Verify generator can get model info."""
        from fal_avatar.generator import FALAvatarGenerator

        generator = FALAvatarGenerator()
        info = generator.get_model_info("grok_video_edit")
        assert info["name"] == "xAI Grok Video Edit"

    def test_generator_display_name(self):
        """Verify generator returns correct display name."""
        from fal_avatar.generator import FALAvatarGenerator

        generator = FALAvatarGenerator()
        display_name = generator.get_display_name("grok_video_edit")
        assert display_name == "xAI Grok Video Edit"

    def test_generator_input_requirements(self):
        """Verify generator returns correct input requirements."""
        from fal_avatar.generator import FALAvatarGenerator

        generator = FALAvatarGenerator()
        requirements = generator.get_input_requirements("grok_video_edit")
        assert "video_url" in requirements["required"]
        assert "prompt" in requirements["required"]

    def test_generator_cost_estimation(self):
        """Verify generator can estimate cost."""
        from fal_avatar.generator import FALAvatarGenerator

        generator = FALAvatarGenerator()
        cost = generator.estimate_cost("grok_video_edit", duration=6)
        assert cost == pytest.approx(0.36)

    def test_generator_validates_inputs(self):
        """Verify generator validates required inputs."""
        from fal_avatar.generator import FALAvatarGenerator

        generator = FALAvatarGenerator()
        with pytest.raises(ValueError, match="Missing required parameters"):
            generator.validate_inputs("grok_video_edit", video_url="test.mp4")
        # Missing prompt should fail

    def test_generator_validates_inputs_success(self):
        """Verify generator accepts valid inputs."""
        from fal_avatar.generator import FALAvatarGenerator

        generator = FALAvatarGenerator()
        result = generator.validate_inputs(
            "grok_video_edit",
            video_url="https://example.com/video.mp4",
            prompt="Colorize video"
        )
        assert result is True

    def test_generator_transform_video_grok_mode(self):
        """Verify transform_video routes to grok correctly."""
        from fal_avatar.generator import FALAvatarGenerator

        generator = FALAvatarGenerator()
        # We can't actually call the API, but we can verify the mode is valid
        # by checking if it doesn't return an error for invalid mode
        result = generator.transform_video(
            video_url="invalid",  # Will fail at URL validation
            prompt="test",
            mode="grok"
        )
        # Should fail at URL validation, not mode validation
        assert result.success is False
        assert "grok" not in result.error.lower() or "mode" not in result.error.lower()


class TestPackageExports:
    """Tests for package exports."""

    def test_model_exported_from_models(self):
        """Verify GrokVideoEditModel is exported from models."""
        from fal_avatar.models import GrokVideoEditModel
        assert GrokVideoEditModel is not None

    def test_model_exported_from_package(self):
        """Verify GrokVideoEditModel is exported from package."""
        from fal_avatar import GrokVideoEditModel
        assert GrokVideoEditModel is not None

    def test_generator_exported_from_package(self):
        """Verify FALAvatarGenerator is exported from package."""
        from fal_avatar import FALAvatarGenerator
        assert FALAvatarGenerator is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
