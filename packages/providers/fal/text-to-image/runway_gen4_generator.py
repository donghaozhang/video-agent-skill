#!/usr/bin/env python3
"""
Runway Gen4 Image Generator

This module provides text-to-image generation with multi-reference image guidance
using Runway's Gen-4 model via Replicate.

Key Features:
- High-quality text-to-image generation
- Support for up to 3 reference images with optional tagging
- Multiple resolution options (720p, 1080p)
- Various aspect ratios supported
- Advanced reference image guidance
"""

import os
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, Union, Literal, List
from dotenv import load_dotenv
from enum import Enum

try:
    import replicate
except (ImportError, Exception):
    replicate = None


class RunwayGen4Model(Enum):
    """Available Runway Gen4 models."""
    GEN4_IMAGE = "runwayml/gen4-image"


# Type definitions
AspectRatio = Literal["16:9", "9:16", "4:3", "3:4", "1:1", "21:9", "9:21"]
Resolution = Literal["720p", "1080p"]


class RunwayGen4Generator:
    """
    Runway Gen4 Image Generator with multi-reference image support.
    
    Provides advanced text-to-image generation with up to 3 reference images
    for precise visual guidance and control.
    """
    
    # Model configurations
    MODEL_CONFIGS = {
        RunwayGen4Model.GEN4_IMAGE: {
            "name": "Runway Gen-4 Image",
            "version": "4.0",
            "features": [
                "High-quality text-to-image generation",
                "Multi-reference image guidance (up to 3 images)",
                "Reference image tagging system",
                "720p and 1080p resolution options",
                "Multiple aspect ratio support",
                "Advanced prompt understanding",
                "Cinematic quality output"
            ],
            "cost_720p": 0.05,  # ~20 images per $1
            "cost_1080p": 0.08,  # ~12 images per $1
            "supported_resolutions": ["720p", "1080p"],
            "supported_ratios": ["16:9", "9:16", "4:3", "3:4", "1:1", "21:9", "9:21"],
            "max_reference_images": 3
        }
    }
    
    def __init__(self, api_token: Optional[str] = None, verbose: bool = True):
        """
        Initialize the Runway Gen4 Image Generator.
        
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
            print("🎬 Runway Gen4 Image Generator initialized")
            print(f"📁 Output directory: {self.output_dir.absolute()}")
    
    def calculate_cost(self, model: RunwayGen4Model, resolution: Resolution = "1080p", num_images: int = 1) -> float:
        """
        Calculate the cost for image generation.
        
        Args:
            model (RunwayGen4Model): Which model to use
            resolution (Resolution): Output resolution
            num_images (int): Number of images to generate
        
        Returns:
            float: Cost in USD
        """
        config = self.MODEL_CONFIGS[model]
        cost_per_image = config["cost_1080p"] if resolution == "1080p" else config["cost_720p"]
        return cost_per_image * num_images
    
    def _validate_reference_images(self, reference_images: Optional[List[str]], reference_tags: Optional[List[str]]) -> bool:
        """Validate reference images and tags."""
        if reference_images is None:
            return True
            
        if len(reference_images) > 3:
            raise ValueError("Maximum 3 reference images supported")
            
        if reference_tags and len(reference_tags) != len(reference_images):
            raise ValueError("Number of reference tags must match number of reference images")
            
        return True
    
    def _prepare_reference_images(self, reference_images: Optional[List[str]]) -> Optional[List[str]]:
        """
        Prepare reference images for API submission.
        
        Args:
            reference_images: List of file paths or URLs
            
        Returns:
            List of valid URLs or None
        """
        if not reference_images:
            return None
            
        prepared_images = []
        for img in reference_images:
            if img.startswith(('http://', 'https://')):
                # Already a URL
                prepared_images.append(img)
            elif img.startswith('data:'):
                # Data URI
                prepared_images.append(img)
            else:
                # Assume it's a local file path
                img_path = Path(img)
                if not img_path.exists():
                    raise ValueError(f"Reference image not found: {img}")
                
                # For now, we'll require URLs. In a production system,
                # you'd upload the image to a temporary hosting service
                raise ValueError(
                    f"Local file paths not yet supported for reference images. "
                    f"Please provide URLs or data URIs. File: {img}"
                )
        
        return prepared_images
    
    def generate_image(
        self,
        prompt: str,
        model: RunwayGen4Model = RunwayGen4Model.GEN4_IMAGE,
        # Gen4-specific options
        resolution: Resolution = "1080p",
        aspect_ratio: AspectRatio = "16:9",
        reference_images: Optional[List[str]] = None,
        reference_tags: Optional[List[str]] = None,
        seed: Optional[int] = None,
        # Common options
        output_filename: Optional[str] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Generate an image with optional reference image guidance.
        
        Args:
            prompt (str): Text description for image generation
            model (RunwayGen4Model): Which model to use
            # Gen4 options:
            resolution (Resolution): Output resolution (720p or 1080p)
            aspect_ratio (AspectRatio): Image aspect ratio
            reference_images (List[str], optional): Up to 3 reference image URLs
            reference_tags (List[str], optional): Tags for reference images
            seed (int, optional): Seed for reproducibility
            # Common options:
            output_filename (str, optional): Custom output filename
            timeout (int): Maximum time to wait for generation
        
        Returns:
            Dict[str, Any]: Generation result with image URL, local path, cost, and metadata
        """
        # Validate inputs
        self._validate_reference_images(reference_images, reference_tags)
        
        # Calculate cost
        cost = self.calculate_cost(model, resolution)
        
        if self.verbose:
            config = self.MODEL_CONFIGS[model]
            print(f"🎬 Generating image with {config['name']}...")
            print(f"📝 Prompt: {prompt}")
            print(f"💰 Estimated cost: ${cost:.3f}")
            print(f"📐 Resolution: {resolution}")
            print(f"📏 Aspect ratio: {aspect_ratio}")
            if reference_images:
                print(f"🖼️ Reference images: {len(reference_images)}")
                if reference_tags:
                    print(f"🏷️ Reference tags: {reference_tags}")
            if seed:
                print(f"🌱 Seed: {seed}")
        
        try:
            # Prepare reference images
            prepared_refs = self._prepare_reference_images(reference_images)
            
            # Prepare request arguments
            input_args = {
                "prompt": prompt,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio
            }
            
            # Add optional parameters
            if prepared_refs:
                input_args["reference_images"] = prepared_refs
            if reference_tags:
                input_args["reference_tags"] = reference_tags
            if seed is not None:
                input_args["seed"] = seed
            
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
                
                ref_suffix = f"_{len(reference_images)}refs" if reference_images else ""
                output_filename = f"runway_gen4_{safe_prompt}_{resolution}{ref_suffix}_{timestamp}.png"
            
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
                'resolution': resolution,
                'aspect_ratio': aspect_ratio,
                'reference_images': reference_images,
                'reference_tags': reference_tags,
                'seed': seed,
                'num_reference_images': len(reference_images) if reference_images else 0
            }
            
            if self.verbose:
                print(f"🖼️ Image saved: {local_path}")
                print(f"🔗 Original URL: {image_url}")
                print(f"💰 Actual cost: ${cost:.3f}")
                if reference_images:
                    print(f"🎯 Used {len(reference_images)} reference images")
            
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
            print("🔍 Testing Replicate connection for Runway Gen4...")
        
        try:
            # Validate API token format
            if not self.api_token.startswith('r8_'):
                if self.verbose:
                    print("❌ Invalid API token format (should start with 'r8_')")
                return False
            
            # Test API connection
            try:
                replicate.models.list()
                if self.verbose:
                    print("✅ API connection successful")
            except Exception as e:
                if self.verbose:
                    print(f"❌ API connection failed: {e}")
                return False
            
            if self.verbose:
                print("✅ Runway Gen4 integration ready")
                print("⚠️ Note: Actual generation will incur costs:")
                print("   • 720p: ~$0.05 per image (20 images per $1)")
                print("   • 1080p: ~$0.08 per image (12 images per $1)")
                print("   • Supports up to 3 reference images with tagging")
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Connection test failed: {e}")
            return False
    
    def get_model_info(self, model: Optional[RunwayGen4Model] = None) -> Dict[str, Any]:
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
        print("🎬 Runway Gen4 Image Models")
        print("=" * 60)
        
        for model, config in self.MODEL_CONFIGS.items():
            print(f"\n🖼️ {config['name']}")
            print("-" * 40)
            print(f"🔗 Endpoint: {model.value}")
            print(f"📐 Resolutions: {', '.join(config['supported_resolutions'])}")
            print(f"💰 Cost: ${config['cost_720p']:.3f} (720p) / ${config['cost_1080p']:.3f} (1080p)")
            print(f"🖼️ Reference images: Up to {config['max_reference_images']}")
            
            print("✨ Features:")
            for feature in config['features']:
                print(f"  • {feature}")
        
        print(f"\n💡 Key Advantages:")
        print("  • Multi-reference image guidance (unique capability)")
        print("  • Reference image tagging for precise control")
        print("  • High-quality cinematic output")
        print("  • Multiple resolution and aspect ratio options")
    
    def get_cost_estimate(self, model: RunwayGen4Model, resolution: Resolution = "1080p", num_images: int = 1) -> str:
        """Get a formatted cost estimate."""
        cost = self.calculate_cost(model, resolution, num_images)
        model_name = self.MODEL_CONFIGS[model]["name"]
        
        if num_images == 1:
            return f"${cost:.3f} for 1 {model_name} image at {resolution}"
        else:
            return f"${cost:.3f} for {num_images} {model_name} images at {resolution}"


