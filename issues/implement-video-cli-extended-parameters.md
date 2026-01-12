# Implement Extended Video CLI Parameters

## Overview

Add support for advanced video generation parameters across all image-to-video models in the AI Content Pipeline CLI. This implementation follows the existing modular architecture pattern and ensures long-term maintainability.

## New Parameters

| Parameter | Type | Description | Use Case |
|-----------|------|-------------|----------|
| `start_frame` | image path/URL | Starting frame image | Control video start appearance |
| `end_frame` | image path/URL | Ending frame image | Frame interpolation between two images |
| `ref_images` | list of paths/URLs | Reference images for style/character | Maintain visual consistency |
| `audio` | audio file path/URL | Audio input for synchronization | Lip-sync, music videos, voiceover |
| `ref_video` | video file path/URL | Reference video for motion/style | Motion transfer, style reference |

## Current Architecture Analysis

### Existing File Structure
```
packages/providers/fal/image-to-video/fal_image_to_video/
├── __init__.py
├── generator.py              # FALImageToVideoGenerator class
├── config/
│   └── constants.py          # MODEL_ENDPOINTS, MODEL_PRICING, etc.
├── models/
│   ├── __init__.py
│   ├── base.py               # BaseVideoModel abstract class
│   ├── hailuo.py             # HailuoModel
│   ├── kling.py              # KlingModel, Kling26ProModel
│   ├── seedance.py           # SeedanceModel
│   ├── sora.py               # Sora2Model, Sora2ProModel
│   └── veo.py                # Veo31FastModel
└── utils/
    ├── __init__.py
    ├── file_utils.py         # upload_image, download_video, ensure_output_directory
    └── validators.py
```

### Key Existing Methods

**BaseVideoModel (base.py:14-213)**
```python
class BaseVideoModel(ABC):
    @abstractmethod
    def validate_parameters(self, **kwargs) -> Dict[str, Any]: ...
    @abstractmethod
    def prepare_arguments(self, prompt: str, image_url: str, **kwargs) -> Dict[str, Any]: ...
    def generate(self, prompt: str, image_url: str, ...) -> Dict[str, Any]: ...
```

**file_utils.py (current functions)**
```python
def ensure_output_directory(output_dir: Optional[str] = None) -> Path
def download_video(video_url: str, output_dir: Path, model_key: str, ...) -> Optional[str]
def upload_image(image_path: str) -> Optional[str]
```

## Model Support Matrix (Based on FAL AI API)

| Model | start_frame | end_frame | ref_images | audio_input | ref_video |
|-------|-------------|-----------|------------|-------------|-----------|
| Veo 3.1 Fast | ✅ image_url | ❌ | ❌ | ✅ generate_audio | ❌ |
| Sora 2 | ✅ image_url | ❌ | ❌ | ❌ | ❌ |
| Sora 2 Pro | ✅ image_url | ❌ | ❌ | ❌ | ❌ |
| Kling v2.1 | ✅ image_url | ✅ tail_image_url | ❌ | ❌ | ❌ |
| Kling v2.6 Pro | ✅ image_url | ✅ tail_image_url | ❌ | ❌ | ❌ |
| Hailuo | ✅ image_url | ❌ | ❌ | ❌ | ❌ |
| Seedance | ✅ image_url | ❌ | ❌ | ❌ | ❌ |

**Note:** FAL AI API documentation should be verified for actual parameter support. The matrix above is based on common video model capabilities.

---

## Implementation Plan

### Phase 1: Core Infrastructure (Foundation)

#### Task 1.1: Extend File Utilities
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/utils/file_utils.py`

**Add to existing file (after line 95):**

```python
from typing import List

# Supported file formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi', '.webm', '.mkv']


def is_url(path: str) -> bool:
    """Check if path is a URL."""
    return path.startswith(('http://', 'https://'))


