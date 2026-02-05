"""
Unit tests for Kling O3 Image-to-Video models.

Tests:
- Model instantiation
- Parameter validation
- Cost estimation
- API argument preparation
"""

import pytest
from fal_image_to_video.models.kling_o3 import (
    KlingO3StandardI2VModel,
    KlingO3ProI2VModel,
    KlingO3StandardRefModel,
    KlingO3ProRefModel
)


class TestKlingO3StandardI2VModel:
    """Tests for Kling O3 Standard Image-to-Video model."""

    def test_model_instantiation(self):
        """Test model can be instantiated."""
        model = KlingO3StandardI2VModel()
        assert model.model_key == "kling_o3_standard_i2v"
        assert "o3/standard/image-to-video" in model.endpoint

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = KlingO3StandardI2VModel()
        params = model.validate_parameters()

        assert params["duration"] == "5"
        assert params["generate_audio"] is True
        assert params["aspect_ratio"] == "16:9"
        assert params["elements"] == []

    def test_validate_parameters_custom(self):
        """Test parameter validation with custom values."""
        model = KlingO3StandardI2VModel()
        params = model.validate_parameters(
            duration="10",
            generate_audio=False,
            aspect_ratio="9:16",
            elements=[{"frontal_image_url": "http://example.com/img.jpg"}]
        )

        assert params["duration"] == "10"
        assert params["generate_audio"] is False
        assert params["aspect_ratio"] == "9:16"
        assert len(params["elements"]) == 1

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = KlingO3StandardI2VModel()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration="20")

    def test_validate_parameters_invalid_aspect_ratio(self):
        """Test validation fails for invalid aspect ratio."""
        model = KlingO3StandardI2VModel()
        with pytest.raises(ValueError, match="Invalid aspect_ratio"):
            model.validate_parameters(aspect_ratio="4:3")

    def test_prepare_arguments(self):
        """Test API argument preparation."""
        model = KlingO3StandardI2VModel()
        args = model.prepare_arguments(
            prompt="Test prompt with @Element1",
            image_url="http://example.com/image.jpg",
            duration="5",
            generate_audio=True,
            elements=[{"frontal_image_url": "http://example.com/char.jpg"}]
        )

        assert args["prompt"] == "Test prompt with @Element1"
        assert args["image_url"] == "http://example.com/image.jpg"
        assert args["duration"] == 5
        assert args["generate_audio"] is True
        assert "elements" in args

    def test_cost_estimation_no_audio(self):
        """Test cost estimation without audio."""
        model = KlingO3StandardI2VModel()
        cost = model.estimate_cost(duration=5, generate_audio=False)
        assert cost == 0.168 * 5  # $0.168/s

    def test_cost_estimation_with_audio(self):
        """Test cost estimation with audio."""
        model = KlingO3StandardI2VModel()
        cost = model.estimate_cost(duration=10, generate_audio=True)
        assert cost == 0.224 * 10  # $0.224/s

    def test_get_model_info(self):
        """Test model info retrieval."""
        model = KlingO3StandardI2VModel()
        info = model.get_model_info()

        assert info["endpoint"] == model.endpoint
        assert info["audio_supported"] is True
        assert info["elements_supported"] is True


class TestKlingO3ProI2VModel:
    """Tests for Kling O3 Pro Image-to-Video model."""

    def test_model_instantiation(self):
        """Test model can be instantiated."""
        model = KlingO3ProI2VModel()
        assert model.model_key == "kling_o3_pro_i2v"
        assert "o3/pro/image-to-video" in model.endpoint

    def test_cost_estimation_no_audio(self):
        """Test cost estimation without audio."""
        model = KlingO3ProI2VModel()
        cost = model.estimate_cost(duration=5, generate_audio=False)
        assert cost == 0.224 * 5  # $0.224/s

    def test_cost_estimation_with_audio(self):
        """Test cost estimation with audio."""
        model = KlingO3ProI2VModel()
        cost = model.estimate_cost(duration=10, generate_audio=True)
        assert cost == 0.28 * 10  # $0.28/s

    def test_get_model_info_professional_tier(self):
        """Test model info shows professional tier."""
        model = KlingO3ProI2VModel()
        info = model.get_model_info()
        assert info["professional_tier"] is True


