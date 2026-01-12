"""
GPT Image 1.5 Edit model implementation
"""

from typing import Dict, Any, Optional
from .base import BaseModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES


class GPTImage15EditModel(BaseModel):
    """GPT Image 1.5 Edit model for GPT-powered image modifications."""

    def __init__(self):
        super().__init__("gpt_image_1_5_edit")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate GPT Image 1.5 Edit parameters."""
        defaults = DEFAULT_VALUES.get("gpt_image_1_5_edit", {})

        strength = kwargs.get("strength", defaults.get("strength", 0.75))

        # Validate strength range
        if not 0.0 <= strength <= 1.0:
            raise ValueError(f"strength must be between 0.0 and 1.0, got {strength}")

        return {
            "strength": strength
        }

    def prepare_arguments(self, prompt: str, image_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for GPT Image 1.5 Edit."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "strength": kwargs.get("strength", 0.75)
        }

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get GPT Image 1.5 Edit model information."""
        return {
            **MODEL_INFO.get("gpt_image_1_5_edit", {}),
            "endpoint": self.endpoint
        }
