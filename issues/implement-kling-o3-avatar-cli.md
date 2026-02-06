# Implement Kling O3 Avatar/Video Models with CLI Support

## Overview

Add support for **9 new Kling O3 video models** from FAL AI, organized into avatar-generation and video-to-video categories. These models provide advanced character consistency, reference-based generation, and video editing capabilities.

**Note:** Kling O3 is different from Kling v3 - O3 refers to "Omni 3" which focuses on character/element reference consistency.

---

## Models to Implement

### Pro Tier Models (5 models)

| Model | Endpoint | Type | Pricing |
|-------|----------|------|---------|
| O3 Pro Image-to-Video | `fal-ai/kling-video/o3/pro/image-to-video` | Image-to-Video | $0.224/s (no audio), $0.28/s (audio) |
| O3 Pro Text-to-Video | `fal-ai/kling-video/o3/pro/text-to-video` | Text-to-Video | $0.224/s (no audio), $0.28/s (audio) |
| O3 Pro Reference-to-Video | `fal-ai/kling-video/o3/pro/reference-to-video` | Reference-to-Video | $0.224/s (no audio), $0.28/s (audio) |
| O3 Pro Video-to-Video Edit | `fal-ai/kling-video/o3/pro/video-to-video/edit` | Video Editing | $0.336/s |
| O3 Pro Video-to-Video Reference | `fal-ai/kling-video/o3/pro/video-to-video/reference` | Video Reference | $0.336/s |

### Standard Tier Models (4 models)

| Model | Endpoint | Type | Pricing |
|-------|----------|------|---------|
| O3 Standard Image-to-Video | `fal-ai/kling-video/o3/standard/image-to-video` | Image-to-Video | $0.168/s (no audio), $0.224/s (audio) |
| O3 Standard Reference-to-Video | `fal-ai/kling-video/o3/standard/reference-to-video` | Reference-to-Video | $0.084/s (no audio), $0.112/s (audio) |
| O3 Standard Video-to-Video Edit | `fal-ai/kling-video/o3/standard/video-to-video/edit` | Video Editing | $0.252/s |
| O3 Standard Video-to-Video Reference | `fal-ai/kling-video/o3/standard/video-to-video/reference` | Video Reference | $0.252/s |

---

## Key Features

### Elements System (Character/Object Consistency)
All O3 models support the `elements` parameter for consistent character/object rendering:
```python
elements = [
    {
        "frontal_image_url": "https://example.com/character_front.jpg",
        "reference_image_urls": ["https://example.com/pose1.jpg", "https://example.com/pose2.jpg"],
        "video_url": "https://example.com/motion_reference.mp4"  # Optional
    }
]
```

### @ Reference Syntax
Prompts can reference elements and images using `@` notation:
- `@Element1`, `@Element2` - Reference elements array
- `@Image1`, `@Image2` - Reference image_urls array
- `@Video1` - Reference video_url

**Example prompts:**
- `"@Element1 and @Element2 enters the scene from two sides"`
- `"Change environment to be fully snow as @Image1. Replace animal with @Element1"`
- `"Style video should be following watercolor style of @Image1"`

### Common Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | Text description with optional @ references |
| `duration` | int/enum | Video length (3-15 seconds) |
| `generate_audio` | bool | Enable native audio generation |
| `aspect_ratio` | enum | "16:9", "9:16", "1:1" |
| `elements` | array | Character/object definitions |
| `image_urls` | array | Style reference images |
| `video_url` | string | Source video for V2V models |
| `start_image_url` | string | Start frame (I2V models) |
| `end_image_url` | string | End frame for transitions |

---

## Implementation Plan

### Subtask 1: Create Avatar Generation Package Structure

**Estimated complexity:** Medium
**Files to create/modify:**

Create a new avatar-generation provider package for Kling O3 models since they represent a different paradigm (reference-based character consistency) than standard video generation.

#### 1.1 Create Package Directory Structure
```
packages/providers/fal/avatar-generation/
├── fal_avatar_generation/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── kling_o3.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── constants.py
│   ├── generator.py
│   └── cli.py
└── tests/
    └── test_kling_o3.py
```

**Alternative:** Add to existing image-to-video and text-to-video packages if they share enough structure.

---

### Subtask 2: Add O3 Image-to-Video Models

