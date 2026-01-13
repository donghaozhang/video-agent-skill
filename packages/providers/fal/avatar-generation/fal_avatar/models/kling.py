"""Kling O1 model implementations for reference and video-to-video."""

from typing import Any, Dict, List, Optional

from .base import BaseAvatarModel, AvatarGenerationResult
from ..config.constants import (
    MODEL_ENDPOINTS,
    MODEL_PRICING,
    MODEL_DEFAULTS,
    SUPPORTED_ASPECT_RATIOS,
    MAX_DURATIONS,
)


class KlingRefToVideoModel(BaseAvatarModel):
    """
    Kling O1 Reference-to-Video - Character/element consistency.

    Upload up to 4 reference images defining people, objects, or settings,
    then generate videos with visual coherence across elements.

    Pricing: $0.112/second
    Max Duration: 10 seconds per generation
    Max References: 4 images
    """

    def __init__(self):
        """Initialize Kling Reference-to-Video model."""
        super().__init__("kling_ref_to_video")
        self.endpoint = MODEL_ENDPOINTS["kling_ref_to_video"]
        self.pricing = MODEL_PRICING["kling_ref_to_video"]
        self.supported_aspect_ratios = SUPPORTED_ASPECT_RATIOS["kling_ref_to_video"]
        self.defaults = MODEL_DEFAULTS["kling_ref_to_video"]
        self.max_duration = MAX_DURATIONS["kling_ref_to_video"]
        self.max_references = 4

    def validate_parameters(
        self,
        prompt: str,
        reference_images: List[str],
        duration: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        audio_url: Optional[str] = None,
        face_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate parameters for Kling Reference-to-Video.

        Args:
            prompt: Video generation prompt (use @Element1, @Element2, etc.)
            reference_images: List of reference image URLs (max 4)
            duration: Output duration ("5" or "10" seconds)
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
            audio_url: Optional audio URL
            face_id: Optional face ID from identify_face API

        Returns:
            Dict of validated parameters
        """
        if not prompt:
            raise ValueError("prompt is required")

        if not reference_images or len(reference_images) == 0:
            raise ValueError("At least one reference image is required")

        if len(reference_images) > self.max_references:
            raise ValueError(f"Maximum {self.max_references} reference images allowed")

        # Validate each reference image URL
        for i, img_url in enumerate(reference_images):
            self._validate_url(img_url, f"reference_images[{i}]")

        # Apply defaults
        duration = duration or self.defaults["duration"]
        aspect_ratio = aspect_ratio or self.defaults["aspect_ratio"]

        # Validate aspect ratio
        self._validate_aspect_ratio(aspect_ratio)

        arguments = {
            "prompt": prompt,
            "reference_images": reference_images,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
        }

        if audio_url:
            self._validate_url(audio_url, "audio_url")
            arguments["audio_url"] = audio_url

        if face_id:
            arguments["face_id"] = face_id

        # Add audio timing parameters if provided
        for param in ["sound_start_time", "sound_end_time", "sound_insert_time"]:
            if param in kwargs and kwargs[param] is not None:
                arguments[param] = kwargs[param]

        return arguments

    def generate(
        self,
        prompt: str,
        reference_images: List[str],
        duration: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        audio_url: Optional[str] = None,
        face_id: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate video with reference image consistency.

        Args:
            prompt: Generation prompt (use @Element1, @Element2, etc.)
            reference_images: List of reference image URLs (max 4)
            duration: Output duration (default: 5 seconds)
            aspect_ratio: Video aspect ratio (default: 16:9)
            audio_url: Optional audio URL
            face_id: Optional face ID

        Returns:
            AvatarGenerationResult with video URL
        """
        try:
            arguments = self.validate_parameters(
                prompt=prompt,
                reference_images=reference_images,
                duration=duration,
                aspect_ratio=aspect_ratio,
                audio_url=audio_url,
                face_id=face_id,
                **kwargs,
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
            video_duration = result.get("duration", int(arguments["duration"]))

            return AvatarGenerationResult(
                success=True,
                video_url=result["video"]["url"],
                duration=video_duration,
                cost=self.estimate_cost(video_duration),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={
                    "aspect_ratio": arguments["aspect_ratio"],
                    "num_references": len(reference_images),
                },
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name,
            )

    def estimate_cost(self, duration: float, **kwargs) -> float:
        """Estimate cost based on duration."""
        return duration * self.pricing["per_second"]

    def get_model_info(self) -> Dict[str, Any]:
        """Return model info."""
        return {
            "name": self.model_name,
            "display_name": "Kling O1 Reference-to-Video",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "supported_aspect_ratios": self.supported_aspect_ratios,
            "max_duration": self.max_duration,
            "max_references": self.max_references,
            "input_types": ["images", "prompt"],
            "description": "Generate videos with consistent characters/elements across shots",
            "best_for": ["character consistency", "product videos", "branded content"],
        }


class KlingV2VReferenceModel(BaseAvatarModel):
    """
    Kling O1 Video-to-Video Reference - Style-guided generation.

    Generate new shots guided by an input reference video,
    preserving motion and camera style.

    Pricing: ~$0.10/second
    Max Duration: 10 seconds per generation
    """

    def __init__(self):
        """Initialize Kling V2V Reference model."""
        super().__init__("kling_v2v_reference")
        self.endpoint = MODEL_ENDPOINTS["kling_v2v_reference"]
        self.pricing = MODEL_PRICING["kling_v2v_reference"]
        self.supported_aspect_ratios = SUPPORTED_ASPECT_RATIOS["kling_v2v_reference"]
        self.defaults = MODEL_DEFAULTS["kling_v2v_reference"]
        self.max_duration = MAX_DURATIONS["kling_v2v_reference"]

    def validate_parameters(
        self,
        prompt: str,
        video_url: str,
        duration: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        audio_url: Optional[str] = None,
        face_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate parameters for Kling V2V Reference.

        Args:
            prompt: Transformation prompt (use @Video1 to reference input)
            video_url: Reference video URL
            duration: Output duration ("5" or "10")
            aspect_ratio: Video aspect ratio
            audio_url: Optional audio URL
            face_id: Optional face ID

        Returns:
            Dict of validated parameters
        """
        if not prompt:
            raise ValueError("prompt is required (use @Video1 to reference input)")

        self._validate_url(video_url, "video_url")

        duration = duration or self.defaults["duration"]
        aspect_ratio = aspect_ratio or self.defaults["aspect_ratio"]

        self._validate_aspect_ratio(aspect_ratio)

        arguments = {
            "prompt": prompt,
            "video_url": video_url,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
        }

        if audio_url:
            self._validate_url(audio_url, "audio_url")
            arguments["audio_url"] = audio_url

        if face_id:
            arguments["face_id"] = face_id

        return arguments

    def generate(
        self,
        prompt: str,
        video_url: str,
        duration: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        audio_url: Optional[str] = None,
        face_id: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate style-guided video.

        Args:
            prompt: Transformation prompt (use @Video1 to reference)
            video_url: Source video URL
            duration: Output duration (default: 5 seconds)
            aspect_ratio: Video aspect ratio (default: 16:9)
            audio_url: Optional audio URL
            face_id: Optional face ID

        Returns:
            AvatarGenerationResult with video URL
        """
        try:
            arguments = self.validate_parameters(
                prompt=prompt,
                video_url=video_url,
                duration=duration,
                aspect_ratio=aspect_ratio,
                audio_url=audio_url,
                face_id=face_id,
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
            video_duration = result.get("duration", int(arguments["duration"]))

            return AvatarGenerationResult(
                success=True,
                video_url=result["video"]["url"],
                duration=video_duration,
                cost=self.estimate_cost(video_duration),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={"aspect_ratio": arguments["aspect_ratio"]},
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name,
            )

    def estimate_cost(self, duration: float, **kwargs) -> float:
        """Estimate cost based on duration."""
        return duration * self.pricing["per_second"]

    def get_model_info(self) -> Dict[str, Any]:
        """Return model info."""
        return {
            "name": self.model_name,
            "display_name": "Kling O1 V2V Reference",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "supported_aspect_ratios": self.supported_aspect_ratios,
            "max_duration": self.max_duration,
            "input_types": ["video", "prompt"],
            "description": "Generate new shots preserving motion and camera style",
            "best_for": ["scene continuity", "style transfer", "next shot generation"],
        }


class KlingV2VEditModel(BaseAvatarModel):
    """
    Kling O1 Video-to-Video Edit - Targeted modifications.

    Make specific edits to videos through natural language prompts
    without regenerating the entire video.

    Pricing: ~$0.10/second
    Max Duration: 10 seconds per generation
    """

    def __init__(self):
        """Initialize Kling V2V Edit model."""
        super().__init__("kling_v2v_edit")
        self.endpoint = MODEL_ENDPOINTS["kling_v2v_edit"]
        self.pricing = MODEL_PRICING["kling_v2v_edit"]
        self.supported_aspect_ratios = SUPPORTED_ASPECT_RATIOS.get("kling_v2v_edit", [])
        self.max_duration = MAX_DURATIONS["kling_v2v_edit"]

    def validate_parameters(
        self,
        video_url: str,
        prompt: str,
        mask_url: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate parameters for Kling V2V Edit.

        Args:
            video_url: Source video URL to edit
            prompt: Edit instructions
            mask_url: Optional mask image for targeted edits

        Returns:
            Dict of validated parameters
        """
        self._validate_url(video_url, "video_url")

        if not prompt:
            raise ValueError("prompt is required (describe the edit)")

        arguments = {
            "video_url": video_url,
            "prompt": prompt,
        }

        if mask_url:
            self._validate_url(mask_url, "mask_url")
            arguments["mask_url"] = mask_url

        return arguments

    def generate(
        self,
        video_url: str,
        prompt: str,
        mask_url: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Edit video with natural language instructions.

        Args:
            video_url: Source video URL
            prompt: Edit instructions
            mask_url: Optional mask for targeted edits

        Returns:
            AvatarGenerationResult with video URL
        """
        try:
            arguments = self.validate_parameters(
                video_url=video_url,
                prompt=prompt,
                mask_url=mask_url,
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
            video_duration = result.get("duration", 5)

            return AvatarGenerationResult(
                success=True,
                video_url=result["video"]["url"],
                duration=video_duration,
                cost=self.estimate_cost(video_duration),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={"has_mask": mask_url is not None},
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name,
            )

    def estimate_cost(self, duration: float, **kwargs) -> float:
        """Estimate cost based on duration."""
        return duration * self.pricing["per_second"]

    def get_model_info(self) -> Dict[str, Any]:
        """Return model info."""
        return {
            "name": self.model_name,
            "display_name": "Kling O1 V2V Edit",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "max_duration": self.max_duration,
            "input_types": ["video", "prompt", "mask (optional)"],
            "description": "Targeted video modifications through natural language",
            "best_for": ["background changes", "object removal", "lighting adjustments"],
        }
