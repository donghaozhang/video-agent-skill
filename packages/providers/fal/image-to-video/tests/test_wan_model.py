"""
Tests for Wan v2.6 image-to-video model.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fal_image_to_video.models.wan import Wan26Model


class TestWan26Model:
    """Tests for Wan v2.6 model."""

    def test_init(self):
        """Test model initialization."""
        model = Wan26Model()
        assert model.model_key == "wan_2_6"
        assert model.endpoint == "wan/v2.6/image-to-video"

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = Wan26Model()
        params = model.validate_parameters()

        assert params["duration"] == "5"
        assert params["resolution"] == "1080p"
        assert params["enable_prompt_expansion"] is True
        assert params["multi_shots"] is False

    def test_validate_parameters_custom(self):
        """Test parameter validation with custom values."""
        model = Wan26Model()
        params = model.validate_parameters(
            duration="15",
            resolution="720p",
            multi_shots=True,
            seed=42
        )

        assert params["duration"] == "15"
        assert params["resolution"] == "720p"
        assert params["multi_shots"] is True
        assert params["seed"] == 42

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = Wan26Model()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration="20")

    def test_validate_parameters_long_negative_prompt(self):
        """Test validation fails for too long negative prompt."""
        model = Wan26Model()
        with pytest.raises(ValueError, match="max 500 characters"):
            model.validate_parameters(negative_prompt="x" * 501)

    def test_prepare_arguments_prompt_length(self):
        """Test prompt length validation."""
        model = Wan26Model()
        with pytest.raises(ValueError, match="max 800 characters"):
            model.prepare_arguments(
                prompt="x" * 801,
                image_url="https://example.com/image.jpg"
            )

    def test_estimate_cost_720p(self):
        """Test 720p cost estimation."""
        model = Wan26Model()
        assert model.estimate_cost(duration="5", resolution="720p") == 0.50
        assert model.estimate_cost(duration="15", resolution="720p") == 1.50

    def test_estimate_cost_1080p(self):
        """Test 1080p cost estimation."""
        model = Wan26Model()
        assert model.estimate_cost(duration="5", resolution="1080p") == 0.75
        assert model.estimate_cost(duration="15", resolution="1080p") == 2.25

    def test_prepare_arguments_with_audio(self):
        """Test arguments preparation with audio URL."""
        model = Wan26Model()
        args = model.prepare_arguments(
            prompt="Test prompt",
            image_url="https://example.com/image.jpg",
            audio_url="https://example.com/audio.mp3"
        )

        assert args["audio_url"] == "https://example.com/audio.mp3"

    def test_prepare_arguments_basic(self):
        """Test basic argument preparation."""
        model = Wan26Model()
        args = model.prepare_arguments(
            prompt="A beautiful scene",
            image_url="https://example.com/image.jpg",
            duration="10",
            resolution="720p"
        )

        assert args["prompt"] == "A beautiful scene"
        assert args["image_url"] == "https://example.com/image.jpg"
        assert args["duration"] == "10"
        assert args["resolution"] == "720p"

    def test_get_model_info(self):
        """Test model info retrieval."""
        model = Wan26Model()
        info = model.get_model_info()

        assert info["name"] == "Wan v2.6"
        assert info["provider"] == "Wan"
        assert info["max_duration"] == 15
        assert "prompt_expansion" in info["features"]
        assert "multi_shots" in info["features"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
