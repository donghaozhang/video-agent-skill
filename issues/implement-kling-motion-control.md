# Implementation Plan: Kling Video v2.6 Motion Control

## Overview

Add support for the **Kling Video v2.6 Standard Motion Control** model (`fal-ai/kling-video/v2.6/standard/motion-control`) to the **Avatar Generation** package.

This model belongs in the avatar package (not image-to-video) because it requires **both image and video inputs** - similar to other Kling video-to-video models already in the avatar package (`kling_v2v_reference`, `kling_v2v_edit`).

## API Reference

**Endpoint:** `fal-ai/kling-video/v2.6/standard/motion-control`

### Input Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `image_url` | string | ✓ | Reference image URL - characters/backgrounds in generated video are based on this | - |
| `video_url` | string | ✓ | Reference video URL - character actions will match this video's motion | - |
| `character_orientation` | enum | ✓ | Output orientation: `video` (max 30s) or `image` (max 10s) | - |
| `keep_original_sound` | boolean | ✗ | Keep original audio from reference video | `true` |
| `prompt` | string | ✗ | Optional text description to guide generation | - |

### Output Schema

```json
{
  "video": {
    "file_size": integer,
    "file_name": "output.mp4",
    "content_type": "video/mp4",
    "url": "string"
  }
}
```

### Key Features
- **Motion Transfer**: Transfer movements from reference video to image
- **Dual Orientation**: `video` mode (up to 30s), `image` mode (up to 10s)
- **Audio Preservation**: Option to keep original sound from reference video
- **Standard Tier**: Cost-effective alternative to Pro models

### Estimated Pricing
- **Base Rate**: ~$0.06/second (estimated, standard tier pricing)

---

## Implementation Tasks

**Total Estimated Time:** ~25-30 minutes

---

### Subtask 1: Add Model Constants (5 min)

**File:** `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py`

Add the following entries:

```python
# In MODEL_ENDPOINTS (line ~4)
MODEL_ENDPOINTS = {
    ...
    "kling_motion_control": "fal-ai/kling-video/v2.6/standard/motion-control",  # NEW
}

# In MODEL_DISPLAY_NAMES (line ~16)
MODEL_DISPLAY_NAMES = {
    ...
    "kling_motion_control": "Kling v2.6 Motion Control",  # NEW
}

# In MODEL_PRICING (line ~28)
MODEL_PRICING = {
    ...
    "kling_motion_control": {"per_second": 0.06},  # NEW - Standard tier pricing
}

# In MODEL_DEFAULTS (line ~40)
MODEL_DEFAULTS = {
    ...
    "kling_motion_control": {  # NEW
        "character_orientation": "video",
        "keep_original_sound": True,
    },
}

# In SUPPORTED_RESOLUTIONS (line ~72) - No resolution param, uses orientation
SUPPORTED_RESOLUTIONS = {
    ...
    "kling_motion_control": [],  # Uses character_orientation instead
}

# In SUPPORTED_ASPECT_RATIOS (line ~85) - No aspect ratio param
SUPPORTED_ASPECT_RATIOS = {
    ...
    "kling_motion_control": [],  # Determined by input image/video
}

# In MAX_DURATIONS (line ~92)
MAX_DURATIONS = {
    ...
    "kling_motion_control": {"video": 30, "image": 10},  # NEW - Depends on orientation
}

# In PROCESSING_TIME_ESTIMATES (line ~103)
PROCESSING_TIME_ESTIMATES = {
    ...
    "kling_motion_control": 60,  # NEW
}

# In INPUT_REQUIREMENTS (line ~115)
INPUT_REQUIREMENTS = {
    ...
    "kling_motion_control": {  # NEW
        "required": ["image_url", "video_url", "character_orientation"],
        "optional": ["keep_original_sound", "prompt"],
    },
}

# In MODEL_CATEGORIES (line ~151)
MODEL_CATEGORIES = {
    ...
    "motion_transfer": ["kling_motion_control"],  # NEW category
}

# In MODEL_RECOMMENDATIONS (line ~159)
MODEL_RECOMMENDATIONS = {
    ...
    "motion_transfer": "kling_motion_control",  # NEW
    "dance_video": "kling_motion_control",       # NEW
}
```

---

### Subtask 2: Create Model Class (10 min)

