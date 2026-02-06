"""
Base model interface for FAL Video to Video models
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import fal_client

from ..utils.file_utils import download_video, ensure_output_directory
from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # side-effect: registers models


class BaseModel(ABC):
    """
    Abstract base class for all FAL Video to Video models.
    """

    def __init__(self, model_key: str):
        """
        Initialize base model.

        Args:
            model_key: Model identifier (e.g., "thinksound")
        """
        self.model_key = model_key
        self._definition = ModelRegistry.get(model_key)
        self.endpoint = self._definition.endpoint
        self.display_name = self._definition.name
    
    @abstractmethod
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate model-specific parameters.
        
        Returns:
            Dictionary of validated parameters
            
        Raises:
            ValueError: If parameters are invalid
        """
        pass
    
    @abstractmethod
    def prepare_arguments(self, video_url: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare API arguments for the model.
        
        Args:
            video_url: URL of input video
            **kwargs: Model-specific parameters
            
        Returns:
            Dictionary of API arguments
        """
        pass
    
    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process API response and extract video.
        
        Args:
            response: Raw API response
            
        Returns:
            Processed response with video information
        """
        # Handle response format
        if "video" in response:
            video_info = response["video"]
            if isinstance(video_info, str):
                # Simple URL string
                response["video_url"] = video_info
            elif isinstance(video_info, dict) and "url" in video_info:
                # Video object with URL
                response["video_url"] = video_info["url"]
        
        return response
    
    def generate(
        self,
        video_url: str,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate audio for video using the model.
        
        Args:
            video_url: URL of input video
            output_dir: Custom output directory
            **kwargs: Model-specific parameters
            
        Returns:
            Dictionary containing generation results
        """
        try:
            # Validate parameters
            validated_params = self.validate_parameters(**kwargs)
            
            # Prepare API arguments
            arguments = self.prepare_arguments(video_url, **validated_params)
            
            # Log generation info
            self._log_generation_start(**validated_params)
            
            # Make API call
            start_time = time.time()
            response = fal_client.subscribe(self.endpoint, arguments=arguments)
            processing_time = time.time() - start_time
            
            print(f"✅ Generation completed in {processing_time:.2f} seconds")
            
            # Process response
            processed_response = self.process_response(response)
            
            # Download video if URL is present
            downloaded_path = None
            if "video_url" in processed_response:
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
            print(f"❌ Error during audio generation: {e}")
            
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
    
    def _log_generation_start(self, **params):
        """Log generation start with parameters."""
        print(f"🎵 Generating audio with {self.display_name}...")
        
        # Log model-specific parameters
        for key, value in params.items():
            if value is not None:
                formatted_key = key.replace('_', ' ').title()
                print(f"   {formatted_key}: {value}")
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information and capabilities.
        
        Returns:
            Dictionary containing model information
        """
        pass