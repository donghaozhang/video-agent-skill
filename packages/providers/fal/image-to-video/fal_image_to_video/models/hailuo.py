"""
MiniMax Hailuo-02 model implementation.

Refactored from existing implementation for modular architecture.
"""

from typing import Dict, Any
from .base import BaseVideoModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, DURATION_OPTIONS


class HailuoModel(BaseVideoModel):
    """
    MiniMax Hailuo-02 model for image-to-video generation.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL
        - duration: 6, 10 seconds
        - prompt_optimizer: Enable prompt optimization

    Pricing: ~$0.05/second
    """

    MODEL_KEY = "hailuo"

    def __init__(self):
        super().__init__("hailuo")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Hailuo parameters."""
        defaults = DEFAULT_VALUES.get("hailuo", {})

        duration = kwargs.get("duration", defaults.get("duration", "6"))
        prompt_optimizer = kwargs.get("prompt_optimizer", defaults.get("prompt_optimizer", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("hailuo", ["6", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        return {
            "duration": duration,
            "prompt_optimizer": bool(prompt_optimizer)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Hailuo."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "6"),
            "prompt_optimizer": kwargs.get("prompt_optimizer", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Hailuo model information."""
        return {
            **MODEL_INFO.get("hailuo", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }
