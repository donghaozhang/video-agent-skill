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
