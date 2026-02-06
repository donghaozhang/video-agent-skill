"""
Unit tests for FAL Avatar Generator module.

Tests cover:
- Model initialization and configuration
- Parameter validation
- Cost estimation
- Generator routing
"""

import pytest
from unittest.mock import patch, MagicMock

# Import avatar module components
from fal_avatar import FALAvatarGenerator
from fal_avatar.models import (
    BaseAvatarModel,
    AvatarGenerationResult,
    OmniHumanModel,
    FabricModel,
    FabricTextModel,
    KlingRefToVideoModel,
    KlingV2VReferenceModel,
    KlingV2VEditModel,
)
from fal_avatar.config.constants import (
    MODEL_ENDPOINTS,
    MODEL_PRICING,
    MODEL_DEFAULTS,
)


class TestAvatarGenerationResult:
    """Tests for AvatarGenerationResult dataclass."""

    def test_success_result(self):
        """Test successful result creation."""
        result = AvatarGenerationResult(
            success=True,
            video_url="https://example.com/video.mp4",
            duration=5.0,
            cost=0.80,
            processing_time=60.0,
            model_used="omnihuman_v1_5",
        )
        assert result.success is True
        assert result.video_url == "https://example.com/video.mp4"
        assert result.duration == 5.0
        assert result.cost == 0.80
        assert result.error is None

    def test_failure_result(self):
        """Test failure result creation."""
        result = AvatarGenerationResult(
            success=False,
            error="API error: rate limited",
            model_used="fabric_1_0",
        )
        assert result.success is False
        assert result.error == "API error: rate limited"
        assert result.video_url is None


class TestOmniHumanModel:
    """Tests for OmniHuman v1.5 model."""

    def test_initialization(self):
        """Test model initialization."""
        model = OmniHumanModel()
        assert model.model_name == "omnihuman_v1_5"
        assert model.endpoint == MODEL_ENDPOINTS["omnihuman_v1_5"]
        assert model.pricing == MODEL_PRICING["omnihuman_v1_5"]

    def test_validate_parameters_success(self):
        """Test parameter validation with valid inputs."""
        model = OmniHumanModel()
        params = model.validate_parameters(
            image_url="https://example.com/image.jpg",
            audio_url="https://example.com/audio.mp3",
        )
        assert "image_url" in params
        assert "audio_url" in params
        assert params["resolution"] == "1080p"  # default

    def test_validate_parameters_missing_image(self):
        """Test validation fails without image URL."""
        model = OmniHumanModel()
        with pytest.raises(ValueError, match="image_url is required"):
            model.validate_parameters(
                image_url=None,
                audio_url="https://example.com/audio.mp3",
            )

    def test_validate_parameters_missing_audio(self):
        """Test validation fails without audio URL."""
        model = OmniHumanModel()
        with pytest.raises(ValueError, match="audio_url is required"):
            model.validate_parameters(
                image_url="https://example.com/image.jpg",
                audio_url=None,
            )

    def test_validate_parameters_invalid_url(self):
        """Test validation fails with invalid URL format."""
        model = OmniHumanModel()
        with pytest.raises(ValueError, match="must be a valid URL"):
            model.validate_parameters(
                image_url="not-a-url",
                audio_url="https://example.com/audio.mp3",
            )

    def test_estimate_cost(self):
        """Test cost estimation."""
        model = OmniHumanModel()
        cost = model.estimate_cost(duration=10)
        expected = 10 * MODEL_PRICING["omnihuman_v1_5"]["per_second"]
        assert cost == expected

    def test_get_model_info(self):
        """Test model info retrieval."""
        model = OmniHumanModel()
        info = model.get_model_info()
        assert info["name"] == "omnihuman_v1_5"
        assert "display_name" in info
        assert "pricing" in info
        assert "best_for" in info


