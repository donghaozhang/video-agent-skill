"""FAL AI Avatar Multi model - Multi-person conversational video generation."""

from typing import Any, Dict, Optional

from .base import BaseAvatarModel, AvatarGenerationResult
from ..config.constants import MODEL_ENDPOINTS, MODEL_PRICING, MODEL_DEFAULTS


class MultiTalkModel(BaseAvatarModel):
    """
    FAL AI Avatar Multi - Native multi-person conversation video generation.

    Generates realistic videos where multiple people speak in sequence,
    driven by separate audio files for each person.

    Endpoint: fal-ai/ai-avatar/multi
    Pricing: Base rate at 480p, 2x at 720p, 1.25x for >81 frames
    """

    def __init__(self):
        """Initialize MultiTalk model."""
        super().__init__("multitalk")
        self.endpoint = MODEL_ENDPOINTS["multitalk"]
        self.pricing = MODEL_PRICING["multitalk"]
        self.defaults = MODEL_DEFAULTS["multitalk"]
        self.supported_resolutions = ["480p", "720p"]
        self.supported_accelerations = ["none", "regular", "high"]

    def validate_parameters(
        self,
        image_url: str,
        first_audio_url: str,
        prompt: str,
        second_audio_url: Optional[str] = None,
        num_frames: Optional[int] = None,
        resolution: Optional[str] = None,
        seed: Optional[int] = None,
        acceleration: Optional[str] = None,
        use_only_first_audio: Optional[bool] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate and prepare parameters for FAL AI Avatar Multi.

        Args:
            image_url: URL of input image containing person(s)
            first_audio_url: URL of Person 1 audio file
            prompt: Text description guiding video generation
            second_audio_url: Optional URL of Person 2 audio file
            num_frames: Frame count (81-129, default 81)
            resolution: Output resolution ("480p" or "720p")
            seed: Random seed for reproducibility
            acceleration: Speed mode ("none", "regular", "high")
            use_only_first_audio: Ignore second audio if provided

        Returns:
            Dict of validated parameters

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate required parameters
        self._validate_url(image_url, "image_url")
        self._validate_url(first_audio_url, "first_audio_url")
        if not prompt or not prompt.strip():
            raise ValueError("prompt is required and cannot be empty")

        # Apply defaults
        num_frames = num_frames if num_frames is not None else self.defaults.get("num_frames", 81)
        resolution = resolution or self.defaults.get("resolution", "480p")
        acceleration = acceleration or self.defaults.get("acceleration", "regular")

        # Validate ranges
        if not (81 <= num_frames <= 129):
            raise ValueError(f"num_frames must be 81-129, got {num_frames}")
        if resolution not in self.supported_resolutions:
            raise ValueError(f"resolution must be one of {self.supported_resolutions}, got {resolution}")
        if acceleration not in self.supported_accelerations:
            raise ValueError(f"acceleration must be one of {self.supported_accelerations}, got {acceleration}")

        # Build arguments
        arguments = {
            "image_url": image_url,
            "first_audio_url": first_audio_url,
            "prompt": prompt,
            "num_frames": num_frames,
            "resolution": resolution,
            "acceleration": acceleration,
        }

        if second_audio_url:
            self._validate_url(second_audio_url, "second_audio_url")
            arguments["second_audio_url"] = second_audio_url

        if seed is not None:
            arguments["seed"] = seed

        if use_only_first_audio is not None:
            arguments["use_only_first_audio"] = use_only_first_audio

        return arguments

    def generate(
        self,
        image_url: Optional[str] = None,
        first_audio_url: Optional[str] = None,
        prompt: Optional[str] = None,
        second_audio_url: Optional[str] = None,
        num_frames: int = 81,
        resolution: str = "480p",
        seed: Optional[int] = None,
        acceleration: str = "regular",
        use_only_first_audio: Optional[bool] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate multi-person conversation video.

        Args:
            image_url: URL of input image containing person(s)
            first_audio_url: URL of Person 1 audio file
            prompt: Text description guiding video generation
            second_audio_url: Optional URL of Person 2 audio file
            num_frames: Frame count (81-129, default 81)
            resolution: Output resolution ("480p" or "720p")
            seed: Random seed for reproducibility
            acceleration: Speed mode ("none", "regular", "high")
            use_only_first_audio: Ignore second audio if provided

        Returns:
            AvatarGenerationResult with video URL and metadata
        """
        try:
            arguments = self.validate_parameters(
                image_url=image_url,
                first_audio_url=first_audio_url,
                prompt=prompt,
                second_audio_url=second_audio_url,
                num_frames=num_frames,
                resolution=resolution,
                seed=seed,
                acceleration=acceleration,
                use_only_first_audio=use_only_first_audio,
            )

            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response["error"],
                    model_used=self.model_name,
                    processing_time=response.get("processing_time"),
                )

            result = response["result"]

            return AvatarGenerationResult(
                success=True,
                video_url=result["video"]["url"],
                cost=self.estimate_cost(num_frames, resolution),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={
                    "resolution": resolution,
                    "num_frames": num_frames,
                    "acceleration": acceleration,
                    "seed": result.get("seed"),
                    "file_size": result["video"].get("file_size"),
                    "file_name": result["video"].get("file_name"),
                    "has_second_person": second_audio_url is not None,
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
        num_frames: int = 81,
        resolution: str = "480p",
        **kwargs,
    ) -> float:
        """
        Estimate generation cost.

        Args:
            num_frames: Number of frames (81-129)
            resolution: "480p" or "720p"

        Returns:
            Estimated cost in USD
        """
        base_cost = self.pricing.get("base", 0.10)

        # Resolution multiplier (720p = 2x)
        if resolution == "720p":
            base_cost *= self.pricing.get("720p_multiplier", 2.0)

        # Frame count multiplier (>81 frames = 1.25x)
        if num_frames > 81:
            base_cost *= self.pricing.get("extended_frames_multiplier", 1.25)

        return base_cost

    def get_model_info(self) -> Dict[str, Any]:
        """Return model capabilities and metadata."""
        return {
            "name": self.model_name,
            "display_name": "AI Avatar Multi (FAL)",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "supported_resolutions": self.supported_resolutions,
            "frame_range": {"min": 81, "max": 129},
            "acceleration_modes": self.supported_accelerations,
            "input_types": ["image", "audio", "audio_second"],
            "description": "Multi-person conversational video with lip-sync",
            "best_for": ["conversations", "podcasts", "interviews", "dual speakers"],
            "commercial_use": True,
        }
