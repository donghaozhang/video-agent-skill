# Concat Videos Step Implementation

## Overview

Add a new pipeline step type `concat_videos` that combines multiple video files into a single video. This enables end-to-end storyboard workflows where split images are animated and then merged into a final video.

## Use Case

```yaml
steps:
  - type: text_to_image      # Generate 2x2 grid
  - type: split_image        # Split into 4 panels
  - type: image_to_video     # Animate each panel (parallel)
  - type: concat_videos      # NEW: Merge into single video
```

## Implementation Tasks

### Subtask 1: Add StepType Enum (5 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/chain.py`

Add to `StepType` enum:
```python
CONCAT_VIDEOS = "concat_videos"
```

Add input/output type mappings in `_get_step_input_type()` and `_get_step_output_type()`:
- Input type: `video` (or `videos` list)
- Output type: `video`

---

### Subtask 2: Create ConcatVideosExecutor (15 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/video_steps.py`

```python
class ConcatVideosExecutor(BaseStepExecutor):
    """Concatenate multiple videos into a single video using FFmpeg."""

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Concatenate videos from previous step.

        Args:
            step: Pipeline step configuration
            input_data: List of video paths from image_to_video step
            chain_config: Pipeline configuration
            step_context: Context from previous steps

        Params (from step.params):
            output_filename: Custom output filename (default: "combined.mp4")
            transition: Transition type (default: None) - future: fade, dissolve

        Returns:
            Dict with success, output_path, processing_time, etc.
        """
```

**Implementation Details:**
1. Accept `input_data` as list of video paths (from `output_paths` of previous step)
2. Create temporary `filelist.txt` with video paths
3. Run FFmpeg concat: `ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4`
4. Clean up temporary file
5. Return standardized result dict

**Key Code:**
```python
import subprocess
import tempfile
from pathlib import Path

def execute(self, step, input_data, chain_config, **kwargs):
    start_time = time.time()

    # Handle input - can be list or single path
    if isinstance(input_data, list):
        video_paths = input_data
    elif step_context and "output_paths" in step_context:
        video_paths = step_context["output_paths"]
    else:
        return self._create_error_result("No video paths provided")

    # Get output directory and filename
    output_dir = chain_config.get("output_dir", "output")
    output_filename = step.params.get("output_filename", "combined.mp4")
    output_path = Path(output_dir) / output_filename

    # Create filelist for FFmpeg concat
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for video_path in video_paths:
            f.write(f"file '{Path(video_path).absolute()}'\n")
        filelist_path = f.name

    try:
        # Run FFmpeg concat
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", filelist_path,
            "-c", "copy",
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return self._create_error_result(f"FFmpeg error: {result.stderr}")

        processing_time = time.time() - start_time

        return {
            "success": True,
            "output_path": str(output_path.absolute()),
            "processing_time": processing_time,
            "cost": 0.0,  # Local processing, no API cost
            "model": "ffmpeg",
            "metadata": {
                "input_count": len(video_paths),
                "input_paths": video_paths,
            }
        }
    finally:
        # Clean up temp file
        Path(filelist_path).unlink(missing_ok=True)
```

---

### Subtask 3: Register Executor (5 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/__init__.py`

Add export:
```python
from .video_steps import ConcatVideosExecutor
```

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/executor.py`

Add to `self._executors` dict:
```python
StepType.CONCAT_VIDEOS: ConcatVideosExecutor(),
```

---

### Subtask 4: Handle output_paths from Previous Step (10 min)

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/executor.py`

Update `_get_next_step_input()` to handle `output_paths` (list) from steps like `image_to_video` with parallel processing:

```python
def _get_next_step_input(self, step_result: Dict[str, Any]) -> Any:
    """Extract input for next step from current step's result."""
    # For concat_videos, prefer output_paths (list) over output_path (single)
    if "output_paths" in step_result and step_result["output_paths"]:
        return step_result["output_paths"]
    # Fall back to single output
    if "output_path" in step_result:
        return step_result["output_path"]
    if "output_url" in step_result:
        return step_result["output_url"]
    if "output_text" in step_result:
        return step_result["output_text"]
    return None
```

---

### Subtask 5: Create Unit Tests (15 min)

**File:** `tests/test_concat_videos.py`

