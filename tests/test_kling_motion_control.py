"""
Unit tests for Kling Video v2.6 Motion Control model.
"""

import pytest
from unittest.mock import patch, MagicMock

from fal_avatar.models.kling import KlingMotionControlModel
from fal_avatar.models.base import AvatarGenerationResult
from fal_avatar.config.constants import (
    MODEL_ENDPOINTS,
    MODEL_DISPLAY_NAMES,
    MODEL_PRICING,
    MODEL_DEFAULTS,
    MAX_DURATIONS,
    INPUT_REQUIREMENTS,
    MODEL_CATEGORIES,
)


class TestKlingMotionControlModel:
    """Tests for KlingMotionControlModel class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.model = KlingMotionControlModel()

    def test_model_initialization(self):
        """Test model initializes with correct attributes."""
        assert self.model.model_name == "kling_motion_control"
        assert self.model.endpoint == "fal-ai/kling-video/v2.6/standard/motion-control"
        assert self.model.pricing["per_second"] == 0.06

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid inputs."""
        params = self.model.validate_parameters(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
            character_orientation="video",
            keep_original_sound=True
        )
        assert params["image_url"] == "https://example.com/image.jpg"
        assert params["video_url"] == "https://example.com/video.mp4"
        assert params["character_orientation"] == "video"
        assert params["keep_original_sound"] is True

    def test_validate_parameters_with_defaults(self):
        """Test parameter validation uses defaults correctly."""
        params = self.model.validate_parameters(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4"
        )
        assert params["character_orientation"] == "video"  # Default
        assert params["keep_original_sound"] is True  # Default

    def test_validate_parameters_missing_image_url(self):
        """Test validation fails when image_url is missing."""
        with pytest.raises(ValueError, match="image_url is required"):
            self.model.validate_parameters(
                image_url=None,
                video_url="https://example.com/video.mp4"
            )

    def test_validate_parameters_missing_video_url(self):
        """Test validation fails when video_url is missing."""
        with pytest.raises(ValueError, match="video_url is required"):
            self.model.validate_parameters(
                image_url="https://example.com/image.jpg",
                video_url=None
            )

    def test_validate_parameters_invalid_orientation(self):
        """Test validation fails with invalid orientation."""
        with pytest.raises(ValueError, match="character_orientation must be one of"):
            self.model.validate_parameters(
                image_url="https://example.com/image.jpg",
                video_url="https://example.com/video.mp4",
                character_orientation="invalid"
            )

    def test_validate_parameters_with_prompt(self):
        """Test validation includes optional prompt."""
        params = self.model.validate_parameters(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
            prompt="A person dancing gracefully"
        )
        assert params["prompt"] == "A person dancing gracefully"

    def test_get_model_info(self):
        """Test model info returns expected structure."""
        info = self.model.get_model_info()
        assert info["name"] == "kling_motion_control"
        assert info["display_name"] == "Kling v2.6 Motion Control"
        assert info["orientation_options"] == ["video", "image"]
        assert "motion transfer" in info["best_for"]

    def test_estimate_cost_video_orientation(self):
        """Test cost estimation for video orientation."""
        cost = self.model.estimate_cost(10, character_orientation="video")
        assert cost == pytest.approx(0.60)  # 10 sec * $0.06

    def test_estimate_cost_image_orientation(self):
        """Test cost estimation for image orientation."""
        cost = self.model.estimate_cost(10, character_orientation="image")
        assert cost == pytest.approx(0.60)  # 10 sec * $0.06

    def test_estimate_cost_capped_at_max(self):
        """Test cost estimation caps at max duration."""
        # Video orientation max is 30s
        cost_video = self.model.estimate_cost(60, character_orientation="video")
        assert cost_video == pytest.approx(1.80)  # Capped at 30 sec * $0.06

        # Image orientation max is 10s
        cost_image = self.model.estimate_cost(60, character_orientation="image")
        assert cost_image == pytest.approx(0.60)  # Capped at 10 sec * $0.06


