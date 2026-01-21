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
