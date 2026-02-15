#!/usr/bin/env python3
"""
Replicate Text-to-Image Generator

This module provides text-to-image generation using Replicate models,
starting with ByteDance Seedream-3.

Supported Models:
1. ByteDance Seedream-3 - High-resolution (up to 2048px) text-to-image model
"""

import os
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Union, Literal
from dotenv import load_dotenv
from enum import Enum

try:
    import replicate
except (ImportError, Exception):
    replicate = None


class ReplicateTextToImageModel(Enum):
    """Available Replicate text-to-image models."""
    SEEDREAM3 = "bytedance/seedream-3"


# Type definitions
AspectRatio = Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]
ImageSize = Literal["small", "regular", "big"]


class ReplicateTextToImageGenerator:
    """
    Replicate Text-to-Image Generator supporting multiple models.
    
    Provides high-quality image generation with various customization options
    and transparent cost tracking.
    """
    
    # Model configurations
    MODEL_CONFIGS = {
        ReplicateTextToImageModel.SEEDREAM3: {
            "name": "ByteDance Seedream-3",
            "version": "3.0",
            "resolution": "Up to 2048px",
            "cost_per_image": 0.003,  # Estimated cost
            "features": [
                "High-resolution generation (up to 2048px)",
                "Custom width/height (512-2048px)",
                "Multiple aspect ratios",
                "CPU-based processing",
                "Native high-resolution output",
                "Guidance scale control",
                "Seed support for reproducibility"
            ]
        }
    }
    
    def __init__(self, api_token: Optional[str] = None, verbose: bool = True):
        """
        Initialize the Replicate Text-to-Image Generator.
        
        Args:
            api_token (str, optional): Replicate API token. If not provided, loads from environment.
            verbose (bool): Enable verbose output. Defaults to True.
        """
        self.verbose = verbose
        
        # Load environment variables
        load_dotenv()
        
        # Set API token
        self.api_token = api_token or os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError(
                "Replicate API token not found. Please set REPLICATE_API_TOKEN environment variable "
                "or pass api_token parameter. Get your token from: https://replicate.com/account/api-tokens"
            )
        
        # Configure replicate client
        os.environ['REPLICATE_API_TOKEN'] = self.api_token
        
        # Create output directory
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        if self.verbose:
            print("🎨 Replicate Text-to-Image Generator initialized")
            print(f"📁 Output directory: {self.output_dir.absolute()}")
    
    def calculate_cost(self, model: ReplicateTextToImageModel, num_images: int = 1) -> float:
        """
        Calculate the cost for image generation.
        
        Args:
            model (ReplicateTextToImageModel): Which model to use
            num_images (int): Number of images to generate
        
        Returns:
            float: Cost in USD
        """
        config = self.MODEL_CONFIGS[model]
        return config["cost_per_image"] * num_images
    
    def generate_image(
        self,
        prompt: str,
        model: ReplicateTextToImageModel = ReplicateTextToImageModel.SEEDREAM3,
        # Seedream-3 specific options
        aspect_ratio: AspectRatio = "16:9",
        guidance_scale: float = 2.5,
        seed: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        # Common options
        output_filename: Optional[str] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Generate an image from text description.
        
        Args:
            prompt (str): Text description for image generation
            model (ReplicateTextToImageModel): Which model to use
            # Seedream-3 options:
            aspect_ratio (AspectRatio): Image aspect ratio
            guidance_scale (float): How closely to follow the prompt (1.0-10.0)
            seed (int, optional): Seed for reproducibility
            width (int, optional): Image width in pixels (512-2048)
            height (int, optional): Image height in pixels (512-2048)
            # Common options:
            output_filename (str, optional): Custom output filename
            timeout (int): Maximum time to wait for generation
        
        Returns:
            Dict[str, Any]: Generation result with image URL, local path, cost, and metadata
        """
        # Calculate cost
        cost = self.calculate_cost(model)
        
        if self.verbose:
            config = self.MODEL_CONFIGS[model]
            print(f"🎨 Generating image with {config['name']}...")
            print(f"📝 Prompt: {prompt}")
            print(f"💰 Estimated cost: ${cost:.3f}")
            print(f"📐 Aspect ratio: {aspect_ratio}")
            print(f"🎯 Guidance scale: {guidance_scale}")
            if seed:
                print(f"🌱 Seed: {seed}")
            if width and height:
                print(f"📏 Size: {width}x{height}px")
        
        try:
            # Prepare request arguments based on model
            if model == ReplicateTextToImageModel.SEEDREAM3:
                input_args = {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "guidance_scale": guidance_scale
                }
                
                # Add optional parameters
                if seed is not None:
                    input_args["seed"] = seed
                if width is not None:
                    input_args["width"] = width
                if height is not None:
                    input_args["height"] = height
            
            else:
                raise ValueError(f"Unknown model: {model}")
            
            if self.verbose:
                print("🔄 Submitting generation request...")
            
            # Submit generation request
            output = replicate.run(
                model.value,
                input=input_args
            )
            
            if self.verbose:
                print("✅ Image generation completed!")
            
            # Handle output (Replicate returns URL or list of URLs)
            if isinstance(output, list):
                image_url = output[0] if output else None
            else:
                image_url = output
            
            if not image_url:
                raise Exception("No image URL in response")
            
            # Generate output filename if not provided
            if not output_filename:
                timestamp = int(time.time())
                safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_prompt = safe_prompt.replace(' ', '_')
                
                model_name = "seedream3" if model == ReplicateTextToImageModel.SEEDREAM3 else "unknown"
                
                output_filename = f"replicate_{model_name}_{safe_prompt}_{timestamp}.png"
            
            # Ensure .png extension
            if not output_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                output_filename += '.png'
            
            # Download image
            local_path = self._download_image(image_url, output_filename)
            
            # Prepare result
            generation_result = {
                'success': True,
                'image_url': image_url,
                'local_path': str(local_path),
                'filename': output_filename,
                'prompt': prompt,
                'model': model.value,
                'model_name': self.MODEL_CONFIGS[model]["name"],
                'provider': 'replicate',
                'cost_usd': cost,
                'aspect_ratio': aspect_ratio,
                'guidance_scale': guidance_scale,
                'seed': seed,
                'width': width,
                'height': height
            }
            
            if self.verbose:
                print(f"🖼️ Image saved: {local_path}")
                print(f"🔗 Original URL: {image_url}")
                print(f"💰 Actual cost: ${cost:.3f}")
            
            return generation_result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'prompt': prompt,
                'model': model.value,
                'provider': 'replicate',
                'estimated_cost': cost
            }
            
            if self.verbose:
                print(f"❌ Generation failed: {e}")
            
            return error_result
    
    def _download_image(self, url: str, filename: str) -> Path:
        """Download image from URL to local file."""
        local_path = self.output_dir / filename
        
        if self.verbose:
            print(f"⬇️ Downloading image: {filename}")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if self.verbose and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r⬇️ Downloading: {progress:.1f}%", end='', flush=True)
            
            if self.verbose:
                if total_size > 0:
                    print()  # New line after progress
                print(f"✅ Download completed: {local_path}")
            
            return local_path
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Download failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test the connection to Replicate API."""
        if self.verbose:
            print("🔍 Testing Replicate connection...")
        
        try:
            # Validate API token format (Replicate tokens start with 'r8_')
            if not self.api_token.startswith('r8_'):
                if self.verbose:
                    print("❌ Invalid API token format (should start with 'r8_')")
                return False
            
            # Test API connection with a simple call
            try:
                replicate.models.list()
                if self.verbose:
                    print("✅ API connection successful")
            except Exception as e:
                if self.verbose:
                    print(f"❌ API connection failed: {e}")
                return False
            
            if self.verbose:
                print("✅ API token format is valid")
                print("✅ replicate client is properly configured")
                print("⚠️ Note: Actual generation will incur costs:")
                print("   • ByteDance Seedream-3: ~$0.003 per image")
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Connection test failed: {e}")
            return False
    
    def get_model_info(self, model: Optional[ReplicateTextToImageModel] = None) -> Dict[str, Any]:
        """Get information about available models or a specific model."""
        if model is None:
            # Return info about all models
            return {
                'available_models': {
                    model.name: {
                        'endpoint': model.value,
                        **config
                    }
                    for model, config in self.MODEL_CONFIGS.items()
                }
            }
        else:
            # Return info about specific model
            config = self.MODEL_CONFIGS[model]
            return {
                'model_name': config['name'],
                'endpoint': model.value,
                **config
            }
    
    def print_model_comparison(self):
        """Print a comparison of available models."""
        print("🎨 Replicate Text-to-Image Models")
        print("=" * 60)
        
        for model, config in self.MODEL_CONFIGS.items():
            print(f"\n🖼️ {config['name']}")
            print("-" * 40)
            print(f"🔗 Endpoint: {model.value}")
            print(f"📐 Resolution: {config['resolution']}")
            print(f"💰 Cost: ${config['cost_per_image']:.3f} per image")
            
            print("✨ Features:")
            for feature in config['features']:
                print(f"  • {feature}")
        
        print(f"\n💡 Recommendation:")
        print("  • Use Seedream-3 for high-resolution, customizable image generation")
    
    def get_cost_estimate(self, model: ReplicateTextToImageModel, num_images: int = 1) -> str:
        """Get a formatted cost estimate."""
        cost = self.calculate_cost(model, num_images)
        model_name = self.MODEL_CONFIGS[model]["name"]
        
        if num_images == 1:
            return f"${cost:.3f} for 1 {model_name} image"
        else:
            return f"${cost:.3f} for {num_images} {model_name} images"


def main():
    """Example usage of Replicate Text-to-Image Generator."""
    print("🎨 Replicate Text-to-Image Generator Example")
    print("=" * 60)
    
    # Initialize generator
    try:
        generator = ReplicateTextToImageGenerator(verbose=True)
    except ValueError as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Print model comparison
    generator.print_model_comparison()
    
    # Test connection
    print("\n🔍 Testing connection...")
    if generator.test_connection():
        print("✅ Connection test passed!")
    else:
        print("❌ Connection test failed!")
        return
    
    # Show cost estimates
    print("\n💰 Cost Estimates:")
    print(f"  • {generator.get_cost_estimate(ReplicateTextToImageModel.SEEDREAM3, 1)}")
    print(f"  • {generator.get_cost_estimate(ReplicateTextToImageModel.SEEDREAM3, 5)}")
    print(f"  • {generator.get_cost_estimate(ReplicateTextToImageModel.SEEDREAM3, 10)}")
    
    print("\n⚠️ WARNING: Image generation incurs costs!")
    print("💡 Use test_replicate_integration.py to run actual generation tests")
    
    # Example usage (commented out to avoid costs):
    """
    # Generate with Seedream-3
    result = generator.generate_image(
        prompt="A majestic cat sitting on a windowsill, golden hour lighting, photorealistic",
        model=ReplicateTextToImageModel.SEEDREAM3,
        aspect_ratio="16:9",
        guidance_scale=3.0,
        seed=42
    )
    
    if result['success']:
        print(f"✅ Generated: {result['local_path']}")
    else:
        print(f"❌ Failed: {result['error']}")
    """


if __name__ == "__main__":
    main()