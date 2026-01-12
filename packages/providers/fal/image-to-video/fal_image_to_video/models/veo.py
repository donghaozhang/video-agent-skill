"""
Veo 3.1 Fast model implementation.

Google's fast image-to-video model with audio generation support.
"""

from typing import Dict, Any
from .base import BaseVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class Veo31FastModel(BaseVideoModel):
    """
    Veo 3.1 Fast model for image-to-video generation with audio.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL (720p+, 16:9 or 9:16)
        - aspect_ratio: auto, 16:9, 9:16
        - duration: 4s, 6s, 8s
        - resolution: 720p, 1080p
        - generate_audio: Enable audio generation
        - auto_fix: Auto-fix input issues

    Pricing: $0.10/second (no audio), $0.15/second (with audio)
    """

    def __init__(self):
        super().__init__("veo_3_1_fast")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Veo 3.1 Fast parameters."""
        defaults = DEFAULT_VALUES.get("veo_3_1_fast", {})

        duration = kwargs.get("duration", defaults.get("duration", "8s"))
        resolution = kwargs.get("resolution", defaults.get("resolution", "720p"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "auto"))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", True))
        auto_fix = kwargs.get("auto_fix", defaults.get("auto_fix", False))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("veo_3_1_fast", ["4s", "6s", "8s"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("veo_3_1_fast", ["720p", "1080p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("veo_3_1_fast", ["auto", "16:9", "9:16"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "generate_audio": bool(generate_audio),
            "auto_fix": bool(auto_fix)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Veo 3.1 Fast."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "8s"),
            "resolution": kwargs.get("resolution", "720p"),
            "aspect_ratio": kwargs.get("aspect_ratio", "auto"),
            "generate_audio": kwargs.get("generate_audio", True),
            "auto_fix": kwargs.get("auto_fix", False)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Veo 3.1 Fast model information."""
        return {
            **MODEL_INFO.get("veo_3_1_fast", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "supports_audio": True
        }

    def estimate_cost(self, duration, generate_audio: bool = True, **kwargs) -> float:
        """
        Estimate cost with audio-based pricing.

        Args:
            duration: Duration as string ("8s") or int (8)
            generate_audio: Whether audio is generated (higher cost)
            **kwargs: Unused, for base class compatibility

        Returns:
            Estimated cost in USD
        """
        # Handle both int and string duration formats
        if isinstance(duration, str):
            # Parse duration string (e.g., "8s" -> 8)
            seconds = int(duration.rstrip("s"))
        else:
            seconds = int(duration)
        base_rate = 0.15 if generate_audio else 0.10
        return base_rate * seconds
