"""
Sora 2 and Sora 2 Pro text-to-video model implementations.
"""

from typing import Dict, Any
from .base import BaseTextToVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class Sora2Model(BaseTextToVideoModel):
    """
    Sora 2 for text-to-video generation.

    API Parameters:
        - prompt: Text description (1-5000 chars)
        - resolution: "720p"
        - aspect_ratio: "9:16", "16:9"
        - duration: 4, 8, 12 seconds
        - delete_video: Auto-delete for privacy

    Pricing: $0.10/second
    """

    def __init__(self):
        super().__init__("sora_2")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Sora 2 parameters."""
        defaults = DEFAULT_VALUES.get("sora_2", {})

        duration = kwargs.get("duration", defaults.get("duration", 4))
        resolution = kwargs.get("resolution", defaults.get("resolution", "720p"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        delete_video = kwargs.get("delete_video", defaults.get("delete_video", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("sora_2", [4, 8, 12])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("sora_2", ["720p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("sora_2", ["9:16", "16:9"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "delete_video": bool(delete_video)
        }

    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Sora 2."""
        return {
            "prompt": prompt,
            "duration": kwargs.get("duration", 4),
            "resolution": kwargs.get("resolution", "720p"),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "delete_video": kwargs.get("delete_video", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Sora 2 model information."""
        return {
            **MODEL_INFO.get("sora_2", {}),
            "endpoint": self.endpoint,
            "pricing": self.pricing
        }

    def estimate_cost(self, duration: int = 4, **kwargs) -> float:
        """Estimate cost based on duration."""
        return 0.10 * duration


class Sora2ProModel(BaseTextToVideoModel):
    """
    Sora 2 Pro for professional text-to-video generation.

    API Parameters:
        - prompt: Text description (1-5000 chars)
        - resolution: "720p", "1080p"
        - aspect_ratio: "9:16", "16:9"
        - duration: 4, 8, 12 seconds
        - delete_video: Auto-delete for privacy

    Pricing: $0.30/s (720p), $0.50/s (1080p)
    """

    def __init__(self):
        super().__init__("sora_2_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Sora 2 Pro parameters."""
        defaults = DEFAULT_VALUES.get("sora_2_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", 4))
        resolution = kwargs.get("resolution", defaults.get("resolution", "1080p"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        delete_video = kwargs.get("delete_video", defaults.get("delete_video", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("sora_2_pro", [4, 8, 12])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("sora_2_pro", ["720p", "1080p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("sora_2_pro", ["9:16", "16:9"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "delete_video": bool(delete_video)
        }

    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Sora 2 Pro."""
        return {
            "prompt": prompt,
            "duration": kwargs.get("duration", 4),
            "resolution": kwargs.get("resolution", "1080p"),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "delete_video": kwargs.get("delete_video", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Sora 2 Pro model information."""
        return {
            **MODEL_INFO.get("sora_2_pro", {}),
            "endpoint": self.endpoint,
            "pricing": self.pricing
        }

    def estimate_cost(self, duration: int = 4, resolution: str = "1080p", **kwargs) -> float:
        """Estimate cost based on duration and resolution."""
        if resolution == "1080p":
            return 0.50 * duration
        return 0.30 * duration
