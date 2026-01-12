"""
Image-to-Image model integration for AI Content Pipeline
"""

import os
import sys
import time
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ImageToImageResult:
    """Result from image-to-image generation."""
    success: bool
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    model_used: Optional[str] = None
    cost_estimate: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UnifiedImageToImageGenerator:
    """
    Unified image-to-image generator for the AI Content Pipeline.
    
    Integrates with the existing FAL Image-to-Image implementation.
    """
    
    def __init__(self):
        """Initialize the image-to-image generator."""
        self.generator = None
        self._initialize_generator()
    
    def _initialize_generator(self):
        """Initialize the FAL Image-to-Image generator."""
        try:
            # Add the fal_image_to_image directory to Python path
            fal_image_to_image_path = Path(__file__).parent.parent.parent.parent.parent / "providers" / "fal" / "image-to-image"
            if fal_image_to_image_path.exists():
                sys.path.insert(0, str(fal_image_to_image_path))
                from fal_image_to_image.generator import FALImageToImageGenerator
                self.generator = FALImageToImageGenerator()
                print("✅ FAL Image-to-Image generator initialized")
            else:
                print("❌ FAL Image-to-Image directory not found at:", fal_image_to_image_path)
                self.generator = None
        except Exception as e:
            print(f"❌ Failed to initialize FAL Image-to-Image generator: {e}")
            self.generator = None
    
    def get_available_models(self) -> list:
        """Get list of available models."""
        return [
            "photon_flash",
            "photon_base",
            "flux_kontext",
            "flux_kontext_multi",
            "seededit_v3",
            "clarity_upscaler",
            "nano_banana_pro_edit",
            "gpt_image_1_5_edit"
        ]
    
    def generate(self, 
                 source_image: str,
                 prompt: str,
                 model: str = "photon_flash",
                 output_dir: str = "output",
                 **kwargs) -> ImageToImageResult:
        """
        Generate modified image from source image.
        
        Args:
            source_image: Path to source image or URL
            prompt: Text prompt for modification
            model: Model to use
            output_dir: Output directory
            **kwargs: Additional model-specific parameters
            
        Returns:
            ImageToImageResult with generation results
        """
        start_time = time.time()
        
        if not self.generator:
            return ImageToImageResult(
                success=False,
                error="FAL Image-to-Image generator not available"
            )
        
        try:
            print(f"🎨 Generating modified image with {model} model...")
            print(f"📝 Prompt: {prompt}")
            print(f"🖼️ Source image: {source_image}")
            
            # Map model names to FAL generator model types
            model_mapping = {
                "photon_flash": "photon",
                "photon_base": "photon_base",
                "flux_kontext": "kontext",
                "flux_kontext_multi": "kontext_multi",
                "seededit_v3": "seededit",
                "clarity_upscaler": "clarity",
                "nano_banana_pro_edit": "nano_banana_pro_edit",
                "gpt_image_1_5_edit": "gpt_image_1_5_edit"
            }
            
            if model not in model_mapping:
                return ImageToImageResult(
                    success=False,
                    error=f"Unsupported model: {model}"
                )
            
            # Use the correct method based on input type
            if source_image.startswith(('http://', 'https://')):
                # Remote image URL
                result = self.generator.modify_image(
                    prompt=prompt,
                    image_url=source_image,
                    model=model_mapping[model],
                    output_dir=output_dir,
                    **{k: v for k, v in kwargs.items() if k not in ['prompt', 'source_image', 'model', 'output_dir']}
                )
            else:
                # Local image path
                result = self.generator.modify_local_image(
                    prompt=prompt,
                    image_path=source_image,
                    model=model_mapping[model],
                    output_dir=output_dir,
                    **{k: v for k, v in kwargs.items() if k not in ['prompt', 'source_image', 'model', 'output_dir']}
                )
            
            processing_time = time.time() - start_time
            
            if result and result.get("success", False):
                # Extract output paths and URLs from FAL result
                output_path = None
                output_url = None
                
                # Get local file path
                if result.get("downloaded_files"):
                    output_path = result["downloaded_files"][0]
                
                # Get remote URL
                if result.get("images") and len(result["images"]) > 0:
                    output_url = result["images"][0].get("url")
                
                return ImageToImageResult(
                    success=True,
                    output_path=output_path,
                    output_url=output_url,
                    model_used=model,
                    cost_estimate=result.get("cost_estimate", 0.02),
                    processing_time=processing_time,
                    metadata=result
                )
            else:
                return ImageToImageResult(
                    success=False,
                    error=result.get("error", "Generation failed"),
                    processing_time=processing_time
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            return ImageToImageResult(
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        model_info = {
            "photon_flash": {
                "name": "Luma Photon Flash",
                "provider": "Luma AI",
                "best_for": "Creative modifications, fast generation",
                "cost_per_image": "$0.02"
            },
            "photon_base": {
                "name": "Luma Photon Base", 
                "provider": "Luma AI",
                "best_for": "High-quality creative modifications",
                "cost_per_image": "$0.03"
            },
            "flux_kontext": {
                "name": "FLUX Kontext Dev",
                "provider": "Black Forest Labs",
                "best_for": "Contextual editing with precise control",
                "cost_per_image": "$0.025"
            },
            "flux_kontext_multi": {
                "name": "FLUX Kontext Multi",
                "provider": "Black Forest Labs", 
                "best_for": "Multi-image processing",
                "cost_per_image": "$0.04"
            },
            "seededit_v3": {
                "name": "ByteDance SeedEdit v3",
                "provider": "ByteDance",
                "best_for": "Precise editing with content preservation",
                "cost_per_image": "$0.02"
            },
            "clarity_upscaler": {
                "name": "Clarity AI Upscaler",
                "provider": "Clarity AI",
                "best_for": "Image upscaling and enhancement",
                "cost_per_image": "$0.05"
            },
            "nano_banana_pro_edit": {
                "name": "Nano Banana Pro Edit",
                "provider": "FAL AI",
                "best_for": "Fast image editing, cost-effective",
                "cost_per_image": "$0.015"
            },
            "gpt_image_1_5_edit": {
                "name": "GPT Image 1.5 Edit",
                "provider": "FAL AI",
                "best_for": "GPT-powered editing, natural language",
                "cost_per_image": "$0.02"
            }
        }

        return model_info.get(model)