# FAL Avatar & Video Generation Support Implementation

**Created:** 2026-01-13
**Completed:** 2026-01-13
**Branch:** `avatar`
**Status:** ✅ Implemented
**Estimated Effort:** 5-7 hours (split into subtasks)

---

## Implementation Summary

All subtasks have been completed:

| Subtask | Status | Files Created/Modified |
|---------|--------|------------------------|
| 1. Base Model Infrastructure | ✅ Done | `fal_avatar/models/base.py`, `fal_avatar/config/constants.py` |
| 2. Individual Model Classes | ✅ Done | `omnihuman.py`, `fabric.py`, `kling.py` |
| 3. Unified Generator | ✅ Done | `fal_avatar/generator.py` |
| 4. Core Pipeline Integration | ✅ Done | `constants.py` (core) |
| 5. CLI Commands | ✅ Done | `__main__.py` |
| 6. YAML Pipeline Support | ✅ Done | Via pipeline manager |
| 7. Unit Tests | ✅ Done | `tests/test_fal_avatar.py` |

### CLI Commands Added

```bash
# Generate lipsync avatar (image + audio)
ai-content-pipeline generate-avatar --image-url "https://..." --audio-url "https://..."

# Generate TTS avatar (image + text)
ai-content-pipeline generate-avatar --image-url "https://..." --text "Hello world!"

# Generate video with reference images
ai-content-pipeline generate-avatar --reference-images img1.jpg img2.jpg --prompt "A person walking"

# Transform existing video
ai-content-pipeline generate-avatar --video-url "https://..." --prompt "cinematic style"

# List all avatar models
ai-content-pipeline list-avatar-models
```

### Package Structure Created

```
packages/providers/fal/avatar-generation/
└── fal_avatar/
    ├── __init__.py
    ├── generator.py
    ├── config/
    │   ├── __init__.py
    │   └── constants.py
    ├── models/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── omnihuman.py
    │   ├── fabric.py
    │   └── kling.py
    └── utils/
        ├── __init__.py
        └── validators.py
```

---

## Overview

Add comprehensive FAL avatar and video generation model support to the AI Content Pipeline, including:
- **OmniHuman v1.5** - Audio-driven human animation (image + audio → video)
- **VEED Fabric 1.0** - Lipsync video generation (image + audio → video)
- **VEED Fabric 1.0 Text** - Text-to-speech avatar videos (image + text → video)
- **Kling O1 Reference-to-Video** - Reference image consistency (images + prompt → video)
- **Kling O1 Video-to-Video Reference** - Style-guided video generation (video + prompt → video)
- **Kling O1 Video-to-Video Edit** - Targeted video modifications (video + prompt → video)

---

## Model Categories

### Category A: Avatar/Lipsync Models (Image + Audio/Text → Video)
- OmniHuman v1.5
- VEED Fabric 1.0
- VEED Fabric 1.0 Text

### Category B: Reference-Based Video Generation (Images → Video)
- Kling O1 Reference-to-Video

### Category C: Video-to-Video Transformation (Video → Video)
- Kling O1 V2V Reference
- Kling O1 V2V Edit

---

## API Specifications

### 1. OmniHuman v1.5 (`fal-ai/bytedance/omnihuman/v1.5`)

**Description:** ByteDance's audio-driven human animation model. Generates realistic videos where character emotions and movements correlate with audio input.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_url` | string | Yes | - | Human figure image URL (portrait/full body) |
| `audio_url` | string | Yes | - | Audio file URL (max 30s @1080p, 60s @720p) |
| `prompt` | string | No | - | Text guidance for generation style |
| `turbo_mode` | boolean | No | false | Faster generation with slight quality trade-off |
| `resolution` | enum | No | "1080p" | Output resolution: "720p" or "1080p" |

**Pricing:** $0.16/second of output video
**Max Duration:** 30 seconds (1080p), 60 seconds (720p)
**Output Schema:**
```json
{
  "video": { "url": "string" },
  "duration": "float (billing duration in seconds)"
}
```

**Best For:** Realistic talking head videos, presentation videos, avatar animations

---

### 2. VEED Fabric 1.0 (`veed/fabric-1.0`)

**Description:** VEED's lipsync model for creating talking videos from image and audio input.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_url` | string | Yes | - | Image source URL (face/portrait) |
| `audio_url` | string | Yes | - | Audio file URL for lipsync |
| `resolution` | enum | Yes | - | Output resolution: "720p" or "480p" |

**Pricing:**
- 480p: $0.08/second
- 720p: $0.15/second
- Fast variant (`veed/fabric-1.0/fast`): +25% cost

**Output Schema:**
```json
{
  "url": "string",
  "content_type": "video/mp4",
  "file_name": "string (optional)",
  "file_size": "integer (bytes, optional)"
}
```

**Best For:** Quick lipsync videos, social media content, multilingual dubbing

---

### 3. VEED Fabric 1.0 Text (`veed/fabric-1.0/text`)

**Description:** Text-to-speech avatar generation. Converts text to speech and animates the image to speak.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image_url` | string | Yes | - | Image source URL (face/portrait) |
| `text` | string | Yes | - | Speech text (max 2000 characters) |
| `resolution` | enum | Yes | - | Output resolution: "720p" or "480p" |
| `voice_description` | string | No | - | Voice characteristics (e.g., "British accent", "professional female") |

**Pricing:**
- 480p: $0.08/second
- 720p: $0.15/second

**Output Schema:**
```json
{
  "video": {
    "url": "string",
    "content_type": "video/mp4"
  }
}
```

**Best For:** Quick avatar videos from scripts, no pre-recorded audio needed

---

### 4. Kling O1 Reference-to-Video (`fal-ai/kling-video/o1/standard/reference-to-video`)

**Description:** Kuaishou's reference image consistency model. Upload up to 4 reference images defining people, objects, or settings, then generate videos with visual coherence across elements.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Video generation prompt (use @Element1, @Element2, etc.) |
| `reference_images` | array | Yes | - | List of reference image URLs (max 4 images) |
| `duration` | enum | No | "5" | Output duration: "5" or "10" seconds |
| `aspect_ratio` | enum | No | "16:9" | "16:9", "9:16", "1:1" |
| `audio_url` | string | No | - | Audio URL (.mp3/.wav/.m4a, max 5MB, 2-60s) |
| `sound_start_time` | int | No | - | Audio crop start time (ms) |
| `sound_end_time` | int | No | - | Audio crop end time (ms) |
| `sound_insert_time` | int | No | - | Insert audio at time (ms) |
| `face_id` | string | No | - | Face ID from identify_face API |

**Pricing:** $0.112/second
**Max Duration:** 10 seconds per generation
**Max References:** 4 images (up to 7 with advanced modes)

**Output Schema:**
```json
{
  "video": { "url": "string" },
  "duration": "float"
}
```

**Best For:** Character consistency across shots, product videos, branded content, recurring characters

**Example Prompt:**
```
"@Element1 walking through a forest, @Element2 visible in background, cinematic lighting"
```

---

### 5. Kling O1 Video-to-Video Reference (`fal-ai/kling-video/o1/standard/video-to-video/reference`)

**Description:** Style-guided video generation. Generate new shots guided by an input reference video, preserving motion and camera style.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Use `@Video1` to reference input video |
| `video_url` | string | Yes | - | Reference video URL |
| `duration` | enum | No | "5" | Output duration: "5" or "10" seconds |
| `aspect_ratio` | enum | No | "16:9" | "16:9", "9:16", "1:1" |
| `audio_url` | string | No | - | Audio URL (.mp3/.wav/.m4a, max 5MB) |
| `sound_start_time` | int | No | - | Audio start time (ms) |
| `sound_end_time` | int | No | - | Audio end time (ms) |
| `sound_insert_time` | int | No | - | Insert audio at time (ms) |
| `face_id` | string | No | - | Face ID from identify_face API |

**Pricing:** ~$0.10/second (estimated)
**Max Duration:** 10 seconds per generation

**Output Schema:**
```json
{
  "video": { "url": "string" },
  "duration": "float"
}
```

**Best For:** Scene continuity, style transfer, generating next shots in sequence

**Example Prompt:**
```
"Based on @Video1, generate the next shot. Keep the style of the video, add dramatic lighting"
```

---

### 6. Kling O1 Video-to-Video Edit (`fal-ai/kling-video/o1/standard/video-to-video/edit`)

**Description:** Targeted video modifications through natural language. Make specific edits without regenerating the entire video.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video_url` | string | Yes | - | Source video URL to edit |
| `prompt` | string | Yes | - | Edit instructions (specific changes) |
| `mask_url` | string | No | - | Optional mask image to define edit region |
| `duration` | enum | No | - | Matches source video |
| `aspect_ratio` | enum | No | - | Matches source video |