def main():
    """Example usage of Runway Gen4 Image Generator."""
    print("🎬 Runway Gen4 Image Generator Example")
    print("=" * 60)
    
    # Initialize generator
    try:
        generator = RunwayGen4Generator(verbose=True)
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
    print(f"  • {generator.get_cost_estimate(RunwayGen4Model.GEN4_IMAGE, '720p', 1)}")
    print(f"  • {generator.get_cost_estimate(RunwayGen4Model.GEN4_IMAGE, '1080p', 1)}")
    print(f"  • {generator.get_cost_estimate(RunwayGen4Model.GEN4_IMAGE, '1080p', 5)}")
    
    print("\n⚠️ WARNING: Image generation incurs costs!")
    print("💡 Use test files to run actual generation tests")
    
    # Example usage (commented out to avoid costs):
    """
    # Generate with text only
    result = generator.generate_image(
        prompt="A beautiful landscape with mountains and a lake at sunset, cinematic lighting",
        resolution="1080p",
        aspect_ratio="16:9"
    )
    
    # Generate with reference images
    result = generator.generate_image(
        prompt="A stylized portrait in the style of the reference images",
        resolution="1080p",
        aspect_ratio="4:3",
        reference_images=[
            "https://example.com/reference1.jpg",
            "https://example.com/reference2.jpg"
        ],
        reference_tags=["style", "composition"]
    )
    
    if result['success']:
        print(f"✅ Generated: {result['local_path']}")
    else:
        print(f"❌ Failed: {result['error']}")
    """


if __name__ == "__main__":
    main()