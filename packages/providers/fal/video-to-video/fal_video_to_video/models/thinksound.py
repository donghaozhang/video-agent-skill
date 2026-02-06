"""
ThinkSound model implementation
"""

from typing import Dict, Any, Optional
from .base import BaseModel
from ..utils.validators import validate_prompt, validate_seed
from ..config.constants import MODEL_INFO, DEFAULT_VALUES


class ThinkSoundModel(BaseModel):
    """ThinkSound model for AI-powered video audio generation."""

    MODEL_KEY = "thinksound"

    def __init__(self):
        super().__init__("thinksound")
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate ThinkSound parameters."""
        defaults = DEFAULT_VALUES["thinksound"]
        
        prompt = kwargs.get("prompt", defaults["prompt"])
        seed = kwargs.get("seed", defaults["seed"])
        
        prompt = validate_prompt(prompt)
        seed = validate_seed(seed)
        
        result = {}
        if prompt is not None:
            result["prompt"] = prompt
        if seed is not None:
            result["seed"] = seed
        
        return result
    
    def prepare_arguments(self, video_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for ThinkSound."""
        args = {
            "video_url": video_url
        }
        
        # Add optional parameters
        if "prompt" in kwargs:
            args["prompt"] = kwargs["prompt"]
        if "seed" in kwargs:
            args["seed"] = kwargs["seed"]
        
        return args
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get ThinkSound model information."""
        return {
            **MODEL_INFO["thinksound"],
            "endpoint": self.endpoint
        }