**File:** `packages/providers/fal/avatar-generation/fal_avatar/models/kling.py`

Add new class after `KlingV2VEditModel`:

```python
class KlingMotionControlModel(BaseAvatarModel):
    """
    Kling Video v2.6 Motion Control - Motion transfer from video to image.

    Transfers motion from a reference video to a reference image,
    creating videos where the image's subjects mimic the video's movements.

    Use Cases:
    - Dance videos: Transfer dance moves to a person image
    - Action sequences: Apply motion patterns to characters
    - Character animation: Animate still images with video motion

    API Parameters:
        - image_url: Reference image URL (characters/background source)
        - video_url: Reference video URL (motion source)
        - character_orientation: "video" (max 30s) or "image" (max 10s)
        - keep_original_sound: Preserve reference video audio
        - prompt: Optional text description

    Pricing: ~$0.06/second (standard tier)
    Max Duration: 30s (video orientation) or 10s (image orientation)
    """

    def __init__(self):
        """Initialize Kling Motion Control model."""
        super().__init__("kling_motion_control")
        self.endpoint = MODEL_ENDPOINTS["kling_motion_control"]
        self.pricing = MODEL_PRICING["kling_motion_control"]
        self.defaults = MODEL_DEFAULTS["kling_motion_control"]
        self.max_durations = MAX_DURATIONS["kling_motion_control"]

    def validate_parameters(
        self,
        image_url: str,
        video_url: str,
        character_orientation: Optional[str] = None,
        keep_original_sound: Optional[bool] = None,
        prompt: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Validate parameters for Kling Motion Control.

        Args:
            image_url: Reference image URL (characters/background source)
            video_url: Reference video URL (motion source)
            character_orientation: "video" (max 30s) or "image" (max 10s)
            keep_original_sound: Keep audio from reference video
            prompt: Optional text description

        Returns:
            Dict of validated parameters

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate required URLs
        self._validate_url(image_url, "image_url")
        self._validate_url(video_url, "video_url")

        # Apply defaults
        character_orientation = character_orientation or self.defaults["character_orientation"]
        if keep_original_sound is None:
            keep_original_sound = self.defaults["keep_original_sound"]

        # Validate character_orientation
        valid_orientations = ["video", "image"]
        if character_orientation not in valid_orientations:
            raise ValueError(
                f"character_orientation must be one of {valid_orientations}, "
                f"got: '{character_orientation}'"
            )

        arguments = {
            "image_url": image_url,
            "video_url": video_url,
            "character_orientation": character_orientation,
            "keep_original_sound": keep_original_sound,
        }

        # Add optional prompt
        if prompt:
            arguments["prompt"] = prompt

        return arguments

    def generate(
        self,
        image_url: str = None,
        video_url: str = None,
        character_orientation: Optional[str] = None,
        keep_original_sound: Optional[bool] = None,
        prompt: Optional[str] = None,
        **kwargs,
    ) -> AvatarGenerationResult:
        """
        Generate motion-controlled video.

        Args:
            image_url: Reference image URL (characters/background source)
            video_url: Reference video URL (motion source)
            character_orientation: "video" (max 30s) or "image" (max 10s)
            keep_original_sound: Keep audio from reference video
            prompt: Optional text description

        Returns:
            AvatarGenerationResult with video URL and metadata
        """
        try:
            arguments = self.validate_parameters(
                image_url=image_url,
                video_url=video_url,
                character_orientation=character_orientation,
                keep_original_sound=keep_original_sound,
                prompt=prompt,
                **kwargs,
            )

            response = self._call_fal_api(arguments)

            if not response["success"]:
                return AvatarGenerationResult(
                    success=False,
                    error=response["error"],
                    model_used=self.model_name,
                    processing_time=response.get("processing_time"),
                )

            result = response["result"]

            # Get max duration based on orientation
            orientation = arguments["character_orientation"]
            max_duration = self.max_durations.get(orientation, 10)

            # Use video duration from result if available, otherwise estimate
            video_duration = result.get("duration", max_duration)

            return AvatarGenerationResult(
                success=True,
                video_url=result["video"]["url"],
                duration=video_duration,
                cost=self.estimate_cost(video_duration, character_orientation=orientation),
                processing_time=response["processing_time"],
                model_used=self.model_name,
                metadata={
                    "character_orientation": orientation,
                    "keep_original_sound": arguments["keep_original_sound"],
                    "file_size": result["video"].get("file_size"),
                    "file_name": result["video"].get("file_name"),
                },
            )

        except Exception as e:
            return AvatarGenerationResult(
                success=False,
                error=str(e),
                model_used=self.model_name,
            )

    def estimate_cost(self, duration: float, **kwargs) -> float:
        """
        Estimate cost based on duration.

        Args:
            duration: Video duration in seconds
            character_orientation: Optional orientation to cap duration

        Returns:
            Estimated cost in USD
        """
        orientation = kwargs.get("character_orientation", "video")
        max_duration = self.max_durations.get(orientation, 30)
        effective_duration = min(duration, max_duration)
        return effective_duration * self.pricing["per_second"]

    def get_model_info(self) -> Dict[str, Any]:
        """Return model info."""
        return {
            "name": self.model_name,
            "display_name": "Kling v2.6 Motion Control",
            "endpoint": self.endpoint,
            "pricing": self.pricing,
            "max_durations": self.max_durations,
            "orientation_options": ["video", "image"],
            "input_types": ["image", "video"],
            "description": "Motion transfer from reference video to reference image",
            "best_for": ["dance videos", "action sequences", "character animation", "motion transfer"],
            "commercial_use": True,
        }
```