class TestKlingMotionControlConstants:
    """Tests for motion control constants configuration."""

    def test_endpoint_configured(self):
        """Test endpoint is properly configured."""
        assert "kling_motion_control" in MODEL_ENDPOINTS
        assert MODEL_ENDPOINTS["kling_motion_control"] == "fal-ai/kling-video/v2.6/standard/motion-control"

    def test_display_name_configured(self):
        """Test display name is configured."""
        assert "kling_motion_control" in MODEL_DISPLAY_NAMES
        assert MODEL_DISPLAY_NAMES["kling_motion_control"] == "Kling v2.6 Motion Control"

    def test_pricing_configured(self):
        """Test pricing is configured."""
        assert "kling_motion_control" in MODEL_PRICING
        assert MODEL_PRICING["kling_motion_control"]["per_second"] == 0.06

    def test_defaults_configured(self):
        """Test default values are configured."""
        assert "kling_motion_control" in MODEL_DEFAULTS
        defaults = MODEL_DEFAULTS["kling_motion_control"]
        assert defaults["character_orientation"] == "video"
        assert defaults["keep_original_sound"] is True

    def test_max_durations_configured(self):
        """Test max durations are configured per orientation."""
        assert "kling_motion_control" in MAX_DURATIONS
        durations = MAX_DURATIONS["kling_motion_control"]
        assert durations["video"] == 30
        assert durations["image"] == 10

    def test_input_requirements_configured(self):
        """Test input requirements include both image and video."""
        assert "kling_motion_control" in INPUT_REQUIREMENTS
        requirements = INPUT_REQUIREMENTS["kling_motion_control"]
        assert "image_url" in requirements["required"]
        assert "video_url" in requirements["required"]
        assert "character_orientation" in requirements["optional"]

    def test_model_category_configured(self):
        """Test model is in motion_transfer category."""
        assert "motion_transfer" in MODEL_CATEGORIES
        assert "kling_motion_control" in MODEL_CATEGORIES["motion_transfer"]


class TestKlingMotionControlGenerate:
    """Tests for generate method with mocked API."""

    def setup_method(self):
        """Set up test fixtures."""
        self.model = KlingMotionControlModel()

    @patch.object(KlingMotionControlModel, '_call_fal_api')
    def test_generate_success(self, mock_api):
        """Test successful video generation."""
        mock_api.return_value = {
            "success": True,
            "result": {
                "video": {
                    "url": "https://fal.media/output/video.mp4",
                    "file_size": 1024000,
                    "file_name": "output.mp4"
                },
                "duration": 10
            },
            "processing_time": 45.5
        }

        result = self.model.generate(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
            character_orientation="video"
        )

        assert result.success is True
        assert result.video_url == "https://fal.media/output/video.mp4"
        assert result.duration == 10
        assert result.cost == 0.60
        assert result.processing_time == 45.5
        assert result.metadata["character_orientation"] == "video"

    @patch.object(KlingMotionControlModel, '_call_fal_api')
    def test_generate_api_failure(self, mock_api):
        """Test handling of API failure."""
        mock_api.return_value = {
            "success": False,
            "error": "API rate limit exceeded",
            "processing_time": 0.5
        }

        result = self.model.generate(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4"
        )

        assert result.success is False
        assert "rate limit" in result.error.lower()

    def test_generate_validation_failure(self):
        """Test handling of validation failure."""
        result = self.model.generate(
            image_url=None,
            video_url="https://example.com/video.mp4"
        )

        assert result.success is False
        assert "image_url" in result.error.lower()


class TestFALAvatarGeneratorIntegration:
    """Tests for generator integration with motion control model."""

    def test_generator_includes_motion_control(self):
        """Test that generator includes the motion control model."""
        from fal_avatar import FALAvatarGenerator

        generator = FALAvatarGenerator()
        assert "kling_motion_control" in generator.list_models()

    def test_generator_transfer_motion_method(self):
        """Test that transfer_motion convenience method exists."""
        from fal_avatar import FALAvatarGenerator

        generator = FALAvatarGenerator()
        assert hasattr(generator, "transfer_motion")

    def test_generator_model_info(self):
        """Test getting model info through generator."""
        from fal_avatar import FALAvatarGenerator

        generator = FALAvatarGenerator()
        info = generator.get_model_info("kling_motion_control")

        assert info["name"] == "kling_motion_control"
        assert info["display_name"] == "Kling v2.6 Motion Control"

    def test_generator_recommend_motion_transfer(self):
        """Test motion_transfer recommendation."""
        from fal_avatar import FALAvatarGenerator

        generator = FALAvatarGenerator()
        recommended = generator.recommend_model("motion_transfer")

        assert recommended == "kling_motion_control"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
