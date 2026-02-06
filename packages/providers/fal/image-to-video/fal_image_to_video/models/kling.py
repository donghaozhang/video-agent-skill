"""
Kling Video model implementations (v2.1, v2.6 Pro, v3 Standard, v3 Pro).

Supports:
- Frame interpolation via end_frame parameter (tail_image_url)
- Native audio generation (v3 models)
- Voice control (v3 models)
- Multi-prompt sequences (v3 models)
- Custom elements/characters with reference images (v3 models)
"""

from typing import Dict, Any, Optional, List
from .base import BaseVideoModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, DURATION_OPTIONS, ASPECT_RATIO_OPTIONS


class KlingModel(BaseVideoModel):
    """
    Kling Video v2.1 model for image-to-video generation.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL (start frame)
        - tail_image_url: End frame for interpolation (optional)
        - duration: 5, 10 seconds
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)

    Pricing: ~$0.05/second
    """

    MODEL_KEY = "kling_2_1"

    def __init__(self):
        """Initialize the Kling v2.1 image-to-video model."""
        super().__init__("kling_2_1")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v2.1 parameters."""
        defaults = DEFAULT_VALUES.get("kling_2_1", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", "blur, distort, and low quality"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        end_frame = kwargs.get("end_frame")  # Optional end frame for interpolation

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_2_1", ["5", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        return {
            "duration": duration,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "end_frame": end_frame
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling v2.1."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5"),
            "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5)
        }

        # Add end frame for interpolation (tail_image_url)
        end_frame = kwargs.get("end_frame")
        if end_frame:
            args["tail_image_url"] = end_frame

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling v2.1 model information."""
        return {
            **MODEL_INFO.get("kling_2_1", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }


class Kling26ProModel(BaseVideoModel):
    """
    Kling Video v2.6 Pro model for professional image-to-video generation.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL (start frame)
        - tail_image_url: End frame for interpolation (optional)
        - duration: 5, 10 seconds
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)

    Pricing: ~$0.10/second
    """

    MODEL_KEY = "kling_2_6_pro"

    def __init__(self):
        """Initialize the Kling v2.6 Pro image-to-video model."""
        super().__init__("kling_2_6_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v2.6 Pro parameters."""
        defaults = DEFAULT_VALUES.get("kling_2_6_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", "blur, distort, and low quality"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        end_frame = kwargs.get("end_frame")  # Optional end frame for interpolation

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_2_6_pro", ["5", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        return {
            "duration": duration,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "end_frame": end_frame
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling v2.6 Pro."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5"),
            "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5)
        }

        # Add end frame for interpolation (tail_image_url)
        end_frame = kwargs.get("end_frame")
        if end_frame:
            args["tail_image_url"] = end_frame

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling v2.6 Pro model information."""
        return {
            **MODEL_INFO.get("kling_2_6_pro", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "professional_tier": True
        }


class KlingV3StandardModel(BaseVideoModel):
    """
    Kling Video v3 Standard model for image-to-video generation.

    Features:
        - Native audio generation
        - Voice control support
        - Multi-prompt sequences
        - Custom elements/characters with reference images
        - End frame interpolation

    API Parameters:
        - prompt: Text description
        - start_image_url: Input image URL (start frame)
        - end_image_url: End frame for interpolation (optional)
        - duration: Video length in seconds (default: 5, max: 12)
        - generate_audio: Enable native audio generation
        - voice_ids: Custom voice IDs for audio
        - multi_prompt: Multiple prompt segments
        - elements: Custom character/object elements
        - aspect_ratio: Output format (16:9, 9:16, 1:1)
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)

    Pricing:
        - $0.168/second (audio off)
        - $0.252/second (audio on)
        - $0.308/second (with voice control)
    """

    MODEL_KEY = "kling_3_standard"

    def __init__(self):
        """Initialize the Kling v3 Standard image-to-video model."""
        super().__init__("kling_3_standard")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v3 Standard parameters."""
        defaults = DEFAULT_VALUES.get("kling_3_standard", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", "blur, distort, and low quality"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        end_frame = kwargs.get("end_frame")
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", False))
        voice_ids = kwargs.get("voice_ids", defaults.get("voice_ids", []))
        multi_prompt = kwargs.get("multi_prompt", defaults.get("multi_prompt", []))
        elements = kwargs.get("elements", defaults.get("elements", []))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_3_standard", ["5", "10", "12"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        # Validate aspect_ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_3_standard", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": str(duration),
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "end_frame": end_frame,
            "generate_audio": bool(generate_audio),
            "voice_ids": voice_ids if isinstance(voice_ids, list) else [],
            "multi_prompt": multi_prompt if isinstance(multi_prompt, list) else [],
            "elements": elements if isinstance(elements, list) else [],
            "aspect_ratio": aspect_ratio
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling v3 Standard."""
        args = {
            "prompt": prompt,
            "start_image_url": image_url,
            "duration": int(kwargs.get("duration", "5")),
            "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5),
            "generate_audio": kwargs.get("generate_audio", False)
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add end frame for interpolation
        end_frame = kwargs.get("end_frame")
        if end_frame:
            args["end_image_url"] = end_frame

        # Add voice IDs if audio is enabled
        voice_ids = kwargs.get("voice_ids", [])
        if voice_ids and args["generate_audio"]:
            args["voice_ids"] = voice_ids

        # Add multi-prompt if provided
        multi_prompt = kwargs.get("multi_prompt", [])
        if multi_prompt:
            args["multi_prompt"] = multi_prompt

        # Add elements (custom characters/objects) if provided
        elements = kwargs.get("elements", [])
        if elements:
            args["elements"] = elements

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling v3 Standard model information."""
        return {
            **MODEL_INFO.get("kling_3_standard", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "audio_supported": True,
            "voice_control_supported": True
        }

    def estimate_cost(self, duration: int = 5, generate_audio: bool = False, voice_ids: List[str] = None, **kwargs) -> float:
        """
        Estimate cost based on duration and audio settings.

        Pricing:
            - $0.168/second (audio off)
            - $0.252/second (audio on)
            - $0.308/second (with voice control)
        """
        duration_seconds = int(duration)
        if voice_ids and generate_audio:
            cost_per_second = 0.308  # Voice control pricing
        elif generate_audio:
            cost_per_second = 0.252  # Audio on pricing
        else:
            cost_per_second = 0.168  # Audio off pricing
        return cost_per_second * duration_seconds


class KlingV3ProModel(BaseVideoModel):
    """
    Kling Video v3 Pro model for professional image-to-video generation.

    Features:
        - Top-tier cinematic visuals and fluid motion
        - Native audio generation
        - Voice control support
        - Multi-prompt sequences
        - Custom elements/characters with reference images
        - End frame interpolation
        - Enhanced quality over Standard

    API Parameters:
        - prompt: Text description
        - start_image_url: Input image URL (start frame)
        - end_image_url: End frame for interpolation (optional)
        - duration: Video length in seconds (default: 5, max: 12)
        - generate_audio: Enable native audio generation
        - voice_ids: Custom voice IDs for audio
        - multi_prompt: Multiple prompt segments
        - elements: Custom character/object elements
        - aspect_ratio: Output format (16:9, 9:16, 1:1)
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)

    Pricing:
        - $0.224/second (audio off)
        - $0.336/second (audio on)
        - $0.392/second (with voice control)
    """

    MODEL_KEY = "kling_3_pro"

    def __init__(self):
        """Initialize the Kling v3 Pro image-to-video model."""
        super().__init__("kling_3_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v3 Pro parameters."""
        defaults = DEFAULT_VALUES.get("kling_3_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", "blur, distort, and low quality"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        end_frame = kwargs.get("end_frame")
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", False))
        voice_ids = kwargs.get("voice_ids", defaults.get("voice_ids", []))
        multi_prompt = kwargs.get("multi_prompt", defaults.get("multi_prompt", []))
        elements = kwargs.get("elements", defaults.get("elements", []))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_3_pro", ["5", "10", "12"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        # Validate aspect_ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_3_pro", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": str(duration),
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "end_frame": end_frame,
            "generate_audio": bool(generate_audio),
            "voice_ids": voice_ids if isinstance(voice_ids, list) else [],
            "multi_prompt": multi_prompt if isinstance(multi_prompt, list) else [],
            "elements": elements if isinstance(elements, list) else [],
            "aspect_ratio": aspect_ratio
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling v3 Pro."""
        args = {
            "prompt": prompt,
            "start_image_url": image_url,
            "duration": int(kwargs.get("duration", "5")),
            "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5),
            "generate_audio": kwargs.get("generate_audio", False)
        }

        # Add aspect ratio
        aspect_ratio = kwargs.get("aspect_ratio")
        if aspect_ratio:
            args["aspect_ratio"] = aspect_ratio

        # Add end frame for interpolation
        end_frame = kwargs.get("end_frame")
        if end_frame:
            args["end_image_url"] = end_frame

        # Add voice IDs if audio is enabled
        voice_ids = kwargs.get("voice_ids", [])
        if voice_ids and args["generate_audio"]:
            args["voice_ids"] = voice_ids

        # Add multi-prompt if provided
        multi_prompt = kwargs.get("multi_prompt", [])
        if multi_prompt:
            args["multi_prompt"] = multi_prompt

        # Add elements (custom characters/objects) if provided
        elements = kwargs.get("elements", [])
        if elements:
            args["elements"] = elements

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling v3 Pro model information."""
        return {
            **MODEL_INFO.get("kling_3_pro", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "professional_tier": True,
            "audio_supported": True,
            "voice_control_supported": True
        }

    def estimate_cost(self, duration: int = 5, generate_audio: bool = False, voice_ids: List[str] = None, **kwargs) -> float:
        """
        Estimate cost based on duration and audio settings.

        Pricing:
            - $0.224/second (audio off)
            - $0.336/second (audio on)
            - $0.392/second (with voice control)
        """
        duration_seconds = int(duration)
        if voice_ids and generate_audio:
            cost_per_second = 0.392  # Voice control pricing
        elif generate_audio:
            cost_per_second = 0.336  # Audio on pricing
        else:
            cost_per_second = 0.224  # Audio off pricing
        return cost_per_second * duration_seconds
