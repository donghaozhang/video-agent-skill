"""
Kling Video v2.6 Pro text-to-video model implementation.
"""

from typing import Dict, Any
from .base import BaseTextToVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class Kling26ProModel(BaseTextToVideoModel):
    """
    Kling Video v2.6 Pro for text-to-video generation.

    API Parameters:
        - prompt: Text description
        - duration: "5", "10" seconds
        - aspect_ratio: "16:9", "9:16", "1:1"
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)
        - generate_audio: Enable audio generation

    Pricing: $0.07/second (no audio), $0.14/second (with audio)
    """

    def __init__(self):
        super().__init__("kling_2_6_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v2.6 Pro parameters."""
        defaults = DEFAULT_VALUES.get("kling_2_6_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_2_6_pro", ["5", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_2_6_pro", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        return {
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "generate_audio": bool(generate_audio)
        }

    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kling v2.6 Pro."""
        args = {
            "prompt": prompt,
            "duration": kwargs.get("duration", "5"),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5),
            "generate_audio": kwargs.get("generate_audio", True)
        }

        # Add negative prompt if provided
        negative_prompt = kwargs.get("negative_prompt")
        if negative_prompt:
            args["negative_prompt"] = negative_prompt

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling v2.6 Pro model information."""
        return {
            **MODEL_INFO.get("kling_2_6_pro", {}),
            "endpoint": self.endpoint,
            "pricing": self.pricing
        }

    def estimate_cost(self, duration: str = "5", generate_audio: bool = True, **kwargs) -> float:
        """Estimate cost based on duration and audio setting."""
        duration_seconds = int(duration)
        cost_per_second = 0.14 if generate_audio else 0.07
        return cost_per_second * duration_seconds
