"""
Image Generator Adapter for ViMax agents.

Wraps existing image generators (FAL, Replicate) to provide
a consistent interface for ViMax agents.
"""

import os
import time
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from pydantic import BaseModel, Field

from .base import BaseAdapter, AdapterConfig

# Try to import existing generators - fall back to direct FAL if not available
try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False


class ImageAdapterConfig(AdapterConfig):
    """Configuration for image adapter."""

    model: str = "nano_banana_pro"
    aspect_ratio: str = "1:1"
    num_inference_steps: int = 28
    guidance_scale: float = 3.5
    output_dir: str = "output/vimax/images"

    # Reference image settings for character consistency
    reference_model: str = "nano_banana_pro"  # Model for image-to-image with reference
    reference_strength: float = 0.6  # How much to follow reference (0.0-1.0)


class ImageOutput(BaseModel):
    """Image generation output."""

    image_path: str = Field(..., description="Path to generated image")
    image_url: Optional[str] = Field(default=None, description="URL if available")
    prompt: str = Field(default="", description="Prompt used for generation")
    model: str = Field(default="", description="Model used")
    width: int = Field(default=0)
    height: int = Field(default=0)
    generation_time: float = Field(default=0.0, description="Generation time in seconds")
    cost: float = Field(default=0.0, description="Generation cost in USD")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ImageGeneratorAdapter(BaseAdapter[str, ImageOutput]):
    """
    Adapter for image generation.

    Wraps FAL AI generators to provide a consistent interface for ViMax agents.

    Usage:
        adapter = ImageGeneratorAdapter(config)
        result = await adapter.generate("A samurai warrior")
    """

    # Model mapping to FAL endpoints (text-to-image)
    MODEL_MAP = {
        "flux_dev": "fal-ai/flux/dev",
        "flux_schnell": "fal-ai/flux/schnell",
        "imagen4": "google/imagen-4",
        "nano_banana_pro": "fal-ai/nano-banana-pro",
        "gpt_image_1_5": "fal-ai/gpt-image-1-5",
        "seedream_v3": "fal-ai/seedream-v3",
    }

    # Model mapping for image-to-image with reference (character consistency)
    REFERENCE_MODEL_MAP = {
        "nano_banana_pro": "fal-ai/nano-banana-pro/edit",  # Default, uses image_urls array
        "flux_kontext": "fal-ai/flux-kontext/max/image-to-image",
        "flux_redux": "fal-ai/flux-pro/v1.1-ultra/redux",
        "seededit_v3": "fal-ai/seededit-v3",
        "photon_flash": "fal-ai/photon/flash",
    }

    # Models that use image_urls array instead of image_url
    ARRAY_IMAGE_MODELS = {"nano_banana_pro"}

    # Cost estimates per image
    COST_MAP = {
        "flux_dev": 0.003,
        "flux_schnell": 0.001,
        "imagen4": 0.004,
        "nano_banana_pro": 0.002,
        "gpt_image_1_5": 0.003,
        "seedream_v3": 0.002,
        # Reference models (image-to-image costs)
        "nano_banana_pro_edit": 0.15,  # nano-banana-pro/edit costs $0.15/image
        "flux_kontext": 0.025,
        "flux_redux": 0.020,
        "seededit_v3": 0.025,
        "photon_flash": 0.015,
    }

    # Max inference steps per model
    MAX_STEPS_MAP = {
        "flux_dev": 50,
        "flux_schnell": 4,  # flux_schnell is fast, max 12 but 4 is recommended
        "imagen4": 50,
        "nano_banana_pro": 50,
        "gpt_image_1_5": 50,
        "seedream_v3": 50,
        # Reference models
        "flux_kontext": 28,
        "flux_redux": 28,
        "seededit_v3": 50,
        "photon_flash": 28,
    }

    def __init__(self, config: Optional[ImageAdapterConfig] = None):
        super().__init__(config or ImageAdapterConfig())
        self.config: ImageAdapterConfig = self.config
        self.logger = logging.getLogger("vimax.adapters.image")

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
        self.logger.info("Image adapter initialized with FAL")
        return True

    async def execute(self, prompt: str) -> ImageOutput:
        """Execute image generation."""
        return await self.generate(prompt)

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        output_path: Optional[str] = None,
        **kwargs,
    ) -> ImageOutput:
        """
        Generate image from text prompt.

        Args:
            prompt: Text description of desired image
            model: Model to use (default from config)
            aspect_ratio: Aspect ratio (default from config)
            output_path: Custom output path
            **kwargs: Additional generation parameters

        Returns:
            ImageOutput with generated image path and metadata
        """
        await self.ensure_initialized()

        model = model or self.config.model
        aspect_ratio = aspect_ratio or self.config.aspect_ratio

        self.logger.info(f"Generating image: model={model}, prompt={prompt[:50]}...")

        start_time = time.time()

        # Check if FAL is available and configured
        api_key = os.getenv('FAL_KEY')
        if not FAL_AVAILABLE or not api_key:
            # Mock mode
            return self._mock_generate(prompt, model, aspect_ratio, output_path, **kwargs)

        try:
            # Get FAL endpoint
            endpoint = self.MODEL_MAP.get(model, self.MODEL_MAP["flux_dev"])

            # Get model-specific max steps
            max_steps = self.MAX_STEPS_MAP.get(model, 28)
            requested_steps = kwargs.get("num_inference_steps", self.config.num_inference_steps)
            num_steps = min(requested_steps, max_steps)

            # Build arguments
            arguments = {
                "prompt": prompt,
                "image_size": self._aspect_to_size(aspect_ratio),
                "num_inference_steps": num_steps,
                "guidance_scale": kwargs.get("guidance_scale", self.config.guidance_scale),
            }

            # Call FAL (run in thread to avoid blocking the event loop)
            result = await asyncio.to_thread(
                fal_client.subscribe,
                endpoint,
                arguments=arguments,
                with_logs=False,
            )

            generation_time = time.time() - start_time

            # Extract image URL
            image_url = None
            if isinstance(result, dict):
                if "images" in result and result["images"]:
                    image_url = result["images"][0].get("url")
                elif "image" in result:
                    image_url = result["image"].get("url")

            # Determine output path
            if output_path:
                image_path = output_path
            else:
                output_dir = Path(self.config.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                image_path = str(output_dir / f"{model}_{int(time.time())}.png")

            # Download if we have a URL
            if image_url:
                self._download_image(image_url, image_path)

            return ImageOutput(
                image_path=image_path,
                image_url=image_url,
                prompt=prompt,
                model=model,
                width=result.get("width", 1024),
                height=result.get("height", 1024),
                generation_time=generation_time,
                cost=self.COST_MAP.get(model, 0.003),
                metadata={"aspect_ratio": aspect_ratio, **kwargs},
            )

        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise

    def _mock_generate(
        self,
        prompt: str,
        model: str,
        aspect_ratio: str,
        output_path: Optional[str],
        **kwargs,
    ) -> ImageOutput:
        """Mock image generation for testing without API keys."""
        self.logger.info("Using mock image generation")

        if output_path:
            image_path = output_path
        else:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            image_path = str(output_dir / f"mock_{model}_{int(time.time())}.png")

        # Create a placeholder file
        Path(image_path).parent.mkdir(parents=True, exist_ok=True)
        Path(image_path).write_text(f"Mock image: {prompt}")

        return ImageOutput(
            image_path=image_path,
            prompt=prompt,
            model=model,
            width=1024,
            height=1024,
            generation_time=0.1,
            cost=0.0,
            metadata={"mock": True, "aspect_ratio": aspect_ratio},
        )

    def _aspect_to_size(self, aspect_ratio: str) -> str:
        """Convert aspect ratio to size string."""
        sizes = {
            "1:1": "square",
            "16:9": "landscape_16_9",
            "9:16": "portrait_16_9",
            "4:3": "landscape_4_3",
            "3:4": "portrait_4_3",
        }
        return sizes.get(aspect_ratio, "square")

    def _download_image(self, url: str, path: str):
        """Download image from URL to path."""
        try:
            import urllib.request
            from urllib.parse import urlparse

            # Validate URL scheme to prevent SSRF or local file access
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Only http and https are allowed.")

            urllib.request.urlretrieve(url, path)
        except Exception as e:
            self.logger.warning(f"Failed to download image: {e}")

    async def generate_batch(
        self,
        prompts: List[str],
        model: Optional[str] = None,
        **kwargs,
    ) -> List[ImageOutput]:
        """
        Generate multiple images from prompts.

        Args:
            prompts: List of text prompts
            model: Model to use
            **kwargs: Additional parameters

        Returns:
            List of ImageOutput objects
        """
        results = []
        for i, prompt in enumerate(prompts):
            self.logger.info(f"Generating image {i+1}/{len(prompts)}")
            result = await self.generate(prompt, model=model, **kwargs)
            results.append(result)
        return results

    async def generate_with_reference(
        self,
        prompt: str,
        reference_image: str,
        model: Optional[str] = None,
        reference_strength: float = 0.6,
        aspect_ratio: Optional[str] = None,
        output_path: Optional[str] = None,
        **kwargs,
    ) -> ImageOutput:
        """
        Generate image using a reference image for character consistency.

        This method uses image-to-image models that can maintain visual
        consistency with a reference image (e.g., character portrait).

        Args:
            prompt: Text description of desired image
            reference_image: Path or URL to reference image
            model: Model to use (must support image-to-image, default: flux_kontext)
            reference_strength: How much to follow reference (0.0-1.0, default: 0.6)
            aspect_ratio: Output aspect ratio
            output_path: Custom output path
            **kwargs: Additional generation parameters

        Returns:
            ImageOutput with generated image path and metadata
        """
        await self.ensure_initialized()

        model = model or self.config.reference_model
        aspect_ratio = aspect_ratio or self.config.aspect_ratio

        self.logger.info(
            f"Generating image with reference: model={model}, "
            f"strength={reference_strength}, prompt={prompt[:50]}..."
        )

        start_time = time.time()

        # Check if FAL is available and configured
        api_key = os.getenv('FAL_KEY')
        if not FAL_AVAILABLE or not api_key:
            # Mock mode
            return self._mock_generate_with_reference(
                prompt, reference_image, model, reference_strength,
                aspect_ratio, output_path, **kwargs
            )

        try:
            # Convert local path to URL if needed
            reference_url = reference_image
            if reference_image and not reference_image.startswith("http"):
                reference_url = self._upload_to_fal(reference_image)

            # Get FAL endpoint for reference model
            endpoint = self.REFERENCE_MODEL_MAP.get(
                model,
                self.REFERENCE_MODEL_MAP["nano_banana_pro"]
            )

            # Build arguments based on model type
            if model in self.ARRAY_IMAGE_MODELS:
                # nano_banana_pro/edit uses different API format
                arguments = {
                    "prompt": prompt,
                    "image_urls": [reference_url],  # Array of image URLs
                    "aspect_ratio": aspect_ratio or "16:9",
                    "num_images": 1,
                }
            else:
                # Standard image-to-image models (flux_kontext, etc.)
                max_steps = self.MAX_STEPS_MAP.get(model, 28)
                requested_steps = kwargs.get("num_inference_steps", self.config.num_inference_steps)
                num_steps = min(requested_steps, max_steps)

                arguments = {
                    "prompt": prompt,
                    "image_url": reference_url,
                    "strength": reference_strength,
                    "image_size": self._aspect_to_size(aspect_ratio),
                    "num_inference_steps": num_steps,
                    "guidance_scale": kwargs.get("guidance_scale", self.config.guidance_scale),
                }

            # Call FAL (run in thread to avoid blocking the event loop)
            result = await asyncio.to_thread(
                fal_client.subscribe,
                endpoint,
                arguments=arguments,
                with_logs=False,
            )

            generation_time = time.time() - start_time

            # Extract image URL and dimensions
            image_url = None
            width = 1024
            height = 1024
            if isinstance(result, dict):
                if "images" in result and result["images"]:
                    img_data = result["images"][0]
                    image_url = img_data.get("url")
                    width = img_data.get("width") or 1024
                    height = img_data.get("height") or 1024
                elif "image" in result:
                    image_url = result["image"].get("url")
                    width = result.get("width") or 1024
                    height = result.get("height") or 1024

            # Determine output path
            if output_path:
                image_path = output_path
            else:
                output_dir = Path(self.config.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                image_path = str(output_dir / f"ref_{model}_{int(time.time())}.png")

            # Download if we have a URL
            if image_url:
                self._download_image(image_url, image_path)

            # Get cost - use _edit suffix for models with different edit pricing
            cost_key = f"{model}_edit" if model in self.ARRAY_IMAGE_MODELS else model
            cost = self.COST_MAP.get(cost_key, self.COST_MAP.get(model, 0.025))

            return ImageOutput(
                image_path=image_path,
                image_url=image_url,
                prompt=prompt,
                model=model,
                width=width,
                height=height,
                generation_time=generation_time,
                cost=cost,
                metadata={
                    "aspect_ratio": aspect_ratio,
                    "reference_image": reference_image,
                    "reference_strength": reference_strength,
                    "with_reference": True,
                    **kwargs,
                },
            )

        except Exception as e:
            self.logger.error(f"Image generation with reference failed: {e}")
            raise

    def _mock_generate_with_reference(
        self,
        prompt: str,
        reference_image: str,
        model: str,
        reference_strength: float,
        aspect_ratio: str,
        output_path: Optional[str],
        **kwargs,
    ) -> ImageOutput:
        """Mock image generation with reference for testing without API keys."""
        self.logger.info("Using mock image generation with reference")

        if output_path:
            image_path = output_path
        else:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            image_path = str(output_dir / f"mock_ref_{model}_{int(time.time())}.png")

        # Create a placeholder file
        Path(image_path).parent.mkdir(parents=True, exist_ok=True)
        Path(image_path).write_text(
            f"Mock image with reference\nPrompt: {prompt}\n"
            f"Reference: {reference_image}\nStrength: {reference_strength}"
        )

        return ImageOutput(
            image_path=image_path,
            prompt=prompt,
            model=model,
            width=1024,
            height=1024,
            generation_time=0.1,
            cost=0.0,
            metadata={
                "mock": True,
                "aspect_ratio": aspect_ratio,
                "reference_image": reference_image,
                "reference_strength": reference_strength,
                "with_reference": True,
            },
        )

    def _upload_to_fal(self, local_path: str) -> str:
        """
        Upload a local image file to FAL storage and return the URL.

        Args:
            local_path: Path to local image file

        Returns:
            URL of uploaded image on FAL storage
        """
        if not FAL_AVAILABLE:
            return local_path

        try:
            # FAL client provides upload functionality
            url = fal_client.upload_file(local_path)
            self.logger.debug(f"Uploaded {local_path} to {url}")
            return url
        except Exception as e:
            self.logger.warning(f"Failed to upload to FAL, using local path: {e}")
            return local_path

    def get_available_models(self) -> List[str]:
        """Return list of available text-to-image models."""
        return list(self.MODEL_MAP.keys())

    def get_available_reference_models(self) -> List[str]:
        """Return list of available image-to-image reference models."""
        return list(self.REFERENCE_MODEL_MAP.keys())

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a model."""
        is_reference = model in self.REFERENCE_MODEL_MAP
        endpoint = (
            self.REFERENCE_MODEL_MAP.get(model)
            if is_reference
            else self.MODEL_MAP.get(model, "unknown")
        )
        return {
            "model": model,
            "endpoint": endpoint,
            "cost": self.COST_MAP.get(model, 0.003),
            "supports_reference": is_reference,
        }

    def supports_reference_images(self, model: str) -> bool:
        """Check if a model supports reference image input."""
        return model in self.REFERENCE_MODEL_MAP


# Convenience function
async def generate_image(prompt: str, model: str = "nano_banana_pro", **kwargs) -> ImageOutput:
    """Quick function to generate a single image."""
    adapter = ImageGeneratorAdapter(ImageAdapterConfig(model=model))
    return await adapter.generate(prompt, **kwargs)


async def generate_image_with_reference(
    prompt: str,
    reference_image: str,
    model: str = "flux_kontext",
    reference_strength: float = 0.6,
    **kwargs,
) -> ImageOutput:
    """Quick function to generate an image with a reference."""
    adapter = ImageGeneratorAdapter(ImageAdapterConfig(reference_model=model))
    return await adapter.generate_with_reference(
        prompt, reference_image, model=model,
        reference_strength=reference_strength, **kwargs
    )