def validate_file_format(file_path: str, supported_formats: List[str], file_type: str) -> None:
    """
    Validate file format against supported formats.

    Args:
        file_path: Path to validate
        supported_formats: List of supported extensions
        file_type: Type description for error message

    Raises:
        ValueError: If format is not supported
    """
    if is_url(file_path):
        return  # URLs are assumed valid

    ext = Path(file_path).suffix.lower()
    if ext not in supported_formats:
        raise ValueError(
            f"Unsupported {file_type} format: {ext}. "
            f"Supported formats: {supported_formats}"
        )


def upload_file(file_path: str) -> Optional[str]:
    """
    Upload any local file to FAL AI.

    Args:
        file_path: Path to local file or URL

    Returns:
        URL of uploaded file, or original URL if already a URL
    """
    if is_url(file_path):
        return file_path

    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None

        print(f"📤 Uploading file: {file_path}")
        url = fal_client.upload_file(file_path)
        print(f"✅ File uploaded: {url[:50]}...")
        return url

    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None


def upload_images(image_paths: List[str]) -> List[str]:
    """
    Upload multiple images and return URLs.

    Args:
        image_paths: List of image paths or URLs

    Returns:
        List of image URLs
    """
    urls = []
    for path in image_paths:
        validate_file_format(path, SUPPORTED_IMAGE_FORMATS, "image")
        url = upload_file(path)
        if url:
            urls.append(url)
        else:
            raise ValueError(f"Failed to upload image: {path}")
    return urls


def upload_audio(audio_path: str) -> Optional[str]:
    """
    Upload audio file and return URL.

    Args:
        audio_path: Path to audio file or URL

    Returns:
        URL of uploaded audio
    """
    validate_file_format(audio_path, SUPPORTED_AUDIO_FORMATS, "audio")
    return upload_file(audio_path)


def upload_video(video_path: str) -> Optional[str]:
    """
    Upload video file and return URL.

    Args:
        video_path: Path to video file or URL

    Returns:
        URL of uploaded video
    """
    validate_file_format(video_path, SUPPORTED_VIDEO_FORMATS, "video")
    return upload_file(video_path)
```

---

#### Task 1.2: Update Constants with Feature Matrix
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`

**Add after MODEL_INFO (line 182):**

```python
# Extended parameter support per model
# This matrix defines which advanced parameters each model supports
MODEL_EXTENDED_FEATURES = {
    "hailuo": {
        "start_frame": True,      # image_url
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "kling_2_1": {
        "start_frame": True,      # image_url
        "end_frame": True,        # tail_image_url
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "kling_2_6_pro": {
        "start_frame": True,      # image_url
        "end_frame": True,        # tail_image_url
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "seedance_1_5_pro": {
        "start_frame": True,      # image_url
        "end_frame": False,
        "ref_images": False,      # May support in future API versions
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "sora_2": {
        "start_frame": True,      # image_url
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "sora_2_pro": {
        "start_frame": True,      # image_url
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,
        "audio_generate": False,
        "ref_video": False,
    },
    "veo_3_1_fast": {
        "start_frame": True,      # image_url
        "end_frame": False,
        "ref_images": False,
        "audio_input": False,     # Only supports audio generation, not input
        "audio_generate": True,   # generate_audio parameter
        "ref_video": False,
    },
}

# API parameter mapping for extended features
# Maps our parameter names to actual API parameter names
EXTENDED_PARAM_MAPPING = {
    "start_frame": "image_url",
    "end_frame": {
        "kling_2_1": "tail_image_url",
        "kling_2_6_pro": "tail_image_url",
    },
    "audio_generate": "generate_audio",
}
```

---

### Phase 2: Model Updates

#### Task 2.1: Update Kling Models (end_frame support)
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/models/kling.py`

**Replace prepare_arguments in KlingModel (line 50-63):**

```python
def prepare_arguments(
    self,
    prompt: str,
    image_url: str,
    **kwargs
) -> Dict[str, Any]:
    """Prepare API arguments for Kling v2.1."""
    args = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": kwargs.get("duration", "5"),
        "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
        "cfg_scale": kwargs.get("cfg_scale", 0.5)
    }

    # Add end frame for interpolation (tail_image_url)
    end_frame = kwargs.get("end_frame")
    if end_frame:
        args["tail_image_url"] = end_frame

    return args
