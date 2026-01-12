# Implementation: Nano Banana Pro Edit Model

## Overview

Fix and properly implement the **Nano Banana Pro Edit** model (`fal-ai/nano-banana-pro/edit`).

> **CRITICAL**: The current implementation in `nano_banana.py` is **WRONG** - it uses `strength` and `num_inference_steps` which are NOT valid API parameters. This must be fixed.

## API Reference

- **Endpoint**: `fal-ai/nano-banana-pro/edit`
- **Method**: POST
- **Pricing**:
  - 1K/2K: $0.015 per image
  - 4K: $0.030 per image (double rate)
  - Web search: +$0.015 per request

---

## Long-Term Architecture Considerations

### 1. Multi-Image Input Support

Unlike other image-to-image models, Nano Banana Pro Edit accepts **multiple input images** (1-4). This requires architectural changes:

```python
# Current BaseModel signature (single image):
def prepare_arguments(self, prompt: str, image_url: str, **kwargs)

# Nano Banana Pro Edit needs (multiple images):
def prepare_arguments(self, prompt: str, image_urls: List[str], **kwargs)
```

**Solution**: Create a `MultiImageBaseModel` abstract class or add optional `image_urls` parameter to existing base.

### 2. Shared Enum Definitions

Create reusable enums that can be shared across models:

```python
# New file: packages/providers/fal/common/enums.py

from enum import Enum

class AspectRatio(str, Enum):
    """Standard aspect ratios used across FAL models."""
    AUTO = "auto"
    ULTRA_WIDE_21_9 = "21:9"
    WIDESCREEN_16_9 = "16:9"
    PHOTO_3_2 = "3:2"
    STANDARD_4_3 = "4:3"
    LARGE_FORMAT_5_4 = "5:4"
    SQUARE_1_1 = "1:1"
    PORTRAIT_4_5 = "4:5"
    PORTRAIT_3_4 = "3:4"
    PORTRAIT_2_3 = "2:3"
    VERTICAL_9_16 = "9:16"
    VERTICAL_9_21 = "9:21"

class Resolution(str, Enum):
    """Resolution options for supported models."""
    RES_1K = "1K"   # ~1024px
    RES_2K = "2K"   # ~2048px
    RES_4K = "4K"   # ~4096px

class OutputFormat(str, Enum):
    """Output image formats."""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
```

### 3. Centralized Validation

Add validators that can be reused across models:

```python
# Add to: packages/providers/fal/image-to-image/fal_image_to_image/utils/validators.py

NANO_BANANA_ASPECT_RATIOS = [
    "auto", "21:9", "16:9", "3:2", "4:3", "5:4",
    "1:1", "4:5", "3:4", "2:3", "9:16"
]

RESOLUTIONS = ["1K", "2K", "4K"]

def validate_nano_banana_aspect_ratio(aspect_ratio: str) -> str:
    """Validate aspect ratio for Nano Banana Pro Edit."""
    if aspect_ratio not in NANO_BANANA_ASPECT_RATIOS:
        raise ValueError(
            f"Invalid aspect_ratio: {aspect_ratio}. "
            f"Valid options: {NANO_BANANA_ASPECT_RATIOS}"
        )
    return aspect_ratio

def validate_resolution(resolution: str) -> str:
    """Validate resolution for models that support it."""
    if resolution not in RESOLUTIONS:
        raise ValueError(
            f"Invalid resolution: {resolution}. "
            f"Valid options: {RESOLUTIONS}"
        )
    return resolution

def validate_image_urls(image_urls: List[str], min_count: int = 1, max_count: int = 4) -> List[str]:
    """Validate list of image URLs."""
    if not image_urls:
        raise ValueError("At least one image URL is required")
    if len(image_urls) < min_count:
        raise ValueError(f"At least {min_count} image URL(s) required")
    if len(image_urls) > max_count:
        raise ValueError(f"Maximum {max_count} image URLs allowed, got {len(image_urls)}")
    return image_urls
```

---

## Input Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | Edit instruction (3-50,000 chars) |
| `image_urls` | List[string] | 1-4 input image URLs |

