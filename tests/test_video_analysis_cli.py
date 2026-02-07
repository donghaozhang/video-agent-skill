"""Unit tests for video analysis CLI command."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core" / "ai_content_pipeline"))

from ai_content_pipeline.video_analysis import (
    MODEL_MAP,
    ANALYSIS_TYPES,
    analyze_video_command,
    list_video_models,
    get_video_tools_path,
)


class TestVideoAnalysisModels:
    """Test model configuration."""

    def test_model_map_has_required_models(self):
        """Ensure all expected models are present."""
        assert "gemini-3-pro" in MODEL_MAP
        assert "gemini-2.5-pro" in MODEL_MAP
        assert "gemini-2.5-flash" in MODEL_MAP
        assert "gemini-direct" in MODEL_MAP

    def test_model_map_structure(self):
        """Ensure model map has correct structure."""
        for key, value in MODEL_MAP.items():
            assert isinstance(value, tuple)
            assert len(value) == 2
            provider, model_id = value
            assert provider in ("fal", "gemini")
            assert isinstance(model_id, str)

    def test_analysis_types(self):
        """Ensure analysis types are defined."""
        assert "timeline" in ANALYSIS_TYPES
        assert "describe" in ANALYSIS_TYPES
        assert "transcribe" in ANALYSIS_TYPES

    def test_fal_models_have_correct_prefix(self):
        """FAL models should have google/ prefix."""
        for key, (provider, model_id) in MODEL_MAP.items():
            if provider == "fal":
                assert model_id.startswith("google/"), f"{key} should have google/ prefix"


class TestGetVideoToolsPath:
    """Test path resolution."""

    def test_get_video_tools_path_returns_path(self):
        """Ensure get_video_tools_path returns a Path object."""
        path = get_video_tools_path()
        assert isinstance(path, Path)

    def test_get_video_tools_path_points_to_video_tools(self):
        """Ensure path ends with video-tools."""
        path = get_video_tools_path()
        assert path.name == "video-tools"


class TestListVideoModels:
    """Test list_video_models function."""

    def test_list_video_models_runs(self, capsys):
        """Ensure list_video_models prints output."""
        list_video_models()
        captured = capsys.readouterr()
        assert "Video Analysis Models" in captured.out
        assert "gemini-3-pro" in captured.out

    def test_list_video_models_shows_analysis_types(self, capsys):
        """Ensure analysis types are shown."""
        list_video_models()
        captured = capsys.readouterr()
        assert "Analysis Types" in captured.out
        assert "timeline" in captured.out
        assert "describe" in captured.out
        assert "transcribe" in captured.out

    def test_list_video_models_shows_usage_examples(self, capsys):
        """Ensure usage examples are shown."""
        list_video_models()
        captured = capsys.readouterr()
        assert "Usage Examples" in captured.out
        assert "aicp analyze-video" in captured.out


class TestAnalyzeVideoCommand:
    """Test analyze_video_command function."""

    def test_missing_input_file(self, capsys, monkeypatch):
        """Test error handling for missing input."""
        monkeypatch.setenv("FAL_KEY", "test-key")
        args = MagicMock()
        args.input = "/nonexistent/video.mp4"
        args.model = "gemini-3-pro"
        args.type = "timeline"
        args.output = "output"
        args.debug = False

        with pytest.raises(SystemExit) as exc_info:
            analyze_video_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Input not found" in captured.out

    def test_invalid_model(self, capsys):
        """Test error handling for invalid model."""
        args = MagicMock()
        args.input = __file__  # Use this test file as input (exists)
        args.model = "invalid-model"
        args.type = "timeline"
        args.output = "output"
        args.debug = False

        with pytest.raises(SystemExit) as exc_info:
            analyze_video_command(args)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Unknown model" in captured.out

    def test_missing_fal_key(self, capsys):
        """Test error handling for missing FAL_KEY."""
        import os
        # Mock load_dotenv to do nothing, then clear FAL_KEY
        with patch('ai_content_pipeline.video_analysis.load_dotenv'):
            original = os.environ.get('FAL_KEY')
            if 'FAL_KEY' in os.environ:
                del os.environ['FAL_KEY']

            try:
                args = MagicMock()
                args.input = __file__
                args.model = "gemini-3-pro"
                args.type = "timeline"
                args.output = "output"
                args.debug = False

                with pytest.raises(SystemExit) as exc_info:
                    analyze_video_command(args)

                assert exc_info.value.code == 1
                captured = capsys.readouterr()
                assert "FAL_KEY" in captured.out
            finally:
                # Restore
                if original:
                    os.environ['FAL_KEY'] = original


class TestModelMapping:
    """Test model mapping correctness."""

    def test_gemini_3_pro_mapping(self):
        """Test gemini-3-pro maps correctly."""
        provider, model_id = MODEL_MAP["gemini-3-pro"]
        assert provider == "fal"
        assert model_id == "google/gemini-3-pro-preview"

    def test_gemini_direct_mapping(self):
        """Test gemini-direct maps to gemini provider."""
        provider, model_id = MODEL_MAP["gemini-direct"]
        assert provider == "gemini"
        assert "gemini" in model_id.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