class TestFabricModel:
    """Tests for VEED Fabric models."""

    def test_standard_initialization(self):
        """Test standard model initialization."""
        model = FabricModel(fast=False)
        assert model.model_name == "fabric_1_0"
        assert model.is_fast is False

    def test_fast_initialization(self):
        """Test fast model initialization."""
        model = FabricModel(fast=True)
        assert model.model_name == "fabric_1_0_fast"
        assert model.is_fast is True

    def test_validate_parameters(self):
        """Test parameter validation."""
        model = FabricModel()
        params = model.validate_parameters(
            image_url="https://example.com/image.jpg",
            audio_url="https://example.com/audio.mp3",
        )
        assert params["resolution"] == "720p"  # default

    def test_estimate_cost_480p(self):
        """Test cost estimation for 480p."""
        model = FabricModel()
        cost = model.estimate_cost(duration=10, resolution="480p")
        expected = 10 * MODEL_PRICING["fabric_1_0"]["480p"]
        assert cost == expected

    def test_estimate_cost_720p(self):
        """Test cost estimation for 720p."""
        model = FabricModel()
        cost = model.estimate_cost(duration=10, resolution="720p")
        expected = 10 * MODEL_PRICING["fabric_1_0"]["720p"]
        assert cost == expected


class TestFabricTextModel:
    """Tests for VEED Fabric Text model."""

    def test_initialization(self):
        """Test model initialization."""
        model = FabricTextModel()
        assert model.model_name == "fabric_1_0_text"
        assert model.max_text_length == 2000

    def test_validate_parameters(self):
        """Test parameter validation with text."""
        model = FabricTextModel()
        params = model.validate_parameters(
            image_url="https://example.com/image.jpg",
            text="Hello, this is a test.",
        )
        assert "text" in params
        assert params["text"] == "Hello, this is a test."

    def test_validate_parameters_missing_text(self):
        """Test validation fails without text."""
        model = FabricTextModel()
        with pytest.raises(ValueError, match="Text is required"):
            model.validate_parameters(
                image_url="https://example.com/image.jpg",
                text="",
            )

    def test_validate_parameters_text_too_long(self):
        """Test validation fails with text exceeding limit."""
        model = FabricTextModel()
        long_text = "x" * 2001
        with pytest.raises(ValueError, match="exceeds maximum length"):
            model.validate_parameters(
                image_url="https://example.com/image.jpg",
                text=long_text,
            )


class TestKlingRefToVideoModel:
    """Tests for Kling Reference-to-Video model."""

    def test_initialization(self):
        """Test model initialization."""
        model = KlingRefToVideoModel()
        assert model.model_name == "kling_ref_to_video"
        assert model.max_references == 4

    def test_validate_parameters(self):
        """Test parameter validation."""
        model = KlingRefToVideoModel()
        params = model.validate_parameters(
            prompt="A person walking",
            reference_images=["https://example.com/img1.jpg"],
        )
        assert "prompt" in params
        assert "reference_images" in params

    def test_validate_parameters_no_references(self):
        """Test validation fails without reference images."""
        model = KlingRefToVideoModel()
        with pytest.raises(ValueError, match="At least one reference image"):
            model.validate_parameters(
                prompt="A person walking",
                reference_images=[],
            )

    def test_validate_parameters_too_many_references(self):
        """Test validation fails with too many references."""
        model = KlingRefToVideoModel()
        with pytest.raises(ValueError, match="Maximum 4 reference images"):
            model.validate_parameters(
                prompt="A person walking",
                reference_images=[
                    "https://example.com/img1.jpg",
                    "https://example.com/img2.jpg",
                    "https://example.com/img3.jpg",
                    "https://example.com/img4.jpg",
                    "https://example.com/img5.jpg",
                ],
            )

    def test_estimate_cost(self):
        """Test cost estimation."""
        model = KlingRefToVideoModel()
        cost = model.estimate_cost(duration=5)
        expected = 5 * MODEL_PRICING["kling_ref_to_video"]["per_second"]
        assert cost == expected


