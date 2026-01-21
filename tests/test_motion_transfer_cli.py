"""
Unit tests for motion transfer CLI module.

Tests cover:
- Module functions (upload, download, API)
- CLI command handler
- Error handling
- Integration with FAL Avatar Generator
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os

# Add package to path
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__),
    '..', 'packages', 'core', 'ai_content_pipeline'
))

from ai_content_pipeline.motion_transfer import (
    check_dependencies,
    upload_if_local,
    download_video,
    transfer_motion_api,
    transfer_motion,
    MotionTransferResult,
    ORIENTATION_OPTIONS,
    DEFAULTS,
)


class TestCheckDependencies:
    """Tests for dependency checking."""

    @patch.dict(os.environ, {"FAL_KEY": "test_key"})
    @patch('ai_content_pipeline.motion_transfer.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.motion_transfer.FAL_AVATAR_AVAILABLE', True)
    def test_all_dependencies_available(self):
        """Test returns success when all dependencies present."""
        ok, error = check_dependencies()
        assert ok is True
        assert error == ""

    @patch('ai_content_pipeline.motion_transfer.FAL_CLIENT_AVAILABLE', False)
    def test_missing_fal_client(self):
        """Test returns error when fal-client missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "fal-client" in error

    @patch('ai_content_pipeline.motion_transfer.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.motion_transfer.FAL_AVATAR_AVAILABLE', False)
    def test_missing_fal_avatar(self):
        """Test returns error when fal_avatar missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "fal_avatar" in error

    @patch.dict(os.environ, {}, clear=True)
    @patch('ai_content_pipeline.motion_transfer.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.motion_transfer.FAL_AVATAR_AVAILABLE', True)
    def test_missing_fal_key(self):
        """Test returns error when FAL_KEY not set."""
        # Clear the FAL_KEY if it exists
        if 'FAL_KEY' in os.environ:
            del os.environ['FAL_KEY']
        ok, error = check_dependencies()
        assert ok is False
        assert "FAL_KEY" in error


class TestUploadIfLocal:
    """Tests for upload_if_local function."""

    def test_https_url_passthrough(self):
        """Test HTTPS URLs are returned as-is."""
        url = "https://example.com/image.jpg"
        result = upload_if_local(url, "image")
        assert result == url

    def test_http_url_passthrough(self):
        """Test HTTP URLs are returned as-is."""
        url = "http://example.com/video.mp4"
        result = upload_if_local(url, "video")
        assert result == url

    def test_local_file_not_found(self):
        """Test raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="Image not found"):
            upload_if_local("/nonexistent/path.jpg", "image")

    def test_local_video_not_found(self):
        """Test raises FileNotFoundError for missing video."""
        with pytest.raises(FileNotFoundError, match="Video not found"):
            upload_if_local("/nonexistent/path.mp4", "video")

    @patch('ai_content_pipeline.motion_transfer.fal_client')
    def test_local_file_upload_success(self, mock_fal, tmp_path):
        """Test local files are uploaded to FAL."""
        # Create temp file
        test_file = tmp_path / "test.jpg"
        test_file.write_text("test content")

        mock_fal.upload_file.return_value = "https://fal.media/uploaded.jpg"

        result = upload_if_local(str(test_file), "image")

        assert result == "https://fal.media/uploaded.jpg"
        mock_fal.upload_file.assert_called_once()

    @patch('ai_content_pipeline.motion_transfer.fal_client')
    def test_local_file_upload_failure(self, mock_fal, tmp_path):
        """Test handles upload failures gracefully."""
        # Create temp file
        test_file = tmp_path / "test.jpg"
        test_file.write_text("test content")

        mock_fal.upload_file.side_effect = Exception("Network error")

        with pytest.raises(ValueError, match="Failed to upload"):
            upload_if_local(str(test_file), "image")


# Check if fal_avatar is available for API tests
try:
    from fal_avatar import FALAvatarGenerator
    FAL_AVATAR_AVAILABLE = True
except ImportError:
    FAL_AVATAR_AVAILABLE = False


