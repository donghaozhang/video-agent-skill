# YAML Pipeline Configuration Guide

Create powerful multi-step AI content generation workflows using YAML configuration files.

## Overview

YAML pipelines allow you to:
- Chain multiple AI operations together
- Pass outputs between steps automatically
- Configure complex workflows declaratively
- Reuse configurations across projects

## Basic Pipeline Structure

```yaml
# Pipeline metadata
name: "My Pipeline"
description: "What this pipeline does"
version: "1.0"

# Optional global settings
settings:
  output_dir: "output"
  parallel: false
  log_level: "INFO"

# Pipeline steps (executed in order)
steps:
  - name: "step_name"
    type: "operation_type"
    model: "model_name"
    params:
      key: "value"
```

## Step Types Reference

### text_to_image

Generate an image from text.

```yaml
- name: "generate_image"
  type: "text_to_image"
  model: "flux_dev"
  params:
    prompt: "a beautiful sunset over mountains"
    width: 1024
    height: 1024
    aspect_ratio: "16:9"  # Alternative to width/height
    seed: 12345           # For reproducibility
    guidance_scale: 7.5
```

**Available Models:** `flux_dev`, `flux_schnell`, `imagen4`, `seedream_v3`, `nano_banana_pro`, `gpt_image_1_5`

---

### image_to_image

Transform an existing image.

```yaml
- name: "edit_image"
  type: "image_to_image"
  model: "photon_flash"
  params:
    image: "path/to/image.png"  # Or use input_from
    prompt: "add dramatic lighting"
    strength: 0.7               # How much to change (0-1)
```

**Available Models:** `photon_flash`, `photon_base`, `nano_banana_pro_edit`, `gpt_image_1_5_edit`, `flux_kontext`, `seededit_v3`

---

### image_to_video

Convert an image to video animation.

```yaml
- name: "animate"
  type: "image_to_video"
  model: "kling_2_6_pro"
  input_from: "generate_image"  # Use output from previous step
  params:
    duration: 5
    fps: 24
    prompt: "gentle camera movement"  # Motion description
```

**Available Models:** `veo_3_1_fast`, `sora_2`, `sora_2_pro`, `kling_2_6_pro`, `kling_2_1`, `hailuo`, `wan_2_6`

---

### text_to_video

Generate video directly from text.

```yaml
- name: "generate_video"
  type: "text_to_video"
  model: "hailuo_pro"
  params:
    prompt: "ocean waves crashing on rocks"
    duration: 6
    resolution: "1080p"
```

**Available Models:** `hailuo_pro`, `sora_2`, `sora_2_pro`, `kling_2_6_pro`

---

### text_to_speech

Convert text to speech audio.

```yaml
- name: "narration"
  type: "text_to_speech"
  model: "elevenlabs"
  params:
    text: "Welcome to our presentation"
    voice: "Rachel"
    stability: 0.5
    similarity_boost: 0.75
```

**Available Models:** `elevenlabs`, `elevenlabs_turbo`, `elevenlabs_v3`

---

### analyze_image

Analyze an image with AI.

```yaml
- name: "analyze"
  type: "analyze_image"
  model: "gemini_detailed"
  params:
    image: "path/to/image.png"
    question: "What objects are in this image?"  # For QA model
```

**Available Models:** `gemini_describe`, `gemini_detailed`, `gemini_classify`, `gemini_objects`, `gemini_ocr`, `gemini_qa`

---

### split_image

Split a grid image into individual panels. Useful for storyboard workflows.

```yaml
- name: "split_panels"
  type: "split_image"
  model: "local"
  input_from: "grid_image"  # Grid image from previous step
  params:
    grid_type: "2x2"        # Grid layout: "2x2", "3x3", "1x4", "4x1"
    output_prefix: "scene"  # Output files: scene_1.png, scene_2.png, etc.
```

**Output:** Returns list of image paths (output_paths) for next step.

---

### concat_videos

Concatenate multiple videos into a single video using FFmpeg.

```yaml
- name: "combine"
  type: "concat_videos"
  model: "ffmpeg"
  input_from: "animate_panels"  # List of videos from image_to_video
  params:
    output_filename: "final.mp4"
```

**Requirements:** FFmpeg must be installed and in PATH.

---

### parallel_group

Execute multiple steps in parallel.

```yaml
- type: "parallel_group"
  name: "batch_generation"
  max_workers: 4
  steps:
    - name: "image_1"
      type: "text_to_image"
      params:
        prompt: "a red car"
    - name: "image_2"
      type: "text_to_image"
      params:
        prompt: "a blue car"
```

---

## Variable Interpolation

Use `{{variable}}` syntax to insert dynamic values.

### Input Variable

```yaml
steps:
  - name: "generate"
    type: "text_to_image"
    params:
      prompt: "{{input}}"  # Replaced with --input value from CLI
```

