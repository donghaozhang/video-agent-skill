# Feature: Grok Imagine Video Integration

**Issue ID:** GROK-001
**Created:** 2026-01-30
**Branch:** `feature/grok-imagine-video`
**Status:** Completed
**Estimated Total Time:** 45-60 minutes

---

## Overview

Add xAI's Grok Imagine Video model support for both text-to-video and image-to-video generation via FAL AI.

### Model Specifications

| Parameter | Text-to-Video | Image-to-Video |
|-----------|---------------|----------------|
| **Endpoint** | `xai/grok-imagine-video/text-to-video` | `xai/grok-imagine-video/image-to-video` |
| **Duration** | 1-15 seconds (default: 6) | 1-15 seconds (default: 6) |
| **Resolution** | 480p, 720p (default: 720p) | 480p, 720p (default: 720p) |
| **Aspect Ratio** | 16:9, 4:3, 3:2, 1:1, 2:3, 3:4, 9:16 | auto, 16:9, 4:3, 3:2, 1:1, 2:3, 3:4, 9:16 |
| **Max Prompt** | 4,096 characters | 4,096 characters |
| **Audio** | Included | Included |

### Pricing Structure

- **Base cost (6s):** $0.30 (text-to-video), $0.302 (image-to-video)
- **Per additional second:** $0.05
- **Image input cost:** $0.002 (image-to-video only)

---

## Subtasks

### Subtask 1: Update Text-to-Video Constants
**Time:** ~5 minutes

Add Grok Imagine model configuration to text-to-video constants.

**File Path:**
```text
packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py
```

**Changes Required:**
1. Add `"grok_imagine"` to `ModelType` Literal
2. Add `"grok_imagine"` to `SUPPORTED_MODELS` list
3. Add endpoint to `MODEL_ENDPOINTS`
4. Add display name to `MODEL_DISPLAY_NAMES`
5. Add pricing to `MODEL_PRICING`
6. Add duration options to `DURATION_OPTIONS`
7. Add resolution options to `RESOLUTION_OPTIONS`
8. Add aspect ratio options to `ASPECT_RATIO_OPTIONS`
9. Add defaults to `DEFAULT_VALUES`
10. Add model info to `MODEL_INFO`

---

### Subtask 2: Create Text-to-Video Model Class
**Time:** ~10 minutes

Create the Grok Imagine text-to-video model implementation.

**File Path:**
```text
packages/providers/fal/text-to-video/fal_text_to_video/models/grok.py
```

**Implementation:**
- Create `GrokImagineModel` class extending `BaseTextToVideoModel`
- Implement `validate_parameters()` method
- Implement `prepare_arguments()` method
- Implement `get_model_info()` method
- Implement `estimate_cost()` method with $0.30 base + $0.05/additional second

---

### Subtask 3: Export Text-to-Video Model
**Time:** ~2 minutes

Update the models package to export the new Grok model.

**File Path:**
```text
packages/providers/fal/text-to-video/fal_text_to_video/models/__init__.py
```

**Changes Required:**
1. Import `GrokImagineModel` from `.grok`
2. Add `GrokImagineModel` to `__all__` list

---

### Subtask 4: Update Image-to-Video Constants
**Time:** ~5 minutes

Add Grok Imagine model configuration to image-to-video constants.

**File Path:**
```text
packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py
```

**Changes Required:**
1. Add `"grok_imagine"` to `ModelType` Literal
2. Add `"grok_imagine"` to `SUPPORTED_MODELS` list
3. Add endpoint to `MODEL_ENDPOINTS`
4. Add display name to `MODEL_DISPLAY_NAMES`
5. Add pricing to `MODEL_PRICING`
6. Add duration options to `DURATION_OPTIONS`
7. Add resolution options to `RESOLUTION_OPTIONS`
8. Add aspect ratio options to `ASPECT_RATIO_OPTIONS`
9. Add defaults to `DEFAULT_VALUES`
10. Add model info to `MODEL_INFO`
11. Add extended features to `MODEL_EXTENDED_FEATURES`

---

### Subtask 5: Create Image-to-Video Model Class
**Time:** ~10 minutes

Create the Grok Imagine image-to-video model implementation.

**File Path:**
```text
packages/providers/fal/image-to-video/fal_image_to_video/models/grok.py
```

**Implementation:**
- Create `GrokImagineModel` class extending `BaseVideoModel`
- Implement `validate_parameters()` method
- Implement `prepare_arguments()` method with `image_url` support
- Implement `get_model_info()` method
- Implement `estimate_cost()` method with $0.002 image + $0.05/second

---

### Subtask 6: Export Image-to-Video Model
**Time:** ~2 minutes

Update the models package to export the new Grok model.

**File Path:**
```text
packages/providers/fal/image-to-video/fal_image_to_video/models/__init__.py
```

**Changes Required:**
1. Import `GrokImagineModel` from `.grok`
2. Add `GrokImagineModel` to `__all__` list

---

### Subtask 7: Create Unit Tests
**Time:** ~15 minutes

Create comprehensive unit tests for the Grok Imagine model.

**File Paths:**
```text
packages/providers/fal/text-to-video/tests/test_grok_model.py
packages/providers/fal/image-to-video/tests/test_grok_model.py
```

**Test Cases:**
1. **Expected Use:** Valid parameters generate correct API arguments
2. **Edge Case:** Maximum duration (15s), minimum duration (1s)
3. **Failure Case:** Invalid duration, resolution, or aspect ratio raises ValueError

---

### Subtask 8: Update Documentation
**Time:** ~5 minutes

Update CLAUDE.md and README to document the new model.

**File Paths:**
```text
CLAUDE.md
README.md (if exists)
```

**Changes Required:**
1. Add Grok Imagine to the model count (now 53 models)
2. Add to Text-to-Video and Image-to-Video model lists
3. Document pricing information

---

## Validation Checklist

- [x] `ai-content-pipeline list-models` shows Grok Imagine
- [x] Text-to-video generation works with mock mode
- [x] Image-to-video generation works with mock mode
- [x] Cost estimation is accurate
- [x] All unit tests pass (45 tests)
- [x] No linting errors

---

## Long-Term Considerations

1. **Extensibility:** Model class follows established patterns for easy maintenance
2. **Pricing Updates:** Pricing is centralized in constants for easy updates
3. **Parameter Validation:** Strict validation prevents API errors
4. **Documentation:** Inline docstrings explain all parameters
5. **Testing:** Unit tests cover regression prevention

---

## Related Files Summary

| Category | File Path |
|----------|-----------|
| T2V Constants | `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py` |
| T2V Model | `packages/providers/fal/text-to-video/fal_text_to_video/models/grok.py` |
| T2V Export | `packages/providers/fal/text-to-video/fal_text_to_video/models/__init__.py` |
| T2V Tests | `packages/providers/fal/text-to-video/tests/test_grok_model.py` |
| I2V Constants | `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py` |
| I2V Model | `packages/providers/fal/image-to-video/fal_image_to_video/models/grok.py` |
| I2V Export | `packages/providers/fal/image-to-video/fal_image_to_video/models/__init__.py` |
| I2V Tests | `packages/providers/fal/image-to-video/tests/test_grok_model.py` |
| Documentation | `CLAUDE.md` |
