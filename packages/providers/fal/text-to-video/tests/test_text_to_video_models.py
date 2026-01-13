"""
Tests for text-to-video model implementations.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fal_text_to_video.models.kling import Kling26ProModel
from fal_text_to_video.models.sora import Sora2Model, Sora2ProModel
from fal_text_to_video.config.constants import (
    SUPPORTED_MODELS, MODEL_ENDPOINTS, MODEL_PRICING
)


class TestKling26ProModel:
    """Tests for Kling v2.6 Pro model."""

    def test_init(self):
        """Test model initialization."""
        model = Kling26ProModel()
        assert model.model_key == "kling_2_6_pro"
        assert model.endpoint == "fal-ai/kling-video/v2.6/pro/text-to-video"

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = Kling26ProModel()
        params = model.validate_parameters()

        assert params["duration"] == "5"
        assert params["aspect_ratio"] == "16:9"
        assert params["cfg_scale"] == 0.5
        assert params["generate_audio"] is True

    def test_validate_parameters_custom(self):
        """Test parameter validation with custom values."""
        model = Kling26ProModel()
        params = model.validate_parameters(
            duration="10",
            aspect_ratio="9:16",
            cfg_scale=0.7,
            generate_audio=False
        )

        assert params["duration"] == "10"
        assert params["aspect_ratio"] == "9:16"
        assert params["cfg_scale"] == 0.7
        assert params["generate_audio"] is False

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = Kling26ProModel()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration="15")

    def test_validate_parameters_invalid_cfg_scale(self):
        """Test validation fails for invalid cfg_scale."""
        model = Kling26ProModel()
        with pytest.raises(ValueError, match="cfg_scale must be"):
            model.validate_parameters(cfg_scale=1.5)

    def test_estimate_cost(self):
        """Test cost estimation."""
        model = Kling26ProModel()
        # With audio (default)
        assert model.estimate_cost(duration="5", generate_audio=True) == pytest.approx(0.70)
        assert model.estimate_cost(duration="10", generate_audio=True) == pytest.approx(1.40)
        # Without audio
        assert model.estimate_cost(duration="5", generate_audio=False) == pytest.approx(0.35)
        assert model.estimate_cost(duration="10", generate_audio=False) == pytest.approx(0.70)

    def test_prepare_arguments(self):
        """Test argument preparation."""
        model = Kling26ProModel()
        args = model.prepare_arguments(
            prompt="A beautiful sunset",
            duration="5",
            aspect_ratio="16:9"
        )
        assert args["prompt"] == "A beautiful sunset"
        assert args["duration"] == "5"
        assert args["aspect_ratio"] == "16:9"


class TestSora2Model:
    """Tests for Sora 2 model."""

    def test_init(self):
        """Test model initialization."""
        model = Sora2Model()
        assert model.model_key == "sora_2"
        assert model.endpoint == "fal-ai/sora-2/text-to-video"

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = Sora2Model()
        params = model.validate_parameters()

        assert params["duration"] == 4
        assert params["resolution"] == "720p"
        assert params["aspect_ratio"] == "16:9"

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = Sora2Model()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration=6)

    def test_estimate_cost(self):
        """Test cost estimation."""
        model = Sora2Model()
        assert model.estimate_cost(duration=4) == pytest.approx(0.40)
        assert model.estimate_cost(duration=12) == pytest.approx(1.20)

    def test_prepare_arguments(self):
        """Test argument preparation."""
        model = Sora2Model()
        args = model.prepare_arguments(
            prompt="A cinematic scene",
            duration=8,
            aspect_ratio="9:16"
        )
        assert args["prompt"] == "A cinematic scene"
        assert args["duration"] == 8
        assert args["aspect_ratio"] == "9:16"


class TestSora2ProModel:
    """Tests for Sora 2 Pro model."""

    def test_init(self):
        """Test model initialization."""
        model = Sora2ProModel()
        assert model.model_key == "sora_2_pro"

    def test_validate_parameters_1080p(self):
        """Test 1080p resolution validation."""
        model = Sora2ProModel()
        params = model.validate_parameters(resolution="1080p")
        assert params["resolution"] == "1080p"

    def test_estimate_cost_resolution_pricing(self):
        """Test resolution-based pricing."""
        model = Sora2ProModel()
        # 720p pricing
        assert model.estimate_cost(duration=4, resolution="720p") == pytest.approx(1.20)
        # 1080p pricing
        assert model.estimate_cost(duration=4, resolution="1080p") == pytest.approx(2.00)

    def test_prepare_arguments(self):
        """Test argument preparation."""
        model = Sora2ProModel()
        args = model.prepare_arguments(
            prompt="Professional footage",
            duration=4,
            resolution="1080p"
        )
        assert args["prompt"] == "Professional footage"
        assert args["resolution"] == "1080p"


class TestConstants:
    """Tests for constants configuration."""

    def test_all_models_have_endpoints(self):
        """Verify all supported models have endpoints."""
        for model in SUPPORTED_MODELS:
            assert model in MODEL_ENDPOINTS, f"Missing endpoint for {model}"

    def test_all_models_have_pricing(self):
        """Verify all supported models have pricing."""
        for model in SUPPORTED_MODELS:
            assert model in MODEL_PRICING, f"Missing pricing for {model}"

    def test_supported_models_count(self):
        """Verify expected number of supported models."""
        assert len(SUPPORTED_MODELS) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
