"""
xAI Grok Imagine Video text-to-video model implementation.

Grok Imagine Video generates high-quality videos with native audio
from text prompts via FAL AI.
"""

from typing import Dict, Any
from .base import BaseTextToVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class GrokImagineModel(BaseTextToVideoModel):
    """
    xAI Grok Imagine Video for text-to-video generation.

    API Parameters:
        - prompt: Text description (max 4,096 chars)
        - duration: 1-15 seconds (default: 6)
        - resolution: "480p", "720p" (default: "720p")
        - aspect_ratio: "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16"

    Pricing:
        - Base cost (6s): $0.30
        - Additional seconds: $0.05 each
    """

    def __init__(self) -> None:
        super().__init__("grok_imagine")

    def validate_parameters(self, **kwargs: Any) -> Dict[str, Any]:
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
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))

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
            ["16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16"]
        )
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio
        }

    def prepare_arguments(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Prepare API arguments for Grok Imagine Video.

        Args:
            prompt: Text description for video generation
            **kwargs: Validated parameters

        Returns:
            Dict of arguments for fal_client.subscribe()
        """
        return {
            "prompt": prompt,
            "duration": kwargs.get("duration", 6),
            "resolution": kwargs.get("resolution", "720p"),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9")
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
            "pricing": self.pricing
        }

    def estimate_cost(self, duration: int = 6, **kwargs: Any) -> float:
        """
        Estimate cost based on duration.

        Pricing: $0.30 for 6s base, $0.05 per additional second.

        Args:
            duration: Video duration in seconds (1-15)
            **kwargs: Additional parameters (unused)

        Returns:
            Estimated cost in USD
        """
        base_cost = self.pricing.get("base_cost_6s", 0.30)
        cost_per_additional = self.pricing.get("cost_per_additional_second", 0.05)

        if duration <= 6:
            return base_cost
        else:
            additional_seconds = duration - 6
            return base_cost + (additional_seconds * cost_per_additional)
