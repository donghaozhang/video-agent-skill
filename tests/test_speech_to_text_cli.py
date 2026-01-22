"""
Unit tests for Speech-to-Text CLI command.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add package path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages/core/ai_content_pipeline"))

from ai_content_pipeline.speech_to_text import (
    check_dependencies,
    upload_if_local,
    transcribe,
    TranscriptionCLIResult,
    MODEL_INFO,
    DEFAULTS,
)


class TestCheckDependencies:
    """Tests for dependency checking."""

    @patch.dict('os.environ', {'FAL_KEY': 'test-key'})
    @patch('ai_content_pipeline.speech_to_text.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.speech_to_text.FAL_SPEECH_AVAILABLE', True)
    def test_all_dependencies_available(self):
        """Test returns success when all dependencies available."""
        ok, error = check_dependencies()
        assert ok is True
        assert error == ""

    @patch('ai_content_pipeline.speech_to_text.FAL_CLIENT_AVAILABLE', False)
    def test_missing_fal_client(self):
        """Test returns error when fal-client missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "fal-client" in error

    @patch('ai_content_pipeline.speech_to_text.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.speech_to_text.FAL_SPEECH_AVAILABLE', False)
    def test_missing_speech_module(self):
        """Test returns error when speech module missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "fal_speech_to_text" in error

    @patch.dict('os.environ', {}, clear=True)
    @patch('ai_content_pipeline.speech_to_text.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.speech_to_text.FAL_SPEECH_AVAILABLE', True)
    def test_missing_api_key(self):
        """Test returns error when FAL_KEY missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "FAL_KEY" in error


class TestUploadIfLocal:
    """Tests for file upload handling."""

    def test_url_passthrough_https(self):
        """Test HTTPS URLs are returned as-is."""
        url = "https://example.com/audio.mp3"
        result = upload_if_local(url)
        assert result == url

    def test_url_passthrough_http(self):
        """Test HTTP URLs are returned as-is."""
        url = "http://example.com/audio.mp3"
        result = upload_if_local(url)
        assert result == url

    def test_missing_local_file(self):
        """Test FileNotFoundError for missing local file."""
        with pytest.raises(FileNotFoundError, match="Audio not found"):
            upload_if_local("/nonexistent/audio.mp3")

    @patch('ai_content_pipeline.speech_to_text.fal_client')
    def test_local_file_upload(self, mock_fal_client, tmp_path):
        """Test local file is uploaded."""
        # Create temp file
        audio_file = tmp_path / "test.mp3"
        audio_file.write_text("fake audio")

        mock_fal_client.upload_file.return_value = "https://fal.media/uploaded.mp3"

        result = upload_if_local(str(audio_file))

        assert result == "https://fal.media/uploaded.mp3"
        mock_fal_client.upload_file.assert_called_once()


class TestTranscribe:
    """Tests for transcribe function."""

    @patch('ai_content_pipeline.speech_to_text.check_dependencies')
    def test_dependency_failure(self, mock_check):
        """Test returns error when dependencies unavailable."""
        mock_check.return_value = (False, "Missing dependency")

        result = transcribe("audio.mp3")

        assert result.success is False
        assert "Missing dependency" in result.error

    @patch('ai_content_pipeline.speech_to_text.check_dependencies')
    @patch('ai_content_pipeline.speech_to_text.upload_if_local')
    @patch('ai_content_pipeline.speech_to_text.FALSpeechToTextGenerator')
    def test_successful_transcription(self, mock_generator_class, mock_upload, mock_check, tmp_path):
        """Test successful transcription workflow."""
        mock_check.return_value = (True, "")
        mock_upload.return_value = "https://fal.media/audio.mp3"

        # Mock generator and result
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.text = "Hello world"
        mock_result.speakers = ["speaker_1"]
        mock_result.duration = 5.0
        mock_result.cost = 0.001
        mock_result.processing_time = 2.5
        mock_result.language_detected = "eng"
        mock_result.words = []
        mock_result.audio_events = []
        mock_generator.transcribe.return_value = mock_result

        result = transcribe("audio.mp3", output_dir=str(tmp_path))

        assert result.success is True
        assert result.text == "Hello world"
        assert result.speakers == ["speaker_1"]
        assert result.duration == 5.0
        assert result.txt_path is not None

    @patch('ai_content_pipeline.speech_to_text.check_dependencies')
    @patch('ai_content_pipeline.speech_to_text.upload_if_local')
    @patch('ai_content_pipeline.speech_to_text.FALSpeechToTextGenerator')
    def test_api_failure(self, mock_generator_class, mock_upload, mock_check):
        """Test handling of API failure."""
        mock_check.return_value = (True, "")
        mock_upload.return_value = "https://fal.media/audio.mp3"

        # Mock generator returning failure
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "API rate limit exceeded"
        mock_result.processing_time = 0.5
        mock_generator.transcribe.return_value = mock_result

        result = transcribe("audio.mp3")

        assert result.success is False
        assert "rate limit" in result.error.lower()

    @patch('ai_content_pipeline.speech_to_text.check_dependencies')
    def test_file_not_found(self, mock_check):
        """Test handling of missing file."""
        mock_check.return_value = (True, "")

        result = transcribe("/nonexistent/audio.mp3")

        assert result.success is False
        assert "not found" in result.error.lower()


