# Implement Motion Transfer CLI Command

**Created:** 2026-01-21
**Completed:** 2026-01-21
**Status:** ✅ Implemented
**Priority:** High
**Estimated Time:** 60 minutes

## Overview

Add a `transfer-motion` CLI command to the AI Content Pipeline following the established architecture patterns (similar to `analyze-video` module structure).

## Architecture Decision: Modular Design

Following the existing pattern of `video_analysis.py`, create a separate `motion_transfer.py` module for:
- **Separation of Concerns**: CLI logic separate from business logic
- **Reusability**: Module can be imported for programmatic use
- **Testability**: Easier to unit test individual components
- **Maintainability**: Changes isolated to single module

## Subtasks

### Subtask 1: Create Motion Transfer Module (20 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/motion_transfer.py`

Create a dedicated module following the `video_analysis.py` pattern:

```python
"""
Motion transfer CLI command implementation.

Provides transfer-motion command for Kling v2.6 Motion Control model
to transfer motion from a reference video to a reference image.
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Try to import FAL client for file uploads
try:
    import fal_client
    FAL_CLIENT_AVAILABLE = True
except ImportError:
    FAL_CLIENT_AVAILABLE = False

# Try to import FAL Avatar Generator
try:
    from fal_avatar import FALAvatarGenerator
    from fal_avatar.models.base import AvatarGenerationResult
    FAL_AVATAR_AVAILABLE = True
except ImportError:
    FAL_AVATAR_AVAILABLE = False


# Orientation options with max durations
ORIENTATION_OPTIONS = {
    "video": {"max_duration": 30, "description": "Use video's character orientation (max 30s)"},
    "image": {"max_duration": 10, "description": "Use image's character orientation (max 10s)"},
}

# Default values
DEFAULTS = {
    "orientation": "video",
    "keep_sound": True,
    "output_dir": "output",
}


@dataclass
class MotionTransferResult:
    """Result from motion transfer operation."""
    success: bool
    video_url: Optional[str] = None
    local_path: Optional[str] = None
    duration: Optional[float] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def check_dependencies() -> tuple[bool, str]:
    """
    Check if required dependencies are available.

    Returns:
        Tuple of (success, error_message)
    """
    if not FAL_CLIENT_AVAILABLE:
        return False, "fal-client not installed. Run: pip install fal-client"
    if not FAL_AVATAR_AVAILABLE:
        return False, "fal_avatar module not available. Ensure package is installed."
    if not os.getenv("FAL_KEY"):
        return False, "FAL_KEY environment variable not set"
    return True, ""


def upload_if_local(file_path: str, file_type: str = "file") -> str:
    """
    Upload local file to FAL if it's a local path, otherwise return as-is.

    Args:
        file_path: Local file path or URL
        file_type: Description for logging ("image" or "video")

    Returns:
        URL (uploaded or original)

    Raises:
        FileNotFoundError: If local file doesn't exist
        ValueError: If upload fails
    """
    # Check if it's a URL
    if file_path.startswith(("http://", "https://")):
        return file_path

    # It's a local file
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"{file_type.title()} not found: {file_path}")

    print(f"📤 Uploading {file_type}: {path.name}")
    try:
        url = fal_client.upload_file(str(path))
        print(f"✅ {file_type.title()} uploaded: {url[:60]}...")
        return url
    except Exception as e:
        raise ValueError(f"Failed to upload {file_type}: {e}")


def download_video(url: str, output_path: Path) -> Path:
    """
    Download video from URL to local path.

    Args:
        url: Video URL
        output_path: Destination path

    Returns:
        Path to downloaded file

    Raises:
        requests.RequestException: If download fails
    """
    print(f"📥 Downloading video...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Video saved: {output_path}")
    return output_path


def transfer_motion_api(
    image_url: str,
    video_url: str,
    orientation: str = "video",
    keep_sound: bool = True,
    prompt: Optional[str] = None,
) -> AvatarGenerationResult:
    """
    Call the motion transfer API.

    This is the core API function that can be used programmatically.

    Args:
        image_url: Image URL (character/background source)
        video_url: Video URL (motion source)
        orientation: "video" (max 30s) or "image" (max 10s)
        keep_sound: Keep audio from reference video
        prompt: Optional text description

    Returns:
        AvatarGenerationResult from FAL Avatar Generator
    """
    generator = FALAvatarGenerator()
    return generator.transfer_motion(
        image_url=image_url,
        video_url=video_url,
        character_orientation=orientation,
        keep_original_sound=keep_sound,
        prompt=prompt,
    )


def transfer_motion(
    image_path: str,
    video_path: str,
    output_dir: str = "output",
    orientation: str = "video",
    keep_sound: bool = True,
    prompt: Optional[str] = None,
    download: bool = True,
) -> MotionTransferResult:
    """
    Transfer motion from video to image with full workflow.

    Handles file uploads, API call, and optional download.

    Args:
        image_path: Image file path or URL
        video_path: Video file path or URL
        output_dir: Output directory for downloaded video
        orientation: "video" (max 30s) or "image" (max 10s)
        keep_sound: Keep audio from reference video
        prompt: Optional text description
        download: Whether to download result video

    Returns:
        MotionTransferResult with all operation details
    """
    # Check dependencies
    ok, error = check_dependencies()
    if not ok:
        return MotionTransferResult(success=False, error=error)

    try:
        # Upload files if local
        image_url = upload_if_local(image_path, "image")
        video_url = upload_if_local(video_path, "video")

        # Call API
        print(f"\n🎬 Starting motion transfer...")
        print(f"   Orientation: {orientation} (max {ORIENTATION_OPTIONS[orientation]['max_duration']}s)")
        print(f"   Keep sound: {keep_sound}")

        result = transfer_motion_api(
            image_url=image_url,
            video_url=video_url,
            orientation=orientation,
            keep_sound=keep_sound,
            prompt=prompt,
        )

        if not result.success:
            return MotionTransferResult(
                success=False,
                error=result.error,
                processing_time=result.processing_time,
            )

        # Download if requested
        local_path = None
        if download and result.video_url:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"motion_transfer_{timestamp}.mp4"
            local_path = str(download_video(result.video_url, output_path / filename))

        return MotionTransferResult(
            success=True,
            video_url=result.video_url,
            local_path=local_path,
            duration=result.duration,
            cost=result.cost,
            processing_time=result.processing_time,
            metadata=result.metadata,
        )

    except FileNotFoundError as e:
        return MotionTransferResult(success=False, error=str(e))
    except ValueError as e:
        return MotionTransferResult(success=False, error=str(e))
    except Exception as e:
        return MotionTransferResult(success=False, error=f"Unexpected error: {e}")


def transfer_motion_command(args) -> None:
    """
    Handle transfer-motion CLI command.

    Args:
        args: Parsed argparse arguments
    """
    load_dotenv()

    # Validate orientation
    orientation = args.orientation
    if orientation not in ORIENTATION_OPTIONS:
        print(f"❌ Invalid orientation: {orientation}")
        print(f"   Valid options: {', '.join(ORIENTATION_OPTIONS.keys())}")
        sys.exit(1)

    # Determine sound setting
    keep_sound = not args.no_sound

    # Print header
    print(f"\n🎬 KLING v2.6 MOTION CONTROL")
    print("=" * 50)
    print(f"🖼️  Image: {args.image}")
    print(f"📹 Video: {args.video}")
    print(f"📁 Output: {args.output}")
    print(f"🔄 Orientation: {orientation}")
    print(f"🔊 Keep sound: {keep_sound}")
    if args.prompt:
        print(f"📝 Prompt: {args.prompt}")
    print()

    # Execute
    result = transfer_motion(
        image_path=args.image,
        video_path=args.video,
        output_dir=args.output,
        orientation=orientation,
        keep_sound=keep_sound,
        prompt=args.prompt,
        download=True,
    )

    # Display results
    if result.success:
        print(f"\n✅ Motion transfer successful!")
        print(f"📦 Model: kling_motion_control")
        if result.duration:
            print(f"⏱️  Duration: {result.duration}s")
        if result.cost:
            print(f"💰 Cost: ${result.cost:.2f}")
        if result.processing_time:
            print(f"⏱️  Processing: {result.processing_time:.1f}s")
        if result.local_path:
            print(f"📁 Output: {result.local_path}")

        # Save JSON if requested
        if args.save_json:
            import json
            json_path = Path(args.output) / args.save_json
            with open(json_path, 'w') as f:
                json.dump({
                    "success": True,
                    "video_url": result.video_url,
                    "local_path": result.local_path,
                    "duration": result.duration,
                    "cost": result.cost,
                    "processing_time": result.processing_time,
                    "metadata": result.metadata,
                }, f, indent=2)
            print(f"📄 Metadata: {json_path}")
    else:
        print(f"\n❌ Motion transfer failed!")
        print(f"   Error: {result.error}")
        sys.exit(1)


def list_motion_models() -> None:
    """Print motion transfer model information."""
    print("\n🎬 Motion Transfer Models")
    print("=" * 50)
    print("\n  kling_motion_control")
    print("    Name: Kling v2.6 Motion Control")
    print("    Provider: FAL AI")
    print("    Cost: $0.06/second")
    print("    Max Duration: 30s (video) / 10s (image)")
    print("    Best for: dance videos, action sequences, character animation")
    print("\n  Orientation Options:")
    for key, info in ORIENTATION_OPTIONS.items():
        print(f"    • {key}: {info['description']}")
```

