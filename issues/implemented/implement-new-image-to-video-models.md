# Implementation Plan: New FAL AI Image-to-Video Models

**Status: IMPLEMENTED** (2026-01-12)

Add 5 new image-to-video models with a refactored modular architecture for long-term maintainability.

## Implementation Status

| Subtask | Description | Status |
|---------|-------------|--------|
| 1 | Package structure & constants | ✅ Complete |
| 2 | Base model class | ✅ Complete |
| 3 | Sora 2 models | ✅ Complete |
| 4 | Veo 3.1 Fast model | ✅ Complete |
| 5 | Seedance model | ✅ Complete |
| 6 | Kling models | ✅ Complete |
| 7 | Hailuo model | ✅ Complete |
| 8 | Utility functions | ✅ Complete |
| 9 | Unified generator | ✅ Complete |
| 10 | Unit tests | ✅ Complete (28 tests passing) |

### Files Created

```
packages/providers/fal/image-to-video/fal_image_to_video/
├── __init__.py
├── generator.py
├── config/
│   ├── __init__.py
│   └── constants.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── hailuo.py
│   ├── kling.py
│   ├── seedance.py
│   ├── sora.py
│   └── veo.py
└── utils/
    ├── __init__.py
    ├── file_utils.py
    └── validators.py

packages/providers/fal/image-to-video/tests/
└── test_video_models.py
```

## New Models to Implement

| Model | Endpoint | Pricing | Key Features |
|-------|----------|---------|--------------|
| ByteDance Seedance v1.5 Pro | `fal-ai/bytedance/seedance/v1.5/pro/image-to-video` | ~$0.08/s | High quality, motion control |
| Kling Video v2.6 Pro | `fal-ai/kling-video/v2.6/pro/image-to-video` | ~$0.10/s | Professional tier, longer videos |
| Sora 2 | `fal-ai/sora-2/image-to-video` | $0.10/s | 720p, 4-12s duration |
| Sora 2 Pro | `fal-ai/sora-2/image-to-video/pro` | $0.30-0.50/s | 720p-1080p, higher quality |
| Veo 3.1 Fast | `fal-ai/veo3.1/fast/image-to-video` | $0.10-0.15/s | Audio generation, fast |

## Architecture Overview

Refactor from single-file to modular package (matching image-to-image pattern):

```
packages/providers/fal/image-to-video/
├── fal_image_to_video/
│   ├── __init__.py
│   ├── generator.py              # Main unified generator
│   ├── config/
│   │   ├── __init__.py
│   │   └── constants.py          # Endpoints, defaults, enums
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract base model
│   │   ├── hailuo.py             # Existing MiniMax Hailuo
│   │   ├── kling.py              # Kling v2.1 + v2.6 Pro
│   │   ├── seedance.py           # ByteDance Seedance v1.5 Pro
│   │   ├── sora.py               # Sora 2 + Sora 2 Pro
│   │   └── veo.py                # Veo 3.1 Fast
│   └── utils/
│       ├── __init__.py
│       ├── validators.py         # Parameter validation
│       └── file_utils.py         # Download, upload utilities
├── fal_image_to_video_generator.py  # Legacy compatibility wrapper
└── tests/
    └── test_models.py
```

---

## Subtask 1: Create Package Structure and Constants (15 min)

### Files to Create

#### 1.1 `packages/providers/fal/image-to-video/fal_image_to_video/__init__.py`

```python
"""
FAL AI Image-to-Video Generator Package

Supports multiple models for high-quality video generation from images.
"""

from .generator import FALImageToVideoGenerator
from .config.constants import ModelType, SUPPORTED_MODELS

__version__ = "2.0.0"
__all__ = ["FALImageToVideoGenerator", "ModelType", "SUPPORTED_MODELS"]
```

#### 1.2 `packages/providers/fal/image-to-video/fal_image_to_video/config/__init__.py`

```python
"""Configuration module for FAL Image-to-Video."""
from .constants import *
```

#### 1.3 `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`

