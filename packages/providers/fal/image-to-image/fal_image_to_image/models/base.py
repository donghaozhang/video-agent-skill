"""
Base model interface for FAL Image-to-Image models
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import fal_client

from ..utils.file_utils import download_images, ensure_output_directory
from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # side-effect: registers models


class BaseModel(ABC):
    """
    Abstract base class for all FAL Image-to-Image models.
    """

    def __init__(self, model_key: str):
        """
        Initialize base model.

        Args:
            model_key: Model identifier (e.g., "photon", "seededit")
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
    def prepare_arguments(self, prompt: str, image_url: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare API arguments for the model.
        
        Args:
            prompt: Text instruction for image modification
            image_url: URL of input image
            **kwargs: Model-specific parameters
            
        Returns:
            Dictionary of API arguments
        """
        pass
    
    def process_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process API response and extract images.
        
        Args:
            response: Raw API response
            
        Returns:
            List of image dictionaries
        """
        images = []
        
        # Handle different response formats
        if "images" in response:
            # Standard format (Photon, Kontext)
            images = response["images"]
        elif "image" in response:
            # SeedEdit v3 format (single image object)
            images = [response["image"]]
        
        return images
    
    def generate(
        self,
        prompt: str,
        image_url: str,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate modified image using the model.
        
        Args:
            prompt: Text instruction for image modification
            image_url: URL of input image
            output_dir: Custom output directory
            **kwargs: Model-specific parameters
            
        Returns:
            Dictionary containing generation results
        """
        try:
            # Validate parameters
            validated_params = self.validate_parameters(**kwargs)
            
            # Prepare API arguments
            arguments = self.prepare_arguments(prompt, image_url, **validated_params)
            
            # Log generation info
            self._log_generation_start(prompt, **validated_params)
            
            # Make API call
            start_time = time.time()
            response = fal_client.subscribe(self.endpoint, arguments=arguments)
            processing_time = time.time() - start_time
            
            print(f"✅ Generation completed in {processing_time:.2f} seconds")
            
            # Process response
            images = self.process_response(response)
            if not images:
                raise Exception("No images generated")
            
            # Download images
            output_directory = ensure_output_directory(output_dir)
            downloaded_files = download_images(images, output_directory)
            
            # Build result dictionary
            result = {
                "success": True,
                "model": self.display_name,
                "prompt": prompt,
                "processing_time": processing_time,
                "images": images,
                "downloaded_files": downloaded_files,
                "output_directory": str(output_directory)
            }
            
            # Add model-specific parameters
            result.update(validated_params)
            
            return result
            
        except Exception as e:
            print(f"❌ Error during image modification: {e}")
            
            error_result = {
                "success": False,
                "error": str(e),
                "model": self.display_name,
                "prompt": prompt
            }
            
            # Add model-specific parameters to error response
            try:
                validated_params = self.validate_parameters(**kwargs)
                error_result.update(validated_params)
            except:
                pass
            
            return error_result
    
    def _log_generation_start(self, prompt: str, **params):
        """Log generation start with parameters."""
        print(f"🎨 Modifying image with {self.display_name}...")
        print(f"   Prompt: {prompt}")
        
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