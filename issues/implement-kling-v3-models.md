# Implement Kling Video v3 Models (Pro & Standard)

## Overview

Add support for **4 new Kling v3 video models** from FAL AI:
- Kling v3 Pro Image-to-Video
- Kling v3 Pro Text-to-Video
- Kling v3 Standard Image-to-Video
- Kling v3 Standard Text-to-Video

**Kling 3.0** is the latest generation with:
- Cinematic visuals and fluid motion
- **Native audio generation** (new feature)
- **Voice control** support (new feature)
- **Multi-prompt** support for complex sequences
- **Custom elements/characters** with reference images
- Extended duration support (up to 12+ seconds)

---

## API Details

### Endpoints

| Model | FAL Endpoint |
|-------|--------------|
| Kling v3 Pro Image-to-Video | `fal-ai/kling-video/v3/pro/image-to-video` |
| Kling v3 Pro Text-to-Video | `fal-ai/kling-video/v3/pro/text-to-video` |
| Kling v3 Standard Image-to-Video | `fal-ai/kling-video/v3/standard/image-to-video` |
| Kling v3 Standard Text-to-Video | `fal-ai/kling-video/v3/standard/text-to-video` |

### Pricing (per second of video)

| Model | Audio Off | Audio On | Voice Control |
|-------|-----------|----------|---------------|
| **Pro** | $0.224 | $0.336 | $0.392 |
| **Standard** | $0.168 | $0.252 | $0.308 |

*Example: 5-second Pro video with audio + voice control = $1.96*

### Parameters

**Image-to-Video Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Video description/instruction |
| `start_image_url` | string | Yes | Initial frame image (jpg, png, webp, gif, avif) |
| `duration` | integer | No | Video length in seconds (default: 12) |
| `generate_audio` | boolean | No | Enable native audio generation |
| `end_image_url` | string | No | Final frame image |
| `elements` | array | No | Custom character/object elements |
| `multi_prompt` | array | No | Multiple prompt segments |
| `aspect_ratio` | string | No | Output format (e.g., "16:9") |
| `negative_prompt` | string | No | Elements to exclude |
| `cfg_scale` | float | No | Control strictness (default: 0.5) |
| `voice_ids` | array | No | Custom voice options for audio |

**Text-to-Video Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text description of desired video |
| `duration` | integer | No | Video length in seconds |
| `generate_audio` | boolean | No | Enable native audio generation |
| `multi_prompt` | array | No | Multiple sequential prompts |
| `voice_ids` | array | No | Custom voice options |
| `shot_type` | string | No | Camera movement customization |
| `aspect_ratio` | string | No | Video format (e.g., "16:9") |
| `negative_prompt` | string | No | Elements to exclude |
| `cfg_scale` | float | No | Control guidance scale |

### Response Format
```json
{
  "video": {
    "url": "string",
    "file_name": "out.mp4",
    "content_type": "video/mp4",
    "file_size": integer
  }
}
```

---

## Implementation Plan

### Subtask 1: Add Image-to-Video Kling v3 Models

**Estimated complexity:** Medium
**Files to modify:**

#### 1.1 Create/Update Model Classes
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/kling.py`

Add two new classes:
```python
class KlingV3StandardModel(BaseVideoModel):
    """Kling v3 Standard image-to-video model."""

class KlingV3ProModel(BaseVideoModel):
    """Kling v3 Pro image-to-video model with enhanced quality."""
```

**New features to implement:**
- `generate_audio` parameter
- `voice_ids` parameter
- `multi_prompt` parameter
- `elements` parameter (character/object references)
- Complex cost calculation (audio on/off/voice control)

#### 1.2 Update Constants
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`

Add to these dictionaries:
- `ModelType` Literal: Add `"kling_3_standard"`, `"kling_3_pro"`
- `SUPPORTED_MODELS`: Add both model keys
- `MODEL_ENDPOINTS`:
  ```python
  "kling_3_standard": "fal-ai/kling-video/v3/standard/image-to-video",
  "kling_3_pro": "fal-ai/kling-video/v3/pro/image-to-video",
  ```
- `MODEL_DISPLAY_NAMES`:
  ```python
  "kling_3_standard": "Kling v3 Standard",
  "kling_3_pro": "Kling v3 Pro",
  ```
- `MODEL_PRICING` (new complex structure for audio variants):
  ```python
  "kling_3_standard": {"no_audio": 0.168, "audio": 0.252, "voice_control": 0.308},
  "kling_3_pro": {"no_audio": 0.224, "audio": 0.336, "voice_control": 0.392},
  ```
- `DURATION_OPTIONS`: Add `["5", "10", "12"]` for both
- `MODEL_INFO`: Add detailed model information
- `MODEL_EXTENDED_FEATURES`: Add support flags for new features

#### 1.3 Update Model Exports
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/__init__.py`

```python
from .kling import KlingModel, Kling26ProModel, KlingV3StandardModel, KlingV3ProModel