```

**Replace prepare_arguments in Kling26ProModel (line 114-127):**

```python
def prepare_arguments(
    self,
    prompt: str,
    image_url: str,
    **kwargs
) -> Dict[str, Any]:
    """Prepare API arguments for Kling v2.6 Pro."""
    args = {
        "prompt": prompt,
        "image_url": image_url,
        "duration": kwargs.get("duration", "5"),
        "negative_prompt": kwargs.get("negative_prompt", "blur, distort, and low quality"),
        "cfg_scale": kwargs.get("cfg_scale", 0.5)
    }

    # Add end frame for interpolation (tail_image_url)
    end_frame = kwargs.get("end_frame")
    if end_frame:
        args["tail_image_url"] = end_frame

    return args
```

**Update validate_parameters in both Kling classes to include end_frame:**

```python
def validate_parameters(self, **kwargs) -> Dict[str, Any]:
    """Validate Kling parameters."""
    defaults = DEFAULT_VALUES.get(self.model_key, {})

    duration = kwargs.get("duration", defaults.get("duration", "5"))
    negative_prompt = kwargs.get("negative_prompt", defaults.get("negative_prompt", "blur, distort, and low quality"))
    cfg_scale = kwargs.get("cfg_scale", defaults.get("cfg_scale", 0.5))
    end_frame = kwargs.get("end_frame")  # Optional end frame

    # Validate duration
    valid_durations = DURATION_OPTIONS.get(self.model_key, ["5", "10"])
    if duration not in valid_durations:
        raise ValueError(f"Invalid duration: {duration}. Valid: {valid_durations}")

    # Validate cfg_scale
    if not 0.0 <= cfg_scale <= 1.0:
        raise ValueError(f"cfg_scale must be between 0.0 and 1.0, got: {cfg_scale}")

    return {
        "duration": duration,
        "negative_prompt": negative_prompt,
        "cfg_scale": cfg_scale,
        "end_frame": end_frame  # Pass through for prepare_arguments
    }
```

---

#### Task 2.2: Update MODEL_INFO for Extended Features
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/config/constants.py`

**Update MODEL_INFO entries to include extended feature documentation:**

```python
MODEL_INFO = {
    "hailuo": {
        "name": "MiniMax Hailuo-02",
        "provider": "MiniMax",
        "description": "Standard image-to-video with prompt optimization",
        "max_duration": 10,
        "features": ["prompt_optimizer"],
        "extended_params": ["start_frame"]
    },
    "kling_2_1": {
        "name": "Kling Video v2.1",
        "provider": "Kuaishou",
        "description": "High-quality generation with negative prompts and frame interpolation",
        "max_duration": 10,
        "features": ["negative_prompt", "cfg_scale", "frame_interpolation"],
        "extended_params": ["start_frame", "end_frame"]
    },
    "kling_2_6_pro": {
        "name": "Kling Video v2.6 Pro",
        "provider": "Kuaishou",
        "description": "Professional tier with enhanced quality and frame interpolation",
        "max_duration": 10,
        "features": ["negative_prompt", "cfg_scale", "professional_quality", "frame_interpolation"],
        "extended_params": ["start_frame", "end_frame"]
    },
    "seedance_1_5_pro": {
        "name": "ByteDance Seedance v1.5 Pro",
        "provider": "ByteDance",
        "description": "Advanced motion synthesis with seed control",
        "max_duration": 10,
        "features": ["seed_control", "motion_quality"],
        "extended_params": ["start_frame"]
    },
    "sora_2": {
        "name": "Sora 2",
        "provider": "OpenAI (via FAL)",
        "description": "OpenAI's image-to-video model",
        "max_duration": 12,
        "features": ["aspect_ratio", "resolution"],
        "extended_params": ["start_frame"]
    },
    "sora_2_pro": {
        "name": "Sora 2 Pro",
        "provider": "OpenAI (via FAL)",
        "description": "Professional Sora with 1080p support",
        "max_duration": 12,
        "features": ["aspect_ratio", "resolution", "1080p"],
        "extended_params": ["start_frame"]
    },
    "veo_3_1_fast": {
        "name": "Veo 3.1 Fast",
        "provider": "Google (via FAL)",
        "description": "Fast video generation with optional audio",
        "max_duration": 8,
        "features": ["audio_generation", "auto_fix", "fast_processing"],
        "extended_params": ["start_frame", "audio_generate"]
    }
}
```