**Files to modify:**
- `packages/providers/fal/image-to-video/fal_image_to_video/models/kling_o3.py` (create)
- `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`
- `packages/providers/fal/image-to-video/fal_image_to_video/models/__init__.py`
- `packages/providers/fal/image-to-video/fal_image_to_video/generator.py`

#### 2.1 Create kling_o3.py Model Classes

```python
class KlingO3StandardI2VModel(BaseVideoModel):
    """Kling O3 Standard image-to-video with element consistency."""

    def __init__(self):
        super().__init__("kling_o3_standard_i2v")

    # Support: elements, image_urls, end_image_url, generate_audio

class KlingO3ProI2VModel(BaseVideoModel):
    """Kling O3 Pro image-to-video with enhanced quality."""

    def __init__(self):
        super().__init__("kling_o3_pro_i2v")
```

#### 2.2 Update constants.py

Add to dictionaries:
- `ModelType`: `"kling_o3_standard_i2v"`, `"kling_o3_pro_i2v"`
- `MODEL_ENDPOINTS`:
  ```python
  "kling_o3_standard_i2v": "fal-ai/kling-video/o3/standard/image-to-video",
  "kling_o3_pro_i2v": "fal-ai/kling-video/o3/pro/image-to-video",
  ```
- `MODEL_PRICING`: Complex pricing with audio tiers
- `DURATION_OPTIONS`: `["3", "5", "10", "15"]`
- `MODEL_INFO`: Features including elements, end_frame, audio

---

### Subtask 3: Add O3 Text-to-Video Model

**Files to modify:**
- `packages/providers/fal/text-to-video/fal_text_to_video/models/kling_o3.py` (create)
- `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py`
- `packages/providers/fal/text-to-video/fal_text_to_video/models/__init__.py`
- `packages/providers/fal/text-to-video/fal_text_to_video/generator.py`

#### 3.1 Create kling_o3.py Model Class

```python
class KlingO3ProT2VModel(BaseTextToVideoModel):
    """Kling O3 Pro text-to-video with multi-prompt and voice support."""

    # Support: multi_prompt, voice_ids (max 2), generate_audio
```

---

### Subtask 4: Add O3 Reference-to-Video Models

**Files to create:**
- `packages/providers/fal/reference-to-video/` (new package)

Or add to existing structure:
- `packages/providers/fal/image-to-video/fal_image_to_video/models/kling_o3_ref.py`

#### 4.1 Create Reference-to-Video Model Classes

```python
class KlingO3StandardRefModel(BaseVideoModel):
    """O3 Standard reference-to-video with element consistency."""

    # Pricing: $0.084/s (no audio), $0.112/s (audio)

class KlingO3ProRefModel(BaseVideoModel):
    """O3 Pro reference-to-video with enhanced quality."""

    # Pricing: $0.224/s (no audio), $0.28/s (audio)
```

---

### Subtask 5: Add O3 Video-to-Video Edit Models

**Files to create:**
- `packages/providers/fal/video-to-video/` (new package)

#### 5.1 Package Structure
```
packages/providers/fal/video-to-video/
├── fal_video_to_video/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── kling_o3.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── constants.py
│   ├── generator.py
│   └── cli.py
└── tests/
    └── test_kling_o3.py
```

#### 5.2 Create Edit Model Classes

```python
class KlingO3StandardEditModel(BaseV2VModel):
    """O3 Standard video editing with element replacement."""

    # Pricing: $0.252/s
    # Parameters: prompt, video_url, image_urls, elements

class KlingO3ProEditModel(BaseV2VModel):
    """O3 Pro video editing with enhanced quality."""

    # Pricing: $0.336/s
```

---

### Subtask 6: Add O3 Video-to-Video Reference Models

**Files to modify:**
- Add to video-to-video package from Subtask 5

#### 6.1 Create Reference Model Classes

```python
class KlingO3StandardV2VRefModel(BaseV2VModel):
    """O3 Standard video reference with style transfer."""

    # Pricing: $0.252/s
    # Parameters: prompt, video_url, image_urls, elements, keep_audio

class KlingO3ProV2VRefModel(BaseV2VModel):
    """O3 Pro video reference with enhanced quality."""

    # Pricing: $0.336/s
```

---

### Subtask 7: Create CLI for Avatar/Reference Generation

**Files to create:**
- `packages/providers/fal/avatar-generation/fal_avatar_generation/cli.py`

Or extend existing CLI:
- `packages/providers/fal/image-to-video/fal_image_to_video/cli.py`

#### 7.1 CLI Commands

