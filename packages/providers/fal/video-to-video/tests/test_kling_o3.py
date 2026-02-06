"""
Unit tests for Kling O3 Video-to-Video models.

Tests:
- Model instantiation
- Parameter validation
- Cost estimation
- API argument preparation
"""

import pytest
from fal_video_to_video.models.kling_o3 import (
    KlingO3StandardEditModel,
    KlingO3ProEditModel,
    KlingO3StandardV2VRefModel,
    KlingO3ProV2VRefModel
)


class TestKlingO3StandardEditModel:
    """Tests for Kling O3 Standard Video Edit model."""

    def test_model_instantiation(self):
        """Test model can be instantiated."""
        model = KlingO3StandardEditModel()
        assert model.model_key == "kling_o3_standard_edit"
        assert "o3/standard/video-to-video/edit" in model.endpoint

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = KlingO3StandardEditModel()
        params = model.validate_parameters()

        assert params["duration"] == "5"
        assert params["aspect_ratio"] == "16:9"
        assert params["elements"] == []
        assert params["image_urls"] == []

    def test_validate_parameters_custom(self):
        """Test parameter validation with custom values."""
        model = KlingO3StandardEditModel()
        params = model.validate_parameters(
            duration="10",
            aspect_ratio="9:16",
            elements=[{"frontal_image_url": "http://example.com/char.jpg"}],
            image_urls=["http://example.com/style.jpg"]
        )

        assert params["duration"] == "10"
        assert params["aspect_ratio"] == "9:16"
        assert len(params["elements"]) == 1
        assert len(params["image_urls"]) == 1

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = KlingO3StandardEditModel()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration="20")

    def test_prepare_arguments(self):
        """Test API argument preparation."""
        model = KlingO3StandardEditModel()
        args = model.prepare_arguments(
            video_url="http://example.com/video.mp4",
            prompt="Change background to @Image1",
            duration="5",
            aspect_ratio="16:9",
            image_urls=["http://example.com/snow.jpg"]
        )

        assert args["prompt"] == "Change background to @Image1"
        assert args["video_url"] == "http://example.com/video.mp4"
        assert args["duration"] == 5
        assert "image_urls" in args

    def test_cost_estimation(self):
        """Test cost estimation. Pricing: $0.252/second."""
        model = KlingO3StandardEditModel()
        cost = model.estimate_cost(duration=5)
        assert cost == 0.252 * 5

    def test_get_model_info(self):
        """Test model info retrieval."""
        model = KlingO3StandardEditModel()
        info = model.get_model_info()

        assert info["price_per_second"] == 0.252
        assert info["elements_supported"] is True
        assert info["reference_syntax"] is True


class TestKlingO3ProEditModel:
    """Tests for Kling O3 Pro Video Edit model."""

    def test_model_instantiation(self):
        """Test model can be instantiated."""
        model = KlingO3ProEditModel()
        assert model.model_key == "kling_o3_pro_edit"
        assert "o3/pro/video-to-video/edit" in model.endpoint

    def test_cost_estimation(self):
        """Test cost estimation. Pricing: $0.336/second."""
        model = KlingO3ProEditModel()
        cost = model.estimate_cost(duration=10)
        assert cost == 0.336 * 10

    def test_get_model_info_professional_tier(self):
        """Test model info shows professional tier."""
        model = KlingO3ProEditModel()
        info = model.get_model_info()
        assert info["professional_tier"] is True
        assert info["price_per_second"] == 0.336


class TestKlingO3StandardV2VRefModel:
    """Tests for Kling O3 Standard V2V Reference model."""

    def test_model_instantiation(self):
        """Test model can be instantiated."""
        model = KlingO3StandardV2VRefModel()
        assert model.model_key == "kling_o3_standard_v2v_ref"
        assert "o3/standard/video-to-video/reference" in model.endpoint

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = KlingO3StandardV2VRefModel()
        params = model.validate_parameters()

        assert params["duration"] == "5"
        assert params["keep_audio"] is False

    def test_validate_parameters_with_keep_audio(self):
        """Test parameter validation with keep_audio."""
        model = KlingO3StandardV2VRefModel()
        params = model.validate_parameters(keep_audio=True)
        assert params["keep_audio"] is True

    def test_prepare_arguments_with_style_transfer(self):
        """Test API argument preparation for style transfer."""
        model = KlingO3StandardV2VRefModel()
        args = model.prepare_arguments(
            video_url="http://example.com/video.mp4",
            prompt="Apply watercolor style of @Image1",
            duration="8",
            image_urls=["http://example.com/watercolor.jpg"],
            keep_audio=True
        )

        assert "@Image1" in args["prompt"]
        assert args["video_url"] == "http://example.com/video.mp4"
        assert "image_urls" in args
        assert args["keep_audio"] is True

    def test_cost_estimation(self):
        """Test cost estimation. Pricing: $0.252/second."""
        model = KlingO3StandardV2VRefModel()
        cost = model.estimate_cost(duration=5)
        assert cost == 0.252 * 5

    def test_get_model_info(self):
        """Test model info retrieval."""
        model = KlingO3StandardV2VRefModel()
        info = model.get_model_info()

        assert info["style_transfer"] is True
        assert info["reference_syntax"] is True


