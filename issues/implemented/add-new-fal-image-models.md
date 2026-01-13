# Add New FAL Image Models

## Overview
Implement support for new FAL AI image generation models with a focus on long-term maintainability and extensibility.

---

## Models to Add

### Text-to-Image
| Model | API | Endpoint |
|-------|-----|----------|
| Nano Banana Pro | https://fal.ai/models/fal-ai/nano-banana-pro/api | `fal-ai/nano-banana-pro` |
| GPT Image 1.5 | https://fal.ai/models/fal-ai/gpt-image-1.5/api | `fal-ai/gpt-image-1.5` |

### Image-to-Image
| Model | API | Endpoint |
|-------|-----|----------|
| Nano Banana Pro Edit | https://fal.ai/models/fal-ai/nano-banana-pro/edit/api | `fal-ai/nano-banana-pro/edit` |
| GPT Image 1.5 Edit | https://fal.ai/models/fal-ai/gpt-image-1.5/edit/api | `fal-ai/gpt-image-1.5/edit` |

---

## Design Principles (Long-term Maintainability)

### 1. Configuration-Driven Architecture
- **Single source of truth**: All model metadata in config files, not scattered across code
- **No hardcoded values**: Endpoints, costs, defaults defined in constants only
- **Schema validation**: Use Pydantic models for model configuration

### 2. Extensibility Pattern
- **Base class inheritance**: New models extend `BaseModel` with minimal overrides
- **Plugin-style registration**: Models auto-register via constants, not manual wiring
- **Feature flags**: Enable/disable models without code changes

### 3. Consistency Standards
- **Naming convention**: `{model_name}` for t2i, `{model_name}_edit` for i2i
- **Parameter normalization**: Standard parameter names across all models
- **Error handling**: Unified error types and messages

### 4. Testing Strategy
- **Contract tests**: Verify API compatibility before integration
- **Mock-based unit tests**: No API calls in CI/CD
- **Integration test suite**: Separate, optional live API tests

---

## Implementation Details

### Files to Modify

#### 1. Text-to-Image Provider
**File**: `packages/providers/fal/text-to-image/fal_text_to_image_generator.py`

**ADD** to `MODEL_ENDPOINTS` dict (~line 36-42):
```python
"nano_banana_pro": "fal-ai/nano-banana-pro",
"gpt_image_1_5": "fal-ai/gpt-image-1.5",
```

**ADD** to `self.model_defaults` (~line 59-87):
```python
self.model_defaults["nano_banana_pro"] = {
    "image_size": "landscape_4_3",
    "num_inference_steps": 4,
    "num_images": 1,
    "sync_mode": True,
    "enable_safety_checker": True
}
self.model_defaults["gpt_image_1_5"] = {
    "image_size": "landscape_4_3",
    "num_images": 1,
    "sync_mode": True
}
```

---

#### 2. Text-to-Image Core Model
**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/models/text_to_image.py`

**ADD** to `get_model_info()` (~line 219-256):
```python
"nano_banana_pro": {
    "name": "Nano Banana Pro",
    "description": "Fast, high-quality image generation",
    "provider": "fal",
    "cost_per_image": 0.002
},
"gpt_image_1_5": {
    "name": "GPT Image 1.5",
    "description": "GPT-powered image generation",
    "provider": "fal",
    "cost_per_image": 0.003
}
```

---

#### 3. Core Constants
**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`

**ADD** to `SUPPORTED_MODELS["text_to_image"]` (~line 6-59):
```python
"nano_banana_pro",
"gpt_image_1_5",
```

**ADD** to `COST_ESTIMATES["text_to_image"]` (~line 124-132):
```python
"nano_banana_pro": 0.002,
"gpt_image_1_5": 0.003,
```

**ADD** to `SUPPORTED_MODELS["image_to_image"]`:
```python
"nano_banana_pro_edit",
"gpt_image_1_5_edit",
```

**ADD** to `COST_ESTIMATES["image_to_image"]`:
```python
"nano_banana_pro_edit": 0.015,
"gpt_image_1_5_edit": 0.02,
```

---

#### 4. Image-to-Image Constants
**File**: `packages/providers/fal/image-to-image/fal_image_to_image/config/constants.py`

