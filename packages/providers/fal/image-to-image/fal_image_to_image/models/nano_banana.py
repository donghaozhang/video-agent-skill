"""
Nano Banana Pro Edit model implementation
"""

from typing import Dict, Any, Optional
from .base import BaseModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES


class NanoBananaProEditModel(BaseModel):
    """Nano Banana Pro Edit model for fast image modifications."""

    def __init__(self):
        super().__init__("nano_banana_pro_edit")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Nano Banana Pro Edit parameters."""
        defaults = DEFAULT_VALUES.get("nano_banana_pro_edit", {})

        strength = kwargs.get("strength", defaults.get("strength", 0.75))
        num_inference_steps = kwargs.get("num_inference_steps", defaults.get("num_inference_steps", 4))

        # Validate strength range
        if not 0.0 <= strength <= 1.0:
            raise ValueError(f"strength must be between 0.0 and 1.0, got {strength}")

        # Validate inference steps
        if not 1 <= num_inference_steps <= 8:
            raise ValueError(f"num_inference_steps must be between 1 and 8, got {num_inference_steps}")

        return {
            "strength": strength,
            "num_inference_steps": num_inference_steps
        }

    def prepare_arguments(self, prompt: str, image_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Nano Banana Pro Edit."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "strength": kwargs.get("strength", 0.75),
            "num_inference_steps": kwargs.get("num_inference_steps", 4)
        }

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Nano Banana Pro Edit model information."""
        return {
            **MODEL_INFO.get("nano_banana_pro_edit", {}),
            "endpoint": self.endpoint
        }