```python
"""
Unit tests for ConcatVideosExecutor.

File: tests/test_concat_videos.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "packages/core/ai_content_pipeline"))


class MockStep:
    def __init__(self, params=None):
        self.params = params or {}


class TestConcatVideosExecutor:
    """Test concat_videos step executor."""

    def test_accepts_list_of_video_paths(self):
        """Verify executor accepts list input from image_to_video."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import ConcatVideosExecutor

        executor = ConcatVideosExecutor()
        step = MockStep(params={"output_filename": "test.mp4"})

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = executor.execute(
                step=step,
                input_data=["/path/scene_1.mp4", "/path/scene_2.mp4"],
                chain_config={"output_dir": "/tmp"},
            )

            assert mock_run.called
            # Verify ffmpeg was called with concat format
            call_args = mock_run.call_args[0][0]
            assert "ffmpeg" in call_args
            assert "-f" in call_args
            assert "concat" in call_args

    def test_uses_custom_output_filename(self):
        """Verify custom output filename is used."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import ConcatVideosExecutor

        executor = ConcatVideosExecutor()
        step = MockStep(params={"output_filename": "my_story.mp4"})

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = executor.execute(
                step=step,
                input_data=["/path/v1.mp4", "/path/v2.mp4"],
                chain_config={"output_dir": "/output"},
            )

            assert "my_story.mp4" in result["output_path"]

    def test_returns_zero_cost(self):
        """Verify local processing has zero API cost."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import ConcatVideosExecutor

        executor = ConcatVideosExecutor()
        step = MockStep()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = executor.execute(
                step=step,
                input_data=["/path/v1.mp4"],
                chain_config={"output_dir": "/tmp"},
            )

            assert result["cost"] == 0.0
            assert result["model"] == "ffmpeg"

    def test_handles_ffmpeg_error(self):
        """Verify FFmpeg errors are handled gracefully."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import ConcatVideosExecutor

        executor = ConcatVideosExecutor()
        step = MockStep()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="FFmpeg error")

            result = executor.execute(
                step=step,
                input_data=["/path/v1.mp4"],
                chain_config={"output_dir": "/tmp"},
            )

            assert result["success"] is False
            assert "FFmpeg error" in result["error"]

    def test_metadata_includes_input_count(self):
        """Verify metadata tracks input video count."""
        from ai_content_pipeline.pipeline.step_executors.video_steps import ConcatVideosExecutor

        executor = ConcatVideosExecutor()
        step = MockStep()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = executor.execute(
                step=step,
                input_data=["/v1.mp4", "/v2.mp4", "/v3.mp4", "/v4.mp4"],
                chain_config={"output_dir": "/tmp"},
            )

            assert result["metadata"]["input_count"] == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

### Subtask 6: Update Documentation (5 min)

**File:** `.claude/skills/ai-content-pipeline/Skill.md`

Add example:
```yaml
### Example: Full Storyboard Pipeline with Video Concatenation

steps:
  - name: "generate_grid"
    type: "text_to_image"
    model: "nano_banana_pro"
    params:
      prompt: "2x2 grid of story panels"

  - name: "split_panels"
    type: "split_image"
    model: "local"
    params:
      grid: "2x2"

  - name: "animate_scenes"
    type: "image_to_video"
    model: "kling_2_6_pro"
    params:
      parallel: true
      max_workers: 4

  - name: "combine_story"
    type: "concat_videos"
    model: "ffmpeg"
    params:
      output_filename: "full_story.mp4"
```

---

## Testing Checklist

- [ ] Unit tests pass: `pytest tests/test_concat_videos.py`
- [ ] Integration test with full pipeline YAML
- [ ] Verify output video plays correctly
- [ ] Verify video order matches input order
- [ ] Verify FFmpeg not found error is handled
- [ ] Verify works with 2, 4, 9 videos (2x2, 3x3 grids)

---

## File Summary

| File | Change |
|------|--------|
| `pipeline/chain.py` | Add `CONCAT_VIDEOS` to StepType enum |
| `pipeline/step_executors/video_steps.py` | Add `ConcatVideosExecutor` class |
| `pipeline/step_executors/__init__.py` | Export `ConcatVideosExecutor` |
| `pipeline/executor.py` | Register executor, update `_get_next_step_input()` |
| `tests/test_concat_videos.py` | Unit tests |
| `.claude/skills/ai-content-pipeline/Skill.md` | Documentation |

---

## Estimated Time

| Subtask | Time |
|---------|------|
| Add StepType enum | 5 min |
| Create ConcatVideosExecutor | 15 min |
| Register executor | 5 min |
| Handle output_paths | 10 min |
| Create unit tests | 15 min |
| Update documentation | 5 min |
| **Total** | **~55 min** |

---

## Future Enhancements

1. **Transitions:** Add fade/dissolve between clips using FFmpeg filters
2. **Re-encoding:** Option to re-encode for consistent format/resolution
3. **Audio mixing:** Merge audio tracks or add background music
4. **Thumbnail:** Generate thumbnail from first frame
