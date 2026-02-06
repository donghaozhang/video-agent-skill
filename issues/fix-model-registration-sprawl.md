# Fix Model Registration Sprawl: Centralized Registry

## Problem Statement

Adding one model currently requires **60-90 edits across 18+ files**. The Kling O3 commit touched 18 files with +2,873 lines. An LLM agent will inevitably miss one location, causing silent breakage (e.g., duration options `["5", "10", "12"]` when the API supports `3-15`).

**Root cause:** Model metadata is duplicated across 6 independent constants files, 4 generator files, 2 CLI files, and 4 `__init__.py` files — with no validation that they stay in sync.

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
  text-to-video/constants.py ──── 10 dicts per model
  image-to-video/constants.py ─── 12 dicts per model
  avatar/constants.py ──────────── 11 dicts per model
  video-to-video/constants.py ─── 8 dicts per model
  ai_content_pipeline/constants.py ── 4 dicts per model
  + 4 generator.py files (MODEL_CLASSES dicts)
  + 2 cli.py files (hardcoded choices + if/elif chains)
  + 4 models/__init__.py files (imports + __all__)

AFTER (Proposed):
  packages/core/ai_content_pipeline/registry.py ── ONE dict per model
  packages/providers/fal/*/models/[model].py ───── model class (self-describing)
```

---

## Subtask 1: Create Central Model Registry

**Time estimate:** 45 minutes
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
    pricing: Dict[str, float]         # {"no_audio": 0.168, "audio": 0.252}
    duration_options: List[int]       # [3, 4, 5, ..., 15]
    aspect_ratios: List[str]          # ["16:9", "9:16", "1:1"]
    resolutions: List[str] = field(default_factory=lambda: ["720p"])
    defaults: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    max_duration: int = 15
    extended_params: List[str] = field(default_factory=list)
    input_requirements: Dict[str, List[str]] = field(default_factory=dict)


class ModelRegistry:
    """Central registry for all AI models."""
    _models: Dict[str, ModelDefinition] = {}

    @classmethod
    def register(cls, model: ModelDefinition):
        cls._models[model.key] = model

    @classmethod
    def get(cls, key: str) -> ModelDefinition:
        if key not in cls._models:
            available = list(cls._models.keys())
            raise ValueError(f"Unknown model: {key}. Available: {available}")
        return cls._models[key]

    @classmethod
    def list_by_category(cls, category: str) -> List[ModelDefinition]:
        return [m for m in cls._models.values() if category in m.categories]

    @classmethod
    def all_keys(cls) -> List[str]:
        return list(cls._models.keys())

    @classmethod
    def keys_for_category(cls, category: str) -> List[str]:
        return [m.key for m in cls._models.values() if category in m.categories]
```

### Relevant existing files to understand
- `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py` (lines 6-93: SUPPORTED_MODELS, lines 187-272: COST_ESTIMATES)
- `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py` (all 10 dicts)
- `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py` (all 12 dicts)

### Test file
**New file:** `tests/test_registry.py`

```python
# Tests:
# 1. Register a model and retrieve it by key
# 2. list_by_category returns correct models
# 3. get() raises ValueError for unknown model
# 4. keys_for_category returns only matching keys
# 5. Duplicate key registration overwrites cleanly
```

---

## Subtask 2: Populate Registry with All Existing Models

**Time estimate:** 60 minutes
**New file:** `packages/core/ai_content_pipeline/ai_content_pipeline/registry_data.py`

### What to build

Migrate all model definitions from the 6 scattered constants files into one file. This is the data layer — one `ModelDefinition(...)` per model.

### Models to migrate (53 total)

**Text-to-Image (8 models):**
- Source: `packages/providers/fal/text-to-image/fal_text_to_image/config/constants.py`
- Models: flux_dev, flux_schnell, imagen4, seedream_v3, seedream3, gen4, nano_banana_pro, gpt_image_1_5

**Text-to-Video (10 models):**
- Source: `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py`
- Models: hailuo_pro, veo3, veo3_fast, kling_2_6_pro, kling_3_standard, kling_3_pro, kling_o3_pro_t2v, sora_2, sora_2_pro, grok_imagine

**Image-to-Image (8 models):**
- Source: `packages/providers/fal/image-to-image/fal_image_to_image/config/constants.py`
- Models: photon, photon_base, kontext, kontext_multi, seededit, clarity, nano_banana_pro_edit, gpt_image_1_5_edit

**Image-to-Video (15 models):**
- Source: `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`
- Models: hailuo, kling_2_1, kling_2_6_pro, kling_3_standard, kling_3_pro, kling_o3_standard_i2v, kling_o3_pro_i2v, kling_o3_standard_ref, kling_o3_pro_ref, seedance_1_5_pro, sora_2, sora_2_pro, veo_3_1_fast, wan_2_6, grok_imagine

**Avatar Generation (10 models):**
- Source: `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py`
- Models: omnihuman_v1_5, fabric_1_0, fabric_1_0_fast, fabric_1_0_text, kling_ref_to_video, kling_v2v_reference, kling_v2v_edit, kling_motion_control, multitalk, grok_video_edit

**Video-to-Video (6 models):**
- Source: `packages/providers/fal/video-to-video/fal_video_to_video/config/constants.py`
- Models: thinksound, topaz, kling_o3_standard_edit, kling_o3_pro_edit, kling_o3_standard_v2v_ref, kling_o3_pro_v2v_ref

**Speech-to-Text (1 model):**
- Source: `packages/providers/fal/speech-to-text/fal_speech_to_text/config/constants.py`
- Models: scribe_v2

**Text-to-Speech (3 models):**
- Source: `packages/services/text-to-speech/` (if exists)
- Models: elevenlabs, elevenlabs_turbo, elevenlabs_v3

### Test file
**New file:** `tests/test_registry_data.py`

```python
# Tests:
# 1. All 53 models are registered
# 2. Each model has required fields (key, name, endpoint, categories, pricing)
# 3. No duplicate keys
# 4. Category counts match expected (8 text-to-image, 10 text-to-video, etc.)
# 5. Pricing values are positive numbers
```

---

## Subtask 3: Make Provider Constants Read from Registry

**Time estimate:** 45 minutes

### What to change

Update each provider's `constants.py` to derive its dicts from the central registry instead of hardcoding. This is the **backward-compatible bridge** — existing code keeps working while the source of truth moves.

### Files to modify

**File 1:** `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py`
- Replace 10 hardcoded dicts with registry lookups
- Keep same variable names (MODEL_ENDPOINTS, MODEL_DISPLAY_NAMES, etc.) for backward compat
- Example:
  ```python
  from ai_content_pipeline.registry import ModelRegistry

  _models = ModelRegistry.list_by_category("text_to_video")
  MODEL_ENDPOINTS = {m.key: m.endpoint for m in _models}
  MODEL_DISPLAY_NAMES = {m.key: m.name for m in _models}
  DURATION_OPTIONS = {m.key: [str(d) for d in m.duration_options] for m in _models}
  # ... etc
  ```

**File 2:** `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`
- Replace 12 hardcoded dicts with registry lookups

**File 3:** `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py`
- Replace 11 hardcoded dicts with registry lookups

**File 4:** `packages/providers/fal/video-to-video/fal_video_to_video/config/constants.py`
- Replace 8 hardcoded dicts with registry lookups

**File 5:** `packages/providers/fal/image-to-image/fal_image_to_image/config/constants.py`
- Replace dicts with registry lookups

**File 6:** `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`
- Replace SUPPORTED_MODELS, COST_ESTIMATES, PROCESSING_TIME_ESTIMATES with registry lookups

### Test approach
- Run existing tests (`python tests/test_core.py`) to verify backward compat
- No new tests needed — existing tests validate the constants are correct

---

## Subtask 4: Make CLI Dynamic (Remove Hardcoded Choices)

**Time estimate:** 30 minutes

### What to change

Replace hardcoded `choices=[]` lists and `if/elif` chains with registry-driven logic.

**File 1:** `packages/providers/fal/text-to-video/fal_text_to_video/cli.py`

Current (lines 222-224, repeated 3 times):
```python
choices=["kling_2_6_pro", "kling_3_standard", "kling_3_pro",
        "kling_o3_pro_t2v", "sora_2", "sora_2_pro", "grok_imagine"]
```

After:
```python
from ai_content_pipeline.registry import ModelRegistry

T2V_MODELS = ModelRegistry.keys_for_category("text_to_video")
# ...
choices=T2V_MODELS
```

Current (lines 29-64, `cmd_generate`):
```python
if args.model == "kling_2_6_pro":
    kwargs["duration"] = int(args.duration) if args.duration else 5
elif args.model in ["kling_3_standard", "kling_3_pro"]:
    kwargs["duration"] = args.duration if args.duration else "5"
# ... 6 more branches
```

After:
```python
def cmd_generate(args):
    model_def = ModelRegistry.get(args.model)
    kwargs = {}
    if args.duration:
        kwargs["duration"] = args.duration
    else:
        kwargs["duration"] = model_def.defaults.get("duration", "5")
    kwargs["aspect_ratio"] = args.aspect_ratio
    if hasattr(args, "audio") and args.audio:
        kwargs["generate_audio"] = True
    # Model class handles type conversion internally
```

Current (lines 142-161, `cmd_estimate_cost`): Same if/elif pattern — replace similarly.

**File 2:** `packages/providers/fal/image-to-video/fal_image_to_video/cli.py`
- Same pattern: replace hardcoded choices and if/elif with registry lookups

### Test file
**New file:** `tests/test_cli_dynamic.py`

```python
# Tests:
# 1. CLI choices match registry models for text-to-video
# 2. CLI choices match registry models for image-to-video
# 3. cmd_generate builds correct kwargs from registry defaults
# 4. Unknown model raises clean error
# 5. Duration type is always string (model class converts)
```

---

## Subtask 5: Make Model Classes Self-Describing

**Time estimate:** 30 minutes

### What to change

Update base model classes so they pull metadata from the registry instead of importing from constants.py. This means model classes become self-describing — they know their own capabilities.

**File 1:** `packages/providers/fal/text-to-video/fal_text_to_video/models/base.py`

Current (lines 28-41):
```python
def __init__(self, model_key: str):
    self.model_key = model_key
    self.endpoint = MODEL_ENDPOINTS.get(model_key, "")
    self.display_name = MODEL_DISPLAY_NAMES.get(model_key, model_key)
    self.pricing = MODEL_PRICING.get(model_key, {})
```

After:
```python
def __init__(self, model_key: str):
    from ai_content_pipeline.registry import ModelRegistry
    self.model_key = model_key
    self._definition = ModelRegistry.get(model_key)
    self.endpoint = self._definition.endpoint
    self.display_name = self._definition.name
    self.pricing = self._definition.pricing
```

**File 2:** `packages/providers/fal/image-to-video/fal_image_to_video/models/base.py`
- Same pattern

**File 3:** `packages/providers/fal/avatar-generation/fal_avatar/models/base.py`
- Same pattern (note: uses `model_name` instead of `model_key`)

**File 4:** `packages/providers/fal/video-to-video/fal_video_to_video/models/base.py`
- Same pattern

**File 5:** `packages/providers/fal/image-to-image/fal_image_to_image/models/base.py`
- Same pattern

### Test approach
- Run existing model unit tests to verify backward compat
- Existing tests in `tests/test_kling_v3.py`, `tests/test_kling_o3.py` etc. cover this

---

## Subtask 6: Auto-Discovery for Generator MODEL_CLASSES

**Time estimate:** 20 minutes

### What to change

Instead of hardcoding MODEL_CLASSES dicts in each generator, use a registration decorator or auto-import pattern.

**File 1:** `packages/providers/fal/text-to-video/fal_text_to_video/generator.py`

Current (lines 30-38):
```python
MODEL_CLASSES: Dict[str, Type[BaseTextToVideoModel]] = {
    "kling_2_6_pro": Kling26ProModel,
    "kling_3_standard": KlingV3StandardModel,
    "kling_3_pro": KlingV3ProModel,
    # ... manually maintained
}
```

After:
```python
from ai_content_pipeline.registry import ModelRegistry

def _build_model_classes():
    """Auto-build MODEL_CLASSES from models/__init__.py exports."""
    from . import models as models_pkg
    classes = {}
    for model_key in ModelRegistry.keys_for_category("text_to_video"):
        # Each model class sets cls.MODEL_KEY = "kling_3_standard"
        for name in dir(models_pkg):
            cls = getattr(models_pkg, name)
            if isinstance(cls, type) and hasattr(cls, 'MODEL_KEY') and cls.MODEL_KEY == model_key:
                classes[model_key] = cls
                break
    return classes

MODEL_CLASSES = _build_model_classes()
```

**Alternative (simpler):** Add `MODEL_KEY` class attribute to each model class and scan at import time. This approach requires adding one line to each existing model class but eliminates the generator dict entirely.

**Files to add MODEL_KEY attribute:**
- `packages/providers/fal/text-to-video/fal_text_to_video/models/kling.py` (3 classes)
- `packages/providers/fal/text-to-video/fal_text_to_video/models/kling_o3.py` (1 class)
- `packages/providers/fal/text-to-video/fal_text_to_video/models/sora.py` (2 classes)
- `packages/providers/fal/text-to-video/fal_text_to_video/models/grok.py` (1 class)
- Same pattern for image-to-video, avatar, video-to-video model files

**File 2:** `packages/providers/fal/image-to-video/fal_image_to_video/generator.py` — same pattern
**File 3:** `packages/providers/fal/avatar-generation/fal_avatar/generator.py` — same pattern
**File 4:** `packages/providers/fal/video-to-video/fal_video_to_video/generator.py` — same pattern

### Test file
**New file:** `tests/test_auto_discovery.py`

```python
# Tests:
# 1. All registered text-to-video models have a corresponding class
# 2. MODEL_KEY attribute matches registry key
# 3. No orphaned model classes (class exists but not in registry)
# 4. Generator can instantiate all discovered models
```

---

## Subtask 7: Validation Script (Guard Against Drift)

**Time estimate:** 15 minutes
**New file:** `scripts/validate_registry.py`

### What to build

A script that verifies the registry is complete and consistent. Run in CI or before commits.

```python
#!/usr/bin/env python3
"""Validate model registry consistency."""

def validate():
    errors = []

    # 1. Every model in registry has a model class
    # 2. Every model class has a registry entry
    # 3. All endpoints are valid FAL URLs
    # 4. All pricing values are positive
    # 5. Duration options are within valid ranges
    # 6. CLI choices match registry
    # 7. No duplicate model keys across categories

    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
        return 1

    print("All validations passed!")
    return 0
```

### Relevant files it validates
- `packages/core/ai_content_pipeline/ai_content_pipeline/registry.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/registry_data.py`
- All `models/__init__.py` files
- All `generator.py` files
- All `cli.py` files

### Test approach
- The script IS the test — run it and check exit code

---

## Implementation Order & Dependencies

```
Subtask 1: Create Registry ─────────────────┐
                                             │
Subtask 2: Populate Registry Data ───────────┤ (depends on 1)
                                             │
         ┌───────────────────────────────────┤
         │                                   │
Subtask 3: Provider Constants ◄──────────────┘ (depends on 2)
         │
         ├── Subtask 4: Dynamic CLI          (depends on 3)
         │
         ├── Subtask 5: Self-Describing Models (depends on 3)
         │
         └── Subtask 6: Auto-Discovery       (depends on 5)

Subtask 7: Validation Script                  (depends on all above)
```

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

### New files (4)
| File | Purpose |
|---|---|
| `packages/core/ai_content_pipeline/ai_content_pipeline/registry.py` | ModelDefinition + ModelRegistry classes |
| `packages/core/ai_content_pipeline/ai_content_pipeline/registry_data.py` | All 53 model definitions |
| `scripts/validate_registry.py` | Consistency validation script |
| `tests/test_registry.py` | Unit tests for registry |

### Modified files (12)
| File | Change |
|---|---|
| `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py` | Derive from registry |
| `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py` | Derive from registry |
| `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py` | Derive from registry |
| `packages/providers/fal/video-to-video/fal_video_to_video/config/constants.py` | Derive from registry |
| `packages/providers/fal/image-to-image/fal_image_to_image/config/constants.py` | Derive from registry |
| `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py` | Derive from registry |
| `packages/providers/fal/text-to-video/fal_text_to_video/cli.py` | Dynamic choices, remove if/elif |
| `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` | Dynamic choices |
| `packages/providers/fal/text-to-video/fal_text_to_video/generator.py` | Auto-discovery |
| `packages/providers/fal/image-to-video/fal_image_to_video/generator.py` | Auto-discovery |
| `packages/providers/fal/avatar-generation/fal_avatar/generator.py` | Auto-discovery |
| `packages/providers/fal/video-to-video/fal_video_to_video/generator.py` | Auto-discovery |

### Model files to add MODEL_KEY attribute (~15 files)
| Directory | Files |
|---|---|
| `packages/providers/fal/text-to-video/fal_text_to_video/models/` | kling.py, kling_o3.py, sora.py, grok.py |
| `packages/providers/fal/image-to-video/fal_image_to_video/models/` | hailuo.py, kling.py, kling_o3.py, seedance.py, sora.py, veo.py, wan.py, grok.py |
| `packages/providers/fal/avatar-generation/fal_avatar/models/` | omnihuman.py, fabric.py, kling.py, multitalk.py, grok.py |
| `packages/providers/fal/video-to-video/fal_video_to_video/models/` | thinksound.py, topaz.py, kling_o3.py |
