"""
Unit tests for extended video parameters.
"""

import pytest
from pathlib import Path
import sys

# Add package to path
_package_path = Path(__file__).parent.parent / "fal_image_to_video"
sys.path.insert(0, str(_package_path.parent))

from fal_image_to_video.models.kling import KlingModel, Kling26ProModel
from fal_image_to_video.config.constants import MODEL_EXTENDED_FEATURES
from fal_image_to_video.utils.file_utils import (
    is_url,
    validate_file_format,
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_AUDIO_FORMATS,
    SUPPORTED_VIDEO_FORMATS
)


class TestFileUtilities:
    """Tests for file utility functions."""

    def test_is_url_with_http(self):
        """HTTP URLs should be recognized."""
        assert is_url("http://example.com/image.jpg") is True

    def test_is_url_with_https(self):
        """HTTPS URLs should be recognized."""
        assert is_url("https://example.com/image.jpg") is True

    def test_is_url_with_local_path(self):
        """Local paths should not be URLs."""
        assert is_url("/path/to/file.jpg") is False
        assert is_url("C:\\path\\to\\file.jpg") is False

    def test_is_url_with_relative_path(self):
        """Relative paths should not be URLs."""
        assert is_url("images/test.png") is False
        assert is_url("./test.png") is False

    def test_validate_image_format_valid(self):
        """Valid image formats should pass."""
        for fmt in SUPPORTED_IMAGE_FORMATS:
            validate_file_format(f"test{fmt}", SUPPORTED_IMAGE_FORMATS, "image")

    def test_validate_image_format_invalid(self):
        """Invalid image formats should raise error."""
        with pytest.raises(ValueError) as exc_info:
            validate_file_format("test.xyz", SUPPORTED_IMAGE_FORMATS, "image")
        assert "Unsupported image format" in str(exc_info.value)

    def test_validate_audio_format_valid(self):
        """Valid audio formats should pass."""
        for fmt in SUPPORTED_AUDIO_FORMATS:
            validate_file_format(f"test{fmt}", SUPPORTED_AUDIO_FORMATS, "audio")

    def test_validate_audio_format_invalid(self):
        """Invalid audio formats should raise error."""
        with pytest.raises(ValueError) as exc_info:
            validate_file_format("test.xyz", SUPPORTED_AUDIO_FORMATS, "audio")
        assert "Unsupported audio format" in str(exc_info.value)

    def test_validate_video_format_valid(self):
        """Valid video formats should pass."""
        for fmt in SUPPORTED_VIDEO_FORMATS:
            validate_file_format(f"test{fmt}", SUPPORTED_VIDEO_FORMATS, "video")

    def test_validate_video_format_invalid(self):
        """Invalid video formats should raise error."""
        with pytest.raises(ValueError) as exc_info:
            validate_file_format("test.xyz", SUPPORTED_VIDEO_FORMATS, "video")
        assert "Unsupported video format" in str(exc_info.value)

    def test_validate_url_skips_validation(self):
        """URLs should skip format validation."""
        # Should not raise even with weird extension
        validate_file_format("https://example.com/file.xyz", SUPPORTED_IMAGE_FORMATS, "image")