---

### Phase 3: Generator Updates

#### Task 3.1: Update Generator with Extended Parameters
**File:** `packages/providers/fal/image-to-video/fal_image_to_video/generator.py`

**Update imports (line 8):**

```python
from typing import Dict, Any, Optional, List
```

**Update import from file_utils (line 21):**

```python
from .utils.file_utils import (
    upload_image,
    upload_file,
    upload_images,
    upload_audio,
    upload_video,
    ensure_output_directory,
    is_url
)
```

**Add import for feature matrix (line 22):**

```python
from .config.constants import SUPPORTED_MODELS, MODEL_INFO, MODEL_EXTENDED_FEATURES
```

**Update generate_video method (replace lines 79-125):**

```python
def generate_video(
    self,
    prompt: str,
    image_url: str,
    model: str = "hailuo",
    output_dir: Optional[str] = None,
    use_async: bool = False,
    # Extended parameters
    start_frame: Optional[str] = None,
    end_frame: Optional[str] = None,
    ref_images: Optional[List[str]] = None,
    audio: Optional[str] = None,
    ref_video: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate video from image using specified model.

    Args:
        prompt: Text description for video generation
        image_url: URL of input image (or use start_frame)
        model: Model to use (default: "hailuo")
        output_dir: Custom output directory
        use_async: Whether to use async processing
        start_frame: Starting frame image (overrides image_url if provided)
        end_frame: Ending frame image for interpolation (Kling models)
        ref_images: Reference images for consistency (future support)
        audio: Audio file for synchronization (future support)
        ref_video: Reference video for motion/style (future support)
        **kwargs: Model-specific parameters

    Returns:
        Dictionary containing generation results
    """
    # Mock mode for CI
    if self.mock_mode:
        import time
        return {
            'success': True,
            'video': {'url': f'mock://video-{int(time.time())}.mp4'},
            'local_path': f'/tmp/mock_video_{int(time.time())}.mp4',
            'model': model,
            'mock_mode': True
        }

    if model not in self.models:
        raise ValueError(
            f"Unsupported model: {model}. "
            f"Supported: {list(self.models.keys())}"
        )

    # Get model feature support
    features = MODEL_EXTENDED_FEATURES.get(model, {})

    # Process start_frame (overrides image_url)
    effective_image_url = image_url
    if start_frame:
        if not is_url(start_frame):
            effective_image_url = upload_file(start_frame)
            if not effective_image_url:
                return {
                    "success": False,
                    "error": f"Failed to upload start_frame: {start_frame}",
                    "model": model
                }
        else:
            effective_image_url = start_frame

    # Process end_frame if supported
    if end_frame:
        if not features.get("end_frame"):
            print(f"⚠️ Model {model} does not support end_frame parameter, ignoring")
        else:
            if not is_url(end_frame):
                end_frame = upload_file(end_frame)
                if not end_frame:
                    return {
                        "success": False,
                        "error": f"Failed to upload end_frame",
                        "model": model
                    }
            kwargs["end_frame"] = end_frame

    # Process ref_images if supported
    if ref_images:
        if not features.get("ref_images"):
            print(f"⚠️ Model {model} does not support ref_images parameter, ignoring")
        else:
            kwargs["ref_images"] = upload_images(ref_images)

    # Process audio if supported
    if audio:
        if not features.get("audio_input"):
            print(f"⚠️ Model {model} does not support audio input parameter, ignoring")
        else:
            if not is_url(audio):
                audio = upload_audio(audio)
                if not audio:
                    return {
                        "success": False,
                        "error": f"Failed to upload audio",
                        "model": model
                    }
            kwargs["audio_url"] = audio

    # Process ref_video if supported
    if ref_video:
        if not features.get("ref_video"):
            print(f"⚠️ Model {model} does not support ref_video parameter, ignoring")
        else:
            if not is_url(ref_video):
                ref_video = upload_video(ref_video)
                if not ref_video:
                    return {
                        "success": False,
                        "error": f"Failed to upload ref_video",
                        "model": model
                    }
            kwargs["ref_video_url"] = ref_video

    return self.models[model].generate(
        prompt=prompt,
        image_url=effective_image_url,
        output_dir=output_dir,
        use_async=use_async,
        **kwargs
    )
```

