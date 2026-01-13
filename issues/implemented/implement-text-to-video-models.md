# Implementation Plan: Add New Text-to-Video Models

## Implementation Status: COMPLETED

**Created:** 2026-01-13
**Implemented:** 2026-01-13
**Branch:** `feat/nano-banana-pro-edit`
**Tests:** 30 passing (19 text-to-video + 11 Wan image-to-video)
**Priority:** Long-term maintainability over short-term gains

---

## Overview

This document outlines the implementation of 4 new FAL AI video generation models:

| Model | Type | Endpoint | Pricing |
|-------|------|----------|---------|
| Kling v2.6 Pro | Text-to-Video | `fal-ai/kling-video/v2.6/pro/text-to-video` | $0.07/s (no audio), $0.14/s (with audio) |
| Wan v2.6 | Image-to-Video | `wan/v2.6/image-to-video` | $0.10/s (720p), $0.15/s (1080p) |
| Sora 2 | Text-to-Video | `fal-ai/sora-2/text-to-video` | $0.10/s |
| Sora 2 Pro | Text-to-Video | `fal-ai/sora-2/text-to-video/pro` | $0.30/s (720p), $0.50/s (1080p) |

---

## Architecture Decision

### Current State
- Text-to-Video: Single-file generator (`fal_text_to_video_generator.py`) with enum-based model selection
- Image-to-Video: Class-based architecture with separate model files, constants, and generator

### Recommended Approach
**Refactor Text-to-Video to match Image-to-Video architecture** for:
- Better maintainability (each model in its own file)
- Easier testing (isolated model logic)
- Consistent patterns across the codebase
- Simpler addition of future models

---

## API Specifications

### 1. Kling v2.6 Pro Text-to-Video

**Endpoint:** `fal-ai/kling-video/v2.6/pro/text-to-video`

| Parameter | Type | Default | Valid Values | Required |
|-----------|------|---------|--------------|----------|
| `prompt` | string | - | Any text | Yes |
| `duration` | enum | `"5"` | `"5"`, `"10"` | No |
| `aspect_ratio` | enum | `"16:9"` | `"16:9"`, `"9:16"`, `"1:1"` | No |
| `negative_prompt` | string | `"blur, distort, and low quality"` | Any text | No |
| `cfg_scale` | float | `0.5` | `0.0` - `1.0` | No |
| `generate_audio` | boolean | `true` | `true`, `false` | No |

**Output:** `{ video: { url, file_size, file_name, content_type } }`

---

### 2. Wan v2.6 Image-to-Video

**Endpoint:** `wan/v2.6/image-to-video`

| Parameter | Type | Default | Valid Values | Required |
|-----------|------|---------|--------------|----------|
| `prompt` | string | - | Max 800 chars | Yes |
| `image_url` | string | - | Image URL (360-2000px, max 25MB) | Yes |
| `resolution` | enum | `"1080p"` | `"720p"`, `"1080p"` | No |
| `duration` | enum | `"5"` | `"5"`, `"10"`, `"15"` | No |
| `negative_prompt` | string | `""` | Max 500 chars | No |
| `enable_prompt_expansion` | boolean | `true` | `true`, `false` | No |
| `multi_shots` | boolean | `false` | `true`, `false` | No |
| `seed` | integer | None | Any integer | No |
| `enable_safety_checker` | boolean | `true` | `true`, `false` | No |
| `audio_url` | string | None | WAV/MP3 (3-30s, max 15MB) | No |

**Output:** `{ video: { url, ... }, seed, actual_prompt }`

**Pricing:**
- 720p: $0.10/second
- 1080p: $0.15/second

---

### 3. Sora 2 Text-to-Video

**Endpoint:** `fal-ai/sora-2/text-to-video`

| Parameter | Type | Default | Valid Values | Required |
|-----------|------|---------|--------------|----------|
| `prompt` | string | - | 1-5000 chars | Yes |
| `resolution` | enum | `"720p"` | `"720p"` | No |
| `aspect_ratio` | enum | `"16:9"` | `"9:16"`, `"16:9"` | No |
| `duration` | integer | `4` | `4`, `8`, `12` | No |
| `delete_video` | boolean | `true` | `true`, `false` | No |

**Output:** `{ video: { url, ... }, video_id, thumbnail?, spritesheet? }`

**Pricing:** $0.10/second

---

### 4. Sora 2 Pro Text-to-Video

**Endpoint:** `fal-ai/sora-2/text-to-video/pro`