### Optional

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aspect_ratio` | enum | "auto" | Output aspect ratio |
| `resolution` | enum | "1K" | Output resolution (affects cost) |
| `output_format` | enum | "png" | Image format |
| `num_images` | int | 1 | Number of outputs (1-4) |
| `sync_mode` | bool | false | Return base64 data URI |
| `enable_web_search` | bool | false | Enable web search (+$0.015) |

### Enum Values

#### AspectRatioEnum (11 options)
| Value | Description |
|-------|-------------|
| `auto` | Automatic based on input |
| `21:9` | Ultra-wide (cinema) |
| `16:9` | Widescreen |
| `3:2` | Classic photo |
| `4:3` | Standard |
| `5:4` | Large format |
| `1:1` | Square |
| `4:5` | Portrait (Instagram) |
| `3:4` | Portrait standard |
| `2:3` | Portrait photo |
| `9:16` | Vertical video |

#### ResolutionEnum (3 options)
| Value | Approx Size | Cost |
|-------|-------------|------|
| `1K` | ~1024px | $0.015/image |
| `2K` | ~2048px | $0.015/image |
| `4K` | ~4096px | $0.030/image |

---

## Implementation Steps

### Step 1: Update Constants

**File**: `packages/providers/fal/image-to-image/fal_image_to_image/config/constants.py`

```python
# Add new aspect ratio list for Nano Banana Pro
NANO_BANANA_ASPECT_RATIOS = [
    "auto", "21:9", "16:9", "3:2", "4:3", "5:4",
    "1:1", "4:5", "3:4", "2:3", "9:16"
]

# Add resolution enum
RESOLUTIONS = ["1K", "2K", "4K"]

# Update DEFAULT_VALUES - REMOVE wrong parameters
DEFAULT_VALUES = {
    # ... existing models ...
    "nano_banana_pro_edit": {
        "aspect_ratio": "auto",      # CORRECT
        "resolution": "1K",          # CORRECT - NEW
        "output_format": "png",      # CORRECT - NEW
        "num_images": 1,             # CORRECT
        "sync_mode": True            # CORRECT - for base64 handling
        # REMOVED: "strength" - NOT a valid API parameter
        # REMOVED: "num_inference_steps" - NOT a valid API parameter
    }
}

# Update MODEL_INFO with correct information
MODEL_INFO = {
    # ... existing models ...
    "nano_banana_pro_edit": {
        "model_name": "Nano Banana Pro Edit",
        "description": "Multi-image editing and composition model",
        "supported_aspect_ratios": NANO_BANANA_ASPECT_RATIOS,
        "supported_resolutions": RESOLUTIONS,
        "max_input_images": 4,
        "cost_1k_2k": "$0.015/image",
        "cost_4k": "$0.030/image",
        "features": [
            "Multi-image input (up to 4)",
            "11 aspect ratio options",
            "Up to 4K resolution",
            "Optional web search enhancement",
            "Fast processing"
        ]
    }
}
```

### Step 2: Update Validators

**File**: `packages/providers/fal/image-to-image/fal_image_to_image/utils/validators.py`

```python
# Add these new validators:

from typing import List

NANO_BANANA_ASPECT_RATIOS = [
    "auto", "21:9", "16:9", "3:2", "4:3", "5:4",
    "1:1", "4:5", "3:4", "2:3", "9:16"
]

RESOLUTIONS = ["1K", "2K", "4K"]


def validate_nano_banana_aspect_ratio(aspect_ratio: str) -> str:
    """
    Validate aspect ratio for Nano Banana Pro Edit.

    Args:
        aspect_ratio: Aspect ratio string

    Returns:
        Validated aspect ratio

    Raises:
        ValueError: If aspect ratio is not supported
    """
    if aspect_ratio not in NANO_BANANA_ASPECT_RATIOS:
        raise ValueError(
            f"Invalid aspect_ratio: {aspect_ratio}. "
            f"Valid options: {NANO_BANANA_ASPECT_RATIOS}"
        )
    return aspect_ratio