**Pricing:** ~$0.10/second (estimated)
**Max Duration:** 10 seconds per generation

**Output Schema:**
```json
{
  "video": { "url": "string" },
  "duration": "float"
}
```

**Best For:** Background changes, object removal, lighting adjustments, fixing specific elements

**Example Prompts:**
```
"Change the background to a beach scene"
"Remove the person in the background"
"Make the lighting more cinematic and warm"
```

---

## Implementation Subtasks

### Subtask 1: Create Base Model Infrastructure (1 hour)

**Goal:** Set up the package structure and base classes

**Files to Create:**
```
packages/providers/fal/avatar-generation/
├── fal_avatar/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── constants.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py
│   └── utils/
│       ├── __init__.py
│       └── validators.py
```

**File: `packages/providers/fal/avatar-generation/fal_avatar/models/base.py`**
```python
"""Base class for all FAL avatar and video generation models."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import fal_client
import time


@dataclass
class AvatarGenerationResult:
    """Standardized result for avatar/video generation."""
    success: bool
    video_url: Optional[str] = None
    duration: Optional[float] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    model_used: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAvatarModel(ABC):
    """Abstract base class for FAL avatar/video generation models."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.endpoint = ""
        self.pricing = {}
        self.max_duration = 60
        self.supported_resolutions = []
        self.supported_aspect_ratios = []

    @abstractmethod
    def generate(self, **kwargs) -> AvatarGenerationResult:
        """Generate video using the model."""
        pass

    @abstractmethod
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """Validate and normalize input parameters."""
        pass

    @abstractmethod
    def estimate_cost(self, duration: float, **kwargs) -> float:
        """Estimate generation cost based on parameters."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Return model capabilities and metadata."""
        pass

    def _call_fal_api(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call to FAL endpoint with error handling."""
        start_time = time.time()
        try:
            result = fal_client.subscribe(
                self.endpoint,
                arguments=arguments,
                with_logs=True
            )
            processing_time = time.time() - start_time
            return {
                "success": True,
                "result": result,
                "processing_time": processing_time
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }

    def _validate_url(self, url: str, param_name: str) -> None:
        """Validate URL format."""
        if not url:
            raise ValueError(f"{param_name} is required")
        if not url.startswith(("http://", "https://", "data:")):
            raise ValueError(f"{param_name} must be a valid URL or base64 data URI")

    def _validate_resolution(self, resolution: str) -> str:
        """Validate resolution parameter."""
        if resolution not in self.supported_resolutions:
            raise ValueError(
                f"Unsupported resolution '{resolution}'. "
                f"Supported: {self.supported_resolutions}"
            )
        return resolution

    def _validate_duration(self, duration: float) -> float:
        """Validate duration parameter."""
        if duration > self.max_duration:
            raise ValueError(
                f"Duration {duration}s exceeds max {self.max_duration}s"
            )
        return duration
```

**File: `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py`**
```python
"""Constants for FAL avatar generation models."""

# Model endpoints
MODEL_ENDPOINTS = {
    "omnihuman_v1_5": "fal-ai/bytedance/omnihuman/v1.5",
    "fabric_1_0": "veed/fabric-1.0",
    "fabric_1_0_fast": "veed/fabric-1.0/fast",
    "fabric_1_0_text": "veed/fabric-1.0/text",
    "kling_ref_to_video": "fal-ai/kling-video/o1/standard/reference-to-video",
    "kling_v2v_reference": "fal-ai/kling-video/o1/standard/video-to-video/reference",
    "kling_v2v_edit": "fal-ai/kling-video/o1/standard/video-to-video/edit",
}

# Display names for UI/CLI
MODEL_DISPLAY_NAMES = {
    "omnihuman_v1_5": "OmniHuman v1.5 (ByteDance)",
    "fabric_1_0": "VEED Fabric 1.0",
    "fabric_1_0_fast": "VEED Fabric 1.0 Fast",
    "fabric_1_0_text": "VEED Fabric 1.0 Text-to-Speech",
    "kling_ref_to_video": "Kling O1 Reference-to-Video",
    "kling_v2v_reference": "Kling O1 V2V Reference",
    "kling_v2v_edit": "Kling O1 V2V Edit",
}

# Pricing per second
MODEL_PRICING = {
    "omnihuman_v1_5": {"per_second": 0.16},
    "fabric_1_0": {"480p": 0.08, "720p": 0.15},
    "fabric_1_0_fast": {"480p": 0.10, "720p": 0.19},
    "fabric_1_0_text": {"480p": 0.08, "720p": 0.15},
    "kling_ref_to_video": {"per_second": 0.112},
    "kling_v2v_reference": {"per_second": 0.10},
    "kling_v2v_edit": {"per_second": 0.10},
}

# Default values
MODEL_DEFAULTS = {
    "omnihuman_v1_5": {
        "resolution": "1080p",
        "turbo_mode": False,
    },
    "fabric_1_0": {
        "resolution": "720p",
    },
    "fabric_1_0_text": {
        "resolution": "720p",
    },
    "kling_ref_to_video": {
        "duration": "5",
        "aspect_ratio": "16:9",
    },
    "kling_v2v_reference": {
        "duration": "5",
        "aspect_ratio": "16:9",
    },
    "kling_v2v_edit": {
        "aspect_ratio": "16:9",
    },
}

# Supported resolutions per model
SUPPORTED_RESOLUTIONS = {
    "omnihuman_v1_5": ["720p", "1080p"],
    "fabric_1_0": ["480p", "720p"],
    "fabric_1_0_fast": ["480p", "720p"],
    "fabric_1_0_text": ["480p", "720p"],
    "kling_ref_to_video": [],  # Uses aspect_ratio instead
    "kling_v2v_reference": [],
    "kling_v2v_edit": [],
}

# Supported aspect ratios
SUPPORTED_ASPECT_RATIOS = {
    "kling_ref_to_video": ["16:9", "9:16", "1:1"],
    "kling_v2v_reference": ["16:9", "9:16", "1:1"],
    "kling_v2v_edit": ["16:9", "9:16", "1:1"],
}

# Max durations (seconds)
MAX_DURATIONS = {
    "omnihuman_v1_5": {"1080p": 30, "720p": 60},
    "fabric_1_0": 120,
    "fabric_1_0_text": 120,
    "kling_ref_to_video": 10,
    "kling_v2v_reference": 10,
    "kling_v2v_edit": 10,
}

# Processing time estimates (seconds)
PROCESSING_TIME_ESTIMATES = {
    "omnihuman_v1_5": 60,
    "fabric_1_0": 45,
    "fabric_1_0_fast": 30,
    "fabric_1_0_text": 45,
    "kling_ref_to_video": 45,
    "kling_v2v_reference": 30,
    "kling_v2v_edit": 30,
}

# Input requirements
INPUT_REQUIREMENTS = {
    "omnihuman_v1_5": {
        "required": ["image_url", "audio_url"],
        "optional": ["prompt", "turbo_mode", "resolution"],
    },
    "fabric_1_0": {
        "required": ["image_url", "audio_url", "resolution"],
        "optional": [],
    },
    "fabric_1_0_text": {
        "required": ["image_url", "text", "resolution"],
        "optional": ["voice_description"],
    },
    "kling_ref_to_video": {
        "required": ["prompt", "reference_images"],
        "optional": ["duration", "aspect_ratio", "audio_url", "face_id"],
    },
    "kling_v2v_reference": {
        "required": ["prompt", "video_url"],
        "optional": ["duration", "aspect_ratio", "audio_url", "face_id"],
    },
    "kling_v2v_edit": {
        "required": ["video_url", "prompt"],
        "optional": ["mask_url"],
    },
}

# Model categories
MODEL_CATEGORIES = {
    "avatar_lipsync": ["omnihuman_v1_5", "fabric_1_0", "fabric_1_0_fast", "fabric_1_0_text"],
    "reference_to_video": ["kling_ref_to_video"],
    "video_to_video": ["kling_v2v_reference", "kling_v2v_edit"],
}

# Model recommendations
MODEL_RECOMMENDATIONS = {
    "quality": "omnihuman_v1_5",
    "speed": "fabric_1_0_fast",
    "text_to_avatar": "fabric_1_0_text",
    "character_consistency": "kling_ref_to_video",
    "style_transfer": "kling_v2v_reference",
    "video_editing": "kling_v2v_edit",
    "budget": "fabric_1_0",
}
```

