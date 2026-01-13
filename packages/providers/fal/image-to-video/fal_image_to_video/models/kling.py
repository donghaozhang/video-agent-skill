"""
Kling Video model implementations (v2.1 and v2.6 Pro).

Supports frame interpolation via end_frame parameter (tail_image_url).
"""

from typing import Dict, Any, Optional
from .base import BaseVideoModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, DURATION_OPTIONS


class KlingModel(BaseVideoModel):
    """
    Kling Video v2.1 model for image-to-video generation.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL (start frame)
        - tail_image_url: End frame for interpolation (optional)
        - duration: 5, 10 seconds
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)

    Pricing: ~$0.05/second
    """

    def __init__(self):
        super().__init__("kling_2_1")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v2.1 parameters."""
        defaults = DEFAULT_VALUES.get("kling_2_1", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", "blur, distort, and low quality"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        end_frame = kwargs.get("end_frame")  # Optional end frame for interpolation

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_2_1", ["5", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        return {
            "duration": duration,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "end_frame": end_frame
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling v2.1."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5"),
            "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5)
        }

        # Add end frame for interpolation (tail_image_url)
        end_frame = kwargs.get("end_frame")
        if end_frame:
            args["tail_image_url"] = end_frame

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling v2.1 model information."""
        return {
            **MODEL_INFO.get("kling_2_1", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }


class Kling26ProModel(BaseVideoModel):
    """
    Kling Video v2.6 Pro model for professional image-to-video generation.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL (start frame)
        - tail_image_url: End frame for interpolation (optional)
        - duration: 5, 10 seconds
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)

    Pricing: ~$0.10/second
    """

    def __init__(self):
        super().__init__("kling_2_6_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v2.6 Pro parameters."""
        defaults = DEFAULT_VALUES.get("kling_2_6_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", "blur, distort, and low quality"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        end_frame = kwargs.get("end_frame")  # Optional end frame for interpolation

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_2_6_pro", ["5", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        return {
            "duration": duration,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "end_frame": end_frame
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling v2.6 Pro."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5"),
            "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5)
        }

        # Add end frame for interpolation (tail_image_url)
        end_frame = kwargs.get("end_frame")
        if end_frame:
            args["tail_image_url"] = end_frame

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling v2.6 Pro model information."""
        return {
            **MODEL_INFO.get("kling_2_6_pro", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "professional_tier": True
        }
