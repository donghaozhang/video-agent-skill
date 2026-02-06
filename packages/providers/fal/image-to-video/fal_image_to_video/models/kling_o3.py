"""
Kling O3 (Omni 3) Video model implementations for image-to-video and reference-to-video.

O3 models focus on character/element consistency with the 'elements' parameter
and support @ reference syntax in prompts (@Element1, @Image1, etc).

Models:
- O3 Standard Image-to-Video: $0.168/s (no audio), $0.224/s (audio)
- O3 Pro Image-to-Video: $0.224/s (no audio), $0.28/s (audio)
- O3 Standard Reference-to-Video: $0.084/s (no audio), $0.112/s (audio)
- O3 Pro Reference-to-Video: $0.224/s (no audio), $0.28/s (audio)
"""

from typing import Dict, Any, Optional, List
from .base import BaseVideoModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, DURATION_OPTIONS, ASPECT_RATIO_OPTIONS


class KlingO3StandardI2VModel(BaseVideoModel):
    """
    Kling O3 Standard image-to-video model with element consistency.

    Features:
        - Element-based character/object consistency
        - Native audio generation
        - End frame transitions
        - 3-15 second duration support

    API Parameters:
        - prompt: Text description with optional @ references
        - image_url: Start frame image URL
        - end_image_url: End frame for transitions (optional)
        - duration: 3-15 seconds
        - generate_audio: Enable native audio
        - elements: Character/object definitions
        - image_urls: Style reference images
        - aspect_ratio: "16:9", "9:16", "1:1"

    Pricing:
        - $0.168/second (audio off)
        - $0.224/second (audio on)
    """

    MODEL_KEY = "kling_o3_standard_i2v"

    def __init__(self):
        """Initialize the Kling O3 Standard image-to-video model."""
        super().__init__("kling_o3_standard_i2v")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling O3 Standard I2V parameters."""
        defaults = DEFAULT_VALUES.get("kling_o3_standard_i2v", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", True))
        elements = kwargs.get("elements", defaults.get("elements", []))
        image_urls = kwargs.get("image_urls", defaults.get("image_urls", []))
        end_frame = kwargs.get("end_frame")
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))

        # Validate duration (3-15 seconds)
        valid_durations = DURATION_OPTIONS.get("kling_o3_standard_i2v", ["3", "5", "10", "15"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate aspect_ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_o3_standard_i2v", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        # Validate cfg_scale if provided
        if cfg_scale is not None and not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        # Validate elements structure
        if elements and not isinstance(elements, list):
            raise ValueError("elements must be a list")

        return {
            "duration": str(duration),
            "generate_audio": bool(generate_audio),
            "elements": elements if isinstance(elements, list) else [],
            "image_urls": image_urls if isinstance(image_urls, list) else [],
            "end_frame": end_frame,
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling O3 Standard I2V."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": int(kwargs.get("duration", "5")),
            "generate_audio": kwargs.get("generate_audio", True)
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add end frame for transitions
        end_frame = kwargs.get("end_frame")
        if end_frame:
            args["end_image_url"] = end_frame

        # Add negative prompt if provided
        negative_prompt = kwargs.get("negative_prompt")
        if negative_prompt:
            args["negative_prompt"] = negative_prompt

        # Add cfg_scale if provided
        cfg_scale = kwargs.get("cfg_scale")
        if cfg_scale is not None:
            args["cfg_scale"] = cfg_scale

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
        """Get Kling O3 Standard I2V model information."""
        return {
            **MODEL_INFO.get("kling_o3_standard_i2v", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "audio_supported": True,
            "elements_supported": True
        }

    def estimate_cost(self, duration: int = 5, generate_audio: bool = True, **kwargs) -> float:
        """
        Estimate cost based on duration and audio settings.

        Pricing:
            - $0.168/second (audio off)
            - $0.224/second (audio on)
        """
        duration_seconds = int(duration)
        if generate_audio:
            cost_per_second = 0.224  # Audio on pricing
        else:
            cost_per_second = 0.168  # Audio off pricing
        return cost_per_second * duration_seconds


class KlingO3ProI2VModel(BaseVideoModel):
    """
    Kling O3 Pro image-to-video model with enhanced quality and element consistency.

    Features:
        - Professional-tier cinematic quality
        - Element-based character/object consistency
        - Native audio generation
        - End frame transitions
        - 3-15 second duration support

    API Parameters:
        - prompt: Text description with optional @ references
        - image_url: Start frame image URL
        - end_image_url: End frame for transitions (optional)
        - duration: 3-15 seconds
        - generate_audio: Enable native audio
        - elements: Character/object definitions
        - image_urls: Style reference images
        - aspect_ratio: "16:9", "9:16", "1:1"

    Pricing:
        - $0.224/second (audio off)
        - $0.28/second (audio on)
    """

    MODEL_KEY = "kling_o3_pro_i2v"

    def __init__(self):
        """Initialize the Kling O3 Pro image-to-video model."""
        super().__init__("kling_o3_pro_i2v")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling O3 Pro I2V parameters."""
        defaults = DEFAULT_VALUES.get("kling_o3_pro_i2v", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", True))
        elements = kwargs.get("elements", defaults.get("elements", []))
        image_urls = kwargs.get("image_urls", defaults.get("image_urls", []))
        end_frame = kwargs.get("end_frame")
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))

        # Validate duration (3-15 seconds)
        valid_durations = DURATION_OPTIONS.get("kling_o3_pro_i2v", ["3", "5", "10", "15"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate aspect_ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_o3_pro_i2v", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        # Validate cfg_scale if provided
        if cfg_scale is not None and not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        return {
            "duration": str(duration),
            "generate_audio": bool(generate_audio),
            "elements": elements if isinstance(elements, list) else [],
            "image_urls": image_urls if isinstance(image_urls, list) else [],
            "end_frame": end_frame,
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling O3 Pro I2V."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": int(kwargs.get("duration", "5")),
            "generate_audio": kwargs.get("generate_audio", True)
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add end frame for transitions
        end_frame = kwargs.get("end_frame")
        if end_frame:
            args["end_image_url"] = end_frame

        # Add negative prompt if provided
        negative_prompt = kwargs.get("negative_prompt")
        if negative_prompt:
            args["negative_prompt"] = negative_prompt

        # Add cfg_scale if provided
        cfg_scale = kwargs.get("cfg_scale")
        if cfg_scale is not None:
            args["cfg_scale"] = cfg_scale

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
        """Get Kling O3 Pro I2V model information."""
        return {
            **MODEL_INFO.get("kling_o3_pro_i2v", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "professional_tier": True,
            "audio_supported": True,
            "elements_supported": True
        }

    def estimate_cost(self, duration: int = 5, generate_audio: bool = True, **kwargs) -> float:
        """
        Estimate cost based on duration and audio settings.

        Pricing:
            - $0.224/second (audio off)
            - $0.28/second (audio on)
        """
        duration_seconds = int(duration)
        if generate_audio:
            cost_per_second = 0.28  # Audio on pricing
        else:
            cost_per_second = 0.224  # Audio off pricing
        return cost_per_second * duration_seconds


class KlingO3StandardRefModel(BaseVideoModel):
    """
    Kling O3 Standard reference-to-video model for element-based generation.

    Features:
        - Element-based character/object consistency
        - @ reference syntax in prompts (@Element1, @Image1)
        - Native audio generation
        - 3-15 second duration support

    API Parameters:
        - prompt: Text with @ references (@Element1, @Element2, @Image1)
        - start_image_url: Background/scene image
        - elements: Array of character/object definitions
        - image_urls: Style reference images
        - duration: 3-15 seconds
        - generate_audio: Enable native audio
        - aspect_ratio: "16:9", "9:16", "1:1"

    Pricing:
        - $0.084/second (audio off)
        - $0.112/second (audio on)
    """

    MODEL_KEY = "kling_o3_standard_ref"

    def __init__(self):
        """Initialize the Kling O3 Standard reference-to-video model."""
        super().__init__("kling_o3_standard_ref")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling O3 Standard Ref parameters."""
        defaults = DEFAULT_VALUES.get("kling_o3_standard_ref", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", False))
        elements = kwargs.get("elements", defaults.get("elements", []))
        image_urls = kwargs.get("image_urls", defaults.get("image_urls", []))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        multi_prompt = kwargs.get("multi_prompt", defaults.get("multi_prompt", []))
        shot_type = kwargs.get("shot_type", defaults.get("shot_type"))

        # Validate duration (3-15 seconds)
        valid_durations = DURATION_OPTIONS.get("kling_o3_standard_ref", ["3", "5", "10", "15"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate aspect_ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_o3_standard_ref", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": str(duration),
            "generate_audio": bool(generate_audio),
            "elements": elements if isinstance(elements, list) else [],
            "image_urls": image_urls if isinstance(image_urls, list) else [],
            "aspect_ratio": aspect_ratio,
            "multi_prompt": multi_prompt if isinstance(multi_prompt, list) else [],
            "shot_type": shot_type
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling O3 Standard Ref."""
        args = {
            "prompt": prompt,
            "start_image_url": image_url,
            "duration": int(kwargs.get("duration", "5")),
            "generate_audio": kwargs.get("generate_audio", False)
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add elements (character/object definitions) - REQUIRED for reference models
        elements = kwargs.get("elements", [])
        if elements:
            args["elements"] = elements

        # Add reference images
        image_urls = kwargs.get("image_urls", [])
        if image_urls:
            args["image_urls"] = image_urls

        # Add multi-prompt if provided
        multi_prompt = kwargs.get("multi_prompt", [])
        if multi_prompt:
            args["multi_prompt"] = multi_prompt

        # Add shot type if provided
        shot_type = kwargs.get("shot_type")
        if shot_type:
            args["shot_type"] = shot_type

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling O3 Standard Ref model information."""
        return {
            **MODEL_INFO.get("kling_o3_standard_ref", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "audio_supported": True,
            "elements_supported": True,
            "reference_syntax": True
        }

    def estimate_cost(self, duration: int = 5, generate_audio: bool = False, **kwargs) -> float:
        """
        Estimate cost based on duration and audio settings.

        Pricing:
            - $0.084/second (audio off)
            - $0.112/second (audio on)
        """
        duration_seconds = int(duration)
        if generate_audio:
            cost_per_second = 0.112  # Audio on pricing
        else:
            cost_per_second = 0.084  # Audio off pricing
        return cost_per_second * duration_seconds


class KlingO3ProRefModel(BaseVideoModel):
    """
    Kling O3 Pro reference-to-video model for professional element-based generation.

    Features:
        - Professional-tier quality
        - Element-based character/object consistency
        - @ reference syntax in prompts (@Element1, @Image1)
        - Native audio generation
        - 3-15 second duration support

    API Parameters:
        - prompt: Text with @ references (@Element1, @Element2, @Image1)
        - start_image_url: Background/scene image
        - elements: Array of character/object definitions
        - image_urls: Style reference images
        - duration: 3-15 seconds
        - generate_audio: Enable native audio
        - aspect_ratio: "16:9", "9:16", "1:1"

    Pricing:
        - $0.224/second (audio off)
        - $0.28/second (audio on)
    """

    MODEL_KEY = "kling_o3_pro_ref"

    def __init__(self):
        """Initialize the Kling O3 Pro reference-to-video model."""
        super().__init__("kling_o3_pro_ref")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling O3 Pro Ref parameters."""
        defaults = DEFAULT_VALUES.get("kling_o3_pro_ref", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", False))
        elements = kwargs.get("elements", defaults.get("elements", []))
        image_urls = kwargs.get("image_urls", defaults.get("image_urls", []))
        end_frame = kwargs.get("end_frame")
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))

        # Validate duration (3-15 seconds)
        valid_durations = DURATION_OPTIONS.get("kling_o3_pro_ref", ["3", "5", "10", "15"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate aspect_ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_o3_pro_ref", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": str(duration),
            "generate_audio": bool(generate_audio),
            "elements": elements if isinstance(elements, list) else [],
            "image_urls": image_urls if isinstance(image_urls, list) else [],
            "end_frame": end_frame,
            "aspect_ratio": aspect_ratio
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling O3 Pro Ref."""
        args = {
            "prompt": prompt,
            "start_image_url": image_url,
            "duration": int(kwargs.get("duration", "5")),
            "generate_audio": kwargs.get("generate_audio", False)
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add end frame if provided
        end_frame = kwargs.get("end_frame")
        if end_frame:
            args["end_image_url"] = end_frame

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
        """Get Kling O3 Pro Ref model information."""
        return {
            **MODEL_INFO.get("kling_o3_pro_ref", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "professional_tier": True,
            "audio_supported": True,
            "elements_supported": True,
            "reference_syntax": True
        }

    def estimate_cost(self, duration: int = 5, generate_audio: bool = False, **kwargs) -> float:
        """
        Estimate cost based on duration and audio settings.

        Pricing:
            - $0.224/second (audio off)
            - $0.28/second (audio on)
        """
        duration_seconds = int(duration)
        if generate_audio:
            cost_per_second = 0.28  # Audio on pricing
        else:
            cost_per_second = 0.224  # Audio off pricing
        return cost_per_second * duration_seconds