| Parameter | Type | Default | Valid Values | Required |
|-----------|------|---------|--------------|----------|
| `prompt` | string | - | 1-5000 chars | Yes |
| `resolution` | enum | `"1080p"` | `"720p"`, `"1080p"` | No |
| `aspect_ratio` | enum | `"16:9"` | `"9:16"`, `"16:9"` | No |
| `duration` | integer | `4` | `4`, `8`, `12` | No |
| `delete_video` | boolean | `true` | `true`, `false` | No |

**Output:** `{ video: { url, ... }, video_id, thumbnail?, spritesheet? }`

**Pricing:** $0.30/s (720p), $0.50/s (1080p)

---

## Implementation Tasks

### Task 1: Refactor Text-to-Video to Class-Based Architecture

#### Task 1.1: Create Directory Structure

**Action:** Create new directories

```bash
mkdir -p packages/providers/fal/text-to-video/fal_text_to_video/models
mkdir -p packages/providers/fal/text-to-video/fal_text_to_video/config
mkdir -p packages/providers/fal/text-to-video/fal_text_to_video/utils
mkdir -p packages/providers/fal/text-to-video/tests
```

---

#### Task 1.2: Create Constants File

**File:** `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py`

**Action:** Create new file

```python
"""
Constants and configuration for FAL Text-to-Video models.
"""

from typing import Literal, List

# Model type definitions
ModelType = Literal[
    "hailuo_pro",
    "veo3",
    "veo3_fast",
    "kling_2_6_pro",
    "sora_2",
    "sora_2_pro"
]

SUPPORTED_MODELS: List[str] = [
    "hailuo_pro",
    "veo3",
    "veo3_fast",
    "kling_2_6_pro",
    "sora_2",
    "sora_2_pro"
]

# Model endpoints
MODEL_ENDPOINTS = {
    "hailuo_pro": "fal-ai/minimax/hailuo-02/pro/text-to-video",
    "veo3": "fal-ai/veo3",
    "veo3_fast": "fal-ai/veo3/fast",
    "kling_2_6_pro": "fal-ai/kling-video/v2.6/pro/text-to-video",
    "sora_2": "fal-ai/sora-2/text-to-video",
    "sora_2_pro": "fal-ai/sora-2/text-to-video/pro"
}

# Display names
MODEL_DISPLAY_NAMES = {
    "hailuo_pro": "MiniMax Hailuo-02 Pro",
    "veo3": "Google Veo 3",
    "veo3_fast": "Google Veo 3 Fast",
    "kling_2_6_pro": "Kling Video v2.6 Pro",
    "sora_2": "Sora 2",
    "sora_2_pro": "Sora 2 Pro"
}

# Pricing (USD)
MODEL_PRICING = {
    "hailuo_pro": {
        "type": "per_video",
        "cost": 0.08
    },
    "veo3": {
        "type": "per_second",
        "cost_no_audio": 0.50,
        "cost_with_audio": 0.75
    },
    "veo3_fast": {
        "type": "per_second",
        "cost_no_audio": 0.25,
        "cost_with_audio": 0.40
    },
    "kling_2_6_pro": {
        "type": "per_second",
        "cost_no_audio": 0.07,
        "cost_with_audio": 0.14
    },
    "sora_2": {
        "type": "per_second",
        "cost": 0.10
    },
    "sora_2_pro": {
        "type": "per_second",
        "cost_720p": 0.30,
        "cost_1080p": 0.50
    }
}

# Duration options per model
DURATION_OPTIONS = {
    "hailuo_pro": ["6"],  # Fixed 6 seconds
    "veo3": ["5s", "6s", "7s", "8s"],
    "veo3_fast": ["5s", "6s", "7s", "8s"],
    "kling_2_6_pro": ["5", "10"],
    "sora_2": [4, 8, 12],
    "sora_2_pro": [4, 8, 12]
}

# Resolution options per model
RESOLUTION_OPTIONS = {
    "hailuo_pro": ["1080p"],
    "veo3": ["720p"],
    "veo3_fast": ["720p"],
    "kling_2_6_pro": ["720p"],  # Text-to-video only supports 720p
    "sora_2": ["720p"],
    "sora_2_pro": ["720p", "1080p"]
}

# Aspect ratio options
ASPECT_RATIO_OPTIONS = {
    "hailuo_pro": ["16:9"],  # Fixed
    "veo3": ["16:9", "9:16", "1:1"],
    "veo3_fast": ["16:9", "9:16", "1:1"],
    "kling_2_6_pro": ["16:9", "9:16", "1:1"],
    "sora_2": ["16:9", "9:16"],
    "sora_2_pro": ["16:9", "9:16"]
}

# Default values per model
DEFAULT_VALUES = {
    "hailuo_pro": {
        "prompt_optimizer": True
    },
    "veo3": {
        "duration": "8s",
        "aspect_ratio": "16:9",
        "generate_audio": True,
        "enhance_prompt": True
    },
    "veo3_fast": {
        "duration": "8s",
        "aspect_ratio": "16:9",
        "generate_audio": True
    },
    "kling_2_6_pro": {
        "duration": "5",
        "aspect_ratio": "16:9",
        "negative_prompt": "blur, distort, and low quality",
        "cfg_scale": 0.5,
        "generate_audio": True
    },
    "sora_2": {
        "duration": 4,
        "resolution": "720p",
        "aspect_ratio": "16:9",
        "delete_video": True
    },
    "sora_2_pro": {
        "duration": 4,
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "delete_video": True
    }
}

# Model info for documentation
MODEL_INFO = {
    "hailuo_pro": {
        "name": "MiniMax Hailuo-02 Pro",
        "provider": "MiniMax",
        "description": "Cost-effective text-to-video with prompt optimization",
        "max_duration": 6,
        "features": ["prompt_optimizer", "1080p", "cost_effective"]
    },
    "veo3": {
        "name": "Google Veo 3",
        "provider": "Google (via FAL)",
        "description": "Premium quality with audio generation",
        "max_duration": 8,
        "features": ["audio_generation", "enhance_prompt", "negative_prompt", "seed_control"]
    },
    "veo3_fast": {
        "name": "Google Veo 3 Fast",
        "provider": "Google (via FAL)",
        "description": "Fast generation with good quality",
        "max_duration": 8,
        "features": ["audio_generation", "fast_processing", "seed_control"]
    },
    "kling_2_6_pro": {
        "name": "Kling Video v2.6 Pro",
        "provider": "Kuaishou",
        "description": "Professional text-to-video with audio support",
        "max_duration": 10,
        "features": ["audio_generation", "negative_prompt", "cfg_scale", "multilingual"]
    },
    "sora_2": {
        "name": "Sora 2",
        "provider": "OpenAI (via FAL)",
        "description": "OpenAI's text-to-video model",
        "max_duration": 12,
        "features": ["aspect_ratio", "long_duration"]
    },
    "sora_2_pro": {
        "name": "Sora 2 Pro",
        "provider": "OpenAI (via FAL)",
        "description": "Professional Sora with 1080p support",
        "max_duration": 12,
        "features": ["aspect_ratio", "1080p", "long_duration"]
    }
}
```