class TestKlingO3ProV2VRefModel:
    """Tests for Kling O3 Pro V2V Reference model."""

    def test_model_instantiation(self):
        """Test model can be instantiated."""
        model = KlingO3ProV2VRefModel()
        assert model.model_key == "kling_o3_pro_v2v_ref"
        assert "o3/pro/video-to-video/reference" in model.endpoint

    def test_cost_estimation(self):
        """Test cost estimation. Pricing: $0.336/second."""
        model = KlingO3ProV2VRefModel()
        cost = model.estimate_cost(duration=10)
        assert cost == 0.336 * 10

    def test_get_model_info_professional_tier(self):
        """Test model info shows professional tier."""
        model = KlingO3ProV2VRefModel()
        info = model.get_model_info()
        assert info["professional_tier"] is True
        assert info["style_transfer"] is True


class TestElementsParameter:
    """Tests for elements parameter handling across V2V models."""

    def test_elements_must_be_list(self):
        """Test that elements must be a list."""
        model = KlingO3StandardEditModel()
        with pytest.raises(ValueError, match="elements must be a list"):
            model.validate_parameters(elements="not a list")

    def test_empty_elements_allowed(self):
        """Test that empty elements list is allowed."""
        model = KlingO3ProEditModel()
        params = model.validate_parameters(elements=[])
        assert params["elements"] == []

    def test_elements_for_character_replacement(self):
        """Test elements for character/object replacement."""
        model = KlingO3ProEditModel()
        params = model.validate_parameters(
            elements=[{
                "frontal_image_url": "http://example.com/new_character.jpg"
            }]
        )
        assert len(params["elements"]) == 1


class TestReferenceSyntaxInPrompts:
    """Tests for @ reference syntax in prompts."""

    def test_element_reference_in_prompt(self):
        """Test @Element reference in prompt."""
        model = KlingO3ProEditModel()
        args = model.prepare_arguments(
            video_url="http://example.com/video.mp4",
            prompt="Replace person with @Element1",
            elements=[{"frontal_image_url": "http://example.com/char.jpg"}]
        )
        assert "@Element1" in args["prompt"]
        assert "elements" in args

    def test_image_reference_in_prompt(self):
        """Test @Image reference in prompt."""
        model = KlingO3StandardV2VRefModel()
        args = model.prepare_arguments(
            video_url="http://example.com/video.mp4",
            prompt="Change environment to match @Image1",
            image_urls=["http://example.com/environment.jpg"]
        )
        assert "@Image1" in args["prompt"]
        assert "image_urls" in args

    def test_multiple_references_in_prompt(self):
        """Test multiple references in prompt."""
        model = KlingO3ProV2VRefModel()
        args = model.prepare_arguments(
            video_url="http://example.com/video.mp4",
            prompt="Integrate @Element1 in the scene. Style should follow @Image1 and @Image2",
            elements=[{"frontal_image_url": "http://example.com/char.jpg"}],
            image_urls=[
                "http://example.com/style1.jpg",
                "http://example.com/style2.jpg"
            ]
        )
        assert "@Element1" in args["prompt"]
        assert "@Image1" in args["prompt"]
        assert "@Image2" in args["prompt"]


class TestDurationValidation:
    """Tests for duration parameter validation across V2V models."""

    def test_valid_durations_edit(self):
        """Test valid duration values for edit models."""
        model = KlingO3StandardEditModel()
        valid_durations = ["3", "5", "10", "15"]

        for duration in valid_durations:
            params = model.validate_parameters(duration=duration)
            assert params["duration"] == duration

    def test_valid_durations_ref(self):
        """Test valid duration values for reference models."""
        model = KlingO3ProV2VRefModel()
        valid_durations = ["3", "5", "10", "15"]

        for duration in valid_durations:
            params = model.validate_parameters(duration=duration)
            assert params["duration"] == duration

    def test_integer_duration_conversion(self):
        """Test integer duration is converted to string."""
        model = KlingO3StandardEditModel()
        params = model.validate_parameters(duration=10)
        assert params["duration"] == "10"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
