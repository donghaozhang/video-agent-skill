"""
Main FAL Image-to-Video Generator with Multi-Model Support.

Unified interface for all image-to-video models.
"""

import os
from typing import Dict, Any, Optional, List
import fal_client
from dotenv import load_dotenv

from .models import (
    HailuoModel,
    KlingModel,
    Kling26ProModel,
    SeedanceModel,
    Sora2Model,
    Sora2ProModel,
    Veo31FastModel,
    Wan26Model
)
from .utils.file_utils import (
    upload_image,
    upload_file,
    upload_images,
    upload_audio,
    upload_video,
    ensure_output_directory,
    is_url
)
from .config.constants import SUPPORTED_MODELS, MODEL_INFO, MODEL_EXTENDED_FEATURES

load_dotenv()


class FALImageToVideoGenerator:
    """
    Unified FAL AI Image-to-Video Generator with Multi-Model Support.

    Supports:
    - MiniMax Hailuo-02: Standard quality, prompt optimization
    - Kling Video v2.1: High-quality with negative prompts
    - Kling Video v2.6 Pro: Professional tier
    - ByteDance Seedance v1.5 Pro: Motion synthesis with seed control
    - Sora 2: OpenAI's image-to-video
    - Sora 2 Pro: Professional Sora with 1080p
    - Veo 3.1 Fast: Google's fast model with audio
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the generator.

        Args:
            api_key: FAL AI API key. If not provided, uses FAL_KEY env var.
        """
        self.mock_mode = False

        if api_key:
            fal_client.api_key = api_key
        else:
            api_key = os.getenv('FAL_KEY')
            if not api_key:
                if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
                    print("⚠️  Running in CI environment - using mock mode")
                    self.mock_mode = True
                    api_key = "mock_key"
                else:
                    raise ValueError(
                        "FAL_KEY environment variable is not set. "
                        "Set it or provide api_key parameter."
                    )
            fal_client.api_key = api_key

        # Initialize all models
        self.models = {
            "hailuo": HailuoModel(),
            "kling_2_1": KlingModel(),
            "kling_2_6_pro": Kling26ProModel(),
            "seedance_1_5_pro": SeedanceModel(),
            "sora_2": Sora2Model(),
            "sora_2_pro": Sora2ProModel(),
            "veo_3_1_fast": Veo31FastModel(),
            "wan_2_6": Wan26Model()
        }

        self.output_dir = ensure_output_directory("output")

    def generate_video(
        self,
        prompt: str,
        image_url: str,
        model: str = "hailuo",
        output_dir: Optional[str] = None,
        use_async: bool = False,
        # Extended parameters
        start_frame: Optional[str] = None,
        end_frame: Optional[str] = None,
        ref_images: Optional[List[str]] = None,
        audio: Optional[str] = None,
        ref_video: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from image using specified model.

        Args:
            prompt: Text description for video generation
            image_url: URL of input image (or use start_frame)
            model: Model to use (default: "hailuo")
            output_dir: Custom output directory
            use_async: Whether to use async processing
            start_frame: Starting frame image (overrides image_url if provided)
            end_frame: Ending frame image for interpolation (Kling models)
            ref_images: Reference images for consistency (future support)
            audio: Audio file for synchronization (future support)
            ref_video: Reference video for motion/style (future support)
            **kwargs: Model-specific parameters

        Returns:
            Dictionary containing generation results
        """
        # Mock mode for CI
        if self.mock_mode:
            import time
            return {
                'success': True,
                'video': {'url': f'mock://video-{int(time.time())}.mp4'},
                'local_path': f'/tmp/mock_video_{int(time.time())}.mp4',
                'model': model,
                'mock_mode': True
            }

        if model not in self.models:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported: {list(self.models.keys())}"
            )

        # Get model feature support
        features = MODEL_EXTENDED_FEATURES.get(model, {})

        # Process start_frame (overrides image_url)
        effective_image_url = image_url
        if start_frame:
            if not is_url(start_frame):
                effective_image_url = upload_file(start_frame)
                if not effective_image_url:
                    return {
                        "success": False,
                        "error": f"Failed to upload start_frame: {start_frame}",
                        "model": model
                    }
            else:
                effective_image_url = start_frame

        # Process end_frame if supported
        if end_frame:
            if not features.get("end_frame"):
                print(f"⚠️ Model {model} does not support end_frame parameter, ignoring")
            else:
                if not is_url(end_frame):
                    end_frame = upload_file(end_frame)
                    if not end_frame:
                        return {
                            "success": False,
                            "error": "Failed to upload end_frame",
                            "model": model
                        }
                kwargs["end_frame"] = end_frame

        # Process ref_images if supported (future)
        if ref_images:
            if not features.get("ref_images"):
                print(f"⚠️ Model {model} does not support ref_images parameter, ignoring")
            else:
                try:
                    kwargs["ref_images"] = upload_images(ref_images)
                except ValueError as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "model": model
                    }

        # Process audio if supported (future)
        if audio:
            if not features.get("audio_input"):
                print(f"⚠️ Model {model} does not support audio input parameter, ignoring")
            else:
                if not is_url(audio):
                    audio = upload_audio(audio)
                    if not audio:
                        return {
                            "success": False,
                            "error": "Failed to upload audio",
                            "model": model
                        }
                kwargs["audio_url"] = audio

        # Process ref_video if supported (future)
        if ref_video:
            if not features.get("ref_video"):
                print(f"⚠️ Model {model} does not support ref_video parameter, ignoring")
            else:
                if not is_url(ref_video):
                    ref_video = upload_video(ref_video)
                    if not ref_video:
                        return {
                            "success": False,
                            "error": "Failed to upload ref_video",
                            "model": model
                        }
                kwargs["ref_video_url"] = ref_video

        return self.models[model].generate(
            prompt=prompt,
            image_url=effective_image_url,
            output_dir=output_dir,
            use_async=use_async,
            **kwargs
        )

    def generate_video_from_local_image(
        self,
        prompt: str,
        image_path: str,
        model: str = "hailuo",
        output_dir: Optional[str] = None,
        use_async: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from local image file.

        Args:
            prompt: Text description for video generation
            image_path: Path to local image file
            model: Model to use
            output_dir: Custom output directory
            use_async: Whether to use async processing
            **kwargs: Model-specific parameters

        Returns:
            Dictionary containing generation results
        """
        # Upload local image
        image_url = upload_image(image_path)
        if not image_url:
            return {
                "success": False,
                "error": f"Failed to upload image: {image_path}",
                "model": model
            }

        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model=model,
            output_dir=output_dir,
            use_async=use_async,
            **kwargs
        )

    # Convenience methods for each model
    def generate_with_sora(
        self,
        prompt: str,
        image_url: str,
        duration: int = 4,
        resolution: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Sora 2."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="sora_2",
            duration=duration,
            resolution=resolution,
            **kwargs
        )

    def generate_with_sora_pro(
        self,
        prompt: str,
        image_url: str,
        duration: int = 4,
        resolution: str = "1080p",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Sora 2 Pro."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="sora_2_pro",
            duration=duration,
            resolution=resolution,
            **kwargs
        )

    def generate_with_veo(
        self,
        prompt: str,
        image_url: str,
        duration: str = "8s",
        generate_audio: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Veo 3.1 Fast."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="veo_3_1_fast",
            duration=duration,
            generate_audio=generate_audio,
            **kwargs
        )

    def generate_with_seedance(
        self,
        prompt: str,
        image_url: str,
        duration: str = "5",
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using ByteDance Seedance."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="seedance_1_5_pro",
            duration=duration,
            seed=seed,
            **kwargs
        )

    def generate_with_kling_pro(
        self,
        prompt: str,
        image_url: str,
        duration: str = "5",
        negative_prompt: str = "blur, distort, and low quality",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Kling v2.6 Pro."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="kling_2_6_pro",
            duration=duration,
            negative_prompt=negative_prompt,
            **kwargs
        )

    def generate_with_hailuo(
        self,
        prompt: str,
        image_url: str,
        duration: str = "6",
        prompt_optimizer: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using MiniMax Hailuo-02."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="hailuo",
            duration=duration,
            prompt_optimizer=prompt_optimizer,
            **kwargs
        )

    def generate_with_kling(
        self,
        prompt: str,
        image_url: str,
        duration: str = "5",
        negative_prompt: str = "blur, distort, and low quality",
        cfg_scale: float = 0.5,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Kling v2.1."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="kling_2_1",
            duration=duration,
            negative_prompt=negative_prompt,
            cfg_scale=cfg_scale,
            **kwargs
        )

    # Information methods
    def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Get information about supported models."""
        if model:
            if model not in self.models:
                raise ValueError(f"Unknown model: {model}")
            return self.models[model].get_model_info()
        return {
            model_key: model_obj.get_model_info()
            for model_key, model_obj in self.models.items()
        }

    def get_supported_models(self) -> List[str]:
        """Get list of supported models."""
        return list(self.models.keys())

    def estimate_cost(self, model: str, duration: int, **kwargs) -> float:
        """Estimate cost for generation."""
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        return self.models[model].estimate_cost(duration, **kwargs)

    def compare_models(self) -> Dict[str, Dict[str, Any]]:
        """Compare all models with their features and pricing."""
        comparison = {}
        for model_key, model_obj in self.models.items():
            info = model_obj.get_model_info()
            comparison[model_key] = {
                "name": info.get("name", model_key),
                "provider": info.get("provider", "Unknown"),
                "price_per_second": model_obj.price_per_second,
                "max_duration": info.get("max_duration", 10),
                "features": info.get("features", [])
            }
        return comparison

    # Extended parameter methods
    def generate_with_interpolation(
        self,
        prompt: str,
        start_frame: str,
        end_frame: str,
        model: str = "kling_2_6_pro",
        duration: str = "5",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video interpolating between two frames.

        Only supported by Kling models.

        Args:
            prompt: Text description for video generation
            start_frame: Starting frame image path/URL
            end_frame: Ending frame image path/URL
            model: Model to use (default: "kling_2_6_pro")
            duration: Video duration
            **kwargs: Additional parameters

        Returns:
            Dictionary containing generation results
        """
        if model not in ["kling_2_1", "kling_2_6_pro"]:
            raise ValueError(
                f"Frame interpolation only supported by Kling models. "
                f"Got: {model}"
            )

        return self.generate_video(
            prompt=prompt,
            image_url=start_frame,
            model=model,
            start_frame=start_frame,
            end_frame=end_frame,
            duration=duration,
            **kwargs
        )

    def get_model_features(self, model: str) -> Dict[str, bool]:
        """
        Get extended feature support for a model.

        Args:
            model: Model key

        Returns:
            Dictionary of feature support flags
        """
        if model not in MODEL_EXTENDED_FEATURES:
            raise ValueError(f"Unknown model: {model}")
        return MODEL_EXTENDED_FEATURES[model].copy()

    def supports_feature(self, model: str, feature: str) -> bool:
        """
        Check if a model supports a specific feature.

        Args:
            model: Model key
            feature: Feature name (start_frame, end_frame, ref_images, etc.)

        Returns:
            True if feature is supported
        """
        features = MODEL_EXTENDED_FEATURES.get(model, {})
        return features.get(feature, False)
