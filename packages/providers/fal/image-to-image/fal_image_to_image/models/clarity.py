"""
Clarity Upscaler model implementation
"""

from typing import Dict, Any, Optional
from .base import BaseModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES


class ClarityModel(BaseModel):
    """Clarity Upscaler model for high-quality image upscaling."""

    MODEL_KEY = "clarity"

    def __init__(self):
        """Initialize the Clarity Upscaler model."""
        super().__init__("clarity")
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Clarity Upscaler parameters."""
        defaults = DEFAULT_VALUES["clarity"]
        
        # Get parameters with defaults
        scale = kwargs.get("scale", defaults["scale"])
        enable_enhancement = kwargs.get("enable_enhancement", defaults["enable_enhancement"])
        prompt = kwargs.get("prompt", None)
        seed = kwargs.get("seed", None)
        
        # Validate scale
        if not isinstance(scale, (int, float)):
            raise ValueError(f"Scale must be a number, got {type(scale).__name__}")
        
        if scale < 1 or scale > 4:
            raise ValueError(f"Scale must be between 1 and 4, got {scale}")
        
        # Convert to float
        scale = float(scale)
        
        # Validate enable_enhancement
        if not isinstance(enable_enhancement, bool):
            raise ValueError(f"enable_enhancement must be a boolean, got {type(enable_enhancement).__name__}")
        
        # Build parameters
        params = {
            "scale": scale,
            "enable_enhancement": enable_enhancement
        }
        
        # Add optional parameters
        if prompt is not None:
            params["prompt"] = str(prompt)
        
        if seed is not None:
            if not isinstance(seed, int):
                raise ValueError(f"Seed must be an integer, got {type(seed).__name__}")
            params["seed"] = seed
        
        return params
    
    def prepare_arguments(self, prompt: str, image_url: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare API arguments for Clarity Upscaler.
        
        Note: The prompt parameter in the method signature is for compatibility,
        but Clarity uses it differently - as an optional enhancement prompt.
        """
        # Build arguments
        args = {
            "image_url": image_url,
            "scale": kwargs["scale"],
            "enable_enhancement": kwargs["enable_enhancement"]
        }
        
        # Add optional prompt if provided
        if "prompt" in kwargs and kwargs["prompt"]:
            args["prompt"] = kwargs["prompt"]
        
        # Add seed if provided
        if "seed" in kwargs and kwargs["seed"] is not None:
            args["seed"] = kwargs["seed"]
        
        return args
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Clarity Upscaler model information."""
        return {
            **MODEL_INFO["clarity"],
            "endpoint": self.endpoint
        }