class TestKlingEndFrame:
    """Tests for Kling end_frame support."""

    def test_kling_prepare_arguments_with_end_frame(self):
        """End frame should be included as tail_image_url."""
        model = KlingModel()
        args = model.prepare_arguments(
            prompt="Test prompt",
            image_url="http://example.com/start.jpg",
            end_frame="http://example.com/end.jpg",
            duration="5"
        )
        assert args.get("tail_image_url") == "http://example.com/end.jpg"

    def test_kling_prepare_arguments_without_end_frame(self):
        """Without end_frame, tail_image_url should not be present."""
        model = KlingModel()
        args = model.prepare_arguments(
            prompt="Test prompt",
            image_url="http://example.com/start.jpg",
            duration="5"
        )
        assert "tail_image_url" not in args

    def test_kling_pro_prepare_arguments_with_end_frame(self):
        """Kling Pro should also support end_frame."""
        model = Kling26ProModel()
        args = model.prepare_arguments(
            prompt="Test prompt",
            image_url="http://example.com/start.jpg",
            end_frame="http://example.com/end.jpg",
            duration="5"
        )
        assert args.get("tail_image_url") == "http://example.com/end.jpg"

    def test_kling_validate_with_end_frame(self):
        """Kling validation should accept and pass through end_frame."""
        model = KlingModel()
        params = model.validate_parameters(
            duration="5",
            end_frame="http://example.com/end.jpg"
        )
        assert params["end_frame"] == "http://example.com/end.jpg"

    def test_kling_validate_without_end_frame(self):
        """Kling validation should work without end_frame."""
        model = KlingModel()
        params = model.validate_parameters(duration="5")
        assert params.get("end_frame") is None


class TestModelFeatureMatrix:
    """Tests for model feature matrix."""

    def test_all_models_have_features(self):
        """All supported models should have feature definitions."""
        expected_models = [
            "hailuo", "kling_2_1", "kling_2_6_pro",
            "seedance_1_5_pro", "sora_2", "sora_2_pro", "veo_3_1_fast"
        ]
        for model in expected_models:
            assert model in MODEL_EXTENDED_FEATURES

    def test_all_features_defined(self):
        """All models should define all expected features."""
        expected_features = [
            "start_frame", "end_frame", "ref_images",
            "audio_input", "audio_generate", "ref_video"
        ]
        for model, features in MODEL_EXTENDED_FEATURES.items():
            for feature in expected_features:
                assert feature in features, f"{model} missing {feature}"

    def test_kling_supports_end_frame(self):
        """Kling models should support end_frame."""
        assert MODEL_EXTENDED_FEATURES["kling_2_1"]["end_frame"] is True
        assert MODEL_EXTENDED_FEATURES["kling_2_6_pro"]["end_frame"] is True

    def test_veo_supports_audio_generate(self):
        """Veo 3.1 Fast should support audio generation."""
        assert MODEL_EXTENDED_FEATURES["veo_3_1_fast"]["audio_generate"] is True

    def test_other_models_no_end_frame(self):
        """Non-Kling models should not support end_frame."""
        non_kling = ["hailuo", "seedance_1_5_pro", "sora_2", "sora_2_pro", "veo_3_1_fast"]
        for model in non_kling:
            assert MODEL_EXTENDED_FEATURES[model]["end_frame"] is False

    def test_all_models_support_start_frame(self):
        """All models should support start_frame."""
        for model, features in MODEL_EXTENDED_FEATURES.items():
            assert features["start_frame"] is True, f"{model} should support start_frame"

    def test_no_models_support_ref_video_yet(self):
        """No models should support ref_video (future feature)."""
        for model, features in MODEL_EXTENDED_FEATURES.items():
            assert features["ref_video"] is False, f"{model} ref_video should be False"


class TestSupportedFormats:
    """Tests for supported file format lists."""

    def test_image_formats_include_common_types(self):
        """Image formats should include common types."""
        assert '.jpg' in SUPPORTED_IMAGE_FORMATS
        assert '.jpeg' in SUPPORTED_IMAGE_FORMATS
        assert '.png' in SUPPORTED_IMAGE_FORMATS
        assert '.webp' in SUPPORTED_IMAGE_FORMATS

    def test_audio_formats_include_common_types(self):
        """Audio formats should include common types."""
        assert '.mp3' in SUPPORTED_AUDIO_FORMATS
        assert '.wav' in SUPPORTED_AUDIO_FORMATS

    def test_video_formats_include_common_types(self):
        """Video formats should include common types."""
        assert '.mp4' in SUPPORTED_VIDEO_FORMATS
        assert '.mov' in SUPPORTED_VIDEO_FORMATS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