---

### Subtask 2: Implement Individual Model Classes (1.5-2 hours)

**Goal:** Create specific model implementations

**File: `packages/providers/fal/avatar-generation/fal_avatar/models/omnihuman.py`**
```python
"""OmniHuman v1.5 model implementation."""

from typing import Any, Dict, Optional
from .base import BaseAvatarModel, AvatarGenerationResult
from ..config.constants import (
    MODEL_ENDPOINTS, MODEL_PRICING, MODEL_DEFAULTS,
    SUPPORTED_RESOLUTIONS, MAX_DURATIONS
)


class OmniHumanModel(BaseAvatarModel):
    """ByteDance OmniHuman v1.5 - Audio-driven human animation."""

    def __init__(self):
        super().__init__("omnihuman_v1_5")
        self.endpoint = MODEL_ENDPOINTS["omnihuman_v1_5"]
        self.pricing = MODEL_PRICING["omnihuman_v1_5"]
        self.supported_resolutions = SUPPORTED_RESOLUTIONS["omnihuman_v1_5"]
        self.defaults = MODEL_DEFAULTS["omnihuman_v1_5"]

    def validate_parameters(
        self,
        image_url: str,
        audio_url: str,
        resolution: str = None,
        turbo_mode: bool = None,
        prompt: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate and prepare parameters for OmniHuman."""
        # Validate required parameters
        self._validate_url(image_url, "image_url")
        self._validate_url(audio_url, "audio_url")

        # Apply defaults
        resolution = resolution or self.defaults["resolution"]
        turbo_mode = turbo_mode if turbo_mode is not None else self.defaults["turbo_mode"]

        # Validate resolution
        self._validate_resolution(resolution)

        # Build arguments
        arguments = {
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": resolution,
            "turbo_mode": turbo_mode,
        }

        if prompt:
            arguments["prompt"] = prompt

        return arguments

    def generate(
        self,
        image_url: str,
        audio_url: str,
        resolution: str = None,
        turbo_mode: bool = None,
        prompt: str = None,
        **kwargs
    ) -> AvatarGenerationResult:
        """Generate video with OmniHuman v1.5."""
        try:
            # Validate and prepare arguments
            arguments = self.validate_parameters(
                image_url=image_url,
                audio_url=audio_url,
                resolution=resolution,
                turbo_mode=turbo_mode,
                prompt=prompt,
            )

            # Call FAL API
            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response["error"],
                    model_used=self.model_name,
                    processing_time=response["processing_time"]
                )

            result = response["result"]
            duration = result.get("duration", 0)

            return AvatarGenerationResult(
                success=True,
                video_url=result["video"]["url"],
                duration=duration,
                cost=self.estimate_cost(duration),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={
                    "resolution": arguments["resolution"],
                    "turbo_mode": arguments["turbo_mode"],
                }
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name
            )

    def estimate_cost(self, duration: float, **kwargs) -> float:
        """Estimate cost based on video duration."""
        return duration * self.pricing["per_second"]

    def get_model_info(self) -> Dict[str, Any]:
        """Return model capabilities and metadata."""
        return {
            "name": self.model_name,
            "display_name": "OmniHuman v1.5 (ByteDance)",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "supported_resolutions": self.supported_resolutions,
            "max_duration": MAX_DURATIONS["omnihuman_v1_5"],
            "input_types": ["image", "audio"],
            "description": "Audio-driven human animation with realistic emotion correlation",
            "best_for": ["talking heads", "presentations", "avatar animations"],
        }
```

**File: `packages/providers/fal/avatar-generation/fal_avatar/models/fabric.py`**
```python
"""VEED Fabric 1.0 model implementations."""

from typing import Any, Dict, Optional
from .base import BaseAvatarModel, AvatarGenerationResult
from ..config.constants import (
    MODEL_ENDPOINTS, MODEL_PRICING, MODEL_DEFAULTS,
    SUPPORTED_RESOLUTIONS
)


class FabricModel(BaseAvatarModel):
    """VEED Fabric 1.0 - Lipsync video from image + audio."""

    def __init__(self, fast: bool = False):
        model_name = "fabric_1_0_fast" if fast else "fabric_1_0"
        super().__init__(model_name)
        self.endpoint = MODEL_ENDPOINTS[model_name]
        self.pricing = MODEL_PRICING[model_name]
        self.supported_resolutions = SUPPORTED_RESOLUTIONS[model_name]
        self.defaults = MODEL_DEFAULTS.get("fabric_1_0", {})
        self.is_fast = fast

    def validate_parameters(
        self,
        image_url: str,
        audio_url: str,
        resolution: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate parameters for Fabric model."""
        self._validate_url(image_url, "image_url")
        self._validate_url(audio_url, "audio_url")
        self._validate_resolution(resolution)

        return {
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": resolution,
        }

    def generate(
        self,
        image_url: str,
        audio_url: str,
        resolution: str = "720p",
        **kwargs
    ) -> AvatarGenerationResult:
        """Generate lipsync video with Fabric."""
        try:
            arguments = self.validate_parameters(
                image_url=image_url,
                audio_url=audio_url,
                resolution=resolution,
            )

            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response["error"],
                    model_used=self.model_name,
                    processing_time=response["processing_time"]
                )

            result = response["result"]
            # Estimate duration from file or default to 10s
            duration = kwargs.get("estimated_duration", 10)

            return AvatarGenerationResult(
                success=True,
                video_url=result.get("url") or result.get("video", {}).get("url"),
                duration=duration,
                cost=self.estimate_cost(duration, resolution=resolution),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={"resolution": resolution, "fast_mode": self.is_fast}
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name
            )

    def estimate_cost(self, duration: float, resolution: str = "720p", **kwargs) -> float:
        """Estimate cost based on duration and resolution."""
        price_per_second = self.pricing.get(resolution, self.pricing["720p"])
        return duration * price_per_second

    def get_model_info(self) -> Dict[str, Any]:
        """Return model info."""
        return {
            "name": self.model_name,
            "display_name": f"VEED Fabric 1.0{' Fast' if self.is_fast else ''}",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "supported_resolutions": self.supported_resolutions,
            "input_types": ["image", "audio"],
            "description": "Lipsync video generation from image and audio",
            "best_for": ["lipsync", "dubbing", "social media"],
        }


class FabricTextModel(BaseAvatarModel):
    """VEED Fabric 1.0 Text - Text-to-speech avatar."""

    def __init__(self):
        super().__init__("fabric_1_0_text")
        self.endpoint = MODEL_ENDPOINTS["fabric_1_0_text"]
        self.pricing = MODEL_PRICING["fabric_1_0_text"]
        self.supported_resolutions = SUPPORTED_RESOLUTIONS["fabric_1_0_text"]

    def validate_parameters(
        self,
        image_url: str,
        text: str,
        resolution: str,
        voice_description: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate parameters for Fabric Text model."""
        self._validate_url(image_url, "image_url")

        if not text or len(text) > 2000:
            raise ValueError("Text is required and must be <= 2000 characters")

        self._validate_resolution(resolution)

        arguments = {
            "image_url": image_url,
            "text": text,
            "resolution": resolution,
        }

        if voice_description:
            arguments["voice_description"] = voice_description

        return arguments

    def generate(
        self,
        image_url: str,
        text: str,
        resolution: str = "720p",
        voice_description: str = None,
        **kwargs
    ) -> AvatarGenerationResult:
        """Generate TTS avatar video with Fabric Text."""
        try:
            arguments = self.validate_parameters(
                image_url=image_url,
                text=text,
                resolution=resolution,
                voice_description=voice_description,
            )

            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response["error"],
                    model_used=self.model_name,
                    processing_time=response["processing_time"]
                )

            result = response["result"]
            # Estimate duration: ~150 words per minute, average 5 chars per word
            estimated_duration = len(text) / 5 / 150 * 60

            return AvatarGenerationResult(
                success=True,
                video_url=result.get("video", {}).get("url"),
                duration=estimated_duration,
                cost=self.estimate_cost(estimated_duration, resolution=resolution),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={
                    "resolution": resolution,
                    "text_length": len(text),
                    "voice_description": voice_description,
                }
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name
            )

    def estimate_cost(self, duration: float, resolution: str = "720p", **kwargs) -> float:
        """Estimate cost based on duration and resolution."""
        price_per_second = self.pricing.get(resolution, self.pricing["720p"])
        return duration * price_per_second

    def get_model_info(self) -> Dict[str, Any]:
        """Return model info."""
        return {
            "name": self.model_name,
            "display_name": "VEED Fabric 1.0 Text-to-Speech",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "supported_resolutions": self.supported_resolutions,
            "input_types": ["image", "text"],
            "description": "Text-to-speech avatar video generation",
            "best_for": ["quick avatars", "no pre-recorded audio"],
        }
```

