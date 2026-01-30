"""
xAI Grok Imagine Video image-to-video model implementation.

Grok Imagine Video generates high-quality videos with native audio
from images and text prompts via FAL AI.
"""

from typing import Dict, Any
from .base import BaseVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class GrokImagineModel(BaseVideoModel):
    """
    xAI Grok Imagine Video for image-to-video generation.

    API Parameters:
        - prompt: Text description (max 4,096 chars)
        - image_url: URL of input image
        - duration: 1-15 seconds (default: 6)
        - resolution: "480p", "720p" (default: "720p")
        - aspect_ratio: "auto", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16"

    Pricing:
        - Image input: $0.002
        - Per second: $0.05
        - Total for 6s: $0.302
    """

    def __init__(self):
        super().__init__("grok_imagine")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate Grok Imagine parameters.

        Args:
            **kwargs: Model parameters including duration, resolution, aspect_ratio

        Returns:
            Dict with validated parameters

        Raises:
            ValueError: If any parameter is invalid
        """
        defaults = DEFAULT_VALUES.get("grok_imagine", {})

        duration = kwargs.get("duration", defaults.get("duration", 6))
        resolution = kwargs.get("resolution", defaults.get("resolution", "720p"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "auto"))

        # Validate duration (1-15 seconds)
        valid_durations = DURATION_OPTIONS.get("grok_imagine", list(range(1, 16)))
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: 1-15 seconds")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("grok_imagine", ["480p", "720p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get(
            "grok_imagine",
            ["auto", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16"]
        )
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare API arguments for Grok Imagine Video.

        Args:
            prompt: Text description for video generation
            image_url: URL of input image
            **kwargs: Validated parameters

        Returns:
            Dict of arguments for fal_client.subscribe()
        """
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", 6),
            "resolution": kwargs.get("resolution", "720p"),
            "aspect_ratio": kwargs.get("aspect_ratio", "auto")
        }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get Grok Imagine model information.

        Returns:
            Dict with model metadata, endpoint, and pricing
        """
        return {
            **MODEL_INFO.get("grok_imagine", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }

    def estimate_cost(self, duration: int = 6, **kwargs) -> float:
        """
        Estimate cost based on duration.

        Pricing: $0.002 image input + $0.05 per second.

        Args:
            duration: Video duration in seconds (1-15)
            **kwargs: Additional parameters (unused)

        Returns:
            Estimated cost in USD
        """
        image_cost = 0.002
        cost_per_second = self.price_per_second  # $0.05
        return image_cost + (cost_per_second * duration)
