"""
Kling Video text-to-video model implementations (v2.6 Pro, v3 Standard, v3 Pro).

Supports:
- Native audio generation
- Voice control (v3 models)
- Multi-prompt sequences (v3 models)
- Shot type customization (v3 models)
"""

from typing import Dict, Any, List
from .base import BaseTextToVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class Kling26ProModel(BaseTextToVideoModel):
    """
    Kling Video v2.6 Pro for text-to-video generation.

    API Parameters:
        - prompt: Text description
        - duration: "5", "10" seconds
        - aspect_ratio: "16:9", "9:16", "1:1"
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)
        - generate_audio: Enable audio generation

    Pricing: $0.07/second (no audio), $0.14/second (with audio)
    """

    MODEL_KEY = "kling_2_6_pro"

    def __init__(self):
        """Initialize the Kling v2.6 Pro text-to-video model."""
        super().__init__("kling_2_6_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v2.6 Pro parameters."""
        defaults = DEFAULT_VALUES.get("kling_2_6_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_2_6_pro", ["5", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_2_6_pro", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        return {
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "generate_audio": bool(generate_audio)
        }

    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kling v2.6 Pro."""
        args = {
            "prompt": prompt,
            "duration": kwargs.get("duration", "5"),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5),
            "generate_audio": kwargs.get("generate_audio", True)
        }

        # Add negative prompt if provided
        negative_prompt = kwargs.get("negative_prompt")
        if negative_prompt:
            args["negative_prompt"] = negative_prompt

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling v2.6 Pro model information."""
        return {
            **MODEL_INFO.get("kling_2_6_pro", {}),
            "endpoint": self.endpoint,
            "pricing": self.pricing
        }

    def estimate_cost(self, duration: str = "5", generate_audio: bool = True, **kwargs) -> float:
        """Estimate cost based on duration and audio setting."""
        duration_seconds = int(duration)
        if generate_audio:
            cost_per_second = self.pricing.get("cost_with_audio", 0.14)
        else:
            cost_per_second = self.pricing.get("cost_no_audio", 0.07)
        return cost_per_second * duration_seconds


class KlingV3StandardModel(BaseTextToVideoModel):
    """
    Kling Video v3 Standard for text-to-video generation.

    Features:
        - Native audio generation
        - Voice control support
        - Multi-prompt sequences
        - Shot type customization

    API Parameters:
        - prompt: Text description
        - duration: Video length in seconds (default: 5, max: 12)
        - aspect_ratio: "16:9", "9:16", "1:1"
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)
        - generate_audio: Enable audio generation
        - voice_ids: Custom voice IDs for audio
        - multi_prompt: Multiple prompt segments
        - shot_type: Camera movement customization

    Pricing:
        - $0.168/second (audio off)
        - $0.252/second (audio on)
        - $0.308/second (with voice control)
    """

    MODEL_KEY = "kling_3_standard"

    def __init__(self):
        """Initialize the Kling v3 Standard text-to-video model."""
        super().__init__("kling_3_standard")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v3 Standard parameters."""
        defaults = DEFAULT_VALUES.get("kling_3_standard", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", False))
        voice_ids = kwargs.get("voice_ids", defaults.get("voice_ids", []))
        multi_prompt = kwargs.get("multi_prompt", defaults.get("multi_prompt", []))
        shot_type = kwargs.get("shot_type", defaults.get("shot_type"))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_3_standard", ["5", "10", "12"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_3_standard", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        return {
            "duration": str(duration),
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "generate_audio": bool(generate_audio),
            "voice_ids": voice_ids if isinstance(voice_ids, list) else [],
            "multi_prompt": multi_prompt if isinstance(multi_prompt, list) else [],
            "shot_type": shot_type
        }

    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kling v3 Standard."""
        args = {
            "prompt": prompt,
            "duration": int(kwargs.get("duration", "5")),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5),
            "generate_audio": kwargs.get("generate_audio", False)
        }

        # Add negative prompt if provided
        negative_prompt = kwargs.get("negative_prompt")
        if negative_prompt:
            args["negative_prompt"] = negative_prompt

        # Add voice IDs if audio is enabled
        voice_ids = kwargs.get("voice_ids", [])
        if voice_ids and args["generate_audio"]:
            args["voice_ids"] = voice_ids

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
        """Get Kling v3 Standard model information."""
        return {
            **MODEL_INFO.get("kling_3_standard", {}),
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "audio_supported": True,
            "voice_control_supported": True
        }

    def estimate_cost(self, duration: str = "5", generate_audio: bool = False, voice_ids: List[str] = None, **kwargs) -> float:
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


class KlingV3ProModel(BaseTextToVideoModel):
    """
    Kling Video v3 Pro for professional text-to-video generation.

    Features:
        - Top-tier cinematic visuals and fluid motion
        - Native audio generation
        - Voice control support
        - Multi-prompt sequences
        - Shot type customization
        - Enhanced quality over Standard

    API Parameters:
        - prompt: Text description
        - duration: Video length in seconds (default: 5, max: 12)
        - aspect_ratio: "16:9", "9:16", "1:1"
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)
        - generate_audio: Enable audio generation
        - voice_ids: Custom voice IDs for audio
        - multi_prompt: Multiple prompt segments
        - shot_type: Camera movement customization

    Pricing:
        - $0.224/second (audio off)
        - $0.336/second (audio on)
        - $0.392/second (with voice control)
    """

    MODEL_KEY = "kling_3_pro"

    def __init__(self):
        """Initialize the Kling v3 Pro text-to-video model."""
        super().__init__("kling_3_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v3 Pro parameters."""
        defaults = DEFAULT_VALUES.get("kling_3_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", False))
        voice_ids = kwargs.get("voice_ids", defaults.get("voice_ids", []))
        multi_prompt = kwargs.get("multi_prompt", defaults.get("multi_prompt", []))
        shot_type = kwargs.get("shot_type", defaults.get("shot_type"))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("kling_3_pro", ["5", "10", "12"])
        if str(duration) not in [str(d) for d in valid_durations]:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("kling_3_pro", ["16:9", "9:16", "1:1"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        # Validate cfg_scale
        if not 0.0 <= cfg_scale <= 1.0:
            raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

        return {
            "duration": str(duration),
            "aspect_ratio": aspect_ratio,
            "negative_prompt": negative_prompt,
            "cfg_scale": cfg_scale,
            "generate_audio": bool(generate_audio),
            "voice_ids": voice_ids if isinstance(voice_ids, list) else [],
            "multi_prompt": multi_prompt if isinstance(multi_prompt, list) else [],
            "shot_type": shot_type
        }

    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Kling v3 Pro."""
        args = {
            "prompt": prompt,
            "duration": int(kwargs.get("duration", "5")),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5),
            "generate_audio": kwargs.get("generate_audio", False)
        }

        # Add negative prompt if provided
        negative_prompt = kwargs.get("negative_prompt")
        if negative_prompt:
            args["negative_prompt"] = negative_prompt

        # Add voice IDs if audio is enabled
        voice_ids = kwargs.get("voice_ids", [])
        if voice_ids and args["generate_audio"]:
            args["voice_ids"] = voice_ids

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
        """Get Kling v3 Pro model information."""
        return {
            **MODEL_INFO.get("kling_3_pro", {}),
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "professional_tier": True,
            "audio_supported": True,
            "voice_control_supported": True
        }

    def estimate_cost(self, duration: str = "5", generate_audio: bool = False, voice_ids: List[str] = None, **kwargs) -> float:
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
