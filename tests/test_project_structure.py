"""
Tests for project structure utilities.

Run with: pytest tests/test_project_structure.py -v
File: tests/test_project_structure.py
"""

import os
import tempfile
import pytest
from pathlib import Path

# Import the module under test
try:
    # Check if package is installed
    from ai_content_pipeline import project_structure as _check
except ImportError:
    # Fallback: add path for running tests directly from repo root
    import sys
    fallback_path = os.path.join(os.path.dirname(__file__), '..', 'packages', 'core', 'ai_content_pipeline')
    if not os.path.isdir(fallback_path):
        raise FileNotFoundError(f"Fallback import path not found: {fallback_path}")
    sys.path.insert(0, fallback_path)

from ai_content_pipeline.project_structure import (
    init_project,
    organize_project,
    organize_output,
    cleanup_temp_files,
    get_structure_info,
    get_destination_folder,
    get_output_destination,
    get_all_directories,
    DEFAULT_STRUCTURE,
    FILE_EXTENSIONS,
    OUTPUT_STRUCTURE,
    OUTPUT_FILE_PATTERNS,
    InitResult,
    OrganizeResult,
)


class TestInitProject:
    """Tests for init_project function."""

    def test_init_creates_all_directories(self):
        """Test that init_project creates all expected directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = init_project(tmpdir)

            assert result.success is True
            assert result.directories_created > 0

            # Check key directories exist
            assert (Path(tmpdir) / "input").exists()
            assert (Path(tmpdir) / "output").exists()
            assert (Path(tmpdir) / "input" / "images").exists()
            assert (Path(tmpdir) / "input" / "videos").exists()
            assert (Path(tmpdir) / "input" / "audio").exists()
            assert (Path(tmpdir) / "input" / "pipelines").exists()
            assert (Path(tmpdir) / "input" / "pipelines" / "video").exists()

    def test_init_dry_run_does_not_create(self):
        """Test that dry_run mode doesn't create directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = init_project(tmpdir, dry_run=True)

            assert result.success is True
            assert result.directories_created > 0  # Reports what would be created

            # But directories should not actually exist
            assert not (Path(tmpdir) / "input").exists()

    def test_init_existing_directories_counted(self):
        """Test that existing directories are counted correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Pre-create some directories
            (Path(tmpdir) / "input").mkdir()
            (Path(tmpdir) / "output").mkdir()

            result = init_project(tmpdir)

            assert result.success is True
            assert result.directories_existed >= 2


class TestOrganizeProject:
    """Tests for organize_project function."""

    def test_organize_moves_images(self):
        """Test that image files are moved to input/images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create structure first
            init_project(tmpdir)

            # Create test image file in root
            test_file = Path(tmpdir) / "test_image.jpg"
            test_file.write_text("fake image data")

            result = organize_project(tmpdir)

            assert result.success is True
            assert result.files_moved == 1

            # Check file was moved
            assert not test_file.exists()
            assert (Path(tmpdir) / "input" / "images" / "test_image.jpg").exists()

    def test_organize_moves_videos(self):
        """Test that video files are moved to input/videos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            test_file = Path(tmpdir) / "test_video.mp4"
            test_file.write_text("fake video data")

            result = organize_project(tmpdir)

            assert result.files_moved == 1
            assert (Path(tmpdir) / "input" / "videos" / "test_video.mp4").exists()

    def test_organize_moves_audio(self):
        """Test that audio files are moved to input/audio."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            test_file = Path(tmpdir) / "test_audio.mp3"
            test_file.write_text("fake audio data")

            result = organize_project(tmpdir)

            assert result.files_moved == 1
            assert (Path(tmpdir) / "input" / "audio" / "test_audio.mp3").exists()

    def test_organize_moves_pipelines(self):
        """Test that YAML files are moved to input/pipelines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            test_file = Path(tmpdir) / "my_pipeline.yaml"
            test_file.write_text("pipeline: test")

            result = organize_project(tmpdir)

            assert result.files_moved == 1
            assert (Path(tmpdir) / "input" / "pipelines" / "my_pipeline.yaml").exists()

    def test_organize_skips_unknown_extensions(self):
        """Test that unknown file types are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            test_file = Path(tmpdir) / "unknown.xyz"
            test_file.write_text("unknown data")

            result = organize_project(tmpdir)

            assert result.files_moved == 0
            assert result.files_skipped == 1
            assert test_file.exists()  # File should remain in place

    def test_organize_dry_run_does_not_move(self):
        """Test that dry_run mode doesn't move files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            test_file = Path(tmpdir) / "test_image.png"
            test_file.write_text("fake image")

            result = organize_project(tmpdir, dry_run=True)

            assert result.files_moved == 1  # Reports what would be moved
            assert test_file.exists()  # But file should remain

    def test_organize_skips_files_already_in_input(self):
        """Test that files already in input/ are skipped when using recursive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            # Create file in input/images
            test_file = Path(tmpdir) / "input" / "images" / "existing.jpg"
            test_file.write_text("already organized")

            # Use recursive to find files in subdirectories
            result = organize_project(tmpdir, recursive=True)

            # File in input/images should be skipped, not moved
            assert result.files_moved == 0
            assert test_file.exists()  # File remains in place


