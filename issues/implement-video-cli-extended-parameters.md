# Implement Extended Video CLI Parameters

## Overview

Add support for advanced video generation parameters across all image-to-video models in the AI Content Pipeline CLI.

## New Parameters

| Parameter | Type | Description | Use Case |
|-----------|------|-------------|----------|
| `start_frame` | image path | Starting frame image | Control video start appearance |
| `end_frame` | image path | Ending frame image | Control video end appearance (interpolation) |
| `ref_images` | list of image paths | Reference images for style/character | Maintain consistency across generations |
| `audio` | audio file path | Audio input for synchronization | Lip-sync, music videos |
| `ref_video` | video file path | Reference video for motion/style | Motion transfer, style reference |

## Model Support Matrix

| Model | start_frame | end_frame | ref_images | audio | ref_video |
|-------|-------------|-----------|------------|-------|-----------|
| Veo 3.1 Fast | ✅ (image_url) | ❌ | ❌ | ✅ (generate) | ❌ |
| Sora 2 | ✅ | ✅ | ❌ | ❌ | ❌ |
| Sora 2 Pro | ✅ | ✅ | ❌ | ❌ | ❌ |
| Kling v2.1 | ✅ | ✅ | ❌ | ❌ | ❌ |
| Kling v2.6 Pro | ✅ | ✅ | ❌ | ❌ | ❌ |
| Hailuo | ✅ | ❌ | ❌ | ❌ | ❌ |
| Seedance | ✅ | ❌ | ✅ | ❌ | ✅ |

## Implementation Plan

### Task 1: Update Base Model Class
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/base.py`
**Time:** 15 minutes

```python
# Add to BaseVideoModel class