```python
"""
Constants and configuration for FAL Image-to-Video models.
"""

from typing import Literal, List

# Model type definitions
ModelType = Literal[
    "hailuo",
    "kling_2_1",
    "kling_2_6_pro",
    "seedance_1_5_pro",
    "sora_2",
    "sora_2_pro",
    "veo_3_1_fast"
]

SUPPORTED_MODELS: List[str] = [
    "hailuo",
    "kling_2_1",
    "kling_2_6_pro",
    "seedance_1_5_pro",
    "sora_2",
    "sora_2_pro",
    "veo_3_1_fast"
]

# Model endpoints
MODEL_ENDPOINTS = {
    "hailuo": "fal-ai/minimax/hailuo-02/standard/image-to-video",
    "kling_2_1": "fal-ai/kling-video/v2.1/standard/image-to-video",
    "kling_2_6_pro": "fal-ai/kling-video/v2.6/pro/image-to-video",
    "seedance_1_5_pro": "fal-ai/bytedance/seedance/v1.5/pro/image-to-video",
    "sora_2": "fal-ai/sora-2/image-to-video",
    "sora_2_pro": "fal-ai/sora-2/image-to-video/pro",
    "veo_3_1_fast": "fal-ai/veo3.1/fast/image-to-video"
}

# Display names
MODEL_DISPLAY_NAMES = {
    "hailuo": "MiniMax Hailuo-02",
    "kling_2_1": "Kling Video v2.1",
    "kling_2_6_pro": "Kling Video v2.6 Pro",
    "seedance_1_5_pro": "ByteDance Seedance v1.5 Pro",
    "sora_2": "Sora 2",
    "sora_2_pro": "Sora 2 Pro",
    "veo_3_1_fast": "Veo 3.1 Fast"
}

# Pricing per second (USD)
MODEL_PRICING = {
    "hailuo": 0.05,
    "kling_2_1": 0.05,
    "kling_2_6_pro": 0.10,
    "seedance_1_5_pro": 0.08,
    "sora_2": 0.10,
    "sora_2_pro": 0.30,  # 720p, 0.50 for 1080p
    "veo_3_1_fast": 0.10  # +0.05 with audio
}

# Duration options per model
DURATION_OPTIONS = {
    "hailuo": ["6", "10"],
    "kling_2_1": ["5", "10"],
    "kling_2_6_pro": ["5", "10"],
    "seedance_1_5_pro": ["5", "10"],
    "sora_2": [4, 8, 12],
    "sora_2_pro": [4, 8, 12],
    "veo_3_1_fast": ["4s", "6s", "8s"]
}

# Resolution options per model
RESOLUTION_OPTIONS = {
    "hailuo": ["768p"],
    "kling_2_1": ["720p", "1080p"],
    "kling_2_6_pro": ["720p", "1080p"],
    "seedance_1_5_pro": ["720p", "1080p"],
    "sora_2": ["auto", "720p"],
    "sora_2_pro": ["auto", "720p", "1080p"],
    "veo_3_1_fast": ["720p", "1080p"]
}

# Aspect ratio options
ASPECT_RATIO_OPTIONS = {
    "sora_2": ["auto", "9:16", "16:9"],
    "sora_2_pro": ["auto", "9:16", "16:9"],
    "veo_3_1_fast": ["auto", "16:9", "9:16"]
}

# Default values per model
DEFAULT_VALUES = {
    "hailuo": {
        "duration": "6",
        "prompt_optimizer": True
    },
    "kling_2_1": {
        "duration": "5",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5
    },
    "kling_2_6_pro": {
        "duration": "5",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5
    },
    "seedance_1_5_pro": {
        "duration": "5",
        "seed": None
    },
    "sora_2": {
        "duration": 4,
        "resolution": "auto",
        "aspect_ratio": "auto",
        "delete_video": True
    },
    "sora_2_pro": {
        "duration": 4,
        "resolution": "auto",
        "aspect_ratio": "auto",
        "delete_video": True
    },
    "veo_3_1_fast": {
        "duration": "8s",
        "resolution": "720p",
        "aspect_ratio": "auto",
        "generate_audio": True,
        "auto_fix": False
    }
}

# Model info for documentation
MODEL_INFO = {
    "hailuo": {
        "name": "MiniMax Hailuo-02",
        "provider": "MiniMax",
        "description": "Standard image-to-video with prompt optimization",
        "max_duration": 10,
        "features": ["prompt_optimizer"]
    },
    "kling_2_1": {
        "name": "Kling Video v2.1",
        "provider": "Kuaishou",
        "description": "High-quality generation with negative prompts",
        "max_duration": 10,
        "features": ["negative_prompt", "cfg_scale"]
    },
    "kling_2_6_pro": {
        "name": "Kling Video v2.6 Pro",
        "provider": "Kuaishou",
        "description": "Professional tier with enhanced quality",
        "max_duration": 10,
        "features": ["negative_prompt", "cfg_scale", "professional_quality"]
    },
    "seedance_1_5_pro": {
        "name": "ByteDance Seedance v1.5 Pro",
        "provider": "ByteDance",
        "description": "Advanced motion synthesis with seed control",
        "max_duration": 10,
        "features": ["seed_control", "motion_quality"]
    },
    "sora_2": {
        "name": "Sora 2",
        "provider": "OpenAI (via FAL)",
        "description": "OpenAI's image-to-video model",
        "max_duration": 12,
        "features": ["aspect_ratio", "resolution"]
    },
    "sora_2_pro": {
        "name": "Sora 2 Pro",
        "provider": "OpenAI (via FAL)",
        "description": "Professional Sora with 1080p support",
        "max_duration": 12,
        "features": ["aspect_ratio", "resolution", "1080p"]
    },
    "veo_3_1_fast": {
        "name": "Veo 3.1 Fast",
        "provider": "Google (via FAL)",
        "description": "Fast video generation with optional audio",
        "max_duration": 8,
        "features": ["audio_generation", "auto_fix", "fast_processing"]
    }
}
```

---

## Subtask 2: Create Base Model Class (10 min)

### File to Create

#### 2.1 `packages/providers/fal/image-to-video/fal_image_to_video/models/__init__.py`

```python
"""Model implementations for FAL Image-to-Video."""

from .base import BaseVideoModel
from .hailuo import HailuoModel
from .kling import KlingModel, Kling26ProModel
from .seedance import SeedanceModel
from .sora import Sora2Model, Sora2ProModel
from .veo import Veo31FastModel

__all__ = [
    "BaseVideoModel",
    "HailuoModel",
    "KlingModel",
    "Kling26ProModel",
    "SeedanceModel",
    "Sora2Model",
    "Sora2ProModel",
    "Veo31FastModel"
]
```

#### 2.2 `packages/providers/fal/image-to-video/fal_image_to_video/models/base.py`

