"""
Unit tests for FAL Image-to-Video models.
"""

import pytest
import sys
from pathlib import Path

# Add package to path
_package_path = Path(__file__).parent.parent / "fal_image_to_video"
sys.path.insert(0, str(_package_path.parent))

from fal_image_to_video.config.constants import (
    SUPPORTED_MODELS,
    MODEL_ENDPOINTS,
    DURATION_OPTIONS,
    RESOLUTION_OPTIONS
)
from fal_image_to_video.models.sora import Sora2Model, Sora2ProModel
from fal_image_to_video.models.veo import Veo31FastModel
from fal_image_to_video.models.seedance import SeedanceModel
from fal_image_to_video.models.kling import KlingModel, Kling26ProModel
from fal_image_to_video.models.hailuo import HailuoModel


class TestConstants:
    """Tests for constants configuration."""

    def test_all_models_have_endpoints(self):
        """Every supported model should have an endpoint."""
        for model in SUPPORTED_MODELS:
            assert model in MODEL_ENDPOINTS

    def test_all_models_have_duration_options(self):
        """Every supported model should have duration options."""
        for model in SUPPORTED_MODELS:
            assert model in DURATION_OPTIONS

    def test_supported_models_count(self):
        """Should have 7 supported models."""
        assert len(SUPPORTED_MODELS) == 7


class TestSora2Model:
    """Tests for Sora 2 model."""

    def test_valid_parameters(self):
        """Valid parameters should pass validation."""
        model = Sora2Model()
        params = model.validate_parameters(
            duration=8,
            resolution="720p",
            aspect_ratio="16:9"
        )
        assert params["duration"] == 8
        assert params["resolution"] == "720p"

    def test_invalid_duration_raises_error(self):
        """Invalid duration should raise ValueError."""
        model = Sora2Model()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(duration=15)
        assert "Invalid duration" in str(exc_info.value)

    def test_invalid_resolution_raises_error(self):
        """Invalid resolution should raise ValueError."""
        model = Sora2Model()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(resolution="4K")
        assert "Invalid resolution" in str(exc_info.value)

    def test_default_parameters(self):
        """Default parameters should be applied."""
        model = Sora2Model()
        params = model.validate_parameters()
        assert params["duration"] == 4
        assert params["resolution"] == "auto"
        assert params["aspect_ratio"] == "auto"


class TestSora2ProModel:
    """Tests for Sora 2 Pro model."""

    def test_supports_1080p(self):
        """Sora 2 Pro should support 1080p resolution."""
        model = Sora2ProModel()
        params = model.validate_parameters(resolution="1080p")
        assert params["resolution"] == "1080p"

    def test_cost_estimation(self):
        """Cost estimation should vary by resolution."""
        model = Sora2ProModel()
        cost_720p = model.estimate_cost(duration=4, resolution="720p")
        cost_1080p = model.estimate_cost(duration=4, resolution="1080p")
        assert cost_1080p > cost_720p
        assert cost_720p == 1.20  # $0.30 * 4
        assert cost_1080p == 2.00  # $0.50 * 4


class TestVeo31FastModel:
    """Tests for Veo 3.1 Fast model."""

    def test_valid_duration_format(self):
        """Duration should accept string format (e.g., '8s')."""
        model = Veo31FastModel()
        params = model.validate_parameters(duration="6s")
        assert params["duration"] == "6s"

    def test_audio_generation_option(self):
        """Audio generation should be configurable."""
        model = Veo31FastModel()
        params = model.validate_parameters(generate_audio=False)
        assert params["generate_audio"] is False

    def test_cost_with_audio(self):
        """Cost should be higher with audio enabled."""
        model = Veo31FastModel()
        cost_no_audio = model.estimate_cost("8s", generate_audio=False)
        cost_with_audio = model.estimate_cost("8s", generate_audio=True)
        assert cost_with_audio > cost_no_audio
        assert cost_no_audio == 0.80  # $0.10 * 8
        assert cost_with_audio == 1.20  # $0.15 * 8

    def test_invalid_duration_raises_error(self):
        """Invalid duration format should raise ValueError."""
        model = Veo31FastModel()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(duration="10s")
        assert "Invalid duration" in str(exc_info.value)


class TestSeedanceModel:
    """Tests for Seedance model."""

    def test_seed_parameter(self):
        """Seed parameter should be optional."""
        model = SeedanceModel()
        params = model.validate_parameters(seed=12345)
        assert params["seed"] == 12345

    def test_seed_none_by_default(self):
        """Seed should be None by default."""
        model = SeedanceModel()
        params = model.validate_parameters()
        assert params["seed"] is None

    def test_invalid_seed_raises_error(self):
        """Negative seed should raise ValueError."""
        model = SeedanceModel()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(seed=-1)
        assert "non-negative" in str(exc_info.value)

    def test_valid_durations(self):
        """Valid durations should pass."""
        model = SeedanceModel()
        params = model.validate_parameters(duration="10")
        assert params["duration"] == "10"


class TestKlingModels:
    """Tests for Kling models."""

    def test_cfg_scale_validation(self):
        """CFG scale should be between 0 and 1."""
        model = KlingModel()
        params = model.validate_parameters(cfg_scale=0.7)
        assert params["cfg_scale"] == 0.7

    def test_invalid_cfg_scale_raises_error(self):
        """CFG scale > 1 should raise ValueError."""
        model = Kling26ProModel()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(cfg_scale=1.5)
        assert "cfg_scale" in str(exc_info.value)

    def test_negative_prompt_default(self):
        """Default negative prompt should be set."""
        model = KlingModel()
        params = model.validate_parameters()
        assert "blur" in params["negative_prompt"]

    def test_kling_pro_is_professional(self):
        """Kling Pro should be marked as professional tier."""
        model = Kling26ProModel()
        info = model.get_model_info()
        assert info.get("professional_tier") is True


class TestHailuoModel:
    """Tests for Hailuo model."""

    def test_prompt_optimizer_default(self):
        """Prompt optimizer should be enabled by default."""
        model = HailuoModel()
        params = model.validate_parameters()
        assert params["prompt_optimizer"] is True

    def test_prompt_optimizer_disabled(self):
        """Prompt optimizer can be disabled."""
        model = HailuoModel()
        params = model.validate_parameters(prompt_optimizer=False)
        assert params["prompt_optimizer"] is False

    def test_valid_durations(self):
        """Hailuo should support 6 and 10 second durations."""
        model = HailuoModel()
        params_6 = model.validate_parameters(duration="6")
        params_10 = model.validate_parameters(duration="10")
        assert params_6["duration"] == "6"
        assert params_10["duration"] == "10"

    def test_invalid_duration_raises_error(self):
        """Duration 5 should be invalid for Hailuo."""
        model = HailuoModel()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(duration="5")
        assert "Invalid duration" in str(exc_info.value)


class TestModelInfo:
    """Tests for model info methods."""

    def test_all_models_have_info(self):
        """All models should return valid info."""
        models = [
            Sora2Model(),
            Sora2ProModel(),
            Veo31FastModel(),
            SeedanceModel(),
            KlingModel(),
            Kling26ProModel(),
            HailuoModel()
        ]
        for model in models:
            info = model.get_model_info()
            assert "endpoint" in info
            assert "price_per_second" in info

    def test_veo_supports_audio(self):
        """Veo model info should indicate audio support."""
        model = Veo31FastModel()
        info = model.get_model_info()
        assert info.get("supports_audio") is True

    def test_seedance_supports_seed(self):
        """Seedance model info should indicate seed support."""
        model = SeedanceModel()
        info = model.get_model_info()
        assert info.get("supports_seed") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
