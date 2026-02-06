# Fix Model Registration Sprawl: Centralized Registry ✅ COMPLETE

## Problem Statement

Adding one model currently requires **60-90 edits across 18+ files**. The Kling O3 commit touched 18 files with +2,873 lines. An LLM agent will inevitably miss one location, causing silent breakage (e.g., duration options `["5", "10", "12"]` when the API supports `3-15`).

**Root cause:** Model metadata is duplicated across 6 independent constants files, 4 generator files, 2 CLI files, and 4 `__init__.py` files -- with no validation that they stay in sync.

---

## Goal

Reduce "add one model" from **60-90 edits in 18+ files** to **2 edits in 2 files**:
1. Add entry to central registry
2. Create model class file

**Estimated total implementation time: 3-4 hours**

---

## Architecture Overview

```
BEFORE (Current):
  text-to-video/constants.py ---- 10 dicts per model (314 lines)
  image-to-video/constants.py --- 12 dicts per model (562 lines)
  avatar/constants.py ----------- 11 dicts per model (204 lines)
  video-to-video/constants.py --- 8 dicts per model (205 lines)
  image-to-image/constants.py --- 7 dicts per model (211 lines)
  ai_content_pipeline/constants.py -- 4 dicts per model (386 lines)
  + 4 generator.py files (MODEL_CLASSES dicts)
  + 2 cli.py files (hardcoded choices + if/elif chains)
  + 5 models/__init__.py files (imports + __all__)

AFTER (Proposed):
  packages/core/ai_content_pipeline/registry.py -- ONE dict per model
  packages/providers/fal/*/models/[model].py ----- model class (self-describing)
```

---

## Subtask 1: Create Central Model Registry ✅ DONE

**Time estimate:** 20 minutes
**New file:** `packages/core/ai_content_pipeline/ai_content_pipeline/registry.py`

### What to build

A single Python module that is the **sole source of truth** for all model metadata:

```python
# registry.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class ModelDefinition:
    """Single source of truth for one model."""
    key: str                          # "kling_3_standard"
    name: str                         # "Kling Video v3 Standard"
    provider: str                     # "Kuaishou"
    endpoint: str                     # "fal-ai/kling-video/v3/standard/text-to-video"
    categories: List[str]             # ["text_to_video", "image_to_video"]
    description: str                  # Human-readable description
    pricing: Dict[str, Any]           # {"no_audio": 0.168, "audio": 0.252} or float
    duration_options: List[Any]       # [3, 4, 5, ..., 15] or ["5s", "6s"]
    aspect_ratios: List[str]          # ["16:9", "9:16", "1:1"]
    resolutions: List[str] = field(default_factory=lambda: ["720p"])
    defaults: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    max_duration: int = 15
    extended_params: List[str] = field(default_factory=list)
    extended_features: Dict[str, bool] = field(default_factory=dict)
    input_requirements: Dict[str, List[str]] = field(default_factory=dict)
    model_info: Dict[str, Any] = field(default_factory=dict)
    cost_estimate: float = 0.0       # Default pipeline cost estimate (USD)
    processing_time: int = 60        # Estimated processing time (seconds)


class ModelRegistry:
    """Central registry for all AI models."""
    _models: Dict[str, ModelDefinition] = {}

    @classmethod
    def register(cls, model: ModelDefinition):
        """Register a model definition."""
        cls._models[model.key] = model

    @classmethod
    def get(cls, key: str) -> ModelDefinition:
        """Get model by key. Raises ValueError if not found."""
        if key not in cls._models:
            available = list(cls._models.keys())
            raise ValueError(f"Unknown model: {key}. Available: {available}")
        return cls._models[key]

    @classmethod
    def list_by_category(cls, category: str) -> List[ModelDefinition]:
        """Get all models in a category."""
        return [m for m in cls._models.values() if category in m.categories]

    @classmethod
    def all_keys(cls) -> List[str]:
        """Get all registered model keys."""
        return list(cls._models.keys())

    @classmethod
    def keys_for_category(cls, category: str) -> List[str]:
        """Get model keys for a category."""
        return [m.key for m in cls._models.values() if category in m.categories]

    @classmethod
    def get_supported_models(cls) -> Dict[str, List[str]]:
        """Get SUPPORTED_MODELS dict (category -> [keys])."""
        result: Dict[str, List[str]] = {}
        for m in cls._models.values():
            for cat in m.categories:
                result.setdefault(cat, []).append(m.key)
        return result

    @classmethod
    def get_cost_estimates(cls) -> Dict[str, Dict[str, float]]:
        """Get COST_ESTIMATES dict (category -> {key: cost})."""
        result: Dict[str, Dict[str, float]] = {}
        for m in cls._models.values():
            for cat in m.categories:
                result.setdefault(cat, {})[m.key] = m.cost_estimate
        return result

    @classmethod
    def get_processing_times(cls) -> Dict[str, Dict[str, int]]:
        """Get PROCESSING_TIME_ESTIMATES dict (category -> {key: seconds})."""
        result: Dict[str, Dict[str, int]] = {}
        for m in cls._models.values():
            for cat in m.categories:
                result.setdefault(cat, {})[m.key] = m.processing_time
        return result
```

### Test file
**New file:** `tests/test_registry.py`

```python
import pytest
from ai_content_pipeline.registry import ModelDefinition, ModelRegistry


def test_register_and_get():
    """Register a model and retrieve it by key."""
    model = ModelDefinition(
        key="test_model", name="Test", provider="Test",
        endpoint="test/endpoint", categories=["test"],
        description="Test model", pricing={"base": 0.1},
        duration_options=[5, 10], aspect_ratios=["16:9"]
    )
    ModelRegistry.register(model)
    assert ModelRegistry.get("test_model").name == "Test"


def test_get_unknown_raises():
    """get() raises ValueError for unknown model."""
    with pytest.raises(ValueError, match="Unknown model"):
        ModelRegistry.get("nonexistent_model_xyz")


def test_list_by_category():
    """list_by_category returns correct models."""
    models = ModelRegistry.list_by_category("test")
    assert any(m.key == "test_model" for m in models)


def test_keys_for_category():
    """keys_for_category returns only matching keys."""
    keys = ModelRegistry.keys_for_category("test")
    assert "test_model" in keys


def test_duplicate_key_overwrites():
    """Duplicate key registration overwrites cleanly."""
    m1 = ModelDefinition(
        key="dup_test", name="V1", provider="Test",
        endpoint="v1", categories=["test"],
        description="V1", pricing={}, duration_options=[], aspect_ratios=[]
    )
    m2 = ModelDefinition(
        key="dup_test", name="V2", provider="Test",
        endpoint="v2", categories=["test"],
        description="V2", pricing={}, duration_options=[], aspect_ratios=[]
    )
    ModelRegistry.register(m1)
    ModelRegistry.register(m2)
    assert ModelRegistry.get("dup_test").name == "V2"
```

---

## Subtask 2: Populate Registry with All Existing Models ✅ DONE

**Time estimate:** 45 minutes
**New file:** `packages/core/ai_content_pipeline/ai_content_pipeline/registry_data.py`

### What to build

Migrate all model definitions from the 6 scattered constants files into one file. One `ModelDefinition(...)` call per model.

### Source files to extract data from

