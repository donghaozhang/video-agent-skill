"""
Video Generator Adapter for ViMax agents.

Wraps existing video generators (FAL Kling, Veo, etc.) to provide
a consistent interface for ViMax agents.
"""

import os
import time
import asyncio
import subprocess
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from pydantic import BaseModel, Field

from .base import BaseAdapter, AdapterConfig

# Try to import FAL client
try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False


class VideoAdapterConfig(AdapterConfig):
    """Configuration for video adapter."""

    model: str = "kling"
    duration: float = 5.0
    fps: int = 24
    output_dir: str = "output/vimax/videos"


class VideoOutput(BaseModel):
    """Video generation output."""

    video_path: str = Field(..., description="Path to generated video")
    video_url: Optional[str] = Field(default=None, description="URL if available")
    source_image: Optional[str] = Field(default=None, description="Source image path")
    prompt: str = Field(default="", description="Prompt used for generation")
    model: str = Field(default="", description="Model used")
    duration: float = Field(default=0.0, description="Video duration in seconds")
    width: int = Field(default=0)
    height: int = Field(default=0)
    fps: int = Field(default=24)
    generation_time: float = Field(default=0.0)
    cost: float = Field(default=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VideoGeneratorAdapter(BaseAdapter[Dict[str, Any], VideoOutput]):
    """
    Adapter for video generation.

    Wraps FAL Image-to-Video generators to provide a consistent interface
    for ViMax agents.

    Usage:
        adapter = VideoGeneratorAdapter(config)
        result = await adapter.generate(
            image_path="input.png",
            prompt="Character walking forward"
        )
    """

    # Model mapping to FAL endpoints
    MODEL_MAP = {
        "kling": "fal-ai/kling-video/v1/standard/image-to-video",
        "kling_2_1": "fal-ai/kling-video/v2.1/standard/image-to-video",
        "kling_2_6_pro": "fal-ai/kling-video/v2.6/pro/image-to-video",
        "veo3": "google/veo-3",
        "veo3_fast": "google/veo-3-fast",
        "hailuo": "fal-ai/hailuo/image-to-video",
        "grok_imagine": "fal-ai/grok/imagine",
    }

    # Cost estimates per second
    COST_PER_SECOND = {
        "kling": 0.03,
        "kling_2_1": 0.03,
        "kling_2_6_pro": 0.06,
        "veo3": 0.10,
        "veo3_fast": 0.06,
        "hailuo": 0.02,
        "grok_imagine": 0.05,
    }

    def __init__(self, config: Optional[VideoAdapterConfig] = None):
        super().__init__(config or VideoAdapterConfig())
        self.config: VideoAdapterConfig = self.config
        self.logger = logging.getLogger("vimax.adapters.video")

    async def initialize(self) -> bool:
        """Initialize the FAL client."""
        if not FAL_AVAILABLE:
            self.logger.warning("FAL client not available - using mock mode")
            return True

        api_key = os.getenv('FAL_KEY')
        if not api_key:
            self.logger.warning("FAL_KEY not set - using mock mode")
            return True

        fal_client.api_key = api_key
        self.logger.info("Video adapter initialized with FAL")
        return True

    async def execute(self, input_data: Dict[str, Any]) -> VideoOutput:
        """Execute video generation."""
        return await self.generate(**input_data)

    async def generate(
        self,
        image_path: str,
        prompt: str,
        model: Optional[str] = None,
        duration: Optional[float] = None,
        output_path: Optional[str] = None,
        **kwargs,
    ) -> VideoOutput:
        """
        Generate video from image and prompt.

        Args:
            image_path: Path to source image
            prompt: Motion/animation description
            model: Video model to use
            duration: Video duration in seconds
            output_path: Custom output path
            **kwargs: Additional parameters

        Returns:
            VideoOutput with generated video path and metadata
        """
        await self.ensure_initialized()

        model = model or self.config.model
        duration = duration or self.config.duration

        self.logger.info(f"Generating video: model={model}, duration={duration}s")

        start_time = time.time()

        # Check if FAL is available and configured
        api_key = os.getenv('FAL_KEY')
        if not FAL_AVAILABLE or not api_key:
            return self._mock_generate(image_path, prompt, model, duration, output_path, **kwargs)

        try:
            # Get FAL endpoint
            endpoint = self.MODEL_MAP.get(model, self.MODEL_MAP["kling"])

            # Upload image if it's a local path
            if os.path.exists(image_path):
                image_url = fal_client.upload_file(image_path)
            else:
                image_url = image_path

            # Build arguments
            arguments = {
                "prompt": prompt,
                "image_url": image_url,
                "duration": str(int(duration)),
            }

            # Call FAL
            result = fal_client.subscribe(
                endpoint,
                arguments=arguments,
                with_logs=False,
            )

            generation_time = time.time() - start_time

            # Extract video URL
            video_url = None
            if isinstance(result, dict):
                video_url = result.get("video", {}).get("url") or result.get("video_url")

            # Determine output path
            if output_path:
                video_path = output_path
            else:
                output_dir = Path(self.config.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                video_path = str(output_dir / f"{model}_{int(time.time())}.mp4")

            # Download if we have a URL
            if video_url:
                self._download_video(video_url, video_path)

            return VideoOutput(
                video_path=video_path,
                video_url=video_url,
                source_image=image_path,
                prompt=prompt,
                model=model,
                duration=duration,
                width=result.get("width", 1280),
                height=result.get("height", 720),
                fps=self.config.fps,
                generation_time=generation_time,
                cost=self._estimate_cost(model, duration),
                metadata=kwargs,
            )

        except Exception as e:
            self.logger.error(f"Video generation failed: {e}")
            raise

    def _mock_generate(
        self,
        image_path: str,
        prompt: str,
        model: str,
        duration: float,
        output_path: Optional[str],
        **kwargs,
    ) -> VideoOutput:
        """Mock video generation for testing without API keys."""
        self.logger.info("Using mock video generation")

        if output_path:
            video_path = output_path
        else:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            video_path = str(output_dir / f"mock_{model}_{int(time.time())}.mp4")

        # Create a placeholder file
        Path(video_path).parent.mkdir(parents=True, exist_ok=True)
        Path(video_path).write_text(f"Mock video: {prompt}")

        return VideoOutput(
            video_path=video_path,
            source_image=image_path,
            prompt=prompt,
            model=model,
            duration=duration,
            width=1280,
            height=720,
            fps=24,
            generation_time=0.1,
            cost=0.0,
            metadata={"mock": True},
        )

    def _download_video(self, url: str, path: str):
        """Download video from URL to path."""
        try:
            import urllib.request
            urllib.request.urlretrieve(url, path)
        except Exception as e:
            self.logger.warning(f"Failed to download video: {e}")

    def _estimate_cost(self, model: str, duration: float) -> float:
        """Estimate generation cost based on model and duration."""
        return self.COST_PER_SECOND.get(model, 0.03) * duration

    async def generate_from_images(
        self,
        images: List[Any],
        prompts: List[str],
        model: Optional[str] = None,
        **kwargs,
    ) -> List[VideoOutput]:
        """
        Generate videos from multiple images.

        Args:
            images: List of image paths or ImageOutput objects
            prompts: List of prompts (one per image)
            model: Video model to use
            **kwargs: Additional parameters

        Returns:
            List of VideoOutput objects
        """
        if len(images) != len(prompts):
            raise ValueError("Number of images must match number of prompts")

        results = []
        for i, (img, prompt) in enumerate(zip(images, prompts)):
            self.logger.info(f"Generating video {i+1}/{len(images)}")

            # Handle both string paths and ImageOutput objects
            if hasattr(img, 'image_path'):
                image_path = img.image_path
            else:
                image_path = str(img)

            result = await self.generate(
                image_path=image_path,
                prompt=prompt,
                model=model,
                **kwargs,
            )
            results.append(result)

        return results

    async def concatenate_videos(
        self,
        videos: List[VideoOutput],
        output_path: str,
    ) -> VideoOutput:
        """
        Concatenate multiple videos into one.

        Args:
            videos: List of videos to concatenate
            output_path: Output path for final video

        Returns:
            VideoOutput for concatenated video
        """
        self.logger.info(f"Concatenating {len(videos)} videos")

        # Create concat file
        concat_file = Path(output_path).parent / "concat_list.txt"
        concat_file.parent.mkdir(parents=True, exist_ok=True)

        with open(concat_file, "w") as f:
            for video in videos:
                # Use forward slashes and escape special characters
                video_path = video.video_path.replace("\\", "/")
                f.write(f"file '{video_path}'\n")

        try:
            # Run ffmpeg
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                output_path,
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                self.logger.warning(f"FFmpeg concat may have failed: {stderr.decode()}")
                # Create a placeholder if ffmpeg failed
                Path(output_path).write_text("Concatenated video placeholder")

        except FileNotFoundError:
            self.logger.warning("FFmpeg not found - creating placeholder")
            Path(output_path).write_text("Concatenated video placeholder")

        finally:
            # Cleanup
            if concat_file.exists():
                concat_file.unlink()

        total_duration = sum(v.duration for v in videos)
        total_cost = sum(v.cost for v in videos)

        return VideoOutput(
            video_path=output_path,
            duration=total_duration,
            cost=total_cost,
            metadata={"source_videos": [v.video_path for v in videos]},
        )

    def get_available_models(self) -> List[str]:
        """Return list of available models."""
        return list(self.MODEL_MAP.keys())


# Convenience function
async def generate_video(
    image_path: str,
    prompt: str,
    model: str = "kling",
    duration: float = 5.0,
    **kwargs,
) -> VideoOutput:
    """Quick function to generate a single video."""
    adapter = VideoGeneratorAdapter(VideoAdapterConfig(model=model, duration=duration))
    return await adapter.generate(image_path, prompt, **kwargs)