### Subtask 2: Update CLI Main Module (15 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

Add imports and command registration:

```python
# Add to imports section (after video_analysis import)
from .motion_transfer import (
    transfer_motion_command,
    list_motion_models,
    ORIENTATION_OPTIONS,
)

# Add parser in main() function (after analyze-video parser)
# Transfer motion command
motion_parser = subparsers.add_parser(
    "transfer-motion",
    help="Transfer motion from video to image (Kling v2.6)"
)
motion_parser.add_argument(
    "-i", "--image",
    required=True,
    help="Image file path or URL (character/background source)"
)
motion_parser.add_argument(
    "-v", "--video",
    required=True,
    help="Video file path or URL (motion source)"
)
motion_parser.add_argument(
    "-o", "--output",
    default="output",
    help="Output directory (default: output)"
)
motion_parser.add_argument(
    "--orientation",
    choices=list(ORIENTATION_OPTIONS.keys()),
    default="video",
    help="Character orientation: video (max 30s) or image (max 10s)"
)
motion_parser.add_argument(
    "--no-sound",
    action="store_true",
    help="Remove audio from output (default: keep sound)"
)
motion_parser.add_argument(
    "-p", "--prompt",
    help="Optional text description to guide generation"
)
motion_parser.add_argument(
    "--save-json",
    help="Save result metadata as JSON file"
)

# List motion models command
subparsers.add_parser(
    "list-motion-models",
    help="List available motion transfer models"
)

# Add to command routing in main()
elif args.command == "transfer-motion":
    transfer_motion_command(args)
elif args.command == "list-motion-models":
    list_motion_models()

# Add to epilog examples
  # Transfer motion from video to image
  python -m ai_content_pipeline transfer-motion -i person.jpg -v dance.mp4

  # With options
  python -m ai_content_pipeline transfer-motion -i person.jpg -v dance.mp4 -o output/ --orientation video -p "Person dancing"

  # List motion models
  python -m ai_content_pipeline list-motion-models
```