| Source File | Dicts to Extract | Line Range |
|---|---|---|
| `packages/providers/fal/text-to-video/.../constants.py` | `ModelType`, `SUPPORTED_MODELS`, `MODEL_ENDPOINTS`, `MODEL_DISPLAY_NAMES`, `MODEL_PRICING`, `DURATION_OPTIONS`, `RESOLUTION_OPTIONS`, `ASPECT_RATIO_OPTIONS`, `DEFAULT_VALUES`, `MODEL_INFO` | Lines 1-313 |
| `packages/providers/fal/image-to-video/.../constants.py` | Same 10 dicts + `MODEL_EXTENDED_FEATURES`, `EXTENDED_PARAM_MAPPING` | Lines 1-562 |
| `packages/providers/fal/avatar-generation/.../constants.py` | `MODEL_ENDPOINTS`, `MODEL_DISPLAY_NAMES`, `MODEL_PRICING`, `MODEL_DEFAULTS`, `SUPPORTED_RESOLUTIONS`, `SUPPORTED_ASPECT_RATIOS`, `MAX_DURATIONS`, `PROCESSING_TIME_ESTIMATES`, `INPUT_REQUIREMENTS`, `MODEL_CATEGORIES`, `MODEL_RECOMMENDATIONS` | Lines 1-204 |
| `packages/providers/fal/video-to-video/.../constants.py` | `ModelType`, `SUPPORTED_MODELS`, `MODEL_ENDPOINTS`, `MODEL_DISPLAY_NAMES`, `MODEL_INFO`, `DEFAULT_VALUES`, `DURATION_OPTIONS`, `ASPECT_RATIO_OPTIONS` | Lines 1-205 |
| `packages/providers/fal/image-to-image/.../constants.py` | `ModelType`, `SUPPORTED_MODELS`, `MODEL_ENDPOINTS`, `MODEL_DISPLAY_NAMES`, `DEFAULT_VALUES`, `MODEL_INFO` + various `*_ASPECT_RATIOS` | Lines 1-211 |
| `packages/core/ai_content_pipeline/.../config/constants.py` | `SUPPORTED_MODELS`, `COST_ESTIMATES`, `PROCESSING_TIME_ESTIMATES`, `MODEL_RECOMMENDATIONS` | Lines 6-354 |

### Example model entries (showing exact data migration)

```python
# registry_data.py
"""All model definitions for the central registry."""

from .registry import ModelDefinition, ModelRegistry


def register_all_models():
    """Register all models. Called once at import time."""

    # =========================================================================
    # TEXT-TO-VIDEO MODELS (10)
    # Source: packages/providers/fal/text-to-video/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="hailuo_pro",
        name="MiniMax Hailuo-02 Pro",
        provider="MiniMax",
        endpoint="fal-ai/minimax/hailuo-02/pro/text-to-video",
        categories=["text_to_video"],
        description="Cost-effective text-to-video with prompt optimization",
        pricing={"type": "per_video", "cost": 0.08},
        duration_options=["6"],
        aspect_ratios=["16:9"],
        resolutions=["1080p"],
        defaults={"prompt_optimizer": True},
        features=["prompt_optimizer", "1080p", "cost_effective"],
        max_duration=6,
        cost_estimate=0.08,
        processing_time=60,
    ))

    ModelRegistry.register(ModelDefinition(
        key="veo3",
        name="Google Veo 3",
        provider="Google (via FAL)",
        endpoint="fal-ai/veo3",
        categories=["text_to_video"],
        description="Premium quality with audio generation",
        pricing={"type": "per_second", "cost_no_audio": 0.50, "cost_with_audio": 0.75},
        duration_options=["5s", "6s", "7s", "8s"],
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p"],
        defaults={"duration": "8s", "aspect_ratio": "16:9", "generate_audio": True, "enhance_prompt": True},
        features=["audio_generation", "enhance_prompt", "negative_prompt", "seed_control"],
        max_duration=8,
        cost_estimate=4.00,
        processing_time=300,
    ))

    ModelRegistry.register(ModelDefinition(
        key="kling_3_standard",
        name="Kling Video v3 Standard",
        provider="Kuaishou",
        endpoint="fal-ai/kling-video/v3/standard/text-to-video",
        categories=["text_to_video"],
        description="Latest generation with native audio, voice control, and multi-prompt support",
        pricing={"type": "per_second", "cost_no_audio": 0.168, "cost_with_audio": 0.252, "cost_voice_control": 0.308},
        duration_options=[str(d) for d in range(3, 16)],  # 3-15 seconds
        aspect_ratios=["16:9", "9:16", "1:1"],
        resolutions=["720p"],
        defaults={
            "duration": "5", "aspect_ratio": "16:9", "negative_prompt": "blur, distort, and low quality",
            "cfg_scale": 0.5, "generate_audio": False, "voice_ids": [], "multi_prompt": [], "shot_type": None
        },
        features=["audio_generation", "voice_control", "multi_prompt", "shot_type", "negative_prompt", "cfg_scale", "multilingual"],
        max_duration=12,
        cost_estimate=0.84,   # 0.168 * 5
        processing_time=90,
    ))

    # ... (repeat for all 10 text-to-video models: veo3_fast, kling_2_6_pro,
    #      kling_3_pro, kling_o3_pro_t2v, sora_2, sora_2_pro, grok_imagine)

    # =========================================================================
    # IMAGE-TO-VIDEO MODELS (15)
    # Source: packages/providers/fal/image-to-video/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="hailuo",
        name="MiniMax Hailuo-02",
        provider="MiniMax",
        endpoint="fal-ai/minimax/hailuo-02/standard/image-to-video",
        categories=["image_to_video"],
        description="Standard image-to-video with prompt optimization",
        pricing=0.05,  # per second, simple float
        duration_options=["6", "10"],
        aspect_ratios=[],  # Not configurable
        resolutions=["768p"],
        defaults={"duration": "6", "prompt_optimizer": True},
        features=["prompt_optimizer"],
        max_duration=10,
        extended_params=["start_frame"],
        extended_features={"start_frame": True, "end_frame": False, "ref_images": False,
                          "audio_input": False, "audio_generate": False, "ref_video": False},
        cost_estimate=0.08,
        processing_time=60,
    ))

    # ... (repeat for all 15 image-to-video models)

    # =========================================================================
    # IMAGE-TO-IMAGE MODELS (8)
    # Source: packages/providers/fal/image-to-image/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="photon",
        name="Luma Photon Flash",
        provider="Luma AI",
        endpoint="fal-ai/luma-photon/flash/modify",
        categories=["image_to_image"],
        description="Creative, personalizable, and intelligent image modification model",
        pricing={"per_megapixel": 0.019},
        duration_options=[],  # N/A for images
        aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"],
        defaults={"strength": 0.8, "aspect_ratio": "1:1"},
        features=["Fast processing", "High-quality results", "Creative modifications"],
        cost_estimate=0.02,
        processing_time=8,
    ))

    # ... (repeat for all 8 image-to-image models)

    # =========================================================================
    # AVATAR MODELS (10)
    # Source: packages/providers/fal/avatar-generation/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="omnihuman_v1_5",
        name="OmniHuman v1.5 (ByteDance)",
        provider="ByteDance",
        endpoint="fal-ai/bytedance/omnihuman/v1.5",
        categories=["avatar"],
        description="High-quality audio-driven human animation",
        pricing={"per_second": 0.16},
        duration_options=[],  # Determined by audio length
        aspect_ratios=[],
        resolutions=["720p", "1080p"],
        defaults={"resolution": "1080p", "turbo_mode": False},
        features=["audio_driven", "high_quality"],
        max_duration=30,  # at 1080p
        input_requirements={"required": ["image_url", "audio_url"], "optional": ["prompt", "turbo_mode", "resolution"]},
        cost_estimate=0.80,
        processing_time=60,
    ))

    # ... (repeat for all 10 avatar models)

    # =========================================================================
    # VIDEO-TO-VIDEO MODELS (6)
    # Source: packages/providers/fal/video-to-video/.../config/constants.py
    # =========================================================================

    ModelRegistry.register(ModelDefinition(
        key="thinksound",
        name="ThinkSound",
        provider="FAL AI",
        endpoint="fal-ai/thinksound",
        categories=["add_audio"],
        description="AI-powered video audio generation that creates realistic sound effects",
        pricing={"per_second": 0.001},
        duration_options=[],  # Determined by input video
        aspect_ratios=[],
        defaults={"seed": None, "prompt": None},
        features=["Automatic sound effect generation", "Text prompt guidance", "Video context understanding"],
        max_duration=300,
        cost_estimate=0.05,
        processing_time=45,
    ))

    ModelRegistry.register(ModelDefinition(
        key="topaz",
        name="Topaz Video Upscale",
        provider="Topaz Labs (via FAL)",
        endpoint="fal-ai/topaz/upscale/video",
        categories=["upscale_video"],
        description="Professional-grade video upscaling with frame interpolation",
        pricing={"per_video": "commercial"},
        duration_options=[],
        aspect_ratios=[],
        defaults={"upscale_factor": 2, "target_fps": None},
        features=["Up to 4x upscaling", "Frame rate enhancement up to 120 FPS"],
        cost_estimate=1.50,
        processing_time=120,
    ))

    # ... (repeat for kling_o3_standard_edit, kling_o3_pro_edit,
    #      kling_o3_standard_v2v_ref, kling_o3_pro_v2v_ref)


# Auto-register on import
register_all_models()
```