class TestGetDestinationFolder:
    """Tests for get_destination_folder function."""

    def test_image_extensions(self):
        """Test that image extensions map to input/images."""
        for ext in [".jpg", ".png", ".gif", ".webp"]:
            file_path = Path(f"/project/test{ext}")
            assert get_destination_folder(file_path) == "input/images"

    def test_video_extensions(self):
        """Test that video extensions map to input/videos."""
        for ext in [".mp4", ".mov", ".webm"]:
            file_path = Path(f"/project/test{ext}")
            assert get_destination_folder(file_path) == "input/videos"

    def test_audio_extensions(self):
        """Test that audio extensions map to input/audio."""
        for ext in [".mp3", ".wav", ".aac"]:
            file_path = Path(f"/project/test{ext}")
            assert get_destination_folder(file_path) == "input/audio"

    def test_pipeline_extensions(self):
        """Test that YAML extensions map to input/pipelines."""
        for ext in [".yaml", ".yml"]:
            file_path = Path(f"/project/test{ext}")
            assert get_destination_folder(file_path) == "input/pipelines"

    def test_unknown_extension_returns_none(self):
        """Test that unknown extensions return None."""
        file_path = Path("/project/test.xyz")
        assert get_destination_folder(file_path) is None


class TestCleanupTempFiles:
    """Tests for cleanup_temp_files function."""

    def test_cleanup_removes_temp_files(self):
        """Test that temp files are removed from output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            # Create temp file in output
            output_dir = Path(tmpdir) / "output" / "test_pipeline"
            output_dir.mkdir(parents=True)
            temp_file = output_dir / "step_1_output.txt"
            temp_file.write_text("temp data")

            count, _deleted = cleanup_temp_files(tmpdir)

            assert count >= 1
            assert not temp_file.exists()

    def test_cleanup_dry_run_does_not_delete(self):
        """Test that dry_run mode doesn't delete files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            output_dir = Path(tmpdir) / "output"
            temp_file = output_dir / "step_1_output.txt"
            temp_file.write_text("temp data")

            count, _deleted = cleanup_temp_files(tmpdir, dry_run=True)

            assert count >= 1
            assert temp_file.exists()  # File should remain


class TestGetStructureInfo:
    """Tests for get_structure_info function."""

    def test_info_for_initialized_project(self):
        """Test structure info for an initialized project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            info = get_structure_info(tmpdir)

            assert info["has_structure"] is True
            assert info["directories"]["input"] is True
            assert info["directories"]["output"] is True

    def test_info_for_empty_directory(self):
        """Test structure info for an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            info = get_structure_info(tmpdir)

            assert info["has_structure"] is False
            assert info["directories"]["input"] is False


class TestGetAllDirectories:
    """Tests for get_all_directories function."""

    def test_returns_all_paths(self):
        """Test that all directory paths are returned."""
        directories = get_all_directories(DEFAULT_STRUCTURE)
        # Normalize paths for cross-platform comparison
        directories = [d.replace("\\", "/") for d in directories]

        assert "input" in directories
        assert "output" in directories
        assert "input/images" in directories
        assert "input/pipelines" in directories
        assert "input/pipelines/video" in directories

    def test_output_subfolders_included(self):
        """Test that output subfolders are in structure."""
        directories = get_all_directories(DEFAULT_STRUCTURE)
        # Normalize paths for cross-platform comparison
        directories = [d.replace("\\", "/") for d in directories]

        assert "output/images" in directories
        assert "output/videos" in directories
        assert "output/audio" in directories
        assert "output/transcripts" in directories


