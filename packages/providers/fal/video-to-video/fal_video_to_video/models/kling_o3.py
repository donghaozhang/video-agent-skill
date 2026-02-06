"""
Kling O3 (Omni 3) Video-to-Video model implementations.

O3 V2V models focus on:
- Video editing with element replacement
- Video style transfer with reference images
- Character/element consistency with @ reference syntax

Models:
- O3 Standard Edit: $0.252/second
- O3 Pro Edit: $0.336/second
- O3 Standard V2V Reference: $0.252/second
- O3 Pro V2V Reference: $0.336/second
"""

from typing import Dict, Any, Optional, List
from .base import BaseModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, DURATION_OPTIONS


class KlingO3StandardEditModel(BaseModel):
    """
    Kling O3 Standard video editing model.

    Features:
        - Element-based object/character replacement
        - @ reference syntax in prompts (@Element1, @Image1)
        - Environment modification
        - 3-15 second duration support

    API Parameters:
        - prompt: Text description with @ references
        - video_url: Source video to edit
        - elements: Character/object definitions for replacement
        - image_urls: Reference images for style/context
        - duration: Output video duration (3-15 seconds)
        - aspect_ratio: "16:9", "9:16", "1:1"

    Pricing: $0.252/second
    """

    def __init__(self):
        super().__init__("kling_o3_standard_edit")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling O3 Standard Edit parameters."""
        defaults = DEFAULT_VALUES.get("kling_o3_standard_edit", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        elements = kwargs.get("elements", defaults.get("elements", []))
        image_urls = kwargs.get("image_urls", defaults.get("image_urls", []))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))

        # Validate duration (3-15 seconds)
        valid_durations = DURATION_OPTIONS.get("kling_o3_standard_edit", ["3", "5", "10", "15"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate elements structure
        if elements and not isinstance(elements, list):
            raise ValueError("elements must be a list")

        return {
            "duration": str(duration),
            "elements": elements if isinstance(elements, list) else [],
            "image_urls": image_urls if isinstance(image_urls, list) else [],
            "aspect_ratio": aspect_ratio
        }

    def prepare_arguments(self, video_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kling O3 Standard Edit."""
        prompt = kwargs.get("prompt", "")
        args = {
            "prompt": prompt,
            "video_url": video_url,
            "duration": int(kwargs.get("duration", "5"))
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add elements (character/object definitions)
        elements = kwargs.get("elements", [])
        if elements:
            args["elements"] = elements

        # Add reference images
        image_urls = kwargs.get("image_urls", [])
        if image_urls:
            args["image_urls"] = image_urls

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling O3 Standard Edit model information."""
        return {
            **MODEL_INFO.get("kling_o3_standard_edit", {}),
            "endpoint": self.endpoint,
            "price_per_second": 0.252,
            "elements_supported": True,
            "reference_syntax": True
        }

    def estimate_cost(self, duration: int = 5, **kwargs) -> float:
        """Estimate cost based on duration. Pricing: $0.252/second."""
        return 0.252 * int(duration)


class KlingO3ProEditModel(BaseModel):
    """
    Kling O3 Pro video editing model with enhanced quality.

    Features:
        - Professional-tier visual quality
        - Element-based object/character replacement
        - @ reference syntax in prompts (@Element1, @Image1)
        - Environment modification
        - 3-15 second duration support

    API Parameters:
        - prompt: Text description with @ references
        - video_url: Source video to edit
        - elements: Character/object definitions for replacement
        - image_urls: Reference images for style/context
        - duration: Output video duration (3-15 seconds)
        - aspect_ratio: "16:9", "9:16", "1:1"

    Pricing: $0.336/second
    """

    def __init__(self):
        super().__init__("kling_o3_pro_edit")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling O3 Pro Edit parameters."""
        defaults = DEFAULT_VALUES.get("kling_o3_pro_edit", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        elements = kwargs.get("elements", defaults.get("elements", []))
        image_urls = kwargs.get("image_urls", defaults.get("image_urls", []))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))

        # Validate duration (3-15 seconds)
        valid_durations = DURATION_OPTIONS.get("kling_o3_pro_edit", ["3", "5", "10", "15"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate elements structure
        if elements and not isinstance(elements, list):
            raise ValueError("elements must be a list")

        return {
            "duration": str(duration),
            "elements": elements if isinstance(elements, list) else [],
            "image_urls": image_urls if isinstance(image_urls, list) else [],
            "aspect_ratio": aspect_ratio
        }

    def prepare_arguments(self, video_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kling O3 Pro Edit."""
        prompt = kwargs.get("prompt", "")
        args = {
            "prompt": prompt,
            "video_url": video_url,
            "duration": int(kwargs.get("duration", "5"))
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add elements (character/object definitions)
        elements = kwargs.get("elements", [])
        if elements:
            args["elements"] = elements

        # Add reference images
        image_urls = kwargs.get("image_urls", [])
        if image_urls:
            args["image_urls"] = image_urls

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling O3 Pro Edit model information."""
        return {
            **MODEL_INFO.get("kling_o3_pro_edit", {}),
            "endpoint": self.endpoint,
            "price_per_second": 0.336,
            "professional_tier": True,
            "elements_supported": True,
            "reference_syntax": True
        }

    def estimate_cost(self, duration: int = 5, **kwargs) -> float:
        """Estimate cost based on duration. Pricing: $0.336/second."""
        return 0.336 * int(duration)


class KlingO3StandardV2VRefModel(BaseModel):
    """
    Kling O3 Standard video-to-video reference model.

    Features:
        - Style transfer from reference images
        - Element integration with consistency
        - @ reference syntax in prompts (@Element1, @Image1)
        - Optional audio preservation
        - 3-15 second duration support

    API Parameters:
        - prompt: Text description with @ references
        - video_url: Source video
        - elements: Character/object definitions
        - image_urls: Style reference images
        - duration: Output video duration (3-15 seconds)
        - aspect_ratio: "16:9", "9:16", "1:1"
        - keep_audio: Preserve original audio (optional)

    Pricing: $0.252/second
    """

    def __init__(self):
        super().__init__("kling_o3_standard_v2v_ref")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling O3 Standard V2V Reference parameters."""
        defaults = DEFAULT_VALUES.get("kling_o3_standard_v2v_ref", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        elements = kwargs.get("elements", defaults.get("elements", []))
        image_urls = kwargs.get("image_urls", defaults.get("image_urls", []))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        keep_audio = kwargs.get("keep_audio", defaults.get("keep_audio", False))

        # Validate duration (3-15 seconds)
        valid_durations = DURATION_OPTIONS.get("kling_o3_standard_v2v_ref", ["3", "5", "10", "15"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        return {
            "duration": str(duration),
            "elements": elements if isinstance(elements, list) else [],
            "image_urls": image_urls if isinstance(image_urls, list) else [],
            "aspect_ratio": aspect_ratio,
            "keep_audio": bool(keep_audio)
        }

    def prepare_arguments(self, video_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kling O3 Standard V2V Reference."""
        prompt = kwargs.get("prompt", "")
        args = {
            "prompt": prompt,
            "video_url": video_url,
            "duration": int(kwargs.get("duration", "5"))
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add elements (character/object definitions)
        elements = kwargs.get("elements", [])
        if elements:
            args["elements"] = elements

        # Add reference images (style transfer)
        image_urls = kwargs.get("image_urls", [])
        if image_urls:
            args["image_urls"] = image_urls

        # Add keep_audio option
        keep_audio = kwargs.get("keep_audio", False)
        if keep_audio:
            args["keep_audio"] = True

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling O3 Standard V2V Reference model information."""
        return {
            **MODEL_INFO.get("kling_o3_standard_v2v_ref", {}),
            "endpoint": self.endpoint,
            "price_per_second": 0.252,
            "elements_supported": True,
            "reference_syntax": True,
            "style_transfer": True
        }

    def estimate_cost(self, duration: int = 5, **kwargs) -> float:
        """Estimate cost based on duration. Pricing: $0.252/second."""
        return 0.252 * int(duration)


class KlingO3ProV2VRefModel(BaseModel):
    """
    Kling O3 Pro video-to-video reference model with enhanced quality.

    Features:
        - Professional-tier visual quality
        - Style transfer from reference images
        - Element integration with consistency
        - @ reference syntax in prompts (@Element1, @Image1)
        - Optional audio preservation
        - 3-15 second duration support

    API Parameters:
        - prompt: Text description with @ references
        - video_url: Source video
        - elements: Character/object definitions
        - image_urls: Style reference images
        - duration: Output video duration (3-15 seconds)
        - aspect_ratio: "16:9", "9:16", "1:1"
        - keep_audio: Preserve original audio (optional)

    Pricing: $0.336/second
    """

    def __init__(self):
        super().__init__("kling_o3_pro_v2v_ref")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling O3 Pro V2V Reference parameters."""
        defaults = DEFAULT_VALUES.get("kling_o3_pro_v2v_ref", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        elements = kwargs.get("elements", defaults.get("elements", []))
        image_urls = kwargs.get("image_urls", defaults.get("image_urls", []))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        keep_audio = kwargs.get("keep_audio", defaults.get("keep_audio", False))

        # Validate duration (3-15 seconds)
        valid_durations = DURATION_OPTIONS.get("kling_o3_pro_v2v_ref", ["3", "5", "10", "15"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        return {
            "duration": str(duration),
            "elements": elements if isinstance(elements, list) else [],
            "image_urls": image_urls if isinstance(image_urls, list) else [],
            "aspect_ratio": aspect_ratio,
            "keep_audio": bool(keep_audio)
        }

    def prepare_arguments(self, video_url: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kling O3 Pro V2V Reference."""
        prompt = kwargs.get("prompt", "")
        args = {
            "prompt": prompt,
            "video_url": video_url,
            "duration": int(kwargs.get("duration", "5"))
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add elements (character/object definitions)
        elements = kwargs.get("elements", [])
        if elements:
            args["elements"] = elements

        # Add reference images (style transfer)
        image_urls = kwargs.get("image_urls", [])
        if image_urls:
            args["image_urls"] = image_urls

        # Add keep_audio option
        keep_audio = kwargs.get("keep_audio", False)
        if keep_audio:
            args["keep_audio"] = True

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling O3 Pro V2V Reference model information."""
        return {
            **MODEL_INFO.get("kling_o3_pro_v2v_ref", {}),
            "endpoint": self.endpoint,
            "price_per_second": 0.336,
            "professional_tier": True,
            "elements_supported": True,
            "reference_syntax": True,
            "style_transfer": True
        }

    def estimate_cost(self, duration: int = 5, **kwargs) -> float:
        """Estimate cost based on duration. Pricing: $0.336/second."""
        return 0.336 * int(duration)
