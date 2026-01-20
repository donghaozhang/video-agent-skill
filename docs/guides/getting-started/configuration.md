# Configuration Guide

Complete guide to configuring the AI Content Generation Suite.

## Environment Configuration

### .env File

Create a `.env` file in your project root:

```env
# =============================================================================
# FAL AI Configuration (Required for most functionality)
# =============================================================================
FAL_KEY=your_fal_api_key_here

# =============================================================================
# Google Cloud Configuration (For Veo and Gemini)
# =============================================================================
GEMINI_API_KEY=your_gemini_api_key_here
PROJECT_ID=your-gcp-project-id
OUTPUT_BUCKET_PATH=gs://your-bucket/output/

# =============================================================================
# ElevenLabs Configuration (For Text-to-Speech)
# =============================================================================
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# =============================================================================
# OpenRouter Configuration (For Alternative Models)
# =============================================================================
OPENROUTER_API_KEY=your_openrouter_api_key_here

# =============================================================================
# Pipeline Configuration
# =============================================================================
PIPELINE_PARALLEL_ENABLED=false
PIPELINE_OUTPUT_DIR=output
PIPELINE_LOG_LEVEL=INFO
```

### Environment Variable Priority

Variables are loaded in this order (later overrides earlier):
1. System environment variables
2. `.env` file in current directory
3. Command-line overrides

---

## YAML Pipeline Configuration

### Basic Structure

```yaml
# Pipeline metadata
name: "My Pipeline"
description: "Description of what this pipeline does"
version: "1.0"

# Global settings (optional)
settings:
  output_dir: "output"
  parallel: false
  log_level: "INFO"

# Pipeline steps
steps:
  - name: "step_1"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"

  - name: "step_2"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "step_1"
```

### Step Types

| Type | Description | Required Params |
|------|-------------|-----------------|
| `text_to_image` | Generate image from text | `prompt` |
| `image_to_image` | Transform image | `image`, `prompt` |
| `image_to_video` | Convert image to video | `image` |
| `text_to_video` | Generate video from text | `prompt` |
| `text_to_speech` | Generate speech | `text` |
| `analyze_image` | Analyze image | `image` |
| `parallel_group` | Run steps in parallel | `steps` |

### Variable Interpolation

Use `{{variable}}` syntax for dynamic values:

```yaml
steps:
  - name: "generate"
    type: "text_to_image"
    params:
      prompt: "{{input}}"  # From CLI --input

  - name: "animate"
    type: "image_to_video"
    input_from: "generate"  # Output from previous step
    params:
      prompt: "{{input}} with subtle motion"
```

### Available Variables

| Variable | Description |
|----------|-------------|
| `{{input}}` | Input from CLI `--input` flag |
| `{{step_NAME.output}}` | Output from step named NAME |
| `{{env.VARIABLE}}` | Environment variable |
| `{{timestamp}}` | Current timestamp |
| `{{random}}` | Random UUID |

---

## Parallel Execution Configuration

### Enable Parallel Processing

**Method 1: Environment Variable**
```bash
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml
```

**Method 2: YAML Configuration**
```yaml
settings:
  parallel: true

steps:
  - type: "parallel_group"
    steps:
      - type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "A cat"
      - type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "A dog"
```

### Parallel Group Configuration

```yaml
steps:
  - type: "parallel_group"
    name: "batch_generation"
    max_workers: 4  # Maximum concurrent operations
    fail_fast: true  # Stop all on first failure
    steps:
      - type: "text_to_image"
        params:
          prompt: "Image 1"
      - type: "text_to_image"
        params:
          prompt: "Image 2"
      - type: "text_to_image"
        params:
          prompt: "Image 3"
```

---

## Model-Specific Configuration

### Text-to-Image Options

```yaml
- type: "text_to_image"
  model: "flux_dev"
  params:
    prompt: "Your prompt here"
    width: 1024
    height: 1024
    aspect_ratio: "16:9"  # Alternative to width/height
    seed: 12345  # For reproducibility
    guidance_scale: 7.5
    num_inference_steps: 50
```

### Image-to-Video Options

```yaml
- type: "image_to_video"
  model: "kling_2_6_pro"
  params:
    duration: 5  # seconds
    fps: 24
    motion_bucket_id: 127
    noise_aug_strength: 0.02
```

### Text-to-Speech Options

```yaml
- type: "text_to_speech"
  model: "elevenlabs"
  params:
    voice: "Rachel"
    stability: 0.5
    similarity_boost: 0.75
    style: 0.0
    use_speaker_boost: true
```

---

## Output Configuration

### Directory Structure

```yaml
settings:
  output_dir: "output"
  create_subdirs: true
  timestamp_dirs: true
```

Result structure:
```
output/
├── 2026-01-21_143052/
│   ├── step_1_image.png
│   ├── step_2_video.mp4
│   └── pipeline_log.json
```

### File Naming

```yaml
settings:
  output_naming:
    pattern: "{step_name}_{timestamp}"
    include_model: true
```

---

## Logging Configuration

### Log Levels

| Level | Description |
|-------|-------------|
| `DEBUG` | Detailed debugging information |
| `INFO` | General operational information |
| `WARNING` | Warning messages |
| `ERROR` | Error messages only |

### Configuration

```yaml
settings:
  log_level: "INFO"
  log_file: "pipeline.log"
  log_format: "%(asctime)s [%(levelname)s] %(message)s"
```

Or via environment:
```bash
PIPELINE_LOG_LEVEL=DEBUG ai-content-pipeline run-chain --config config.yaml
```

---

## Cost Management Configuration

### Cost Limits

```yaml
settings:
  cost_management:
    max_cost_per_run: 10.00  # USD
    warn_threshold: 5.00
    require_confirmation: true  # Prompt before expensive operations
```

### Cost Tracking

```yaml
settings:
  cost_tracking:
    enabled: true
    output_file: "costs.json"
    include_timestamps: true
```

---

## Example Configurations

### Basic Text-to-Video Pipeline

```yaml
name: "Text to Video"
description: "Generate video from text prompt"

steps:
  - name: "generate_image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
      aspect_ratio: "16:9"

  - name: "create_video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "generate_image"
    params:
      duration: 5
```

### Batch Image Generation

```yaml
name: "Batch Images"
description: "Generate multiple images in parallel"

settings:
  parallel: true

steps:
  - type: "parallel_group"
    steps:
      - type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "A sunset over the ocean"
      - type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "A mountain landscape"
      - type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "A city skyline at night"
```

### Multi-Step Content Pipeline

```yaml
name: "Complete Content Pipeline"
description: "Generate image, video, and narration"

steps:
  - name: "image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"

  - name: "video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "image"

  - name: "narration"
    type: "text_to_speech"
    model: "elevenlabs"
    params:
      text: "{{input}}"
      voice: "Rachel"
```

---

## Configuration Validation

### Validate Configuration

```bash
# Check configuration without running
ai-content-pipeline run-chain --config config.yaml --dry-run
```

### Common Validation Errors

| Error | Solution |
|-------|----------|
| "Model not found" | Check model name in models reference |
| "Missing required param" | Add required parameter to step |
| "Invalid step reference" | Ensure `input_from` matches existing step name |
| "Circular dependency" | Remove circular references between steps |

---

[Back to Documentation Index](../../index.md)