**Add new convenience method for frame interpolation:**

```python
def generate_with_interpolation(
    self,
    prompt: str,
    start_frame: str,
    end_frame: str,
    model: str = "kling_2_6_pro",
    duration: str = "5",
    **kwargs
) -> Dict[str, Any]:
    """
    Generate video interpolating between two frames.

    Only supported by Kling models.

    Args:
        prompt: Text description for video generation
        start_frame: Starting frame image path/URL
        end_frame: Ending frame image path/URL
        model: Model to use (default: "kling_2_6_pro")
        duration: Video duration
        **kwargs: Additional parameters

    Returns:
        Dictionary containing generation results
    """
    if model not in ["kling_2_1", "kling_2_6_pro"]:
        raise ValueError(
            f"Frame interpolation only supported by Kling models. "
            f"Got: {model}"
        )

    return self.generate_video(
        prompt=prompt,
        image_url=start_frame,  # Will be overridden by start_frame
        model=model,
        start_frame=start_frame,
        end_frame=end_frame,
        duration=duration,
        **kwargs
    )
```

**Add method to check model feature support:**

```python
def get_model_features(self, model: str) -> Dict[str, bool]:
    """
    Get extended feature support for a model.

    Args:
        model: Model key

    Returns:
        Dictionary of feature support flags
    """
    if model not in MODEL_EXTENDED_FEATURES:
        raise ValueError(f"Unknown model: {model}")
    return MODEL_EXTENDED_FEATURES[model].copy()

def supports_feature(self, model: str, feature: str) -> bool:
    """
    Check if a model supports a specific feature.

    Args:
        model: Model key
        feature: Feature name (start_frame, end_frame, ref_images, etc.)

    Returns:
        True if feature is supported
    """
    features = MODEL_EXTENDED_FEATURES.get(model, {})
    return features.get(feature, False)
```

---

### Phase 4: Unit Tests

#### Task 4.1: Create Extended Parameters Tests
**File:** `packages/providers/fal/image-to-video/tests/test_extended_parameters.py`

