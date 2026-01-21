"""Tests for FAL ElevenLabs Scribe v2 speech-to-text model.

Tests cover:
- Model initialization and configuration
- Parameter validation
- Cost estimation
- Generator integration
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add paths for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "packages" / "providers" / "fal" / "speech-to-text"))


class TestScribeV2Model:
    """Unit tests for ScribeV2Model."""

    def test_model_initialization(self):
        """Test model initializes with correct endpoint."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()
        assert model.model_name == "scribe_v2"
        assert model.endpoint == "fal-ai/elevenlabs/speech-to-text/scribe-v2"

    def test_model_defaults(self):
        """Test model has correct default values."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()
        assert model.defaults["language_code"] is None  # Auto-detect
        assert model.defaults["diarize"] is True
        assert model.defaults["tag_audio_events"] is True

    def test_validate_parameters_success(self):
        """Test validation passes with valid parameters."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()
        params = model.validate_parameters(
            audio_url="https://example.com/audio.mp3"
        )

        assert params["audio_url"] == "https://example.com/audio.mp3"
        assert params["diarize"] is True
        assert params["tag_audio_events"] is True

    def test_validate_parameters_with_language(self):
        """Test validation includes language code when provided."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()
        params = model.validate_parameters(
            audio_url="https://example.com/audio.mp3",
            language_code="spa"
        )

        assert params["language_code"] == "spa"

    def test_validate_parameters_with_keyterms(self):
        """Test validation includes keyterms when provided."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()
        params = model.validate_parameters(
            audio_url="https://example.com/audio.mp3",
            keyterms=["AI", "machine learning"]
        )

        assert "keyterms" in params
        assert params["keyterms"] == ["AI", "machine learning"]

    def test_validate_parameters_missing_audio_url(self):
        """Test validation rejects missing audio_url."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()

        with pytest.raises(ValueError, match="audio_url"):
            model.validate_parameters(audio_url=None)

    def test_validate_parameters_invalid_audio_url(self):
        """Test validation rejects invalid audio_url format."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()

        with pytest.raises(ValueError, match="must be a valid URL"):
            model.validate_parameters(audio_url="not-a-url")

    def test_validate_parameters_invalid_keyterms_type(self):
        """Test validation rejects non-list keyterms."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()

        with pytest.raises(ValueError, match="keyterms must be a list"):
            model.validate_parameters(
                audio_url="https://example.com/audio.mp3",
                keyterms="single term"
            )

    def test_cost_estimation_basic(self):
        """Test basic cost estimation."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()
        cost = model.estimate_cost(duration_minutes=10)

        # $0.008/min * 10 min = $0.08
        assert abs(cost - 0.08) < 0.001

    def test_cost_estimation_with_keyterms(self):
        """Test cost estimation with keyterms surcharge."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()
        cost = model.estimate_cost(duration_minutes=10, use_keyterms=True)

        # $0.008/min * 10 min * 1.30 = $0.104
        assert abs(cost - 0.104) < 0.001

    def test_model_info(self):
        """Test model info includes required fields."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()
        info = model.get_model_info()

        assert info["name"] == "scribe_v2"
        assert info["display_name"] == "ElevenLabs Scribe v2"
        assert info["endpoint"] == "fal-ai/elevenlabs/speech-to-text/scribe-v2"
        assert info["commercial_use"] is True
        assert "word_timestamps" in info["features"]
        assert "speaker_diarization" in info["features"]


class TestScribeV2Constants:
    """Tests for speech-to-text constants configuration."""

    def test_endpoint_configured(self):
        """Test endpoint is correctly configured."""
        from fal_speech_to_text.config.constants import MODEL_ENDPOINTS

        assert "scribe_v2" in MODEL_ENDPOINTS
        assert MODEL_ENDPOINTS["scribe_v2"] == "fal-ai/elevenlabs/speech-to-text/scribe-v2"

    def test_display_name_configured(self):
        """Test display name is correctly configured."""
        from fal_speech_to_text.config.constants import MODEL_DISPLAY_NAMES

        assert "scribe_v2" in MODEL_DISPLAY_NAMES
        assert MODEL_DISPLAY_NAMES["scribe_v2"] == "ElevenLabs Scribe v2"

    def test_pricing_configured(self):
        """Test pricing is correctly configured."""
        from fal_speech_to_text.config.constants import MODEL_PRICING

        assert "scribe_v2" in MODEL_PRICING
        assert "per_minute" in MODEL_PRICING["scribe_v2"]
        assert MODEL_PRICING["scribe_v2"]["per_minute"] == 0.008
        assert "keyterms_surcharge" in MODEL_PRICING["scribe_v2"]
        assert MODEL_PRICING["scribe_v2"]["keyterms_surcharge"] == 0.30

    def test_defaults_configured(self):
        """Test defaults are correctly configured."""
        from fal_speech_to_text.config.constants import MODEL_DEFAULTS

        assert "scribe_v2" in MODEL_DEFAULTS
        assert MODEL_DEFAULTS["scribe_v2"]["diarize"] is True
        assert MODEL_DEFAULTS["scribe_v2"]["tag_audio_events"] is True

    def test_input_requirements_configured(self):
        """Test input requirements are correctly configured."""
        from fal_speech_to_text.config.constants import INPUT_REQUIREMENTS

        assert "scribe_v2" in INPUT_REQUIREMENTS
        assert "audio_url" in INPUT_REQUIREMENTS["scribe_v2"]["required"]
        assert "language_code" in INPUT_REQUIREMENTS["scribe_v2"]["optional"]
        assert "diarize" in INPUT_REQUIREMENTS["scribe_v2"]["optional"]


