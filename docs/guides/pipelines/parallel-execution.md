# Parallel Execution Guide

Speed up your AI content generation pipelines with parallel processing.

## Overview

Parallel execution allows multiple independent operations to run simultaneously, providing:
- **2-3x faster pipeline execution**
- **Better resource utilization**
- **Efficient batch processing**

## Enabling Parallel Execution

### Method 1: Environment Variable

```bash
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config pipeline.yaml
```

### Method 2: YAML Configuration

```yaml
settings:
  parallel: true
```

### Method 3: Python API

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager(parallel=True)
# or
results = manager.run_pipeline(config, parallel=True)
```

## Parallel Groups

Use `parallel_group` to explicitly define steps that should run concurrently.

### Basic Parallel Group

```yaml
steps:
  - type: "parallel_group"
    name: "batch_images"
    steps:
      - name: "image_1"
        type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "a red sports car"

      - name: "image_2"
        type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "a blue motorcycle"

      - name: "image_3"
        type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "a green bicycle"
```

### Parallel Group Options

```yaml
- type: "parallel_group"
  name: "batch_generation"
  max_workers: 4      # Maximum concurrent operations
  fail_fast: true     # Stop all if one fails
  timeout: 300        # Timeout in seconds
  steps:
    - ...
```

| Option | Description | Default |
|--------|-------------|---------|
| `max_workers` | Maximum concurrent threads | 4 |
| `fail_fast` | Stop on first failure | true |
| `timeout` | Operation timeout (seconds) | 300 |

## Understanding Dependencies

### Independent Steps (Can Parallelize)

Steps without dependencies can run in parallel:

```yaml
# These can run simultaneously
steps:
  - type: "parallel_group"
    steps:
      - name: "sunset_image"
        type: "text_to_image"
        params:
          prompt: "sunset"

      - name: "mountain_image"
        type: "text_to_image"
        params:
          prompt: "mountains"

      - name: "ocean_image"
        type: "text_to_image"
        params:
          prompt: "ocean"
```

### Dependent Steps (Must Be Sequential)

Steps with `input_from` must wait for their dependency:

```yaml
steps:
  - name: "image"           # Step 1: Runs first
    type: "text_to_image"
    params:
      prompt: "sunset"

  - name: "video"           # Step 2: Waits for step 1
    type: "image_to_video"
    input_from: "image"     # Dependency
```

## Hybrid Pipelines

Combine sequential and parallel execution:

```yaml
name: "Hybrid Pipeline"
description: "Mix of sequential and parallel steps"

steps:
  # Step 1: Generate base image (sequential)
  - name: "base_image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"

  # Steps 2-4: Create variations in parallel
  - type: "parallel_group"
    name: "variations"
    steps:
      - name: "video_version"
        type: "image_to_video"
        model: "kling_2_6_pro"
        input_from: "base_image"

      - name: "edited_version"
        type: "image_to_image"
        model: "photon_flash"
        input_from: "base_image"
        params:
          prompt: "add dramatic lighting"

      - name: "upscaled_version"
        type: "image_to_image"
        model: "clarity_upscaler"
        input_from: "base_image"

  # Step 5: Final processing (sequential, after all parallel steps)
  - name: "final"
    type: "analyze_image"
    model: "gemini_detailed"
    input_from: "edited_version"
```

Execution flow:
```
base_image (sequential)
    │
    ├──► video_version ─────┐
    ├──► edited_version ────┼──► final (sequential)
    └──► upscaled_version ──┘
         (parallel group)
```

## Performance Optimization

### Optimal Worker Count

```yaml
settings:
  max_workers: 4  # Good for most cases
```

**Guidelines:**
- **2-4 workers**: Good for standard pipelines
- **6-8 workers**: For I/O-heavy operations
- **More than 8**: Diminishing returns, may hit API rate limits

### Batch Processing

For large batches, process in chunks:

```yaml
name: "Batch Processing"
settings:
  parallel: true
  max_workers: 4

steps:
  - type: "parallel_group"
    name: "batch_1"
    steps:
      - { name: "img_1", type: "text_to_image", params: { prompt: "cat 1" } }
      - { name: "img_2", type: "text_to_image", params: { prompt: "cat 2" } }
      - { name: "img_3", type: "text_to_image", params: { prompt: "cat 3" } }
      - { name: "img_4", type: "text_to_image", params: { prompt: "cat 4" } }

  - type: "parallel_group"
    name: "batch_2"
    steps:
      - { name: "img_5", type: "text_to_image", params: { prompt: "cat 5" } }
      - { name: "img_6", type: "text_to_image", params: { prompt: "cat 6" } }
      - { name: "img_7", type: "text_to_image", params: { prompt: "cat 7" } }
      - { name: "img_8", type: "text_to_image", params: { prompt: "cat 8" } }
