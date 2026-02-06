"""
Sora 2 and Sora 2 Pro model implementations.

OpenAI's image-to-video models accessed via FAL AI.
"""

from typing import Dict, Any
from .base import BaseVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class Sora2Model(BaseVideoModel):
    """
    Sora 2 model for image-to-video generation.

    API Parameters:
        - prompt: Text description (1-5000 chars)
        - image_url: Input image URL
        - resolution: auto, 720p
        - aspect_ratio: auto, 9:16, 16:9
        - duration: 4, 8, 12 seconds
        - delete_video: Auto-delete for privacy

    Pricing: $0.10/second
    """

    MODEL_KEY = "sora_2"

    def __init__(self):
        """Initialize the Sora 2 image-to-video model."""
        super().__init__("sora_2")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Sora 2 parameters."""
        defaults = DEFAULT_VALUES.get("sora_2", {})

        duration = kwargs.get("duration", defaults.get("duration", 4))
        resolution = kwargs.get("resolution", defaults.get("resolution", "auto"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "auto"))
        delete_video = kwargs.get("delete_video", defaults.get("delete_video", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("sora_2", [4, 8, 12])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("sora_2", ["auto", "720p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("sora_2", ["auto", "9:16", "16:9"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "delete_video": bool(delete_video)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Sora 2."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", 4),
            "resolution": kwargs.get("resolution", "auto"),
            "aspect_ratio": kwargs.get("aspect_ratio", "auto"),
            "delete_video": kwargs.get("delete_video", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Sora 2 model information."""
        return {
            **MODEL_INFO.get("sora_2", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }


class Sora2ProModel(BaseVideoModel):
    """
    Sora 2 Pro model for professional image-to-video generation.

    API Parameters:
        - prompt: Text description (1-5000 chars)
        - image_url: Input image URL
        - resolution: auto, 720p, 1080p
        - aspect_ratio: auto, 9:16, 16:9
        - duration: 4, 8, 12 seconds
        - delete_video: Auto-delete for privacy

    Pricing: $0.30/second (720p), $0.50/second (1080p)
    """

    MODEL_KEY = "sora_2_pro"

    def __init__(self):
        """Initialize the Sora 2 Pro image-to-video model."""
        super().__init__("sora_2_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Sora 2 Pro parameters."""
        defaults = DEFAULT_VALUES.get("sora_2_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", 4))
        resolution = kwargs.get("resolution", defaults.get("resolution", "auto"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "auto"))
        delete_video = kwargs.get("delete_video", defaults.get("delete_video", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("sora_2_pro", [4, 8, 12])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("sora_2_pro", ["auto", "720p", "1080p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("sora_2_pro", ["auto", "9:16", "16:9"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "delete_video": bool(delete_video)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Sora 2 Pro."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", 4),
            "resolution": kwargs.get("resolution", "auto"),
            "aspect_ratio": kwargs.get("aspect_ratio", "auto"),
            "delete_video": kwargs.get("delete_video", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Sora 2 Pro model information."""
        return {
            **MODEL_INFO.get("sora_2_pro", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }

    def estimate_cost(self, duration: int, resolution: str = "720p", **kwargs) -> float:
        """Estimate cost with resolution-based pricing."""
        if resolution == "1080p":
            return 0.50 * duration
        return 0.30 * duration