class TestScribeV2Transcribe:
    """Tests for transcribe method with mocked API."""

    def test_transcribe_success(self):
        """Test successful transcription."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()

        # Mock the _call_fal_api method
        with patch.object(model, '_call_fal_api') as mock_api:
            mock_api.return_value = {
                "success": True,
                "result": {
                    "text": "Hello world. This is a test.",
                    "words": [
                        {"word": "Hello", "start": 0.0, "end": 0.5, "speaker": "SPEAKER_1"},
                        {"word": "world.", "start": 0.5, "end": 1.0, "speaker": "SPEAKER_1"},
                        {"word": "This", "start": 1.2, "end": 1.4, "speaker": "SPEAKER_1"},
                        {"word": "is", "start": 1.4, "end": 1.5, "speaker": "SPEAKER_1"},
                        {"word": "a", "start": 1.5, "end": 1.6, "speaker": "SPEAKER_1"},
                        {"word": "test.", "start": 1.6, "end": 2.0, "speaker": "SPEAKER_1"},
                    ],
                    "duration": 2.0,
                    "language_code": "eng",
                },
                "processing_time": 1.5,
            }

            result = model.transcribe(audio_url="https://example.com/audio.mp3")

            assert result.success is True
            assert result.text == "Hello world. This is a test."
            assert result.duration == 2.0
            assert len(result.words) == 6
            assert result.language_detected == "eng"

    def test_transcribe_with_diarization(self):
        """Test transcription with speaker diarization."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()

        with patch.object(model, '_call_fal_api') as mock_api:
            mock_api.return_value = {
                "success": True,
                "result": {
                    "text": "Hello. Hi there.",
                    "words": [
                        {"word": "Hello.", "start": 0.0, "end": 0.5, "speaker": "SPEAKER_1"},
                        {"word": "Hi", "start": 1.0, "end": 1.3, "speaker": "SPEAKER_2"},
                        {"word": "there.", "start": 1.3, "end": 1.8, "speaker": "SPEAKER_2"},
                    ],
                    "duration": 2.0,
                },
                "processing_time": 1.2,
            }

            result = model.transcribe(
                audio_url="https://example.com/audio.mp3",
                diarize=True
            )

            assert result.success is True
            assert result.speakers is not None
            assert len(result.speakers) == 2
            assert "SPEAKER_1" in result.speakers
            assert "SPEAKER_2" in result.speakers

    def test_transcribe_api_failure(self):
        """Test handling of API failure."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()

        with patch.object(model, '_call_fal_api') as mock_api:
            mock_api.return_value = {
                "success": False,
                "error": "API rate limit exceeded",
                "processing_time": 0.5,
            }

            result = model.transcribe(audio_url="https://example.com/audio.mp3")

            assert result.success is False
            assert "rate limit" in result.error.lower()

    def test_transcribe_validation_failure(self):
        """Test handling of validation failure."""
        from fal_speech_to_text.models import ScribeV2Model

        model = ScribeV2Model()
        result = model.transcribe(audio_url=None)

        assert result.success is False
        assert "audio_url" in result.error.lower()


class TestFALSpeechToTextGeneratorIntegration:
    """Tests for generator integration."""

    def test_generator_includes_scribe_v2(self):
        """Test FALSpeechToTextGenerator includes scribe_v2 model."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        assert "scribe_v2" in generator.list_models()

    def test_generator_transcribe_method(self):
        """Test transcribe convenience method exists."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        assert hasattr(generator, 'transcribe')
        assert callable(generator.transcribe)

    def test_generator_transcribe_with_diarization_method(self):
        """Test transcribe_with_diarization convenience method exists."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        assert hasattr(generator, 'transcribe_with_diarization')
        assert callable(generator.transcribe_with_diarization)

    def test_model_recommendation_quality(self):
        """Test scribe_v2 is recommended for quality."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        recommended = generator.recommend_model("quality")
        assert recommended == "scribe_v2"

    def test_model_recommendation_diarization(self):
        """Test scribe_v2 is recommended for diarization."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        recommended = generator.recommend_model("diarization")
        assert recommended == "scribe_v2"

    def test_get_model_info(self):
        """Test getting model info through generator."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        info = generator.get_model_info("scribe_v2")

        assert info["name"] == "scribe_v2"
        assert info["commercial_use"] is True

    def test_get_input_requirements(self):
        """Test getting input requirements for scribe_v2."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        requirements = generator.get_input_requirements("scribe_v2")

        assert "audio_url" in requirements["required"]
        assert "language_code" in requirements["optional"]

    def test_list_models_by_category(self):
        """Test scribe_v2 is in transcription category."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        categories = generator.list_models_by_category()

        assert "transcription" in categories
        assert "scribe_v2" in categories["transcription"]

    def test_estimate_cost(self):
        """Test cost estimation through generator."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        cost = generator.estimate_cost("scribe_v2", duration_minutes=10)

        assert abs(cost - 0.08) < 0.001

    def test_unknown_model_error(self):
        """Test error handling for unknown model."""
        from fal_speech_to_text import FALSpeechToTextGenerator

        generator = FALSpeechToTextGenerator()
        result = generator.transcribe(
            audio_url="https://example.com/audio.mp3",
            model="unknown_model"
        )

        assert result.success is False
        assert "Unknown model" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
