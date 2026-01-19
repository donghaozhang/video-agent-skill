"""
Unit tests for AI analysis commands refactoring.

Tests the command_utils module and verifies backwards compatibility
of the ai_analysis_commands module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the package to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "services" / "video-tools"))


class TestCommandUtils:
    """Tests for command_utils.py functions."""

    def test_check_and_report_gemini_status_available(self, capsys):
        """Test Gemini status check when available."""
        from video_utils.command_utils import check_and_report_gemini_status

        with patch('video_utils.command_utils.check_gemini_requirements') as mock_check:
            mock_check.return_value = (True, "Gemini API ready")
            result = check_and_report_gemini_status()

            assert result is True
            captured = capsys.readouterr()
            assert "Gemini API ready" in captured.out

    def test_check_and_report_gemini_status_not_installed(self, capsys):
        """Test Gemini status check when library not installed."""
        from video_utils.command_utils import check_and_report_gemini_status

        with patch('video_utils.command_utils.check_gemini_requirements') as mock_check:
            mock_check.return_value = (False, "Google GenerativeAI library not installed")
            result = check_and_report_gemini_status()

            assert result is False
            captured = capsys.readouterr()
            assert "not available" in captured.out
            assert "pip install" in captured.out

    def test_check_and_report_gemini_status_no_api_key(self, capsys):
        """Test Gemini status check when API key not set."""
        from video_utils.command_utils import check_and_report_gemini_status

        with patch('video_utils.command_utils.check_gemini_requirements') as mock_check:
            mock_check.return_value = (False, "GEMINI_API_KEY not set")
            result = check_and_report_gemini_status()

            assert result is False
            captured = capsys.readouterr()
            assert "not available" in captured.out
            assert "GEMINI_API_KEY" in captured.out

    def test_setup_paths_with_input_file(self, tmp_path):
        """Test path setup with a specific input file."""
        from video_utils.command_utils import setup_paths

        # Create a test video file
        test_file = tmp_path / "test.mp4"
        test_file.touch()

        result = setup_paths(
            input_path=str(test_file),
            output_path=None,
            file_finder=lambda p: [test_file],
            media_type="video",
            supported_extensions={'.mp4'}
        )

        assert result is not None
        assert len(result.files) == 1
        assert result.files[0] == test_file

    def test_setup_paths_with_input_directory(self, tmp_path):
        """Test path setup with input directory."""
        from video_utils.command_utils import setup_paths

        # Create test files
        (tmp_path / "video1.mp4").touch()
        (tmp_path / "video2.mp4").touch()

        def mock_finder(path):
            return list(path.glob("*.mp4"))

        result = setup_paths(
            input_path=str(tmp_path),
            output_path=None,
            file_finder=mock_finder,
            media_type="video",
            supported_extensions={'.mp4'}
        )

        assert result is not None
        assert len(result.files) == 2

    def test_setup_paths_nonexistent_input(self, tmp_path, capsys):
        """Test path setup with non-existent input path."""
        from video_utils.command_utils import setup_paths

        result = setup_paths(
            input_path=str(tmp_path / "nonexistent" / "path"),
            output_path=None,
            file_finder=lambda p: [],
            media_type="video",
            supported_extensions={'.mp4'}
        )

        assert result is None
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_setup_paths_unsupported_format(self, tmp_path, capsys):
        """Test path setup with unsupported file format."""
        from video_utils.command_utils import setup_paths

        test_file = tmp_path / "test.xyz"
        test_file.touch()

        result = setup_paths(
            input_path=str(test_file),
            output_path=None,
            file_finder=lambda p: [],
            media_type="video",
            supported_extensions={'.mp4'}
        )

        assert result is None
        captured = capsys.readouterr()
        assert "not a supported" in captured.out

    def test_setup_paths_no_files_found(self, tmp_path, capsys):
        """Test path setup when no files found."""
        from video_utils.command_utils import setup_paths

        result = setup_paths(
            input_path=str(tmp_path),
            output_path=None,
            file_finder=lambda p: [],
            media_type="video",
            supported_extensions={'.mp4'}
        )

        assert result is None
        captured = capsys.readouterr()
        assert "No video files found" in captured.out

    def test_setup_paths_with_output_directory(self, tmp_path):
        """Test path setup with output directory."""
        from video_utils.command_utils import setup_paths

        test_file = tmp_path / "input" / "test.mp4"
        test_file.parent.mkdir()
        test_file.touch()

        output_dir = tmp_path / "output"

        result = setup_paths(
            input_path=str(test_file),
            output_path=str(output_dir),
            file_finder=lambda p: [test_file],
            media_type="video",
            supported_extensions={'.mp4'}
        )

        assert result is not None
        assert result.output_dir == output_dir
        assert output_dir.exists()

    def test_show_result_preview_truncation(self, capsys):
        """Test result preview is properly truncated."""
        from video_utils.command_utils import show_result_preview

        result = {'description': 'A' * 300}
        show_result_preview(result, 'description', max_length=200)

        captured = capsys.readouterr()
        assert '...' in captured.out

    def test_show_result_preview_short_content(self, capsys):
        """Test result preview with short content."""
        from video_utils.command_utils import show_result_preview

        result = {'description': 'Short content'}
        show_result_preview(result, 'description', max_length=200)

        captured = capsys.readouterr()
        assert 'Short content' in captured.out
        assert '...' not in captured.out

    def test_show_result_preview_unknown_type(self, capsys):
        """Test result preview with unknown analysis type."""
        from video_utils.command_utils import show_result_preview

        result = {'description': 'Some content'}
        show_result_preview(result, 'unknown_type', max_length=200)

        captured = capsys.readouterr()
        assert captured.out == ''

    def test_print_results_summary(self, capsys, tmp_path):
        """Test results summary printing."""
        from video_utils.command_utils import print_results_summary

        output_dir = tmp_path / "output"
        print_results_summary(5, 2, output_dir)

        captured = capsys.readouterr()
        assert '5 successful' in captured.out
        assert '2 failed' in captured.out
        assert 'output' in captured.out

    def test_print_results_summary_no_output_dir(self, capsys):
        """Test results summary without output directory."""
        from video_utils.command_utils import print_results_summary

        print_results_summary(3, 0)

        captured = capsys.readouterr()
        assert '3 successful' in captured.out
        assert 'Analysis complete' in captured.out

    def test_analysis_config_defaults(self):
        """Test AnalysisConfig default values."""
        from video_utils.command_utils import AnalysisConfig

        config = AnalysisConfig(analysis_type='description')

        assert config.analysis_type == 'description'
        assert config.detailed is False
        assert config.include_timestamps is True
        assert config.speaker_identification is True
        assert config.questions is None

    def test_path_config_creation(self, tmp_path):
        """Test PathConfig creation."""
        from video_utils.command_utils import PathConfig

        files = [tmp_path / "file1.mp4", tmp_path / "file2.mp4"]

        config = PathConfig(
            input_dir=tmp_path,
            output_dir=tmp_path / "output",
            output_file=None,
            files=files
        )

        assert config.input_dir == tmp_path
        assert len(config.files) == 2


class TestVideoCommands:
    """Tests for video_commands.py functions."""

    def test_video_extensions_defined(self):
        """Test video extensions constant is defined."""
        from video_utils.ai_commands.video_commands import VIDEO_EXTENSIONS

        assert '.mp4' in VIDEO_EXTENSIONS
        assert '.avi' in VIDEO_EXTENSIONS
        assert '.mov' in VIDEO_EXTENSIONS
        assert '.mkv' in VIDEO_EXTENSIONS
        assert '.webm' in VIDEO_EXTENSIONS

    def test_video_analysis_types_defined(self):
        """Test video analysis types are defined."""
        from video_utils.ai_commands.video_commands import VIDEO_ANALYSIS_TYPES

        assert '1' in VIDEO_ANALYSIS_TYPES
        assert VIDEO_ANALYSIS_TYPES['1'][0] == 'description'
        assert VIDEO_ANALYSIS_TYPES['2'][0] == 'transcription'

    def test_cmd_analyze_videos_no_gemini(self, capsys):
        """Test analyze videos fails gracefully without Gemini."""
        from video_utils.ai_commands.video_commands import cmd_analyze_videos

        with patch('video_utils.ai_commands.video_commands.check_and_report_gemini_status') as mock:
            mock.return_value = False
            cmd_analyze_videos()

        assert mock.called


class TestAudioCommands:
    """Tests for audio_commands.py functions."""

    def test_audio_extensions_defined(self):
        """Test audio extensions constant is defined."""
        from video_utils.ai_commands.audio_commands import AUDIO_EXTENSIONS

        assert '.mp3' in AUDIO_EXTENSIONS
        assert '.wav' in AUDIO_EXTENSIONS
        assert '.m4a' in AUDIO_EXTENSIONS
        assert '.flac' in AUDIO_EXTENSIONS

    def test_audio_analysis_types_defined(self):
        """Test audio analysis types are defined."""
        from video_utils.ai_commands.audio_commands import AUDIO_ANALYSIS_TYPES

        assert '1' in AUDIO_ANALYSIS_TYPES
        assert AUDIO_ANALYSIS_TYPES['1'][0] == 'description'
        assert AUDIO_ANALYSIS_TYPES['2'][0] == 'transcription'


class TestImageCommands:
    """Tests for image_commands.py functions."""

    def test_image_extensions_defined(self):
        """Test image extensions constant is defined."""
        from video_utils.ai_commands.image_commands import IMAGE_EXTENSIONS

        assert '.jpg' in IMAGE_EXTENSIONS
        assert '.jpeg' in IMAGE_EXTENSIONS
        assert '.png' in IMAGE_EXTENSIONS
        assert '.webp' in IMAGE_EXTENSIONS
        assert '.gif' in IMAGE_EXTENSIONS

    def test_image_analysis_types_defined(self):
        """Test image analysis types are defined."""
        from video_utils.ai_commands.image_commands import IMAGE_ANALYSIS_TYPES

        assert '1' in IMAGE_ANALYSIS_TYPES
        assert IMAGE_ANALYSIS_TYPES['1'][0] == 'description'
        assert IMAGE_ANALYSIS_TYPES['4'][0] == 'text'


class TestBackwardsCompatibility:
    """Tests for backwards compatibility of imports."""

    def test_import_from_ai_analysis_commands(self):
        """Test all functions can be imported from original module."""
        from video_utils.ai_analysis_commands import (
            cmd_analyze_videos,
            cmd_transcribe_videos,
            cmd_describe_videos,
            cmd_describe_videos_with_params,
            cmd_transcribe_videos_with_params,
            cmd_analyze_audio,
            cmd_transcribe_audio,
            cmd_describe_audio,
            cmd_analyze_audio_with_params,
            cmd_analyze_images,
            cmd_describe_images,
            cmd_extract_text,
            cmd_analyze_images_with_params,
        )

        # All imports should be callable
        assert callable(cmd_analyze_videos)
        assert callable(cmd_transcribe_videos)
        assert callable(cmd_describe_videos)
        assert callable(cmd_describe_videos_with_params)
        assert callable(cmd_transcribe_videos_with_params)
        assert callable(cmd_analyze_audio)
        assert callable(cmd_transcribe_audio)
        assert callable(cmd_describe_audio)
        assert callable(cmd_analyze_audio_with_params)
        assert callable(cmd_analyze_images)
        assert callable(cmd_describe_images)
        assert callable(cmd_extract_text)
        assert callable(cmd_analyze_images_with_params)

    def test_import_from_ai_commands_package(self):
        """Test all functions can be imported from new package."""
        from video_utils.ai_commands import (
            cmd_analyze_videos,
            cmd_transcribe_videos,
            cmd_describe_videos,
            cmd_describe_videos_with_params,
            cmd_transcribe_videos_with_params,
            cmd_analyze_audio,
            cmd_transcribe_audio,
            cmd_describe_audio,
            cmd_analyze_audio_with_params,
            cmd_analyze_images,
            cmd_describe_images,
            cmd_extract_text,
            cmd_analyze_images_with_params,
        )

        assert callable(cmd_analyze_videos)
        assert callable(cmd_transcribe_videos)
        assert callable(cmd_analyze_audio)
        assert callable(cmd_analyze_images)

    def test_import_star_from_ai_analysis_commands(self):
        """Test star import from original module."""
        import video_utils.ai_analysis_commands as module

        # Check __all__ is defined
        assert hasattr(module, '__all__')
        assert 'cmd_analyze_videos' in module.__all__
        assert 'cmd_analyze_audio' in module.__all__
        assert 'cmd_analyze_images' in module.__all__

    def test_functions_are_same_objects(self):
        """Test that functions from both modules are the same objects."""
        from video_utils.ai_analysis_commands import cmd_analyze_videos as old_func
        from video_utils.ai_commands import cmd_analyze_videos as new_func

        # They should be the exact same function object
        assert old_func is new_func