```bash
# Image-to-Video with elements
python -m fal_image_to_video.cli generate \
  --model kling_o3_pro_i2v \
  --image start.jpg \
  --prompt "The character walks forward slowly" \
  --element-front character_front.jpg \
  --element-ref pose1.jpg pose2.jpg \
  --duration 10 \
  --audio

# Reference-to-Video
python -m fal_image_to_video.cli generate-ref \
  --model kling_o3_pro_ref \
  --image background.jpg \
  --prompt "@Element1 and @Element2 enters the scene" \
  --element-front char1.jpg char2.jpg \
  --duration 8

# Video-to-Video Edit
python -m fal_video_to_video.cli edit \
  --model kling_o3_pro_edit \
  --video source.mp4 \
  --prompt "Change environment to snow as @Image1" \
  --ref-image snow_scene.jpg \
  --element-front new_character.jpg

# Video-to-Video Reference
python -m fal_video_to_video.cli reference \
  --model kling_o3_pro_v2v_ref \
  --video source.mp4 \
  --prompt "Apply watercolor style of @Image1" \
  --ref-image watercolor_ref.jpg
```

---

### Subtask 8: Update Core Pipeline Integration

**Files to modify:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/models/image_to_video.py`
- `packages/core/ai_content_pipeline/ai_content_pipeline/models/__init__.py`

Add new model keys to supported models list.

---

### Subtask 9: Write Unit Tests

**Files to create:**
- `packages/providers/fal/image-to-video/tests/test_kling_o3.py`
- `packages/providers/fal/text-to-video/tests/test_kling_o3.py`
- `packages/providers/fal/video-to-video/tests/test_kling_o3.py`

#### Test Coverage
- Model instantiation
- Parameter validation (elements, image_urls, video_url)
- @ reference parsing in prompts
- Cost estimation with audio tiers
- API argument preparation
- Model info retrieval

---

## File Path Summary

### New Files to Create

| File | Purpose |
|------|---------|
| `packages/providers/fal/image-to-video/fal_image_to_video/models/kling_o3.py` | O3 I2V models |
| `packages/providers/fal/text-to-video/fal_text_to_video/models/kling_o3.py` | O3 T2V model |
| `packages/providers/fal/video-to-video/` | New V2V package |
| `packages/providers/fal/video-to-video/fal_video_to_video/models/kling_o3.py` | O3 V2V models |
| `packages/providers/fal/video-to-video/fal_video_to_video/cli.py` | V2V CLI |
| `packages/providers/fal/image-to-video/tests/test_kling_o3.py` | I2V tests |
| `packages/providers/fal/text-to-video/tests/test_kling_o3.py` | T2V tests |
| `packages/providers/fal/video-to-video/tests/test_kling_o3.py` | V2V tests |

### Files to Modify

| File | Modification |
|------|--------------|
| `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py` | Add O3 models |
| `packages/providers/fal/image-to-video/fal_image_to_video/models/__init__.py` | Export O3 classes |
| `packages/providers/fal/image-to-video/fal_image_to_video/generator.py` | Register O3 models |
| `packages/providers/fal/image-to-video/fal_image_to_video/cli.py` | Add O3 options, element args |
| `packages/providers/fal/text-to-video/fal_text_to_video/config/constants.py` | Add O3 Pro T2V |
| `packages/providers/fal/text-to-video/fal_text_to_video/models/__init__.py` | Export O3 class |
| `packages/providers/fal/text-to-video/fal_text_to_video/generator.py` | Register O3 model |
| `packages/core/ai_content_pipeline/ai_content_pipeline/models/image_to_video.py` | Add O3 keys |

---

## Pricing Summary

| Model | Audio Off | Audio On |
|-------|-----------|----------|
| O3 Pro I2V | $0.224/s | $0.28/s |
| O3 Pro T2V | $0.224/s | $0.28/s |
| O3 Pro Ref | $0.224/s | $0.28/s |
| O3 Pro V2V Edit | $0.336/s | - |
| O3 Pro V2V Ref | $0.336/s | - |
| O3 Standard I2V | $0.168/s | $0.224/s |
| O3 Standard Ref | $0.084/s | $0.112/s |
| O3 Standard V2V Edit | $0.252/s | - |
| O3 Standard V2V Ref | $0.252/s | - |

---

## Implementation Order

1. **Subtask 2**: O3 Image-to-Video models (builds on existing I2V structure)
2. **Subtask 3**: O3 Text-to-Video model (builds on existing T2V structure)
3. **Subtask 4**: O3 Reference-to-Video models (can add to I2V package)
4. **Subtask 5**: Create Video-to-Video package structure
5. **Subtask 6**: O3 V2V Edit and Reference models
6. **Subtask 7**: CLI extensions
7. **Subtask 8**: Core pipeline integration
8. **Subtask 9**: Unit tests

---

## Testing Checklist

- [ ] O3 Pro I2V model instantiation and validation
- [ ] O3 Standard I2V model instantiation and validation
- [ ] O3 Pro T2V model instantiation and validation
- [ ] O3 Pro Ref model instantiation and validation
- [ ] O3 Standard Ref model instantiation and validation
- [ ] O3 Pro V2V Edit model instantiation and validation
- [ ] O3 Standard V2V Edit model instantiation and validation
- [ ] O3 Pro V2V Ref model instantiation and validation
- [ ] O3 Standard V2V Ref model instantiation and validation
- [ ] Elements parameter validation
- [ ] @ reference syntax in prompts
- [ ] Cost estimation all tiers
- [ ] CLI element arguments
- [ ] CLI reference commands
- [ ] End-to-end generation (manual, requires API key)

---

## Example Use Cases

### 1. Character Walking Animation
```python
# O3 Pro Image-to-Video
result = generator.generate_video(
    prompt="The character walks forward slowly, with the camera following from behind",
    image_url="character_start.jpg",
    model="kling_o3_pro_i2v",
    duration="10",
    generate_audio=True
)
```

### 2. Multi-Character Scene
```python
# O3 Pro Reference-to-Video
result = generator.generate_video(
    prompt="@Element1 and @Element2 enters the scene from two sides. Elephant starts to play with the ball",
    image_url="scene_background.jpg",
    model="kling_o3_pro_ref",
    elements=[
        {"frontal_image_url": "elephant.jpg"},
        {"frontal_image_url": "ball.jpg"}
    ],
    duration="8"
)
```

### 3. Video Style Transfer
```python
# O3 Pro Video-to-Video Reference
result = v2v_generator.edit_video(
    prompt="Integrate @Element1 in the scene. Style video should be following watercolor style of @Image1",
    video_url="source_video.mp4",
    image_urls=["watercolor_reference.jpg"],
    elements=[{"frontal_image_url": "new_character.jpg"}],
    model="kling_o3_pro_v2v_ref"
)
```

### 4. Video Environment Edit
```python
# O3 Pro Video-to-Video Edit
result = v2v_generator.edit_video(
    prompt="Change environment to be fully snow as @Image1. Replace animal with @Element1",
    video_url="summer_scene.mp4",
    image_urls=["snow_landscape.jpg"],
    elements=[{"frontal_image_url": "polar_bear.jpg"}],
    model="kling_o3_pro_edit"
)
```

---

## Notes

- O3 models differ from v3 models - O3 focuses on "Omni" character/element consistency
- The `elements` parameter is central to O3 functionality
- @ reference syntax in prompts requires parsing/validation
- Consider creating a utility function for building element arrays
- V2V models require a new package as they operate on video input
- Standard tier is significantly cheaper for Reference-to-Video

---

## References

- [O3 Pro Image-to-Video](https://fal.ai/models/fal-ai/kling-video/o3/pro/image-to-video)
- [O3 Pro Text-to-Video](https://fal.ai/models/fal-ai/kling-video/o3/pro/text-to-video)
- [O3 Pro Reference-to-Video](https://fal.ai/models/fal-ai/kling-video/o3/pro/reference-to-video)
- [O3 Pro Video-to-Video Edit](https://fal.ai/models/fal-ai/kling-video/o3/pro/video-to-video/edit)
- [O3 Pro Video-to-Video Reference](https://fal.ai/models/fal-ai/kling-video/o3/pro/video-to-video/reference)
- [O3 Standard Image-to-Video](https://fal.ai/models/fal-ai/kling-video/o3/standard/image-to-video)
- [O3 Standard Reference-to-Video](https://fal.ai/models/fal-ai/kling-video/o3/standard/reference-to-video)
- [O3 Standard Video-to-Video Edit](https://fal.ai/models/fal-ai/kling-video/o3/standard/video-to-video/edit)
- [O3 Standard Video-to-Video Reference](https://fal.ai/models/fal-ai/kling-video/o3/standard/video-to-video/reference)