def validate_resolution(resolution: str) -> str:
    """
    Validate resolution for models that support 1K/2K/4K.

    Args:
        resolution: Resolution string (1K, 2K, 4K)

    Returns:
        Validated resolution

    Raises:
        ValueError: If resolution is not supported
    """
    if resolution not in RESOLUTIONS:
        raise ValueError(
            f"Invalid resolution: {resolution}. "
            f"Valid options: {RESOLUTIONS}"
        )
    return resolution


def validate_image_urls(
    image_urls: List[str],
    min_count: int = 1,
    max_count: int = 4
) -> List[str]:
    """
    Validate list of image URLs for multi-image models.

    Args:
        image_urls: List of image URLs
        min_count: Minimum required images
        max_count: Maximum allowed images

    Returns:
        Validated list of URLs

    Raises:
        ValueError: If count is outside valid range
    """
    if not image_urls:
        raise ValueError("At least one image URL is required")

    if len(image_urls) < min_count:
        raise ValueError(f"At least {min_count} image URL(s) required")

    if len(image_urls) > max_count:
        raise ValueError(
            f"Maximum {max_count} image URLs allowed, got {len(image_urls)}"
        )

    return image_urls
```

### Step 3: Fix nano_banana.py Model

**File**: `packages/providers/fal/image-to-image/fal_image_to_image/models/nano_banana.py`

```python
"""
Nano Banana Pro Edit model implementation

This model supports multi-image editing and composition.
"""

from typing import Dict, Any, List, Optional
from .base import BaseModel
from ..config.constants import MODEL_INFO, DEFAULT_VALUES, NANO_BANANA_ASPECT_RATIOS, RESOLUTIONS
from ..utils.validators import (
    validate_nano_banana_aspect_ratio,
    validate_resolution,
    validate_image_urls,
    validate_num_images,
    validate_output_format
)


class NanoBananaProEditModel(BaseModel):
    """
    Nano Banana Pro Edit model for multi-image editing and composition.

    Unlike other image-to-image models, this accepts multiple input images
    and supports resolution selection (1K, 2K, 4K).
    """

    def __init__(self):
        super().__init__("nano_banana_pro_edit")

    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate Nano Banana Pro Edit parameters.

        Valid parameters:
        - aspect_ratio: auto, 21:9, 16:9, 3:2, 4:3, 5:4, 1:1, 4:5, 3:4, 2:3, 9:16
        - resolution: 1K, 2K, 4K
        - output_format: jpeg, png, webp
        - num_images: 1-4
        - enable_web_search: bool
        """
        defaults = DEFAULT_VALUES.get("nano_banana_pro_edit", {})

        # Get and validate parameters
        aspect_ratio = kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "auto"))
        resolution = kwargs.get("resolution", defaults.get("resolution", "1K"))
        output_format = kwargs.get("output_format", defaults.get("output_format", "png"))
        num_images = kwargs.get("num_images", defaults.get("num_images", 1))
        enable_web_search = kwargs.get("enable_web_search", False)
        sync_mode = kwargs.get("sync_mode", defaults.get("sync_mode", True))

        # Validate all parameters
        validated_aspect_ratio = validate_nano_banana_aspect_ratio(aspect_ratio)
        validated_resolution = validate_resolution(resolution)
        validated_output_format = validate_output_format(output_format)
        validated_num_images = validate_num_images(num_images, max_images=4)

        return {
            "aspect_ratio": validated_aspect_ratio,
            "resolution": validated_resolution,
            "output_format": validated_output_format,
            "num_images": validated_num_images,
            "enable_web_search": bool(enable_web_search),
            "sync_mode": bool(sync_mode)
        }

    def prepare_arguments(
        self,
        prompt: str,
        image_url: str = None,
        image_urls: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare API arguments for Nano Banana Pro Edit.

        This model supports multiple input images via image_urls parameter.
        For backwards compatibility, image_url (singular) is also accepted.

        Args:
            prompt: Edit instruction
            image_url: Single image URL (backwards compatibility)
            image_urls: List of image URLs (preferred)
            **kwargs: Additional parameters
        """
        # Handle both single and multiple image inputs
        if image_urls:
            urls = validate_image_urls(image_urls, min_count=1, max_count=4)
        elif image_url:
            urls = [image_url]
        else:
            raise ValueError("Either image_url or image_urls must be provided")

        args = {
            "prompt": prompt,
            "image_urls": urls,
            "aspect_ratio": kwargs.get("aspect_ratio", "auto"),
            "resolution": kwargs.get("resolution", "1K"),
            "output_format": kwargs.get("output_format", "png"),
            "num_images": kwargs.get("num_images", 1),
            "sync_mode": kwargs.get("sync_mode", True)
        }

        # Add optional web search
        if kwargs.get("enable_web_search"):
            args["enable_web_search"] = True

        return args

    def get_model_info(self) -> Dict[str, Any]:
        """Get Nano Banana Pro Edit model information."""
        return {
            **MODEL_INFO.get("nano_banana_pro_edit", {}),
            "endpoint": self.endpoint,
            "supports_multi_image": True,
            "max_input_images": 4
        }

    def estimate_cost(self, resolution: str = "1K", num_images: int = 1,
                      enable_web_search: bool = False) -> float:
        """
        Estimate cost for generation.

        Args:
            resolution: Output resolution (1K, 2K, 4K)
            num_images: Number of images to generate
            enable_web_search: Whether web search is enabled

        Returns:
            Estimated cost in USD
        """
        # Base cost per image
        if resolution == "4K":
            base_cost = 0.030
        else:
            base_cost = 0.015

        total = base_cost * num_images

        # Add web search cost if enabled
        if enable_web_search:
            total += 0.015

        return total