class TestKlingV2VModels:
    """Tests for Kling Video-to-Video models."""

    def test_reference_model_initialization(self):
        """Test V2V Reference model initialization."""
        model = KlingV2VReferenceModel()
        assert model.model_name == "kling_v2v_reference"

    def test_edit_model_initialization(self):
        """Test V2V Edit model initialization."""
        model = KlingV2VEditModel()
        assert model.model_name == "kling_v2v_edit"

    def test_reference_validate_parameters(self):
        """Test V2V Reference parameter validation."""
        model = KlingV2VReferenceModel()
        params = model.validate_parameters(
            prompt="Transform style",
            video_url="https://example.com/video.mp4",
        )
        assert params["prompt"] == "Transform style"
        assert params["video_url"] == "https://example.com/video.mp4"

    def test_edit_validate_parameters(self):
        """Test V2V Edit parameter validation."""
        model = KlingV2VEditModel()
        params = model.validate_parameters(
            video_url="https://example.com/video.mp4",
            prompt="Change background to beach",
        )
        assert "video_url" in params
        assert "prompt" in params


class TestFALAvatarGenerator:
    """Tests for the unified FAL Avatar Generator."""

    def test_initialization(self):
        """Test generator initialization with all models."""
        generator = FALAvatarGenerator()
        assert len(generator.models) == 10
        assert "omnihuman_v1_5" in generator.models
        assert "fabric_1_0" in generator.models
        assert "fabric_1_0_fast" in generator.models
        assert "fabric_1_0_text" in generator.models
        assert "kling_ref_to_video" in generator.models
        assert "kling_v2v_reference" in generator.models
        assert "kling_v2v_edit" in generator.models
        assert "kling_motion_control" in generator.models
        assert "multitalk" in generator.models
        assert "grok_video_edit" in generator.models

    def test_list_models(self):
        """Test listing available models."""
        generator = FALAvatarGenerator()
        models = generator.list_models()
        assert len(models) == 10
        assert "omnihuman_v1_5" in models

    def test_list_models_by_category(self):
        """Test listing models by category."""
        generator = FALAvatarGenerator()
        categories = generator.list_models_by_category()
        assert "avatar_lipsync" in categories
        assert "reference_to_video" in categories
        assert "video_to_video" in categories

    def test_get_model_info(self):
        """Test getting model info."""
        generator = FALAvatarGenerator()
        info = generator.get_model_info("omnihuman_v1_5")
        assert info["name"] == "omnihuman_v1_5"
        assert "pricing" in info

    def test_get_model_info_unknown(self):
        """Test getting info for unknown model raises error."""
        generator = FALAvatarGenerator()
        with pytest.raises(ValueError, match="Unknown model"):
            generator.get_model_info("unknown_model")

    def test_generate_unknown_model(self):
        """Test generate with unknown model returns error result."""
        generator = FALAvatarGenerator()
        result = generator.generate(model="unknown_model")
        assert result.success is False
        assert "Unknown model" in result.error

    def test_estimate_cost(self):
        """Test cost estimation through generator."""
        generator = FALAvatarGenerator()
        cost = generator.estimate_cost("omnihuman_v1_5", duration=10)
        assert cost > 0

    def test_estimate_cost_unknown_model(self):
        """Test cost estimation for unknown model raises error."""
        generator = FALAvatarGenerator()
        with pytest.raises(ValueError, match="Unknown model"):
            generator.estimate_cost("unknown_model", duration=10)

    def test_recommend_model_quality(self):
        """Test model recommendation for quality."""
        generator = FALAvatarGenerator()
        model = generator.recommend_model("quality")
        assert model == "omnihuman_v1_5"

    def test_recommend_model_speed(self):
        """Test model recommendation for speed."""
        generator = FALAvatarGenerator()
        model = generator.recommend_model("speed")
        assert model == "fabric_1_0_fast"

    def test_recommend_model_text_to_avatar(self):
        """Test model recommendation for text-to-avatar."""
        generator = FALAvatarGenerator()
        model = generator.recommend_model("text_to_avatar")
        assert model == "fabric_1_0_text"

    def test_get_display_name(self):
        """Test getting display name."""
        generator = FALAvatarGenerator()
        name = generator.get_display_name("omnihuman_v1_5")
        assert "OmniHuman" in name

    def test_get_input_requirements(self):
        """Test getting input requirements."""
        generator = FALAvatarGenerator()
        reqs = generator.get_input_requirements("omnihuman_v1_5")
        assert "required" in reqs
        assert "optional" in reqs
        assert "image_url" in reqs["required"]
        assert "audio_url" in reqs["required"]

    def test_validate_inputs_success(self):
        """Test input validation success."""
        generator = FALAvatarGenerator()
        result = generator.validate_inputs(
            "omnihuman_v1_5",
            image_url="https://example.com/image.jpg",
            audio_url="https://example.com/audio.mp3",
        )
        assert result is True

    def test_validate_inputs_missing_required(self):
        """Test input validation fails with missing required params."""
        generator = FALAvatarGenerator()
        with pytest.raises(ValueError, match="Missing required parameters"):
            generator.validate_inputs(
                "omnihuman_v1_5",
                image_url="https://example.com/image.jpg",
            )

    def test_generate_avatar_auto_select_text(self):
        """Test generate_avatar auto-selects text model."""
        generator = FALAvatarGenerator()
        # Mock the generate method to check which model was selected
        with patch.object(generator, 'generate') as mock_generate:
            mock_generate.return_value = AvatarGenerationResult(success=True)
            generator.generate_avatar(
                image_url="https://example.com/image.jpg",
                text="Hello world",
            )
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            assert call_args[1]["model"] == "fabric_1_0_text"

    def test_generate_avatar_auto_select_audio(self):
        """Test generate_avatar auto-selects audio model."""
        generator = FALAvatarGenerator()
        with patch.object(generator, 'generate') as mock_generate:
            mock_generate.return_value = AvatarGenerationResult(success=True)
            generator.generate_avatar(
                image_url="https://example.com/image.jpg",
                audio_url="https://example.com/audio.mp3",
            )
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            assert call_args[1]["model"] == "omnihuman_v1_5"