**ADD** to `MODEL_ENDPOINTS` (~line 15-22):
```python
"nano_banana_pro_edit": "fal-ai/nano-banana-pro/edit",
"gpt_image_1_5_edit": "fal-ai/gpt-image-1.5/edit",
```

**ADD** to `MODEL_DISPLAY_NAMES` (~line 61-68):
```python
"nano_banana_pro_edit": "Nano Banana Pro Edit",
"gpt_image_1_5_edit": "GPT Image 1.5 Edit",
```

**ADD** to `DEFAULT_VALUES` (~line 41-58):
```python
"nano_banana_pro_edit": {
    "strength": 0.75,
    "num_inference_steps": 4
},
"gpt_image_1_5_edit": {
    "strength": 0.75
}
```

**ADD** to `MODEL_INFO` (~line 71-156):
```python
"nano_banana_pro_edit": {
    "name": "Nano Banana Pro Edit",
    "description": "Fast image editing with Nano Banana Pro",
    "provider": "fal",
    "parameters": ["prompt", "image_url", "strength"]
},
"gpt_image_1_5_edit": {
    "name": "GPT Image 1.5 Edit",
    "description": "GPT-powered image editing",
    "provider": "fal",
    "parameters": ["prompt", "image_url", "strength"]
}
```

---

#### 5. Image-to-Image Model Classes
**Directory**: `packages/providers/fal/image-to-image/fal_image_to_image/models/`

**CREATE** `nano_banana.py` - Full implementation with validation and argument preparation
**CREATE** `gpt_image.py` - Full implementation with validation and argument preparation

---

#### 6. Image-to-Image Generator
**File**: `packages/providers/fal/image-to-image/fal_image_to_image/generator.py`

**ADD** imports and register models in `self.models` dict

---