```

### Step 4: Update Cost Calculator

**File**: `packages/core/ai_content_platform/utils/cost_calculator.py`

```python
# Update the cost entry to handle resolution-based pricing
StepType.IMAGE_TO_IMAGE: {
    # ... existing models ...
    "nano_banana_pro_edit": 0.015,      # 1K/2K default
    "nano_banana_pro_edit_4k": 0.030,   # 4K resolution
}
```

### Step 5: Handle Base64 Responses

The model returns base64 data URLs when `sync_mode=True`. Ensure the existing base64 handling from `fal_text_to_image_generator.py` is applied:

```python
# In base.py or file_utils.py, add base64 support:

import base64

def download_images(images: List[Dict], output_dir: Path) -> List[str]:
    """Download images, handling both URLs and base64 data."""
    downloaded = []

    for i, img in enumerate(images):
        url = img.get("url", "")

        if url.startswith("data:"):
            # Handle base64 data URL
            filepath = save_base64_image(url, output_dir, i)
        else:
            # Handle regular URL
            filepath = download_url_image(url, output_dir, i)

        downloaded.append(str(filepath))

    return downloaded


def save_base64_image(data_url: str, output_dir: Path, index: int) -> Path:
    """Save base64 data URL to file."""
    header, encoded = data_url.split(",", 1)

    # Determine extension from MIME type
    if "image/png" in header:
        ext = ".png"
    elif "image/jpeg" in header:
        ext = ".jpg"
    elif "image/webp" in header:
        ext = ".webp"
    else:
        ext = ".png"

    filename = f"nano_banana_edit_{int(time.time())}_{index}{ext}"
    filepath = output_dir / filename

    image_data = base64.b64decode(encoded)
    filepath.write_bytes(image_data)

    return filepath