**File: `packages/providers/fal/avatar-generation/fal_avatar/models/kling.py`**
```python
"""Kling O1 model implementations for reference and video-to-video."""

from typing import Any, Dict, List, Optional
from .base import BaseAvatarModel, AvatarGenerationResult
from ..config.constants import (
    MODEL_ENDPOINTS, MODEL_PRICING, MODEL_DEFAULTS,
    SUPPORTED_ASPECT_RATIOS, MAX_DURATIONS
)


class KlingRefToVideoModel(BaseAvatarModel):
    """Kling O1 Reference-to-Video - Character/element consistency."""

    def __init__(self):
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
        duration: str = None,
        aspect_ratio: str = None,
        audio_url: str = None,
        face_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate parameters for Kling Reference-to-Video."""
        if not prompt:
            raise ValueError("prompt is required")

        if not reference_images or len(reference_images) == 0:
            raise ValueError("At least one reference image is required")

        if len(reference_images) > self.max_references:
            raise ValueError(f"Maximum {self.max_references} reference images allowed")

        for i, img_url in enumerate(reference_images):
            self._validate_url(img_url, f"reference_images[{i}]")

        # Apply defaults
        duration = duration or self.defaults["duration"]
        aspect_ratio = aspect_ratio or self.defaults["aspect_ratio"]

        if aspect_ratio not in self.supported_aspect_ratios:
            raise ValueError(f"Unsupported aspect_ratio. Supported: {self.supported_aspect_ratios}")

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
        duration: str = None,
        aspect_ratio: str = None,
        audio_url: str = None,
        face_id: str = None,
        **kwargs
    ) -> AvatarGenerationResult:
        """Generate video with reference image consistency."""
        try:
            arguments = self.validate_parameters(
                prompt=prompt,
                reference_images=reference_images,
                duration=duration,
                aspect_ratio=aspect_ratio,
                audio_url=audio_url,
                face_id=face_id,
                **kwargs
            )

            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response["error"],
                    model_used=self.model_name,
                    processing_time=response["processing_time"]
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
                }
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name
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
    """Kling O1 Video-to-Video Reference - Style-guided generation."""

    def __init__(self):
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
        duration: str = None,
        aspect_ratio: str = None,
        audio_url: str = None,
        face_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate parameters for Kling V2V Reference."""
        if not prompt:
            raise ValueError("prompt is required (use @Video1 to reference input)")

        self._validate_url(video_url, "video_url")

        duration = duration or self.defaults["duration"]
        aspect_ratio = aspect_ratio or self.defaults["aspect_ratio"]

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
        duration: str = None,
        aspect_ratio: str = None,
        audio_url: str = None,
        face_id: str = None,
        **kwargs
    ) -> AvatarGenerationResult:
        """Generate style-guided video."""
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
                    processing_time=response["processing_time"]
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
                metadata={"aspect_ratio": arguments["aspect_ratio"]}
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name
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
            "max_duration": self.max_duration,
            "input_types": ["video", "prompt"],
            "description": "Generate new shots preserving motion and camera style",
            "best_for": ["scene continuity", "style transfer", "next shot generation"],
        }


class KlingV2VEditModel(BaseAvatarModel):
    """Kling O1 Video-to-Video Edit - Targeted modifications."""

    def __init__(self):
        super().__init__("kling_v2v_edit")
        self.endpoint = MODEL_ENDPOINTS["kling_v2v_edit"]
        self.pricing = MODEL_PRICING["kling_v2v_edit"]
        self.max_duration = MAX_DURATIONS["kling_v2v_edit"]

    def validate_parameters(
        self,
        video_url: str,
        prompt: str,
        mask_url: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate parameters for Kling V2V Edit."""
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
        mask_url: str = None,
        **kwargs
    ) -> AvatarGenerationResult:
        """Edit video with natural language instructions."""
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
                    processing_time=response["processing_time"]
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
                metadata={"has_mask": mask_url is not None}
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name
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
```

**File: `packages/providers/fal/avatar-generation/fal_avatar/models/__init__.py`**
```python
"""FAL Avatar model exports."""

from .base import BaseAvatarModel, AvatarGenerationResult
from .omnihuman import OmniHumanModel
from .fabric import FabricModel, FabricTextModel
from .kling import KlingRefToVideoModel, KlingV2VReferenceModel, KlingV2VEditModel

__all__ = [
    "BaseAvatarModel",
    "AvatarGenerationResult",
    "OmniHumanModel",
    "FabricModel",
    "FabricTextModel",
    "KlingRefToVideoModel",
    "KlingV2VReferenceModel",
    "KlingV2VEditModel",
]
```

---

### Subtask 3: Create Unified Generator (45 min - 1 hour)

**Goal:** Create the main generator class that routes to appropriate models