```python
"""
Unit tests for extended video parameters.
"""

import pytest
from pathlib import Path

# Add package to path
import sys
_package_path = Path(__file__).parent.parent / "fal_image_to_video"
sys.path.insert(0, str(_package_path.parent))

from fal_image_to_video.models.kling import KlingModel, Kling26ProModel
from fal_image_to_video.config.constants import MODEL_EXTENDED_FEATURES
from fal_image_to_video.utils.file_utils import (
    is_url,
    validate_file_format,
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_AUDIO_FORMATS,
    SUPPORTED_VIDEO_FORMATS
)


class TestFileUtilities:
    """Tests for file utility functions."""

    def test_is_url_with_http(self):
        """HTTP URLs should be recognized."""
        assert is_url("http://example.com/image.jpg") is True

    def test_is_url_with_https(self):
        """HTTPS URLs should be recognized."""
        assert is_url("https://example.com/image.jpg") is True

    def test_is_url_with_local_path(self):
        """Local paths should not be URLs."""
        assert is_url("/path/to/file.jpg") is False
        assert is_url("C:\\path\\to\\file.jpg") is False

    def test_validate_image_format_valid(self):
        """Valid image formats should pass."""
        for fmt in SUPPORTED_IMAGE_FORMATS:
            validate_file_format(f"test{fmt}", SUPPORTED_IMAGE_FORMATS, "image")

    def test_validate_image_format_invalid(self):
        """Invalid image formats should raise error."""
        with pytest.raises(ValueError) as exc_info:
            validate_file_format("test.xyz", SUPPORTED_IMAGE_FORMATS, "image")
        assert "Unsupported image format" in str(exc_info.value)

    def test_validate_audio_format_valid(self):
        """Valid audio formats should pass."""
        for fmt in SUPPORTED_AUDIO_FORMATS:
            validate_file_format(f"test{fmt}", SUPPORTED_AUDIO_FORMATS, "audio")

    def test_validate_video_format_valid(self):
        """Valid video formats should pass."""
        for fmt in SUPPORTED_VIDEO_FORMATS:
            validate_file_format(f"test{fmt}", SUPPORTED_VIDEO_FORMATS, "video")


class TestKlingEndFrame:
    """Tests for Kling end_frame support."""

    def test_kling_prepare_arguments_with_end_frame(self):
        """End frame should be included as tail_image_url."""
        model = KlingModel()
        args = model.prepare_arguments(
            prompt="Test prompt",
            image_url="http://example.com/start.jpg",
            end_frame="http://example.com/end.jpg",
            duration="5"
        )
        assert args.get("tail_image_url") == "http://example.com/end.jpg"

    def test_kling_prepare_arguments_without_end_frame(self):
        """Without end_frame, tail_image_url should not be present."""
        model = KlingModel()
        args = model.prepare_arguments(
            prompt="Test prompt",
            image_url="http://example.com/start.jpg",
            duration="5"
        )
        assert "tail_image_url" not in args

    def test_kling_pro_prepare_arguments_with_end_frame(self):
        """Kling Pro should also support end_frame."""
        model = Kling26ProModel()
        args = model.prepare_arguments(
            prompt="Test prompt",
            image_url="http://example.com/start.jpg",
            end_frame="http://example.com/end.jpg",
            duration="5"
        )
        assert args.get("tail_image_url") == "http://example.com/end.jpg"


class TestModelFeatureMatrix:
    """Tests for model feature matrix."""

    def test_all_models_have_features(self):
        """All supported models should have feature definitions."""
        expected_models = [
            "hailuo", "kling_2_1", "kling_2_6_pro",
            "seedance_1_5_pro", "sora_2", "sora_2_pro", "veo_3_1_fast"
        ]
        for model in expected_models:
            assert model in MODEL_EXTENDED_FEATURES

    def test_all_features_defined(self):
        """All models should define all expected features."""
        expected_features = [
            "start_frame", "end_frame", "ref_images",
            "audio_input", "audio_generate", "ref_video"
        ]
        for model, features in MODEL_EXTENDED_FEATURES.items():
            for feature in expected_features:
                assert feature in features, f"{model} missing {feature}"

    def test_kling_supports_end_frame(self):
        """Kling models should support end_frame."""
        assert MODEL_EXTENDED_FEATURES["kling_2_1"]["end_frame"] is True
        assert MODEL_EXTENDED_FEATURES["kling_2_6_pro"]["end_frame"] is True

    def test_veo_supports_audio_generate(self):
        """Veo 3.1 Fast should support audio generation."""
        assert MODEL_EXTENDED_FEATURES["veo_3_1_fast"]["audio_generate"] is True

    def test_other_models_no_end_frame(self):
        """Non-Kling models should not support end_frame."""
        non_kling = ["hailuo", "seedance_1_5_pro", "sora_2", "sora_2_pro", "veo_3_1_fast"]
        for model in non_kling:
            assert MODEL_EXTENDED_FEATURES[model]["end_frame"] is False


class TestValidateParameters:
    """Tests for parameter validation with extended params."""

    def test_kling_validate_with_end_frame(self):
        """Kling validation should accept end_frame."""
        model = KlingModel()
        params = model.validate_parameters(
            duration="5",
            end_frame="http://example.com/end.jpg"
        )
        assert params["end_frame"] == "http://example.com/end.jpg"

    def test_kling_validate_without_end_frame(self):
        """Kling validation should work without end_frame."""
        model = KlingModel()
        params = model.validate_parameters(duration="5")
        assert params.get("end_frame") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

### Phase 5: Documentation Updates

#### Task 5.1: Update REFERENCE.md
**File:** `.claude/skills/ai-content-pipeline/REFERENCE.md`

**Add section after Video Generation parameters:**

```markdown
### Extended Video Parameters