---

### Subtask 3: Update Model Exports (2 min)

**File:** `packages/providers/fal/avatar-generation/fal_avatar/models/__init__.py`

```python
"""FAL Avatar model exports."""

from .base import BaseAvatarModel, AvatarGenerationResult
from .omnihuman import OmniHumanModel
from .fabric import FabricModel, FabricTextModel
from .kling import (
    KlingRefToVideoModel,
    KlingV2VReferenceModel,
    KlingV2VEditModel,
    KlingMotionControlModel,  # ADD
)
from .multitalk import MultiTalkModel

__all__ = [
    "BaseAvatarModel",
    "AvatarGenerationResult",
    "OmniHumanModel",
    "FabricModel",
    "FabricTextModel",
    "KlingRefToVideoModel",
    "KlingV2VReferenceModel",
    "KlingV2VEditModel",
    "KlingMotionControlModel",  # ADD
    "MultiTalkModel",
]
```

---

### Subtask 4: Update Generator (5 min)

**File:** `packages/providers/fal/avatar-generation/fal_avatar/generator.py`

Add to imports (line ~6):
```python
from .models import (
    ...
    KlingMotionControlModel,  # ADD
)
```

Add to model initialization (line ~40):
```python
self.models: Dict[str, BaseAvatarModel] = {
    ...
    "kling_motion_control": KlingMotionControlModel(),  # ADD
}
```

Add convenience method (after `transform_video` method, ~line 178):
```python
def transfer_motion(
    self,
    image_url: str,
    video_url: str,
    character_orientation: str = "video",
    keep_original_sound: bool = True,
    prompt: Optional[str] = None,
    **kwargs,
) -> AvatarGenerationResult:
    """
    Transfer motion from a reference video to a reference image.

    Creates videos where characters in the image mimic movements
    from the reference video.

    Args:
        image_url: Reference image URL (characters/background source)
        video_url: Reference video URL (motion source)
        character_orientation: "video" (max 30s) or "image" (max 10s)
        keep_original_sound: Keep audio from reference video
        prompt: Optional text description
        **kwargs: Additional parameters

    Returns:
        AvatarGenerationResult with video URL

    Example:
        result = generator.transfer_motion(
            image_url="https://example.com/person.jpg",
            video_url="https://example.com/dance.mp4",
            character_orientation="video",
            keep_original_sound=True
        )
    """
    return self.generate(
        model="kling_motion_control",
        image_url=image_url,
        video_url=video_url,
        character_orientation=character_orientation,
        keep_original_sound=keep_original_sound,
        prompt=prompt,
        **kwargs,
    )
```

Update docstring for class (line ~25):
```python
"""
Unified generator for FAL avatar and video generation models.

Provides a single interface to access all avatar models:
- OmniHuman v1.5 - Audio-driven human animation
- VEED Fabric 1.0 - Lipsync video generation
- VEED Fabric 1.0 Text - Text-to-speech avatar
- Kling O1 Reference-to-Video - Character consistency
- Kling O1 V2V Reference - Style-guided video
- Kling O1 V2V Edit - Targeted video modifications
- Kling v2.6 Motion Control - Motion transfer from video to image  # ADD
- AI Avatar Multi - Multi-person conversational video
"""
```

