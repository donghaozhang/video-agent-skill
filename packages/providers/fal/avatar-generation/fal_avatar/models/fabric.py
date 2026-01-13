"""VEED Fabric 1.0 model implementations."""

from typing import Any, Dict, Optional

from .base import BaseAvatarModel, AvatarGenerationResult
from ..config.constants import (
    MODEL_ENDPOINTS,
    MODEL_PRICING,
    MODEL_DEFAULTS,
    SUPPORTED_RESOLUTIONS,
)


class FabricModel(BaseAvatarModel):
    """
    VEED Fabric 1.0 - Lipsync video from image + audio.

    Creates talking videos by synchronizing lip movements with audio.

    Pricing: $0.08/sec (480p), $0.15/sec (720p)
    Fast variant: +25% cost
    """

    def __init__(self, fast: bool = False):
        """
        Initialize Fabric model.

        Args:
            fast: Use fast variant for quicker processing
        """
        model_name = "fabric_1_0_fast" if fast else "fabric_1_0"
        super().__init__(model_name)
        self.endpoint = MODEL_ENDPOINTS[model_name]
        self.pricing = MODEL_PRICING[model_name]
        self.supported_resolutions = SUPPORTED_RESOLUTIONS[model_name]
        self.defaults = MODEL_DEFAULTS.get("fabric_1_0", {"resolution": "720p"})
        self.is_fast = fast
        self.max_duration = 120

    def validate_parameters(
        self,
        image_url: str,
        audio_url: str,
        resolution: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate parameters for Fabric model.

        Args:
            image_url: Image source URL (face/portrait)
            audio_url: Audio file URL for lipsync
            resolution: Output resolution (480p or 720p)

        Returns:
            Dict of validated parameters
        """
        self._validate_url(image_url, "image_url")
        self._validate_url(audio_url, "audio_url")

        resolution = resolution or self.defaults["resolution"]
        self._validate_resolution(resolution)

        return {
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": resolution,
        }

    def generate(
        self,
        image_url: str,
        audio_url: str,
        resolution: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate lipsync video with Fabric.

        Args:
            image_url: Image source URL (face/portrait)
            audio_url: Audio file URL
            resolution: Output resolution (default: 720p)

        Returns:
            AvatarGenerationResult with video URL
        """
        try:
            arguments = self.validate_parameters(
                image_url=image_url,
                audio_url=audio_url,
                resolution=resolution,
            )

            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response["error"],
                    model_used=self.model_name,
                    processing_time=response["processing_time"],
                )

            result = response["result"]
            # Extract video URL from response
            video_url = result.get("url") or result.get("video", {}).get("url")

            # Estimate duration from kwargs or default to 10s
            duration = kwargs.get("estimated_duration", 10)

            return AvatarGenerationResult(
                success=True,
                video_url=video_url,
                duration=duration,
                cost=self.estimate_cost(duration, resolution=arguments["resolution"]),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={
                    "resolution": arguments["resolution"],
                    "fast_mode": self.is_fast,
                },
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name,
            )

    def estimate_cost(
        self,
        duration: float,
        resolution: Optional[str] = None,
        **kwargs,
    ) -> float:
        """
        Estimate cost based on duration and resolution.

        Args:
            duration: Video duration in seconds
            resolution: Video resolution (480p or 720p)

        Returns:
            Estimated cost in USD
        """
        resolution = resolution or "720p"
        price_per_second = self.pricing.get(resolution, self.pricing.get("720p", 0.15))
        return duration * price_per_second

    def get_model_info(self) -> Dict[str, Any]:
        """Return model info."""
        return {
            "name": self.model_name,
            "display_name": f"VEED Fabric 1.0{' Fast' if self.is_fast else ''}",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "supported_resolutions": self.supported_resolutions,
            "max_duration": self.max_duration,
            "input_types": ["image", "audio"],
            "description": "Lipsync video generation from image and audio",
            "best_for": ["lipsync", "dubbing", "social media"],
        }