```python
"""
Base model interface for FAL Image-to-Video models.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import fal_client

from ..config.constants import MODEL_ENDPOINTS, MODEL_DISPLAY_NAMES, MODEL_PRICING
from ..utils.file_utils import download_video, ensure_output_directory


class BaseVideoModel(ABC):
    """
    Abstract base class for all FAL Image-to-Video models.
    """

    def __init__(self, model_key: str):
        """
        Initialize base model.

        Args:
            model_key: Model identifier (e.g., "hailuo", "sora_2")
        """
        self.model_key = model_key
        self.endpoint = MODEL_ENDPOINTS[model_key]
        self.display_name = MODEL_DISPLAY_NAMES[model_key]
        self.price_per_second = MODEL_PRICING[model_key]

    @abstractmethod
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate model-specific parameters.

        Returns:
            Dictionary of validated parameters

        Raises:
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare API arguments for the model.

        Args:
            prompt: Text description for video generation
            image_url: URL of input image
            **kwargs: Model-specific parameters

        Returns:
            Dictionary of API arguments
        """
        pass

    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process API response and extract video info.

        Args:
            response: Raw API response

        Returns:
            Processed video information
        """
        video_info = response.get("video", {})
        return {
            "url": video_info.get("url"),
            "content_type": video_info.get("content_type"),
            "file_name": video_info.get("file_name"),
            "file_size": video_info.get("file_size"),
            "duration": video_info.get("duration"),
            "fps": video_info.get("fps"),
            "width": video_info.get("width"),
            "height": video_info.get("height")
        }

    def generate(
        self,
        prompt: str,
        image_url: str,
        output_dir: Optional[str] = None,
        use_async: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video using the model.

        Args:
            prompt: Text description for video generation
            image_url: URL of input image
            output_dir: Custom output directory
            use_async: Whether to use async processing
            **kwargs: Model-specific parameters

        Returns:
            Dictionary containing generation results
        """
        try:
            # Validate parameters
            validated_params = self.validate_parameters(**kwargs)

            # Prepare API arguments
            arguments = self.prepare_arguments(prompt, image_url, **validated_params)

            # Log generation info
            self._log_generation_start(prompt, image_url, **validated_params)

            # Make API call
            start_time = time.time()

            def on_queue_update(update):
                if hasattr(update, 'logs') and update.logs:
                    for log in update.logs:
                        print(f"  {log.get('message', str(log))}")

            if use_async:
                result = self._generate_async(arguments)
            else:
                result = fal_client.subscribe(
                    self.endpoint,
                    arguments=arguments,
                    with_logs=True,
                    on_queue_update=on_queue_update
                )

            processing_time = time.time() - start_time
            print(f"✅ Generation completed in {processing_time:.2f} seconds")

            # Process response
            video_info = self.process_response(result)
            if not video_info.get("url"):
                raise Exception("No video URL in response")

            # Download video
            output_directory = ensure_output_directory(output_dir)
            local_path = download_video(
                video_info["url"],
                output_directory,
                self.model_key
            )

            # Calculate cost estimate
            duration = validated_params.get("duration", 5)
            if isinstance(duration, str):
                duration = int(duration.replace("s", ""))
            cost_estimate = self.price_per_second * duration

            return {
                "success": True,
                "model": self.display_name,
                "model_key": self.model_key,
                "prompt": prompt,
                "video": video_info,
                "local_path": local_path,
                "processing_time": processing_time,
                "cost_estimate": cost_estimate,
                **validated_params
            }

        except Exception as e:
            print(f"❌ Error during video generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.display_name,
                "model_key": self.model_key,
                "prompt": prompt
            }

    def _generate_async(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle async generation with polling."""
        handler = fal_client.submit(self.endpoint, arguments=arguments)
        request_id = handler.request_id
        print(f"📤 Request submitted: {request_id}")

        while True:
            status = fal_client.status(self.endpoint, request_id, with_logs=True)
            print(f"   Status: {status.status}")

            if status.status == "COMPLETED":
                return fal_client.result(self.endpoint, request_id)
            elif status.status == "FAILED":
                raise Exception(f"Generation failed: {status}")

            time.sleep(5)

    def _log_generation_start(self, prompt: str, image_url: str, **params):
        """Log generation start with parameters."""
        print(f"🎬 Generating video with {self.display_name}...")
        print(f"   Prompt: {prompt[:100]}...")
        print(f"   Image: {image_url[:50]}...")
        for key, value in params.items():
            if value is not None:
                print(f"   {key}: {value}")

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and capabilities."""
        pass

    def estimate_cost(self, duration: int) -> float:
        """Estimate cost for generation."""
        return self.price_per_second * duration
```

---

## Subtask 3: Implement Sora 2 Models (15 min)

### File to Create

#### 3.1 `packages/providers/fal/image-to-video/fal_image_to_video/models/sora.py`

