"""ElevenLabs Scribe v2 speech-to-text model implementation."""

from typing import Any, Dict, List, Optional

from .base import (
    BaseSpeechToTextModel,
    TranscriptionResult,
    WordTimestamp,
    AudioEvent,
)
from ..config.constants import (
    MODEL_ENDPOINTS,
    MODEL_DISPLAY_NAMES,
    MODEL_PRICING,
    MODEL_DEFAULTS,
    SUPPORTED_LANGUAGES,
)


class ScribeV2Model(BaseSpeechToTextModel):
    """
    ElevenLabs Scribe v2 speech-to-text model.

    Features:
    - Blazingly fast inference
    - 99 language support
    - Word-level timestamps
    - Speaker diarization
    - Audio event tagging (laughter, applause, etc.)
    """

    def __init__(self):
        """Initialize Scribe v2 model."""
        super().__init__("scribe_v2")
        self.endpoint = MODEL_ENDPOINTS["scribe_v2"]
        self.pricing = MODEL_PRICING["scribe_v2"]
        self.defaults = MODEL_DEFAULTS["scribe_v2"]

    def validate_parameters(
        self,
        audio_url: Optional[str] = None,
        language_code: Optional[str] = None,
        diarize: Optional[bool] = None,
        tag_audio_events: Optional[bool] = None,
        keyterms: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate and apply defaults to parameters.

        Args:
            audio_url: URL of audio file to transcribe
            language_code: Language code (e.g., "eng", "spa")
            diarize: Enable speaker identification
            tag_audio_events: Enable audio event tagging
            keyterms: Terms to bias transcription toward

        Returns:
            Dict of validated parameters

        Raises:
            ValueError: If required parameters missing or invalid
        """
        # Validate required parameter
        audio_url = self._validate_url(audio_url, "audio_url")

        # Validate language code if provided
        if language_code is not None and language_code not in SUPPORTED_LANGUAGES:
            # Allow unknown language codes but warn
            pass  # FAL API may support more languages than we list

        # Validate keyterms if provided
        if keyterms is not None:
            if not isinstance(keyterms, list):
                raise ValueError("keyterms must be a list of strings")
            if not all(isinstance(term, str) for term in keyterms):
                raise ValueError("All keyterms must be strings")

        # Build params with defaults
        params = {
            "audio_url": audio_url,
            "language_code": language_code if language_code is not None else self.defaults["language_code"],
            "diarize": diarize if diarize is not None else self.defaults["diarize"],
            "tag_audio_events": tag_audio_events if tag_audio_events is not None else self.defaults["tag_audio_events"],
        }

        # Only include keyterms if provided (affects pricing)
        if keyterms:
            params["keyterms"] = keyterms

        return params

    def transcribe(
        self,
        audio_url: Optional[str] = None,
        language_code: Optional[str] = None,
        diarize: bool = True,
        tag_audio_events: bool = True,
        keyterms: Optional[List[str]] = None,
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe audio using ElevenLabs Scribe v2.

        Args:
            audio_url: URL of audio file to transcribe
            language_code: Language code for transcription
            diarize: Enable speaker identification
            tag_audio_events: Enable audio event tagging
            keyterms: Terms to bias transcription toward

        Returns:
            TranscriptionResult with text and metadata
        """
        # Validate parameters
        try:
            params = self.validate_parameters(
                audio_url=audio_url,
                language_code=language_code,
                diarize=diarize,
                tag_audio_events=tag_audio_events,
                keyterms=keyterms,
            )
        except ValueError as e:
            return TranscriptionResult(
                success=False,
                error=str(e),
                model_used=self.model_name,
            )

        # Build API payload
        payload = {
            "audio_url": params["audio_url"],
            "diarize": params["diarize"],
            "tag_audio_events": params["tag_audio_events"],
        }

        # Add optional parameters
        if params.get("language_code"):
            payload["language_code"] = params["language_code"]
        if params.get("keyterms"):
            payload["keyterms"] = params["keyterms"]

        # Call FAL API
        api_result = self._call_fal_api(payload)

        if not api_result["success"]:
            return TranscriptionResult(
                success=False,
                error=api_result.get("error", "API call failed"),
                processing_time=api_result.get("processing_time", 0),
                model_used=self.model_name,
            )

        # Parse API response
        result = api_result["result"]
        processing_time = api_result["processing_time"]

        # Extract text
        text = result.get("text", "")

        # Parse word timestamps if available
        words = None
        if "words" in result:
            words = [
                WordTimestamp(
                    word=w.get("word", ""),
                    start=w.get("start", 0.0),
                    end=w.get("end", 0.0),
                    speaker=w.get("speaker"),
                    confidence=w.get("confidence"),
                )
                for w in result["words"]
            ]

        # Parse audio events if available
        audio_events = None
        if "audio_events" in result:
            audio_events = [
                AudioEvent(
                    event_type=e.get("type", "unknown"),
                    start=e.get("start", 0.0),
                    end=e.get("end", 0.0),
                )
                for e in result["audio_events"]
            ]

        # Extract unique speakers
        speakers = None
        if words and diarize:
            speaker_set = set(w.speaker for w in words if w.speaker)
            if speaker_set:
                speakers = sorted(list(speaker_set))

        # Get duration (estimate from last word timestamp if not provided)
        duration = result.get("duration")
        if duration is None and words:
            duration = max(w.end for w in words)

        # Estimate cost
        duration_minutes = (duration or 0) / 60.0
        use_keyterms = bool(keyterms)
        cost = self.estimate_cost(duration_minutes, use_keyterms=use_keyterms)

        return TranscriptionResult(
            success=True,
            text=text,
            words=words,
            speakers=speakers,
            audio_events=audio_events,
            duration=duration,
            cost=cost,
            processing_time=processing_time,
            model_used=self.model_name,
            language_detected=result.get("language_code"),
            metadata={
                "diarize": params["diarize"],
                "tag_audio_events": params["tag_audio_events"],
                "keyterms_used": bool(keyterms),
            },
        )

    def estimate_cost(
        self,
        duration_minutes: float,
        use_keyterms: bool = False,
        **kwargs
    ) -> float:
        """
        Estimate transcription cost.

        Args:
            duration_minutes: Audio duration in minutes
            use_keyterms: Whether keyterms feature is used (+30% cost)

        Returns:
            Estimated cost in USD
        """
        base_cost = duration_minutes * self.pricing["per_minute"]
        if use_keyterms:
            base_cost *= (1 + self.pricing["keyterms_surcharge"])
        return round(base_cost, 4)

    def get_model_info(self) -> Dict[str, Any]:
        """Return model metadata."""
        return {
            "name": self.model_name,
            "display_name": MODEL_DISPLAY_NAMES[self.model_name],
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "features": [
                "word_timestamps",
                "speaker_diarization",
                "audio_event_tagging",
                "99_languages",
                "fast_inference",
            ],
            "supported_languages": len(SUPPORTED_LANGUAGES),
            "best_for": "Fast, accurate transcription with speaker identification",
            "commercial_use": True,
        }