### Test file
**New file:** `tests/test_registry_data.py`

```python
import pytest
from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # triggers registration


def test_total_model_count():
    """All models are registered (approximate, update as models are added)."""
    assert len(ModelRegistry.all_keys()) >= 50


def test_text_to_video_count():
    assert len(ModelRegistry.keys_for_category("text_to_video")) == 10


def test_image_to_video_count():
    assert len(ModelRegistry.keys_for_category("image_to_video")) == 15


def test_image_to_image_count():
    assert len(ModelRegistry.keys_for_category("image_to_image")) == 8


def test_avatar_count():
    assert len(ModelRegistry.keys_for_category("avatar")) == 10


def test_all_models_have_required_fields():
    for key in ModelRegistry.all_keys():
        m = ModelRegistry.get(key)
        assert m.key, f"{key}: missing key"
        assert m.name, f"{key}: missing name"
        assert m.endpoint, f"{key}: missing endpoint"
        assert m.categories, f"{key}: missing categories"


def test_no_duplicate_keys():
    keys = ModelRegistry.all_keys()
    assert len(keys) == len(set(keys))
```

---

## Subtask 3: Make Provider Constants Read from Registry ✅ DONE

**Time estimate:** 45 minutes

### What to change

Update each provider's `constants.py` to derive its dicts from the central registry instead of hardcoding. **Keep same variable names** for backward compat.

---

### File 1: `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py`

**Current** (314 lines): 10 hardcoded dicts - `ModelType`, `SUPPORTED_MODELS`, `MODEL_ENDPOINTS`, `MODEL_DISPLAY_NAMES`, `MODEL_PRICING`, `DURATION_OPTIONS`, `RESOLUTION_OPTIONS`, `ASPECT_RATIO_OPTIONS`, `DEFAULT_VALUES`, `MODEL_INFO`

**Replace entire file with:**

```python
"""
Constants and configuration for FAL Text-to-Video models.
Derived from central registry - DO NOT hardcode values here.
"""

from typing import Literal, List
from ai_content_pipeline.registry import ModelRegistry

# Ensure registry data is loaded
import ai_content_pipeline.registry_data  # noqa: F401

_CATEGORY = "text_to_video"
_models = ModelRegistry.list_by_category(_CATEGORY)

# Model type definitions (for type hints)
_model_keys = ModelRegistry.keys_for_category(_CATEGORY)
ModelType = Literal[tuple(_model_keys)]  # type: ignore

SUPPORTED_MODELS: List[str] = _model_keys

# Model endpoints
MODEL_ENDPOINTS = {m.key: m.endpoint for m in _models}

# Display names
MODEL_DISPLAY_NAMES = {m.key: m.name for m in _models}

# Pricing (USD) - preserves original nested dict structure
MODEL_PRICING = {m.key: m.pricing for m in _models}

# Duration options per model
DURATION_OPTIONS = {m.key: m.duration_options for m in _models}

# Resolution options per model
RESOLUTION_OPTIONS = {m.key: m.resolutions for m in _models}

# Aspect ratio options
ASPECT_RATIO_OPTIONS = {m.key: m.aspect_ratios for m in _models}

# Default values per model
DEFAULT_VALUES = {m.key: m.defaults for m in _models}

# Model info for documentation
MODEL_INFO = {m.key: m.model_info for m in _models}
```

**Lines deleted:** 1-313 (entire original content)
**Lines added:** ~35 lines (above)

---

### File 2: `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`

**Current** (562 lines): 12 hardcoded dicts including `MODEL_EXTENDED_FEATURES` and `EXTENDED_PARAM_MAPPING`

**Replace entire file with:**

```python
"""
Constants and configuration for FAL Image-to-Video models.
Derived from central registry - DO NOT hardcode values here.
"""

from typing import Literal, List
from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # noqa: F401

_CATEGORY = "image_to_video"
_models = ModelRegistry.list_by_category(_CATEGORY)
_model_keys = ModelRegistry.keys_for_category(_CATEGORY)

ModelType = Literal[tuple(_model_keys)]  # type: ignore
SUPPORTED_MODELS: List[str] = _model_keys
MODEL_ENDPOINTS = {m.key: m.endpoint for m in _models}
MODEL_DISPLAY_NAMES = {m.key: m.name for m in _models}
MODEL_PRICING = {m.key: m.pricing for m in _models}
DURATION_OPTIONS = {m.key: m.duration_options for m in _models}
RESOLUTION_OPTIONS = {m.key: m.resolutions for m in _models}
ASPECT_RATIO_OPTIONS = {m.key: m.aspect_ratios for m in _models if m.aspect_ratios}
DEFAULT_VALUES = {m.key: m.defaults for m in _models}
MODEL_INFO = {m.key: m.model_info for m in _models}

# Extended feature support - derived from registry
MODEL_EXTENDED_FEATURES = {m.key: m.extended_features for m in _models if m.extended_features}

# API parameter mapping for extended features (static, doesn't change per model)
EXTENDED_PARAM_MAPPING = {
    "start_frame": "image_url",
    "end_frame": {
        "kling_2_1": "tail_image_url",
        "kling_2_6_pro": "tail_image_url",
        "kling_3_standard": "end_image_url",
        "kling_3_pro": "end_image_url",
    },
    "audio_generate": "generate_audio",
}
```

**Lines deleted:** 1-562 (entire original content)
**Lines added:** ~40 lines

---

### File 3: `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py`