---

### Subtask 5: Update Core Pipeline Constants (3 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`

Add to `SUPPORTED_MODELS["avatar"]` (line ~77):
```python
"avatar": [
    ...
    "kling_motion_control",  # Kling v2.6 Motion Control  # ADD
]
```

Add to `COST_ESTIMATES["avatar"]` (line ~241):
```python
"avatar": {
    ...
    "kling_motion_control": 0.60,  # $0.06/sec * 10sec default  # ADD
}
```

Add to `PROCESSING_TIME_ESTIMATES["avatar"]` (line ~316):
```python
"avatar": {
    ...
    "kling_motion_control": 60,  # 60 seconds for motion transfer  # ADD
}
```

Add to `MODEL_RECOMMENDATIONS["avatar"]` (line ~159):
```python
"avatar": {
    ...
    "motion_transfer": "kling_motion_control",  # ADD
}
```

---

### Subtask 6: Write Unit Tests (5 min)

**File:** `tests/test_kling_motion_control.py` (NEW)

```python
"""
Unit tests for Kling Video v2.6 Motion Control model.
"""

import pytest
from unittest.mock import patch, MagicMock

from fal_avatar.models.kling import KlingMotionControlModel
from fal_avatar.models.base import AvatarGenerationResult
from fal_avatar.config.constants import (
    MODEL_ENDPOINTS,
    MODEL_DISPLAY_NAMES,
    MODEL_PRICING,
    MODEL_DEFAULTS,
    MAX_DURATIONS,
    INPUT_REQUIREMENTS,
    MODEL_CATEGORIES,
)


class TestKlingMotionControlModel:
    """Tests for KlingMotionControlModel class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.model = KlingMotionControlModel()

    def test_model_initialization(self):
        """Test model initializes with correct attributes."""
        assert self.model.model_name == "kling_motion_control"
        assert self.model.endpoint == "fal-ai/kling-video/v2.6/standard/motion-control"
        assert self.model.pricing["per_second"] == 0.06

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid inputs."""
        params = self.model.validate_parameters(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
            character_orientation="video",
            keep_original_sound=True
        )
        assert params["image_url"] == "https://example.com/image.jpg"
        assert params["video_url"] == "https://example.com/video.mp4"
        assert params["character_orientation"] == "video"
        assert params["keep_original_sound"] is True

    def test_validate_parameters_with_defaults(self):
        """Test parameter validation uses defaults correctly."""
        params = self.model.validate_parameters(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4"
        )
        assert params["character_orientation"] == "video"  # Default
        assert params["keep_original_sound"] is True  # Default

    def test_validate_parameters_missing_image_url(self):
        """Test validation fails when image_url is missing."""
        with pytest.raises(ValueError, match="image_url is required"):
            self.model.validate_parameters(
                image_url=None,
                video_url="https://example.com/video.mp4"
            )

    def test_validate_parameters_missing_video_url(self):
        """Test validation fails when video_url is missing."""
        with pytest.raises(ValueError, match="video_url is required"):
            self.model.validate_parameters(
                image_url="https://example.com/image.jpg",
                video_url=None
            )

    def test_validate_parameters_invalid_orientation(self):
        """Test validation fails with invalid orientation."""
        with pytest.raises(ValueError, match="character_orientation must be one of"):
            self.model.validate_parameters(
                image_url="https://example.com/image.jpg",
                video_url="https://example.com/video.mp4",
                character_orientation="invalid"
            )

    def test_validate_parameters_with_prompt(self):
        """Test validation includes optional prompt."""
        params = self.model.validate_parameters(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
            prompt="A person dancing gracefully"
        )
        assert params["prompt"] == "A person dancing gracefully"

    def test_get_model_info(self):
        """Test model info returns expected structure."""
        info = self.model.get_model_info()
        assert info["name"] == "kling_motion_control"
        assert info["display_name"] == "Kling v2.6 Motion Control"
        assert info["orientation_options"] == ["video", "image"]
        assert "motion transfer" in info["best_for"]

    def test_estimate_cost_video_orientation(self):
        """Test cost estimation for video orientation."""
        cost = self.model.estimate_cost(10, character_orientation="video")
        assert cost == 0.60  # 10 sec * $0.06

    def test_estimate_cost_image_orientation(self):
        """Test cost estimation for image orientation."""
        cost = self.model.estimate_cost(10, character_orientation="image")
        assert cost == 0.60  # 10 sec * $0.06

    def test_estimate_cost_capped_at_max(self):
        """Test cost estimation caps at max duration."""
        # Video orientation max is 30s
        cost_video = self.model.estimate_cost(60, character_orientation="video")
        assert cost_video == 1.80  # Capped at 30 sec * $0.06

        # Image orientation max is 10s
        cost_image = self.model.estimate_cost(60, character_orientation="image")
        assert cost_image == 0.60  # Capped at 10 sec * $0.06


class TestKlingMotionControlConstants:
    """Tests for motion control constants configuration."""

    def test_endpoint_configured(self):
        """Test endpoint is properly configured."""
        assert "kling_motion_control" in MODEL_ENDPOINTS
        assert MODEL_ENDPOINTS["kling_motion_control"] == "fal-ai/kling-video/v2.6/standard/motion-control"

    def test_display_name_configured(self):
        """Test display name is configured."""
        assert "kling_motion_control" in MODEL_DISPLAY_NAMES
        assert MODEL_DISPLAY_NAMES["kling_motion_control"] == "Kling v2.6 Motion Control"

    def test_pricing_configured(self):
        """Test pricing is configured."""
        assert "kling_motion_control" in MODEL_PRICING
        assert MODEL_PRICING["kling_motion_control"]["per_second"] == 0.06

    def test_defaults_configured(self):
        """Test default values are configured."""
        assert "kling_motion_control" in MODEL_DEFAULTS
        defaults = MODEL_DEFAULTS["kling_motion_control"]
        assert defaults["character_orientation"] == "video"
        assert defaults["keep_original_sound"] is True

    def test_max_durations_configured(self):
        """Test max durations are configured per orientation."""
        assert "kling_motion_control" in MAX_DURATIONS
        durations = MAX_DURATIONS["kling_motion_control"]
        assert durations["video"] == 30
        assert durations["image"] == 10

    def test_input_requirements_configured(self):
        """Test input requirements include both image and video."""
        assert "kling_motion_control" in INPUT_REQUIREMENTS
        requirements = INPUT_REQUIREMENTS["kling_motion_control"]
        assert "image_url" in requirements["required"]
        assert "video_url" in requirements["required"]
        assert "character_orientation" in requirements["required"]

    def test_model_category_configured(self):
        """Test model is in motion_transfer category."""
        assert "motion_transfer" in MODEL_CATEGORIES
        assert "kling_motion_control" in MODEL_CATEGORIES["motion_transfer"]


class TestKlingMotionControlGenerate:
    """Tests for generate method with mocked API."""

    def setup_method(self):
        """Set up test fixtures."""
        self.model = KlingMotionControlModel()

    @patch.object(KlingMotionControlModel, '_call_fal_api')
    def test_generate_success(self, mock_api):
        """Test successful video generation."""
        mock_api.return_value = {
            "success": True,
            "result": {
                "video": {
                    "url": "https://fal.media/output/video.mp4",
                    "file_size": 1024000,
                    "file_name": "output.mp4"
                },
                "duration": 10
            },
            "processing_time": 45.5
        }

        result = self.model.generate(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
            character_orientation="video"
        )

        assert result.success is True
        assert result.video_url == "https://fal.media/output/video.mp4"
        assert result.duration == 10
        assert result.cost == 0.60
        assert result.processing_time == 45.5
        assert result.metadata["character_orientation"] == "video"

    @patch.object(KlingMotionControlModel, '_call_fal_api')
    def test_generate_api_failure(self, mock_api):
        """Test handling of API failure."""
        mock_api.return_value = {
            "success": False,
            "error": "API rate limit exceeded",
            "processing_time": 0.5
        }

        result = self.model.generate(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4"
        )

        assert result.success is False
        assert "rate limit" in result.error.lower()

    def test_generate_validation_failure(self):
        """Test handling of validation failure."""
        result = self.model.generate(
            image_url=None,
            video_url="https://example.com/video.mp4"
        )

        assert result.success is False
        assert "image_url" in result.error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

### Subtask 7: Update Documentation (5 min)

**File:** `docs/reference/models.md`

Add under Avatar Generation section:
```markdown
### Kling v2.6 Motion Control