---

#### Task 1.3: Create Base Model Class

**File:** `packages/providers/fal/text-to-video/fal_text_to_video/models/base.py`

**Action:** Create new file

```python
"""
Base class for text-to-video models.
"""

import os
import time
import requests
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import fal_client
except ImportError:
    raise ImportError("fal-client not installed. Run: pip install fal-client")

from ..config.constants import MODEL_ENDPOINTS, MODEL_PRICING, MODEL_DISPLAY_NAMES


class BaseTextToVideoModel(ABC):
    """
    Abstract base class for text-to-video models.

    All model implementations must inherit from this class and implement
    the abstract methods.
    """

    def __init__(self, model_key: str):
        """
        Initialize the model.

        Args:
            model_key: Model identifier (e.g., "sora_2", "kling_2_6_pro")
        """
        self.model_key = model_key
        self.endpoint = MODEL_ENDPOINTS.get(model_key)
        self.display_name = MODEL_DISPLAY_NAMES.get(model_key, model_key)
        self.pricing = MODEL_PRICING.get(model_key, {})

        if not self.endpoint:
            raise ValueError(f"Unknown model: {model_key}")

    @abstractmethod
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate and normalize input parameters.

        Args:
            **kwargs: Model-specific parameters

        Returns:
            Dict with validated parameters

        Raises:
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare arguments for the FAL API call.

        Args:
            prompt: Text description for video generation
            **kwargs: Additional model-specific parameters

        Returns:
            Dict of arguments for fal_client.subscribe()
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and capabilities."""
        pass

    @abstractmethod
    def estimate_cost(self, **kwargs) -> float:
        """
        Estimate cost for generation.

        Args:
            **kwargs: Parameters that affect cost (duration, resolution, etc.)

        Returns:
            Estimated cost in USD
        """
        pass

    def generate(
        self,
        prompt: str,
        output_dir: Optional[Path] = None,
        timeout: int = 600,
        verbose: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt.

        Args:
            prompt: Text description for video generation
            output_dir: Directory to save output (default: ./output)
            timeout: Maximum wait time in seconds
            verbose: Enable verbose output
            **kwargs: Model-specific parameters

        Returns:
            Dict with generation results
        """
        output_dir = output_dir or Path("output")
        output_dir.mkdir(exist_ok=True)

        # Validate parameters
        validated_params = self.validate_parameters(**kwargs)

        # Estimate cost
        cost = self.estimate_cost(**validated_params)

        if verbose:
            print(f"Generating video with {self.display_name}...")
            print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            print(f"Estimated cost: ${cost:.2f}")

        try:
            # Prepare API arguments
            arguments = self.prepare_arguments(prompt, **validated_params)

            if verbose:
                print("Submitting generation request...")

            # Call FAL API
            result = fal_client.subscribe(
                self.endpoint,
                arguments=arguments,
                with_logs=verbose,
                timeout=timeout
            )

            if verbose:
                print("Video generation completed!")

            # Extract video URL
            video_url = result.get('video', {}).get('url')
            if not video_url:
                raise Exception("No video URL in response")

            # Generate filename
            timestamp = int(time.time())
            safe_prompt = "".join(
                c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')
            ).rstrip().replace(' ', '_')
            filename = f"{self.model_key}_{safe_prompt}_{timestamp}.mp4"

            # Download video
            local_path = self._download_video(video_url, output_dir / filename, verbose)

            return {
                "success": True,
                "video_url": video_url,
                "local_path": str(local_path),
                "filename": filename,
                "prompt": prompt,
                "model": self.model_key,
                "model_name": self.display_name,
                "cost_usd": cost,
                "parameters": validated_params,
                "metadata": result
            }

        except Exception as e:
            if verbose:
                print(f"Generation failed: {e}")

            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
                "model": self.model_key,
                "estimated_cost": cost
            }

    def _download_video(
        self,
        url: str,
        local_path: Path,
        verbose: bool = True
    ) -> Path:
        """Download video from URL to local file."""
        if verbose:
            print(f"Downloading video: {local_path.name}")

        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if verbose and total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rDownloading: {progress:.1f}%", end='', flush=True)

        if verbose and total_size > 0:
            print()  # New line after progress
            print(f"Download completed: {local_path}")

        return local_path
```

