"""
Topaz Video Upscale model implementation
"""

from typing import Dict, Any, Optional
from .base import BaseModel
from ..utils.validators import validate_upscale_factor, validate_target_fps
from ..config.constants import MODEL_INFO, DEFAULT_VALUES


class TopazModel(BaseModel):
    """Topaz Video Upscale model for professional-grade video enhancement."""

    MODEL_KEY = "topaz"

    def __init__(self):
        """Initialize the Topaz video upscaling model."""
        super().__init__("topaz")
    
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Topaz parameters."""
        defaults = DEFAULT_VALUES["topaz"]
        
        upscale_factor = kwargs.get("upscale_factor", defaults["upscale_factor"])
        target_fps = kwargs.get("target_fps", defaults["target_fps"])
        
        upscale_factor = validate_upscale_factor(upscale_factor)
        target_fps = validate_target_fps(target_fps)
        
        result = {
            "upscale_factor": upscale_factor
        }
        
        if target_fps is not None:
            result["target_fps"] = target_fps
        
        return result
    
    def prepare_arguments(self, video_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Topaz."""
        args = {
            "video_url": video_url,
            "upscale_factor": kwargs["upscale_factor"]
        }
        
        # Add optional parameters
        if "target_fps" in kwargs:
            args["target_fps"] = kwargs["target_fps"]
        
        return args
    
    def generate(
        self,
        video_url: str,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate upscaled video using Topaz.
        Override base method since Topaz doesn't use prompts.
        """
        try:
            # Validate parameters
            validated_params = self.validate_parameters(**kwargs)
            
            # Prepare API arguments
            arguments = self.prepare_arguments(video_url, **validated_params)
            
            # Log generation info
            print(f"🔍 Upscaling video with {self.display_name}...")
            for key, value in validated_params.items():
                if value is not None:
                    formatted_key = key.replace('_', ' ').title()
                    print(f"   {formatted_key}: {value}")
            
            # Make API call
            import time
            start_time = time.time()
            import fal_client
            response = fal_client.subscribe(self.endpoint, arguments=arguments)
            processing_time = time.time() - start_time
            
            print(f"✅ Upscaling completed in {processing_time:.2f} seconds")
            
            # Process response
            processed_response = self.process_response(response)
            
            # Download video if URL is present
            downloaded_path = None
            if "video_url" in processed_response:
                from ..utils.file_utils import download_video, ensure_output_directory
                output_directory = ensure_output_directory(output_dir)
                downloaded_path = download_video(
                    processed_response["video_url"], 
                    output_directory
                )
            
            # Build result dictionary
            result = {
                "success": True,
                "model": self.display_name,
                "processing_time": processing_time,
                "response": processed_response,
                "output_directory": str(ensure_output_directory(output_dir))
            }
            
            if downloaded_path:
                result["local_path"] = downloaded_path
            
            # Add model-specific parameters
            result.update(validated_params)
            
            return result
            
        except Exception as e:
            print(f"❌ Error during video upscaling: {e}")
            
            error_result = {
                "success": False,
                "error": str(e),
                "model": self.display_name,
                "video_url": video_url
            }
            
            # Add model-specific parameters to error response
            try:
                validated_params = self.validate_parameters(**kwargs)
                error_result.update(validated_params)
            except:
                pass
            
            return error_result
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Topaz model information."""
        return {
            **MODEL_INFO["topaz"],
            "endpoint": self.endpoint
        }