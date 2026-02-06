"""
Unit tests for Kling O3 Text-to-Video model.

Tests:
- Model instantiation
- Parameter validation
- Cost estimation
- API argument preparation
"""

import pytest
from fal_text_to_video.models.kling_o3 import KlingO3ProT2VModel


class TestKlingO3ProT2VModel:
    """Tests for Kling O3 Pro Text-to-Video model."""

    def test_model_instantiation(self):
        """Test model can be instantiated."""
        model = KlingO3ProT2VModel()
        assert model.model_key == "kling_o3_pro_t2v"
        assert "o3/pro/text-to-video" in model.endpoint

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = KlingO3ProT2VModel()
        params = model.validate_parameters()

        assert params["duration"] == "5"
        assert params["generate_audio"] is True
        assert params["aspect_ratio"] == "16:9"
        assert params["elements"] == []
        assert params["image_urls"] == []

    def test_validate_parameters_custom(self):
        """Test parameter validation with custom values."""
        model = KlingO3ProT2VModel()
        params = model.validate_parameters(
            duration="10",
            generate_audio=False,
            aspect_ratio="9:16",
            elements=[{"frontal_image_url": "http://example.com/img.jpg"}],
            image_urls=["http://example.com/ref.jpg"],
            cfg_scale=0.7
        )

        assert params["duration"] == "10"
        assert params["generate_audio"] is False
        assert params["aspect_ratio"] == "9:16"
        assert len(params["elements"]) == 1
        assert len(params["image_urls"]) == 1
        assert params["cfg_scale"] == 0.7

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = KlingO3ProT2VModel()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration="20")

    def test_validate_parameters_invalid_aspect_ratio(self):
        """Test validation fails for invalid aspect ratio."""
        model = KlingO3ProT2VModel()
        with pytest.raises(ValueError, match="Invalid aspect_ratio"):
            model.validate_parameters(aspect_ratio="4:3")

    def test_validate_parameters_invalid_cfg_scale(self):
        """Test validation fails for invalid cfg_scale."""
        model = KlingO3ProT2VModel()
        with pytest.raises(ValueError, match="cfg_scale must be between"):
            model.validate_parameters(cfg_scale=1.5)

    def test_validate_parameters_elements_must_be_list(self):
        """Test that elements must be a list."""
        model = KlingO3ProT2VModel()
        with pytest.raises(ValueError, match="elements must be a list"):
            model.validate_parameters(elements="not a list")

    def test_prepare_arguments(self):
        """Test API argument preparation."""
        model = KlingO3ProT2VModel()
        args = model.prepare_arguments(
            prompt="Test prompt with @Element1 character",
            duration="5",
            generate_audio=True,
            aspect_ratio="16:9",
            cfg_scale=0.5,
            elements=[{"frontal_image_url": "http://example.com/char.jpg"}],
            image_urls=["http://example.com/style.jpg"]
        )

        assert args["prompt"] == "Test prompt with @Element1 character"
        assert args["duration"] == 5
        assert args["generate_audio"] is True
        assert args["aspect_ratio"] == "16:9"
        assert args["cfg_scale"] == 0.5
        assert "elements" in args
        assert "image_urls" in args

    def test_prepare_arguments_with_multi_prompt(self):
        """Test API argument preparation with multi-prompt."""
        model = KlingO3ProT2VModel()
        args = model.prepare_arguments(
            prompt="Main prompt",
            duration="10",
            multi_prompt=[
                {"timestamp": 0, "prompt": "Start scene"},
                {"timestamp": 5, "prompt": "End scene"}
            ]
        )

        assert "multi_prompt" in args
        assert len(args["multi_prompt"]) == 2

    def test_prepare_arguments_with_shot_type(self):
        """Test API argument preparation with shot type."""
        model = KlingO3ProT2VModel()
        args = model.prepare_arguments(
            prompt="Cinematic scene",
            duration="5",
            shot_type="close_up"
        )

        assert args["shot_type"] == "close_up"

    def test_cost_estimation_no_audio(self):
        """Test cost estimation without audio."""
        model = KlingO3ProT2VModel()
        cost = model.estimate_cost(duration="5", generate_audio=False)
        assert cost == 0.224 * 5  # $0.224/s

    def test_cost_estimation_with_audio(self):
        """Test cost estimation with audio."""
        model = KlingO3ProT2VModel()
        cost = model.estimate_cost(duration="10", generate_audio=True)
        assert cost == 0.28 * 10  # $0.28/s

    def test_get_model_info(self):
        """Test model info retrieval."""
        model = KlingO3ProT2VModel()
        info = model.get_model_info()

        assert info["endpoint"] == model.endpoint
        assert info["professional_tier"] is True
        assert info["audio_supported"] is True
        assert info["elements_supported"] is True
        assert info["reference_syntax"] is True


class TestElementsAndReferencesSyntax:
    """Tests for elements parameter and @ reference syntax."""

    def test_elements_with_frontal_image(self):
        """Test elements with frontal_image_url."""
        model = KlingO3ProT2VModel()
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

    def test_multiple_elements(self):
        """Test multiple elements for multi-character scenes."""
        model = KlingO3ProT2VModel()
        params = model.validate_parameters(
            elements=[
                {"frontal_image_url": "http://example.com/char1.jpg"},
                {"frontal_image_url": "http://example.com/char2.jpg"},
                {"frontal_image_url": "http://example.com/char3.jpg"}
            ]
        )
        assert len(params["elements"]) == 3

    def test_prompt_with_reference_syntax(self):
        """Test prompt containing @ reference syntax."""
        model = KlingO3ProT2VModel()
        prompt = "@Element1 and @Element2 talk to each other. Style follows @Image1."
        args = model.prepare_arguments(
            prompt=prompt,
            duration="10",
            elements=[
                {"frontal_image_url": "http://example.com/char1.jpg"},
                {"frontal_image_url": "http://example.com/char2.jpg"}
            ],
            image_urls=["http://example.com/style.jpg"]
        )

        assert "@Element1" in args["prompt"]
        assert "@Element2" in args["prompt"]
        assert "@Image1" in args["prompt"]


class TestDurationValidation:
    """Tests for duration parameter validation."""

    def test_valid_durations(self):
        """Test all valid duration values."""
        model = KlingO3ProT2VModel()
        valid_durations = ["3", "5", "10", "15"]

        for duration in valid_durations:
            params = model.validate_parameters(duration=duration)
            assert params["duration"] == duration

    def test_integer_duration(self):
        """Test integer duration is converted to string."""
        model = KlingO3ProT2VModel()
        params = model.validate_parameters(duration=10)
        assert params["duration"] == "10"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
