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
    from ai_content_pipeline.project_structure import (
        init_project,
        organize_project,
        cleanup_temp_files,
        get_structure_info,
        get_destination_folder,
        get_all_directories,
        DEFAULT_STRUCTURE,
        FILE_EXTENSIONS,
        InitResult,
        OrganizeResult,
    )
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'core', 'ai_content_pipeline'))
    from ai_content_pipeline.project_structure import (
        init_project,
        organize_project,
        cleanup_temp_files,
        get_structure_info,
        get_destination_folder,
        get_all_directories,
        DEFAULT_STRUCTURE,
        FILE_EXTENSIONS,
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
        root = Path("/project")
        for ext in [".jpg", ".png", ".gif", ".webp"]:
            file_path = Path(f"/project/test{ext}")
            assert get_destination_folder(file_path, root) == "input/images"

    def test_video_extensions(self):
        """Test that video extensions map to input/videos."""
        root = Path("/project")
        for ext in [".mp4", ".mov", ".webm"]:
            file_path = Path(f"/project/test{ext}")
            assert get_destination_folder(file_path, root) == "input/videos"

    def test_audio_extensions(self):
        """Test that audio extensions map to input/audio."""
        root = Path("/project")
        for ext in [".mp3", ".wav", ".aac"]:
            file_path = Path(f"/project/test{ext}")
            assert get_destination_folder(file_path, root) == "input/audio"

    def test_pipeline_extensions(self):
        """Test that YAML extensions map to input/pipelines."""
        root = Path("/project")
        for ext in [".yaml", ".yml"]:
            file_path = Path(f"/project/test{ext}")
            assert get_destination_folder(file_path, root) == "input/pipelines"

    def test_unknown_extension_returns_none(self):
        """Test that unknown extensions return None."""
        root = Path("/project")
        file_path = Path("/project/test.xyz")
        assert get_destination_folder(file_path, root) is None


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

            count, deleted = cleanup_temp_files(tmpdir)

            assert count >= 1
            assert not temp_file.exists()

    def test_cleanup_dry_run_does_not_delete(self):
        """Test that dry_run mode doesn't delete files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            init_project(tmpdir)

            output_dir = Path(tmpdir) / "output"
            temp_file = output_dir / "step_1_output.txt"
            temp_file.write_text("temp data")

            count, deleted = cleanup_temp_files(tmpdir, dry_run=True)

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

        assert "input" in directories
        assert "output" in directories
        assert "input/images" in directories
        assert "input/pipelines" in directories
        assert "input/pipelines/video" in directories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