class TestTransferMotionApi:
    """Tests for transfer_motion_api function."""

    @pytest.mark.skipif(not FAL_AVATAR_AVAILABLE, reason="fal_avatar not installed")
    def test_calls_generator_transfer_motion(self):
        """Test API function calls generator correctly."""
        with patch.object(FALAvatarGenerator, 'transfer_motion') as mock_transfer:
            mock_transfer.return_value = MagicMock(
                success=True,
                video_url="https://fal.media/output.mp4"
            )

            result = transfer_motion_api(
                image_url="https://example.com/image.jpg",
                video_url="https://example.com/video.mp4",
                orientation="video",
                keep_sound=True,
                prompt="Test prompt"
            )

            mock_transfer.assert_called_once_with(
                image_url="https://example.com/image.jpg",
                video_url="https://example.com/video.mp4",
                character_orientation="video",
                keep_original_sound=True,
                prompt="Test prompt",
            )

    @pytest.mark.skipif(not FAL_AVATAR_AVAILABLE, reason="fal_avatar not installed")
    def test_passes_default_values(self):
        """Test default values are passed correctly."""
        with patch.object(FALAvatarGenerator, 'transfer_motion') as mock_transfer:
            mock_transfer.return_value = MagicMock(success=True)

            transfer_motion_api(
                image_url="https://example.com/image.jpg",
                video_url="https://example.com/video.mp4"
            )

            # Check defaults
            call_kwargs = mock_transfer.call_args[1]
            assert call_kwargs["character_orientation"] == "video"
            assert call_kwargs["keep_original_sound"] is True
            assert call_kwargs["prompt"] is None


class TestTransferMotion:
    """Tests for main transfer_motion function."""

    @patch('ai_content_pipeline.motion_transfer.check_dependencies')
    def test_returns_error_if_dependencies_missing(self, mock_check):
        """Test returns error when dependencies unavailable."""
        mock_check.return_value = (False, "Missing dependency")

        result = transfer_motion("image.jpg", "video.mp4")

        assert result.success is False
        assert "Missing dependency" in result.error

    @patch('ai_content_pipeline.motion_transfer.check_dependencies')
    @patch('ai_content_pipeline.motion_transfer.upload_if_local')
    @patch('ai_content_pipeline.motion_transfer.transfer_motion_api')
    @patch('ai_content_pipeline.motion_transfer.download_video')
    def test_full_workflow_success(
        self, mock_download, mock_api, mock_upload, mock_check, tmp_path
    ):
        """Test successful full workflow."""
        mock_check.return_value = (True, "")
        mock_upload.side_effect = [
            "https://fal.media/image.jpg",
            "https://fal.media/video.mp4"
        ]
        mock_api.return_value = MagicMock(
            success=True,
            video_url="https://fal.media/output.mp4",
            duration=10,
            cost=0.60,
            processing_time=45.0,
            metadata={"orientation": "video"}
        )
        mock_download.return_value = tmp_path / "output.mp4"

        result = transfer_motion(
            "local_image.jpg",
            "local_video.mp4",
            output_dir=str(tmp_path),
            download=True
        )

        assert result.success is True
        assert result.video_url == "https://fal.media/output.mp4"
        assert result.duration == 10
        assert result.cost == 0.60

    @patch('ai_content_pipeline.motion_transfer.check_dependencies')
    @patch('ai_content_pipeline.motion_transfer.upload_if_local')
    def test_handles_file_not_found(self, mock_upload, mock_check):
        """Test handles FileNotFoundError."""
        mock_check.return_value = (True, "")
        mock_upload.side_effect = FileNotFoundError("Image not found: test.jpg")

        result = transfer_motion("test.jpg", "video.mp4")

        assert result.success is False
        assert "Image not found" in result.error

    @patch('ai_content_pipeline.motion_transfer.check_dependencies')
    @patch('ai_content_pipeline.motion_transfer.upload_if_local')
    def test_handles_upload_error(self, mock_upload, mock_check):
        """Test handles file upload errors."""
        mock_check.return_value = (True, "")
        mock_upload.side_effect = ValueError("Upload failed")

        result = transfer_motion("image.jpg", "video.mp4")

        assert result.success is False
        assert "Upload failed" in result.error

    @patch('ai_content_pipeline.motion_transfer.check_dependencies')
    @patch('ai_content_pipeline.motion_transfer.upload_if_local')
    @patch('ai_content_pipeline.motion_transfer.transfer_motion_api')
    def test_handles_api_failure(self, mock_api, mock_upload, mock_check):
        """Test handles API failure."""
        mock_check.return_value = (True, "")
        mock_upload.side_effect = ["https://url1", "https://url2"]
        mock_api.return_value = MagicMock(
            success=False,
            error="API rate limit exceeded",
            processing_time=1.0
        )

        result = transfer_motion("image.jpg", "video.mp4")

        assert result.success is False
        assert "rate limit" in result.error.lower()

    @patch('ai_content_pipeline.motion_transfer.check_dependencies')
    @patch('ai_content_pipeline.motion_transfer.upload_if_local')
    @patch('ai_content_pipeline.motion_transfer.transfer_motion_api')
    def test_skip_download_when_disabled(self, mock_api, mock_upload, mock_check):
        """Test skips download when download=False."""
        mock_check.return_value = (True, "")
        mock_upload.side_effect = ["https://url1", "https://url2"]
        mock_api.return_value = MagicMock(
            success=True,
            video_url="https://fal.media/output.mp4",
            duration=10,
            cost=0.60,
            processing_time=45.0,
            metadata={}
        )

        result = transfer_motion(
            "image.jpg",
            "video.mp4",
            download=False
        )

        assert result.success is True
        assert result.local_path is None
        assert result.video_url == "https://fal.media/output.mp4"


class TestOrientationOptions:
    """Tests for orientation configuration."""

    def test_video_orientation_max_duration(self):
        """Test video orientation has 30s max."""
        assert ORIENTATION_OPTIONS["video"]["max_duration"] == 30

    def test_image_orientation_max_duration(self):
        """Test image orientation has 10s max."""
        assert ORIENTATION_OPTIONS["image"]["max_duration"] == 10

    def test_both_orientations_have_descriptions(self):
        """Test both orientations have descriptions."""
        for key in ["video", "image"]:
            assert "description" in ORIENTATION_OPTIONS[key]
            assert len(ORIENTATION_OPTIONS[key]["description"]) > 0


class TestDefaults:
    """Tests for default values."""

    def test_default_orientation(self):
        """Test default orientation is video."""
        assert DEFAULTS["orientation"] == "video"

    def test_default_keep_sound(self):
        """Test default keep_sound is True."""
        assert DEFAULTS["keep_sound"] is True

    def test_default_output_dir(self):
        """Test default output_dir is output."""
        assert DEFAULTS["output_dir"] == "output"


class TestMotionTransferResult:
    """Tests for MotionTransferResult dataclass."""

    def test_success_result(self):
        """Test creating success result."""
        result = MotionTransferResult(
            success=True,
            video_url="https://example.com/video.mp4",
            duration=10,
            cost=0.60
        )
        assert result.success is True
        assert result.error is None
        assert result.video_url == "https://example.com/video.mp4"

    def test_failure_result(self):
        """Test creating failure result."""
        result = MotionTransferResult(
            success=False,
            error="Something went wrong"
        )
        assert result.success is False
        assert result.video_url is None
        assert result.error == "Something went wrong"

    def test_result_with_all_fields(self):
        """Test result with all fields populated."""
        result = MotionTransferResult(
            success=True,
            video_url="https://example.com/video.mp4",
            local_path="/path/to/video.mp4",
            duration=10.5,
            cost=0.63,
            processing_time=45.2,
            metadata={"orientation": "video"}
        )
        assert result.success is True
        assert result.local_path == "/path/to/video.mp4"
        assert result.duration == 10.5
        assert result.cost == 0.63
        assert result.processing_time == 45.2
        assert result.metadata["orientation"] == "video"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
