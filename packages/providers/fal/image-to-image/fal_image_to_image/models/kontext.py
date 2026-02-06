"""
FLUX Kontext model implementations
"""

from typing import Dict, Any, Optional, List
from .base import BaseModel
from ..utils.validators import (
    validate_inference_steps, validate_guidance_scale, 
    validate_aspect_ratio, validate_num_images, validate_safety_tolerance
)
from ..config.constants import MODEL_INFO, DEFAULT_VALUES


class KontextModel(BaseModel):
    """FLUX Kontext Dev model for contextual image editing."""

    MODEL_KEY = "kontext"

    def __init__(self):
        """Initialize the FLUX Kontext model."""
        super().__init__("kontext")
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kontext Dev parameters."""
        defaults = DEFAULT_VALUES["kontext"]
        
        num_inference_steps = kwargs.get("num_inference_steps", defaults["num_inference_steps"])
        guidance_scale = kwargs.get("guidance_scale", defaults["guidance_scale"])
        resolution_mode = kwargs.get("resolution_mode", defaults["resolution_mode"])
        enable_safety_checker = kwargs.get("enable_safety_checker", False)
        seed = kwargs.get("seed", None)
        
        num_inference_steps = validate_inference_steps(num_inference_steps)
        guidance_scale = validate_guidance_scale(guidance_scale, "kontext")
        resolution_mode = validate_aspect_ratio(resolution_mode, "kontext")
        
        return {
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "resolution_mode": resolution_mode,
            "enable_safety_checker": enable_safety_checker,
            "seed": seed
        }
    
    def prepare_arguments(self, prompt: str, image_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kontext Dev."""
        arguments = {
            "prompt": prompt,
            "image_url": image_url,
            "num_inference_steps": kwargs["num_inference_steps"],
            "guidance_scale": kwargs["guidance_scale"],
            "resolution_mode": kwargs["resolution_mode"],
            "enable_safety_checker": kwargs["enable_safety_checker"]
        }
        
        if kwargs.get("seed") is not None:
            arguments["seed"] = kwargs["seed"]
        
        return arguments
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Kontext Dev model information."""
        return {
            **MODEL_INFO["kontext"],
            "endpoint": self.endpoint
        }


class KontextMultiModel(BaseModel):
    """FLUX Kontext [max] Multi model for multi-image processing."""

    MODEL_KEY = "kontext_multi"

    def __init__(self):
        """Initialize the FLUX Kontext Multi model."""
        super().__init__("kontext_multi")
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kontext Multi parameters."""
        guidance_scale = kwargs.get("guidance_scale", 3.5)
        num_images = kwargs.get("num_images", 1)
        aspect_ratio = kwargs.get("aspect_ratio", "1:1")
        safety_tolerance = kwargs.get("safety_tolerance", 6)
        output_format = kwargs.get("output_format", "jpeg")
        sync_mode = kwargs.get("sync_mode", True)
        seed = kwargs.get("seed", None)
        
        guidance_scale = validate_guidance_scale(guidance_scale, "kontext")
        num_images = validate_num_images(num_images)
        aspect_ratio = validate_aspect_ratio(aspect_ratio, "kontext_multi")
        safety_tolerance = validate_safety_tolerance(safety_tolerance)
        
        return {
            "guidance_scale": guidance_scale,
            "num_images": num_images,
            "aspect_ratio": aspect_ratio,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
            "sync_mode": sync_mode,
            "seed": seed
        }
    
    def prepare_arguments(self, prompt: str, image_urls: List[str], **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kontext Multi."""
        arguments = {
            "prompt": prompt,
            "image_urls": image_urls,
            "guidance_scale": kwargs["guidance_scale"],
            "num_images": kwargs["num_images"],
            "aspect_ratio": kwargs["aspect_ratio"],
            "safety_tolerance": str(kwargs["safety_tolerance"]),
            "output_format": kwargs["output_format"],
            "sync_mode": kwargs["sync_mode"]
        }
        
        if kwargs.get("seed") is not None:
            arguments["seed"] = kwargs["seed"]
        
        return arguments
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Kontext Multi model information."""
        return {
            **MODEL_INFO["kontext_multi"],
            "endpoint": self.endpoint
        }