**File: `packages/providers/fal/avatar-generation/fal_avatar/generator.py`**
```python
"""Unified FAL Avatar Generator - Routes to appropriate model implementations."""

from typing import Any, Dict, List, Optional, Union
from .models import (
    BaseAvatarModel,
    AvatarGenerationResult,
    OmniHumanModel,
    FabricModel,
    FabricTextModel,
    KlingRefToVideoModel,
    KlingV2VReferenceModel,
    KlingV2VEditModel,
)
from .config.constants import (
    MODEL_DISPLAY_NAMES,
    MODEL_CATEGORIES,
    MODEL_RECOMMENDATIONS,
    INPUT_REQUIREMENTS,
)


class FALAvatarGenerator:
    """Unified generator for FAL avatar and video generation models."""

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
        }

    def generate(
        self,
        model: str = "omnihuman_v1_5",
        **kwargs
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
                model_used=model
            )

        return self.models[model].generate(**kwargs)

    def generate_avatar(
        self,
        image_url: str,
        audio_url: str = None,
        text: str = None,
        model: str = None,
        **kwargs
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
                    error="Either audio_url or text is required for avatar generation"
                )

        return self.generate(
            model=model,
            image_url=image_url,
            audio_url=audio_url,
            text=text,
            **kwargs
        )

    def generate_reference_video(
        self,
        prompt: str,
        reference_images: List[str],
        model: str = "kling_ref_to_video",
        **kwargs
    ) -> AvatarGenerationResult:
        """
        Generate video with reference image consistency.

        Args:
            prompt: Generation prompt (use @Element1, @Element2, etc.)
            reference_images: List of reference image URLs (max 4)
            model: Model to use
            **kwargs: Additional parameters (duration, aspect_ratio, etc.)
        """
        return self.generate(
            model=model,
            prompt=prompt,
            reference_images=reference_images,
            **kwargs
        )

    def transform_video(
        self,
        video_url: str,
        prompt: str,
        mode: str = "reference",
        **kwargs
    ) -> AvatarGenerationResult:
        """
        Transform existing video (style transfer or edit).

        Args:
            video_url: Source video URL
            prompt: Transformation prompt
            mode: "reference" for style-guided, "edit" for targeted modifications
            **kwargs: Additional parameters
        """
        model = "kling_v2v_reference" if mode == "reference" else "kling_v2v_edit"

        return self.generate(
            model=model,
            video_url=video_url,
            prompt=prompt,
            **kwargs
        )

    def list_models(self) -> List[str]:
        """Return list of available model identifiers."""
        return list(self.models.keys())

    def list_models_by_category(self) -> Dict[str, List[str]]:
        """Return models grouped by category."""
        return MODEL_CATEGORIES.copy()

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a specific model."""
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
        **kwargs
    ) -> float:
        """Estimate generation cost for a model."""
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        return self.models[model].estimate_cost(duration, **kwargs)

    def recommend_model(
        self,
        use_case: str = "quality"
    ) -> str:
        """
        Get model recommendation for a use case.

        Args:
            use_case: One of "quality", "speed", "text_to_avatar",
                     "character_consistency", "style_transfer",
                     "video_editing", "budget"
        """
        if use_case in MODEL_RECOMMENDATIONS:
            return MODEL_RECOMMENDATIONS[use_case]
        return MODEL_RECOMMENDATIONS["quality"]

    def get_input_requirements(self, model: str) -> Dict[str, List[str]]:
        """Get required and optional inputs for a model."""
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
            True if valid, raises ValueError if invalid
        """
        requirements = self.get_input_requirements(model)
        missing = [
            param for param in requirements["required"]
            if param not in kwargs or kwargs[param] is None
        ]

        if missing:
            raise ValueError(f"Missing required parameters for {model}: {missing}")

        return True
```

---

### Subtask 4: Integrate with Core Pipeline (45 min - 1 hour)

**Goal:** Register models in core constants and update pipeline manager

**Files to Modify:**

1. **`packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`**

Add the following to existing dictionaries:

```python
# Add to SUPPORTED_MODELS
"avatar": [
    "omnihuman_v1_5",       # ByteDance - audio-driven animation
    "fabric_1_0",           # VEED - lipsync (image + audio)
    "fabric_1_0_fast",      # VEED - fast lipsync
    "fabric_1_0_text",      # VEED - text-to-speech avatar
    "kling_ref_to_video",   # Kling - reference image consistency
    "kling_v2v_reference",  # Kling - style-guided video
    "kling_v2v_edit",       # Kling - targeted modifications
],

# Add to MODEL_RECOMMENDATIONS
"avatar": {
    "quality": "omnihuman_v1_5",
    "speed": "fabric_1_0_fast",
    "balanced": "fabric_1_0",
    "text_to_avatar": "fabric_1_0_text",
    "character_consistency": "kling_ref_to_video",
    "style_transfer": "kling_v2v_reference",
    "video_editing": "kling_v2v_edit",
},

# Add to COST_ESTIMATES (per second)
"avatar": {
    "omnihuman_v1_5": 0.16,
    "fabric_1_0": 0.15,
    "fabric_1_0_fast": 0.19,
    "fabric_1_0_text": 0.15,
    "kling_ref_to_video": 0.112,
    "kling_v2v_reference": 0.10,
    "kling_v2v_edit": 0.10,
},

# Add to PROCESSING_TIME_ESTIMATES (seconds)
"avatar": {
    "omnihuman_v1_5": 60,
    "fabric_1_0": 45,
    "fabric_1_0_fast": 30,
    "fabric_1_0_text": 45,
    "kling_ref_to_video": 45,
    "kling_v2v_reference": 30,
    "kling_v2v_edit": 30,
},
```

2. **`packages/core/ai_content_pipeline/ai_content_pipeline/models/avatar.py`**

Update to integrate FAL generator:

```python
"""Unified Avatar Generator with FAL and Replicate support."""

from typing import Any, Dict, List, Optional
from .base import BaseContentModel, ModelResult

# Import FAL generator
from packages.providers.fal.avatar_generation.fal_avatar.generator import (
    FALAvatarGenerator,
    AvatarGenerationResult,
)


class UnifiedAvatarGenerator(BaseContentModel):
    """Unified interface for all avatar/video generation models."""

    FAL_MODELS = [
        "omnihuman_v1_5", "fabric_1_0", "fabric_1_0_fast",
        "fabric_1_0_text", "kling_ref_to_video",
        "kling_v2v_reference", "kling_v2v_edit"
    ]

    def __init__(self):
        super().__init__("avatar")
        self.fal_generator = FALAvatarGenerator()

    def generate(
        self,
        input_data: Dict[str, Any] = None,
        model: str = "omnihuman_v1_5",
        **kwargs
    ) -> ModelResult:
        """Generate avatar/video using specified model."""
        # Merge input_data with kwargs
        params = {**(input_data or {}), **kwargs}

        if model in self.FAL_MODELS:
            result = self.fal_generator.generate(model=model, **params)
            return self._convert_result(result)
        else:
            return ModelResult(
                success=False,
                error=f"Unknown model: {model}",
                model_used=model
            )

    def _convert_result(self, result: AvatarGenerationResult) -> ModelResult:
        """Convert FAL result to standard ModelResult."""
        return ModelResult(
            success=result.success,
            output_url=result.video_url,
            cost_estimate=result.cost,
            processing_time=result.processing_time,
            model_used=result.model_used,
            error=result.error,
            metadata=result.metadata
        )

    def get_available_models(self) -> List[str]:
        """Return all available avatar models."""
        return self.FAL_MODELS.copy()

    def estimate_cost(self, model: str, duration: float = 10, **kwargs) -> float:
        """Estimate generation cost."""
        return self.fal_generator.estimate_cost(model, duration, **kwargs)

    def validate_input(
        self,
        input_data: Dict[str, Any],
        model: str,
        **kwargs
    ) -> bool:
        """Validate input for specified model."""
        return self.fal_generator.validate_inputs(model, **input_data, **kwargs)
```

---

### Subtask 5: Add CLI Commands (30-45 min)

**Goal:** Add CLI support for avatar and video generation

**File to Modify:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