#### Frame Interpolation (Kling models only)
```yaml
params:
  start_frame: "input/images/morning.png"
  end_frame: "input/images/evening.png"
  prompt: "Time-lapse transition"
  duration: "10"
```

#### Audio Generation (Veo 3.1 Fast only)
```yaml
params:
  image: "input/images/scene.png"
  prompt: "Ocean waves with seagulls"
  generate_audio: true
  duration: "8s"
```

### Model Extended Feature Support

| Feature | Hailuo | Kling | Seedance | Sora | Veo 3.1 |
|---------|--------|-------|----------|------|---------|
| start_frame | ✅ | ✅ | ✅ | ✅ | ✅ |
| end_frame | ❌ | ✅ | ❌ | ❌ | ❌ |
| audio_generate | ❌ | ❌ | ❌ | ❌ | ✅ |
```

---

## Implementation Summary

| Phase | Task | File | Estimated Time |
|-------|------|------|----------------|
| 1.1 | Extend File Utilities | utils/file_utils.py | 20 min |
| 1.2 | Update Constants | config/constants.py | 15 min |
| 2.1 | Update Kling Models | models/kling.py | 20 min |
| 2.2 | Update MODEL_INFO | config/constants.py | 10 min |
| 3.1 | Update Generator | generator.py | 30 min |
| 4.1 | Unit Tests | tests/test_extended_parameters.py | 25 min |
| 5.1 | Documentation | REFERENCE.md | 15 min |

**Total Estimated Time:** ~2.5 hours

---

## CLI Usage Examples

### Frame Interpolation
```bash
# Using Kling Pro for frame interpolation
ai-content-pipeline generate-video \
  --model kling_2_6_pro \
  --start-frame "input/images/start.png" \
  --end-frame "input/images/end.png" \
  --prompt "Smooth morphing transition" \
  --duration "10"
```

### Audio Generation
```bash
# Using Veo 3.1 Fast with audio
ai-content-pipeline generate-video \
  --model veo_3_1_fast \
  --image "input/images/beach.png" \
  --prompt "Waves crashing on shore with seagulls" \
  --generate-audio true \
  --duration "8s"
```

---

## YAML Pipeline Examples

### Frame Interpolation Pipeline
```yaml
name: "Day to Night Transition"
description: "Create video interpolating between morning and evening images"

steps:
  - name: "interpolate"
    type: "image-to-video"
    model: "kling_2_6_pro"
    params:
      start_frame: "input/images/morning_cityscape.png"
      end_frame: "input/images/evening_cityscape.png"
      prompt: "Time-lapse of city transitioning from day to night, lights turning on"
      duration: "10"
      negative_prompt: "blur, distortion, artifacts"
```

---

## Future Extensions

The architecture supports future additions when FAL AI APIs add support:

1. **ref_images**: Character/style consistency across generations
2. **audio_input**: External audio for lip-sync/voiceover
3. **ref_video**: Motion transfer from reference videos

These can be enabled by updating `MODEL_EXTENDED_FEATURES` when API support is confirmed.

---

## Validation Checklist

- [ ] All local file paths are uploaded before API calls
- [ ] Unsupported parameters generate warnings (not errors)
- [ ] Feature matrix is easily extensible
- [ ] Unit tests cover all parameter combinations
- [ ] Documentation reflects actual API capabilities
- [ ] Backwards compatible with existing code
