"""
Unit tests for Kling v3 Text-to-Video models.

Tests cover:
- Model instantiation
- Parameter validation
- API argument preparation
- Cost estimation with audio tiers
"""

import pytest
from fal_text_to_video.models import KlingV3StandardModel, KlingV3ProModel


class TestKlingV3StandardModel:
    """Tests for Kling v3 Standard text-to-video model."""

    def test_model_init(self):
        """Test model instantiation."""
        model = KlingV3StandardModel()
        assert model.model_key == "kling_3_standard"
        assert "kling-video/v3/standard" in model.endpoint

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid inputs."""
        model = KlingV3StandardModel()
        params = model.validate_parameters(
            duration="10",
            aspect_ratio="16:9",
            negative_prompt="blur",
            cfg_scale=0.7,
            generate_audio=True
        )
        assert params["duration"] == "10"
        assert params["aspect_ratio"] == "16:9"
        assert params["negative_prompt"] == "blur"
        assert params["cfg_scale"] == 0.7
        assert params["generate_audio"] is True

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = KlingV3StandardModel()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration="99")

    def test_validate_parameters_invalid_aspect_ratio(self):
        """Test validation fails for invalid aspect ratio."""
        model = KlingV3StandardModel()
        with pytest.raises(ValueError, match="Invalid aspect_ratio"):
            model.validate_parameters(aspect_ratio="4:3")

    def test_validate_parameters_invalid_cfg_scale(self):
        """Test validation fails for invalid cfg_scale."""
        model = KlingV3StandardModel()
        with pytest.raises(ValueError, match="cfg_scale must be between"):
            model.validate_parameters(cfg_scale=-0.1)

    def test_prepare_arguments(self):
        """Test API argument preparation."""
        model = KlingV3StandardModel()
        args = model.prepare_arguments(
            prompt="A cat walking in a garden",
            duration="5",
            aspect_ratio="16:9",
            generate_audio=True,
            voice_ids=["voice1"]
        )
        assert args["prompt"] == "A cat walking in a garden"
        assert args["duration"] == 5
        assert args["aspect_ratio"] == "16:9"
        assert args["generate_audio"] is True
        assert args["voice_ids"] == ["voice1"]

    def test_prepare_arguments_with_multi_prompt(self):
        """Test API argument preparation with multi-prompt."""
        model = KlingV3StandardModel()
        multi_prompt = [{"prompt": "Scene 1"}, {"prompt": "Scene 2"}]
        args = model.prepare_arguments(
            prompt="Main prompt",
            multi_prompt=multi_prompt
        )
        assert args["multi_prompt"] == multi_prompt

    def test_prepare_arguments_with_shot_type(self):
        """Test API argument preparation with shot type."""
        model = KlingV3StandardModel()
        args = model.prepare_arguments(
            prompt="Action scene",
            shot_type="wide"
        )
        assert args["shot_type"] == "wide"

    def test_cost_estimation_no_audio(self):
        """Test cost calculation without audio."""
        model = KlingV3StandardModel()
        cost = model.estimate_cost(duration="5", generate_audio=False)
        assert cost == pytest.approx(0.168 * 5)  # $0.168/s

    def test_cost_estimation_with_audio(self):
        """Test cost calculation with audio."""
        model = KlingV3StandardModel()
        cost = model.estimate_cost(duration="5", generate_audio=True)
        assert cost == pytest.approx(0.252 * 5)  # $0.252/s

    def test_cost_estimation_voice_control(self):
        """Test cost calculation with voice control."""
        model = KlingV3StandardModel()
        cost = model.estimate_cost(duration="5", generate_audio=True, voice_ids=["voice1"])
        assert cost == pytest.approx(0.308 * 5)  # $0.308/s

    def test_model_info(self):
        """Test model info retrieval."""
        model = KlingV3StandardModel()
        info = model.get_model_info()
        assert info["audio_supported"] is True
        assert info["voice_control_supported"] is True
        assert "kling-video/v3/standard" in info["endpoint"]


class TestKlingV3ProModel:
    """Tests for Kling v3 Pro text-to-video model."""

    def test_model_init(self):
        """Test model instantiation."""
        model = KlingV3ProModel()
        assert model.model_key == "kling_3_pro"
        assert "kling-video/v3/pro" in model.endpoint

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid inputs."""
        model = KlingV3ProModel()
        params = model.validate_parameters(
            duration="12",
            aspect_ratio="9:16",
            generate_audio=True
        )
        assert params["duration"] == "12"
        assert params["aspect_ratio"] == "9:16"
        assert params["generate_audio"] is True

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = KlingV3ProModel()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration="15")

    def test_prepare_arguments(self):
        """Test API argument preparation."""
        model = KlingV3ProModel()
        args = model.prepare_arguments(
            prompt="Cinematic landscape",
            duration="10",
            aspect_ratio="16:9",
            generate_audio=True
        )
        assert args["prompt"] == "Cinematic landscape"
        assert args["duration"] == 10
        assert args["aspect_ratio"] == "16:9"
        assert args["generate_audio"] is True

    def test_cost_estimation_no_audio(self):
        """Test cost calculation without audio."""
        model = KlingV3ProModel()
        cost = model.estimate_cost(duration="5", generate_audio=False)
        assert cost == pytest.approx(0.224 * 5)  # $0.224/s

    def test_cost_estimation_with_audio(self):
        """Test cost calculation with audio."""
        model = KlingV3ProModel()
        cost = model.estimate_cost(duration="5", generate_audio=True)
        assert cost == pytest.approx(0.336 * 5)  # $0.336/s

    def test_cost_estimation_voice_control(self):
        """Test cost calculation with voice control."""
        model = KlingV3ProModel()
        cost = model.estimate_cost(duration="5", generate_audio=True, voice_ids=["voice1"])
        assert cost == pytest.approx(0.392 * 5)  # $0.392/s

    def test_model_info(self):
        """Test model info retrieval."""
        model = KlingV3ProModel()
        info = model.get_model_info()
        assert info["professional_tier"] is True
        assert info["audio_supported"] is True
        assert info["voice_control_supported"] is True


class TestKlingV3Comparison:
    """Tests comparing Standard vs Pro models."""

    def test_pro_costs_more_than_standard(self):
        """Test that Pro model costs more than Standard."""
        standard = KlingV3StandardModel()
        pro = KlingV3ProModel()

        # No audio
        assert pro.estimate_cost("5", False) > standard.estimate_cost("5", False)
        # With audio
        assert pro.estimate_cost("5", True) > standard.estimate_cost("5", True)
        # With voice control
        assert pro.estimate_cost("5", True, ["v1"]) > standard.estimate_cost("5", True, ["v1"])

    def test_both_support_same_durations(self):
        """Test that both models support same duration options."""
        standard = KlingV3StandardModel()
        pro = KlingV3ProModel()

        for duration in ["5", "10", "12"]:
            standard.validate_parameters(duration=duration)
            pro.validate_parameters(duration=duration)

    def test_both_support_same_aspect_ratios(self):
        """Test that both models support same aspect ratio options."""
        standard = KlingV3StandardModel()
        pro = KlingV3ProModel()

        for ratio in ["16:9", "9:16", "1:1"]:
            standard.validate_parameters(aspect_ratio=ratio)
            pro.validate_parameters(aspect_ratio=ratio)