__all__ = [
    # ... existing exports
    "KlingV3StandardModel",
    "KlingV3ProModel",
]
```

#### 1.4 Update Generator
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/generator.py`

```python
from .models import KlingV3StandardModel, KlingV3ProModel

self.models = {
    # ... existing models
    "kling_3_standard": KlingV3StandardModel(),
    "kling_3_pro": KlingV3ProModel(),
}
```

Add convenience methods:
```python
def generate_with_kling_v3_standard(self, prompt, image_url, **kwargs):
    return self.generate_video(prompt, image_url, "kling_3_standard", **kwargs)

def generate_with_kling_v3_pro(self, prompt, image_url, **kwargs):
    return self.generate_video(prompt, image_url, "kling_3_pro", **kwargs)
```

#### 1.5 Update CLI
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/cli.py`

- Add `kling_3_standard` and `kling_3_pro` to model choices
- Add CLI arguments for new parameters: `--generate-audio`, `--voice-ids`

---

### Subtask 2: Add Text-to-Video Kling v3 Models

**Estimated complexity:** Medium
**Files to modify:**

#### 2.1 Create/Update Model Classes
**File:** `packages/providers/fal/text-to-video/fal_text_to_video/models/kling.py`

Add two new classes:
```python
class KlingV3StandardModel(BaseTextToVideoModel):
    """Kling v3 Standard text-to-video model."""

class KlingV3ProModel(BaseTextToVideoModel):
    """Kling v3 Pro text-to-video model with enhanced quality."""
```

**New features to implement:**
- `generate_audio` parameter
- `voice_ids` parameter
- `multi_prompt` parameter
- `shot_type` parameter
- Complex cost calculation

#### 2.2 Update Constants
**File:** `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py`

Add to these dictionaries:
- `ModelType` Literal: Add `"kling_3_standard"`, `"kling_3_pro"`
- `SUPPORTED_MODELS`: Add both model keys
- `MODEL_ENDPOINTS`:
  ```python
  "kling_3_standard": "fal-ai/kling-video/v3/standard/text-to-video",
  "kling_3_pro": "fal-ai/kling-video/v3/pro/text-to-video",
  ```
- `MODEL_DISPLAY_NAMES`
- `MODEL_PRICING` (complex structure for audio variants)
- `DURATION_OPTIONS`
- `ASPECT_RATIO_OPTIONS`: `["16:9", "9:16", "1:1"]`
- `MODEL_INFO`

#### 2.3 Update Model Exports
**File:** `packages/providers/fal/text-to-video/fal_text_to_video/models/__init__.py`

```python
from .kling import Kling26ProModel, KlingV3StandardModel, KlingV3ProModel

__all__ = [
    # ... existing exports
    "KlingV3StandardModel",
    "KlingV3ProModel",
]
```

#### 2.4 Update Generator
**File:** `packages/providers/fal/text-to-video/fal_text_to_video/generator.py`

```python
from .models import KlingV3StandardModel, KlingV3ProModel

MODEL_CLASSES: Dict[str, Type[BaseTextToVideoModel]] = {
    # ... existing models
    "kling_3_standard": KlingV3StandardModel,
    "kling_3_pro": KlingV3ProModel,
}
```

#### 2.5 Update CLI (if exists)
**File:** `packages/providers/fal/text-to-video/fal_text_to_video/cli.py`

- Add model choices
- Add new parameter arguments

---

### Subtask 3: Update Core Pipeline Integration

**Estimated complexity:** Low
**Files to modify:**

#### 3.1 Update Image-to-Video Pipeline
**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/models/image_to_video.py`

Add new models to `fal_models` list:
```python
fal_models = [
    "hailuo", "kling", "kling_2_1", "kling_2_6_pro",
    "kling_3_standard", "kling_3_pro",  # New v3 models
    "seedance_1_5_pro", "sora_2", "sora_2_pro",
    "veo_3_1_fast", "wan_2_6"
]
```

#### 3.2 Update Text-to-Video Pipeline
**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/models/text_to_video.py`

Add new models to supported models list.

---

### Subtask 4: Write Unit Tests

**Estimated complexity:** Low
**Files to create/update:**

#### 4.1 Image-to-Video Tests
**File:** `packages/providers/fal/image-to-video/tests/test_kling_v3.py`

```python
import pytest
from fal_image_to_video.models import KlingV3StandardModel, KlingV3ProModel