```

### Avoiding Rate Limits

Some APIs have rate limits. Handle them with:

```yaml
settings:
  parallel: true
  max_workers: 2        # Reduce workers
  rate_limit_delay: 1   # Delay between requests (seconds)
```

## Error Handling

### Fail-Fast Mode (Default)

Stop all parallel operations when one fails:

```yaml
- type: "parallel_group"
  fail_fast: true  # Default
  steps:
    - ...
```

### Continue on Failure

Continue other operations even if some fail:

```yaml
- type: "parallel_group"
  fail_fast: false
  steps:
    - ...
```

### Timeout Handling

Set timeouts to prevent hanging:

```yaml
- type: "parallel_group"
  timeout: 300  # 5 minutes
  steps:
    - ...
```

## Python API Parallel Processing

### Basic Parallel Execution

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager(parallel=True)

results = manager.run_pipeline(
    config="pipeline.yaml",
    input_text="beautiful landscape"
)
```

### Async Processing

```python
import asyncio
from packages.core.ai_content_pipeline.pipeline.manager import AsyncAIPipelineManager

async def main():
    manager = AsyncAIPipelineManager()

    # Run multiple generations concurrently
    tasks = [
        manager.generate_image(prompt="sunset"),
        manager.generate_image(prompt="mountains"),
        manager.generate_image(prompt="ocean")
    ]

    results = await asyncio.gather(*tasks)

    for result in results:
        print(f"Generated: {result.output_path}")

asyncio.run(main())
```

### Custom Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

manager = AIPipelineManager()
prompts = ["cat", "dog", "bird", "fish"]

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(manager.generate_image, prompt=p)
        for p in prompts
    ]

    results = [f.result() for f in futures]
```

## Monitoring Parallel Execution

### Progress Tracking

```yaml
settings:
  log_level: "INFO"  # See progress updates
```

Output:
```
[INFO] Starting parallel group 'batch_images' with 4 steps
[INFO] [1/4] Started: image_1
[INFO] [2/4] Started: image_2
[INFO] [3/4] Started: image_3
[INFO] [4/4] Started: image_4
[INFO] [1/4] Completed: image_1 (2.3s)
[INFO] [3/4] Completed: image_3 (2.5s)
[INFO] [2/4] Completed: image_2 (2.7s)
[INFO] [4/4] Completed: image_4 (2.8s)
[INFO] Parallel group completed in 2.8s (vs 10.3s sequential)
```

### Performance Metrics

```python
results = manager.run_pipeline(config, parallel=True)

print(f"Total time: {results.total_duration}s")
print(f"Sequential estimate: {results.sequential_estimate}s")
print(f"Speedup: {results.speedup}x")
```

## Common Patterns

### Generate Multiple Sizes

```yaml
- type: "parallel_group"
  name: "sizes"
  steps:
    - name: "square"
      type: "text_to_image"
      params:
        prompt: "{{input}}"
        aspect_ratio: "1:1"

    - name: "portrait"
      type: "text_to_image"
      params:
        prompt: "{{input}}"
        aspect_ratio: "9:16"

    - name: "landscape"
      type: "text_to_image"
      params:
        prompt: "{{input}}"
        aspect_ratio: "16:9"
```

### Multi-Model Comparison

```yaml
- type: "parallel_group"
  name: "model_comparison"
  steps:
    - name: "flux_result"
      type: "text_to_image"
      model: "flux_dev"
      params:
        prompt: "{{input}}"

    - name: "imagen_result"
      type: "text_to_image"
      model: "imagen4"
      params:
        prompt: "{{input}}"

    - name: "seedream_result"
      type: "text_to_image"
      model: "seedream_v3"
      params:
        prompt: "{{input}}"
```

### Parallel Video Creation

```yaml
steps:
  # Generate images in parallel
  - type: "parallel_group"
    name: "images"
    steps:
      - name: "scene_1"
        type: "text_to_image"
        params:
          prompt: "opening scene"

      - name: "scene_2"
        type: "text_to_image"
        params:
          prompt: "middle scene"

      - name: "scene_3"
        type: "text_to_image"
        params:
          prompt: "closing scene"

  # Convert to videos in parallel
  - type: "parallel_group"
    name: "videos"
    steps:
      - name: "video_1"
        type: "image_to_video"
        input_from: "scene_1"

      - name: "video_2"
        type: "image_to_video"
        input_from: "scene_2"

      - name: "video_3"
        type: "image_to_video"
        input_from: "scene_3"
```

## Troubleshooting

### "Rate limit exceeded"

Reduce parallel workers:
```yaml
settings:
  max_workers: 2
```

### "Memory issues"

Process in smaller batches or reduce workers.

### "Inconsistent results"

Set seeds for reproducibility:
```yaml
params:
  seed: 12345
```

### "Timeout errors"

Increase timeout:
```yaml
- type: "parallel_group"
  timeout: 600  # 10 minutes
```