def prepare_arguments(
    self,
    prompt: str,
    image_url: str,
    start_frame: Optional[str] = None,
    end_frame: Optional[str] = None,
    ref_images: Optional[List[str]] = None,
    audio: Optional[str] = None,
    ref_video: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Prepare API arguments with extended parameters.

    Args:
        prompt: Text description for video generation
        image_url: Primary input image URL (same as start_frame if not provided)
        start_frame: Starting frame image path/URL
        end_frame: Ending frame image path/URL (for interpolation)
        ref_images: List of reference image paths/URLs
        audio: Audio file path/URL for synchronization
        ref_video: Reference video path/URL for motion/style
        **kwargs: Model-specific parameters
    """
    pass  # Implement in subclasses
```

### Task 2: Add File Upload Utilities
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/utils/file_utils.py`
**Time:** 20 minutes

```python
# Add new functions

def upload_file(file_path: str) -> str:
    """Upload any file to FAL and return URL."""
    if file_path.startswith(('http://', 'https://')):
        return file_path
    return fal_client.upload_file(file_path)

def upload_images(image_paths: List[str]) -> List[str]:
    """Upload multiple images and return URLs."""
    return [upload_file(path) for path in image_paths]

def upload_audio(audio_path: str) -> str:
    """Upload audio file and return URL."""
    supported = ['.mp3', '.wav', '.m4a', '.aac', '.ogg']
    ext = Path(audio_path).suffix.lower()
    if ext not in supported:
        raise ValueError(f"Unsupported audio format: {ext}. Supported: {supported}")
    return upload_file(audio_path)

def upload_video(video_path: str) -> str:
    """Upload video file and return URL."""
    supported = ['.mp4', '.mov', '.avi', '.webm']
    ext = Path(video_path).suffix.lower()
    if ext not in supported:
        raise ValueError(f"Unsupported video format: {ext}. Supported: {supported}")
    return upload_file(video_path)
```

### Task 3: Update Sora Models (start_frame, end_frame)
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/sora.py`
**Time:** 20 minutes

```python
# Update Sora2Model and Sora2ProModel

def prepare_arguments(
    self,
    prompt: str,
    image_url: str,
    start_frame: Optional[str] = None,
    end_frame: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Prepare Sora API arguments with frame interpolation support."""
    args = {
        "prompt": prompt,
        "image_url": start_frame or image_url,
    }

    # End frame for video interpolation
    if end_frame:
        args["end_image_url"] = end_frame

    # Standard parameters
    args["duration"] = kwargs.get("duration", 4)
    args["resolution"] = kwargs.get("resolution", "auto")
    args["aspect_ratio"] = kwargs.get("aspect_ratio", "auto")

    return args
```

### Task 4: Update Kling Models (start_frame, end_frame)
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/kling.py`
**Time:** 20 minutes

```python
# Update KlingModel and Kling26ProModel

def prepare_arguments(
    self,
    prompt: str,
    image_url: str,
    start_frame: Optional[str] = None,
    end_frame: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Prepare Kling API arguments with frame interpolation."""
    args = {
        "prompt": prompt,
        "image_url": start_frame or image_url,
        "duration": kwargs.get("duration", "5"),
        "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
        "cfg_scale": kwargs.get("cfg_scale", 0.5)
    }

    if end_frame:
        args["tail_image_url"] = end_frame

    return args
```

### Task 5: Update Seedance Model (ref_images, ref_video)
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/seedance.py`
**Time:** 25 minutes

```python
# Update SeedanceModel

def prepare_arguments(
    self,
    prompt: str,
    image_url: str,
    ref_images: Optional[List[str]] = None,
    ref_video: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Prepare Seedance API arguments with reference support."""
    args = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": kwargs.get("duration", "5"),
    }

    # Seed for reproducibility
    if kwargs.get("seed") is not None:
        args["seed"] = kwargs["seed"]

    # Reference images for character/style consistency
    if ref_images:
        args["reference_images"] = ref_images

    # Reference video for motion transfer
    if ref_video:
        args["reference_video_url"] = ref_video

    return args
```

### Task 6: Update Veo 3.1 Fast (audio generation flag)
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/veo.py`
**Time:** 15 minutes

```python
# Veo 3.1 Fast already supports audio generation
# No changes needed - generate_audio parameter already implemented

def prepare_arguments(
    self,
    prompt: str,
    image_url: str,
    audio: Optional[str] = None,  # For future audio input support
    **kwargs
) -> Dict[str, Any]:
    """Prepare Veo 3.1 Fast API arguments."""
    args = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": kwargs.get("duration", "8s"),
        "generate_audio": kwargs.get("generate_audio", True),
    }

    # Future: audio input for synchronization
    # if audio:
    #     args["audio_url"] = audio

    return args
```

### Task 7: Update Generator with Extended Parameters
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/generator.py`
**Time:** 25 minutes

```python
# Update FALImageToVideoGenerator

def generate_video(
    self,
    prompt: str,
    image_url: str,
    model: str = "hailuo",
    start_frame: Optional[str] = None,
    end_frame: Optional[str] = None,
    ref_images: Optional[List[str]] = None,
    audio: Optional[str] = None,
    ref_video: Optional[str] = None,
    output_dir: Optional[str] = None,
    use_async: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate video with extended parameter support.

    Args:
        prompt: Text description
        image_url: Primary input image
        model: Model to use
        start_frame: Starting frame image (overrides image_url)
        end_frame: Ending frame image (interpolation)
        ref_images: Reference images for consistency
        audio: Audio file for synchronization
        ref_video: Reference video for motion/style
        output_dir: Output directory
        use_async: Use async processing
        **kwargs: Model-specific parameters
    """
    # Upload local files
    if start_frame and not start_frame.startswith('http'):
        start_frame = upload_file(start_frame)
    if end_frame and not end_frame.startswith('http'):
        end_frame = upload_file(end_frame)
    if ref_images:
        ref_images = upload_images(ref_images)
    if audio and not audio.startswith('http'):
        audio = upload_audio(audio)
    if ref_video and not ref_video.startswith('http'):
        ref_video = upload_video(ref_video)

    return self.models[model].generate(
        prompt=prompt,
        image_url=start_frame or image_url,
        end_frame=end_frame,
        ref_images=ref_images,
        audio=audio,
        ref_video=ref_video,
        output_dir=output_dir,
        use_async=use_async,
        **kwargs
    )
```

### Task 8: Update Constants
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`
**Time:** 10 minutes

```python
# Add feature support matrix

MODEL_FEATURES = {
    "hailuo": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio": False,
        "ref_video": False
    },
    "kling_2_1": {
        "start_frame": True,
        "end_frame": True,
        "ref_images": False,
        "audio": False,
        "ref_video": False
    },
    "kling_2_6_pro": {
        "start_frame": True,
        "end_frame": True,
        "ref_images": False,
        "audio": False,
        "ref_video": False
    },
    "seedance_1_5_pro": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": True,
        "ref_video": True,
        "audio": False
    },
    "sora_2": {
        "start_frame": True,
        "end_frame": True,
        "ref_images": False,
        "audio": False,
        "ref_video": False
    },
    "sora_2_pro": {
        "start_frame": True,
        "end_frame": True,
        "ref_images": False,
        "audio": False,
        "ref_video": False
    },
    "veo_3_1_fast": {
        "start_frame": True,
        "end_frame": False,
        "ref_images": False,
        "audio": True,  # generate_audio
        "ref_video": False
    }
}

SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.m4a', '.aac', '.ogg']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi', '.webm']
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
```

### Task 9: Add Unit Tests
**File:** `packages/providers/fal/image-to-video/tests/test_extended_parameters.py`
**Time:** 30 minutes

```python
"""Unit tests for extended video parameters."""

import pytest
from pathlib import Path

from fal_image_to_video.models.sora import Sora2Model, Sora2ProModel
from fal_image_to_video.models.kling import KlingModel, Kling26ProModel
from fal_image_to_video.models.seedance import SeedanceModel
from fal_image_to_video.config.constants import MODEL_FEATURES


class TestSoraFrameInterpolation:
    """Tests for Sora start/end frame support."""

    def test_start_frame_only(self):
        """Start frame should be used as image_url."""
        model = Sora2Model()
        args = model.prepare_arguments(
            prompt="Test",
            image_url="http://original.jpg",
            start_frame="http://start.jpg"
        )
        assert args["image_url"] == "http://start.jpg"

    def test_end_frame_included(self):
        """End frame should be added for interpolation."""
        model = Sora2ProModel()
        args = model.prepare_arguments(
            prompt="Test",
            image_url="http://start.jpg",
            end_frame="http://end.jpg"
        )
        assert args.get("end_image_url") == "http://end.jpg"


class TestKlingFrameInterpolation:
    """Tests for Kling start/end frame support."""

    def test_tail_image_url(self):
        """End frame should be tail_image_url for Kling."""
        model = Kling26ProModel()
        args = model.prepare_arguments(
            prompt="Test",
            image_url="http://start.jpg",
            end_frame="http://end.jpg"
        )
        assert args.get("tail_image_url") == "http://end.jpg"


class TestSeedanceReferences:
    """Tests for Seedance reference support."""

    def test_reference_images(self):
        """Reference images should be included."""
        model = SeedanceModel()
        refs = ["http://ref1.jpg", "http://ref2.jpg"]
        args = model.prepare_arguments(
            prompt="Test",
            image_url="http://main.jpg",
            ref_images=refs
        )
        assert args.get("reference_images") == refs

    def test_reference_video(self):
        """Reference video should be included."""
        model = SeedanceModel()
        args = model.prepare_arguments(
            prompt="Test",
            image_url="http://main.jpg",
            ref_video="http://reference.mp4"
        )
        assert args.get("reference_video_url") == "http://reference.mp4"


class TestModelFeatures:
    """Tests for model feature matrix."""

    def test_all_models_have_features(self):
        """All models should have feature definitions."""
        for model_key in ["hailuo", "kling_2_1", "kling_2_6_pro",
                          "seedance_1_5_pro", "sora_2", "sora_2_pro",
                          "veo_3_1_fast"]:
            assert model_key in MODEL_FEATURES

    def test_sora_supports_end_frame(self):
        """Sora models should support end_frame."""
        assert MODEL_FEATURES["sora_2"]["end_frame"] is True
        assert MODEL_FEATURES["sora_2_pro"]["end_frame"] is True

    def test_seedance_supports_references(self):
        """Seedance should support ref_images and ref_video."""
        assert MODEL_FEATURES["seedance_1_5_pro"]["ref_images"] is True
        assert MODEL_FEATURES["seedance_1_5_pro"]["ref_video"] is True

    def test_veo_supports_audio(self):
        """Veo 3.1 Fast should support audio generation."""
        assert MODEL_FEATURES["veo_3_1_fast"]["audio"] is True
```

### Task 10: Update CLI Documentation
**File:** `.claude/skills/ai-content-pipeline/REFERENCE.md`
**Time:** 15 minutes

Add section for extended parameters in the documentation.

## CLI Usage Examples

### Start and End Frame (Interpolation)
```bash
# Sora 2 - interpolate between two images
ai-content-pipeline generate-video \
  --model sora_2_pro \
  --start-frame "input/images/frame_start.png" \
  --end-frame "input/images/frame_end.png" \
  --prompt "Smooth transition between the two scenes" \
  --duration 8
```

### Reference Images (Character Consistency)
```bash
# Seedance - maintain character across generations
ai-content-pipeline generate-video \
  --model seedance_1_5_pro \
  --image "input/images/scene.png" \
  --ref-images "input/images/character1.png,input/images/character2.png" \
  --prompt "The character walks through the scene"
```

### Reference Video (Motion Transfer)
```bash
# Seedance - use reference video for motion
ai-content-pipeline generate-video \
  --model seedance_1_5_pro \
  --image "input/images/person.png" \
  --ref-video "input/videos/dance_reference.mp4" \
  --prompt "Person performs the dance moves"
```

### Audio Generation
```bash
# Veo 3.1 Fast - with audio
ai-content-pipeline generate-video \
  --model veo_3_1_fast \
  --image "input/images/scene.png" \
  --prompt "Waves crash on the beach with seagulls calling" \
  --generate-audio true

# Veo 3.1 Fast - without audio
ai-content-pipeline generate-video \
  --model veo_3_1_fast \
  --image "input/images/scene.png" \
  --prompt "Silent nature scene" \
  --generate-audio false
```

## YAML Pipeline Examples

### Frame Interpolation Pipeline
```yaml
name: "Frame Interpolation Video"
description: "Create video transitioning between two images"

steps:
  - name: "interpolate_video"
    type: "image-to-video"
    model: "sora_2_pro"
    params:
      start_frame: "input/images/morning.png"
      end_frame: "input/images/evening.png"
      prompt: "Time-lapse from morning to evening, sun moves across the sky"
      duration: 8
      resolution: "1080p"
```

### Character Consistent Video
```yaml
name: "Character Video with References"
description: "Generate video maintaining character consistency"

steps:
  - name: "character_video"
    type: "image-to-video"
    model: "seedance_1_5_pro"
    params:
      image: "input/images/scene.png"
      ref_images:
        - "input/images/character_front.png"
        - "input/images/character_side.png"
      prompt: "The character turns and walks toward the camera"
      duration: "10"
```

### Motion Transfer Pipeline
```yaml
name: "Motion Transfer Video"
description: "Apply motion from reference video to image"

steps:
  - name: "motion_transfer"
    type: "image-to-video"
    model: "seedance_1_5_pro"
    params:
      image: "input/images/portrait.png"
      ref_video: "input/videos/talking_head.mp4"
      prompt: "Person speaks naturally with head movements"
      duration: "10"
```

## Implementation Summary

| Task | File | Estimated Time |
|------|------|----------------|
| 1. Update Base Model | models/base.py | 15 min |
| 2. File Upload Utils | utils/file_utils.py | 20 min |
| 3. Update Sora Models | models/sora.py | 20 min |
| 4. Update Kling Models | models/kling.py | 20 min |
| 5. Update Seedance | models/seedance.py | 25 min |
| 6. Update Veo | models/veo.py | 15 min |
| 7. Update Generator | generator.py | 25 min |
| 8. Update Constants | config/constants.py | 10 min |
| 9. Unit Tests | tests/test_extended_parameters.py | 30 min |
| 10. Documentation | REFERENCE.md | 15 min |

**Total Estimated Time:** ~3 hours

## Validation Checklist

- [ ] All local file paths are uploaded before API calls
- [ ] Unsupported parameters are ignored gracefully per model
- [ ] Error messages indicate which model supports which features
- [ ] Unit tests cover all parameter combinations
- [ ] CLI help text documents new parameters
- [ ] YAML config supports all new parameters