class TestGetOutputDestination:
    """Tests for get_output_destination function."""

    def test_generated_image_files(self):
        """Test that generated image files map to images folder."""
        assert get_output_destination(Path("generated_image_123.png")) == "images"
        assert get_output_destination(Path("generated_image_456.jpg")) == "images"
        assert get_output_destination(Path("upscaled_image.png")) == "images"

    def test_generated_video_files(self):
        """Test that generated video files map to videos folder."""
        assert get_output_destination(Path("generated_video_123.mp4")) == "videos"
        assert get_output_destination(Path("motion_transfer.mp4")) == "videos"
        assert get_output_destination(Path("avatar_output.webm")) == "videos"

    def test_transcript_files(self):
        """Test that transcript files map to transcripts folder."""
        assert get_output_destination(Path("video_transcript.srt")) == "transcripts"
        assert get_output_destination(Path("audio_words.json")) == "transcripts"
        assert get_output_destination(Path("speech_transcript.vtt")) == "transcripts"

    def test_audio_files(self):
        """Test that audio files map to audio folder."""
        assert get_output_destination(Path("generated_audio_123.mp3")) == "audio"
        assert get_output_destination(Path("tts_output.wav")) == "audio"

    def test_unknown_files_return_none(self):
        """Test that unknown file patterns return None."""
        assert get_output_destination(Path("random_file.xyz")) is None
        assert get_output_destination(Path("document.pdf")) is None


class TestOrganizeOutput:
    """Tests for organize_output function."""

    def test_organize_moves_generated_images(self):
        """Test that generated images are moved to output/images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            # Create generated image in output root
            output_dir = Path(tmpdir) / "output"
            test_file = output_dir / "generated_image_123.png"
            test_file.write_text("fake image")

            result = organize_output(tmpdir)

            assert result.success is True
            assert result.files_moved == 1
            assert not test_file.exists()
            assert (output_dir / "images" / "generated_image_123.png").exists()

    def test_organize_moves_generated_videos(self):
        """Test that generated videos are moved to output/videos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            output_dir = Path(tmpdir) / "output"
            test_file = output_dir / "generated_video_456.mp4"
            test_file.write_text("fake video")

            result = organize_output(tmpdir)

            assert result.files_moved == 1
            assert (output_dir / "videos" / "generated_video_456.mp4").exists()

    def test_organize_moves_transcripts(self):
        """Test that transcript files are moved to output/transcripts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            output_dir = Path(tmpdir) / "output"
            test_file = output_dir / "video_transcript.srt"
            test_file.write_text("subtitle content")

            result = organize_output(tmpdir)

            assert result.files_moved == 1
            assert (output_dir / "transcripts" / "video_transcript.srt").exists()

    def test_organize_dry_run_does_not_move(self):
        """Test that dry_run mode doesn't move files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            output_dir = Path(tmpdir) / "output"
            test_file = output_dir / "generated_image_789.png"
            test_file.write_text("fake image")

            result = organize_output(tmpdir, dry_run=True)

            assert result.files_moved == 1  # Reports what would be moved
            assert test_file.exists()  # But file should remain

    def test_organize_skips_unknown_files(self):
        """Test that unknown file types are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            output_dir = Path(tmpdir) / "output"
            test_file = output_dir / "random_document.pdf"
            test_file.write_text("pdf content")

            result = organize_output(tmpdir)

            assert result.files_moved == 0
            assert result.files_skipped == 1
            assert test_file.exists()


class TestOutputStructureConstants:
    """Tests for output structure constants."""

    def test_output_structure_has_required_folders(self):
        """Test OUTPUT_STRUCTURE has all required folders."""
        assert "images" in OUTPUT_STRUCTURE
        assert "videos" in OUTPUT_STRUCTURE
        assert "audio" in OUTPUT_STRUCTURE
        assert "transcripts" in OUTPUT_STRUCTURE
        assert "analysis" in OUTPUT_STRUCTURE
        assert "pipelines" in OUTPUT_STRUCTURE

    def test_output_file_patterns_defined(self):
        """Test OUTPUT_FILE_PATTERNS has patterns for each folder."""
        assert "images" in OUTPUT_FILE_PATTERNS
        assert "videos" in OUTPUT_FILE_PATTERNS
        assert "audio" in OUTPUT_FILE_PATTERNS
        assert "transcripts" in OUTPUT_FILE_PATTERNS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