**Current** (204 lines): 11 hardcoded dicts

**Replace entire file with:**

```python
"""Constants for FAL avatar generation models. Derived from central registry."""

from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # noqa: F401

_CATEGORY = "avatar"
_models = ModelRegistry.list_by_category(_CATEGORY)

MODEL_ENDPOINTS = {m.key: m.endpoint for m in _models}
MODEL_DISPLAY_NAMES = {m.key: m.name for m in _models}
MODEL_PRICING = {m.key: m.pricing for m in _models}
MODEL_DEFAULTS = {m.key: m.defaults for m in _models}
SUPPORTED_RESOLUTIONS = {m.key: m.resolutions for m in _models}
SUPPORTED_ASPECT_RATIOS = {m.key: m.aspect_ratios for m in _models if m.aspect_ratios}
MAX_DURATIONS = {m.key: m.max_duration for m in _models}
PROCESSING_TIME_ESTIMATES = {m.key: m.processing_time for m in _models}
INPUT_REQUIREMENTS = {m.key: m.input_requirements for m in _models if m.input_requirements}

# Model categories (static grouping within avatar domain)
MODEL_CATEGORIES = {
    "avatar_lipsync": ["omnihuman_v1_5", "fabric_1_0", "fabric_1_0_fast", "fabric_1_0_text"],
    "reference_to_video": ["kling_ref_to_video"],
    "video_to_video": ["kling_v2v_reference", "kling_v2v_edit", "grok_video_edit"],
    "motion_transfer": ["kling_motion_control"],
    "conversational": ["multitalk"],
}

# Model recommendations (static)
MODEL_RECOMMENDATIONS = {
    "quality": "omnihuman_v1_5",
    "speed": "fabric_1_0_fast",
    "text_to_avatar": "fabric_1_0_text",
    "character_consistency": "kling_ref_to_video",
    "style_transfer": "kling_v2v_reference",
    "video_editing": "kling_v2v_edit",
    "motion_transfer": "kling_motion_control",
    "dance_video": "kling_motion_control",
    "cost_effective": "fabric_1_0",
    "conversation": "multitalk",
    "multi_person": "multitalk",
    "podcast": "multitalk",
    "colorize": "grok_video_edit",
    "video_transform": "grok_video_edit",
}
```

**Lines deleted:** 1-204
**Lines added:** ~45

---

### File 4: `packages/providers/fal/video-to-video/fal_video_to_video/config/constants.py`

**Current** (205 lines): 8 hardcoded dicts + file constants

**Replace lines 1-193 with registry lookups, keep lines 194-205 (file constants):**

```python
"""Constants and configuration for FAL Video to Video models. Derived from central registry."""

from typing import Dict, List, Literal
from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # noqa: F401

# Combine two categories since V2V has both add_audio and upscale models
_v2v_edit_models = ModelRegistry.list_by_category("video_to_video_edit")
_audio_models = ModelRegistry.list_by_category("add_audio")
_upscale_models = ModelRegistry.list_by_category("upscale_video")
_all_models = _audio_models + _upscale_models + _v2v_edit_models

_model_keys = [m.key for m in _all_models]

ModelType = Literal[tuple(_model_keys)]  # type: ignore
SUPPORTED_MODELS = _model_keys
MODEL_ENDPOINTS = {m.key: m.endpoint for m in _all_models}
MODEL_DISPLAY_NAMES = {m.key: m.name for m in _all_models}
MODEL_INFO = {m.key: m.model_info for m in _all_models}
DEFAULT_VALUES = {m.key: m.defaults for m in _all_models}
DURATION_OPTIONS = {m.key: m.duration_options for m in _all_models if m.duration_options}
ASPECT_RATIO_OPTIONS = {m.key: m.aspect_ratios for m in _all_models if m.aspect_ratios}

# File size limits (static)
MAX_VIDEO_SIZE_MB = 100
MAX_VIDEO_DURATION_SECONDS = 300

# Output settings (static)
DEFAULT_OUTPUT_FORMAT = "mp4"
VIDEO_CODECS = {
    "mp4": "libx264",
    "webm": "libvpx",
    "mov": "libx264"
}
```

**Lines deleted:** 1-193
**Lines added:** ~35

---

### File 5: `packages/providers/fal/image-to-image/fal_image_to_image/config/constants.py`

**Current** (211 lines): 7 hardcoded dicts + parameter ranges

**Replace model dicts with registry lookups, keep parameter range constants:**

```python
"""Constants and configuration for FAL Image-to-Image models. Derived from central registry."""

from typing import Dict, List, Literal
from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # noqa: F401

_CATEGORY = "image_to_image"
_models = ModelRegistry.list_by_category(_CATEGORY)
_model_keys = ModelRegistry.keys_for_category(_CATEGORY)

ModelType = Literal[tuple(_model_keys)]  # type: ignore
SUPPORTED_MODELS = _model_keys
MODEL_ENDPOINTS = {m.key: m.endpoint for m in _models}
MODEL_DISPLAY_NAMES = {m.key: m.name for m in _models}
DEFAULT_VALUES = {m.key: m.defaults for m in _models}
MODEL_INFO = {m.key: m.model_info for m in _models}

# Aspect ratios - derive from registry
ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]
KONTEXT_MULTI_ASPECT_RATIOS = ["21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21"]
NANO_BANANA_ASPECT_RATIOS = [
    "auto", "21:9", "16:9", "3:2", "4:3", "5:4",
    "1:1", "4:5", "3:4", "2:3", "9:16"
]

# Reframe endpoints (static, model-specific API feature)
REFRAME_ENDPOINTS = {
    "photon": "fal-ai/luma-photon/flash/reframe",
    "photon_base": "fal-ai/luma-photon/reframe"
}

# Resolution and format options (static)
RESOLUTIONS = ["1K", "2K", "4K"]
OUTPUT_FORMATS = ["jpeg", "png", "webp"]

# Parameter ranges (static validation constraints)
PHOTON_STRENGTH_RANGE = (0.0, 1.0)
KONTEXT_INFERENCE_STEPS_RANGE = (1, 50)
KONTEXT_GUIDANCE_SCALE_RANGE = (1.0, 20.0)
SEEDEDIT_GUIDANCE_SCALE_RANGE = (0.0, 1.0)
```

**Lines deleted:** 1-211
**Lines added:** ~42

---

### File 6: `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`

**Current** (386 lines): `SUPPORTED_MODELS` (lines 6-93), `MODEL_RECOMMENDATIONS` (lines 111-184), `COST_ESTIMATES` (lines 187-272), `PROCESSING_TIME_ESTIMATES` (lines 275-354), static config (lines 357-386)

**Replace lines 6-354 with registry lookups. Keep lines 357-386 (SUPPORTED_FORMATS, DEFAULT_CHAIN_CONFIG):**