---

#### Task 1.4: Create Kling v2.6 Pro Model

**File:** `packages/providers/fal/text-to-video/fal_text_to_video/models/kling.py`

**Action:** Create new file

```python
"""
Kling Video v2.6 Pro text-to-video model implementation.
"""

from typing import Dict, Any
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

    def __init__(self):
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
        cost_per_second = 0.14 if generate_audio else 0.07
        return cost_per_second * duration_seconds
```

---

#### Task 1.5: Create Sora 2 Models

**File:** `packages/providers/fal/text-to-video/fal_text_to_video/models/sora.py`

**Action:** Create new file

```python
"""
Sora 2 and Sora 2 Pro text-to-video model implementations.
"""

from typing import Dict, Any
from .base import BaseTextToVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS, ASPECT_RATIO_OPTIONS
)


class Sora2Model(BaseTextToVideoModel):
    """
    Sora 2 for text-to-video generation.

    API Parameters:
        - prompt: Text description (1-5000 chars)
        - resolution: "720p"
        - aspect_ratio: "9:16", "16:9"
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
        resolution = kwargs.get("resolution", defaults.get("resolution", "720p"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        delete_video = kwargs.get("delete_video", defaults.get("delete_video", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("sora_2", [4, 8, 12])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("sora_2", ["720p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("sora_2", ["9:16", "16:9"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "delete_video": bool(delete_video)
        }

    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Sora 2."""
        return {
            "prompt": prompt,
            "duration": kwargs.get("duration", 4),
            "resolution": kwargs.get("resolution", "720p"),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "delete_video": kwargs.get("delete_video", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Sora 2 model information."""
        return {
            **MODEL_INFO.get("sora_2", {}),
            "endpoint": self.endpoint,
            "pricing": self.pricing
        }

    def estimate_cost(self, duration: int = 4, **kwargs) -> float:
        """Estimate cost based on duration."""
        return 0.10 * duration


class Sora2ProModel(BaseTextToVideoModel):
    """
    Sora 2 Pro for professional text-to-video generation.

    API Parameters:
        - prompt: Text description (1-5000 chars)
        - resolution: "720p", "1080p"
        - aspect_ratio: "9:16", "16:9"
        - duration: 4, 8, 12 seconds
        - delete_video: Auto-delete for privacy

    Pricing: $0.30/s (720p), $0.50/s (1080p)
    """

    def __init__(self):
        super().__init__("sora_2_pro")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Sora 2 Pro parameters."""
        defaults = DEFAULT_VALUES.get("sora_2_pro", {})

        duration = kwargs.get("duration", defaults.get("duration", 4))
        resolution = kwargs.get("resolution", defaults.get("resolution", "1080p"))
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9"))
        delete_video = kwargs.get("delete_video", defaults.get("delete_video", True))

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("sora_2_pro", [4, 8, 12])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("sora_2_pro", ["720p", "1080p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate aspect ratio
        valid_ratios = ASPECT_RATIO_OPTIONS.get("sora_2_pro", ["9:16", "16:9"])
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

        return {
            "duration": duration,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "delete_video": bool(delete_video)
        }

    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Prepare API arguments for Sora 2 Pro."""
        return {
            "prompt": prompt,
            "duration": kwargs.get("duration", 4),
            "resolution": kwargs.get("resolution", "1080p"),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "delete_video": kwargs.get("delete_video", True)
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get Sora 2 Pro model information."""
        return {
            **MODEL_INFO.get("sora_2_pro", {}),
            "endpoint": self.endpoint,
            "pricing": self.pricing
        }

    def estimate_cost(self, duration: int = 4, resolution: str = "1080p", **kwargs) -> float:
        """Estimate cost based on duration and resolution."""
        if resolution == "1080p":
            return 0.50 * duration
        return 0.30 * duration
```