```python
"""
Sora 2 and Sora 2 Pro model implementations.

OpenAI's image-to-video models accessed via FAL AI.
"""

from typing import Dict, Any
from .base import BaseVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class Sora2Model(BaseVideoModel):
    """
    Sora 2 model for image-to-video generation.

    API Parameters:
        - prompt: Text description (1-5000 chars)
        - image_url: Input image URL
        - resolution: auto, 720p
        - aspect_ratio: auto, 9:16, 16:9
        - duration: 4, 8, 12 seconds
        - delete_video: Auto-delete for privacy

    Pricing: $0.10/second
    """

    def __init__(self):
        super().__init__("sora_2")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Sora 2 parameters."""
        defaults = DEFAULT_VALUES.get("sora_2", {})

        duration = kwargs.get("duration", defaults.get("duration", 4))
        resolution = kwargs.get("resolution", defaults.get("resolution", "auto"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "auto"))
        delete_video = kwargs.get("delete_video", defaults.get("delete_video", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("sora_2", [4, 8, 12])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("sora_2", ["auto", "720p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("sora_2", ["auto", "9:16", "16:9"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "delete_video": bool(delete_video)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Sora 2."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", 4),
            "resolution": kwargs.get("resolution", "auto"),
            "aspect_ratio": kwargs.get("aspect_ratio", "auto"),
            "delete_video": kwargs.get("delete_video", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Sora 2 model information."""
        return {
            **MODEL_INFO.get("sora_2", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }


class Sora2ProModel(BaseVideoModel):
    """
    Sora 2 Pro model for professional image-to-video generation.

    API Parameters:
        - prompt: Text description (1-5000 chars)
        - image_url: Input image URL
        - resolution: auto, 720p, 1080p
        - aspect_ratio: auto, 9:16, 16:9
        - duration: 4, 8, 12 seconds
        - delete_video: Auto-delete for privacy

    Pricing: $0.30/second (720p), $0.50/second (1080p)
    """

    def __init__(self):
        super().__init__("sora_2_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Sora 2 Pro parameters."""
        defaults = DEFAULT_VALUES.get("sora_2_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", 4))
        resolution = kwargs.get("resolution", defaults.get("resolution", "auto"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "auto"))
        delete_video = kwargs.get("delete_video", defaults.get("delete_video", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("sora_2_pro", [4, 8, 12])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("sora_2_pro", ["auto", "720p", "1080p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("sora_2_pro", ["auto", "9:16", "16:9"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "delete_video": bool(delete_video)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Sora 2 Pro."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", 4),
            "resolution": kwargs.get("resolution", "auto"),
            "aspect_ratio": kwargs.get("aspect_ratio", "auto"),
            "delete_video": kwargs.get("delete_video", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Sora 2 Pro model information."""
        return {
            **MODEL_INFO.get("sora_2_pro", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }

    def estimate_cost(self, duration: int, resolution: str = "720p") -> float:
        """Estimate cost with resolution-based pricing."""
        if resolution == "1080p":
            return 0.50 * duration
        return 0.30 * duration
```

---

## Subtask 4: Implement Veo 3.1 Fast Model (15 min)

### File to Create

#### 4.1 `packages/providers/fal/image-to-video/fal_image_to_video/models/veo.py`

```python
"""
Veo 3.1 Fast model implementation.

Google's fast image-to-video model with audio generation support.
"""

from typing import Dict, Any
from .base import BaseVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class Veo31FastModel(BaseVideoModel):
    """
    Veo 3.1 Fast model for image-to-video generation with audio.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL (720p+, 16:9 or 9:16)
        - aspect_ratio: auto, 16:9, 9:16
        - duration: 4s, 6s, 8s
        - resolution: 720p, 1080p
        - generate_audio: Enable audio generation
        - auto_fix: Auto-fix input issues

    Pricing: $0.10/second (no audio), $0.15/second (with audio)
    """

    def __init__(self):
        super().__init__("veo_3_1_fast")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Veo 3.1 Fast parameters."""
        defaults = DEFAULT_VALUES.get("veo_3_1_fast", {})

        duration = kwargs.get("duration", defaults.get("duration", "8s"))
        resolution = kwargs.get("resolution", defaults.get("resolution", "720p"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "auto"))
        generate_audio = kwargs.get("generate_audio", defaults.get("generate_audio", True))
        auto_fix = kwargs.get("auto_fix", defaults.get("auto_fix", False))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("veo_3_1_fast", ["4s", "6s", "8s"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("veo_3_1_fast", ["720p", "1080p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("veo_3_1_fast", ["auto", "16:9", "9:16"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "generate_audio": bool(generate_audio),
            "auto_fix": bool(auto_fix)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Veo 3.1 Fast."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "8s"),
            "resolution": kwargs.get("resolution", "720p"),
            "aspect_ratio": kwargs.get("aspect_ratio", "auto"),
            "generate_audio": kwargs.get("generate_audio", True),
            "auto_fix": kwargs.get("auto_fix", False)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Veo 3.1 Fast model information."""
        return {
            **MODEL_INFO.get("veo_3_1_fast", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "supports_audio": True
        }

    def estimate_cost(self, duration: str, generate_audio: bool = True) -> float:
        """Estimate cost with audio-based pricing."""
        # Parse duration string (e.g., "8s" -> 8)
        seconds = int(duration.replace("s", ""))
        base_rate = 0.15 if generate_audio else 0.10
        return base_rate * seconds
```

---

## Subtask 5: Implement Seedance Model (15 min)

### File to Create

#### 5.1 `packages/providers/fal/image-to-video/fal_image_to_video/models/seedance.py`

