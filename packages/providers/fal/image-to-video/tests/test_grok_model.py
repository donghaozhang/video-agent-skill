"""
Tests for xAI Grok Imagine Video image-to-video model.

Run with: pytest packages/providers/fal/image-to-video/tests/test_grok_model.py
Or install package first: pip install -e .
"""

import pytest

# Try normal import first (when package is installed via pip install -e .)
# Fall back to path modification for direct script execution
try:
    from fal_image_to_video.models.grok import GrokImagineModel
    from fal_image_to_video.config.constants import (
        SUPPORTED_MODELS, MODEL_ENDPOINTS, MODEL_PRICING,
        DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS,
        MODEL_EXTENDED_FEATURES
    )
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from fal_image_to_video.models.grok import GrokImagineModel
    from fal_image_to_video.config.constants import (
        SUPPORTED_MODELS, MODEL_ENDPOINTS, MODEL_PRICING,
        DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS,
        MODEL_EXTENDED_FEATURES
    )


class TestGrokImagineModel:
    """Tests for xAI Grok Imagine Video image-to-video model."""

    def test_init(self):
        """Test model initialization."""
        model = GrokImagineModel()
        assert model.model_key == "grok_imagine"
        assert model.endpoint == "xai/grok-imagine-video/image-to-video"
        assert model.display_name == "xAI Grok Imagine Video"

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = GrokImagineModel()
        params = model.validate_parameters()

        assert params["duration"] == 6
        assert params["resolution"] == "720p"
        assert params["aspect_ratio"] == "auto"

    def test_validate_parameters_custom(self):
        """Test parameter validation with custom values."""
        model = GrokImagineModel()
        params = model.validate_parameters(
            duration=10,
            resolution="480p",
            aspect_ratio="9:16"
        )

        assert params["duration"] == 10
        assert params["resolution"] == "480p"
        assert params["aspect_ratio"] == "9:16"

    def test_validate_parameters_edge_case_min_duration(self):
        """Test minimum duration (1 second) is valid."""
        model = GrokImagineModel()
        params = model.validate_parameters(duration=1)
        assert params["duration"] == 1

    def test_validate_parameters_edge_case_max_duration(self):
        """Test maximum duration (15 seconds) is valid."""
        model = GrokImagineModel()
        params = model.validate_parameters(duration=15)
        assert params["duration"] == 15

    def test_validate_parameters_invalid_duration_zero(self):
        """Test validation fails for zero duration."""
        model = GrokImagineModel()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration=0)

    def test_validate_parameters_invalid_duration_over_max(self):
        """Test validation fails for duration over 15 seconds."""
        model = GrokImagineModel()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration=16)

    def test_validate_parameters_invalid_resolution(self):
        """Test validation fails for invalid resolution."""
        model = GrokImagineModel()
        with pytest.raises(ValueError, match="Invalid resolution"):
            model.validate_parameters(resolution="1080p")

    def test_validate_parameters_invalid_aspect_ratio(self):
        """Test validation fails for invalid aspect ratio."""
        model = GrokImagineModel()
        with pytest.raises(ValueError, match="Invalid aspect_ratio"):
            model.validate_parameters(aspect_ratio="21:9")

    def test_estimate_cost_base(self):
        """Test cost estimation for base 6-second video."""
        model = GrokImagineModel()
        # 6 seconds = $0.002 image + 6 * $0.05 = $0.302
        assert model.estimate_cost(duration=6) == pytest.approx(0.302)

    def test_estimate_cost_short_video(self):
        """Test cost estimation for video shorter than 6 seconds."""
        model = GrokImagineModel()
        # 3 seconds = $0.002 image + 3 * $0.05 = $0.152
        assert model.estimate_cost(duration=3) == pytest.approx(0.152)
        # 1 second = $0.002 image + 1 * $0.05 = $0.052
        assert model.estimate_cost(duration=1) == pytest.approx(0.052)

    def test_estimate_cost_long_video(self):
        """Test cost estimation for video longer than 6 seconds."""
        model = GrokImagineModel()
        # 10 seconds = $0.002 image + 10 * $0.05 = $0.502
        assert model.estimate_cost(duration=10) == pytest.approx(0.502)
        # 15 seconds = $0.002 image + 15 * $0.05 = $0.752
        assert model.estimate_cost(duration=15) == pytest.approx(0.752)

    def test_prepare_arguments(self):
        """Test argument preparation for API call."""
        model = GrokImagineModel()
        args = model.prepare_arguments(
            prompt="A beautiful sunset over the ocean",
            image_url="https://example.com/image.jpg",
            duration=8,
            resolution="720p",
            aspect_ratio="16:9"
        )

        assert args["prompt"] == "A beautiful sunset over the ocean"
        assert args["image_url"] == "https://example.com/image.jpg"
        assert args["duration"] == 8
        assert args["resolution"] == "720p"
        assert args["aspect_ratio"] == "16:9"

    def test_prepare_arguments_with_defaults(self):
        """Test argument preparation uses correct defaults."""
        model = GrokImagineModel()
        args = model.prepare_arguments(
            prompt="Test prompt",
            image_url="https://example.com/test.jpg"
        )

        assert args["prompt"] == "Test prompt"
        assert args["image_url"] == "https://example.com/test.jpg"
        assert args["duration"] == 6
        assert args["resolution"] == "720p"
        assert args["aspect_ratio"] == "auto"

    def test_get_model_info(self):
        """Test model info contains expected fields."""
        model = GrokImagineModel()
        info = model.get_model_info()

        assert info["name"] == "xAI Grok Imagine Video"
        assert info["provider"] == "xAI (via FAL)"
        assert info["max_duration"] == 15
        assert "audio_generation" in info["features"]
        assert info["endpoint"] == "xai/grok-imagine-video/image-to-video"

    def test_all_aspect_ratios_valid(self):
        """Test all documented aspect ratios are accepted."""
        model = GrokImagineModel()
        valid_ratios = ["auto", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16"]

        for ratio in valid_ratios:
            params = model.validate_parameters(aspect_ratio=ratio)
            assert params["aspect_ratio"] == ratio


class TestGrokImagineConstants:
    """Tests for Grok Imagine constants integration."""

    def test_model_in_supported_models(self):
        """Verify grok_imagine is in SUPPORTED_MODELS."""
        assert "grok_imagine" in SUPPORTED_MODELS

    def test_model_has_endpoint(self):
        """Verify grok_imagine has endpoint defined."""
        assert "grok_imagine" in MODEL_ENDPOINTS
        assert MODEL_ENDPOINTS["grok_imagine"] == "xai/grok-imagine-video/image-to-video"

    def test_model_has_pricing(self):
        """Verify grok_imagine has pricing defined."""
        assert "grok_imagine" in MODEL_PRICING
        assert MODEL_PRICING["grok_imagine"] == 0.05  # $0.05/second

    def test_model_has_duration_options(self):
        """Verify grok_imagine has duration options."""
        assert "grok_imagine" in DURATION_OPTIONS
        durations = DURATION_OPTIONS["grok_imagine"]
        assert 1 in durations
        assert 15 in durations

    def test_model_has_resolution_options(self):
        """Verify grok_imagine has resolution options."""
        assert "grok_imagine" in RESOLUTION_OPTIONS
        resolutions = RESOLUTION_OPTIONS["grok_imagine"]
        assert "480p" in resolutions
        assert "720p" in resolutions

    def test_model_has_aspect_ratio_options(self):
        """Verify grok_imagine has aspect ratio options."""
        assert "grok_imagine" in ASPECT_RATIO_OPTIONS
        ratios = ASPECT_RATIO_OPTIONS["grok_imagine"]
        assert "auto" in ratios
        assert "16:9" in ratios
        assert "9:16" in ratios
        assert "1:1" in ratios

    def test_model_has_extended_features(self):
        """Verify grok_imagine has extended features defined."""
        assert "grok_imagine" in MODEL_EXTENDED_FEATURES
        features = MODEL_EXTENDED_FEATURES["grok_imagine"]
        assert features["start_frame"] is True
        assert features["end_frame"] is False
        assert features["audio_input"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
