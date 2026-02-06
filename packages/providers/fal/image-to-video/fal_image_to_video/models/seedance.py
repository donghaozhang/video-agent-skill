"""
ByteDance Seedance v1.5 Pro model implementation.

Advanced motion synthesis with seed control.
"""

from typing import Dict, Any, Optional
from .base import BaseVideoModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, DURATION_OPTIONS


class SeedanceModel(BaseVideoModel):
    """
    ByteDance Seedance v1.5 Pro model for image-to-video generation.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL
        - duration: 5, 10 seconds
        - seed: Optional seed for reproducibility

    Pricing: ~$0.08/second
    """

    MODEL_KEY = "seedance_1_5_pro"

    def __init__(self):
        """Initialize the Seedance v1.5 Pro image-to-video model."""
        super().__init__("seedance_1_5_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Seedance parameters."""
        defaults = DEFAULT_VALUES.get("seedance_1_5_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        seed = kwargs.get("seed", defaults.get("seed", None))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("seedance_1_5_pro", ["5", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate seed if provided
        if seed is not None:
            if not isinstance(seed, int) or seed < 0:
                raise ValueError("Seed must be a non-negative integer")

        return {
            "duration": duration,
            "seed": seed
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Seedance."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5")
        }

        # Add optional seed
        seed = kwargs.get("seed")
        if seed is not None:
            args["seed"] = seed

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Seedance model information."""
        return {
            **MODEL_INFO.get("seedance_1_5_pro", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "supports_seed": True
        }