```python
"""
ByteDance Seedance v1.5 Pro model implementation.

Advanced motion synthesis with seed control.
"""

from typing import Dict, Any, Optional
from .base import BaseVideoModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, DURATION_OPTIONS


class SeedanceModel(BaseVideoModel):
    """
    ByteDance Seedance v1.5 Pro model for image-to-video generation.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL
        - duration: 5, 10 seconds
        - seed: Optional seed for reproducibility

    Pricing: ~$0.08/second
    """

    def __init__(self):
        super().__init__("seedance_1_5_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Seedance parameters."""
        defaults = DEFAULT_VALUES.get("seedance_1_5_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        seed = kwargs.get("seed", defaults.get("seed", None))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("seedance_1_5_pro", ["5", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate seed if provided
        if seed is not None:
            if not isinstance(seed, int) or seed < 0:
                raise ValueError("Seed must be a non-negative integer")

        return {
            "duration": duration,
            "seed": seed
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Seedance."""
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5")
        }

        # Add optional seed
        seed = kwargs.get("seed")
        if seed is not None:
            args["seed"] = seed

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Seedance model information."""
        return {
            **MODEL_INFO.get("seedance_1_5_pro", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "supports_seed": True
        }
```

---

## Subtask 6: Implement Kling v2.6 Pro Model (15 min)

### File to Create

#### 6.1 `packages/providers/fal/image-to-video/fal_image_to_video/models/kling.py`

```python
"""
Kling Video model implementations (v2.1 and v2.6 Pro).
"""

from typing import Dict, Any
from .base import BaseVideoModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, DURATION_OPTIONS


class KlingModel(BaseVideoModel):
    """
    Kling Video v2.1 model for image-to-video generation.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL
        - duration: 5, 10 seconds
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)

    Pricing: ~$0.05/second
    """

    def __init__(self):
        super().__init__("kling_2_1")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v2.1 parameters."""
        defaults = DEFAULT_VALUES.get("kling_2_1", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", "blur, distort, and low quality"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))

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
            "cfg_scale": cfg_scale
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling v2.1."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5"),
            "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5)
        }

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
        - image_url: Input image URL
        - duration: 5, 10 seconds
        - negative_prompt: Elements to avoid
        - cfg_scale: Guidance scale (0-1)

    Pricing: ~$0.10/second
    """

    def __init__(self):
        super().__init__("kling_2_6_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Kling v2.6 Pro parameters."""
        defaults = DEFAULT_VALUES.get("kling_2_6_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", "blur, distort, and low quality"))
        cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))

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
            "cfg_scale": cfg_scale
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Kling v2.6 Pro."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5"),
            "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
            "cfg_scale": kwargs.get("cfg_scale", 0.5)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Kling v2.6 Pro model information."""
        return {
            **MODEL_INFO.get("kling_2_6_pro", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second,
            "professional_tier": True
        }
```

---

## Subtask 7: Implement Hailuo Model (Refactor Existing) (10 min)

### File to Create

#### 7.1 `packages/providers/fal/image-to-video/fal_image_to_video/models/hailuo.py`

```python
"""
MiniMax Hailuo-02 model implementation.

Refactored from existing implementation for modular architecture.
"""

from typing import Dict, Any
from .base import BaseVideoModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, DURATION_OPTIONS


class HailuoModel(BaseVideoModel):
    """
    MiniMax Hailuo-02 model for image-to-video generation.

    API Parameters:
        - prompt: Text description
        - image_url: Input image URL
        - duration: 6, 10 seconds
        - prompt_optimizer: Enable prompt optimization

    Pricing: ~$0.05/second
    """

    def __init__(self):
        super().__init__("hailuo")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Hailuo parameters."""
        defaults = DEFAULT_VALUES.get("hailuo", {})

        duration = kwargs.get("duration", defaults.get("duration", "6"))
        prompt_optimizer = kwargs.get("prompt_optimizer", defaults.get("prompt_optimizer", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("hailuo", ["6", "10"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        return {
            "duration": duration,
            "prompt_optimizer": bool(prompt_optimizer)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Hailuo."""
        return {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "6"),
            "prompt_optimizer": kwargs.get("prompt_optimizer", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Hailuo model information."""
        return {
            **MODEL_INFO.get("hailuo", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }
```

---

## Subtask 8: Create Utility Functions (10 min)

### Files to Create

#### 8.1 `packages/providers/fal/image-to-video/fal_image_to_video/utils/__init__.py`

```python
"""Utility functions for FAL Image-to-Video."""
from .file_utils import download_video, upload_image, ensure_output_directory
from .validators import validate_model, validate_image_url

__all__ = [
    "download_video",
    "upload_image",
    "ensure_output_directory",
    "validate_model",
    "validate_image_url"
]
```

#### 8.2 `packages/providers/fal/image-to-video/fal_image_to_video/utils/file_utils.py`

```python
"""
File utility functions for FAL Image-to-Video.
"""

import os
import time
import requests
import fal_client
from pathlib import Path
from typing import Optional


def ensure_output_directory(output_dir: Optional[str] = None) -> Path:
    """
    Ensure output directory exists.

    Args:
        output_dir: Custom output directory path

    Returns:
        Path object for the output directory
    """
    if output_dir is None:
        output_dir = "output"

    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def download_video(
    video_url: str,
    output_dir: Path,
    model_key: str,
    filename: Optional[str] = None
) -> Optional[str]:
    """
    Download video from URL to local folder.

    Args:
        video_url: URL of the video to download
        output_dir: Output directory path
        model_key: Model identifier for filename
        filename: Optional custom filename

    Returns:
        Local path of the downloaded video or None if failed
    """
    try:
        if filename is None:
            timestamp = int(time.time())
            filename = f"{model_key}_video_{timestamp}.mp4"

        print(f"📥 Downloading video...")
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        local_path = output_dir / filename
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        absolute_path = str(local_path.absolute())
        print(f"✅ Video saved: {absolute_path}")
        return absolute_path

    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        return None


def upload_image(image_path: str) -> Optional[str]:
    """
    Upload a local image file to FAL AI.

    Args:
        image_path: Path to the local image file

    Returns:
        URL of the uploaded image or None if failed
    """
    try:
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return None

        print(f"📤 Uploading image: {image_path}")
        url = fal_client.upload_file(image_path)
        print(f"✅ Image uploaded: {url[:50]}...")
        return url

    except Exception as e:
        print(f"❌ Error uploading image: {e}")
        return None
```

