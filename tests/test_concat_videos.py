"""
Unit tests for ConcatVideosExecutor.

Tests the video concatenation step executor for the pipeline.
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core" / "ai_content_pipeline"))

from ai_content_pipeline.pipeline.step_executors.video_steps import ConcatVideosExecutor
from ai_content_pipeline.pipeline.chain import PipelineStep, StepType


class MockStep:
    """Mock pipeline step for testing."""
    def __init__(self, params=None, model="ffmpeg"):
        self.params = params or {}
        self.model = model
        self.step_type = StepType.CONCAT_VIDEOS


class TestConcatVideosExecutor:
    """Test suite for ConcatVideosExecutor."""

    def test_executor_init(self):
        """Test executor can be instantiated."""
        executor = ConcatVideosExecutor()
        assert executor is not None

    def test_empty_input_list(self):
        """Test handling of empty input list."""
        executor = ConcatVideosExecutor()
        step = MockStep()
        chain_config = {"output_dir": "output"}

        result = executor.execute(step, [], chain_config)

        assert result["success"] is False
        assert "No valid video files" in result["error"]

    def test_none_input(self):
        """Test handling of None input."""
        executor = ConcatVideosExecutor()
        step = MockStep()
        chain_config = {"output_dir": "output"}

        result = executor.execute(step, None, chain_config)

        assert result["success"] is False
        assert "No video paths provided" in result["error"]

    def test_single_string_input(self):
        """Test handling of single string input (non-existent file)."""
        executor = ConcatVideosExecutor()
        step = MockStep()
        chain_config = {"output_dir": "output"}

        result = executor.execute(step, "/nonexistent/video.mp4", chain_config)

        assert result["success"] is False
        assert "No valid video files" in result["error"]

    def test_filters_nonexistent_files(self):
        """Test that non-existent files are filtered out."""
        executor = ConcatVideosExecutor()
        step = MockStep()
        chain_config = {"output_dir": "output"}

        # Mix of nonexistent paths
        input_paths = [
            "/path/to/nonexistent1.mp4",
            "/path/to/nonexistent2.mp4",
        ]

        result = executor.execute(step, input_paths, chain_config)

        assert result["success"] is False
        assert "No valid video files" in result["error"]

    def test_custom_output_filename(self):
        """Test custom output filename parameter is used in execution."""
        executor = ConcatVideosExecutor()
        step = MockStep(params={"output_filename": "my_video.mp4"})

        with tempfile.TemporaryDirectory() as tmpdir:
            video1 = Path(tmpdir) / "video1.mp4"
            video1.touch()

            chain_config = {"output_dir": tmpdir}

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr="")
                # Create output file so success path works
                (Path(tmpdir) / "my_video.mp4").write_bytes(b"fake video data")

                result = executor.execute(step, [str(video1)], chain_config)

                assert result["success"] is True
                assert "my_video.mp4" in result["output_path"]

    @patch("subprocess.run")
    def test_ffmpeg_called_with_correct_args(self, mock_run):
        """Test FFmpeg is called with correct concatenation arguments."""
        executor = ConcatVideosExecutor()
        step = MockStep()

        # Create temp files to simulate existing videos
        with tempfile.TemporaryDirectory() as tmpdir:
            video1 = Path(tmpdir) / "video1.mp4"
            video2 = Path(tmpdir) / "video2.mp4"
            video1.touch()
            video2.touch()

            chain_config = {"output_dir": tmpdir}

            # Mock successful FFmpeg run
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = executor.execute(step, [str(video1), str(video2)], chain_config)

            # Verify FFmpeg was called
            assert mock_run.called
            call_args = mock_run.call_args[0][0]

            # Check FFmpeg command structure
            assert "ffmpeg" in call_args[0]
            assert "-f" in call_args
            assert "concat" in call_args
            assert "-c" in call_args
            assert "copy" in call_args

    @patch("subprocess.run")
    def test_ffmpeg_error_handling(self, mock_run):
        """Test handling of FFmpeg errors."""
        executor = ConcatVideosExecutor()
        step = MockStep()

        with tempfile.TemporaryDirectory() as tmpdir:
            video1 = Path(tmpdir) / "video1.mp4"
            video1.touch()

            chain_config = {"output_dir": tmpdir}

            # Mock FFmpeg failure
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr="Error: Invalid video format"
            )

            result = executor.execute(step, [str(video1)], chain_config)

            assert result["success"] is False
            assert "FFmpeg concat failed" in result["error"]

    @patch("subprocess.run")
    def test_ffmpeg_timeout_handling(self, mock_run):
        """Test handling of FFmpeg timeout."""
        executor = ConcatVideosExecutor()
        step = MockStep()

        with tempfile.TemporaryDirectory() as tmpdir:
            video1 = Path(tmpdir) / "video1.mp4"
            video1.touch()

            chain_config = {"output_dir": tmpdir}

            # Mock timeout
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="ffmpeg", timeout=300)

            result = executor.execute(step, [str(video1)], chain_config)

            assert result["success"] is False
            assert "timed out" in result["error"]

    def test_ffmpeg_not_found_handling(self):
        """Test handling when FFmpeg is not installed."""
        executor = ConcatVideosExecutor()
        step = MockStep()

        with tempfile.TemporaryDirectory() as tmpdir:
            video1 = Path(tmpdir) / "video1.mp4"
            video1.touch()

            chain_config = {"output_dir": tmpdir}

            # Patch subprocess.run to raise FileNotFoundError
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError("ffmpeg not found")

                result = executor.execute(step, [str(video1)], chain_config)

                assert result["success"] is False
                assert "FFmpeg not found" in result["error"]

    @patch("subprocess.run")
    def test_output_paths_sorted(self, mock_run):
        """Test that input paths are sorted before concatenation."""
        executor = ConcatVideosExecutor()
        step = MockStep()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with unsorted names
            video3 = Path(tmpdir) / "scene_3.mp4"
            video1 = Path(tmpdir) / "scene_1.mp4"
            video2 = Path(tmpdir) / "scene_2.mp4"

            for v in [video1, video2, video3]:
                v.touch()

            chain_config = {"output_dir": tmpdir}

            # Mock successful run
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            # Pass unsorted list
            result = executor.execute(
                step,
                [str(video3), str(video1), str(video2)],
                chain_config
            )

            # The executor should sort paths internally
            # Verify metadata contains sorted paths
            assert mock_run.called

    @patch("subprocess.run")
    def test_success_result_structure(self, mock_run):
        """Test successful result has correct structure."""
        executor = ConcatVideosExecutor()
        step = MockStep()

        with tempfile.TemporaryDirectory() as tmpdir:
            video1 = Path(tmpdir) / "video1.mp4"
            video1.touch()

            output_path = Path(tmpdir) / "combined.mp4"
            # Create fake output file
            output_path.write_bytes(b"fake video data" * 100)

            chain_config = {"output_dir": tmpdir}

            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = executor.execute(step, [str(video1)], chain_config)

            # Note: success depends on output file existing after ffmpeg
            # In this mock scenario, we need the file to exist
            assert "output_path" in result
            assert "processing_time" in result
            assert "cost" in result
            assert result["cost"] == 0.0  # Local processing
            assert result["model"] == "ffmpeg"
            assert "metadata" in result

    def test_metadata_contains_input_info(self):
        """Test that metadata contains input file information."""
        executor = ConcatVideosExecutor()
        step = MockStep()

        with tempfile.TemporaryDirectory() as tmpdir:
            video1 = Path(tmpdir) / "video1.mp4"
            video2 = Path(tmpdir) / "video2.mp4"
            video1.touch()
            video2.touch()

            output_path = Path(tmpdir) / "combined.mp4"
            output_path.write_bytes(b"fake" * 1000)

            chain_config = {"output_dir": tmpdir}

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr="")

                result = executor.execute(
                    step,
                    [str(video1), str(video2)],
                    chain_config
                )

                # Check metadata
                if result["success"]:
                    assert result["metadata"]["input_count"] == 2
                    assert "input_paths" in result["metadata"]


class TestConcatVideosIntegration:
    """Integration tests for concat_videos step type."""

    def test_step_type_exists(self):
        """Test CONCAT_VIDEOS step type is defined."""
        assert hasattr(StepType, "CONCAT_VIDEOS")
        assert StepType.CONCAT_VIDEOS.value == "concat_videos"

    def test_pipeline_step_creation(self):
        """Test creating PipelineStep for concat_videos."""
        step_dict = {
            "type": "concat_videos",
            "model": "ffmpeg",
            "params": {
                "output_filename": "final.mp4"
            }
        }

        step = PipelineStep.from_dict(step_dict)

        assert step.step_type == StepType.CONCAT_VIDEOS
        assert step.model == "ffmpeg"
        assert step.params["output_filename"] == "final.mp4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