### Subtask 3: Add YAML Pipeline Support (10 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py`

Add motion_transfer step type:

```python
# Add to SUPPORTED_MODELS dict
"motion_transfer": ["kling_motion_control"],

# Add to step type definitions if exists
STEP_TYPES = {
    # ... existing types ...
    "motion_transfer": {
        "description": "Transfer motion from video to image",
        "input_type": "image_and_video",
        "output_type": "video",
        "models": ["kling_motion_control"],
    },
}
```

**Example YAML config:** `input/pipelines/motion_transfer_example.yaml`

```yaml
name: "Motion Transfer Pipeline"
description: "Transfer dance moves to a character image"

input_image: "path/to/person.jpg"
input_video: "path/to/dance.mp4"

steps:
  - name: "transfer_motion"
    type: "motion_transfer"
    model: "kling_motion_control"
    params:
      character_orientation: "video"
      keep_original_sound: true
      prompt: "A person performing dance moves"
```

### Subtask 4: Write Comprehensive Unit Tests (15 min)

**File:** `tests/test_motion_transfer_cli.py`

```python
"""
Unit tests for motion transfer CLI module.

Tests cover:
- Module functions (upload, download, API)
- CLI command handler
- Error handling
- Integration with FAL Avatar Generator
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import sys
import os

# Add package to path
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__),
    '..', 'packages', 'core', 'ai_content_pipeline'
))

from ai_content_pipeline.motion_transfer import (
    check_dependencies,
    upload_if_local,
    download_video,
    transfer_motion_api,
    transfer_motion,
    MotionTransferResult,
    ORIENTATION_OPTIONS,
    DEFAULTS,
)


class TestCheckDependencies:
    """Tests for dependency checking."""

    @patch.dict(os.environ, {"FAL_KEY": "test_key"})
    @patch('ai_content_pipeline.motion_transfer.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.motion_transfer.FAL_AVATAR_AVAILABLE', True)
    def test_all_dependencies_available(self):
        """Test returns success when all dependencies present."""
        ok, error = check_dependencies()
        assert ok is True
        assert error == ""

    @patch('ai_content_pipeline.motion_transfer.FAL_CLIENT_AVAILABLE', False)
    def test_missing_fal_client(self):
        """Test returns error when fal-client missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "fal-client" in error

    @patch('ai_content_pipeline.motion_transfer.FAL_CLIENT_AVAILABLE', True)
    @patch('ai_content_pipeline.motion_transfer.FAL_AVATAR_AVAILABLE', False)
    def test_missing_fal_avatar(self):
        """Test returns error when fal_avatar missing."""
        ok, error = check_dependencies()
        assert ok is False
        assert "fal_avatar" in error


class TestUploadIfLocal:
    """Tests for upload_if_local function."""

    def test_url_passthrough(self):
        """Test URLs are returned as-is."""
        url = "https://example.com/image.jpg"
        result = upload_if_local(url, "image")
        assert result == url

    def test_http_url_passthrough(self):
        """Test HTTP URLs are returned as-is."""
        url = "http://example.com/video.mp4"
        result = upload_if_local(url, "video")
        assert result == url

    def test_local_file_not_found(self):
        """Test raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="Image not found"):
            upload_if_local("/nonexistent/path.jpg", "image")

    @patch('ai_content_pipeline.motion_transfer.fal_client')
    def test_local_file_upload(self, mock_fal, tmp_path):
        """Test local files are uploaded to FAL."""
        # Create temp file
        test_file = tmp_path / "test.jpg"
        test_file.write_text("test content")

        mock_fal.upload_file.return_value = "https://fal.media/uploaded.jpg"

        result = upload_if_local(str(test_file), "image")

        assert result == "https://fal.media/uploaded.jpg"
        mock_fal.upload_file.assert_called_once()


class TestTransferMotionApi:
    """Tests for transfer_motion_api function."""

    @patch('ai_content_pipeline.motion_transfer.FALAvatarGenerator')
    def test_calls_generator_transfer_motion(self, mock_generator_class):
        """Test API function calls generator correctly."""
        mock_generator = MagicMock()
        mock_generator.transfer_motion.return_value = MagicMock(
            success=True,
            video_url="https://fal.media/output.mp4"
        )
        mock_generator_class.return_value = mock_generator

        result = transfer_motion_api(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
            orientation="video",
            keep_sound=True,
            prompt="Test prompt"
        )

        mock_generator.transfer_motion.assert_called_once_with(
            image_url="https://example.com/image.jpg",
            video_url="https://example.com/video.mp4",
            character_orientation="video",
            keep_original_sound=True,
            prompt="Test prompt",
        )


class TestTransferMotion:
    """Tests for main transfer_motion function."""

    @patch('ai_content_pipeline.motion_transfer.check_dependencies')
    def test_returns_error_if_dependencies_missing(self, mock_check):
        """Test returns error when dependencies unavailable."""
        mock_check.return_value = (False, "Missing dependency")

        result = transfer_motion("image.jpg", "video.mp4")

        assert result.success is False
        assert "Missing dependency" in result.error

    @patch('ai_content_pipeline.motion_transfer.check_dependencies')
    @patch('ai_content_pipeline.motion_transfer.upload_if_local')
    @patch('ai_content_pipeline.motion_transfer.transfer_motion_api')
    @patch('ai_content_pipeline.motion_transfer.download_video')
    def test_full_workflow_success(
        self, mock_download, mock_api, mock_upload, mock_check, tmp_path
    ):
        """Test successful full workflow."""
        mock_check.return_value = (True, "")
        mock_upload.side_effect = [
            "https://fal.media/image.jpg",
            "https://fal.media/video.mp4"
        ]
        mock_api.return_value = MagicMock(
            success=True,
            video_url="https://fal.media/output.mp4",
            duration=10,
            cost=0.60,
            processing_time=45.0,
            metadata={"orientation": "video"}
        )
        mock_download.return_value = tmp_path / "output.mp4"

        result = transfer_motion(
            "local_image.jpg",
            "local_video.mp4",
            output_dir=str(tmp_path),
            download=True
        )

        assert result.success is True
        assert result.video_url == "https://fal.media/output.mp4"
        assert result.duration == 10
        assert result.cost == 0.60

    @patch('ai_content_pipeline.motion_transfer.check_dependencies')
    @patch('ai_content_pipeline.motion_transfer.upload_if_local')
    def test_handles_upload_error(self, mock_upload, mock_check):
        """Test handles file upload errors."""
        mock_check.return_value = (True, "")
        mock_upload.side_effect = ValueError("Upload failed")

        result = transfer_motion("image.jpg", "video.mp4")

        assert result.success is False
        assert "Upload failed" in result.error


class TestOrientationOptions:
    """Tests for orientation configuration."""

    def test_video_orientation_max_duration(self):
        """Test video orientation has 30s max."""
        assert ORIENTATION_OPTIONS["video"]["max_duration"] == 30

    def test_image_orientation_max_duration(self):
        """Test image orientation has 10s max."""
        assert ORIENTATION_OPTIONS["image"]["max_duration"] == 10

    def test_both_orientations_have_descriptions(self):
        """Test both orientations have descriptions."""
        for key in ["video", "image"]:
            assert "description" in ORIENTATION_OPTIONS[key]


class TestDefaults:
    """Tests for default values."""

    def test_default_orientation(self):
        """Test default orientation is video."""
        assert DEFAULTS["orientation"] == "video"

    def test_default_keep_sound(self):
        """Test default keep_sound is True."""
        assert DEFAULTS["keep_sound"] is True

    def test_default_output_dir(self):
        """Test default output_dir is output."""
        assert DEFAULTS["output_dir"] == "output"


class TestMotionTransferResult:
    """Tests for MotionTransferResult dataclass."""

    def test_success_result(self):
        """Test creating success result."""
        result = MotionTransferResult(
            success=True,
            video_url="https://example.com/video.mp4",
            duration=10,
            cost=0.60
        )
        assert result.success is True
        assert result.error is None

    def test_failure_result(self):
        """Test creating failure result."""
        result = MotionTransferResult(
            success=False,
            error="Something went wrong"
        )
        assert result.success is False
        assert result.video_url is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Subtask 5: Update Skill Documentation (5 min)

**File:** `.claude/skills/ai-content-pipeline/Skill.md`

Add to appropriate section:

```markdown
### Transfer Motion (Kling v2.6 Motion Control)