class TestKlingV3StandardModel:
    def test_model_init(self):
        """Test model instantiation."""

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid inputs."""

    def test_validate_parameters_invalid_duration(self):
        """Test validation fails for invalid duration."""

    def test_prepare_arguments(self):
        """Test API argument preparation."""

    def test_cost_estimation_no_audio(self):
        """Test cost calculation without audio."""

    def test_cost_estimation_with_audio(self):
        """Test cost calculation with audio."""

    def test_cost_estimation_voice_control(self):
        """Test cost calculation with voice control."""

class TestKlingV3ProModel:
    # Similar test structure
```

#### 4.2 Text-to-Video Tests
**File:** `packages/providers/fal/text-to-video/tests/test_kling_v3.py`

Similar test structure for text-to-video models.

---

### Subtask 5: Update Documentation

**Estimated complexity:** Low
**Files to update:**

#### 5.1 Update CLAUDE.md
**File:** `CLAUDE.md`

Add Kling v3 models to the "Available AI Models" section:
```markdown
### 📦 Image-to-Video (14 models)
- **Kling v3 Pro** - Latest generation with native audio (NEW)
- **Kling v3 Standard** - Cost-effective v3 option (NEW)
- **Kling v2.6 Pro** - Previous generation Pro
- **Kling v2.1** - Standard quality
```

#### 5.2 Update README.md (if applicable)
Add new models to the features list.

---

## File Path Summary

### Image-to-Video Files
| File | Action |
|------|--------|
| `packages/providers/fal/image-to-video/fal_image_to_video/models/kling.py` | Add 2 new classes |
| `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py` | Add to 8+ dictionaries |
| `packages/providers/fal/image-to-video/fal_image_to_video/models/__init__.py` | Export new classes |
| `packages/providers/fal/image-to-video/fal_image_to_video/generator.py` | Register models |
| `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` | Update choices |
| `packages/providers/fal/image-to-video/tests/test_kling_v3.py` | Create new test file |

### Text-to-Video Files
| File | Action |
|------|--------|
| `packages/providers/fal/text-to-video/fal_text_to_video/models/kling.py` | Add 2 new classes |
| `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py` | Add to 8+ dictionaries |
| `packages/providers/fal/text-to-video/fal_text_to_video/models/__init__.py` | Export new classes |
| `packages/providers/fal/text-to-video/fal_text_to_video/generator.py` | Register models |
| `packages/providers/fal/text-to-video/tests/test_kling_v3.py` | Create new test file |

### Core Pipeline Files
| File | Action |
|------|--------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/models/image_to_video.py` | Add model keys |
| `packages/core/ai_content_pipeline/ai_content_pipeline/models/text_to_video.py` | Add model keys |

### Documentation Files
| File | Action |
|------|--------|
| `CLAUDE.md` | Update model counts |
| `README.md` | Update features (optional) |

---

## New Features to Support

### 1. Native Audio Generation
Both v3 models support generating audio alongside video:
```python
generate_audio: bool = False  # Enable native audio
```

### 2. Voice Control
Custom voices for generated audio:
```python
voice_ids: List[str] = []  # Custom voice IDs
```

### 3. Multi-Prompt Sequences
Support for complex multi-shot videos:
```python
multi_prompt: List[dict] = []  # Sequential prompt segments
```

### 4. Custom Elements (Image-to-Video)
Character/object consistency with reference images:
```python
elements: List[dict] = [
    {
        "frontal_image_url": "...",  # Front-facing reference
        "reference_image_urls": [...],  # Additional references
        "video_url": "..."  # Motion reference
    }
]
```

### 5. Shot Type Control (Text-to-Video)
Camera movement customization:
```python
shot_type: str = "medium"  # Camera framing
```

---

## Testing Checklist

- [ ] Model instantiation works
- [ ] Parameter validation accepts valid inputs
- [ ] Parameter validation rejects invalid inputs
- [ ] API arguments are prepared correctly
- [ ] Cost estimation works for all pricing tiers (no audio, audio, voice control)
- [ ] Model info returns correct metadata
- [ ] CLI accepts new model choices
- [ ] CLI new parameters work (`--generate-audio`, `--voice-ids`)
- [ ] Integration with pipeline works
- [ ] End-to-end generation test (manual, requires API key)

---

## Implementation Order

1. **Subtask 1**: Image-to-Video models (foundation)
2. **Subtask 2**: Text-to-Video models (similar pattern)
3. **Subtask 3**: Core pipeline integration (enables CLI usage)
4. **Subtask 4**: Unit tests (verify implementation)
5. **Subtask 5**: Documentation (finalize)

---

## Notes

- Follow existing code patterns from `Kling26ProModel` as reference
- Use complex pricing structure to handle audio/voice control tiers
- The `elements` parameter is unique to v3 image-to-video - requires careful implementation
- Consider adding helper methods for multi-prompt construction
- Voice IDs may require additional API documentation research

---

## References

- [Kling v3 Pro Image-to-Video](https://fal.ai/models/fal-ai/kling-video/v3/pro/image-to-video)
- [Kling v3 Pro Text-to-Video](https://fal.ai/models/fal-ai/kling-video/v3/pro/text-to-video)
- [Kling v3 Standard Image-to-Video](https://fal.ai/models/fal-ai/kling-video/v3/standard/image-to-video)
- [Kling v3 Standard Text-to-Video](https://fal.ai/models/fal-ai/kling-video/v3/standard/text-to-video)
