"""Unified FAL Avatar Generator - Routes to appropriate model implementations."""

from typing import Any, Dict, List, Optional

from .models import (
    BaseAvatarModel,
    AvatarGenerationResult,
    OmniHumanModel,
    FabricModel,
    FabricTextModel,
    KlingRefToVideoModel,
    KlingV2VReferenceModel,
    KlingV2VEditModel,
    KlingMotionControlModel,
    MultiTalkModel,
    GrokVideoEditModel,
)
from .config.constants import (
    MODEL_DISPLAY_NAMES,
    MODEL_CATEGORIES,
    MODEL_RECOMMENDATIONS,
    INPUT_REQUIREMENTS,
)


class FALAvatarGenerator:
    """
    Unified generator for FAL avatar and video generation models.

    Provides a single interface to access all avatar models:
    - OmniHuman v1.5 - Audio-driven human animation
    - VEED Fabric 1.0 - Lipsync video generation
    - VEED Fabric 1.0 Text - Text-to-speech avatar
    - Kling O1 Reference-to-Video - Character consistency
    - Kling O1 V2V Reference - Style-guided video
    - Kling O1 V2V Edit - Targeted video modifications
    - Kling v2.6 Motion Control - Motion transfer from video to image
    - AI Avatar Multi - Multi-person conversational video
    - Grok Video Edit - xAI video-to-video editing
    """

    def __init__(self):
        """Initialize all available models."""
        self.models: Dict[str, BaseAvatarModel] = {
            "omnihuman_v1_5": OmniHumanModel(),
            "fabric_1_0": FabricModel(fast=False),
            "fabric_1_0_fast": FabricModel(fast=True),
            "fabric_1_0_text": FabricTextModel(),
            "kling_ref_to_video": KlingRefToVideoModel(),
            "kling_v2v_reference": KlingV2VReferenceModel(),
            "kling_v2v_edit": KlingV2VEditModel(),
            "kling_motion_control": KlingMotionControlModel(),
            "multitalk": MultiTalkModel(),
            "grok_video_edit": GrokVideoEditModel(),
        }

    def generate(
        self,
        model: str = "omnihuman_v1_5",
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate avatar/video using the specified model.

        Args:
            model: Model identifier (see list_models())
            **kwargs: Model-specific parameters

        Returns:
            AvatarGenerationResult with video URL and metadata
        """
        if model not in self.models:
            available = ", ".join(self.models.keys())
            return AvatarGenerationResult(
                success=False,
                error=f"Unknown model '{model}'. Available: {available}",
                model_used=model,
            )

        return self.models[model].generate(**kwargs)

    def generate_avatar(
        self,
        image_url: str,
        audio_url: Optional[str] = None,
        text: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Convenience method for avatar/lipsync generation.
        Auto-selects model based on inputs if not specified.

        Args:
            image_url: Portrait/face image URL
            audio_url: Audio file URL (for lipsync)
            text: Text to speak (for TTS)
            model: Model to use (auto-selected if not provided)
            **kwargs: Additional model parameters

        Returns:
            AvatarGenerationResult with video URL
        """
        # Auto-select model based on inputs
        if model is None:
            if text and not audio_url:
                model = "fabric_1_0_text"
            elif audio_url:
                model = "omnihuman_v1_5"
            else:
                return AvatarGenerationResult(
                    success=False,
                    error="Either audio_url or text is required for avatar generation",
                )

        return self.generate(
            model=model,
            image_url=image_url,
            audio_url=audio_url,
            text=text,
            **kwargs,
        )

    def generate_reference_video(
        self,
        prompt: str,
        reference_images: List[str],
        model: str = "kling_ref_to_video",
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate video with reference image consistency.

        Args:
            prompt: Generation prompt (use @Element1, @Element2, etc.)
            reference_images: List of reference image URLs (max 4)
            model: Model to use
            **kwargs: Additional parameters (duration, aspect_ratio, etc.)

        Returns:
            AvatarGenerationResult with video URL
        """
        return self.generate(
            model=model,
            prompt=prompt,
            reference_images=reference_images,
            **kwargs,
        )

    def transform_video(
        self,
        video_url: str,
        prompt: str,
        mode: str = "reference",
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Transform existing video (style transfer, edit, or grok edit).

        Args:
            video_url: Source video URL
            prompt: Transformation prompt
            mode: "reference" for style-guided, "edit" for Kling targeted modifications,
                  "grok" for xAI Grok video editing
            **kwargs: Additional parameters

        Returns:
            AvatarGenerationResult with video URL
        """
        valid_modes = {
            "reference": "kling_v2v_reference",
            "edit": "kling_v2v_edit",
            "grok": "grok_video_edit",
        }
        if mode not in valid_modes:
            return AvatarGenerationResult(
                success=False,
                error=f"Invalid mode '{mode}'. Must be 'reference', 'edit', or 'grok'.",
                model_used="unknown",
            )
        model = valid_modes[mode]

        return self.generate(
            model=model,
            video_url=video_url,
            prompt=prompt,
            **kwargs,
        )

    def generate_conversation(
        self,
        image_url: str,
        first_audio_url: str,
        prompt: str,
        second_audio_url: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate multi-person conversational video.

        Convenience method for the MultiTalk model. Creates realistic videos
        where multiple people speak in sequence, driven by separate audio files.

        Args:
            image_url: URL of input image containing person(s)
            first_audio_url: URL of Person 1 audio file
            prompt: Text description guiding video generation
            second_audio_url: Optional URL of Person 2 audio file
            **kwargs: Additional parameters:
                - num_frames: Frame count (81-129, default 81)
                - resolution: "480p" or "720p" (default "480p")
                - seed: Random seed for reproducibility
                - acceleration: "none", "regular", or "high" (default "regular")
                - use_only_first_audio: Ignore second audio if provided

        Returns:
            AvatarGenerationResult with video URL and metadata
        """
        return self.generate(
            model="multitalk",
            image_url=image_url,
            first_audio_url=first_audio_url,
            prompt=prompt,
            second_audio_url=second_audio_url,
            **kwargs,
        )

    def transfer_motion(
        self,
        image_url: str,
        video_url: str,
        character_orientation: str = "video",
        keep_original_sound: bool = True,
        prompt: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Transfer motion from a reference video to a reference image.

        Creates videos where characters in the image mimic movements
        from the reference video.

        Args:
            image_url: Reference image URL (characters/background source)
            video_url: Reference video URL (motion source)
            character_orientation: "video" (max 30s) or "image" (max 10s)
            keep_original_sound: Keep audio from reference video
            prompt: Optional text description
            **kwargs: Additional parameters

        Returns:
            AvatarGenerationResult with video URL

        Example:
            result = generator.transfer_motion(
                image_url="https://example.com/person.jpg",
                video_url="https://example.com/dance.mp4",
                character_orientation="video",
                keep_original_sound=True
            )
        """
        return self.generate(
            model="kling_motion_control",
            image_url=image_url,
            video_url=video_url,
            character_orientation=character_orientation,
            keep_original_sound=keep_original_sound,
            prompt=prompt,
            **kwargs,
        )

    def list_models(self) -> List[str]:
        """Return list of available model identifiers."""
        return list(self.models.keys())

    def list_models_by_category(self) -> Dict[str, List[str]]:
        """Return models grouped by category."""
        return MODEL_CATEGORIES.copy()

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.

        Args:
            model: Model identifier

        Returns:
            Dict containing model information

        Raises:
            ValueError: If model not found
        """
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        return self.models[model].get_model_info()

    def get_all_models_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available models."""
        return {name: model.get_model_info() for name, model in self.models.items()}

    def estimate_cost(
        self,
        model: str,
        duration: float,
        **kwargs,
    ) -> float:
        """
        Estimate generation cost for a model.

        Args:
            model: Model identifier
            duration: Video duration in seconds
            **kwargs: Additional parameters affecting cost

        Returns:
            Estimated cost in USD

        Raises:
            ValueError: If model not found
        """
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        return self.models[model].estimate_cost(duration, **kwargs)

    def recommend_model(
        self,
        use_case: str = "quality",
    ) -> str:
        """
        Get model recommendation for a use case.

        Args:
            use_case: One of "quality", "speed", "text_to_avatar",
                     "character_consistency", "style_transfer",
                     "video_editing", "cost_effective"

        Returns:
            Recommended model identifier
        """
        if use_case in MODEL_RECOMMENDATIONS:
            return MODEL_RECOMMENDATIONS[use_case]
        return MODEL_RECOMMENDATIONS["quality"]

    def get_input_requirements(self, model: str) -> Dict[str, List[str]]:
        """
        Get required and optional inputs for a model.

        Args:
            model: Model identifier

        Returns:
            Dict with "required" and "optional" input lists

        Raises:
            ValueError: If model not found
        """
        if model not in INPUT_REQUIREMENTS:
            raise ValueError(f"Unknown model: {model}")
        return INPUT_REQUIREMENTS[model].copy()

    def validate_inputs(self, model: str, **kwargs) -> bool:
        """
        Validate that required inputs are provided for a model.

        Args:
            model: Model identifier
            **kwargs: Inputs to validate

        Returns:
            True if valid

        Raises:
            ValueError: If required inputs are missing
        """
        requirements = self.get_input_requirements(model)

        def _is_empty(value) -> bool:
            """Check if value is None or empty (string/list)."""
            if value is None:
                return True
            if isinstance(value, str) and not value.strip():
                return True
            if isinstance(value, (list, tuple)) and len(value) == 0:
                return True
            return False

        missing = [
            param for param in requirements["required"]
            if param not in kwargs or _is_empty(kwargs[param])
        ]

        if missing:
            raise ValueError(f"Missing required parameters for {model}: {missing}")

        return True

    def get_display_name(self, model: str) -> str:
        """
        Get human-readable display name for a model.

        Args:
            model: Model identifier

        Returns:
            Display name string
        """
        return MODEL_DISPLAY_NAMES.get(model, model)