```python
"""Configuration constants for AI Content Pipeline. Derived from central registry."""

from ai_content_pipeline.registry import ModelRegistry

import ai_content_pipeline.registry_data  # noqa: F401

# Supported models for each pipeline step
SUPPORTED_MODELS = ModelRegistry.get_supported_models()

# Pipeline step types (static)
PIPELINE_STEPS = [
    "text_to_image", "text_to_video", "image_understanding", "prompt_generation",
    "image_to_image", "image_to_video", "text_to_speech", "speech_to_text",
    "add_audio", "upscale_video", "avatar"
]

# Model recommendations based on use case (static - these are editorial choices)
MODEL_RECOMMENDATIONS = {
    "text_to_image": {
        "quality": "flux_dev", "speed": "flux_schnell", "cost_effective": "seedream_v3",
        "photorealistic": "imagen4", "high_resolution": "seedream3",
        "cinematic": "gen4", "reference_guided": "gen4"
    },
    "text_to_video": {
        "quality": "sora_2_pro", "speed": "veo3_fast", "cost_effective": "hailuo_pro",
        "balanced": "sora_2", "long_duration": "sora_2", "cinematic": "veo3", "1080p": "sora_2_pro"
    },
    # ... (keep all other recommendation categories unchanged)
}

# Cost estimates (USD) - derived from registry
COST_ESTIMATES = ModelRegistry.get_cost_estimates()

# Processing time estimates (seconds) - derived from registry
PROCESSING_TIME_ESTIMATES = ModelRegistry.get_processing_times()

# File format mappings (static)
SUPPORTED_FORMATS = {
    "image": [".jpg", ".jpeg", ".png", ".webp"],
    "video": [".mp4", ".mov", ".avi", ".webm"],
    "audio": [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
}

# Default configuration (static)
DEFAULT_CHAIN_CONFIG = {
    "steps": [
        {"type": "text_to_image", "model": "flux_dev", "params": {"aspect_ratio": "16:9", "style": "cinematic"}},
        {"type": "image_to_video", "model": "veo3", "params": {"duration": 8, "motion_level": "medium"}}
    ],
    "output_dir": "output",
    "temp_dir": "temp",
    "cleanup_temp": True
}
```

**Lines deleted:** 6-354 (model-specific dicts)
**Lines added:** ~50

### Test approach for Subtask 3
- Run existing tests: `python tests/test_core.py`
- No new tests needed -- existing tests validate the constants are correct
- Verify all imports still work by running: `python -c "from fal_text_to_video.config.constants import MODEL_ENDPOINTS; print(len(MODEL_ENDPOINTS))"`

---

## Subtask 4: Make CLI Dynamic (Remove Hardcoded Choices) ✅ DONE

**Time estimate:** 20 minutes

### File 1: `packages/providers/fal/text-to-video/fal_text_to_video/cli.py`

#### Change 1: Import registry (add at top, line 13)
```python
# ADD after line 13:
from ai_content_pipeline.registry import ModelRegistry
T2V_MODELS = ModelRegistry.keys_for_category("text_to_video")
```

#### Change 2: Replace `cmd_generate` if/elif chain (lines 29-64)

**DELETE lines 29-64:**
```python
    if args.model == "kling_2_6_pro":
        kwargs["duration"] = int(args.duration) if args.duration else 5
        kwargs["aspect_ratio"] = args.aspect_ratio
        kwargs["cfg_scale"] = args.cfg_scale
        kwargs["generate_audio"] = args.audio
        if args.negative_prompt:
            kwargs["negative_prompt"] = args.negative_prompt

    elif args.model in ["kling_3_standard", "kling_3_pro"]:
        # ... (36 lines total)
```

**REPLACE WITH:**
```python
    model_def = ModelRegistry.get(args.model)
    if args.duration:
        kwargs["duration"] = args.duration
    else:
        kwargs["duration"] = model_def.defaults.get("duration", "5")
    kwargs["aspect_ratio"] = args.aspect_ratio
    if hasattr(args, "cfg_scale") and args.cfg_scale is not None:
        kwargs["cfg_scale"] = args.cfg_scale
    if hasattr(args, "audio") and args.audio:
        kwargs["generate_audio"] = True
    if args.negative_prompt:
        kwargs["negative_prompt"] = args.negative_prompt
    if hasattr(args, "resolution") and args.resolution:
        kwargs["resolution"] = args.resolution
    if hasattr(args, "keep_remote") and args.keep_remote:
        kwargs["delete_video"] = False
```

#### Change 3: Replace `cmd_estimate_cost` if/elif chain (lines 142-161)

**DELETE lines 142-161** and **REPLACE WITH:**
```python
    model_def = ModelRegistry.get(args.model)
    if args.duration:
        kwargs["duration"] = args.duration
    else:
        kwargs["duration"] = model_def.defaults.get("duration", "5")
    if hasattr(args, "audio") and args.audio:
        kwargs["generate_audio"] = True
    if hasattr(args, "resolution") and args.resolution:
        kwargs["resolution"] = args.resolution
```

#### Change 4: Replace hardcoded choices in argparse (3 locations)

**Line 222-223** (generate command):
```python
# DELETE:
                           choices=["kling_2_6_pro", "kling_3_standard", "kling_3_pro",
                                   "kling_o3_pro_t2v", "sora_2", "sora_2_pro", "grok_imagine"],
# REPLACE WITH:
                           choices=T2V_MODELS,
```

**Line 252-253** (model-info command):
```python
# DELETE:
    info_parser.add_argument("model", choices=["kling_2_6_pro", "kling_3_standard", "kling_3_pro",
                                             "kling_o3_pro_t2v", "sora_2", "sora_2_pro", "grok_imagine"],
# REPLACE WITH:
    info_parser.add_argument("model", choices=T2V_MODELS,
```

**Lines 260-261** (estimate-cost command):
```python
# DELETE:
                            choices=["kling_2_6_pro", "kling_3_standard", "kling_3_pro",
                                    "kling_o3_pro_t2v", "sora_2", "sora_2_pro", "grok_imagine"],
# REPLACE WITH:
                            choices=T2V_MODELS,
```

---

### File 2: `packages/providers/fal/image-to-video/fal_image_to_video/cli.py`

#### Change 1: Import registry (add at top)
```python
from ai_content_pipeline.registry import ModelRegistry
I2V_MODELS = ModelRegistry.keys_for_category("image_to_video")
```

#### Change 2: Replace hardcoded choices (lines 188-194)
```python
# DELETE:
                           choices=["hailuo", "kling_2_1", "kling_2_6_pro",
                                   "kling_3_standard", "kling_3_pro",
                                   "kling_o3_standard_i2v", "kling_o3_pro_i2v",
                                   "kling_o3_standard_ref", "kling_o3_pro_ref",
                                   "seedance_1_5_pro", "sora_2", "sora_2_pro",
                                   "veo_3_1_fast", "wan_2_6", "grok_imagine"],
# REPLACE WITH:
                           choices=I2V_MODELS,
```

---

## Subtask 5: Make Model Classes Self-Describing ✅ DONE

**Time estimate:** 15 minutes

### File 1: `packages/providers/fal/text-to-video/fal_text_to_video/models/base.py`

**DELETE line 17:**
```python
from ..config.constants import MODEL_ENDPOINTS, MODEL_PRICING, MODEL_DISPLAY_NAMES
```

**REPLACE lines 28-41 with:**
```python
    def __init__(self, model_key: str):
        """
        Initialize the model.

        Args:
            model_key: Model identifier (e.g., "sora_2", "kling_2_6_pro")
        """
        from ai_content_pipeline.registry import ModelRegistry
        self.model_key = model_key
        self._definition = ModelRegistry.get(model_key)
        self.endpoint = self._definition.endpoint
        self.display_name = self._definition.name
        self.pricing = self._definition.pricing

        if not self.endpoint:
            raise ValueError(f"Unknown model: {model_key}")
```

---

### File 2: `packages/providers/fal/image-to-video/fal_image_to_video/models/base.py`