class FabricTextModel(BaseAvatarModel):
    """
    VEED Fabric 1.0 Text - Text-to-speech avatar.

    Converts text to speech and animates the image to speak.

    Pricing: $0.08/sec (480p), $0.15/sec (720p)
    """

    def __init__(self):
        """Initialize Fabric Text model."""
        super().__init__("fabric_1_0_text")
        self.endpoint = MODEL_ENDPOINTS["fabric_1_0_text"]
        self.pricing = MODEL_PRICING["fabric_1_0_text"]
        self.supported_resolutions = SUPPORTED_RESOLUTIONS["fabric_1_0_text"]
        self.defaults = MODEL_DEFAULTS.get("fabric_1_0_text", {"resolution": "720p"})
        self.max_duration = 120
        self.max_text_length = 2000

    def validate_parameters(
        self,
        image_url: str,
        text: str,
        resolution: Optional[str] = None,
        voice_description: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate parameters for Fabric Text model.

        Args:
            image_url: Image source URL (face/portrait)
            text: Speech text (max 2000 characters)
            resolution: Output resolution (480p or 720p)
            voice_description: Voice characteristics

        Returns:
            Dict of validated parameters
        """
        self._validate_url(image_url, "image_url")

        if not text:
            raise ValueError("Text is required")
        if len(text) > self.max_text_length:
            raise ValueError(f"Text exceeds maximum length of {self.max_text_length} characters")

        resolution = resolution or self.defaults["resolution"]
        self._validate_resolution(resolution)

        arguments = {
            "image_url": image_url,
            "text": text,
            "resolution": resolution,
        }

        if voice_description:
            arguments["voice_description"] = voice_description

        return arguments

    def generate(
        self,
        image_url: str,
        text: str,
        resolution: Optional[str] = None,
        voice_description: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate TTS avatar video with Fabric Text.

        Args:
            image_url: Image source URL
            text: Speech text (max 2000 chars)
            resolution: Output resolution (default: 720p)
            voice_description: Voice characteristics

        Returns:
            AvatarGenerationResult with video URL
        """
        try:
            arguments = self.validate_parameters(
                image_url=image_url,
                text=text,
                resolution=resolution,
                voice_description=voice_description,
            )

            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response["error"],
                    model_used=self.model_name,
                    processing_time=response["processing_time"],
                )

            result = response["result"]
            video_url = result.get("video", {}).get("url")

            # Estimate duration: ~150 words per minute, average 5 chars per word
            estimated_duration = len(text) / 5 / 150 * 60

            return AvatarGenerationResult(
                success=True,
                video_url=video_url,
                duration=estimated_duration,
                cost=self.estimate_cost(estimated_duration, resolution=arguments["resolution"]),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={
                    "resolution": arguments["resolution"],
                    "text_length": len(text),
                    "voice_description": voice_description,
                },
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name,
            )

    def estimate_cost(
        self,
        duration: float,
        resolution: Optional[str] = None,
        **kwargs,
    ) -> float:
        """
        Estimate cost based on duration and resolution.

        Args:
            duration: Video duration in seconds
            resolution: Video resolution

        Returns:
            Estimated cost in USD
        """
        resolution = resolution or "720p"
        price_per_second = self.pricing.get(resolution, self.pricing.get("720p", 0.15))
        return duration * price_per_second

    def get_model_info(self) -> Dict[str, Any]:
        """Return model info."""
        return {
            "name": self.model_name,
            "display_name": "VEED Fabric 1.0 Text-to-Speech",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "supported_resolutions": self.supported_resolutions,
            "max_duration": self.max_duration,
            "max_text_length": self.max_text_length,
            "input_types": ["image", "text"],
            "description": "Text-to-speech avatar video generation",
            "best_for": ["quick avatars", "no pre-recorded audio"],
        }
