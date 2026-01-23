# Implementation Plan: ElevenLabs Scribe v2 Speech-to-Text

## Overview

Add the ElevenLabs Scribe v2 speech-to-text model via FAL AI to enable high-quality audio transcription with speaker diarization and audio event tagging.

**FAL Endpoint**: `fal-ai/elevenlabs/speech-to-text/scribe-v2`

## Model Capabilities

| Feature | Description |
|---------|-------------|
| **Speed** | Blazingly fast inference |
| **Languages** | 99 languages supported |
| **Timestamps** | Word-level timestamps included |
| **Diarization** | Speaker identification (who said what) |
| **Audio Events** | Tags laughter, applause, music, etc. |
| **Pricing** | $0.008/minute (30% surcharge with keyterms) |

## API Parameters

### Required
| Parameter | Type | Description |
|-----------|------|-------------|
| `audio_url` | string | URL of audio file to transcribe |

### Optional
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language_code` | string | auto | Language code (e.g., "eng", "spa", "fra") |
| `diarize` | boolean | true | Enable speaker identification |
| `tag_audio_events` | boolean | true | Tag audio events (laughter, applause) |
| `keyterms` | list[string] | null | Bias toward specific terms (+30% cost) |

## Architecture Decision

**Location**: New `speech-to-text` package under `packages/providers/fal/`

**Rationale**:
- Follows existing FAL provider pattern (text-to-image, avatar-generation, etc.)
- Mirrors the text-to-speech service structure
- Allows future expansion with other STT models
- Maintains clean separation from video-tools Whisper implementation

---

## Subtask 1: Create Package Structure
**Estimated time**: 15 minutes

### Files to CREATE

#### `packages/providers/fal/speech-to-text/fal_speech_to_text/__init__.py`

```python
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
```

#### `packages/providers/fal/speech-to-text/fal_speech_to_text/config/__init__.py`

```python
"""Configuration for FAL speech-to-text models."""

from .constants import (
    MODEL_ENDPOINTS,
    MODEL_DISPLAY_NAMES,
    MODEL_PRICING,
    MODEL_DEFAULTS,
    INPUT_REQUIREMENTS,
    SUPPORTED_LANGUAGES,
    MODEL_CATEGORIES,
    MODEL_RECOMMENDATIONS,
    PROCESSING_TIME_ESTIMATES,
)

__all__ = [
    "MODEL_ENDPOINTS",
    "MODEL_DISPLAY_NAMES",
    "MODEL_PRICING",
    "MODEL_DEFAULTS",
    "INPUT_REQUIREMENTS",
    "SUPPORTED_LANGUAGES",
    "MODEL_CATEGORIES",
    "MODEL_RECOMMENDATIONS",
    "PROCESSING_TIME_ESTIMATES",
]
```

#### `packages/providers/fal/speech-to-text/fal_speech_to_text/models/__init__.py`

```python
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
```

---

## Subtask 2: Implement Model Constants
**Estimated time**: 10 minutes

### File to CREATE

#### `packages/providers/fal/speech-to-text/fal_speech_to_text/config/constants.py`

```python
"""Constants for FAL speech-to-text models."""

# Model endpoints
MODEL_ENDPOINTS = {
    "scribe_v2": "fal-ai/elevenlabs/speech-to-text/scribe-v2",
}

# Display names for UI/CLI
MODEL_DISPLAY_NAMES = {
    "scribe_v2": "ElevenLabs Scribe v2",
}

# Pricing structure
MODEL_PRICING = {
    "scribe_v2": {
        "per_minute": 0.008,
        "keyterms_surcharge": 0.30,  # 30% additional when using keyterms
    },
}

# Default values
MODEL_DEFAULTS = {
    "scribe_v2": {
        "language_code": None,  # Auto-detect
        "diarize": True,
        "tag_audio_events": True,
    },
}

