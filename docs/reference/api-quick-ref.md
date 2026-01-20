# API Quick Reference

Condensed reference for Python API methods and CLI commands.

## Python API

### Import

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager
manager = AIPipelineManager()
```

### Image Generation

```python
# Generate image from text
result = manager.generate_image(
    prompt="description",           # Required
    model="flux_dev",               # Optional, default: flux_dev
    aspect_ratio="16:9",            # Optional
    num_images=1,                   # Optional
    output_dir="output/"            # Optional
)

# Returns
result.success          # bool
result.output_path      # str
result.cost             # float
result.model            # str
result.metadata         # dict
```

### Image-to-Image

```python
# Transform existing image
result = manager.transform_image(
    input_path="input.png",         # Required
    prompt="modifications",         # Required
    model="photon_flash",           # Optional
    strength=0.7                    # Optional, 0.0-1.0
)
```

### Video Generation

```python
# Text to video (direct)
result = manager.text_to_video(
    prompt="description",           # Required
    model="hailuo_pro",             # Optional
    duration=6                      # Optional, seconds
)

# Image to video
result = manager.image_to_video(
    input_path="image.png",         # Required
    prompt="motion description",    # Optional
    model="kling_2_6_pro",          # Optional
    duration=5                      # Optional
)

# Full pipeline (text → image → video)
result = manager.create_video(
    prompt="description",           # Required
    image_model="flux_dev",         # Optional
    video_model="kling_2_6_pro"     # Optional
)
```

### Video Analysis

```python
# Analyze video content
result = manager.analyze_video(
    input_path="video.mp4",         # Required
    model="gemini-3-pro",           # Optional
    analysis_type="timeline"        # timeline|describe|transcribe
)

# Returns
result.analysis         # str (analysis text)
result.video_duration   # float (seconds)
```

### Pipeline Execution

```python
# Run from config file
results = manager.run_pipeline(
    config_path="pipeline.yaml",    # Required
    input_text="prompt",            # Optional
    dry_run=False                   # Optional
)

# Run from dict
results = manager.run_pipeline(
    config={
        "name": "Pipeline",
        "steps": [...]
    },
    input_text="prompt"
)

# Returns list of StepResult objects
for step in results:
    print(step.step_name)
    print(step.output_path)
    print(step.cost)
```

### Cost Estimation

```python
# Estimate before running
estimate = manager.estimate_cost(
    config_path="pipeline.yaml",    # Required
    input_text="prompt"             # Optional
)

# Returns
estimate.total          # float (total cost)
estimate.steps          # list (per-step costs)
estimate.breakdown      # dict (detailed breakdown)
```

### Utility Methods

```python
# List available models
models = manager.list_models(
    category="text_to_image"        # Optional filter
)

# Validate configuration
is_valid = manager.validate_config("pipeline.yaml")

# Get model info
info = manager.get_model_info("flux_dev")
```

---

## CLI Commands

### Image Commands

```bash
# Generate image
ai-content-pipeline generate-image \
  --text "prompt" \
  --model flux_dev \
  --aspect-ratio 16:9 \
  --output image.png

# Transform image
ai-content-pipeline transform-image \
  --input source.png \
  --text "changes" \
  --model photon_flash

# Aliases
aicp generate-image --text "prompt"
```

### Video Commands

```bash
# Text to video
ai-content-pipeline text-to-video \
  --text "prompt" \
  --model hailuo_pro \
  --duration 6

# Image to video
ai-content-pipeline image-to-video \
  --image input.png \
  --model kling_2_6_pro \
  --duration 5

# Full pipeline
ai-content-pipeline create-video \
  --text "prompt"
```

### Video Analysis

```bash
# Analyze video
ai-content-pipeline analyze-video \
  -i video.mp4 \
  -m gemini-3-pro \
  -t timeline

# List analysis models
ai-content-pipeline list-video-models
```

### Pipeline Commands

```bash
# Run pipeline
ai-content-pipeline run-chain \
  --config pipeline.yaml \
  --input "prompt"