**Add Commands:**
```python
@cli.command()
@click.option("--image", help="Image URL or local path")
@click.option("--audio", help="Audio URL or local path")
@click.option("--text", help="Text for TTS avatar")
@click.option("--video", help="Video URL for video-to-video")
@click.option("--reference-images", multiple=True, help="Reference images (max 4)")
@click.option("--prompt", help="Generation/edit prompt")
@click.option("--model", default="auto", help="Model to use (default: auto-select)")
@click.option("--resolution", default="720p", help="Output resolution")
@click.option("--aspect-ratio", default="16:9", help="Aspect ratio for Kling models")
@click.option("--duration", default="5", help="Duration (5 or 10 seconds)")
@click.option("--output", "-o", help="Output directory")
@click.option("--mock", is_flag=True, help="Run in mock mode (no API calls)")
def generate_avatar(
    image, audio, text, video, reference_images,
    prompt, model, resolution, aspect_ratio, duration, output, mock
):
    """
    Generate avatar video or transform existing video.

    Examples:

    \b
    # Audio-driven avatar (auto-selects OmniHuman)
    aicp generate-avatar --image face.jpg --audio speech.mp3

    \b
    # Text-to-speech avatar (auto-selects Fabric Text)
    aicp generate-avatar --image face.jpg --text "Hello world"

    \b
    # Reference-based video (character consistency)
    aicp generate-avatar --reference-images char1.jpg char2.jpg \\
        --prompt "@Element1 walking in park, @Element2 watching"

    \b
    # Video style transfer
    aicp generate-avatar --video source.mp4 --prompt "cinematic style"

    \b
    # Video editing
    aicp generate-avatar --video source.mp4 --prompt "change background" \\
        --model kling_v2v_edit
    """
    from .models.avatar import UnifiedAvatarGenerator

    generator = UnifiedAvatarGenerator()

    # Auto-select model based on inputs
    if model == "auto":
        if reference_images:
            model = "kling_ref_to_video"
        elif video and not audio:
            model = "kling_v2v_reference"
        elif text and image:
            model = "fabric_1_0_text"
        elif audio and image:
            model = "omnihuman_v1_5"
        else:
            click.echo("Error: Could not auto-select model. Please specify --model")
            return

    # Build parameters
    params = {}
    if image:
        params["image_url"] = image
    if audio:
        params["audio_url"] = audio
    if text:
        params["text"] = text
    if video:
        params["video_url"] = video
    if reference_images:
        params["reference_images"] = list(reference_images)
    if prompt:
        params["prompt"] = prompt
    if resolution:
        params["resolution"] = resolution
    if aspect_ratio:
        params["aspect_ratio"] = aspect_ratio
    if duration:
        params["duration"] = duration

    click.echo(f"Generating with model: {model}")
    click.echo(f"Parameters: {params}")

    if mock:
        click.echo("[MOCK MODE] Would call API with above parameters")
        return

    # Generate
    result = generator.generate(model=model, **params)

    if result.success:
        click.echo(f"Success! Video URL: {result.output_url}")
        click.echo(f"Cost: ${result.cost_estimate:.4f}")
        click.echo(f"Processing time: {result.processing_time:.1f}s")
    else:
        click.echo(f"Error: {result.error}")
```

**CLI Usage Examples:**
```bash
# Audio-driven avatar (OmniHuman)
aicp generate-avatar --image face.jpg --audio speech.mp3

# Fast lipsync (Fabric Fast)
aicp generate-avatar --image face.jpg --audio speech.mp3 --model fabric_1_0_fast

# Text-to-speech avatar (Fabric Text)
aicp generate-avatar --image face.jpg --text "Hello, this is a demo." --resolution 720p

# Reference-based video with character consistency
aicp generate-avatar \
    --reference-images character.jpg background.jpg \
    --prompt "@Element1 walking through @Element2, cinematic" \
    --duration 10 --aspect-ratio 16:9

# Video style transfer (preserve motion/camera)
aicp generate-avatar --video source.mp4 \
    --prompt "Based on @Video1, generate next shot with dramatic lighting"

# Video editing (targeted modifications)
aicp generate-avatar --video source.mp4 \
    --prompt "Change the background to a beach scene" \
    --model kling_v2v_edit

# Mock mode for testing
aicp generate-avatar --image test.jpg --audio test.mp3 --mock
```

---

### Subtask 6: Add YAML Pipeline Support (30-45 min)

**Goal:** Enable avatar steps in YAML configurations

**File to Modify:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py`

Ensure the pipeline manager handles `type: "avatar"` steps.

**Example YAML Configurations:**

**File: `input/pipelines/avatar_from_audio.yaml`**
```yaml
name: "Audio to Avatar Video"
description: "Generate talking avatar from portrait and audio"

steps:
  - name: "create_avatar"
    type: "avatar"
    model: "omnihuman_v1_5"
    params:
      image_url: "https://example.com/portrait.jpg"
      audio_url: "https://example.com/speech.mp3"
      resolution: "1080p"
      turbo_mode: false
    output: "avatar_video"
```

**File: `input/pipelines/avatar_from_text.yaml`**
```yaml
name: "Text to Avatar Video"
description: "Generate speaking avatar from text script"

steps:
  - name: "create_tts_avatar"
    type: "avatar"
    model: "fabric_1_0_text"
    params:
      image_url: "https://example.com/face.jpg"
      text: "Welcome to our product demonstration. Today I'll show you how easy it is to use our platform."
      resolution: "720p"
      voice_description: "Professional, confident, female voice"
    output: "avatar_video"
```

**File: `input/pipelines/character_consistency.yaml`**
```yaml
name: "Character Consistency Pipeline"
description: "Generate video with consistent characters across shots"

steps:
  - name: "generate_consistent_video"
    type: "avatar"
    model: "kling_ref_to_video"
    params:
      reference_images:
        - "https://example.com/character_front.jpg"
        - "https://example.com/character_side.jpg"
        - "https://example.com/product.jpg"
      prompt: "@Element1 presenting @Element3 to camera, professional studio lighting"
      duration: "10"
      aspect_ratio: "16:9"
    output: "product_video"
```

**File: `input/pipelines/video_style_transfer.yaml`**
```yaml
name: "Video Style Transfer"
description: "Transform video while preserving motion"

steps:
  - name: "style_transfer"
    type: "avatar"
    model: "kling_v2v_reference"
    params:
      video_url: "https://example.com/source.mp4"
      prompt: "Based on @Video1, generate the next shot. Make it cinematic with warm golden hour lighting"
      duration: "5"
      aspect_ratio: "16:9"
    output: "styled_video"
```

**File: `input/pipelines/full_avatar_pipeline.yaml`**
```yaml
name: "Full Avatar Production Pipeline"
description: "Generate portrait, create avatar, and enhance"

steps:
  - name: "generate_portrait"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "Professional corporate headshot of a friendly businesswoman, neutral gray background, soft lighting, high quality portrait"
      width: 1024
      height: 1024
    output: "portrait_image"

  - name: "create_avatar"
    type: "avatar"
    model: "fabric_1_0_text"
    params:
      image_url: "{{generate_portrait.output}}"
      text: "Hello and welcome! I'm excited to walk you through our latest features today. Let's get started with the dashboard overview."
      resolution: "720p"
      voice_description: "Warm, professional female voice with American accent"
    output: "avatar_video"

  - name: "enhance_video"
    type: "video_processing"
    model: "topaz"
    params:
      video_url: "{{create_avatar.output}}"
      scale: 2
    output: "final_video"
```

---

### Subtask 7: Write Unit Tests (45 min - 1 hour)

**Goal:** Create comprehensive tests

**File: `tests/test_avatar_models.py`**
```python
"""Unit tests for FAL avatar model classes."""

import pytest
from unittest.mock import patch, MagicMock

from packages.providers.fal.avatar_generation.fal_avatar.models import (
    OmniHumanModel,
    FabricModel,
    FabricTextModel,
    KlingRefToVideoModel,
    KlingV2VReferenceModel,
    KlingV2VEditModel,
    AvatarGenerationResult,
)