---

### Task 2: Add Wan v2.6 to Image-to-Video

#### Task 2.1: Update Image-to-Video Constants

**File:** `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`

**Action:** Modify existing file

**Add to `ModelType` (line 8):**
```python
ModelType = Literal[
    "hailuo",
    "kling_2_1",
    "kling_2_6_pro",
    "seedance_1_5_pro",
    "sora_2",
    "sora_2_pro",
    "veo_3_1_fast",
    "wan_2_6"  # ADD THIS
]
```

**Add to `SUPPORTED_MODELS` (line 18):**
```python
SUPPORTED_MODELS: List[str] = [
    "hailuo",
    "kling_2_1",
    "kling_2_6_pro",
    "seedance_1_5_pro",
    "sora_2",
    "sora_2_pro",
    "veo_3_1_fast",
    "wan_2_6"  # ADD THIS
]
```

**Add to `MODEL_ENDPOINTS` (after line 36):**
```python
    "wan_2_6": "wan/v2.6/image-to-video"
```

**Add to `MODEL_DISPLAY_NAMES` (after line 47):**
```python
    "wan_2_6": "Wan v2.6"
```

**Add to `MODEL_PRICING` (after line 58):**
```python
    "wan_2_6": 0.10  # Base price, 1080p is 0.15
```

**Add to `DURATION_OPTIONS` (after line 69):**
```python
    "wan_2_6": ["5", "10", "15"]
```

**Add to `RESOLUTION_OPTIONS` (after line 80):**
```python
    "wan_2_6": ["720p", "1080p"]
```

**Add to `ASPECT_RATIO_OPTIONS` (after line 87):**
```python
    "wan_2_6": ["16:9", "9:16", "1:1"]
```

**Add to `DEFAULT_VALUES` (after line 128):**
```python
    "wan_2_6": {
        "duration": "5",
        "resolution": "1080p",
        "negative_prompt": "",
        "enable_prompt_expansion": True,
        "multi_shots": False,
        "seed": None,
        "enable_safety_checker": True
    }
```

**Add to `MODEL_INFO` (after line 188):**
```python
    "wan_2_6": {
        "name": "Wan v2.6",
        "provider": "Wan",
        "description": "High-quality image-to-video with multi-shot support",
        "max_duration": 15,
        "features": ["prompt_expansion", "multi_shots", "audio_input", "seed_control", "safety_checker"],
        "extended_params": ["start_frame", "audio_input"]
    }
```

**Add to `MODEL_EXTENDED_FEATURES` (after line 249):**
```python
    "wan_2_6": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio_input": True,  # Supports audio_url
        "audio_generate": False,
        "ref_video": False,
    }
```

---

#### Task 2.2: Create Wan Model Class

**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/wan.py`

**Action:** Create new file

```python
"""
Wan v2.6 image-to-video model implementation.
"""

from typing import Dict, Any, Optional
from .base import BaseVideoModel
from ..config.constants import (
    MODEL_INFO, DEFAULT_VALUES,
    DURATION_OPTIONS, RESOLUTION_OPTIONS
)