# Input requirements
INPUT_REQUIREMENTS = {
    "scribe_v2": {
        "required": ["audio_url"],
        "optional": ["language_code", "diarize", "tag_audio_events", "keyterms"],
    },
}

# Supported language codes (ISO 639-3)
SUPPORTED_LANGUAGES = [
    "eng",  # English
    "spa",  # Spanish
    "fra",  # French
    "deu",  # German
    "ita",  # Italian
    "por",  # Portuguese
    "nld",  # Dutch
    "pol",  # Polish
    "rus",  # Russian
    "jpn",  # Japanese
    "kor",  # Korean
    "cmn",  # Mandarin Chinese
    "ara",  # Arabic
    "hin",  # Hindi
    "ben",  # Bengali
    "vie",  # Vietnamese
    "tur",  # Turkish
    "ukr",  # Ukrainian
    "tha",  # Thai
    "ind",  # Indonesian
    # ... 99 total languages supported
]

# Model categories
MODEL_CATEGORIES = {
    "transcription": ["scribe_v2"],
    "diarization": ["scribe_v2"],
}

# Model recommendations
MODEL_RECOMMENDATIONS = {
    "quality": "scribe_v2",
    "speed": "scribe_v2",
    "diarization": "scribe_v2",
    "multilingual": "scribe_v2",
}

