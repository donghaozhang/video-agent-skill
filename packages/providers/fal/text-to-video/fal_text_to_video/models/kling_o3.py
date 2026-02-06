"""
Kling O3 (Omni 3) text-to-video model implementation.

O3 Pro T2V focuses on element-based character/object consistency with the 'elements' parameter
and supports @ reference syntax in prompts (@Element1, @Image1, etc).

Pricing:
- $0.224/second (audio off)
- $0.28/second (audio on)
"""

from typing import Dict, Any, List, Optional
from .base import BaseTextToVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class KlingO3ProT2VModel(BaseTextToVideoModel):
    """
    Kling O3 Pro text-to-video model with element-based character consistency.

    Features:
        - Professional-tier cinematic quality
        - Element-based character/object consistency
        - @ reference syntax in prompts (@Element1, @Image1)
        - Native audio generation
        - 3-15 second duration support
        - Multi-prompt support
        - Shot type customization

    API Parameters:
        - prompt: Text description with optional @ references
        - duration: 3-15 seconds
        - aspect_ratio: "16:9", "9:16", "1:1"
        - generate_audio: Enable native audio
        - elements: Character/object definitions
        - image_urls: Style reference images
        - multi_prompt: Multiple prompt segments
        - shot_type: Camera movement customization
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)

    Pricing:
        - $0.224/second (audio off)
        - $0.28/second (audio on)
    """

    MODEL_KEY = "kling_o3_pro_t2v"

    def __init__(self):
        """Initialize the Kling O3 Pro text-to-video model."""
        super().__init__("kling_o3_pro_t2v")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling O3 Pro T2V parameters."""
        defaults = DEFAULT_VALUES.get("kling_o3_pro_t2v", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", True))
        elements = kwargs.get("elements", defaults.get("elements", []))
        image_urls = kwargs.get("image_urls", defaults.get("image_urls", []))
        multi_prompt = kwargs.get("multi_prompt", defaults.get("multi_prompt", []))
        shot_type = kwargs.get("shot_type", defaults.get("shot_type"))

        # Validate duration (3-15 seconds)
        valid_durations = DURATION_OPTIONS.get("kling_o3_pro_t2v", ["3", "5", "10", "15"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_o3_pro_t2v", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        # Validate cfg_scale if provided
        if cfg_scale is not None and not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        # Validate elements structure
        if elements and not isinstance(elements, list):
            raise ValueError("elements must be a list")

        return {
            "duration": str(duration),
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "generate_audio": bool(generate_audio),
            "elements": elements if isinstance(elements, list) else [],
            "image_urls": image_urls if isinstance(image_urls, list) else [],
            "multi_prompt": multi_prompt if isinstance(multi_prompt, list) else [],
            "shot_type": shot_type
        }

    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kling O3 Pro T2V."""
        args = {
            "prompt": prompt,
            "duration": int(kwargs.get("duration", "5")),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "generate_audio": kwargs.get("generate_audio", True)
        }

        # Add negative prompt if provided
        negative_prompt = kwargs.get("negative_prompt")
        if negative_prompt:
            args["negative_prompt"] = negative_prompt

        # Add cfg_scale if provided
        cfg_scale = kwargs.get("cfg_scale")
        if cfg_scale is not None:
            args["cfg_scale"] = cfg_scale

        # Add elements (character/object definitions)
        elements = kwargs.get("elements", [])
        if elements:
            args["elements"] = elements

        # Add reference images
        image_urls = kwargs.get("image_urls", [])
        if image_urls:
            args["image_urls"] = image_urls

        # Add multi-prompt if provided
        multi_prompt = kwargs.get("multi_prompt", [])
        if multi_prompt:
            args["multi_prompt"] = multi_prompt

        # Add shot type if provided
        shot_type = kwargs.get("shot_type")
        if shot_type:
            args["shot_type"] = shot_type

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling O3 Pro T2V model information."""
        return {
            **MODEL_INFO.get("kling_o3_pro_t2v", {}),
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "professional_tier": True,
            "audio_supported": True,
            "elements_supported": True,
            "reference_syntax": True
        }

    def estimate_cost(
        self,
        duration: str = "5",
        generate_audio: bool = True,
        **kwargs
    ) -> float:
        """
        Estimate cost based on duration and audio settings.

        Pricing:
            - $0.224/second (audio off)
            - $0.28/second (audio on)
        """
        duration_seconds = int(duration)
        if generate_audio:
            cost_per_second = 0.28  # Audio on pricing
        else:
            cost_per_second = 0.224  # Audio off pricing
        return cost_per_second * duration_seconds
