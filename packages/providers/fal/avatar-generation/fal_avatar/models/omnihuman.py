"""OmniHuman v1.5 model implementation."""

from typing import Any, Dict, Optional

from .base import BaseAvatarModel, AvatarGenerationResult
from ..config.constants import (
    MODEL_ENDPOINTS,
    MODEL_PRICING,
    MODEL_DEFAULTS,
    SUPPORTED_RESOLUTIONS,
    MAX_DURATIONS,
)


class OmniHumanModel(BaseAvatarModel):
    """
    ByteDance OmniHuman v1.5 - Audio-driven human animation.

    Generates realistic videos where character emotions and movements
    correlate with audio input.

    Pricing: $0.16/second
    Max Duration: 30s (1080p), 60s (720p)
    """

    def __init__(self):
        """Initialize OmniHuman model."""
        super().__init__("omnihuman_v1_5")
        self.endpoint = MODEL_ENDPOINTS["omnihuman_v1_5"]
        self.pricing = MODEL_PRICING["omnihuman_v1_5"]
        self.supported_resolutions = SUPPORTED_RESOLUTIONS["omnihuman_v1_5"]
        self.defaults = MODEL_DEFAULTS["omnihuman_v1_5"]
        self.max_durations = MAX_DURATIONS["omnihuman_v1_5"]

    def validate_parameters(
        self,
        image_url: str,
        audio_url: str,
        resolution: Optional[str] = None,
        turbo_mode: Optional[bool] = None,
        prompt: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate and prepare parameters for OmniHuman.

        Args:
            image_url: Human figure image URL
            audio_url: Audio file URL
            resolution: Output resolution (720p or 1080p)
            turbo_mode: Enable faster generation with slight quality trade-off
            prompt: Optional text guidance

        Returns:
            Dict of validated parameters
        """
        # Validate required parameters
        self._validate_url(image_url, "image_url")
        self._validate_url(audio_url, "audio_url")

        # Apply defaults
        resolution = resolution or self.defaults["resolution"]
        turbo_mode = turbo_mode if turbo_mode is not None else self.defaults["turbo_mode"]

        # Validate resolution
        self._validate_resolution(resolution)

        # Set max duration based on resolution
        self.max_duration = self.max_durations.get(resolution, 30)

        # Build arguments
        arguments = {
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": resolution,
            "turbo_mode": turbo_mode,
        }

        if prompt:
            arguments["prompt"] = prompt

        return arguments

    def generate(
        self,
        image_url: str,
        audio_url: str,
        resolution: Optional[str] = None,
        turbo_mode: Optional[bool] = None,
        prompt: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate video with OmniHuman v1.5.

        Args:
            image_url: Human figure image URL
            audio_url: Audio file URL (max 30s @1080p, 60s @720p)
            resolution: Output resolution (default: 1080p)
            turbo_mode: Faster generation with slight quality trade-off
            prompt: Optional text guidance

        Returns:
            AvatarGenerationResult with video URL
        """
        try:
            # Validate and prepare arguments
            arguments = self.validate_parameters(
                image_url=image_url,
                audio_url=audio_url,
                resolution=resolution,
                turbo_mode=turbo_mode,
                prompt=prompt,
            )

            # Call FAL API
            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response["error"],
                    model_used=self.model_name,
                    processing_time=response["processing_time"],
                )

            result = response["result"]
            duration = result.get("duration", 0)

            return AvatarGenerationResult(
                success=True,
                video_url=result["video"]["url"],
                duration=duration,
                cost=self.estimate_cost(duration),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={
                    "resolution": arguments["resolution"],
                    "turbo_mode": arguments["turbo_mode"],
                },
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name,
            )

    def estimate_cost(self, duration: float, **kwargs) -> float:
        """
        Estimate cost based on video duration.

        Args:
            duration: Video duration in seconds

        Returns:
            Estimated cost in USD
        """
        return duration * self.pricing["per_second"]

    def get_model_info(self) -> Dict[str, Any]:
        """Return model capabilities and metadata."""
        return {
            "name": self.model_name,
            "display_name": "OmniHuman v1.5 (ByteDance)",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "supported_resolutions": self.supported_resolutions,
            "max_duration": self.max_durations,
            "input_types": ["image", "audio"],
            "description": "Audio-driven human animation with realistic emotion correlation",
            "best_for": ["talking heads", "presentations", "avatar animations"],
        }
