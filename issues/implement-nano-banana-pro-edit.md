# Implementation: Nano Banana Pro Edit Model

## Overview

Add support for the **Nano Banana Pro Edit** model (`fal-ai/nano-banana-pro/edit`) - a multi-image editing model that can combine and modify multiple input images based on text prompts.

## API Reference

- **Endpoint**: `https://fal.run/fal-ai/nano-banana-pro/edit`
- **Method**: POST
- **Pricing**: $0.015 per image (~7 images per $1.00)
  - 4K outputs: Double rate ($0.030)
  - Web search: Additional $0.015

## Input Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | The prompt for image editing (3-50,000 chars) |
| `image_urls` | array[string] | URLs of images to edit (1-4 images) |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_images` | integer | 1 | Number of images to generate (1-4) |
| `aspect_ratio` | AspectRatioEnum | "auto" | Output aspect ratio |
| `resolution` | ResolutionEnum | "1K" | Output resolution |
| `output_format` | OutputFormatEnum | "png" | Image format |
| `sync_mode` | boolean | false | Return as base64 data URI |
| `limit_generations` | boolean | false | Restrict to 1 generation per prompt |
| `enable_web_search` | boolean | false | Enable web search capability |

### Enum Values

#### AspectRatioEnum
```python
ASPECT_RATIOS = [
    "auto",   # Automatic based on input
    "21:9",   # Ultra-wide
    "16:9",   # Widescreen
    "3:2",    # Classic photo
    "4:3",    # Standard
    "5:4",    # Large format
    "1:1",    # Square
    "4:5",    # Portrait (Instagram)
    "3:4",    # Portrait standard
    "2:3",    # Portrait photo
    "9:16"    # Vertical video
]
```

#### ResolutionEnum
```python
RESOLUTIONS = [
    "1K",   # ~1024px (default, $0.015/image)
    "2K",   # ~2048px ($0.015/image)
    "4K"    # ~4096px ($0.030/image - double rate)
]
```

#### OutputFormatEnum
```python
OUTPUT_FORMATS = ["jpeg", "png", "webp"]
```

## Output Schema

```json
{
  "images": [
    {
      "url": "string",
      "file_name": "string",
      "content_type": "string",
      "file_size": 123456,
      "width": 1024,
      "height": 1024
    }
  ],
  "description": "string"
}
```

## Implementation Plan

### 1. Update FAL Image-to-Image Generator

**File**: `packages/providers/fal/image-to-image/fal_image_to_image_generator.py`

Add new model endpoint:
```python
MODEL_ENDPOINTS = {
    # ... existing models ...
    "nano_banana_pro_edit": "fal-ai/nano-banana-pro/edit",
}
```

Add model defaults:
```python
model_defaults = {
    # ... existing models ...
    "nano_banana_pro_edit": {
        "aspect_ratio": "auto",
        "resolution": "1K",
        "output_format": "png",
        "num_images": 1,
        "sync_mode": True  # To handle base64 responses
    }
}
```

### 2. Create Generation Method

```python
def generate_with_nano_banana_pro_edit(
    self,
    prompt: str,
    image_urls: List[str],
    aspect_ratio: str = "auto",
    resolution: str = "1K",
    output_format: str = "png",
    num_images: int = 1,
    enable_web_search: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Edit/combine images using Nano Banana Pro Edit model.

    Args:
        prompt: Text description for the edit
        image_urls: List of 1-4 image URLs to edit/combine
        aspect_ratio: Output aspect ratio (auto, 1:1, 16:9, etc.)
        resolution: Output resolution (1K, 2K, 4K)
        output_format: Image format (png, jpeg, webp)
        num_images: Number of output images (1-4)
        enable_web_search: Enable web search for context

    Returns:
        Dict with success status, image URLs, and metadata
    """
    # Validate aspect_ratio
    valid_ratios = ["auto", "21:9", "16:9", "3:2", "4:3", "5:4",
                   "1:1", "4:5", "3:4", "2:3", "9:16"]
    if aspect_ratio not in valid_ratios:
        raise ValueError(f"Invalid aspect_ratio: {aspect_ratio}. Valid: {valid_ratios}")

    # Validate resolution
    valid_resolutions = ["1K", "2K", "4K"]
    if resolution not in valid_resolutions:
        raise ValueError(f"Invalid resolution: {resolution}. Valid: {valid_resolutions}")

    # Validate image_urls
    if not image_urls or len(image_urls) > 4:
        raise ValueError("image_urls must contain 1-4 image URLs")

    payload = {
        "prompt": prompt,
        "image_urls": image_urls,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "output_format": output_format,
        "num_images": num_images,
        "sync_mode": True,
        "enable_web_search": enable_web_search
    }

    result = fal_client.subscribe(
        "fal-ai/nano-banana-pro/edit",
        arguments=payload,
        with_logs=True
    )

    # Handle response (including base64 data URLs)
    # ... implementation similar to nano_banana_pro text-to-image
```

### 3. Update Constants

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`

```python
SUPPORTED_MODELS = {
    # ... existing models ...
    "image_to_image": [
        # ... existing models ...
        "nano_banana_pro_edit",
    ]
}

COST_ESTIMATES = {
    "image_to_image": {
        # ... existing models ...
        "nano_banana_pro_edit": 0.015,
        "nano_banana_pro_edit_4k": 0.030,
    }
}
```

### 4. Update Unified Image-to-Image Generator

**File**: `packages/providers/fal/text-to-image/unified_text_to_image_generator.py`

Add to MODEL_CATALOG:
```python
"nano_banana_pro_edit": {
    "provider": Provider.FAL,
    "model_key": "nano_banana_pro_edit",
    "name": "Nano Banana Pro Edit",
    "resolution": "1K-4K",
    "cost_per_image": 0.015,
    "quality": "high",
    "speed": "fast",
    "use_case": "Multi-image editing and composition",
    "special_features": [
        "Up to 4 input images",
        "Multiple aspect ratios",
        "Up to 4K resolution",
        "Web search enhancement"
    ]
}
```

### 5. Update Cost Calculator

**File**: `packages/core/ai_content_platform/utils/cost_calculator.py`

```python
StepType.IMAGE_TO_IMAGE: {
    # ... existing models ...
    "nano_banana_pro_edit": 0.015,
}
```

### 6. Add CLI Support

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

Add new command or update existing image-to-image command:
```python
@cli.command()
@click.option("--images", "-i", multiple=True, required=True, help="Input image URLs/paths")
@click.option("--prompt", "-p", required=True, help="Edit prompt")
@click.option("--model", "-m", default="nano_banana_pro_edit", help="Model to use")
@click.option("--aspect-ratio", default="auto", help="Output aspect ratio")
@click.option("--resolution", default="1K", help="Output resolution (1K, 2K, 4K)")
def edit_image(images, prompt, model, aspect_ratio, resolution):
    """Edit or combine multiple images."""
    pass
```

### 7. YAML Pipeline Support

Example pipeline configuration:
```yaml
name: "Multi-Image Edit"
description: "Combine and edit multiple images"

steps:
  - type: "image_to_image"
    model: "nano_banana_pro_edit"
    params:
      prompt: "Combine these images into a cohesive scene"
      aspect_ratio: "16:9"
      resolution: "2K"
      output_format: "png"
    enabled: true

output_dir: "output"
```

## Example Usage

### Python API
```python
from packages.providers.fal.image_to_image import FALImageToImageGenerator

generator = FALImageToImageGenerator()

result = generator.generate_with_nano_banana_pro_edit(
    prompt="make a photo of the man driving the car down the california coastline",
    image_urls=[
        "https://example.com/person.jpg",
        "https://example.com/car.jpg"
    ],
    aspect_ratio="16:9",
    resolution="2K",
    output_format="png"
)

if result["success"]:
    print(f"Edited image: {result['image_url']}")
```

### CLI
```bash
# Single image edit
venv\Scripts\ai-content-pipeline edit-image \
  --images "path/to/image.jpg" \
  --prompt "Change the background to a beach" \
  --aspect-ratio "16:9" \
  --resolution "2K"

# Multi-image composition
venv\Scripts\ai-content-pipeline edit-image \
  --images "person.jpg" \
  --images "car.jpg" \
  --images "background.jpg" \
  --prompt "Create a scene with the person driving the car" \
  --aspect-ratio "auto"
```

## Testing

### Unit Tests
```python
def test_nano_banana_pro_edit_valid_aspect_ratios():
    """Test all valid aspect ratios."""
    valid_ratios = ["auto", "21:9", "16:9", "3:2", "4:3", "5:4",
                   "1:1", "4:5", "3:4", "2:3", "9:16"]
    for ratio in valid_ratios:
        # Should not raise
        validate_aspect_ratio(ratio)

def test_nano_banana_pro_edit_valid_resolutions():
    """Test all valid resolutions."""
    valid_resolutions = ["1K", "2K", "4K"]
    for res in valid_resolutions:
        # Should not raise
        validate_resolution(res)

def test_nano_banana_pro_edit_image_limit():
    """Test image URL validation."""
    # Should fail with 0 images
    with pytest.raises(ValueError):
        validate_image_urls([])

    # Should fail with 5+ images
    with pytest.raises(ValueError):
        validate_image_urls(["1", "2", "3", "4", "5"])
```

## Files to Modify

| File | Changes |
|------|---------|
| `packages/providers/fal/image-to-image/fal_image_to_image_generator.py` | Add model endpoint, defaults, and generation method |
| `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py` | Add to SUPPORTED_MODELS and COST_ESTIMATES |
| `packages/core/ai_content_platform/utils/cost_calculator.py` | Add cost entry |
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Add CLI command |
| `packages/core/ai_content_pipeline/ai_content_pipeline/models/image_to_image.py` | Add model routing |

## Checklist

- [ ] Add model endpoint to FAL generator
- [ ] Implement `generate_with_nano_banana_pro_edit()` method
- [ ] Handle base64 data URL responses (sync_mode=True)
- [ ] Add aspect_ratio validation with all enum values
- [ ] Add resolution validation (1K, 2K, 4K)
- [ ] Update constants with new model
- [ ] Update cost calculator
- [ ] Add CLI command for image editing
- [ ] Add YAML pipeline support
- [ ] Write unit tests
- [ ] Update documentation
- [ ] Test with real API calls

## Notes

1. **Base64 Response Handling**: When `sync_mode=True`, the API returns base64 data URLs. Use the existing `download_image()` fix that handles base64 data URLs.

2. **Cost Considerations**: 4K resolution costs double ($0.030 vs $0.015). Consider adding a warning when 4K is selected.

3. **Multi-Image Input**: Unlike other models, this accepts multiple input images. Ensure the pipeline can handle passing multiple images between steps.

4. **Web Search**: The `enable_web_search` option adds $0.015 per request. This could be useful for adding context to edits.