# Dry run (validate only)
ai-content-pipeline run-chain \
  --config pipeline.yaml \
  --dry-run

# Parallel execution
PIPELINE_PARALLEL_ENABLED=true \
  ai-content-pipeline run-chain \
  --config pipeline.yaml
```

### Utility Commands

```bash
# List models
ai-content-pipeline list-models
ai-content-pipeline list-models --type text_to_image

# Estimate cost
ai-content-pipeline estimate-cost --config pipeline.yaml

# Create examples
ai-content-pipeline create-examples

# Help
ai-content-pipeline --help
aicp --help
```

---

## YAML Configuration

### Minimal Pipeline

```yaml
name: "Pipeline Name"
steps:
  - type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
```

### Full Pipeline Structure

```yaml
name: "Pipeline Name"
description: "Optional description"

settings:
  parallel: true
  max_workers: 4
  max_budget: 10.00
  output_naming: "timestamp"

output:
  directory: "output/project"

steps:
  - name: "step_name"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
      aspect_ratio: "16:9"

  - name: "next_step"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "step_name"
    params:
      duration: 5
```

### Step Types

| Type | Purpose | Required Params |
|------|---------|-----------------|
| `text_to_image` | Generate image | `prompt` |
| `image_to_image` | Transform image | `prompt`, `input`/`input_from` |
| `text_to_video` | Generate video | `prompt` |
| `image_to_video` | Animate image | `input`/`input_from` |
| `video_analysis` | Analyze video | `input`/`input_from`, `analysis_type` |
| `text_to_speech` | Generate audio | `text` |
| `video_upscale` | Enhance video | `input`/`input_from` |
| `parallel_group` | Run in parallel | `steps` |

### Variables

```yaml
params:
  prompt: "{{input}}"              # User input
  prompt: "{{step_name.output}}"   # Previous step output
  prompt: "Static text"            # Literal value
```

---

## Models Quick Reference

### Text-to-Image

| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| `flux_schnell` | ★★★★★ | ★★★ | $0.001 |
| `flux_dev` | ★★★ | ★★★★★ | $0.003 |
| `imagen4` | ★★ | ★★★★★ | $0.004 |

### Image-to-Video

| Model | Duration | Quality | Cost |
|-------|----------|---------|------|
| `hailuo` | 6s | ★★★ | $0.30 |
| `kling_2_1` | 5s | ★★★★ | $0.25-0.50 |
| `kling_2_6_pro` | 5-10s | ★★★★★ | $0.50-1.00 |
| `sora_2_pro` | 4-20s | ★★★★★ | $1.20-3.60 |

### Text-to-Video

| Model | Duration | Cost |
|-------|----------|------|
| `hailuo_pro` | 6s | $0.08 |
| `kling_2_6_pro` | 5-10s | $0.35-1.40 |
| `sora_2` | 4-12s | $0.40-1.20 |

---

## Environment Variables

```bash
# Required
FAL_KEY=your_fal_key

# Optional
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENROUTER_API_KEY=your_openrouter_key

# Settings
PIPELINE_PARALLEL_ENABLED=true
PIPELINE_LOG_LEVEL=INFO
```

---

## Result Objects

### ImageResult

```python
result.success          # bool
result.output_path      # str
result.cost             # float
result.model            # str
result.prompt           # str
result.aspect_ratio     # str
result.metadata         # dict
```

### VideoResult

```python
result.success          # bool
result.output_path      # str
result.cost             # float
result.model            # str
result.duration         # float
result.metadata         # dict
```

### PipelineResult

```python
result.success          # bool
result.total_cost       # float
result.steps            # list[StepResult]
result.outputs          # list[str]
result.execution_time   # float
```

### StepResult

```python
step.step_name          # str
step.step_type          # str
step.success            # bool
step.output_path        # str
step.cost               # float
step.error              # str | None
```

---

[Back to Documentation Index](../index.md)