#### 8.3 `packages/providers/fal/image-to-video/fal_image_to_video/utils/validators.py`

```python
"""
Parameter validation utilities for FAL Image-to-Video.
"""

from typing import List
from ..config.constants import SUPPORTED_MODELS


def validate_model(model: str) -> str:
    """
    Validate and return the model type.

    Args:
        model: Model type string

    Returns:
        Validated model type

    Raises:
        ValueError: If model is not supported
    """
    if model not in SUPPORTED_MODELS:
        raise ValueError(
            f"Unsupported model: {model}. "
            f"Supported models: {SUPPORTED_MODELS}"
        )
    return model


def validate_image_url(url: str) -> str:
    """
    Validate image URL format.

    Args:
        url: Image URL to validate

    Returns:
        Validated URL

    Raises:
        ValueError: If URL is invalid
    """
    if not url:
        raise ValueError("Image URL is required")

    if not url.startswith(("http://", "https://", "data:")):
        raise ValueError(
            f"Invalid image URL format: {url}. "
            "Must start with http://, https://, or data:"
        )

    return url
```

---

## Subtask 9: Create Unified Generator (15 min)

### File to Create

#### 9.1 `packages/providers/fal/image-to-video/fal_image_to_video/generator.py`

```python
"""
Main FAL Image-to-Video Generator with Multi-Model Support.

Unified interface for all image-to-video models.
"""

import os
from typing import Dict, Any, Optional, List
import fal_client
from dotenv import load_dotenv

from .models import (
    HailuoModel,
    KlingModel,
    Kling26ProModel,
    SeedanceModel,
    Sora2Model,
    Sora2ProModel,
    Veo31FastModel
)
from .utils.file_utils import upload_image, ensure_output_directory
from .config.constants import SUPPORTED_MODELS, MODEL_INFO

load_dotenv()


class FALImageToVideoGenerator:
    """
    Unified FAL AI Image-to-Video Generator with Multi-Model Support.

    Supports:
    - MiniMax Hailuo-02: Standard quality, prompt optimization
    - Kling Video v2.1: High-quality with negative prompts
    - Kling Video v2.6 Pro: Professional tier
    - ByteDance Seedance v1.5 Pro: Motion synthesis with seed control
    - Sora 2: OpenAI's image-to-video
    - Sora 2 Pro: Professional Sora with 1080p
    - Veo 3.1 Fast: Google's fast model with audio
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the generator.

        Args:
            api_key: FAL AI API key. If not provided, uses FAL_KEY env var.
        """
        if api_key:
            fal_client.api_key = api_key
        else:
            api_key = os.getenv('FAL_KEY')
            if not api_key:
                if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
                    print("⚠️  Running in CI environment - using mock mode")
                    self.mock_mode = True
                    api_key = "mock_key"
                else:
                    raise ValueError(
                        "FAL_KEY environment variable is not set. "
                        "Set it or provide api_key parameter."
                    )
            else:
                self.mock_mode = False
            fal_client.api_key = api_key

        # Initialize all models
        self.models = {
            "hailuo": HailuoModel(),
            "kling_2_1": KlingModel(),
            "kling_2_6_pro": Kling26ProModel(),
            "seedance_1_5_pro": SeedanceModel(),
            "sora_2": Sora2Model(),
            "sora_2_pro": Sora2ProModel(),
            "veo_3_1_fast": Veo31FastModel()
        }

        self.output_dir = ensure_output_directory("output")

    def generate_video(
        self,
        prompt: str,
        image_url: str,
        model: str = "hailuo",
        output_dir: Optional[str] = None,
        use_async: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from image using specified model.

        Args:
            prompt: Text description for video generation
            image_url: URL of input image
            model: Model to use (default: "hailuo")
            output_dir: Custom output directory
            use_async: Whether to use async processing
            **kwargs: Model-specific parameters

        Returns:
            Dictionary containing generation results
        """
        # Mock mode for CI
        if hasattr(self, 'mock_mode') and self.mock_mode:
            import time
            return {
                'success': True,
                'video': {'url': f'mock://video-{int(time.time())}.mp4'},
                'local_path': f'/tmp/mock_video_{int(time.time())}.mp4',
                'model': model,
                'mock_mode': True
            }

        if model not in self.models:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported: {list(self.models.keys())}"
            )

        return self.models[model].generate(
            prompt=prompt,
            image_url=image_url,
            output_dir=output_dir,
            use_async=use_async,
            **kwargs
        )

    def generate_video_from_local_image(
        self,
        prompt: str,
        image_path: str,
        model: str = "hailuo",
        output_dir: Optional[str] = None,
        use_async: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from local image file.

        Args:
            prompt: Text description for video generation
            image_path: Path to local image file
            model: Model to use
            output_dir: Custom output directory
            use_async: Whether to use async processing
            **kwargs: Model-specific parameters

        Returns:
            Dictionary containing generation results
        """
        # Upload local image
        image_url = upload_image(image_path)
        if not image_url:
            return {
                "success": False,
                "error": f"Failed to upload image: {image_path}",
                "model": model
            }

        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model=model,
            output_dir=output_dir,
            use_async=use_async,
            **kwargs
        )

    # Convenience methods for each model
    def generate_with_sora(
        self,
        prompt: str,
        image_url: str,
        duration: int = 4,
        resolution: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Sora 2."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="sora_2",
            duration=duration,
            resolution=resolution,
            **kwargs
        )

    def generate_with_sora_pro(
        self,
        prompt: str,
        image_url: str,
        duration: int = 4,
        resolution: str = "1080p",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Sora 2 Pro."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="sora_2_pro",
            duration=duration,
            resolution=resolution,
            **kwargs
        )

    def generate_with_veo(
        self,
        prompt: str,
        image_url: str,
        duration: str = "8s",
        generate_audio: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Veo 3.1 Fast."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="veo_3_1_fast",
            duration=duration,
            generate_audio=generate_audio,
            **kwargs
        )

    def generate_with_seedance(
        self,
        prompt: str,
        image_url: str,
        duration: str = "5",
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using ByteDance Seedance."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="seedance_1_5_pro",
            duration=duration,
            seed=seed,
            **kwargs
        )

    def generate_with_kling_pro(
        self,
        prompt: str,
        image_url: str,
        duration: str = "5",
        negative_prompt: str = "blur, distort, and low quality",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video using Kling v2.6 Pro."""
        return self.generate_video(
            prompt=prompt,
            image_url=image_url,
            model="kling_2_6_pro",
            duration=duration,
            negative_prompt=negative_prompt,
            **kwargs
        )

    # Information methods
    def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """Get information about supported models."""
        if model:
            if model not in self.models:
                raise ValueError(f"Unknown model: {model}")
            return self.models[model].get_model_info()
        return {
            model_key: model_obj.get_model_info()
            for model_key, model_obj in self.models.items()
        }

    def get_supported_models(self) -> List[str]:
        """Get list of supported models."""
        return list(self.models.keys())

    def estimate_cost(self, model: str, duration: int, **kwargs) -> float:
        """Estimate cost for generation."""
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        return self.models[model].estimate_cost(duration, **kwargs)
```

