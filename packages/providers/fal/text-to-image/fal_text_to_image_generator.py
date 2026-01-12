"""
FAL AI Text-to-Image Generator

This module provides a unified interface for generating images using four different
FAL AI text-to-image models:
1. Imagen 4 Preview Fast - Cost-effective Google model
2. Seedream v3 - Bilingual (Chinese/English) text-to-image model  
3. FLUX.1 Schnell - Fastest inference FLUX model
4. FLUX.1 Dev - High-quality 12B parameter FLUX model

Author: AI Assistant
Date: 2024
"""

import os
import requests
import time
from typing import Dict, Any, Optional, List
import fal_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FALTextToImageGenerator:
    """
    A unified text-to-image generator supporting multiple FAL AI models.
    
    Supported models:
    - imagen4: fal-ai/imagen4/preview/fast
    - seedream: fal-ai/bytedance/seedream/v3/text-to-image  
    - flux_schnell: fal-ai/flux-1/schnell
    - flux_dev: fal-ai/flux-1/dev
    """
    
    # Model endpoint mappings
    MODEL_ENDPOINTS = {
        "imagen4": "fal-ai/imagen4/preview/fast",
        "seedream": "fal-ai/bytedance/seedream/v3/text-to-image",
        "flux_schnell": "fal-ai/flux-1/schnell",
        "flux_dev": "fal-ai/flux-1/dev",
        "nano_banana_pro": "fal-ai/nano-banana-pro",
        "gpt_image_1_5": "fal-ai/gpt-image-1.5"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the FAL Text-to-Image Generator.
        
        Args:
            api_key: FAL AI API key. If not provided, will try to load from environment.
        """
        self.api_key = api_key or os.getenv('FAL_KEY')
        if not self.api_key:
            raise ValueError("FAL_KEY not found in environment variables or provided as parameter")
        
        # Set the API key for fal_client
        os.environ['FAL_KEY'] = self.api_key
        
        # Model-specific default parameters
        self.model_defaults = {
            "imagen4": {
                "image_size": "landscape_4_3",  # Options: square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9
                "num_inference_steps": 4,
                "guidance_scale": 3.0,
                "num_images": 1,
                "enable_safety_checker": True
            },
            "seedream": {
                "image_size": "square",  # Options: square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9
                "num_inference_steps": 20,
                "guidance_scale": 7.5,
                "num_images": 1,
                "seed": None  # Random if None
            },
            "flux_schnell": {
                "image_size": "landscape_4_3",  # Options: square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9
                "num_inference_steps": 4,  # Schnell is optimized for 1-4 steps
                "num_images": 1,
                "enable_safety_checker": True
            },
            "flux_dev": {
                "image_size": "landscape_4_3",  # Options: square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9
                "num_inference_steps": 28,  # Dev typically uses more steps for quality
                "guidance_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": True
            },
            "nano_banana_pro": {
                "image_size": "landscape_4_3",
                "num_inference_steps": 4,
                "num_images": 1,
                "sync_mode": True,
                "enable_safety_checker": True
            },
            "gpt_image_1_5": {
                "image_size": "landscape_4_3",
                "num_images": 1,
                "sync_mode": True
            }
        }
    
    def validate_model(self, model: str) -> str:
        """
        Validate and return the model endpoint.
        
        Args:
            model: Model name (imagen4, seedream, flux_schnell, flux_dev)
            
        Returns:
            Model endpoint string
            
        Raises:
            ValueError: If model is not supported
        """
        if model not in self.MODEL_ENDPOINTS:
            available_models = ", ".join(self.MODEL_ENDPOINTS.keys())
            raise ValueError(f"Model '{model}' not supported. Available models: {available_models}")
        
        return self.MODEL_ENDPOINTS[model]
    
    def generate_image(
        self,
        prompt: str,
        model: str = "flux_schnell",
        negative_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate an image using the specified model.
        
        Args:
            prompt: Text description of the image to generate
            model: Model to use (imagen4, seedream, flux_schnell, flux_dev)
            negative_prompt: What to avoid in the image (not supported by all models)
            **kwargs: Model-specific parameters
            
        Returns:
            Dictionary containing image URL and metadata
        """
        endpoint = self.validate_model(model)
        
        # Get default parameters for the model
        default_params = self.model_defaults[model].copy()
        
        # Override with provided kwargs
        default_params.update(kwargs)
        
        # Build the request payload
        payload = {
            "prompt": prompt,
            **default_params
        }
        
        # Add negative prompt if supported and provided
        if negative_prompt and model in ["seedream", "flux_dev"]:
            payload["negative_prompt"] = negative_prompt
        
        try:
            print(f"🎨 Generating image with {model} model...")
            print(f"📝 Prompt: {prompt}")
            if negative_prompt and model in ["seedream", "flux_dev"]:
                print(f"❌ Negative prompt: {negative_prompt}")
            
            # Submit the request
            result = fal_client.subscribe(
                endpoint,
                arguments=payload,
                with_logs=True
            )
            
            if result and 'images' in result and len(result['images']) > 0:
                image_data = result['images'][0]
                
                # Get output folder from kwargs or use default
                output_folder = kwargs.get('output_folder', 'output')
                
                # Get the raw URL from the API response
                raw_url = image_data['url']
                is_base64_url = raw_url.startswith('data:')

                response = {
                    'success': True,
                    'model': model,
                    'endpoint': endpoint,
                    'image_url': raw_url,  # Will be replaced with local path if base64
                    'image_size': str(image_data.get('width', 'unknown')) + 'x' + str(image_data.get('height', 'unknown')) if 'width' in image_data else 'unknown',
                    'prompt': prompt,
                    'negative_prompt': negative_prompt,
                    'parameters': payload,
                    'full_result': result
                }

                print(f"✅ Image generated successfully!")
                if is_base64_url:
                    print(f"📦 Received base64 image data ({len(raw_url) / 1024:.1f} KB)")
                else:
                    print(f"🔗 Image URL: {response['image_url']}")

                # Automatically download/save the image
                try:
                    local_path = self.download_image(raw_url, output_folder)
                    response['local_path'] = local_path

                    # Replace base64 data URL with local path to prevent huge strings
                    if is_base64_url:
                        response['image_url'] = local_path
                        response['original_was_base64'] = True

                    print(f"📥 Image saved to: {local_path}")
                except Exception as e:
                    print(f"⚠️  Warning: Could not download image: {e}")
                
                return response
            else:
                raise Exception("No images returned from API")
                
        except Exception as e:
            print(f"❌ Error generating image: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model': model,
                'endpoint': endpoint,
                'prompt': prompt
            }
    
    def generate_with_imagen4(
        self,
        prompt: str,
        image_size: str = "landscape_4_3",
        num_inference_steps: int = 4,
        guidance_scale: float = 3.0,
        num_images: int = 1,
        enable_safety_checker: bool = True
    ) -> Dict[str, Any]:
        """
        Generate image using Imagen 4 Preview Fast model.
        
        Args:
            prompt: Text description
            image_size: Image aspect ratio (square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9)
            num_inference_steps: Number of denoising steps (1-8, default 4)
            guidance_scale: How closely to follow the prompt (1.0-10.0, default 3.0)
            num_images: Number of images to generate (1-4, default 1)
            enable_safety_checker: Enable safety filtering
            
        Returns:
            Generation result dictionary
        """
        return self.generate_image(
            prompt=prompt,
            model="imagen4",
            image_size=image_size,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            num_images=num_images,
            enable_safety_checker=enable_safety_checker
        )
    
    def generate_with_seedream(
        self,
        prompt: str,
        image_size: str = "square",
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate image using Seedream v3 model (supports Chinese and English).
        
        Args:
            prompt: Text description (Chinese or English)
            image_size: Image aspect ratio (square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9)
            num_inference_steps: Number of denoising steps (1-50, default 20)
            guidance_scale: How closely to follow the prompt (1.0-20.0, default 7.5)
            negative_prompt: What to avoid in the image
            seed: Random seed for reproducibility
            
        Returns:
            Generation result dictionary
        """
        return self.generate_image(
            prompt=prompt,
            model="seedream",
            image_size=image_size,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            negative_prompt=negative_prompt,
            seed=seed
        )
    
    def generate_with_flux_schnell(
        self,
        prompt: str,
        image_size: str = "landscape_4_3",
        num_inference_steps: int = 4,
        num_images: int = 1,
        enable_safety_checker: bool = True
    ) -> Dict[str, Any]:
        """
        Generate image using FLUX.1 Schnell (fastest) model.
        
        Args:
            prompt: Text description
            image_size: Image aspect ratio (square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9)
            num_inference_steps: Number of denoising steps (1-4 recommended, default 4)
            num_images: Number of images to generate (1-4, default 1)
            enable_safety_checker: Enable safety filtering
            
        Returns:
            Generation result dictionary
        """
        return self.generate_image(
            prompt=prompt,
            model="flux_schnell",
            image_size=image_size,
            num_inference_steps=num_inference_steps,
            num_images=num_images,
            enable_safety_checker=enable_safety_checker
        )
    
    def generate_with_flux_dev(
        self,
        prompt: str,
        image_size: str = "landscape_4_3",
        num_inference_steps: int = 28,
        guidance_scale: float = 3.5,
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        enable_safety_checker: bool = True
    ) -> Dict[str, Any]:
        """
        Generate image using FLUX.1 Dev (high-quality) model.
        
        Args:
            prompt: Text description
            image_size: Image aspect ratio (square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9)
            num_inference_steps: Number of denoising steps (1-50, default 28)
            guidance_scale: How closely to follow the prompt (1.0-10.0, default 3.5)
            negative_prompt: What to avoid in the image
            num_images: Number of images to generate (1-4, default 1)
            enable_safety_checker: Enable safety filtering
            
        Returns:
            Generation result dictionary
        """
        return self.generate_image(
            prompt=prompt,
            model="flux_dev",
            image_size=image_size,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            negative_prompt=negative_prompt,
            num_images=num_images,
            enable_safety_checker=enable_safety_checker
        )
    
    def download_image(self, image_url: str, output_folder: str = "output", filename: Optional[str] = None) -> str:
        """
        Download an image from URL to local folder.

        Supports both HTTP/HTTPS URLs and base64 data URLs.

        Args:
            image_url: URL of the image to download (HTTP URL or data: URL)
            output_folder: Local folder to save the image
            filename: Custom filename (optional)

        Returns:
            Path to the downloaded image
        """
        import base64

        try:
            # Create output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

            # Generate filename if not provided
            if not filename:
                timestamp = int(time.time())
                filename = f"generated_image_{timestamp}.png"

            # Handle base64 data URLs (e.g., "data:image/png;base64,...")
            if image_url.startswith('data:'):
                # Parse the data URL
                # Format: data:[<mediatype>][;base64],<data>
                try:
                    header, encoded_data = image_url.split(',', 1)

                    # Determine file extension from MIME type
                    if 'image/png' in header:
                        ext = '.png'
                    elif 'image/jpeg' in header or 'image/jpg' in header:
                        ext = '.jpg'
                    elif 'image/webp' in header:
                        ext = '.webp'
                    elif 'image/gif' in header:
                        ext = '.gif'
                    else:
                        ext = '.png'  # Default to PNG

                    # Ensure filename has correct extension
                    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                        filename += ext

                    filepath = os.path.join(output_folder, filename)

                    # Decode and save
                    print(f"💾 Saving base64 image to: {filepath}")
                    image_data = base64.b64decode(encoded_data)

                    with open(filepath, 'wb') as f:
                        f.write(image_data)

                    print(f"✅ Image saved successfully! ({len(image_data) / 1024:.1f} KB)")
                    return filepath

                except Exception as e:
                    raise ValueError(f"Failed to decode base64 image: {e}")

            # Handle regular HTTP/HTTPS URLs
            # Ensure filename has extension
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                filename += '.png'

            filepath = os.path.join(output_folder, filename)

            # Download the image
            print(f"⬇️ Downloading image to: {filepath}")
            response = requests.get(image_url, stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print("✅ Image downloaded successfully!")
            return filepath

        except Exception as e:
            print(f"❌ Error downloading image: {str(e)}")
            raise
    
    def batch_generate(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        negative_prompt: Optional[str] = None,
        output_folder: str = "output",
        download_images: bool = True,
        auto_confirm: bool = False,
        **model_kwargs
    ) -> Dict[str, Any]:
        """
        Generate images with multiple models using the same prompt (batch processing).
        
        Args:
            prompt: Text description for all models
            models: List of models to use (default: all models)
            negative_prompt: What to avoid (only used for compatible models)
            output_folder: Folder to save generated images
            download_images: Whether to download images locally
            auto_confirm: Skip confirmation prompt (use with caution!)
            **model_kwargs: Additional parameters to pass to all models
            
        Returns:
            Dictionary with results from all models
        """
        if models is None:
            models = list(self.MODEL_ENDPOINTS.keys())
        
        # Validate models
        for model in models:
            if model not in self.MODEL_ENDPOINTS:
                available_models = ", ".join(self.MODEL_ENDPOINTS.keys())
                raise ValueError(f"Model '{model}' not supported. Available models: {available_models}")
        
        print(f"🔄 Batch generating with {len(models)} models...")
        print(f"📝 Prompt: {prompt}")
        if negative_prompt:
            compatible_models = [m for m in models if m in ["seedream", "flux_dev"]]
            print(f"❌ Negative prompt (for {', '.join(compatible_models)}): {negative_prompt}")
        print(f"💰 Estimated cost: ~${len(models) * 0.015:.3f} (~$0.01-0.02 per image)")
        
        if not auto_confirm:
            confirm = input("⚠️ This will generate multiple images and cost money. Continue? (y/N): ")
            if confirm.lower() not in ['y', 'yes']:
                print("❌ Batch generation cancelled.")
                return {'cancelled': True, 'reason': 'User cancelled'}
        
        results = {}
        successful_count = 0
        start_time = time.time()
        
        for i, model in enumerate(models, 1):
            print(f"\n🎨 [{i}/{len(models)}] Generating with {model}...")
            
            try:
                # Generate image
                model_start_time = time.time()
                result = self.generate_image(
                    prompt=prompt,
                    model=model,
                    negative_prompt=negative_prompt,
                    **model_kwargs
                )
                model_time = time.time() - model_start_time
                
                if result['success']:
                    successful_count += 1
                    result['generation_time'] = model_time
                    
                    # Download image if requested
                    if download_images:
                        try:
                            timestamp = int(time.time())
                            filename = f"batch_{model}_{timestamp}.png"
                            local_path = self.download_image(
                                result['image_url'],
                                output_folder,
                                filename
                            )
                            result['local_path'] = local_path
                        except Exception as download_error:
                            print(f"⚠️ Download failed for {model}: {download_error}")
                            result['download_error'] = str(download_error)
                
                results[model] = result
                
            except Exception as e:
                print(f"❌ Error with {model}: {str(e)}")
                results[model] = {
                    'success': False,
                    'error': str(e),
                    'model': model
                }
        
        total_time = time.time() - start_time
        
        # Summary
        print(f"\n📊 Batch generation complete!")
        print(f"✅ Success: {successful_count}/{len(models)} models")
        print(f"⏱️ Total time: {total_time:.2f} seconds")
        print(f"💰 Estimated cost: ~${successful_count * 0.015:.3f}")
        
        if successful_count > 0:
            avg_time = sum(r.get('generation_time', 0) for r in results.values() if r.get('success')) / successful_count
            print(f"⚡ Average generation time: {avg_time:.2f} seconds")
        
        return {
            'results': results,
            'summary': {
                'total_models': len(models),
                'successful': successful_count,
                'failed': len(models) - successful_count,
                'total_time': total_time,
                'estimated_cost': successful_count * 0.015,
                'prompt': prompt,
                'negative_prompt': negative_prompt
            }
        }
    
    def compare_models(
        self,
        prompt: str,
        models: Optional[List[str]] = None,
        negative_prompt: Optional[str] = None,
        output_folder: str = "output"
    ) -> Dict[str, Any]:
        """
        Generate images with multiple models for comparison (legacy method).
        
        Args:
            prompt: Text description
            models: List of models to compare (default: all models)
            negative_prompt: What to avoid (only used for compatible models)
            output_folder: Folder to save comparison images
            
        Returns:
            Dictionary with results from all models
        """
        print("ℹ️ Using legacy compare_models method. Consider using batch_generate for more options.")
        
        result = self.batch_generate(
            prompt=prompt,
            models=models,
            negative_prompt=negative_prompt,
            output_folder=output_folder,
            download_images=True,
            auto_confirm=False
        )
        
        # Return in legacy format for backward compatibility
        if 'cancelled' in result:
            return result
        
        return result['results']
    
    def get_model_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all supported models.
        
        Returns:
            Dictionary with model information and capabilities
        """
        return {
            "imagen4": {
                "name": "Imagen 4 Preview Fast",
                "endpoint": self.MODEL_ENDPOINTS["imagen4"],
                "description": "Google's cost-effective text-to-image model",
                "strengths": ["Fast generation", "Cost-effective", "Good quality"],
                "supported_features": ["Safety checker", "Multiple aspect ratios"],
                "max_steps": 8,
                "supports_negative_prompt": False
            },
            "seedream": {
                "name": "Seedream v3",
                "endpoint": self.MODEL_ENDPOINTS["seedream"],
                "description": "Bilingual (Chinese/English) text-to-image model",
                "strengths": ["Bilingual support", "High quality", "Flexible sizing"],
                "supported_features": ["Negative prompts", "Custom seeds", "Multiple sizes"],
                "max_steps": 50,
                "supports_negative_prompt": True
            },
            "flux_schnell": {
                "name": "FLUX.1 Schnell",
                "endpoint": self.MODEL_ENDPOINTS["flux_schnell"],
                "description": "Fastest FLUX model optimized for speed",
                "strengths": ["Ultra-fast generation", "Good quality", "Low cost"],
                "supported_features": ["Safety checker", "Multiple aspect ratios"],
                "max_steps": 4,
                "supports_negative_prompt": False
            },
            "flux_dev": {
                "name": "FLUX.1 Dev",
                "endpoint": self.MODEL_ENDPOINTS["flux_dev"],
                "description": "High-quality 12B parameter FLUX model",
                "strengths": ["Highest quality", "Detailed images", "Professional results"],
                "supported_features": ["Negative prompts", "Guidance scale", "Safety checker"],
                "max_steps": 50,
                "supports_negative_prompt": True
            },
            "nano_banana_pro": {
                "name": "Nano Banana Pro",
                "endpoint": self.MODEL_ENDPOINTS["nano_banana_pro"],
                "description": "Fast, high-quality image generation model",
                "strengths": ["Fast generation", "High quality", "Cost-effective"],
                "supported_features": ["Safety checker", "Multiple aspect ratios"],
                "max_steps": 4,
                "supports_negative_prompt": False
            },
            "gpt_image_1_5": {
                "name": "GPT Image 1.5",
                "endpoint": self.MODEL_ENDPOINTS["gpt_image_1_5"],
                "description": "GPT-powered image generation model",
                "strengths": ["GPT-powered", "Natural language understanding", "High quality"],
                "supported_features": ["Multiple aspect ratios", "Sync mode"],
                "max_steps": 1,
                "supports_negative_prompt": False
            }
        }
    
    def load_prompt_from_input(self, prompt_input: str) -> str:
        """
        Load prompt from either text string or file path.
        
        Args:
            prompt_input: Either a text prompt or path to a text file
            
        Returns:
            The prompt text
            
        Raises:
            FileNotFoundError: If file path is provided but doesn't exist
            ValueError: If file is empty or invalid
        """
        # Check if input looks like a file path
        if (prompt_input.endswith(('.txt', '.md', '.prompt')) or 
            os.path.sep in prompt_input or 
            os.path.exists(prompt_input)):
            
            if not os.path.exists(prompt_input):
                raise FileNotFoundError(f"Prompt file not found: {prompt_input}")
            
            try:
                with open(prompt_input, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if not content:
                    raise ValueError(f"Prompt file is empty: {prompt_input}")
                
                print(f"📁 Loaded prompt from file: {prompt_input}")
                return content
                
            except Exception as e:
                raise ValueError(f"Error reading prompt file {prompt_input}: {e}")
        
        # It's a direct text prompt
        return prompt_input
    
    def generate_from_cli(self, 
                         prompt_input: str,
                         model: str = "flux_schnell",
                         output_path: Optional[str] = None,
                         **model_params) -> Dict[str, Any]:
        """
        Generate image from CLI with support for prompt files and output path.
        
        Args:
            prompt_input: Text prompt or path to prompt file
            model: Model to use (imagen4, seedream, flux_schnell, flux_dev)
            output_path: Custom output directory path
            **model_params: Model-specific parameters
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Load prompt from input (text or file)
            prompt = self.load_prompt_from_input(prompt_input)
            
            # Validate model
            self.validate_model(model)
            
            # Set output directory
            output_dir = output_path or "output"
            
            print(f"🎨 Generating image with {model}")
            print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            print(f"📁 Output: {output_dir}")
            
            # Filter model-specific parameters
            valid_params = self._filter_model_params(model, model_params)
            
            # Generate image
            result = self.generate_image(
                prompt=prompt,
                model=model,
                **valid_params
            )
            
            # Download image if successful
            if result.get('success') and result.get('image_url'):
                try:
                    local_path = self.download_image(result['image_url'], output_dir)
                    result['local_path'] = local_path
                    print(f"✅ Image saved to: {local_path}")
                except Exception as e:
                    print(f"⚠️ Download failed: {e}")
                    result['download_error'] = str(e)
            
            return result
            
        except Exception as e:
            error_msg = f"CLI generation failed: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def _filter_model_params(self, model: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter parameters to only include those valid for the specified model.
        
        Args:
            model: Model name
            params: Dictionary of parameters
            
        Returns:
            Filtered parameters dictionary
        """
        if not params:
            return {}
        
        # Define valid parameters for each model
        valid_params = {
            "imagen4": {
                "image_size", "num_inference_steps", "guidance_scale",
                "num_images", "enable_safety_checker"
            },
            "seedream": {
                "image_size", "num_inference_steps", "guidance_scale",
                "num_images", "seed", "negative_prompt"
            },
            "flux_schnell": {
                "image_size", "num_inference_steps", "num_images",
                "enable_safety_checker"
            },
            "flux_dev": {
                "image_size", "num_inference_steps", "guidance_scale",
                "num_images", "enable_safety_checker", "negative_prompt"
            },
            "nano_banana_pro": {
                "image_size", "num_inference_steps", "num_images",
                "sync_mode", "enable_safety_checker"
            },
            "gpt_image_1_5": {
                "image_size", "num_images", "sync_mode"
            }
        }
        
        model_valid_params = valid_params.get(model, set())
        filtered = {k: v for k, v in params.items() 
                   if k in model_valid_params and v is not None}
        
        if filtered:
            print(f"🔧 Using parameters: {filtered}")
        
        return filtered
    
    def batch_generate_from_cli(self,
                              prompt_input: str,
                              models: Optional[List[str]] = None,
                              output_path: Optional[str] = None,
                              save_results: Optional[str] = None,
                              **shared_params) -> Dict[str, Any]:
        """
        Generate images with multiple models from CLI.
        
        Args:
            prompt_input: Text prompt or path to prompt file
            models: List of models to use (default: all models)
            output_path: Custom output directory path
            save_results: Path to save JSON results
            **shared_params: Parameters to apply to all compatible models
            
        Returns:
            Dictionary with results from all models
        """
        try:
            # Load prompt
            prompt = self.load_prompt_from_input(prompt_input)
            
            # Use all models if none specified
            if not models:
                models = list(self.MODEL_ENDPOINTS.keys())
            
            # Set output directory
            output_dir = output_path or "output"
            
            print(f"🆚 Batch generating with {len(models)} models")
            print(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            print(f"📁 Output: {output_dir}")
            print(f"🤖 Models: {', '.join(models)}")
            
            # Use the existing batch_generate method
            result = self.batch_generate(
                prompt=prompt,
                models=models,
                output_folder=output_dir,
                download_images=True,
                auto_confirm=True,  # Skip interactive confirmation in CLI mode
                **shared_params
            )
            
            # Save results if requested
            if save_results and result:
                try:
                    import json
                    with open(save_results, 'w') as f:
                        json.dump(result, f, indent=2)
                    print(f"📄 Results saved to: {save_results}")
                except Exception as e:
                    print(f"⚠️ Failed to save results: {e}")
            
            return result
            
        except Exception as e:
            error_msg = f"CLI batch generation failed: {e}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}


if __name__ == "__main__":
    # Example usage
    try:
        generator = FALTextToImageGenerator()
        
        # Test with FLUX Schnell (fastest)
        result = generator.generate_with_flux_schnell(
            prompt="A beautiful sunset over mountains, digital art style",
            image_size="landscape_4_3"
        )
        
        if result['success']:
            print(f"Generated image: {result['image_url']}")
            # Download the image
            local_path = generator.download_image(result['image_url'])
            print(f"Saved to: {local_path}")
        else:
            print(f"Generation failed: {result['error']}")
            
    except Exception as e:
        print(f"Error: {e}")