**Endpoint:** `fal-ai/kling-video/v2.6/standard/motion-control`

Transfer motion from a reference video to a reference image. Creates videos where characters in the image mimic movements from the reference video.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image_url` | string | Yes | Reference image (characters/background source) |
| `video_url` | string | Yes | Reference video (motion source) |
| `character_orientation` | enum | Yes | `video` (max 30s) or `image` (max 10s) |
| `keep_original_sound` | boolean | No | Keep reference video audio (default: true) |
| `prompt` | string | No | Optional text description |

**Pricing:** ~$0.06/second

**Best For:** Dance videos, action transfer, character animation, motion mimicry
```

**File:** `CLAUDE.md`

Update model count from 49 to 50 and update Avatar section:
```markdown
- **Multi-Model Support**: 50 AI models across 8 categories
```

```markdown
### 📦 Avatar Generation (9 models)
...
- **Kling v2.6 Motion Control** - Motion transfer from video to image
```

**File:** `.claude/skills/ai-content-pipeline/Skill.md`

Update similarly with new model count and listing.

---

## File Summary

| File Path | Action | Description |
|-----------|--------|-------------|
| `packages/providers/fal/avatar-generation/fal_avatar/config/constants.py` | MODIFY | Add model constants |
| `packages/providers/fal/avatar-generation/fal_avatar/models/kling.py` | MODIFY | Add KlingMotionControlModel class |
| `packages/providers/fal/avatar-generation/fal_avatar/models/__init__.py` | MODIFY | Export new model |
| `packages/providers/fal/avatar-generation/fal_avatar/generator.py` | MODIFY | Add model + convenience method |
| `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py` | MODIFY | Add to pipeline constants |
| `tests/test_kling_motion_control.py` | CREATE | Unit tests |
| `docs/reference/models.md` | MODIFY | Add documentation |
| `CLAUDE.md` | MODIFY | Update model count (49 → 50) |
| `.claude/skills/ai-content-pipeline/Skill.md` | MODIFY | Update model count |

