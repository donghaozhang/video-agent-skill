"""
ByteDance SeedEdit v3 model implementation
"""

from typing import Dict, Any, Optional
from .base import BaseModel
from ..utils.validators import validate_guidance_scale
from ..config.constants import MODEL_INFO, DEFAULT_VALUES


class SeedEditModel(BaseModel):
    """
    ByteDance SeedEdit v3 model for accurate image editing with content preservation.
    """

    MODEL_KEY = "seededit"

    def __init__(self):
        super().__init__("seededit")
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate SeedEdit v3 parameters.
        
        Returns:
            Dictionary of validated parameters
        """
        # Get default values
        defaults = DEFAULT_VALUES["seededit"]
        
        # Extract parameters with defaults
        guidance_scale = kwargs.get("guidance_scale", defaults["guidance_scale"])
        seed = kwargs.get("seed", None)
        
        # Validate guidance scale
        guidance_scale = validate_guidance_scale(guidance_scale, "seededit")
        
        return {
            "guidance_scale": guidance_scale,
            "seed": seed
        }
    
    def prepare_arguments(self, prompt: str, image_url: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare API arguments for SeedEdit v3.
        
        Args:
            prompt: Text instruction for image editing
            image_url: URL of input image
            **kwargs: Validated parameters
            
        Returns:
            Dictionary of API arguments
        """
        arguments = {
            "prompt": prompt,
            "image_url": image_url,
            "guidance_scale": kwargs["guidance_scale"]
        }
        
        # Add optional seed
        if kwargs.get("seed") is not None:
            arguments["seed"] = kwargs["seed"]
        
        return arguments
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get SeedEdit v3 model information.
        
        Returns:
            Dictionary containing model information
        """
        return {
            **MODEL_INFO["seededit"],
            "endpoint": self.endpoint
        }
    
    def modify_image(
        self,
        prompt: str,
        image_url: str,
        guidance_scale: float = 0.5,
        seed: Optional[int] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convenience method for SeedEdit v3 image modification.
        
        Args:
            prompt: Text instruction for image editing
            image_url: URL of input image
            guidance_scale: Controls adherence to prompt (0.0-1.0, default: 0.5)
            seed: Random seed for reproducible results
            output_dir: Custom output directory
            
        Returns:
            Dictionary containing generation results
        """
        return self.generate(
            prompt=prompt,
            image_url=image_url,
            guidance_scale=guidance_scale,
            seed=seed,
            output_dir=output_dir
        )