class TestKlingO3StandardRefModel:
    """Tests for Kling O3 Standard Reference-to-Video model."""

    def test_model_instantiation(self):
        """Test model can be instantiated."""
        model = KlingO3StandardRefModel()
        assert model.model_key == "kling_o3_standard_ref"
        assert "o3/standard/reference-to-video" in model.endpoint

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = KlingO3StandardRefModel()
        params = model.validate_parameters()

        assert params["duration"] == "5"
        assert params["generate_audio"] is False  # Default off for ref models
        assert params["elements"] == []

    def test_prepare_arguments_reference_syntax(self):
        """Test API argument preparation with @ reference syntax."""
        model = KlingO3StandardRefModel()
        args = model.prepare_arguments(
            prompt="@Element1 and @Element2 enters the scene",
            image_url="http://example.com/background.jpg",
            duration="8",
            elements=[
                {"frontal_image_url": "http://example.com/char1.jpg"},
                {"frontal_image_url": "http://example.com/char2.jpg"}
            ]
        )

        assert "@Element1" in args["prompt"]
        assert "@Element2" in args["prompt"]
        assert len(args["elements"]) == 2
        assert args["start_image_url"] == "http://example.com/background.jpg"

    def test_cost_estimation(self):
        """Test cost estimation."""
        model = KlingO3StandardRefModel()

        # Without audio: $0.084/s
        cost_no_audio = model.estimate_cost(duration=5, generate_audio=False)
        assert cost_no_audio == 0.084 * 5

        # With audio: $0.112/s
        cost_audio = model.estimate_cost(duration=5, generate_audio=True)
        assert cost_audio == 0.112 * 5

    def test_get_model_info_reference_syntax(self):
        """Test model info shows reference syntax support."""
        model = KlingO3StandardRefModel()
        info = model.get_model_info()
        assert info["reference_syntax"] is True


class TestKlingO3ProRefModel:
    """Tests for Kling O3 Pro Reference-to-Video model."""

    def test_model_instantiation(self):
        """Test model can be instantiated."""
        model = KlingO3ProRefModel()
        assert model.model_key == "kling_o3_pro_ref"
        assert "o3/pro/reference-to-video" in model.endpoint

    def test_cost_estimation(self):
        """Test cost estimation."""
        model = KlingO3ProRefModel()

        # Without audio: $0.224/s
        cost_no_audio = model.estimate_cost(duration=5, generate_audio=False)
        assert cost_no_audio == 0.224 * 5

        # With audio: $0.28/s
        cost_audio = model.estimate_cost(duration=10, generate_audio=True)
        assert cost_audio == 0.28 * 10

    def test_get_model_info_professional_tier(self):
        """Test model info shows professional tier."""
        model = KlingO3ProRefModel()
        info = model.get_model_info()
        assert info["professional_tier"] is True
        assert info["reference_syntax"] is True


class TestElementsParameter:
    """Tests for elements parameter handling."""

    def test_elements_must_be_list(self):
        """Test that elements must be a list."""
        model = KlingO3StandardI2VModel()
        with pytest.raises(ValueError, match="elements must be a list"):
            model.validate_parameters(elements="not a list")

    def test_empty_elements_allowed(self):
        """Test that empty elements list is allowed."""
        model = KlingO3StandardI2VModel()
        params = model.validate_parameters(elements=[])
        assert params["elements"] == []

    def test_elements_with_frontal_image(self):
        """Test elements with frontal_image_url."""
        model = KlingO3ProRefModel()
        params = model.validate_parameters(
            elements=[{
                "frontal_image_url": "http://example.com/character.jpg",
                "reference_image_urls": [
                    "http://example.com/pose1.jpg",
                    "http://example.com/pose2.jpg"
                ]
            }]
        )
        assert len(params["elements"]) == 1
        assert "frontal_image_url" in params["elements"][0]


class TestCfgScaleValidation:
    """Tests for cfg_scale parameter validation."""

    def test_cfg_scale_valid_range(self):
        """Test valid cfg_scale values."""
        model = KlingO3StandardI2VModel()
        params = model.validate_parameters(cfg_scale=0.5)
        assert params["cfg_scale"] == 0.5

    def test_cfg_scale_boundary_values(self):
        """Test cfg_scale boundary values."""
        model = KlingO3StandardI2VModel()

        params_zero = model.validate_parameters(cfg_scale=0.0)
        assert params_zero["cfg_scale"] == 0.0

        params_one = model.validate_parameters(cfg_scale=1.0)
        assert params_one["cfg_scale"] == 1.0

    def test_cfg_scale_invalid(self):
        """Test invalid cfg_scale values."""
        model = KlingO3StandardI2VModel()
        with pytest.raises(ValueError, match="cfg_scale must be between"):
            model.validate_parameters(cfg_scale=1.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