Usage:
```bash
ai-content-pipeline run-chain --config pipeline.yaml --input "beautiful landscape"
```

### Step Output Reference

```yaml
steps:
  - name: "image"
    type: "text_to_image"
    params:
      prompt: "a sunset"

  - name: "video"
    type: "image_to_video"
    input_from: "image"  # Uses output from "image" step
```

### Environment Variables

```yaml
steps:
  - name: "generate"
    type: "text_to_image"
    params:
      prompt: "{{env.MY_PROMPT}}"  # From environment variable
```

### Built-in Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{input}}` | CLI input value | User's prompt |
| `{{timestamp}}` | Current timestamp | 2026-01-21_143052 |
| `{{random}}` | Random UUID | a1b2c3d4-... |
| `{{step_NAME.output}}` | Step output path | output/image.png |

### Variable in Prompts

```yaml
steps:
  - name: "base_image"
    type: "text_to_image"
    params:
      prompt: "{{input}}, photorealistic, 4k"

  - name: "video"
    type: "image_to_video"
    input_from: "base_image"
    params:
      prompt: "{{input}} with gentle motion"
```

---

## Step Dependencies

### Sequential Execution

Steps execute in order by default:

```yaml
steps:
  - name: "step_1"  # Runs first
    type: "text_to_image"

  - name: "step_2"  # Runs after step_1
    type: "image_to_video"
    input_from: "step_1"
```

### Explicit Dependencies

Use `input_from` to specify dependencies:

```yaml
steps:
  - name: "image_a"
    type: "text_to_image"
    params:
      prompt: "sunset"

  - name: "image_b"
    type: "text_to_image"
    params:
      prompt: "mountains"

  - name: "video_a"
    type: "image_to_video"
    input_from: "image_a"  # Depends on image_a

  - name: "video_b"
    type: "image_to_video"
    input_from: "image_b"  # Depends on image_b
```

---

## Global Settings

```yaml
settings:
  # Output configuration
  output_dir: "output"
  create_subdirs: true
  timestamp_dirs: true

  # Execution settings
  parallel: false
  max_workers: 4
  fail_fast: true

  # Logging
  log_level: "INFO"
  log_file: "pipeline.log"

  # Cost management
  max_cost: 10.00
  warn_threshold: 5.00
```

---

## Complete Examples

### Text to Video Pipeline

```yaml
name: "Text to Video"
description: "Generate video from text description"

steps:
  - name: "image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
      aspect_ratio: "16:9"

  - name: "video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "image"
    params:
      duration: 5
```

### Multi-Style Image Generation

```yaml
name: "Style Variations"
description: "Generate same scene in multiple styles"

settings:
  parallel: true

steps:
  - type: "parallel_group"
    steps:
      - name: "photorealistic"
        type: "text_to_image"
        model: "imagen4"
        params:
          prompt: "{{input}}, photorealistic, 4k photography"

      - name: "artistic"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "{{input}}, oil painting style, impressionist"

      - name: "anime"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "{{input}}, anime style, studio ghibli"
```

### Content Production Pipeline

```yaml
name: "Content Production"
description: "Create image, video, and narration"

steps:
  - name: "image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
      aspect_ratio: "16:9"

  - name: "video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "image"
    params:
      duration: 8

  - name: "narration"
    type: "text_to_speech"
    model: "elevenlabs"
    params:
      text: "{{input}}"
      voice: "Rachel"
```

### Image Analysis Pipeline

```yaml
name: "Image Analysis"
description: "Analyze images with multiple models"

steps:
  - name: "generate"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"

  - type: "parallel_group"
    steps:
      - name: "description"
        type: "analyze_image"
        model: "gemini_detailed"
        input_from: "generate"

      - name: "objects"
        type: "analyze_image"
        model: "gemini_objects"
        input_from: "generate"

      - name: "composition"
        type: "analyze_image"
        model: "gemini_composition"
        input_from: "generate"
```

---

## Validation and Testing

### Validate Configuration

```bash
# Dry run to validate without executing
ai-content-pipeline run-chain --config pipeline.yaml --dry-run

# Estimate cost
ai-content-pipeline estimate-cost --config pipeline.yaml
```

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid YAML syntax" | Indentation or format error | Check YAML formatting |
| "Unknown step type" | Invalid type value | Use valid step types |
| "Model not found" | Invalid model name | Check models reference |
| "Missing required param" | Required parameter missing | Add required parameters |
| "Circular dependency" | Steps reference each other | Fix dependency chain |

---

## Best Practices

1. **Use descriptive step names** - Makes debugging easier
2. **Set appropriate aspect ratios** - Match your target platform
3. **Use parallel groups** - For independent operations
4. **Estimate costs first** - Before running expensive pipelines
5. **Use mock mode for testing** - Validate configuration without API calls
6. **Keep pipelines focused** - One purpose per pipeline file

---

[Back to Documentation Index](../../index.md) | [Next: Parallel Execution](parallel-execution.md)
