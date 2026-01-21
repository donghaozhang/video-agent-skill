"""FAL Speech-to-Text Package.

This package provides unified access to FAL speech-to-text models:
- ElevenLabs Scribe v2 - Fast, accurate transcription with diarization
"""

from .generator import FALSpeechToTextGenerator
from .models import (
    BaseSpeechToTextModel,
    TranscriptionResult,
    WordTimestamp,
    AudioEvent,
    ScribeV2Model,
)

__all__ = [
    "FALSpeechToTextGenerator",
    "BaseSpeechToTextModel",
    "TranscriptionResult",
    "WordTimestamp",
    "AudioEvent",
    "ScribeV2Model",
]

__version__ = "1.0.0"