class TestOmniHumanModel:
    """Tests for OmniHuman v1.5 model."""

    def test_initialization(self):
        """Test model initializes with correct attributes."""
        model = OmniHumanModel()
        assert model.model_name == "omnihuman_v1_5"
        assert model.endpoint == "fal-ai/bytedance/omnihuman/v1.5"
        assert model.pricing["per_second"] == 0.16

    def test_cost_estimation(self):
        """Test cost calculation."""
        model = OmniHumanModel()
        cost = model.estimate_cost(duration=10)
        assert cost == 1.60  # $0.16 * 10 seconds

        cost_30s = model.estimate_cost(duration=30)
        assert cost_30s == 4.80  # $0.16 * 30 seconds

    def test_validate_parameters_success(self):
        """Test parameter validation with valid inputs."""
        model = OmniHumanModel()
        params = model.validate_parameters(
            image_url="https://example.com/face.jpg",
            audio_url="https://example.com/audio.mp3",
        )
        assert params["image_url"] == "https://example.com/face.jpg"
        assert params["resolution"] == "1080p"  # Default

    def test_validate_parameters_missing_image(self):
        """Test validation fails without image."""
        model = OmniHumanModel()
        with pytest.raises(ValueError, match="image_url is required"):
            model.validate_parameters(
                image_url=None,
                audio_url="https://example.com/audio.mp3",
            )

    def test_validate_parameters_invalid_resolution(self):
        """Test validation fails with invalid resolution."""
        model = OmniHumanModel()
        with pytest.raises(ValueError, match="Unsupported resolution"):
            model.validate_parameters(
                image_url="https://example.com/face.jpg",
                audio_url="https://example.com/audio.mp3",
                resolution="4k",
            )

    def test_get_model_info(self):
        """Test model info returns expected structure."""
        model = OmniHumanModel()
        info = model.get_model_info()
        assert info["name"] == "omnihuman_v1_5"
        assert "pricing" in info
        assert "best_for" in info


class TestFabricModel:
    """Tests for VEED Fabric models."""

    def test_standard_initialization(self):
        """Test standard Fabric model."""
        model = FabricModel(fast=False)
        assert model.model_name == "fabric_1_0"
        assert model.is_fast is False

    def test_fast_initialization(self):
        """Test fast Fabric model."""
        model = FabricModel(fast=True)
        assert model.model_name == "fabric_1_0_fast"
        assert model.is_fast is True

    def test_resolution_based_pricing(self):
        """Test different prices for resolutions."""
        model = FabricModel()

        cost_480p = model.estimate_cost(duration=10, resolution="480p")
        assert cost_480p == 0.80  # $0.08 * 10

        cost_720p = model.estimate_cost(duration=10, resolution="720p")
        assert cost_720p == 1.50  # $0.15 * 10


class TestFabricTextModel:
    """Tests for VEED Fabric Text model."""

    def test_initialization(self):
        """Test model initialization."""
        model = FabricTextModel()
        assert model.model_name == "fabric_1_0_text"
        assert "image" in model.get_model_info()["input_types"]
        assert "text" in model.get_model_info()["input_types"]

    def test_validate_text_length(self):
        """Test text length validation."""
        model = FabricTextModel()

        # Empty text should fail
        with pytest.raises(ValueError):
            model.validate_parameters(
                image_url="https://example.com/face.jpg",
                text="",
                resolution="720p",
            )

        # Text over 2000 chars should fail
        with pytest.raises(ValueError):
            model.validate_parameters(
                image_url="https://example.com/face.jpg",
                text="x" * 2001,
                resolution="720p",
            )


class TestKlingRefToVideoModel:
    """Tests for Kling Reference-to-Video model."""

    def test_initialization(self):
        """Test model initialization."""
        model = KlingRefToVideoModel()
        assert model.model_name == "kling_ref_to_video"
        assert model.max_references == 4
        assert model.max_duration == 10

    def test_cost_estimation(self):
        """Test cost calculation."""
        model = KlingRefToVideoModel()
        cost = model.estimate_cost(duration=10)
        assert cost == 1.12  # $0.112 * 10 seconds

    def test_validate_max_references(self):
        """Test reference image limit."""
        model = KlingRefToVideoModel()

        # 4 images should work
        params = model.validate_parameters(
            prompt="test",
            reference_images=[
                "https://example.com/1.jpg",
                "https://example.com/2.jpg",
                "https://example.com/3.jpg",
                "https://example.com/4.jpg",
            ],
        )
        assert len(params["reference_images"]) == 4

        # 5 images should fail
        with pytest.raises(ValueError, match="Maximum 4 reference images"):
            model.validate_parameters(
                prompt="test",
                reference_images=[f"https://example.com/{i}.jpg" for i in range(5)],
            )


class TestKlingV2VModels:
    """Tests for Kling Video-to-Video models."""

    def test_reference_model(self):
        """Test V2V Reference model."""
        model = KlingV2VReferenceModel()
        assert model.model_name == "kling_v2v_reference"
        assert "video" in model.get_model_info()["input_types"]

    def test_edit_model(self):
        """Test V2V Edit model."""
        model = KlingV2VEditModel()
        assert model.model_name == "kling_v2v_edit"

        # Should allow optional mask
        params = model.validate_parameters(
            video_url="https://example.com/video.mp4",
            prompt="change background",
            mask_url="https://example.com/mask.png",
        )
        assert "mask_url" in params
```

**File: `tests/test_avatar_generator.py`**
```python
"""Unit tests for FAL Avatar Generator."""

import pytest
from unittest.mock import patch, MagicMock

from packages.providers.fal.avatar_generation.fal_avatar.generator import (
    FALAvatarGenerator,
)
from packages.providers.fal.avatar_generation.fal_avatar.models import (
    AvatarGenerationResult,
)


class TestFALAvatarGenerator:
    """Tests for the unified generator."""

    def test_initialization(self):
        """Test generator initializes all models."""
        generator = FALAvatarGenerator()
        assert len(generator.models) == 7
        assert "omnihuman_v1_5" in generator.models
        assert "kling_ref_to_video" in generator.models

    def test_list_models(self):
        """Test model listing."""
        generator = FALAvatarGenerator()
        models = generator.list_models()

        assert "omnihuman_v1_5" in models
        assert "fabric_1_0" in models
        assert "fabric_1_0_fast" in models
        assert "fabric_1_0_text" in models
        assert "kling_ref_to_video" in models
        assert "kling_v2v_reference" in models
        assert "kling_v2v_edit" in models

    def test_list_models_by_category(self):
        """Test category-based listing."""
        generator = FALAvatarGenerator()
        categories = generator.list_models_by_category()

        assert "avatar_lipsync" in categories
        assert "reference_to_video" in categories
        assert "video_to_video" in categories

    def test_get_model_info(self):
        """Test getting model info."""
        generator = FALAvatarGenerator()
        info = generator.get_model_info("omnihuman_v1_5")

        assert info["name"] == "omnihuman_v1_5"
        assert "pricing" in info
        assert "endpoint" in info

    def test_get_model_info_invalid(self):
        """Test error on invalid model."""
        generator = FALAvatarGenerator()
        with pytest.raises(ValueError, match="Unknown model"):
            generator.get_model_info("nonexistent_model")

    def test_recommend_model(self):
        """Test model recommendations."""
        generator = FALAvatarGenerator()

        assert generator.recommend_model("quality") == "omnihuman_v1_5"
        assert generator.recommend_model("speed") == "fabric_1_0_fast"
        assert generator.recommend_model("text_to_avatar") == "fabric_1_0_text"
        assert generator.recommend_model("character_consistency") == "kling_ref_to_video"

    def test_estimate_cost(self):
        """Test cost estimation through generator."""
        generator = FALAvatarGenerator()

        cost = generator.estimate_cost("omnihuman_v1_5", duration=10)
        assert cost == 1.60

        cost = generator.estimate_cost("fabric_1_0", duration=10, resolution="480p")
        assert cost == 0.80

    def test_get_input_requirements(self):
        """Test input requirements retrieval."""
        generator = FALAvatarGenerator()

        reqs = generator.get_input_requirements("omnihuman_v1_5")
        assert "image_url" in reqs["required"]
        assert "audio_url" in reqs["required"]

        reqs = generator.get_input_requirements("fabric_1_0_text")
        assert "text" in reqs["required"]

    def test_validate_inputs_success(self):
        """Test input validation success."""
        generator = FALAvatarGenerator()

        result = generator.validate_inputs(
            "omnihuman_v1_5",
            image_url="https://example.com/face.jpg",
            audio_url="https://example.com/audio.mp3",
        )
        assert result is True

    def test_validate_inputs_failure(self):
        """Test input validation failure."""
        generator = FALAvatarGenerator()

        with pytest.raises(ValueError, match="Missing required parameters"):
            generator.validate_inputs(
                "omnihuman_v1_5",
                image_url="https://example.com/face.jpg",
                # Missing audio_url
            )

    def test_generate_unknown_model(self):
        """Test generate with unknown model returns error."""
        generator = FALAvatarGenerator()
        result = generator.generate(model="nonexistent")

        assert result.success is False
        assert "Unknown model" in result.error

    def test_generate_avatar_auto_select_text(self):
        """Test auto-selection for text input."""
        generator = FALAvatarGenerator()

        with patch.object(generator.models["fabric_1_0_text"], "generate") as mock:
            mock.return_value = AvatarGenerationResult(success=True)
            generator.generate_avatar(
                image_url="https://example.com/face.jpg",
                text="Hello world",
            )
            mock.assert_called_once()

    def test_generate_avatar_auto_select_audio(self):
        """Test auto-selection for audio input."""
        generator = FALAvatarGenerator()

        with patch.object(generator.models["omnihuman_v1_5"], "generate") as mock:
            mock.return_value = AvatarGenerationResult(success=True)
            generator.generate_avatar(
                image_url="https://example.com/face.jpg",
                audio_url="https://example.com/audio.mp3",
            )
            mock.assert_called_once()
