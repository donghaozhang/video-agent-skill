# AI Content Pipeline - YAML Examples

This file contains YAML pipeline configuration examples for common workflows.

## Step Types

**IMPORTANT:** Step types use underscores (e.g., `text_to_image`, not `text-to-image`)

Available step types:
- `text_to_image` - Generate image from text
- `image_to_image` - Transform/edit image
- `image_to_video` - Generate video from image
- `image_understanding` - Analyze image
- `text_to_speech` - Generate audio from text
- `speech_to_text` - Transcribe audio to text
- `add_audio` - Add audio to video
- `upscale_video` - Upscale video resolution
- `split_image` - Split grid into separate images
- `parallel_group` - Run steps in parallel

## Basic Examples

### Text to Image
```yaml
name: "Simple Image Generation"
description: "Generate an image from text"

steps:
  - name: "generate_image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "A majestic mountain landscape at sunset"
      width: 1920
      height: 1080
```

### Image to Image (Edit)
```yaml
name: "Image Transformation"
description: "Transform an existing image"
input_image: "path/to/source/image.jpg"

steps:
  - name: "transform_image"
    type: "image_to_image"
    model: "nano_banana_pro_edit"
    params:
      prompt: "Transform into a watercolor painting style"
```

### Image to Video
```yaml
name: "Video from Image"
description: "Generate video from image"
input_image: "path/to/image.jpg"

steps:
  - name: "create_video"
    type: "image_to_video"
    model: "veo3"
    params:
      prompt: "Camera slowly pans across the landscape"
      duration: 5
```

## Multi-Step Pipelines

### Text → Image → Video
```yaml
name: "Full Content Pipeline"
description: "Generate image and convert to video"

steps:
  - name: "generate_image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "A beautiful sunset over the ocean"

  - name: "create_video"
    type: "image_to_video"
    model: "veo3"
    params:
      prompt: "Gentle waves, sun slowly setting"
      duration: 5
```

### Image Grid → Split → Parallel Video
```yaml
name: "Storyboard Animation"
description: "Split grid and animate scenes in parallel"

steps:
  - name: "generate_grid"
    type: "text_to_image"
    model: "nano_banana_pro"
    params:
      prompt: "A 2x2 grid of 4 cinematic scenes"
      aspect_ratio: "16:9"

  - name: "split_panels"
    type: "split_image"
    model: "local"
    params:
      grid: "2x2"

  - name: "animate_all"
    type: "image_to_video"
    model: "kling_2_6_pro"
    params:
      parallel: true        # Process all images concurrently
      max_workers: 4        # Maximum concurrent generations
      duration: "5"
      prompts:              # Optional per-image prompts
        - "Scene 1 motion: camera push in, dramatic reveal"
        - "Scene 2 motion: slow pan left, ambient movement"
        - "Scene 3 motion: zoom out, establishing shot"
        - "Scene 4 motion: tracking shot, character focus"
```

**Performance:** 4 images sequential (~8 min) → parallel (~2 min)

## Video Analysis Examples

### Detailed Timeline Analysis (CLI)
```bash
# Default: Gemini 3 Pro, timeline analysis
aicp analyze-video -i video.mp4

# Specify model and output
aicp analyze-video -i video.mp4 -m gemini-3-pro -t timeline -o output/

# Quick description
aicp analyze-video -i video.mp4 -t describe

# Transcription only
aicp analyze-video -i video.mp4 -t transcribe
```

### Video Analysis (Python API)
```python
from video_utils.ai_commands import cmd_detailed_timeline_with_params

result = cmd_detailed_timeline_with_params(
    input_path='path/to/video.mp4',
    output_path='output/',
    provider='fal',  # or 'gemini'
    model='google/gemini-3-pro-preview'
)
```

## Avatar/Lipsync Examples

### Lipsync with Audio
```bash
aicp generate-avatar \
  --image-url "https://example.com/face.jpg" \
  --audio-url "https://example.com/speech.mp3" \
  --model omnihuman_v1_5
```

### Text-to-Speech Avatar
```bash
aicp generate-avatar \
  --image-url "https://example.com/face.jpg" \
  --text "Hello, this is a demonstration of text-to-speech avatar generation." \
  --model fabric_1_0_text
```

## Motion Transfer Examples

### Basic Motion Transfer
```bash
aicp transfer-motion -i person.jpg -v dance.mp4
```

### With Options
```bash
aicp transfer-motion \
  -i person.jpg \
  -v dance.mp4 \
  -o output/ \
  --orientation video \
  -p "A person dancing gracefully"
```

## Running Pipelines

### Basic Execution
```bash
aicp run-chain --config pipeline.yaml
```

### With Parallel Execution (2-3x speedup)
```bash
PIPELINE_PARALLEL_ENABLED=true aicp run-chain --config pipeline.yaml
```

### With Input Override
```bash
aicp run-chain --config pipeline.yaml --input "custom prompt text"
```

## Output Structure

Generated files follow QCut's standard project structure:
```
media/
├── generated/
│   ├── images/           # AI-generated images
│   │   └── YYYY-MM-DD_HHMMSS_image.png
│   ├── videos/           # AI-generated videos
│   │   └── YYYY-MM-DD_HHMMSS_video.mp4
│   └── audio/            # AI-generated audio/speech
│       └── YYYY-MM-DD_HHMMSS_audio.mp3
└── temp/                 # Processing intermediates
    └── frames/           # Extracted frames for analysis
```

Pipeline metadata:
```
media/generated/pipeline_results.json
```

Results JSON contains:
- Step execution times
- Model parameters used
- Output file paths
- Cost breakdown

**Note:** This structure aligns with QCut's organize-project skill for consistent project organization.