Transfer motion from a reference video to a reference image.

```bash
# Basic usage - local files
./venv/Scripts/aicp.exe transfer-motion -i person.jpg -v dance.mp4

# With all options
./venv/Scripts/aicp.exe transfer-motion \
  -i person.jpg \
  -v dance.mp4 \
  -o output/ \
  --orientation video \
  -p "A person dancing gracefully"

# Using URLs
./venv/Scripts/aicp.exe transfer-motion \
  -i "https://example.com/person.jpg" \
  -v "https://example.com/dance.mp4"

# Remove audio
./venv/Scripts/aicp.exe transfer-motion -i person.jpg -v dance.mp4 --no-sound

# List motion models
./venv/Scripts/aicp.exe list-motion-models
```

**Options:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--image` | `-i` | required | Image path/URL (character source) |
| `--video` | `-v` | required | Video path/URL (motion source) |
| `--output` | `-o` | `output/` | Output directory |
| `--orientation` | | `video` | `video` (max 30s) or `image` (max 10s) |
| `--no-sound` | | false | Remove audio from output |
| `--prompt` | `-p` | | Optional description |
| `--save-json` | | | Save metadata as JSON |

**Pricing:** $0.06/second
```

## File Summary

| File | Action | Description |
|------|--------|-------------|
| `packages/core/ai_content_pipeline/ai_content_pipeline/motion_transfer.py` | **Create** | Dedicated module for motion transfer |
| `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` | Modify | Add CLI command and routing |
| `packages/core/ai_content_pipeline/ai_content_pipeline/config/constants.py` | Modify | Add motion_transfer step type |
| `input/pipelines/motion_transfer_example.yaml` | Create | Example YAML config |
| `tests/test_motion_transfer_cli.py` | **Create** | Comprehensive unit tests |
| `.claude/skills/ai-content-pipeline/Skill.md` | Modify | Add CLI documentation |