---

## Subtask 10: Update Legacy Wrapper for Backwards Compatibility (10 min)

### File to Modify

#### 10.1 `packages/providers/fal/image-to-video/fal_image_to_video_generator.py`

Add deprecation notice and wrapper to new package at the top of the file:

```python
"""
FAL AI Image-to-Video Generation - LEGACY WRAPPER

DEPRECATED: This file is maintained for backwards compatibility.
Use the new modular package instead:

    from fal_image_to_video import FALImageToVideoGenerator

The new package supports additional models:
- Sora 2 / Sora 2 Pro
- Veo 3.1 Fast (with audio)
- ByteDance Seedance v1.5 Pro
- Kling Video v2.6 Pro
"""

import warnings

# Show deprecation warning
warnings.warn(
    "fal_image_to_video_generator.py is deprecated. "
    "Use 'from fal_image_to_video import FALImageToVideoGenerator' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from new package for backwards compatibility
try:
    from fal_image_to_video import FALImageToVideoGenerator as NewGenerator

    class FALImageToVideoGenerator(NewGenerator):
        """Legacy wrapper for backwards compatibility."""

        def generate_video_from_image(self, *args, **kwargs):
            """Map old method to new interface."""
            # Map old model names to new
            model = kwargs.get("model", "")
            model_map = {
                "fal-ai/minimax/hailuo-02/standard/image-to-video": "hailuo",
                "fal-ai/kling-video/v2.1/standard/image-to-video": "kling_2_1"
            }
            if model in model_map:
                kwargs["model"] = model_map[model]

            return self.generate_video(*args, **kwargs)

except ImportError:
    # Fallback to original implementation if new package not available
    pass

# Original implementation follows for fallback...
```

---

## Subtask 11: Create Unit Tests (15 min)

### File to Create

#### 11.1 `packages/providers/fal/image-to-video/tests/test_models.py`

