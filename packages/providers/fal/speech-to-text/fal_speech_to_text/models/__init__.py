"""FAL Speech-to-Text model exports."""

from .base import BaseSpeechToTextModel, TranscriptionResult, WordTimestamp, AudioEvent
from .scribe_v2 import ScribeV2Model

__all__ = [
    "BaseSpeechToTextModel",
    "TranscriptionResult",
    "WordTimestamp",
    "AudioEvent",
    "ScribeV2Model",
]
