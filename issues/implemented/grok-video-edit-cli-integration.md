# Feature: Grok Imagine Video Edit CLI Integration

**Issue ID:** GROK-002
**Created:** 2026-01-30
**Branch:** `feature/grok-imagine-video` (existing)
**Status:** Planning
**Estimated Total Time:** 35-45 minutes

---

## Overview

Add xAI's Grok Imagine Video Edit model to the avatar-generation package for video-to-video editing functionality via FAL AI.

### Model Specifications

| Parameter | Value |
|-----------|-------|
| **Endpoint** | `xai/grok-imagine-video/edit-video` |
| **Category** | Video-to-Video editing |
| **Input Video** | Resized to max 854x480, truncated to 8 seconds |
| **Resolution** | auto, 480p, 720p (default: auto) |
| **Max Prompt** | 4,096 characters |

### Pricing Structure

- **Base cost (6s):** $0.36
- **Per second input:** $0.01
- **Per second output:** $0.05
- **Per additional second:** $0.06

---

## Subtasks

### Subtask 1: Update Avatar Constants
**Time:** ~5 minutes

Add Grok Video Edit model configuration to avatar constants.

**File Path:**
```
packages/providers/fal/avatar-generation/fal_avatar/config/constants.py
```

**Changes Required:**
1. Add `"grok_video_edit"` to model type definitions
2. Add endpoint to `MODEL_ENDPOINTS`
3. Add display name to `MODEL_DISPLAY_NAMES`
4. Add pricing to `MODEL_PRICING`
5. Add defaults to `MODEL_DEFAULTS`
6. Add resolution to `SUPPORTED_RESOLUTIONS`
7. Add max duration to `MAX_DURATIONS`
8. Add input requirements to `INPUT_REQUIREMENTS`
9. Add to `MODEL_CATEGORIES` under "video_to_video"

---

### Subtask 2: Create Grok Video Edit Model Class
**Time:** ~10 minutes

Create the Grok Video Edit model implementation.

**File Path:**
```
packages/providers/fal/avatar-generation/fal_avatar/models/grok.py
```

**Implementation:**
- Create `GrokVideoEditModel` class extending `BaseAvatarModel`
- Implement `validate_parameters()` method for video_url, prompt, resolution
- Implement `prepare_arguments()` method
- Implement `estimate_cost()` method with $0.01/s input + $0.05/s output
- Implement `get_model_info()` method

---

### Subtask 3: Export Grok Model
**Time:** ~2 minutes

Update the models package to export the new Grok model.

**File Path:**
```
packages/providers/fal/avatar-generation/fal_avatar/models/__init__.py
```

**Changes Required:**
1. Import `GrokVideoEditModel` from `.grok`
2. Add `GrokVideoEditModel` to `__all__` list

---

### Subtask 4: Register Model in Generator
**Time:** ~5 minutes

Add Grok Video Edit to the generator's model registry.

**File Path:**
```
packages/providers/fal/avatar-generation/fal_avatar/generator.py
```

**Changes Required:**
1. Import `GrokVideoEditModel`
2. Add to `self.models` dictionary
3. Ensure `transform_video()` method can route to grok_video_edit

---

### Subtask 5: Add CLI Support
**Time:** ~5 minutes

Check if avatar-generation has a CLI file and add grok_video_edit support.

**File Paths:**
```
packages/providers/fal/avatar-generation/fal_avatar/cli.py (if exists)
# OR add to main pipeline CLI
packages/core/ai_content_pipeline/cli.py
```

**Changes Required:**
1. Add grok_video_edit to video editing CLI options
2. Handle video_url and prompt parameters
3. Support resolution option (auto, 480p, 720p)

---

### Subtask 6: Create Unit Tests
**Time:** ~10 minutes

Create comprehensive unit tests for the Grok Video Edit model.

**File Path:**
```
packages/providers/fal/avatar-generation/tests/test_grok_video_edit.py
```

**Test Cases:**
1. **Expected Use:** Valid parameters generate correct API arguments
2. **Edge Case:** Auto resolution, max prompt length
3. **Failure Case:** Invalid resolution, missing video_url raises ValueError

---

### Subtask 7: Update Package Init
**Time:** ~2 minutes

Update the package __init__.py to export the new model.

**File Path:**
```
packages/providers/fal/avatar-generation/fal_avatar/__init__.py
```

**Changes Required:**
1. Import `GrokVideoEditModel`
2. Add to `__all__` list

---

## Validation Checklist

- [ ] `FALAvatarGenerator().list_models()` shows grok_video_edit
- [ ] `generator.transform_video()` works with grok_video_edit
- [ ] Cost estimation is accurate ($0.36 for 6s)
- [ ] All unit tests pass
- [ ] No linting errors

---

## Long-Term Considerations

1. **Extensibility:** Model class follows BaseAvatarModel pattern
2. **Pricing Updates:** Pricing centralized in constants for easy updates
3. **Parameter Validation:** Strict validation prevents API errors
4. **Category Integration:** Properly grouped in "video_to_video" category
5. **CLI Integration:** Accessible via transform-video or edit-video command

---

## Related Files Summary

| Category | File Path |
|----------|-----------|
| Constants | `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py` |
| Model | `packages/providers/fal/avatar-generation/fal_avatar/models/grok.py` |
| Model Export | `packages/providers/fal/avatar-generation/fal_avatar/models/__init__.py` |
| Generator | `packages/providers/fal/avatar-generation/fal_avatar/generator.py` |
| Package Init | `packages/providers/fal/avatar-generation/fal_avatar/__init__.py` |
| Tests | `packages/providers/fal/avatar-generation/tests/test_grok_video_edit.py` |

---

## API Reference

### Endpoint
```
xai/grok-imagine-video/edit-video
```

### Request Parameters
```python
{
    "prompt": str,          # Required, max 4096 chars
    "video_url": str,       # Required, input video URL
    "resolution": str       # Optional: "auto", "480p", "720p"
}
```

### Response
```python
{
    "video": {
        "url": str,
        "width": int,
        "height": int,
        "fps": float,
        "duration": float,
        "num_frames": int,
        "content_type": "video/mp4",
        "file_name": str
    }
}
```