---

## Testing Commands

```bash
# Run unit tests
pytest tests/test_kling_motion_control.py -v

# Run all avatar tests
pytest tests/test_fal_avatar.py tests/test_kling_motion_control.py -v

# Quick integration test (requires FAL_KEY)
python -c "
from fal_avatar import FALAvatarGenerator
gen = FALAvatarGenerator()
print(gen.get_model_info('kling_motion_control'))
print('Models:', gen.list_models())
"
```

---

## Usage Example

```python
from fal_avatar import FALAvatarGenerator

generator = FALAvatarGenerator()

# Using convenience method
result = generator.transfer_motion(
    image_url="https://example.com/person.jpg",
    video_url="https://example.com/dance.mp4",
    character_orientation="video",
    keep_original_sound=True,
    prompt="A person dancing gracefully"
)

# Using generic method
result = generator.generate(
    model="kling_motion_control",
    image_url="https://example.com/person.jpg",
    video_url="https://example.com/dance.mp4",
    character_orientation="video"
)

if result.success:
    print(f"Video URL: {result.video_url}")
    print(f"Cost: ${result.cost:.2f}")
    print(f"Duration: {result.duration}s")
```

---

## Post-Implementation Checklist

- [ ] All constants added to `fal_avatar/config/constants.py`
- [ ] `KlingMotionControlModel` class implemented in `fal_avatar/models/kling.py`
- [ ] Model exported in `fal_avatar/models/__init__.py`
- [ ] Generator updated with model and `transfer_motion()` method
- [ ] Core pipeline constants updated
- [ ] Unit tests written and passing
- [ ] Documentation updated
- [ ] Model count updated (49 → 50)
- [ ] Git commit with descriptive message

---

## Notes

- This model is unique because it requires **both image AND video inputs**
- Unlike image-to-video models, this belongs in avatar package alongside other Kling V2V models
- The `character_orientation` parameter determines max duration limits:
  - `video`: Up to 30 seconds
  - `image`: Up to 10 seconds
- The model uses standard tier pricing (~$0.06/sec), making it cost-effective
- Consider using the `prompt` parameter to guide the style of motion transfer
