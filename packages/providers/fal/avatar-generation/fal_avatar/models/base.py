"""Base class for all FAL avatar and video generation models."""

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
class AvatarGenerationResult:
    """Standardized result for avatar/video generation."""

    success: bool
    video_url: Optional[str] = None
    duration: Optional[float] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    model_used: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class BaseAvatarModel(ABC):
    """Abstract base class for FAL avatar/video generation models."""

    def __init__(self, model_name: str):
        """
        Initialize the base avatar model.

        Args:
            model_name: Unique identifier for the model
        """
        self.model_name = model_name
        self.endpoint = ""
        self.pricing: Dict[str, Any] = {}
        self.max_duration = 60
        self.supported_resolutions: List[str] = []
        self.supported_aspect_ratios: List[str] = []

    @abstractmethod
    def generate(self, **kwargs) -> AvatarGenerationResult:
        """
        Generate video using the model.

        Args:
            **kwargs: Model-specific parameters

        Returns:
            AvatarGenerationResult with video URL and metadata
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
    def estimate_cost(self, duration: float, **kwargs) -> float:
        """
        Estimate generation cost based on parameters.

        Args:
            duration: Video duration in seconds
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

    def _validate_resolution(self, resolution: str) -> str:
        """
        Validate resolution parameter.

        Args:
            resolution: Resolution string

        Returns:
            Validated resolution

        Raises:
            ValueError: If resolution not supported
        """
        if self.supported_resolutions and resolution not in self.supported_resolutions:
            raise ValueError(
                f"Unsupported resolution '{resolution}'. "
                f"Supported: {self.supported_resolutions}"
            )
        return resolution

    def _validate_aspect_ratio(self, aspect_ratio: str) -> str:
        """
        Validate aspect ratio parameter.

        Args:
            aspect_ratio: Aspect ratio string

        Returns:
            Validated aspect ratio

        Raises:
            ValueError: If aspect ratio not supported
        """
        if self.supported_aspect_ratios and aspect_ratio not in self.supported_aspect_ratios:
            raise ValueError(
                f"Unsupported aspect ratio '{aspect_ratio}'. "
                f"Supported: {self.supported_aspect_ratios}"
            )
        return aspect_ratio

    def _validate_duration(self, duration: float) -> float:
        """
        Validate duration parameter.

        Args:
            duration: Duration in seconds

        Returns:
            Validated duration

        Raises:
            ValueError: If duration is invalid or exceeds max
        """
        import math

        if not isinstance(duration, (int, float)):
            raise ValueError(f"Duration must be a number, got {type(duration).__name__}")
        if math.isnan(duration) or math.isinf(duration):
            raise ValueError(f"Duration must be finite, got {duration}")
        if duration <= 0:
            raise ValueError(f"Duration must be positive, got {duration}s")
        if duration > self.max_duration:
            raise ValueError(
                f"Duration {duration}s exceeds maximum {self.max_duration}s"
            )
        return duration