# Processing time estimates (seconds per minute of audio)
PROCESSING_TIME_ESTIMATES = {
    "scribe_v2": 5,  # ~5 seconds per minute of audio
}
```

---

## Subtask 3: Implement Base Model and Result Classes
**Estimated time**: 15 minutes

### File to CREATE

#### `packages/providers/fal/speech-to-text/fal_speech_to_text/models/base.py`

```python
"""Base class for all FAL speech-to-text models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
import os

# Try to import fal_client, gracefully handle if not available
try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False


@dataclass
class WordTimestamp:
    """Word-level timestamp information."""
    word: str
    start: float  # Start time in seconds
    end: float    # End time in seconds
    speaker: Optional[str] = None  # Speaker ID if diarization enabled
    confidence: Optional[float] = None


@dataclass
class AudioEvent:
    """Audio event annotation."""
    event_type: str  # "laughter", "applause", "music", etc.
    start: float     # Start time in seconds
    end: float       # End time in seconds


@dataclass
class TranscriptionResult:
    """Standardized result for speech-to-text transcription."""

    success: bool
    text: str = ""
    words: Optional[List[WordTimestamp]] = None
    speakers: Optional[List[str]] = None
    audio_events: Optional[List[AudioEvent]] = None
    duration: Optional[float] = None  # Audio duration in seconds
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    model_used: Optional[str] = None
    language_detected: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class BaseSpeechToTextModel(ABC):
    """Abstract base class for FAL speech-to-text models."""

    def __init__(self, model_name: str):
        """
        Initialize the base speech-to-text model.

        Args:
            model_name: Unique identifier for the model
        """
        self.model_name = model_name
        self.endpoint = ""
        self.pricing: Dict[str, Any] = {}
        self.defaults: Dict[str, Any] = {}

    @abstractmethod
    def transcribe(self, audio_url: str, **kwargs) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio_url: URL of audio file to transcribe
            **kwargs: Model-specific parameters

        Returns:
            TranscriptionResult with text and metadata
        """
        pass

    @abstractmethod
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate and normalize input parameters.

        Args:
            **kwargs: Parameters to validate

        Returns:
            Dict of validated parameters

        Raises:
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    def estimate_cost(self, duration_minutes: float, **kwargs) -> float:
        """
        Estimate transcription cost based on audio duration.

        Args:
            duration_minutes: Audio duration in minutes
            **kwargs: Additional parameters affecting cost

        Returns:
            Estimated cost in USD
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Return model capabilities and metadata.

        Returns:
            Dict containing model information
        """
        pass

    def _call_fal_api(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API call to FAL endpoint with error handling.

        Args:
            arguments: API request arguments

        Returns:
            Dict with success status, result or error, and processing time
        """
        if not FAL_AVAILABLE:
            return {
                "success": False,
                "error": "fal_client not installed. Run: pip install fal-client",
                "processing_time": 0,
            }

        # Check for API key
        if not os.environ.get("FAL_KEY"):
            return {
                "success": False,
                "error": "FAL_KEY environment variable not set",
                "processing_time": 0,
            }

        start_time = time.time()
        try:
            result = fal_client.subscribe(
                self.endpoint,
                arguments=arguments,
                with_logs=True,
            )
            processing_time = time.time() - start_time
            return {
                "success": True,
                "result": result,
                "processing_time": processing_time,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }

    def _validate_url(self, url: Optional[str], param_name: str) -> str:
        """
        Validate URL format.

        Args:
            url: URL to validate
            param_name: Parameter name for error messages

        Returns:
            Validated URL

        Raises:
            ValueError: If URL is invalid
        """
        if not url:
            raise ValueError(f"{param_name} is required")
        if not url.startswith(("http://", "https://", "data:")):
            raise ValueError(f"{param_name} must be a valid URL or base64 data URI")
        return url
```

---

## Subtask 4: Implement Scribe v2 Model Class
**Estimated time**: 20 minutes

### File to CREATE

#### `packages/providers/fal/speech-to-text/fal_speech_to_text/models/scribe_v2.py`

```python
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
```

---

## Subtask 5: Implement Unified Generator
**Estimated time**: 15 minutes

### File to CREATE

#### `packages/providers/fal/speech-to-text/fal_speech_to_text/generator.py`

```python
"""Unified FAL Speech-to-Text Generator - Routes to appropriate model implementations."""

from typing import Any, Dict, List, Optional

from .models import (
    BaseSpeechToTextModel,
    TranscriptionResult,
    ScribeV2Model,
)
from .config.constants import (
    MODEL_DISPLAY_NAMES,
    MODEL_CATEGORIES,
    MODEL_RECOMMENDATIONS,
    INPUT_REQUIREMENTS,
)


class FALSpeechToTextGenerator:
    """
    Unified generator for FAL speech-to-text models.

    Provides a single interface to access all speech-to-text models:
    - ElevenLabs Scribe v2 - Fast, accurate transcription with diarization
    """

    def __init__(self):
        """Initialize all available models."""
        self.models: Dict[str, BaseSpeechToTextModel] = {
            "scribe_v2": ScribeV2Model(),
        }

    def transcribe(
        self,
        audio_url: str,
        model: str = "scribe_v2",
        **kwargs,
    ) -> TranscriptionResult:
        """
        Transcribe audio using the specified model.

        Args:
            audio_url: URL of audio file to transcribe
            model: Model identifier (see list_models())
            **kwargs: Model-specific parameters

        Returns:
            TranscriptionResult with text and metadata
        """
        if model not in self.models:
            available = ", ".join(self.models.keys())
            return TranscriptionResult(
                success=False,
                error=f"Unknown model '{model}'. Available: {available}",
                model_used=model,
            )

        return self.models[model].transcribe(audio_url=audio_url, **kwargs)

    def transcribe_with_diarization(
        self,
        audio_url: str,
        model: str = "scribe_v2",
        **kwargs,
    ) -> TranscriptionResult:
        """
        Convenience method for transcription with speaker diarization.

        Args:
            audio_url: URL of audio file to transcribe
            model: Model to use
            **kwargs: Additional model parameters

        Returns:
            TranscriptionResult with speaker annotations
        """
        return self.transcribe(
            audio_url=audio_url,
            model=model,
            diarize=True,
            **kwargs,
        )

    def list_models(self) -> List[str]:
        """Return list of available model identifiers."""
        return list(self.models.keys())

    def list_models_by_category(self) -> Dict[str, List[str]]:
        """Return models grouped by category."""
        return MODEL_CATEGORIES.copy()

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.

        Args:
            model: Model identifier

        Returns:
            Dict containing model information

        Raises:
            ValueError: If model not found
        """
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        return self.models[model].get_model_info()

    def get_all_models_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available models."""
        return {name: model.get_model_info() for name, model in self.models.items()}

    def estimate_cost(
        self,
        model: str,
        duration_minutes: float,
        **kwargs,
    ) -> float:
        """
        Estimate transcription cost for a model.

        Args:
            model: Model identifier
            duration_minutes: Audio duration in minutes
            **kwargs: Additional parameters affecting cost

        Returns:
            Estimated cost in USD

        Raises:
            ValueError: If model not found
        """
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        return self.models[model].estimate_cost(duration_minutes, **kwargs)

    def recommend_model(
        self,
        use_case: str = "quality",
    ) -> str:
        """
        Get model recommendation for a use case.

        Args:
            use_case: One of "quality", "speed", "diarization", "multilingual"

        Returns:
            Recommended model identifier
        """
        if use_case in MODEL_RECOMMENDATIONS:
            return MODEL_RECOMMENDATIONS[use_case]
        return MODEL_RECOMMENDATIONS["quality"]

    def get_input_requirements(self, model: str) -> Dict[str, List[str]]:
        """
        Get required and optional inputs for a model.

        Args:
            model: Model identifier

        Returns:
            Dict with "required" and "optional" input lists

        Raises:
            ValueError: If model not found
        """
        if model not in INPUT_REQUIREMENTS:
            raise ValueError(f"Unknown model: {model}")
        return INPUT_REQUIREMENTS[model].copy()

    def get_display_name(self, model: str) -> str:
        """
        Get human-readable display name for a model.

        Args:
            model: Model identifier

        Returns:
            Display name string
        """
        return MODEL_DISPLAY_NAMES.get(model, model)
```

---

## Subtask 6: Update Core Pipeline Constants
**Estimated time**: 10 minutes

### File to MODIFY

#### `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`

**ADD** the following entries:

```python
# In SUPPORTED_MODELS dict, ADD new entry:
SUPPORTED_MODELS = {
    # ... existing entries ...
    "speech_to_text": [
        "scribe_v2",  # ElevenLabs Scribe v2 via FAL
    ],
}

# In PIPELINE_STEPS list, ADD:
PIPELINE_STEPS = [
    "text_to_image",
    "text_to_video",
    "image_understanding",
    "prompt_generation",
    "image_to_image",
    "image_to_video",
    "text_to_speech",
    "speech_to_text",  # ADD THIS
    "add_audio",
    "upscale_video",
    "avatar"
]

# In MODEL_RECOMMENDATIONS dict, ADD new section:
MODEL_RECOMMENDATIONS = {
    # ... existing entries ...
    "speech_to_text": {
        "quality": "scribe_v2",
        "speed": "scribe_v2",
        "diarization": "scribe_v2",
        "multilingual": "scribe_v2",
    },
}

# In COST_ESTIMATES dict, ADD new section:
COST_ESTIMATES = {
    # ... existing entries ...
    "speech_to_text": {
        "scribe_v2": 0.08,  # ~$0.008/min * 10min average
    },
}

# In PROCESSING_TIME_ESTIMATES dict, ADD new section:
PROCESSING_TIME_ESTIMATES = {
    # ... existing entries ...
    "speech_to_text": {
        "scribe_v2": 15,  # ~15 seconds for average audio
    },
}
```

---

## Subtask 7: Implement Step Executor
**Estimated time**: 15 minutes

### File to MODIFY

#### `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/audio_steps.py`

**ADD** the following class at the end of the file:

```python
class SpeechToTextExecutor(BaseStepExecutor):
    """Executor for speech-to-text transcription steps."""

    def __init__(self, generator=None):
        """
        Initialize executor with optional generator.

        Args:
            generator: FALSpeechToTextGenerator instance (lazy loaded if not provided)
        """
        self._generator = generator

    @property
    def generator(self):
        """Lazy load the generator."""
        if self._generator is None:
            from fal_speech_to_text import FALSpeechToTextGenerator
            self._generator = FALSpeechToTextGenerator()
        return self._generator

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute speech-to-text transcription.

        Args:
            step: PipelineStep configuration
            input_data: Audio URL or path from previous step
            chain_config: Pipeline configuration
            step_context: Context from previous steps

        Returns:
            Dict with transcription text, timestamps, speakers, cost, etc.
        """
        try:
            # Get audio URL from params or input
            audio_url = step.params.get("audio_url") or input_data

            if not audio_url:
                return self._create_error_result(
                    "No audio URL provided. Use 'audio_url' parameter or provide from previous step.",
                    step.model
                )

            # Get optional parameters
            language_code = step.params.get("language_code", kwargs.get("language_code"))
            diarize = step.params.get("diarize", kwargs.get("diarize", True))
            tag_audio_events = step.params.get("tag_audio_events", kwargs.get("tag_audio_events", True))
            keyterms = step.params.get("keyterms", kwargs.get("keyterms"))

            print(f"Starting transcription with {step.model}...")

            # Call transcription
            result = self.generator.transcribe(
                audio_url=audio_url,
                model=step.model,
                language_code=language_code,
                diarize=diarize,
                tag_audio_events=tag_audio_events,
                keyterms=keyterms,
            )

            if result.success:
                # Build speaker summary if available
                speaker_count = len(result.speakers) if result.speakers else 0

                return {
                    "success": True,
                    "output_path": None,
                    "output_url": None,
                    "output_text": result.text,
                    "processing_time": result.processing_time or 0,
                    "cost": result.cost or 0,
                    "model": result.model_used,
                    "metadata": {
                        "duration": result.duration,
                        "word_count": len(result.words) if result.words else 0,
                        "speaker_count": speaker_count,
                        "speakers": result.speakers,
                        "audio_events": [
                            {"type": e.event_type, "start": e.start, "end": e.end}
                            for e in (result.audio_events or [])
                        ],
                        "language_detected": result.language_detected,
                        **(result.metadata or {}),
                    },
                    "error": None
                }
            else:
                return self._create_error_result(
                    result.error or "Transcription failed",
                    step.model
                )

        except Exception as e:
            return self._create_error_result(
                f"Speech-to-text execution failed: {str(e)}",
                step.model
            )
```

---

## Subtask 8: Create Unit Tests
**Estimated time**: 20 minutes

### File to CREATE

#### `tests/test_fal_scribe_v2.py`

```python
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

    @patch.object(__import__('fal_speech_to_text.models.scribe_v2', fromlist=['ScribeV2Model']).ScribeV2Model, '_call_fal_api')
    def test_transcribe_success(self, mock_api):
        """Test successful transcription."""
        from fal_speech_to_text.models import ScribeV2Model

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

        model = ScribeV2Model()
        result = model.transcribe(audio_url="https://example.com/audio.mp3")

        assert result.success is True
        assert result.text == "Hello world. This is a test."
        assert result.duration == 2.0
        assert len(result.words) == 6
        assert result.language_detected == "eng"

    @patch.object(__import__('fal_speech_to_text.models.scribe_v2', fromlist=['ScribeV2Model']).ScribeV2Model, '_call_fal_api')
    def test_transcribe_with_diarization(self, mock_api):
        """Test transcription with speaker diarization."""
        from fal_speech_to_text.models import ScribeV2Model

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

        model = ScribeV2Model()
        result = model.transcribe(
            audio_url="https://example.com/audio.mp3",
            diarize=True
        )

        assert result.success is True
        assert result.speakers is not None
        assert len(result.speakers) == 2
        assert "SPEAKER_1" in result.speakers
        assert "SPEAKER_2" in result.speakers

    @patch.object(__import__('fal_speech_to_text.models.scribe_v2', fromlist=['ScribeV2Model']).ScribeV2Model, '_call_fal_api')
    def test_transcribe_api_failure(self, mock_api):
        """Test handling of API failure."""
        from fal_speech_to_text.models import ScribeV2Model

        mock_api.return_value = {
            "success": False,
            "error": "API rate limit exceeded",
            "processing_time": 0.5,
        }

        model = ScribeV2Model()
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Subtask 9: Update Documentation
**Estimated time**: 15 minutes

### Files to MODIFY

#### `CLAUDE.md`

**FIND AND REPLACE** model count:
```
# Old
50 AI models across 8 categories

# New
51 AI models across 9 categories
```

**ADD** new section under "Available AI Models":
```markdown
### 📦 Speech-to-Text (1 model)
- **ElevenLabs Scribe v2** - Fast transcription with 99 languages, diarization, and audio event tagging
```

---

#### `docs/reference/models.md`

**UPDATE** the overview table:
```markdown
| Category | Model Count | Providers |
|----------|-------------|-----------|
| Text-to-Image | 8 | FAL AI, Replicate |
| Image-to-Image | 8 | FAL AI |
| Image-to-Video | 8 | FAL AI, Google |
| Text-to-Video | 4 | FAL AI |
| Image Understanding | 7 | Google Gemini |
| Text-to-Speech | 3 | ElevenLabs |
| Speech-to-Text | 1 | FAL AI (ElevenLabs) |
| Prompt Generation | 5 | OpenRouter |
| Audio/Video Processing | 2 | FAL AI |
| Avatar Generation | 9 | FAL AI |
| **Total** | **51*** | **Multiple** |
```

**ADD** new section after Text-to-Speech:
```markdown
## Speech-to-Text Models

Transcribe audio to text with timestamps and speaker identification.

### scribe_v2
**Provider:** FAL AI (ElevenLabs) | **Cost:** $0.008/minute | **Languages:** 99

Fast, accurate speech-to-text with word-level timestamps and speaker diarization.

```bash
# Python API
from fal_speech_to_text import FALSpeechToTextGenerator

generator = FALSpeechToTextGenerator()
result = generator.transcribe(
    audio_url="https://example.com/audio.mp3",
    diarize=True,
    tag_audio_events=True
)
print(result.text)
print(f"Speakers: {result.speakers}")
```

**Features:**
- Word-level timestamps
- Speaker diarization (who said what)
- Audio event tagging (laughter, applause, music)
- 99 language support
- Keyterms biasing (+30% cost)
- Commercial use allowed

---
```

---

#### `.claude/skills/ai-content-pipeline/Skill.md`

**UPDATE** model count:
```
# Old
## Available AI Models (50 Total)

# New
## Available AI Models (51 Total)
```

**ADD** new section:
```markdown
### Speech-to-Text (1 model)
| Model | Key | Description |
|-------|-----|-------------|
| ElevenLabs Scribe v2 | `scribe_v2` | Fast transcription with diarization |
```

---

#### `packages/providers/fal/speech-to-text/README.md` (CREATE)

```markdown
# FAL Speech-to-Text

Speech-to-text transcription using FAL AI models.

## Installation

```bash
pip install -e packages/providers/fal/speech-to-text
```

## Quick Start

```python
from fal_speech_to_text import FALSpeechToTextGenerator

generator = FALSpeechToTextGenerator()

# Basic transcription
result = generator.transcribe(
    audio_url="https://example.com/audio.mp3"
)
print(result.text)

# With speaker diarization
result = generator.transcribe_with_diarization(
    audio_url="https://example.com/meeting.mp3"
)
for speaker in result.speakers:
    print(f"Speaker: {speaker}")
print(result.text)
```

## Available Models

| Model | Description | Cost |
|-------|-------------|------|
| `scribe_v2` | ElevenLabs Scribe v2 | $0.008/min |

## Features

- **99 Languages**: Auto-detect or specify language
- **Word Timestamps**: Precise timing for each word
- **Speaker Diarization**: Identify who said what
- **Audio Events**: Tag laughter, applause, music, etc.
- **Keyterms**: Bias transcription toward specific terms

## API Reference

### FALSpeechToTextGenerator

```python
generator.transcribe(audio_url, model="scribe_v2", **kwargs)
generator.transcribe_with_diarization(audio_url, model="scribe_v2", **kwargs)
generator.list_models()
generator.get_model_info(model)
generator.estimate_cost(model, duration_minutes, **kwargs)
```

### TranscriptionResult

```python
result.success      # bool
result.text         # str - Full transcription
result.words        # List[WordTimestamp] - Word-level timestamps
result.speakers     # List[str] - Unique speaker IDs
result.audio_events # List[AudioEvent] - Detected audio events
result.duration     # float - Audio duration in seconds
result.cost         # float - Estimated cost in USD
```

## Environment Variables

```
FAL_KEY=your_fal_api_key
```
```

---

## File Summary

| File | Action | Lines |
|------|--------|-------|
| `packages/providers/fal/speech-to-text/fal_speech_to_text/__init__.py` | CREATE | ~30 |
| `packages/providers/fal/speech-to-text/fal_speech_to_text/config/__init__.py` | CREATE | ~20 |
| `packages/providers/fal/speech-to-text/fal_speech_to_text/config/constants.py` | CREATE | ~80 |
| `packages/providers/fal/speech-to-text/fal_speech_to_text/models/__init__.py` | CREATE | ~15 |
| `packages/providers/fal/speech-to-text/fal_speech_to_text/models/base.py` | CREATE | ~130 |
| `packages/providers/fal/speech-to-text/fal_speech_to_text/models/scribe_v2.py` | CREATE | ~200 |
| `packages/providers/fal/speech-to-text/fal_speech_to_text/generator.py` | CREATE | ~140 |
| `packages/providers/fal/speech-to-text/README.md` | CREATE | ~90 |
| `packages/core/.../config/constants.py` | MODIFY | +25 |
| `packages/core/.../pipeline/step_executors/audio_steps.py` | MODIFY | +80 |
| `tests/test_fal_scribe_v2.py` | CREATE | ~300 |
| `CLAUDE.md` | MODIFY | +5 |
| `docs/reference/models.md` | MODIFY | +40 |
| `.claude/skills/ai-content-pipeline/Skill.md` | MODIFY | +10 |

## Dependencies

- `fal-client` (already installed)
- No new dependencies required

## Estimated Total Time

| Subtask | Time |
|---------|------|
| 1. Package structure | 15 min |
| 2. Model constants | 10 min |
| 3. Base classes | 15 min |
| 4. Scribe v2 model | 20 min |
| 5. Unified generator | 15 min |
| 6. Core constants | 10 min |
| 7. Step executor | 15 min |
| 8. Unit tests | 20 min |
| 9. Documentation | 15 min |
| **Total** | **~135 min** |

## Testing Strategy

1. **Unit tests**: `PYTHONPATH="packages/providers/fal/speech-to-text" pytest tests/test_fal_scribe_v2.py -v`
2. **Integration test** (requires FAL_KEY):
   ```python
   from fal_speech_to_text import FALSpeechToTextGenerator

   generator = FALSpeechToTextGenerator()
   result = generator.transcribe(
       audio_url="https://example.com/audio.mp3",
       diarize=True
   )
   print(result.text)
   print(f"Speakers: {result.speakers}")
   print(f"Cost: ${result.cost:.4f}")
   ```

## Success Criteria

- [ ] All unit tests pass
- [ ] Model accessible via `FALSpeechToTextGenerator`
- [ ] Pipeline step `speech_to_text` works in YAML configs
- [ ] Cost estimation accurate ($0.008/min base, +30% with keyterms)
- [ ] Documentation updated with model count 51
- [ ] Package installable with `pip install -e .`
