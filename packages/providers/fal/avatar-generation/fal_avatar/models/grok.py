"""xAI Grok Imagine Video Edit model implementation."""

from typing import Any, Dict, Optional

from .base import BaseAvatarModel, AvatarGenerationResult
from ..config.constants import (
    MODEL_ENDPOINTS,
    MODEL_PRICING,
    MODEL_DEFAULTS,
    SUPPORTED_RESOLUTIONS,
    MAX_DURATIONS,
)


class GrokVideoEditModel(BaseAvatarModel):
    """
    xAI Grok Imagine Video Edit - Video-to-Video editing.

    Edit videos with text prompts for effects like colorization,
    style transfer, and other visual transformations.

    Input: Videos resized to max 854x480, truncated to 8 seconds
    Pricing: $0.01/s input + $0.05/s output (~$0.36 for 6s)
    Max Duration: 8 seconds (input automatically truncated)
    Max Prompt: 4,096 characters
    """

    MODEL_KEY = "grok_video_edit"

    def __init__(self):
        """Initialize Grok Video Edit model."""
        super().__init__("grok_video_edit")
        self.endpoint = MODEL_ENDPOINTS["grok_video_edit"]
        self.pricing = MODEL_PRICING["grok_video_edit"]
        self.supported_resolutions = SUPPORTED_RESOLUTIONS["grok_video_edit"]
        self.defaults = MODEL_DEFAULTS["grok_video_edit"]
        self.max_duration = MAX_DURATIONS["grok_video_edit"]
        self.max_prompt_length = 4096

    def validate_parameters(
        self,
        video_url: str,
        prompt: str,
        resolution: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate parameters for Grok Video Edit.

        Args:
            video_url: URL of input video to edit
            prompt: Text description of desired edit (max 4096 chars)
            resolution: Output resolution - "auto", "480p", "720p" (default: auto)

        Returns:
            Dict of validated parameters

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate video_url
        self._validate_url(video_url, "video_url")

        # Validate prompt (reject empty or whitespace-only)
        if not prompt or not prompt.strip():
            raise ValueError("prompt is required and cannot be whitespace-only")
        if len(prompt) > self.max_prompt_length:
            raise ValueError(
                f"prompt exceeds maximum length of {self.max_prompt_length} characters "
                f"(got {len(prompt)})"
            )

        # Apply defaults and validate resolution
        resolution = resolution or self.defaults["resolution"]
        self._validate_resolution(resolution)

        return {
            "video_url": video_url,
            "prompt": prompt,
            "resolution": resolution,
        }

    def generate(
        self,
        video_url: str,
        prompt: str,
        resolution: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Edit video with text prompt.

        Args:
            video_url: URL of input video to edit
            prompt: Text description of desired edit
            resolution: Output resolution (default: auto)

        Returns:
            AvatarGenerationResult with edited video URL
        """
        try:
            arguments = self.validate_parameters(
                video_url=video_url,
                prompt=prompt,
                resolution=resolution,
                **kwargs,
            )

            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response.get("error", "Unknown error"),
                    processing_time=response.get("processing_time"),
                    model_used=self.model_name,
                )

            result = response["result"]
            video_info = result.get("video", {})
            # Guard against None duration from API
            video_duration = video_info.get("duration")
            duration_for_cost = video_duration if video_duration is not None else 6

            return AvatarGenerationResult(
                success=True,
                video_url=video_info.get("url"),
                duration=video_duration,
                cost=self.estimate_cost(
                    duration=duration_for_cost,
                    input_duration=min(8, duration_for_cost),
                ),
                processing_time=response.get("processing_time"),
                model_used=self.model_name,
                metadata={
                    "width": video_info.get("width"),
                    "height": video_info.get("height"),
                    "fps": video_info.get("fps"),
                    "num_frames": video_info.get("num_frames"),
                    "content_type": video_info.get("content_type"),
                    "file_name": video_info.get("file_name"),
                    "resolution": arguments["resolution"],
                },
            )

        except ValueError as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name,
            )
        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=f"Generation failed: {str(e)}",
                model_used=self.model_name,
            )

    def estimate_cost(
        self,
        duration: float = 6,
        input_duration: Optional[float] = None,
        **kwargs,
    ) -> float:
        """
        Estimate cost based on input and output duration.

        Pricing: $0.01/s input + $0.05/s output
        For 6s video: $0.06 input + $0.30 output = $0.36

        Args:
            duration: Output video duration in seconds
            input_duration: Input video duration (defaults to output duration)

        Returns:
            Estimated cost in USD
        """
        input_duration = input_duration or duration
        # Input is capped at 8 seconds
        input_duration = min(input_duration, self.max_duration)

        input_cost = self.pricing["input_per_second"] * input_duration
        output_cost = self.pricing["output_per_second"] * duration

        return input_cost + output_cost

    def get_model_info(self) -> Dict[str, Any]:
        """
        Return model capabilities and metadata.

        Returns:
            Dict containing model information
        """
        return {
            "name": "xAI Grok Video Edit",
            "provider": "xAI (via FAL)",
            "endpoint": self.endpoint,
            "description": "Edit videos with text prompts for colorization, style transfer, and visual transformations",
            "max_duration": self.max_duration,
            "max_prompt_length": self.max_prompt_length,
            "supported_resolutions": self.supported_resolutions,
            "pricing": self.pricing,
            "input_constraints": {
                "max_resolution": "854x480",
                "max_duration": "8 seconds (auto-truncated)",
            },
            "features": [
                "video_editing",
                "colorization",
                "style_transfer",
                "visual_effects",
            ],
        }