```

---

## Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `fal_image_to_image/config/constants.py` | Add correct enums, fix DEFAULT_VALUES | **HIGH** |
| `fal_image_to_image/utils/validators.py` | Add new validators | **HIGH** |
| `fal_image_to_image/models/nano_banana.py` | Complete rewrite with correct API | **HIGH** |
| `fal_image_to_image/utils/file_utils.py` | Add base64 image handling | **MEDIUM** |
| `ai_content_platform/utils/cost_calculator.py` | Add resolution-aware pricing | **MEDIUM** |
| `ai_content_pipeline/__main__.py` | Add CLI support (future) | **LOW** |

---

## Checklist

### Phase 1: Fix Current Bugs (Required)
- [x] Remove wrong parameters (`strength`, `num_inference_steps`) from constants
- [x] Add correct parameters (`aspect_ratio`, `resolution`, `output_format`)
- [x] Add `NANO_BANANA_ASPECT_RATIOS` constant with all 11 options
- [x] Add `RESOLUTIONS` constant with 1K/2K/4K
- [x] Rewrite `nano_banana.py` with correct API parameters

### Phase 2: Add Validators (Required)
- [x] Add `validate_nano_banana_aspect_ratio()` function
- [x] Add `validate_resolution()` function
- [x] Add `validate_image_urls()` function for multi-image support

### Phase 3: Handle Responses (Required)
- [x] Add base64 data URL handling to file_utils.py
- [ ] Test with real API calls

### Phase 4: Cost & Documentation (Recommended)
- [x] Update cost calculator with resolution-aware pricing
- [x] Add warning when 4K resolution selected (double cost)
- [x] Update MODEL_INFO with accurate capabilities
- [x] Add unit tests for validators

### Phase 5: CLI & YAML Support (Future)
- [x] Add `--resolution` option to CLI
- [x] Add `--aspect-ratio` option to CLI (already existed, enhanced help text)
- [x] Document YAML pipeline usage (created `image_nano_banana_edit.yaml`)
- [ ] Add integration tests

---

## Breaking Changes

This fix will change the API for `nano_banana_pro_edit`:

```python
# OLD (WRONG) - These parameters don't exist in the API
model.generate(
    prompt="...",
    image_url="...",
    strength=0.75,           # ❌ NOT VALID
    num_inference_steps=4    # ❌ NOT VALID
)

# NEW (CORRECT) - Actual API parameters
model.generate(
    prompt="...",
    image_urls=["..."],      # Note: plural, list
    aspect_ratio="16:9",     # ✅ Valid
    resolution="2K",         # ✅ Valid
    output_format="png"      # ✅ Valid
)
```

---

## Testing

```python
import pytest
from fal_image_to_image.utils.validators import (
    validate_nano_banana_aspect_ratio,
    validate_resolution,
    validate_image_urls
)

class TestNanoBananaValidators:

    def test_valid_aspect_ratios(self):
        """All 11 aspect ratios should be valid."""
        valid = ["auto", "21:9", "16:9", "3:2", "4:3", "5:4",
                 "1:1", "4:5", "3:4", "2:3", "9:16"]
        for ratio in valid:
            assert validate_nano_banana_aspect_ratio(ratio) == ratio

    def test_invalid_aspect_ratio(self):
        """Invalid ratios should raise ValueError."""
        with pytest.raises(ValueError):
            validate_nano_banana_aspect_ratio("invalid")
        with pytest.raises(ValueError):
            validate_nano_banana_aspect_ratio("16:10")  # Not supported

    def test_valid_resolutions(self):
        """1K, 2K, 4K should be valid."""
        for res in ["1K", "2K", "4K"]:
            assert validate_resolution(res) == res

    def test_invalid_resolution(self):
        """Invalid resolutions should raise ValueError."""
        with pytest.raises(ValueError):
            validate_resolution("8K")
        with pytest.raises(ValueError):
            validate_resolution("HD")

    def test_image_urls_valid(self):
        """1-4 URLs should be valid."""
        assert validate_image_urls(["url1"]) == ["url1"]
        assert validate_image_urls(["a", "b", "c", "d"]) == ["a", "b", "c", "d"]

    def test_image_urls_empty(self):
        """Empty list should raise ValueError."""
        with pytest.raises(ValueError):
            validate_image_urls([])

    def test_image_urls_too_many(self):
        """More than 4 URLs should raise ValueError."""
        with pytest.raises(ValueError):
            validate_image_urls(["1", "2", "3", "4", "5"])
```

---

## Summary

This implementation focuses on **long-term maintainability**:

1. **Correct API parameters** - Fix the current broken implementation
2. **Reusable validators** - Functions that can be used by other models
3. **Proper enums** - Type-safe constants for aspect ratios and resolutions
4. **Multi-image support** - Architecture that supports both single and multiple inputs
5. **Cost awareness** - Resolution-based pricing with warnings
6. **Base64 handling** - Reuse existing fix from text-to-image