```

---

### Subtask 8: Update Documentation (30 min)

**Goal:** Update README and CLAUDE.md

**Updates for `README.md`:**
```markdown
### 📦 Avatar & Video Generation (7 models)

| Model | Input | Output | Pricing | Best For |
|-------|-------|--------|---------|----------|
| **OmniHuman v1.5** | Image + Audio | Video | $0.16/sec | Realistic talking heads |
| **Fabric 1.0** | Image + Audio | Video | $0.08-0.15/sec | Quick lipsync |
| **Fabric 1.0 Fast** | Image + Audio | Video | $0.10-0.19/sec | Speed priority |
| **Fabric 1.0 Text** | Image + Text | Video | $0.08-0.15/sec | No audio needed |
| **Kling Ref-to-Video** | Images + Prompt | Video | $0.112/sec | Character consistency |
| **Kling V2V Reference** | Video + Prompt | Video | $0.10/sec | Style transfer |
| **Kling V2V Edit** | Video + Prompt | Video | $0.10/sec | Targeted edits |
```

**Updates for `CLAUDE.md`:**
```markdown
### 🎭 Avatar Generation Commands
```bash
# Audio-driven avatar (OmniHuman)
aicp generate-avatar --image face.jpg --audio speech.mp3

# Text-to-speech avatar (Fabric Text)
aicp generate-avatar --image face.jpg --text "Hello world"

# Reference-based video (character consistency)
aicp generate-avatar --reference-images char.jpg bg.jpg \
    --prompt "@Element1 in @Element2"

# Video style transfer
aicp generate-avatar --video source.mp4 --prompt "cinematic style"

# Video editing
aicp generate-avatar --video source.mp4 --prompt "change background" \
    --model kling_v2v_edit
```
```

---

## File Path Summary

| Category | File Path | Action |
|----------|-----------|--------|
| **Package Init** | `packages/providers/fal/avatar-generation/fal_avatar/__init__.py` | Create |
| **Config** | `packages/providers/fal/avatar-generation/fal_avatar/config/__init__.py` | Create |
| **Config** | `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py` | Create |
| **Base Model** | `packages/providers/fal/avatar-generation/fal_avatar/models/__init__.py` | Create |
| **Base Model** | `packages/providers/fal/avatar-generation/fal_avatar/models/base.py` | Create |
| **OmniHuman** | `packages/providers/fal/avatar-generation/fal_avatar/models/omnihuman.py` | Create |
| **Fabric** | `packages/providers/fal/avatar-generation/fal_avatar/models/fabric.py` | Create |
| **Kling** | `packages/providers/fal/avatar-generation/fal_avatar/models/kling.py` | Create |
| **Utils** | `packages/providers/fal/avatar-generation/fal_avatar/utils/__init__.py` | Create |
| **Utils** | `packages/providers/fal/avatar-generation/fal_avatar/utils/validators.py` | Create |
| **Generator** | `packages/providers/fal/avatar-generation/fal_avatar/generator.py` | Create |
| **Core Constants** | `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py` | Modify |
| **Core Avatar** | `packages/core/ai_content_pipeline/ai_content_pipeline/models/avatar.py` | Modify |
| **Pipeline** | `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/manager.py` | Modify |
| **CLI** | `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Modify |
| **Tests** | `tests/test_avatar_models.py` | Create |
| **Tests** | `tests/test_avatar_generator.py` | Create |
| **YAML Examples** | `input/pipelines/avatar_*.yaml` | Create |
| **Docs** | `README.md` | Modify |
| **Docs** | `CLAUDE.md` | Modify |

---

## Input Types Summary

| Model | Image | Audio | Video | Text | Ref Images |
|-------|-------|-------|-------|------|------------|
| OmniHuman v1.5 | ✅ Required | ✅ Required | ❌ | ⚪ Optional | ❌ |
| Fabric 1.0 | ✅ Required | ✅ Required | ❌ | ❌ | ❌ |
| Fabric 1.0 Text | ✅ Required | ❌ | ❌ | ✅ Required | ❌ |
| Kling Ref-to-Video | ❌ | ⚪ Optional | ❌ | ✅ Prompt | ✅ 1-4 images |
| Kling V2V Reference | ❌ | ⚪ Optional | ✅ Required | ✅ Prompt | ❌ |
| Kling V2V Edit | ❌ | ❌ | ✅ Required | ✅ Prompt | ❌ |

---

## Model Selection Guide

| Use Case | Recommended Model | Why |
|----------|-------------------|-----|
| Realistic talking head | `omnihuman_v1_5` | Best quality, emotion correlation |
| Quick social media | `fabric_1_0_fast` | Fastest processing |
| No audio available | `fabric_1_0_text` | Built-in TTS |
| Budget-conscious | `fabric_1_0` (480p) | Lowest cost |
| Character consistency | `kling_ref_to_video` | Multi-reference support |
| Scene continuation | `kling_v2v_reference` | Preserves motion/style |
| Fix specific elements | `kling_v2v_edit` | Targeted modifications |

---

## Dependencies

No new dependencies required - uses existing:
- `fal-client` (already installed)
- `click` (already installed)
- `pydantic` (already installed)

---

## References

- [OmniHuman v1.5 API](https://fal.ai/models/fal-ai/bytedance/omnihuman/v1.5/api)
- [VEED Fabric 1.0 API](https://fal.ai/models/veed/fabric-1.0/api)
- [VEED Fabric 1.0 Text API](https://fal.ai/models/veed/fabric-1.0/text/api)
- [Kling O1 Reference-to-Video API](https://fal.ai/models/fal-ai/kling-video/o1/standard/reference-to-video/api)
- [Kling O1 Developer Guide](https://fal.ai/learn/devs/kling-o1-developer-guide)
- [Kling V2V Reference API](https://fal.ai/models/fal-ai/kling-video/o1/standard/video-to-video/reference/api)
- [Kling V2V Edit API](https://fal.ai/models/fal-ai/kling-video/o1/standard/video-to-video/edit/api)
- [Introducing Kling O1](https://blog.fal.ai/introducing-kling-o1-video-available-exclusively-as-an-api-on-fal/)