class Wan26Model(BaseVideoModel):
    """
    Wan v2.6 for image-to-video generation.

    API Parameters:
        - prompt: Text description (max 800 chars)
        - image_url: Input image URL
        - resolution: "720p", "1080p"
        - duration: "5", "10", "15" seconds
        - negative_prompt: Elements to avoid (max 500 chars)
        - enable_prompt_expansion: Expand prompt for better results
        - multi_shots: Enable multi-shot generation
        - seed: Random seed for reproducibility
        - enable_safety_checker: Content safety filtering
        - audio_url: Optional audio input (WAV/MP3, 3-30s)

    Pricing: $0.10/s (720p), $0.15/s (1080p)
    """

    def __init__(self):
        super().__init__("wan_2_6")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate Wan v2.6 parameters."""
        defaults = DEFAULT_VALUES.get("wan_2_6", {})

        duration = kwargs.get("duration", defaults.get("duration", "5"))
        resolution = kwargs.get("resolution", defaults.get("resolution", "1080p"))
        negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", ""))
        enable_prompt_expansion = kwargs.get(
            "enable_prompt_expansion",
            defaults.get("enable_prompt_expansion", True)
        )
        multi_shots = kwargs.get("multi_shots", defaults.get("multi_shots", False))
        seed = kwargs.get("seed", defaults.get("seed"))
        enable_safety_checker = kwargs.get(
            "enable_safety_checker",
            defaults.get("enable_safety_checker", True)
        )
        audio_url = kwargs.get("audio_url")

        # Validate duration
        valid_durations = DURATION_OPTIONS.get("wan_2_6", ["5", "10", "15"])
        if duration not in valid_durations:
            raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

        # Validate resolution
        valid_resolutions = RESOLUTION_OPTIONS.get("wan_2_6", ["720p", "1080p"])
        if resolution not in valid_resolutions:
            raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

        # Validate prompt lengths
        if negative_prompt and len(negative_prompt) > 500:
            raise ValueError("negative_prompt must be max 500 characters")

        return {
            "duration": duration,
            "resolution": resolution,
            "negative_prompt": negative_prompt,
            "enable_prompt_expansion": bool(enable_prompt_expansion),
            "multi_shots": bool(multi_shots),
            "seed": seed,
            "enable_safety_checker": bool(enable_safety_checker),
            "audio_url": audio_url
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare API arguments for Wan v2.6."""
        # Validate prompt length
        if len(prompt) > 800:
            raise ValueError("prompt must be max 800 characters")

        args = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": kwargs.get("duration", "5"),
            "resolution": kwargs.get("resolution", "1080p"),
            "enable_prompt_expansion": kwargs.get("enable_prompt_expansion", True),
            "multi_shots": kwargs.get("multi_shots", False),
            "enable_safety_checker": kwargs.get("enable_safety_checker", True)
        }

        # Add optional parameters
        negative_prompt = kwargs.get("negative_prompt")
        if negative_prompt:
            args["negative_prompt"] = negative_prompt

        seed = kwargs.get("seed")
        if seed is not None:
            args["seed"] = seed

        audio_url = kwargs.get("audio_url")
        if audio_url:
            args["audio_url"] = audio_url

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Wan v2.6 model information."""
        return {
            **MODEL_INFO.get("wan_2_6", {}),
            "endpoint": self.endpoint,
            "price_per_second": self.price_per_second
        }

    def estimate_cost(
        self,
        duration: str = "5",
        resolution: str = "1080p",
        **kwargs
    ) -> float:
        """Estimate cost based on duration and resolution."""
        duration_seconds = int(duration)
        if resolution == "1080p":
            return 0.15 * duration_seconds
        return 0.10 * duration_seconds
```

---

#### Task 2.3: Update Image-to-Video Models __init__.py

**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/__init__.py`

**Action:** Modify existing file

**Add import and export:**
```python
from .wan import Wan26Model

__all__ = [
    # ... existing exports ...
    "Wan26Model"
]
```

---

#### Task 2.4: Update Image-to-Video Generator

**File:** `packages/providers/fal/image-to-video/fal_image_to_video/generator.py`

**Action:** Modify existing file

**Add import (around line 20):**
```python
from .models.wan import Wan26Model
```

**Add to models dict in `__init__` (around line 82):**
```python
            "wan_2_6": Wan26Model()
```

---

### Task 3: Create Tests

#### Task 3.1: Text-to-Video Model Tests

**File:** `packages/providers/fal/text-to-video/tests/test_text_to_video_models.py`

**Action:** Create new file

```python
"""
Tests for text-to-video model implementations.
"""

import pytest
from fal_text_to_video.models.kling import Kling26ProModel
from fal_text_to_video.models.sora import Sora2Model, Sora2ProModel
from fal_text_to_video.config.constants import (
    SUPPORTED_MODELS, MODEL_ENDPOINTS, MODEL_PRICING
)


class TestKling26ProModel:
    """Tests for Kling v2.6 Pro model."""

    def test_init(self):
        """Test model initialization."""
        model = Kling26ProModel()
        assert model.model_key == "kling_2_6_pro"
        assert model.endpoint == "fal-ai/kling-video/v2.6/pro/text-to-video"

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = Kling26ProModel()
        params = model.validate_parameters()

        assert params["duration"] == "5"
        assert params["aspect_ratio"] == "16:9"
        assert params["cfg_scale"] == 0.5
        assert params["generate_audio"] is True

    def test_validate_parameters_custom(self):
        """Test parameter validation with custom values."""
        model = Kling26ProModel()
        params = model.validate_parameters(
            duration="10",
            aspect_ratio="9:16",
            cfg_scale=0.7,
            generate_audio=False
        )

        assert params["duration"] == "10"
        assert params["aspect_ratio"] == "9:16"
        assert params["cfg_scale"] == 0.7
        assert params["generate_audio"] is False

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = Kling26ProModel()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration="15")

    def test_validate_parameters_invalid_cfg_scale(self):
        """Test validation fails for invalid cfg_scale."""
        model = Kling26ProModel()
        with pytest.raises(ValueError, match="cfg_scale must be"):
            model.validate_parameters(cfg_scale=1.5)

    def test_estimate_cost(self):
        """Test cost estimation."""
        model = Kling26ProModel()
        # With audio (default)
        assert model.estimate_cost(duration="5", generate_audio=True) == 0.70
        assert model.estimate_cost(duration="10", generate_audio=True) == 1.40
        # Without audio
        assert model.estimate_cost(duration="5", generate_audio=False) == 0.35
        assert model.estimate_cost(duration="10", generate_audio=False) == 0.70


class TestSora2Model:
    """Tests for Sora 2 model."""

    def test_init(self):
        """Test model initialization."""
        model = Sora2Model()
        assert model.model_key == "sora_2"
        assert model.endpoint == "fal-ai/sora-2/text-to-video"

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = Sora2Model()
        params = model.validate_parameters()

        assert params["duration"] == 4
        assert params["resolution"] == "720p"
        assert params["aspect_ratio"] == "16:9"

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = Sora2Model()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration=6)

    def test_estimate_cost(self):
        """Test cost estimation."""
        model = Sora2Model()
        assert model.estimate_cost(duration=4) == 0.40
        assert model.estimate_cost(duration=12) == 1.20


class TestSora2ProModel:
    """Tests for Sora 2 Pro model."""

    def test_init(self):
        """Test model initialization."""
        model = Sora2ProModel()
        assert model.model_key == "sora_2_pro"

    def test_validate_parameters_1080p(self):
        """Test 1080p resolution validation."""
        model = Sora2ProModel()
        params = model.validate_parameters(resolution="1080p")
        assert params["resolution"] == "1080p"

    def test_estimate_cost_resolution_pricing(self):
        """Test resolution-based pricing."""
        model = Sora2ProModel()
        # 720p pricing
        assert model.estimate_cost(duration=4, resolution="720p") == 1.20
        # 1080p pricing
        assert model.estimate_cost(duration=4, resolution="1080p") == 2.00


class TestConstants:
    """Tests for constants configuration."""

    def test_all_models_have_endpoints(self):
        """Verify all supported models have endpoints."""
        for model in SUPPORTED_MODELS:
            assert model in MODEL_ENDPOINTS, f"Missing endpoint for {model}"

    def test_all_models_have_pricing(self):
        """Verify all supported models have pricing."""
        for model in SUPPORTED_MODELS:
            assert model in MODEL_PRICING, f"Missing pricing for {model}"
```

---

#### Task 3.2: Wan v2.6 Tests

**File:** `packages/providers/fal/image-to-video/tests/test_wan_model.py`

**Action:** Create new file

```python
"""
Tests for Wan v2.6 image-to-video model.
"""

import pytest
from fal_image_to_video.models.wan import Wan26Model


class TestWan26Model:
    """Tests for Wan v2.6 model."""

    def test_init(self):
        """Test model initialization."""
        model = Wan26Model()
        assert model.model_key == "wan_2_6"
        assert model.endpoint == "wan/v2.6/image-to-video"

    def test_validate_parameters_defaults(self):
        """Test parameter validation with defaults."""
        model = Wan26Model()
        params = model.validate_parameters()

        assert params["duration"] == "5"
        assert params["resolution"] == "1080p"
        assert params["enable_prompt_expansion"] is True
        assert params["multi_shots"] is False

    def test_validate_parameters_custom(self):
        """Test parameter validation with custom values."""
        model = Wan26Model()
        params = model.validate_parameters(
            duration="15",
            resolution="720p",
            multi_shots=True,
            seed=42
        )

        assert params["duration"] == "15"
        assert params["resolution"] == "720p"
        assert params["multi_shots"] is True
        assert params["seed"] == 42

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""
        model = Wan26Model()
        with pytest.raises(ValueError, match="Invalid duration"):
            model.validate_parameters(duration="20")

    def test_validate_parameters_long_negative_prompt(self):
        """Test validation fails for too long negative prompt."""
        model = Wan26Model()
        with pytest.raises(ValueError, match="max 500 characters"):
            model.validate_parameters(negative_prompt="x" * 501)

    def test_prepare_arguments_prompt_length(self):
        """Test prompt length validation."""
        model = Wan26Model()
        with pytest.raises(ValueError, match="max 800 characters"):
            model.prepare_arguments(
                prompt="x" * 801,
                image_url="https://example.com/image.jpg"
            )

    def test_estimate_cost_720p(self):
        """Test 720p cost estimation."""
        model = Wan26Model()
        assert model.estimate_cost(duration="5", resolution="720p") == 0.50
        assert model.estimate_cost(duration="15", resolution="720p") == 1.50

    def test_estimate_cost_1080p(self):
        """Test 1080p cost estimation."""
        model = Wan26Model()
        assert model.estimate_cost(duration="5", resolution="1080p") == 0.75
        assert model.estimate_cost(duration="15", resolution="1080p") == 2.25

    def test_prepare_arguments_with_audio(self):
        """Test arguments preparation with audio URL."""
        model = Wan26Model()
        args = model.prepare_arguments(
            prompt="Test prompt",
            image_url="https://example.com/image.jpg",
            audio_url="https://example.com/audio.mp3"
        )

        assert args["audio_url"] == "https://example.com/audio.mp3"
```

---

## File Summary

### Files to Create

| File Path | Description |
|-----------|-------------|
| `packages/providers/fal/text-to-video/fal_text_to_video/config/__init__.py` | Config package init |
| `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py` | Text-to-video constants |
| `packages/providers/fal/text-to-video/fal_text_to_video/models/__init__.py` | Models package init |
| `packages/providers/fal/text-to-video/fal_text_to_video/models/base.py` | Base model class |
| `packages/providers/fal/text-to-video/fal_text_to_video/models/kling.py` | Kling v2.6 Pro model |
| `packages/providers/fal/text-to-video/fal_text_to_video/models/sora.py` | Sora 2 models |
| `packages/providers/fal/text-to-video/fal_text_to_video/utils/__init__.py` | Utils package init |
| `packages/providers/fal/image-to-video/fal_image_to_video/models/wan.py` | Wan v2.6 model |
| `packages/providers/fal/text-to-video/tests/test_text_to_video_models.py` | Text-to-video tests |
| `packages/providers/fal/image-to-video/tests/test_wan_model.py` | Wan model tests |

### Files to Modify

| File Path | Changes |
|-----------|---------|
| `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py` | Add Wan v2.6 config |
| `packages/providers/fal/image-to-video/fal_image_to_video/models/__init__.py` | Export Wan26Model |
| `packages/providers/fal/image-to-video/fal_image_to_video/generator.py` | Add Wan v2.6 to models dict |

### Files to Keep (No Changes)

| File Path | Reason |
|-----------|--------|
| `packages/providers/fal/text-to-video/fal_text_to_video_generator.py` | Keep for backward compatibility |

---

## Implementation Order

1. **Phase 1: Text-to-Video Refactoring**
   - Create directory structure
   - Create constants file
   - Create base model class
   - Create Kling v2.6 Pro model
   - Create Sora 2 models
   - Create tests

2. **Phase 2: Wan v2.6 Integration**
   - Update image-to-video constants
   - Create Wan model class
   - Update generator
   - Create tests

3. **Phase 3: Integration & Testing**
   - Run all tests
   - Update CLI if needed
   - Update documentation

---

## Estimated Effort

| Task | Complexity | Files |
|------|------------|-------|
| Task 1: Refactor Text-to-Video | High | 8 new files |
| Task 2: Add Wan v2.6 | Medium | 1 new file, 3 modified |
| Task 3: Tests | Medium | 2 new files |

**Total:** ~11 new files, ~3 modified files
