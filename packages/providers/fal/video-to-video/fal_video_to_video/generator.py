"""
Main generator class for FAL Video to Video
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import fal_client
from dotenv import load_dotenv

from .models.base import BaseModel
from .utils.validators import validate_model, validate_video_url, validate_video_path
from .utils.file_utils import upload_video, get_video_info
from .config.constants import SUPPORTED_MODELS, MODEL_DISPLAY_NAMES


class FALVideoToVideoGenerator:
    """
    Main interface for FAL Video to Video generation.
    
    This class provides methods to generate audio for videos using various
    FAL AI models like ThinkSound.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the generator.
        
        Args:
            api_key: Optional FAL API key. If not provided, will look for FAL_KEY env var.
        """
        # Load environment variables
        load_dotenv()
        
        # Set API key
        self.api_key = api_key or os.getenv("FAL_KEY")
        if not self.api_key:
            raise ValueError(
                "FAL API key not found. Please provide api_key or set FAL_KEY environment variable."
            )
        
        fal_client.api_key = self.api_key
        
        # Auto-discover and instantiate all models
        self.models = self._build_models()

        print("✅ FAL Video to Video Generator initialized")

    @staticmethod
    def _build_models():
        """Auto-discover and instantiate model classes by MODEL_KEY attribute."""
        from . import models as models_pkg
        instances = {}
        for name in dir(models_pkg):
            cls = getattr(models_pkg, name)
            if (isinstance(cls, type)
                    and issubclass(cls, BaseModel)
                    and cls is not BaseModel
                    and hasattr(cls, 'MODEL_KEY')):
                instances[cls.MODEL_KEY] = cls()
        return instances

    def add_audio_to_video(
        self,
        video_url: str,
        model: str = "thinksound",
        prompt: Optional[str] = None,
        seed: Optional[int] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add AI-generated audio to a video using URL input.
        
        Args:
            video_url: URL of the input video
            model: Model to use (default: "thinksound")
            prompt: Optional text prompt to guide audio generation
            seed: Optional random seed for reproducibility
            output_dir: Custom output directory
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing:
                - success: Whether generation was successful
                - model: Model used
                - local_path: Path to downloaded video with audio
                - response: Full API response
                - processing_time: Time taken for generation
        """
        # Validate inputs
        model = validate_model(model)
        video_url = validate_video_url(video_url)
        
        # Get model instance
        model_instance = self.models[model]
        
        # Prepare parameters
        params = {
            "prompt": prompt,
            "seed": seed,
            **kwargs
        }
        
        # Generate audio
        return model_instance.generate(
            video_url=video_url,
            output_dir=output_dir,
            **params
        )
    
    def add_audio_to_local_video(
        self,
        video_path: str,
        model: str = "thinksound",
        prompt: Optional[str] = None,
        seed: Optional[int] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Add AI-generated audio to a local video file.
        
        Args:
            video_path: Path to local video file
            model: Model to use (default: "thinksound")
            prompt: Optional text prompt to guide audio generation
            seed: Optional random seed for reproducibility
            output_dir: Custom output directory
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing generation results
        """
        # Validate inputs
        model = validate_model(model)
        video_path = validate_video_path(video_path)
        
        # Get video info
        video_info = get_video_info(video_path)
        if video_info:
            print(f"📹 Video info:")
            print(f"   Duration: {video_info.get('duration', 'Unknown')}s")
            print(f"   Resolution: {video_info.get('width', '?')}x{video_info.get('height', '?')}")
            print(f"   Has audio: {'Yes' if video_info.get('has_audio') else 'No'}")
        
        # Upload video
        video_url = upload_video(video_path)
        
        # Generate audio
        return self.add_audio_to_video(
            video_url=video_url,
            model=model,
            prompt=prompt,
            seed=seed,
            output_dir=output_dir,
            **kwargs
        )
    
    def upscale_video(
        self,
        video_url: str,
        upscale_factor: float = 2,
        target_fps: Optional[int] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upscale a video using Topaz Video Upscale from URL input.
        
        Args:
            video_url: URL of the input video
            upscale_factor: Upscaling factor (1-4, default: 2)
            target_fps: Optional target FPS for frame interpolation (1-120)
            output_dir: Custom output directory
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing:
                - success: Whether upscaling was successful
                - model: Model used
                - local_path: Path to downloaded upscaled video
                - response: Full API response
                - processing_time: Time taken for upscaling
        """
        # Validate inputs
        video_url = validate_video_url(video_url)
        
        # Get model instance
        model_instance = self.models["topaz"]
        
        # Prepare parameters
        params = {
            "upscale_factor": upscale_factor,
            "target_fps": target_fps,
            **kwargs
        }
        
        # Generate upscaled video
        return model_instance.generate(
            video_url=video_url,
            output_dir=output_dir,
            **params
        )
    
    def upscale_local_video(
        self,
        video_path: str,
        upscale_factor: float = 2,
        target_fps: Optional[int] = None,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Upscale a local video file using Topaz Video Upscale.
        
        Args:
            video_path: Path to local video file
            upscale_factor: Upscaling factor (1-4, default: 2)
            target_fps: Optional target FPS for frame interpolation (1-120)
            output_dir: Custom output directory
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dictionary containing upscaling results
        """
        # Validate inputs
        video_path = validate_video_path(video_path)
        
        # Get video info
        video_info = get_video_info(video_path)
        if video_info:
            print(f"📹 Video info:")
            print(f"   Duration: {video_info.get('duration', 'Unknown')}s")
            print(f"   Resolution: {video_info.get('width', '?')}x{video_info.get('height', '?')}")
            print(f"   FPS: {video_info.get('fps', 'Unknown')}")
            
            # Calculate expected output resolution
            if video_info.get('width') and video_info.get('height'):
                new_width = int(video_info['width'] * upscale_factor)
                new_height = int(video_info['height'] * upscale_factor)
                print(f"   Expected output: {new_width}x{new_height}")
        
        # Upload video
        video_url = upload_video(video_path)
        
        # Upscale video
        return self.upscale_video(
            video_url=video_url,
            upscale_factor=upscale_factor,
            target_fps=target_fps,
            output_dir=output_dir,
            **kwargs
        )
    
    def edit_video(
        self,
        video_url: str,
        prompt: str,
        model: str = "kling_o3_pro_edit",
        elements: Optional[list] = None,
        image_urls: Optional[list] = None,
        duration: str = "5",
        aspect_ratio: str = "16:9",
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Edit video using Kling O3 with element replacement and @ reference syntax.

        Args:
            video_url: URL of source video to edit
            prompt: Text description with @ references (e.g., "Change background to @Image1")
            model: Model to use ("kling_o3_standard_edit" or "kling_o3_pro_edit")
            elements: Character/object definitions for replacement
            image_urls: Reference images for style/context
            duration: Output video duration (3-15 seconds)
            aspect_ratio: "16:9", "9:16", "1:1"
            output_dir: Custom output directory
            **kwargs: Additional parameters

        Returns:
            Dictionary containing edit results
        """
        if model not in ["kling_o3_standard_edit", "kling_o3_pro_edit"]:
            raise ValueError(f"Invalid edit model: {model}. Use 'kling_o3_standard_edit' or 'kling_o3_pro_edit'")

        video_url = validate_video_url(video_url)
        model_instance = self.models[model]

        params = {
            "prompt": prompt,
            "elements": elements or [],
            "image_urls": image_urls or [],
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            **kwargs
        }

        return model_instance.generate(
            video_url=video_url,
            output_dir=output_dir,
            **params
        )

    def apply_style_transfer(
        self,
        video_url: str,
        prompt: str,
        model: str = "kling_o3_pro_v2v_ref",
        elements: Optional[list] = None,
        image_urls: Optional[list] = None,
        duration: str = "5",
        aspect_ratio: str = "16:9",
        keep_audio: bool = False,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Apply style transfer to video using Kling O3 reference model.

        Args:
            video_url: URL of source video
            prompt: Text description with @ references (e.g., "Apply watercolor style of @Image1")
            model: Model to use ("kling_o3_standard_v2v_ref" or "kling_o3_pro_v2v_ref")
            elements: Character/object definitions for consistency
            image_urls: Style reference images
            duration: Output video duration (3-15 seconds)
            aspect_ratio: "16:9", "9:16", "1:1"
            keep_audio: Preserve original audio
            output_dir: Custom output directory
            **kwargs: Additional parameters

        Returns:
            Dictionary containing style transfer results
        """
        if model not in ["kling_o3_standard_v2v_ref", "kling_o3_pro_v2v_ref"]:
            raise ValueError(f"Invalid reference model: {model}. Use 'kling_o3_standard_v2v_ref' or 'kling_o3_pro_v2v_ref'")

        video_url = validate_video_url(video_url)
        model_instance = self.models[model]

        params = {
            "prompt": prompt,
            "elements": elements or [],
            "image_urls": image_urls or [],
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "keep_audio": keep_audio,
            **kwargs
        }

        return model_instance.generate(
            video_url=video_url,
            output_dir=output_dir,
            **params
        )

    def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about available models.
        
        Args:
            model: Specific model to get info for. If None, returns info for all models.
            
        Returns:
            Dictionary containing model information
        """
        if model:
            model = validate_model(model)
            return self.models[model].get_model_info()
        else:
            # Return info for all models
            return {
                model_key: model_instance.get_model_info()
                for model_key, model_instance in self.models.items()
            }
    
    def list_models(self) -> list:
        """
        List all available models.
        
        Returns:
            List of available model names
        """
        return SUPPORTED_MODELS
    
    def __repr__(self) -> str:
        """String representation of the generator."""
        return f"FALVideoToVideoGenerator(models={self.list_models()})"