## Architecture Benefits (Long-term)

1. **Modular Design**: Separate `motion_transfer.py` module can be:
   - Imported for programmatic use
   - Extended with new motion models
   - Tested independently

2. **Reusable Functions**:
   - `upload_if_local()` can be extracted to shared utils
   - `download_video()` already pattern-matched from existing code

3. **YAML Pipeline Support**:
   - Consistent with existing pipeline architecture
   - Enables batch processing

4. **Dataclass Result**:
   - Type-safe result handling
   - Easy serialization to JSON

5. **Error Handling**:
   - Graceful dependency checks
   - Detailed error messages

## CLI Usage (After Implementation)

```bash
# Basic
aicp transfer-motion -i person.jpg -v dance.mp4

# Full options
aicp transfer-motion \
  -i person.jpg \
  -v dance.mp4 \
  -o output/ \
  --orientation video \
  -p "Person dancing" \
  --save-json result.json

# List models
aicp list-motion-models
```

## Programmatic Usage

```python
from ai_content_pipeline.motion_transfer import transfer_motion, transfer_motion_api

# Full workflow (upload + API + download)
result = transfer_motion(
    image_path="person.jpg",
    video_path="dance.mp4",
    output_dir="output/",
    orientation="video",
    keep_sound=True,
    prompt="Person dancing"
)

# API only (for URLs)
from fal_avatar.models.base import AvatarGenerationResult
result: AvatarGenerationResult = transfer_motion_api(
    image_url="https://...",
    video_url="https://...",
    orientation="video"
)
```

## Success Criteria

- [x] CLI command `transfer-motion` accessible via `aicp`
- [x] Local files auto-uploaded to FAL
- [x] URLs passed through directly
- [x] Result video downloaded to output directory
- [x] Progress and cost displayed
- [x] `list-motion-models` command works
- [x] Unit tests created (comprehensive coverage)
- [x] Documentation updated
- [x] YAML pipeline example created

## Implementation Summary

**Files Created:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/motion_transfer.py` - Main module
- `tests/test_motion_transfer_cli.py` - Unit tests
- `input/pipelines/motion_transfer_example.yaml` - Example YAML config

**Files Modified:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py` - CLI registration
- `.claude/skills/ai-content-pipeline/Skill.md` - Documentation

## Related Files

- `packages/providers/fal/avatar-generation/fal_avatar/models/kling.py` - Model implementation
- `packages/providers/fal/avatar-generation/fal_avatar/generator.py` - Generator class
- `packages/core/ai_content_pipeline/ai_content_pipeline/video_analysis.py` - Reference pattern
- `tests/test_kling_motion_control.py` - Existing model tests