class TestModelInfo:
    """Tests for model constants."""

    def test_scribe_v2_exists(self):
        """Test scribe_v2 model is configured."""
        assert "scribe_v2" in MODEL_INFO

    def test_scribe_v2_pricing(self):
        """Test scribe_v2 has correct pricing."""
        assert MODEL_INFO["scribe_v2"]["cost_per_minute"] == 0.008

    def test_scribe_v2_features(self):
        """Test scribe_v2 has expected features."""
        features = MODEL_INFO["scribe_v2"]["features"]
        assert any("diarization" in f.lower() for f in features)
        assert any("language" in f.lower() for f in features)

    def test_defaults_configured(self):
        """Test default values are set."""
        assert DEFAULTS["model"] == "scribe_v2"
        assert DEFAULTS["diarize"] is True
        assert DEFAULTS["output_dir"] == "output"


class TestTranscriptionCLIResult:
    """Tests for result dataclass."""

    def test_success_result(self):
        """Test successful result creation."""
        result = TranscriptionCLIResult(
            success=True,
            text="Hello world",
            txt_path="/output/transcript.txt",
            duration=5.0,
            cost=0.001,
        )
        assert result.success is True
        assert result.text == "Hello world"
        assert result.txt_path == "/output/transcript.txt"

    def test_error_result(self):
        """Test error result creation."""
        result = TranscriptionCLIResult(
            success=False,
            error="API error"
        )
        assert result.success is False
        assert result.error == "API error"
        assert result.text == ""

    def test_optional_fields(self):
        """Test optional fields default to None."""
        result = TranscriptionCLIResult(success=True)
        assert result.speakers is None
        assert result.duration is None
        assert result.cost is None
        assert result.metadata is None

    def test_raw_response_field(self):
        """Test raw_response field for word-level timestamps."""
        mock_raw_response = {
            "text": "Hello world",
            "language_code": "eng",
            "language_probability": 0.99,
            "words": [
                {"text": "Hello", "start": 0.0, "end": 0.5, "type": "word", "speaker_id": "speaker_0"},
                {"text": " ", "start": 0.5, "end": 0.6, "type": "spacing", "speaker_id": "speaker_0"},
                {"text": "world", "start": 0.6, "end": 1.0, "type": "word", "speaker_id": "speaker_0"},
            ]
        }
        result = TranscriptionCLIResult(
            success=True,
            text="Hello world",
            raw_response=mock_raw_response,
            language_probability=0.99,
        )
        assert result.raw_response is not None
        assert "words" in result.raw_response
        assert len(result.raw_response["words"]) == 3
        assert result.raw_response["words"][0]["type"] == "word"
        assert result.raw_response["words"][1]["type"] == "spacing"
        assert result.language_probability == 0.99


class TestRawJsonOutput:
    """Tests for raw JSON output with word-level timestamps."""

    @patch('ai_content_pipeline.speech_to_text.check_dependencies')
    @patch('ai_content_pipeline.speech_to_text.upload_if_local')
    @patch('ai_content_pipeline.speech_to_text.FALSpeechToTextGenerator')
    def test_raw_response_passthrough(self, mock_generator_class, mock_upload, mock_check, tmp_path):
        """Test raw API response is passed through to result."""
        mock_check.return_value = (True, "")
        mock_upload.return_value = "https://fal.media/audio.mp3"

        # Mock raw API response with word-level timestamps
        mock_raw_response = {
            "text": "Hello world",
            "language_code": "eng",
            "language_probability": 0.98,
            "words": [
                {"text": "Hello", "start": 0.0, "end": 0.5, "type": "word", "speaker_id": "speaker_0"},
                {"text": " ", "start": 0.5, "end": 0.6, "type": "spacing", "speaker_id": "speaker_0"},
                {"text": "world", "start": 0.6, "end": 1.0, "type": "word", "speaker_id": "speaker_0"},
            ]
        }

        # Mock generator and result
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.text = "Hello world"
        mock_result.speakers = ["speaker_0"]
        mock_result.duration = 1.0
        mock_result.cost = 0.001
        mock_result.processing_time = 0.5
        mock_result.language_detected = "eng"
        mock_result.language_probability = 0.98
        mock_result.words = []
        mock_result.audio_events = []
        mock_result.raw_response = mock_raw_response
        mock_generator.transcribe.return_value = mock_result

        result = transcribe("audio.mp3", output_dir=str(tmp_path))

        assert result.success is True
        assert result.raw_response is not None
        assert result.raw_response["language_probability"] == 0.98
        assert len(result.raw_response["words"]) == 3
        assert result.raw_response["words"][0]["type"] == "word"
        assert result.raw_response["words"][1]["type"] == "spacing"

    def test_word_timestamp_format(self):
        """Test word timestamp format matches expected structure."""
        word_data = {"text": "Hello", "start": 0.0, "end": 0.5, "type": "word", "speaker_id": "speaker_0"}

        assert "text" in word_data
        assert "start" in word_data
        assert "end" in word_data
        assert "type" in word_data
        assert "speaker_id" in word_data
        assert word_data["type"] in ["word", "spacing", "audio_event"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