**DELETE line 10:**
```python
from ..config.constants import MODEL_ENDPOINTS, MODEL_DISPLAY_NAMES, MODEL_PRICING
```

**REPLACE lines 19-29 with:**
```python
    def __init__(self, model_key: str):
        """
        Initialize base model.

        Args:
            model_key: Model identifier (e.g., "hailuo", "sora_2")
        """
        from ai_content_pipeline.registry import ModelRegistry
        self.model_key = model_key
        self._definition = ModelRegistry.get(model_key)
        self.endpoint = self._definition.endpoint
        self.display_name = self._definition.name
        self.price_per_second = self._definition.pricing
```

---

### File 3: `packages/providers/fal/avatar-generation/fal_avatar/models/base.py`

**No import to remove** (avatar base doesn't import constants in `__init__`; subclasses set endpoint/pricing directly).

**MODIFY lines 34-46 to add registry fallback:**
```python
    def __init__(self, model_name: str):
        """
        Initialize the base avatar model.

        Args:
            model_name: Unique identifier for the model
        """
        from ai_content_pipeline.registry import ModelRegistry
        self.model_name = model_name
        try:
            self._definition = ModelRegistry.get(model_name)
            self.endpoint = self._definition.endpoint
            self.pricing = self._definition.pricing
            self.max_duration = self._definition.max_duration
            self.supported_resolutions = self._definition.resolutions
            self.supported_aspect_ratios = self._definition.aspect_ratios
        except ValueError:
            # Fallback for models not yet in registry
            self.endpoint = ""
            self.pricing: Dict[str, Any] = {}
            self.max_duration = 60
            self.supported_resolutions: List[str] = []
            self.supported_aspect_ratios: List[str] = []
```

---

### File 4: `packages/providers/fal/video-to-video/fal_video_to_video/models/base.py`

**DELETE line 11:**
```python
from ..config.constants import MODEL_ENDPOINTS, MODEL_DISPLAY_NAMES
```

**REPLACE lines 19-28 with:**
```python
    def __init__(self, model_key: str):
        """
        Initialize base model.

        Args:
            model_key: Model identifier (e.g., "thinksound")
        """
        from ai_content_pipeline.registry import ModelRegistry
        self.model_key = model_key
        self._definition = ModelRegistry.get(model_key)
        self.endpoint = self._definition.endpoint
        self.display_name = self._definition.name
```

---

### File 5: `packages/providers/fal/image-to-image/fal_image_to_image/models/base.py`

**DELETE line 11:**
```python
from ..config.constants import MODEL_ENDPOINTS, MODEL_DISPLAY_NAMES
```

**REPLACE lines 19-28 with:**
```python
    def __init__(self, model_key: str):
        """
        Initialize base model.

        Args:
            model_key: Model identifier (e.g., "photon", "seededit")
        """
        from ai_content_pipeline.registry import ModelRegistry
        self.model_key = model_key
        self._definition = ModelRegistry.get(model_key)
        self.endpoint = self._definition.endpoint
        self.display_name = self._definition.name
```

---

## Subtask 6: Auto-Discovery for Generator MODEL_CLASSES ✅ DONE

**Time estimate:** 20 minutes

### Step A: Add `MODEL_KEY` class attribute to all model classes

Each model class file needs ONE line added. The `MODEL_KEY` must match the key used in the registry.

#### Text-to-Video model files (4 files, 7 classes):

**`packages/providers/fal/text-to-video/fal_text_to_video/models/kling.py`** (3 classes):
```python
class Kling26ProModel(BaseTextToVideoModel):
    MODEL_KEY = "kling_2_6_pro"           # ADD THIS LINE

class KlingV3StandardModel(BaseTextToVideoModel):
    MODEL_KEY = "kling_3_standard"        # ADD THIS LINE

class KlingV3ProModel(BaseTextToVideoModel):
    MODEL_KEY = "kling_3_pro"             # ADD THIS LINE
```

**`packages/providers/fal/text-to-video/fal_text_to_video/models/kling_o3.py`** (1 class):
```python
class KlingO3ProT2VModel(BaseTextToVideoModel):
    MODEL_KEY = "kling_o3_pro_t2v"        # ADD THIS LINE
```

**`packages/providers/fal/text-to-video/fal_text_to_video/models/sora.py`** (2 classes):
```python
class Sora2Model(BaseTextToVideoModel):
    MODEL_KEY = "sora_2"                  # ADD THIS LINE

class Sora2ProModel(BaseTextToVideoModel):
    MODEL_KEY = "sora_2_pro"              # ADD THIS LINE
```

**`packages/providers/fal/text-to-video/fal_text_to_video/models/grok.py`** (1 class):
```python
class GrokImagineModel(BaseTextToVideoModel):
    MODEL_KEY = "grok_imagine"            # ADD THIS LINE
```

#### Image-to-Video model files (8 files, 15 classes):

**`packages/providers/fal/image-to-video/fal_image_to_video/models/hailuo.py`**: `MODEL_KEY = "hailuo"`
**`packages/providers/fal/image-to-video/fal_image_to_video/models/kling.py`**: `MODEL_KEY` for `KlingModel` = `"kling_2_1"`, `Kling26ProModel` = `"kling_2_6_pro"`, `KlingV3StandardModel` = `"kling_3_standard"`, `KlingV3ProModel` = `"kling_3_pro"`
**`packages/providers/fal/image-to-video/fal_image_to_video/models/kling_o3.py`**: `MODEL_KEY` for `KlingO3StandardI2VModel` = `"kling_o3_standard_i2v"`, `KlingO3ProI2VModel` = `"kling_o3_pro_i2v"`, `KlingO3StandardRefModel` = `"kling_o3_standard_ref"`, `KlingO3ProRefModel` = `"kling_o3_pro_ref"`
**`packages/providers/fal/image-to-video/fal_image_to_video/models/seedance.py`**: `MODEL_KEY = "seedance_1_5_pro"`
**`packages/providers/fal/image-to-video/fal_image_to_video/models/sora.py`**: `Sora2Model.MODEL_KEY = "sora_2"`, `Sora2ProModel.MODEL_KEY = "sora_2_pro"`
**`packages/providers/fal/image-to-video/fal_image_to_video/models/veo.py`**: `MODEL_KEY = "veo_3_1_fast"`
**`packages/providers/fal/image-to-video/fal_image_to_video/models/wan.py`**: `MODEL_KEY = "wan_2_6"`
**`packages/providers/fal/image-to-video/fal_image_to_video/models/grok.py`**: `MODEL_KEY = "grok_imagine"`

#### Avatar model files (5 files, 10 classes):

**`packages/providers/fal/avatar-generation/fal_avatar/models/omnihuman.py`**: `MODEL_KEY = "omnihuman_v1_5"`
**`packages/providers/fal/avatar-generation/fal_avatar/models/fabric.py`**: `FabricModel.MODEL_KEY = "fabric_1_0"` (and `fabric_1_0_fast` variant), `FabricTextModel.MODEL_KEY = "fabric_1_0_text"`
**`packages/providers/fal/avatar-generation/fal_avatar/models/kling.py`**: 4 classes: `kling_ref_to_video`, `kling_v2v_reference`, `kling_v2v_edit`, `kling_motion_control`
**`packages/providers/fal/avatar-generation/fal_avatar/models/multitalk.py`**: `MODEL_KEY = "multitalk"`
**`packages/providers/fal/avatar-generation/fal_avatar/models/grok.py`**: `MODEL_KEY = "grok_video_edit"`

#### Video-to-Video model files (3 files, 6 classes):

**`packages/providers/fal/video-to-video/fal_video_to_video/models/thinksound.py`**: `MODEL_KEY = "thinksound"`
**`packages/providers/fal/video-to-video/fal_video_to_video/models/topaz.py`**: `MODEL_KEY = "topaz"`
**`packages/providers/fal/video-to-video/fal_video_to_video/models/kling_o3.py`**: 4 classes: `kling_o3_standard_edit`, `kling_o3_pro_edit`, `kling_o3_standard_v2v_ref`, `kling_o3_pro_v2v_ref`

#### Image-to-Image model files (6 files, 8 classes):

**`packages/providers/fal/image-to-image/fal_image_to_image/models/photon.py`**: `PhotonModel.MODEL_KEY = "photon"`, `PhotonBaseModel.MODEL_KEY = "photon_base"`
**`packages/providers/fal/image-to-image/fal_image_to_image/models/kontext.py`**: `KontextModel.MODEL_KEY = "kontext"`, `KontextMultiModel.MODEL_KEY = "kontext_multi"`
**`packages/providers/fal/image-to-image/fal_image_to_image/models/seededit.py`**: `MODEL_KEY = "seededit"`
**`packages/providers/fal/image-to-image/fal_image_to_image/models/clarity.py`**: `MODEL_KEY = "clarity"`
**`packages/providers/fal/image-to-image/fal_image_to_image/models/nano_banana.py`**: `MODEL_KEY = "nano_banana_pro_edit"`
**`packages/providers/fal/image-to-image/fal_image_to_image/models/gpt_image.py`**: `MODEL_KEY = "gpt_image_1_5_edit"`

### Step B: Update generator files to use auto-discovery

#### `packages/providers/fal/text-to-video/fal_text_to_video/generator.py`

**DELETE lines 16-38:**
```python
from .models import (
    BaseTextToVideoModel,
    Kling26ProModel,
    KlingV3StandardModel,
    KlingV3ProModel,
    KlingO3ProT2VModel,
    Sora2Model,
    Sora2ProModel,
    GrokImagineModel
)
from .config import SUPPORTED_MODELS, MODEL_INFO

# Model class registry
MODEL_CLASSES: Dict[str, Type[BaseTextToVideoModel]] = {
    "kling_2_6_pro": Kling26ProModel,
    "kling_3_standard": KlingV3StandardModel,
    "kling_3_pro": KlingV3ProModel,
    "kling_o3_pro_t2v": KlingO3ProT2VModel,
    "sora_2": Sora2Model,
    "sora_2_pro": Sora2ProModel,
    "grok_imagine": GrokImagineModel
}
```

**REPLACE WITH:**
```python
from .models import BaseTextToVideoModel
from .config import SUPPORTED_MODELS, MODEL_INFO
from ai_content_pipeline.registry import ModelRegistry


def _build_model_classes():
    """Auto-discover model classes by MODEL_KEY attribute."""
    from . import models as models_pkg
    classes = {}
    for name in dir(models_pkg):
        cls = getattr(models_pkg, name)
        if (isinstance(cls, type)
                and issubclass(cls, BaseTextToVideoModel)
                and cls is not BaseTextToVideoModel
                and hasattr(cls, 'MODEL_KEY')):
            classes[cls.MODEL_KEY] = cls
    return classes


MODEL_CLASSES = _build_model_classes()
```

#### `packages/providers/fal/image-to-video/fal_image_to_video/generator.py`

**DELETE lines 12-28** (import block) and **lines 83-99** (`self.models = { ... }`)

**REPLACE import block with:**
```python
from .models import BaseVideoModel
from .models import *  # noqa: F401,F403 - Import all for MODEL_KEY scanning


def _build_models():
    """Auto-discover and instantiate model classes by MODEL_KEY attribute."""
    from . import models as models_pkg
    from .models.base import BaseVideoModel
    instances = {}
    for name in dir(models_pkg):
        cls = getattr(models_pkg, name)
        if (isinstance(cls, type)
                and issubclass(cls, BaseVideoModel)
                and cls is not BaseVideoModel
                and hasattr(cls, 'MODEL_KEY')):
            instances[cls.MODEL_KEY] = cls()
    return instances
```

**REPLACE `self.models = {...}` in `__init__` with:**
```python
        self.models = _build_models()
```

#### `packages/providers/fal/avatar-generation/fal_avatar/generator.py`

**DELETE lines 5-17** (explicit model imports in the import block)

**REPLACE `self.models = {...}` in `__init__` (lines 44-55) with auto-discovery:**
```python
        # Auto-discover models
        from . import models as models_pkg
        from .models.base import BaseAvatarModel
        self.models: Dict[str, BaseAvatarModel] = {}
        for name in dir(models_pkg):
            cls = getattr(models_pkg, name)
            if (isinstance(cls, type)
                    and issubclass(cls, BaseAvatarModel)
                    and cls is not BaseAvatarModel
                    and hasattr(cls, 'MODEL_KEY')):
                self.models[cls.MODEL_KEY] = cls()
```

**Note:** `FabricModel` has `fast=False` and `fast=True` variants. This needs special handling -- either two MODEL_KEYs or a factory pattern. Simplest: make `FabricFastModel` a separate class with `MODEL_KEY = "fabric_1_0_fast"`.

#### `packages/providers/fal/video-to-video/fal_video_to_video/generator.py`

**DELETE lines 10-18** (explicit model imports) and **lines 52-59** (`self.models = {...}`)

**REPLACE with auto-discovery using same pattern as above.**

### Test file
**New file:** `tests/test_auto_discovery.py`

```python
import pytest
from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # noqa


def test_all_t2v_models_have_class():
    """All registered text-to-video models have a corresponding class."""
    from fal_text_to_video.generator import MODEL_CLASSES
    for key in ModelRegistry.keys_for_category("text_to_video"):
        assert key in MODEL_CLASSES, f"Missing class for {key}"


def test_model_key_matches_registry():
    """MODEL_KEY attribute matches registry key."""
    from fal_text_to_video.generator import MODEL_CLASSES
    for key, cls in MODEL_CLASSES.items():
        assert cls.MODEL_KEY == key


def test_generator_instantiates_all():
    """Generator can instantiate all discovered models."""
    from fal_text_to_video.generator import MODEL_CLASSES
    for key, cls in MODEL_CLASSES.items():
        instance = cls()
        assert instance.model_key == key
```

---

## Subtask 7: Validation Script (Guard Against Drift) ✅ DONE

**Time estimate:** 15 minutes
**New file:** `scripts/validate_registry.py`

```python
#!/usr/bin/env python3
"""Validate model registry consistency.

Run: python scripts/validate_registry.py
Exit code 0 = all validations passed.
"""

import sys


def validate():
    """Run all validation checks."""
    errors = []

    from ai_content_pipeline.registry import ModelRegistry
    import ai_content_pipeline.registry_data  # noqa

    all_keys = ModelRegistry.all_keys()

    # 1. Check minimum model count
    if len(all_keys) < 50:
        errors.append(f"Expected 50+ models, found {len(all_keys)}")

    # 2. Every model has required fields
    for key in all_keys:
        m = ModelRegistry.get(key)
        if not m.name:
            errors.append(f"{key}: missing name")
        if not m.endpoint:
            errors.append(f"{key}: missing endpoint")
        if not m.categories:
            errors.append(f"{key}: missing categories")

    # 3. All endpoints are valid FAL/xai URLs
    for key in all_keys:
        m = ModelRegistry.get(key)
        if m.endpoint and not (
            m.endpoint.startswith("fal-ai/")
            or m.endpoint.startswith("veed/")
            or m.endpoint.startswith("xai/")
            or m.endpoint.startswith("wan/")
        ):
            errors.append(f"{key}: endpoint '{m.endpoint}' has unexpected prefix")

    # 4. No duplicate keys
    if len(all_keys) != len(set(all_keys)):
        errors.append("Duplicate model keys detected")

    # 5. Check model classes exist for all registered models
    try:
        from fal_text_to_video.generator import MODEL_CLASSES as t2v_classes
        for key in ModelRegistry.keys_for_category("text_to_video"):
            if key not in t2v_classes:
                errors.append(f"text_to_video model '{key}' has no class in generator.py")
    except ImportError:
        errors.append("Could not import fal_text_to_video.generator")

    # Report
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  ERROR: {e}")
        return 1

    print(f"All validations passed! ({len(all_keys)} models registered)")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
```

---

## Implementation Order & Dependencies

```
Subtask 1: Create Registry (20 min) ------+
                                           |
Subtask 2: Populate Registry (45 min) -----+ (depends on 1)
                                           |
         +-------- depends on 2 ----------+
         |                                 |
Subtask 3: Provider Constants (45 min)     |
         |                                 |
         +-- Subtask 4: Dynamic CLI (20 min)   (depends on 3)
         |
         +-- Subtask 5: Self-Describing Models (15 min)  (depends on 3)
         |
         +-- Subtask 6: Auto-Discovery (20 min)  (depends on 5)

Subtask 7: Validation Script (15 min)  (depends on all above)
```

**Total: ~3 hours**

---

## Impact After Implementation

| Metric | Before | After |
|---|---|---|
| Files to edit for new model | 18+ files | 2 files |
| Locations to edit | 60-90 | 2 (registry entry + model class) |
| Risk of missed edit | High | Near zero (validation script catches) |
| Duration type inconsistency | `int` vs `str` per model | Consistent (model class handles) |
| CLI choices sync | Manual, 3-4 copies | Auto-generated from registry |
| Cross-package model discovery | Not possible | `ModelRegistry.list_by_category()` |

---

## Backward Compatibility Strategy

- **Phase 1 (Subtasks 1-2):** Registry exists alongside old constants. No breaking changes.
- **Phase 2 (Subtask 3):** Provider constants derive from registry. Same variable names exported. All imports still work.
- **Phase 3 (Subtasks 4-6):** CLI and generators use registry. Old hardcoded lists removed.
- **Phase 4 (Subtask 7):** Validation enforces consistency going forward.

Each phase can be merged independently. If any subtask causes issues, the previous phase still works.

---

## Files Summary

### New files (5)
| File | Purpose |
|---|---|
| `packages/core/ai_content_pipeline/ai_content_pipeline/registry.py` | `ModelDefinition` dataclass + `ModelRegistry` class |
| `packages/core/ai_content_pipeline/ai_content_pipeline/registry_data.py` | All ~55 model definitions |
| `scripts/validate_registry.py` | Consistency validation script |
| `tests/test_registry.py` | Unit tests for registry core |
| `tests/test_registry_data.py` | Tests for registry data completeness |

### Modified files: Provider constants (6 files)
| File | Lines Deleted | Lines Added | Change |
|---|---|---|---|
| `packages/providers/fal/text-to-video/.../config/constants.py` | 314 | ~35 | Derive all 10 dicts from registry |
| `packages/providers/fal/image-to-video/.../config/constants.py` | 562 | ~40 | Derive all 12 dicts from registry |
| `packages/providers/fal/avatar-generation/.../config/constants.py` | 204 | ~45 | Derive all 11 dicts from registry |
| `packages/providers/fal/video-to-video/.../config/constants.py` | 193 | ~35 | Derive all 8 dicts from registry |
| `packages/providers/fal/image-to-image/.../config/constants.py` | 211 | ~42 | Derive model dicts, keep param ranges |
| `packages/core/ai_content_pipeline/.../config/constants.py` | 349 | ~50 | Derive SUPPORTED_MODELS, COST_ESTIMATES, PROCESSING_TIME |

### Modified files: Base model classes (5 files)
| File | Change |
|---|---|
| `packages/providers/fal/text-to-video/.../models/base.py` | Delete constants import (line 17), replace `__init__` (lines 28-41) with registry lookup |
| `packages/providers/fal/image-to-video/.../models/base.py` | Delete constants import (line 10), replace `__init__` (lines 19-29) with registry lookup |
| `packages/providers/fal/avatar-generation/.../models/base.py` | Add registry lookup in `__init__` (lines 34-46) with fallback |
| `packages/providers/fal/video-to-video/.../models/base.py` | Delete constants import (line 11), replace `__init__` (lines 19-28) with registry lookup |
| `packages/providers/fal/image-to-image/.../models/base.py` | Delete constants import (line 11), replace `__init__` (lines 19-28) with registry lookup |

### Modified files: CLIs (2 files)
| File | Change |
|---|---|
| `packages/providers/fal/text-to-video/.../cli.py` | Add registry import, replace 3x hardcoded `choices=[]` lists, replace 2x if/elif chains (lines 29-64, 142-161) |
| `packages/providers/fal/image-to-video/.../cli.py` | Add registry import, replace hardcoded `choices=[]` list (lines 188-194) |

### Modified files: Generators (4 files)
| File | Change |
|---|---|
| `packages/providers/fal/text-to-video/.../generator.py` | Replace explicit imports + `MODEL_CLASSES` dict (lines 16-38) with auto-discovery |
| `packages/providers/fal/image-to-video/.../generator.py` | Replace explicit imports (lines 12-28) + `self.models` dict (lines 83-99) with auto-discovery |
| `packages/providers/fal/avatar-generation/.../generator.py` | Replace explicit imports (lines 5-17) + `self.models` dict (lines 44-55) with auto-discovery |
| `packages/providers/fal/video-to-video/.../generator.py` | Replace explicit imports (lines 10-18) + `self.models` dict (lines 52-59) with auto-discovery |

### Model files to add `MODEL_KEY` attribute (~26 files, ~46 classes)
| Directory | Files | Classes |
|---|---|---|
| `text-to-video/models/` | `kling.py`, `kling_o3.py`, `sora.py`, `grok.py` | 7 classes |
| `image-to-video/models/` | `hailuo.py`, `kling.py`, `kling_o3.py`, `seedance.py`, `sora.py`, `veo.py`, `wan.py`, `grok.py` | 15 classes |
| `avatar-generation/models/` | `omnihuman.py`, `fabric.py`, `kling.py`, `multitalk.py`, `grok.py` | 10 classes |
| `video-to-video/models/` | `thinksound.py`, `topaz.py`, `kling_o3.py` | 6 classes |
| `image-to-image/models/` | `photon.py`, `kontext.py`, `seededit.py`, `clarity.py`, `nano_banana.py`, `gpt_image.py` | 8 classes |

**Total: 5 new + 17 modified + ~26 model files with `MODEL_KEY` = ~48 files touched**