#### 7. Image-to-Image Core Model
**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/models/image_to_image.py`

**ADD** to available models list (~line 56-63)

---

#### 8. Cost Calculator
**File**: `packages/core/ai_content_platform/utils/cost_calculator.py`

**ADD** cost rates for new models (~line 45-95)

---

## Implementation Tasks (Subtasks < 10 min each)

### Phase 1: Research & Documentation
- [x] **1.1** Fetch Nano Banana Pro API spec - document parameters, response format
- [x] **1.2** Fetch GPT Image 1.5 API spec - document parameters, response format
- [x] **1.3** Fetch Nano Banana Pro Edit API spec - document parameters, response format
- [x] **1.4** Fetch GPT Image 1.5 Edit API spec - document parameters, response format
- [x] **1.5** Document cost per request for each model from FAL pricing

### Phase 2: Text-to-Image - Nano Banana Pro
- [x] **2.1** Add endpoint to `MODEL_ENDPOINTS` in `fal_text_to_image_generator.py`
- [x] **2.2** Add default parameters to `model_defaults` in `fal_text_to_image_generator.py`
- [x] **2.3** Add model info to `get_model_info()` in `text_to_image.py`
- [x] **2.4** Add to `SUPPORTED_MODELS` in `constants.py`
- [x] **2.5** Add to `COST_ESTIMATES` in `constants.py`
- [x] **2.6** Add cost rate to `cost_calculator.py`
- [x] **2.7** Write unit test for Nano Banana Pro generation

### Phase 3: Text-to-Image - GPT Image 1.5
- [x] **3.1** Add endpoint to `MODEL_ENDPOINTS` in `fal_text_to_image_generator.py`
- [x] **3.2** Add default parameters to `model_defaults` in `fal_text_to_image_generator.py`
- [x] **3.3** Add model info to `get_model_info()` in `text_to_image.py`
- [x] **3.4** Add to `SUPPORTED_MODELS` in `constants.py`
- [x] **3.5** Add to `COST_ESTIMATES` in `constants.py`
- [x] **3.6** Add cost rate to `cost_calculator.py`
- [x] **3.7** Write unit test for GPT Image 1.5 generation

### Phase 4: Image-to-Image - Nano Banana Pro Edit
- [x] **4.1** Add endpoint to `MODEL_ENDPOINTS` in i2i `constants.py`
- [x] **4.2** Add display name to `MODEL_DISPLAY_NAMES` in i2i `constants.py`
- [x] **4.3** Add defaults to `DEFAULT_VALUES` in i2i `constants.py`
- [x] **4.4** Add info to `MODEL_INFO` in i2i `constants.py`
- [x] **4.5** Create `nano_banana.py` - define class structure
- [x] **4.6** Implement `validate_parameters()` method
- [x] **4.7** Implement `prepare_arguments()` method
- [x] **4.8** Implement `get_model_info()` method
- [x] **4.9** Add export to `models/__init__.py`
- [x] **4.10** Register in `generator.py` models dict
- [x] **4.11** Add to available models in `image_to_image.py`
- [x] **4.12** Add to `SUPPORTED_MODELS` in core `constants.py`
- [x] **4.13** Add to `COST_ESTIMATES` in core `constants.py`
- [x] **4.14** Add cost rate to `cost_calculator.py`
- [x] **4.15** Write unit test for Nano Banana Pro Edit

### Phase 5: Image-to-Image - GPT Image 1.5 Edit
- [x] **5.1** Add endpoint to `MODEL_ENDPOINTS` in i2i `constants.py`
- [x] **5.2** Add display name to `MODEL_DISPLAY_NAMES` in i2i `constants.py`
- [x] **5.3** Add defaults to `DEFAULT_VALUES` in i2i `constants.py`
- [x] **5.4** Add info to `MODEL_INFO` in i2i `constants.py`
- [x] **5.5** Create `gpt_image.py` - define class structure
- [x] **5.6** Implement `validate_parameters()` method
- [x] **5.7** Implement `prepare_arguments()` method
- [x] **5.8** Implement `get_model_info()` method
- [x] **5.9** Add export to `models/__init__.py`
- [x] **5.10** Register in `generator.py` models dict
- [x] **5.11** Add to available models in `image_to_image.py`
- [x] **5.12** Add to `SUPPORTED_MODELS` in core `constants.py`
- [x] **5.13** Add to `COST_ESTIMATES` in core `constants.py`
- [x] **5.14** Add cost rate to `cost_calculator.py`
- [x] **5.15** Write unit test for GPT Image 1.5 Edit

### Phase 6: Integration & Validation
- [x] **6.1** Run existing test suite - verify no regressions
- [x] **6.2** Test `ai-content-pipeline list-models` shows new models
- [ ] **6.3** Test text-to-image generation with Nano Banana Pro (requires API key)
- [ ] **6.4** Test text-to-image generation with GPT Image 1.5 (requires API key)
- [ ] **6.5** Test image-to-image with Nano Banana Pro Edit (requires API key)
- [ ] **6.6** Test image-to-image with GPT Image 1.5 Edit (requires API key)
- [x] **6.7** Verify cost estimation accuracy for new models

### Phase 7: Documentation & Cleanup
- [x] **7.1** Update README with new models in "Available AI Models" section
- [ ] **7.2** Add example YAML configs using new models
- [x] **7.3** Update CLAUDE.md if model count changed
- [x] **7.4** Git commit and push changes

---

## Summary of Changes

| File | Action | Description |
|------|--------|-------------|
| `fal_text_to_image_generator.py` | MODIFY | Add endpoints + defaults for 2 models |
| `text_to_image.py` | MODIFY | Add model info for 2 models |
| `constants.py` (core) | MODIFY | Add 4 models to supported + costs |
| `constants.py` (fal i2i) | MODIFY | Add endpoints, names, defaults, info for 2 models |
| `nano_banana.py` | CREATE | NanoBananaProEditModel class |
| `gpt_image.py` | CREATE | GPTImage15EditModel class |
| `generator.py` (i2i) | MODIFY | Register 2 new models |
| `models/__init__.py` | MODIFY | Export 2 new classes |
| `image_to_image.py` | MODIFY | Add 2 models to available list |
| `cost_calculator.py` | MODIFY | Add cost rates for 4 models |

---

## Maintainability Checklist

Before marking complete, verify:

- [ ] All model config in constants files (no hardcoded values in logic)
- [ ] Consistent naming: `{name}` for t2i, `{name}_edit` for i2i
- [ ] Model classes follow BaseModel pattern exactly
- [ ] Unit tests use mocks (no live API calls)
- [ ] Cost estimates validated against FAL pricing
- [ ] Error messages include model name for debugging
- [ ] Documentation updated in all relevant files