```python
"""
Unit tests for FAL Image-to-Video models.
"""

import pytest
import sys
from pathlib import Path

# Add package to path
_package_path = Path(__file__).parent.parent / "fal_image_to_video"
sys.path.insert(0, str(_package_path.parent))

from fal_image_to_video.config.constants import (
    SUPPORTED_MODELS,
    MODEL_ENDPOINTS,
    DURATION_OPTIONS,
    RESOLUTION_OPTIONS
)
from fal_image_to_video.models.sora import Sora2Model, Sora2ProModel
from fal_image_to_video.models.veo import Veo31FastModel
from fal_image_to_video.models.seedance import SeedanceModel
from fal_image_to_video.models.kling import KlingModel, Kling26ProModel


class TestConstants:
    """Tests for constants configuration."""

    def test_all_models_have_endpoints(self):
        """Every supported model should have an endpoint."""
        for model in SUPPORTED_MODELS:
            assert model in MODEL_ENDPOINTS

    def test_all_models_have_duration_options(self):
        """Every supported model should have duration options."""
        for model in SUPPORTED_MODELS:
            assert model in DURATION_OPTIONS


class TestSora2Model:
    """Tests for Sora 2 model."""

    def test_valid_parameters(self):
        """Valid parameters should pass validation."""
        model = Sora2Model()
        params = model.validate_parameters(
            duration=8,
            resolution="720p",
            aspect_ratio="16:9"
        )
        assert params["duration"] == 8
        assert params["resolution"] == "720p"

    def test_invalid_duration_raises_error(self):
        """Invalid duration should raise ValueError."""
        model = Sora2Model()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(duration=15)
        assert "Invalid duration" in str(exc_info.value)

    def test_invalid_resolution_raises_error(self):
        """Invalid resolution should raise ValueError."""
        model = Sora2Model()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(resolution="4K")
        assert "Invalid resolution" in str(exc_info.value)


class TestSora2ProModel:
    """Tests for Sora 2 Pro model."""

    def test_supports_1080p(self):
        """Sora 2 Pro should support 1080p resolution."""
        model = Sora2ProModel()
        params = model.validate_parameters(resolution="1080p")
        assert params["resolution"] == "1080p"

    def test_cost_estimation(self):
        """Cost estimation should vary by resolution."""
        model = Sora2ProModel()
        cost_720p = model.estimate_cost(duration=4, resolution="720p")
        cost_1080p = model.estimate_cost(duration=4, resolution="1080p")
        assert cost_1080p > cost_720p


class TestVeo31FastModel:
    """Tests for Veo 3.1 Fast model."""

    def test_valid_duration_format(self):
        """Duration should accept string format (e.g., '8s')."""
        model = Veo31FastModel()
        params = model.validate_parameters(duration="6s")
        assert params["duration"] == "6s"

    def test_audio_generation_option(self):
        """Audio generation should be configurable."""
        model = Veo31FastModel()
        params = model.validate_parameters(generate_audio=False)
        assert params["generate_audio"] is False

    def test_cost_with_audio(self):
        """Cost should be higher with audio enabled."""
        model = Veo31FastModel()
        cost_no_audio = model.estimate_cost("8s", generate_audio=False)
        cost_with_audio = model.estimate_cost("8s", generate_audio=True)
        assert cost_with_audio > cost_no_audio


class TestSeedanceModel:
    """Tests for Seedance model."""

    def test_seed_parameter(self):
        """Seed parameter should be optional."""
        model = SeedanceModel()
        params = model.validate_parameters(seed=12345)
        assert params["seed"] == 12345

    def test_invalid_seed_raises_error(self):
        """Negative seed should raise ValueError."""
        model = SeedanceModel()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(seed=-1)
        assert "non-negative" in str(exc_info.value)


class TestKlingModels:
    """Tests for Kling models."""

    def test_cfg_scale_validation(self):
        """CFG scale should be between 0 and 1."""
        model = KlingModel()
        params = model.validate_parameters(cfg_scale=0.7)
        assert params["cfg_scale"] == 0.7

    def test_invalid_cfg_scale_raises_error(self):
        """CFG scale > 1 should raise ValueError."""
        model = Kling26ProModel()
        with pytest.raises(ValueError) as exc_info:
            model.validate_parameters(cfg_scale=1.5)
        assert "cfg_scale" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Subtask 12: Update AI Content Pipeline Integration (15 min)

### File to Modify

#### 12.1 `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`

Add new models to the supported models list:

```python
# Add to SUPPORTED_MODELS["image_to_video"]
"image_to_video": [
    "hailuo",
    "kling_2_1",
    "kling_2_6_pro",
    "seedance_1_5_pro",
    "sora_2",
    "sora_2_pro",
    "veo_3_1_fast"
]

# Add to COST_ESTIMATES["image_to_video"]
"image_to_video": {
    "hailuo": 0.30,  # ~$0.05/s * 6s
    "kling_2_1": 0.25,  # ~$0.05/s * 5s
    "kling_2_6_pro": 0.50,  # ~$0.10/s * 5s
    "seedance_1_5_pro": 0.40,  # ~$0.08/s * 5s
    "sora_2": 0.40,  # $0.10/s * 4s
    "sora_2_pro": 1.20,  # $0.30/s * 4s
    "veo_3_1_fast": 1.20  # $0.15/s * 8s with audio
}
```

---

## Implementation Summary

| Subtask | Description | Est. Time | Files |
|---------|-------------|-----------|-------|
| 1 | Package structure & constants | 15 min | 3 files |
| 2 | Base model class | 10 min | 2 files |
| 3 | Sora 2 models | 15 min | 1 file |
| 4 | Veo 3.1 Fast model | 15 min | 1 file |
| 5 | Seedance model | 15 min | 1 file |
| 6 | Kling v2.6 Pro model | 15 min | 1 file |
| 7 | Hailuo model (refactor) | 10 min | 1 file |
| 8 | Utility functions | 10 min | 3 files |
| 9 | Unified generator | 15 min | 1 file |
| 10 | Legacy wrapper | 10 min | 1 file (modify) |
| 11 | Unit tests | 15 min | 1 file |
| 12 | Pipeline integration | 15 min | 1 file (modify) |

**Total Estimated Time:** ~2.5 hours

## Long-Term Benefits

1. **Maintainability**: Each model in its own file, easy to update
2. **Extensibility**: Add new models by creating a single file
3. **Consistency**: All models follow the same interface
4. **Testing**: Individual model testing without affecting others
5. **Documentation**: Self-documenting with type hints and docstrings
6. **Backwards Compatibility**: Legacy wrapper preserves existing usage

---

*Created for AI Content Pipeline - Long-term maintainable architecture*
