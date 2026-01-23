# Parallel Image-to-Video Processing Implementation

## Overview

Add parallel processing support for image-to-video generation when processing multiple images from `split_image` step. This enables concurrent video generation, reducing total processing time significantly.

## Current State

- **File**: `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/video_steps.py`
- **Method**: `_process_multiple_images()` at line 177
- **Behavior**: Sequential processing - one image at a time
- **Time**: 4 images × ~2 min each = ~8 minutes total

## Target State

- **Behavior**: Parallel processing with configurable workers
- **Time**: 4 images in parallel = ~2 minutes total (4x speedup)
- **YAML Support**: `parallel: true` and `max_workers: N` parameters

## YAML Configuration Example

```yaml
- name: "animate_all_scenes"
  type: "image_to_video"
  model: "kling_2_6_pro"
  params:
    parallel: true        # Enable parallel processing
    max_workers: 4        # Max concurrent video generations
    duration: "5"
    prompts:
      - "Scene 1 motion prompt..."
      - "Scene 2 motion prompt..."
      - "Scene 3 motion prompt..."
      - "Scene 4 motion prompt..."
```

---

## Implementation Subtasks

### Subtask 1: Add Parallel Processing to ImageToVideoExecutor

**Files to modify:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/video_steps.py`

**Changes:**
1. Import `ThreadPoolExecutor` and `as_completed` from `concurrent.futures`
2. Add `_process_multiple_images_parallel()` method
3. Modify `_process_multiple_images()` to check for `parallel` param and dispatch accordingly

**Implementation:**

```python
# Add to imports at top of file
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add new method after _process_multiple_images()
def _process_multiple_images_parallel(
    self,
    step,
    image_paths: list,
    prompts_array: list,
    default_prompt: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Process multiple images to videos in parallel."""
    max_workers = params.pop('max_workers', 4)
    print(f"Processing {len(image_paths)} images in parallel (max_workers={max_workers})...")

    results_dict = {}
    output_paths = []
    output_urls = []
    total_cost = 0
    errors = []

    def process_single(index: int, image_path: str) -> tuple:
        """Process a single image and return (index, result)."""
        prompt = prompts_array[index] if index < len(prompts_array) else default_prompt
        input_dict = {"prompt": prompt, "image_path": image_path}
        result = self.generator.generate(input_data=input_dict, model=step.model, **params)
        return (index, result)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single, i, path): i
            for i, path in enumerate(image_paths)
        }

        for future in as_completed(futures):
            index = futures[future]
            try:
                idx, result = future.result()
                results_dict[idx] = result
                if result.success:
                    print(f"   ✅ Video {idx+1} completed: {result.output_path}")
                else:
                    errors.append(f"Image {idx+1}: {result.error}")
            except Exception as e:
                errors.append(f"Image {index+1}: {str(e)}")

    # Collect results in order
    for i in range(len(image_paths)):
        if i in results_dict and results_dict[i].success:
            output_paths.append(results_dict[i].output_path)
            output_urls.append(results_dict[i].output_url)
            total_cost += results_dict[i].cost_estimate or 0

    return {
        "success": len(output_paths) > 0,
        "output_path": output_paths[0] if output_paths else None,
        "output_paths": output_paths,
        "output_url": output_urls[0] if output_urls else None,
        "output_urls": output_urls,
        "cost": total_cost,
        "model": step.model,
        "metadata": {
            "parallel": True,
            "max_workers": max_workers,
            "total_images": len(image_paths),
            "videos_generated": len(output_paths),
        },
        "error": "; ".join(errors) if errors else None
    }
```

**Modify existing `_process_multiple_images()`:**

```python
def _process_multiple_images(
    self,
    step,
    image_paths: list,
    prompt: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Process multiple images to videos (from split_image step)."""
    prompts_array = step.params.get("prompts", [])

    # Check if parallel processing is requested
    if params.get('parallel', False):
        params_copy = params.copy()
        params_copy.pop('parallel', None)
        return self._process_multiple_images_parallel(
            step, image_paths, prompts_array, prompt, params_copy
        )

    # ... existing sequential code ...
```

---

### Subtask 2: Update Parameter Exclusion List

**Files to modify:**
- `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/step_executors/video_steps.py`

**Changes:**
Update `exclude_keys` in `execute()` method to include new parameters:

```python
params = self._merge_params(
    step.params, chain_config, kwargs,
    exclude_keys=["prompt", "prompts", "parallel", "max_workers"]
)
```

---

### Subtask 3: Add Documentation

**Files to modify:**
- `docs/Skill.md` (if exists)
- `CLAUDE.md`

**Add documentation for new parallel feature:**

```markdown
### Parallel Image-to-Video Processing

When using `split_image` followed by `image_to_video`, enable parallel processing:

```yaml
- type: "image_to_video"
  model: "kling_2_6_pro"
  params:
    parallel: true      # Process all images concurrently
    max_workers: 4      # Maximum concurrent generations (default: 4)
    prompts:            # Optional per-image prompts
      - "Prompt for image 1"
      - "Prompt for image 2"
```

**Performance:** 4 images sequential (~8 min) → parallel (~2 min)
```

---

### Subtask 4: Create Unit Tests

**Files to create:**
- `tests/test_parallel_video_generation.py`

**Test cases:**

```python
"""Unit tests for parallel image-to-video processing."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import Future

# Test 1: Parallel flag detection
def test_parallel_flag_triggers_parallel_processing():
    """Verify parallel=true triggers _process_multiple_images_parallel."""
    pass

# Test 2: Sequential when parallel=false
def test_sequential_when_parallel_false():
    """Verify parallel=false uses sequential processing."""
    pass

# Test 3: Max workers respected
def test_max_workers_parameter():
    """Verify max_workers limits concurrent threads."""
    pass

# Test 4: Individual prompts in parallel mode
def test_individual_prompts_in_parallel():
    """Verify each image gets its correct prompt in parallel mode."""
    pass

# Test 5: Error handling in parallel mode
def test_error_handling_parallel():
    """Verify errors in one thread don't crash others."""
    pass

# Test 6: Results collected in order
def test_results_ordered_correctly():
    """Verify output_paths maintains original image order."""
    pass

# Test 7: Default max_workers
def test_default_max_workers():
    """Verify default max_workers is 4 when not specified."""
    pass
```

---

### Subtask 5: Create Integration Test YAML

**Files to create:**
- `input/pipelines/storyboard/love_story_parallel_test.yaml`

**Content:**

```yaml
name: "love_story_parallel_test"
description: "Test parallel image-to-video with individual prompts"

prompt: |
  A 2x2 grid of 4 cinematic panels telling a love story:
  Panel 1: Coffee shop meet-cute
  Panel 2: Walking in the park
  Panel 3: Cooking dinner together
  Panel 4: Stargazing on rooftop
  Style: cinematic, warm lighting

steps:
  - name: "generate_storyboard"
    type: "text_to_image"
    model: "nano_banana_pro"
    params:
      aspect_ratio: "16:9"

  - name: "split_scenes"
    type: "split_image"
    model: "local"
    params:
      grid: "2x2"
      naming: "scene_{n}"

  - name: "animate_parallel"
    type: "image_to_video"
    model: "kling_2_6_pro"
    params:
      parallel: true
      max_workers: 4
      duration: "5"
      prompts:
        - "Coffee cups steam, eyes meet across table, gentle smile"
        - "Leaves fall around them, hands brush, laughter"
        - "Kitchen warmth, flour on nose, playful moment"
        - "Stars twinkle, blanket, leaning close together"

output_dir: "output/love_story_parallel_test"
save_intermediates: true
```

---

## File Summary

| File | Action | Purpose |
|------|--------|---------|
| `packages/core/.../step_executors/video_steps.py` | Modify | Add parallel processing method |
| `tests/test_parallel_video_generation.py` | Create | Unit tests |
| `input/pipelines/storyboard/love_story_parallel_test.yaml` | Create | Integration test |
| `docs/Skill.md` | Modify | Documentation |

---

## Testing Checklist

- [ ] Unit tests pass: `pytest tests/test_parallel_video_generation.py`
- [ ] Sequential mode still works (backward compatible)
- [ ] Parallel mode with 2x2 grid (4 images)
- [ ] Parallel mode with 3x3 grid (9 images)
- [ ] Individual prompts work in parallel mode
- [ ] Error in one video doesn't crash others
- [ ] Output order matches input order

---

## Rollback Plan

If issues arise, parallel processing can be disabled by:
1. Not setting `parallel: true` in YAML (default is sequential)
2. Removing the `parallel` parameter entirely

No breaking changes to existing pipelines.
