"""
Wan v2.6 image-to-video model implementation.
"""

from typing import Dict, Any, Optional
from .base import BaseVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS
)


class Wan26Model(BaseVideoModel):
    """
    Wan v2.6 for image-to-video generation.

    API Parameters:
        - prompt: Text description (max 800 chars)
        - image_url: Input image URL
        - resolution: "720p", "1080p"
        - duration: "5", "10", "15" seconds
        - negative_prompt: Elements to avoid (max 500 chars)
        - enable_prompt_expansion: Expand prompt for better results
        - multi_shots: Enable multi-shot generation
        - seed: Random seed for reproducibility
        - enable_safety_checker: Content safety filtering
        - audio_url: Optional audio input (WAV/MP3, 3-30s)

    Pricing: $0.10/s (720p), $0.15/s (1080p)
    """

    def __init__(self):
        super().__init__("wan_2_6")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Wan v2.6 parameters."""
        defaults = DEFAULT_VALUES.get("wan_2_6", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        resolution = kwargs.get("resolution", defaults.get("resolution", "1080p"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", ""))
        enable_prompt_expansion = kwargs.get(
            "enable_prompt_expansion",
            defaults.get("enable_prompt_expansion", True)
        )
        multi_shots = kwargs.get("multi_shots", defaults.get("multi_shots", False))
        seed = kwargs.get("seed", defaults.get("seed"))
        enable_safety_checker = kwargs.get(
            "enable_safety_checker",
            defaults.get("enable_safety_checker", True)
        )
        audio_url = kwargs.get("audio_url")

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("wan_2_6", ["5", "10", "15"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("wan_2_6", ["720p", "1080p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate prompt lengths
        if negative_prompt and len(negative_prompt) > 500:
            raise ValueError("negative_prompt must be max 500 characters")

        return {
            "duration": duration,
            "resolution": resolution,
            "negative_prompt": negative_prompt,
            "enable_prompt_expansion": bool(enable_prompt_expansion),
            "multi_shots": bool(multi_shots),
            "seed": seed,
            "enable_safety_checker": bool(enable_safety_checker),
            "audio_url": audio_url
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Wan v2.6."""
        # Validate prompt length
        if len(prompt) > 800:
            raise ValueError("prompt must be max 800 characters")

        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5"),
            "resolution": kwargs.get("resolution", "1080p"),
            "enable_prompt_expansion": kwargs.get("enable_prompt_expansion", True),
            "multi_shots": kwargs.get("multi_shots", False),
            "enable_safety_checker": kwargs.get("enable_safety_checker", True)
        }

        # Add optional parameters
        negative_prompt = kwargs.get("negative_prompt")
        if negative_prompt:
            args["negative_prompt"] = negative_prompt

        seed = kwargs.get("seed")
        if seed is not None:
            args["seed"] = seed

        audio_url = kwargs.get("audio_url")
        if audio_url:
            args["audio_url"] = audio_url

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Wan v2.6 model information."""
        return {
            **MODEL_INFO.get("wan_2_6", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }

    def estimate_cost(
        self,
        duration: str = "5",
        resolution: str = "1080p",
        **kwargs
    ) -> float:
        """Estimate cost based on duration and resolution."""
        duration_seconds = int(duration)
        if resolution == "1080p":
            return 0.15 * duration_seconds
        return 0.10 * duration_seconds