class TestBaseModelValidation:
    """Tests for base model validation methods."""

    def test_validate_url_http(self):
        """Test URL validation accepts http URLs."""
        model = OmniHumanModel()
        url = model._validate_url("http://example.com/file.jpg", "test_param")
        assert url == "http://example.com/file.jpg"

    def test_validate_url_https(self):
        """Test URL validation accepts https URLs."""
        model = OmniHumanModel()
        url = model._validate_url("https://example.com/file.jpg", "test_param")
        assert url == "https://example.com/file.jpg"

    def test_validate_url_data_uri(self):
        """Test URL validation accepts data URIs."""
        model = OmniHumanModel()
        url = model._validate_url("data:image/png;base64,abc123", "test_param")
        assert url.startswith("data:")

    def test_validate_url_invalid(self):
        """Test URL validation rejects invalid URLs."""
        model = OmniHumanModel()
        with pytest.raises(ValueError, match="must be a valid URL"):
            model._validate_url("invalid-url", "test_param")

    def test_validate_resolution_valid(self):
        """Test resolution validation with valid value."""
        model = OmniHumanModel()
        res = model._validate_resolution("1080p")
        assert res == "1080p"

    def test_validate_resolution_invalid(self):
        """Test resolution validation rejects invalid value."""
        model = OmniHumanModel()
        with pytest.raises(ValueError, match="Unsupported resolution"):
            model._validate_resolution("4K")  # Not supported by OmniHuman

    def test_validate_aspect_ratio_valid(self):
        """Test aspect ratio validation with valid value."""
        model = KlingRefToVideoModel()
        ratio = model._validate_aspect_ratio("16:9")
        assert ratio == "16:9"

    def test_validate_aspect_ratio_invalid(self):
        """Test aspect ratio validation rejects invalid value."""
        model = KlingRefToVideoModel()
        with pytest.raises(ValueError, match="Unsupported aspect ratio"):
            model._validate_aspect_ratio("21:9")  # Not supported


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
