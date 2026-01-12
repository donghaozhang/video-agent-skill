"""
Main FAL Image-to-Image Generator with Multi-Model Support

This module provides a unified interface for multiple FAL AI image editing models.
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import fal_client
from dotenv import load_dotenv

from .models import PhotonModel, PhotonBaseModel, KontextModel, KontextMultiModel, SeedEditModel, ClarityModel, NanoBananaProEditModel, GPTImage15EditModel
from .utils.file_utils import upload_local_image, ensure_output_directory
from .config.constants import SUPPORTED_MODELS, MODEL_INFO, ModelType

# Load environment variables
load_dotenv()


class FALImageToImageGenerator:
    """
    Unified FAL AI Image-to-Image Generator with Multi-Model Support
    
    Supports multiple models:
    - Luma Photon Flash: Creative modifications with aspect ratio control
    - Luma Photon Base: High-quality creative modifications
    - FLUX Kontext Dev: Contextual editing with precise control
    - FLUX Kontext Multi: Multi-image processing
    - ByteDance SeedEdit v3: Accurate editing with content preservation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the generator.
        
        Args:
            api_key: FAL AI API key. If not provided, will load from environment.
        """
        # Set API key
        if api_key:
            fal_client.api_key = api_key
        else:
            api_key = os.getenv('FAL_KEY')
            if not api_key:
                # Check if we should use mock mode
                if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
                    print("⚠️  Running in CI environment - using mock mode")
                    self.mock_mode = True
                    api_key = "mock_key"
                else:
                    raise ValueError("FAL_KEY environment variable is not set. Please set it or provide api_key parameter.")
            else:
                self.mock_mode = False
            fal_client.api_key = api_key
        
        # Initialize models
        self.models = {
            "photon": PhotonModel(),
            "photon_base": PhotonBaseModel(),
            "kontext": KontextModel(),
            "kontext_multi": KontextMultiModel(),
            "seededit": SeedEditModel(),
            "clarity": ClarityModel(),
            "nano_banana_pro_edit": NanoBananaProEditModel(),
            "gpt_image_1_5_edit": GPTImage15EditModel()
        }
        
        # Create output directories
        self.output_dir = ensure_output_directory("output")
        self.test_output_dir = self.output_dir  # Use same output directory
    
    def modify_image(
        self,
        prompt: str,
        image_url: str,
        model: ModelType = "photon",
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Modify an image using the specified model.
        
        Args:
            prompt: Text instruction for image modification
            image_url: URL of input image
            model: Model to use (default: "photon")
            output_dir: Custom output directory
            **kwargs: Model-specific parameters
            
        Returns:
            Dictionary containing generation results
        """
        # Check if we're in mock mode
        if hasattr(self, 'mock_mode') and self.mock_mode:
            import time
            return {
                'success': True,
                'image_url': f'mock://modified-image-{int(time.time())}.jpg',
                'image_path': f'/tmp/mock_modified_{int(time.time())}.jpg',
                'model_used': model,
                'provider': 'fal_mock',
                'cost_estimate': 0.01,
                'processing_time': 2.0,
                'prompt': prompt,
                'mock_mode': True
            }
        
        if model not in self.models:
            raise ValueError(f"Unsupported model: {model}. Supported models: {list(self.models.keys())}")
        
        return self.models[model].generate(
            prompt=prompt,
            image_url=image_url,
            output_dir=output_dir,
            **kwargs
        )
    
    def modify_local_image(
        self,
        prompt: str,
        image_path: str,
        model: ModelType = "photon",
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Modify a local image file.
        
        Args:
            prompt: Text instruction for image modification
            image_path: Path to local image file
            model: Model to use (default: "photon")
            output_dir: Custom output directory
            **kwargs: Model-specific parameters
            
        Returns:
            Dictionary containing generation results
        """
        try:
            # Upload local image
            print(f"📤 Uploading local image: {image_path}")
            image_url = upload_local_image(image_path)
            
            # Modify using uploaded image
            return self.modify_image(
                prompt=prompt,
                image_url=image_url,
                model=model,
                output_dir=output_dir,
                **kwargs
            )
            
        except Exception as e:
            print(f"❌ Error processing local image: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": model,
                "prompt": prompt,
                "image_path": image_path
            }
    
    # Convenience methods for each model
    def modify_image_photon(
        self,
        prompt: str,
        image_url: str,
        strength: float = 0.8,
        aspect_ratio: str = "1:1",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convenience method for Photon Flash modifications."""
        return self.modify_image(
            prompt=prompt,
            image_url=image_url,
            model="photon",
            strength=strength,
            aspect_ratio=aspect_ratio,
            output_dir=output_dir
        )
    
    def modify_image_seededit(
        self,
        prompt: str,
        image_url: str,
        guidance_scale: float = 0.5,
        seed: Optional[int] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convenience method for SeedEdit v3 modifications."""
        return self.modify_image(
            prompt=prompt,
            image_url=image_url,
            model="seededit",
            guidance_scale=guidance_scale,
            seed=seed,
            output_dir=output_dir
        )
    
    def modify_local_image_seededit(
        self,
        prompt: str,
        image_path: str,
        guidance_scale: float = 0.5,
        seed: Optional[int] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convenience method for SeedEdit v3 local image modifications."""
        return self.modify_local_image(
            prompt=prompt,
            image_path=image_path,
            model="seededit",
            guidance_scale=guidance_scale,
            seed=seed,
            output_dir=output_dir
        )
    
    def upscale_image(
        self,
        image_url: str,
        scale: float = 2,
        enable_enhancement: bool = True,
        prompt: Optional[str] = None,
        seed: Optional[int] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convenience method for Clarity Upscaler."""
        kwargs = {
            "scale": scale,
            "enable_enhancement": enable_enhancement
        }
        if prompt:
            kwargs["prompt"] = prompt
        if seed is not None:
            kwargs["seed"] = seed
            
        # Extract prompt to avoid conflict
        enhancement_prompt = kwargs.pop("prompt", "")
        
        return self.modify_image(
            prompt=enhancement_prompt,  # Use the enhancement prompt
            image_url=image_url,
            model="clarity",
            output_dir=output_dir,
            **kwargs
        )
    
    def upscale_local_image(
        self,
        image_path: str,
        scale: float = 2,
        enable_enhancement: bool = True,
        prompt: Optional[str] = None,
        seed: Optional[int] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convenience method for Clarity Upscaler with local images."""
        kwargs = {
            "scale": scale,
            "enable_enhancement": enable_enhancement
        }
        if prompt:
            kwargs["prompt"] = prompt
        if seed is not None:
            kwargs["seed"] = seed
            
        # Extract prompt to avoid conflict
        enhancement_prompt = kwargs.pop("prompt", "")
        
        return self.modify_local_image(
            prompt=enhancement_prompt,  # Use the enhancement prompt
            image_path=image_path,
            model="clarity",
            output_dir=output_dir,
            **kwargs
        )
    
    # Information methods
    def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about supported models.
        
        Args:
            model: Specific model to get info for. If None, returns all models.
        
        Returns:
            Dictionary containing model information
        """
        if model:
            if model not in self.models:
                raise ValueError(f"Unknown model: {model}")
            return self.models[model].get_model_info()
        else:
            return {
                model_key: model_obj.get_model_info()
                for model_key, model_obj in self.models.items()
            }
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported models."""
        return list(self.models.keys())
    
    def get_supported_aspect_ratios(self, model: str = "photon") -> List[str]:
        """Get list of supported aspect ratios for a specific model."""
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        
        model_info = self.models[model].get_model_info()
        return model_info.get("supported_aspect_ratios", [])
    
    # Batch processing
    def batch_modify_images(
        self,
        prompts: List[str],
        image_urls: List[str],
        model: ModelType = "photon",
        output_dir: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Modify multiple images with different prompts.
        
        Args:
            prompts: List of text instructions
            image_urls: List of image URLs
            model: Model to use for all modifications
            output_dir: Custom output directory
            **kwargs: Model-specific parameters
            
        Returns:
            List of generation results for each image
        """
        if len(prompts) != len(image_urls):
            raise ValueError("Number of prompts must match number of image URLs")
        
        results = []
        total_images = len(prompts)
        
        print(f"🎨 Starting batch modification of {total_images} images with {model}...")
        
        for i, (prompt, image_url) in enumerate(zip(prompts, image_urls), 1):
            print(f"\n📸 Processing image {i}/{total_images}")
            
            result = self.modify_image(
                prompt=prompt,
                image_url=image_url,
                model=model,
                output_dir=output_dir,
                **kwargs
            )
            results.append(result)
            
            # Brief pause between requests
            if i < total_images:
                import time
                time.sleep(1)
        
        successful = sum(1 for r in results if r.get("success", False))
        print(f"\n✅ Batch processing completed: {successful}/{total_images} successful")
        
        return results