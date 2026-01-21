---
name: AI Content Pipeline
description: Generate AI content (images, videos, audio, avatars) and analyze videos with detailed timelines using YAML pipelines with 46 models across 8 categories. Includes video analysis with Gemini 3 Pro.
dependencies: python>=3.10
---

# AI Content Pipeline Skill

Generate AI content (images, videos, audio) and analyze videos using this unified Python package.

## IMPORTANT: First-Time Setup Check

**Before running ANY pipeline commands, you MUST check if the environment is set up:**

```bash
# Check if venv exists (Windows - use bash syntax)
test -f "venv/Scripts/python.exe" && echo "venv exists" || echo "venv NOT found - run setup"

# Check if venv exists (Linux/Mac)
test -f venv/bin/python && echo "venv exists" || echo "venv NOT found - run setup"
```

**If venv does NOT exist, run this setup first:**

```bash
# Windows Setup (from bash)
python -m venv venv && ./venv/Scripts/pip install -e .

# Linux/Mac Setup
python3 -m venv venv && source venv/bin/activate && pip install -e .
```

## Running Commands

**All commands must use the venv Python directly:**

```bash
# Windows - Use venv/Scripts directly (bash syntax)
./venv/Scripts/ai-content-pipeline.exe --help
./venv/Scripts/aicp.exe --help

# Linux/Mac
./venv/bin/ai-content-pipeline --help
./venv/bin/aicp --help
```

## Quick Commands (after setup)

### Generate Image
```bash
# Windows
./venv/Scripts/ai-content-pipeline.exe generate-image --text "your prompt" --model flux_dev

# Linux/Mac
./venv/bin/ai-content-pipeline generate-image --text "your prompt" --model flux_dev
```

### Run Pipeline
```bash
# Windows (with parallel execution for 2-3x speedup)
PIPELINE_PARALLEL_ENABLED=true ./venv/Scripts/ai-content-pipeline.exe run-chain --config input/pipelines/config.yaml

# Linux/Mac
PIPELINE_PARALLEL_ENABLED=true ./venv/bin/ai-content-pipeline run-chain --config input/pipelines/config.yaml
```

### List Models
```bash
# Windows
./venv/Scripts/ai-content-pipeline.exe list-models

# Linux/Mac
./venv/bin/ai-content-pipeline list-models
```

### Generate Avatar (Lipsync/TTS)
```bash
# Avatar with audio (lipsync)
./venv/Scripts/ai-content-pipeline.exe generate-avatar --image-url "https://..." --audio-url "https://..." --model omnihuman_v1_5

# Avatar with text (TTS)
./venv/Scripts/ai-content-pipeline.exe generate-avatar --image-url "https://..." --text "Hello world!" --model fabric_1_0_text
```

### Transfer Motion (Kling v2.6)
Transfer motion from a reference video to a reference image.

```bash
# Basic usage - local files (auto-uploads to FAL)
./venv/Scripts/aicp.exe transfer-motion -i person.jpg -v dance.mp4

# With all options
./venv/Scripts/aicp.exe transfer-motion -i person.jpg -v dance.mp4 -o output/ --orientation video -p "A person dancing"

# Using URLs directly
./venv/Scripts/aicp.exe transfer-motion -i "https://example.com/person.jpg" -v "https://example.com/dance.mp4"

# Remove audio from output
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

## Available AI Models (46 Total)

### Text-to-Image (8 models)
| Model | Key | Provider | Cost |
|-------|-----|----------|------|
| Nano Banana Pro | `nano_banana_pro` | FAL AI | $0.002 |
| GPT Image 1.5 | `gpt_image_1_5` | FAL AI | $0.003 |
| ... | `flux_dev`, `flux_schnell`, `imagen4`, `seedream_v3`, `seedream3`, `gen4` | Other models | $0.001-0.08 |

### Image-to-Image (8 models)
| Model | Key | Description |
|-------|-----|-------------|
| Nano Banana Pro Edit | `nano_banana_pro_edit` | Fast image editing |
| GPT Image 1.5 Edit | `gpt_image_1_5_edit` | GPT-powered editing |
| ... | `photon_flash`, `photon_base`, `flux_kontext`, `flux_kontext_multi`, `seededit_v3`, `clarity_upscaler` | Other editing models |

### Image-to-Video (11 models)
| Model | Key | Description |
|-------|-----|-------------|
| Veo 3 | `veo3` | Google's latest video model |
| Veo 3 Fast | `veo3_fast` | Faster Veo 3 variant |
| Veo 3.1 Fast | `veo_3_1_fast` | Google's fast model with audio |
| Veo 2 | `veo2` | Previous generation Veo |
| Hailuo | `hailuo` | MiniMax video generation |
| Kling | `kling` | Base Kling model |
| Kling v2.1 | `kling_2_1` | High-quality video synthesis |
| Kling v2.6 Pro | `kling_2_6_pro` | Professional tier Kling |
| Sora 2 | `sora_2` | OpenAI's image-to-video |
| Sora 2 Pro | `sora_2_pro` | Professional Sora with 1080p |
| Seedance v1.5 Pro | `seedance_1_5_pro` | ByteDance with seed control |

### Image Understanding (7 models)
| Model | Key | Description |
|-------|-----|-------------|
| Gemini Describe | `gemini_describe` | Basic image description |
| Gemini Detailed | `gemini_detailed` | Detailed analysis |
| Gemini Classify | `gemini_classify` | Image classification |
| Gemini Objects | `gemini_objects` | Object detection |
| Gemini OCR | `gemini_ocr` | Text extraction |
| Gemini Composition | `gemini_composition` | Composition analysis |
| Gemini Q&A | `gemini_qa` | Visual question answering |

### Audio & Video Processing (2 models)
| Model | Key | Description |
|-------|-----|-------------|
| ThinksSound | `thinksound` | Audio generation |
| Topaz | `topaz` | Video upscaling |

### Avatar Generation (9 models)
| Model | Key | Description |
|-------|-----|-------------|
| Kling Ref-to-Video | `kling_ref_to_video` | Character consistency |
| Kling V2V Reference | `kling_v2v_reference` | Style transfer |
| Kling V2V Edit | `kling_v2v_edit` | Video editing |
| Kling v2.6 Motion | `kling_motion_control` | Motion transfer from video to image |
| ... | `omnihuman_v1_5`, `fabric_1_0`, `fabric_1_0_fast`, `fabric_1_0_text`, `multitalk` | Other avatar/lipsync models |

### Speech-to-Text (1 model)
| Model | Key | Description |
|-------|-----|-------------|
| ElevenLabs Scribe v2 | `scribe_v2` | Fast transcription with diarization |

## YAML Pipeline Configuration

**IMPORTANT:** Step types use underscores (e.g., `text_to_image`, not `text-to-image`)

### Available Step Types
- `text_to_image` - Generate image from text
- `image_to_image` - Transform/edit image
- `image_to_video` - Generate video from image
- `image_understanding` - Analyze image
- `text_to_speech` - Generate audio from text
- `speech_to_text` - Transcribe audio to text
- `add_audio` - Add audio to video
- `upscale_video` - Upscale video resolution
- `parallel_group` - Run steps in parallel

### Example: Text to Image Pipeline
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

### Example: Image to Image Pipeline
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

### Example: Image to Video Pipeline
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

### Example: Multi-step Pipeline
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

## Environment Variables

Required in `.env` file:
```
# FAL AI (required for most models)
FAL_KEY=your_fal_api_key

# Google Cloud (for Veo models)
PROJECT_ID=your-gcp-project-id
OUTPUT_BUCKET_PATH=gs://your-bucket/output/

# Optional services
ELEVENLABS_API_KEY=your_elevenlabs_key
GEMINI_API_KEY=your_gemini_key
REPLICATE_API_TOKEN=your_replicate_token
```

## Cost Estimation

| Category | Cost Range |
|----------|------------|
| Text-to-Image | $0.001-0.08 per image |
| Image-to-Image | $0.01-0.05 per modification |
| Image-to-Video | $0.08-6.00 per video |
| Avatar Generation | $0.08-0.25 per video |
| Video Upscaling | Varies by resolution |

## Testing

```bash
# Windows - Quick smoke tests
./venv/Scripts/python.exe tests/test_core.py

# Windows - Full test suite
./venv/Scripts/python.exe tests/run_all_tests.py --quick

# Linux/Mac
./venv/bin/python tests/test_core.py
./venv/bin/python tests/run_all_tests.py --quick
```

## Video Analysis (AI Understanding)

Analyze videos using Gemini models via FAL OpenRouter or direct Gemini API.

### Detailed Timeline Analysis (Second-by-Second)

Generate comprehensive video breakdowns with 2-5 second intervals, complete transcripts, people directory, and key quotes.

```python
# Python API
from video_utils.ai_commands import cmd_detailed_timeline_with_params

result = cmd_detailed_timeline_with_params(
    input_path='path/to/video.mp4',
    output_path='output/',
    provider='fal',  # or 'gemini'
    model='google/gemini-3-pro-preview'
)
```

**Available Models for Video Analysis:**
| Provider | Model | Description |
|----------|-------|-------------|
| FAL | `google/gemini-3-pro-preview` | Latest Gemini 3 Pro (Recommended) |
| FAL | `google/gemini-2.5-pro` | Gemini 2.5 Pro with reasoning |
| FAL | `google/gemini-2.5-flash` | Faster, cost-effective |
| Gemini | `gemini-2.0-flash-exp` | Direct API (local files, no upload) |

**Output includes:**
- 2-5 second interval breakdowns with Visual/Audio/Action/On-screen text
- Complete word-for-word transcript with speaker labels
- People directory with descriptions and timestamps
- All graphics/text logged with timestamps
- Key quotes with exact timestamps

### Other Video Analysis Commands

```python
from video_utils.ai_commands import (
    cmd_analyze_videos,           # Interactive video analysis
    cmd_transcribe_videos,        # Audio transcription
    cmd_describe_videos,          # Video description
    cmd_detailed_timeline,        # Interactive detailed timeline
)

# Programmatic versions with parameters
from video_utils.ai_commands import (
    cmd_describe_videos_with_params,
    cmd_transcribe_videos_with_params,
    cmd_detailed_timeline_with_params,
)
```

### Video Analysis CLI Command

The `analyze-video` command provides AI-powered video understanding using Gemini models.

```bash
# Windows - Basic usage (default: gemini-3-pro, timeline)
./venv/Scripts/aicp.exe analyze-video -i video.mp4

# Windows - With all options
./venv/Scripts/aicp.exe analyze-video -i video.mp4 -m gemini-3-pro -t timeline -o output/

# Linux/Mac
./venv/bin/aicp analyze-video -i video.mp4 -m gemini-3-pro -t timeline -o output/
```

**Analysis Types:**
```bash
# Detailed timeline (default) - second-by-second breakdown with transcript
./venv/Scripts/aicp.exe analyze-video -i video.mp4 -t timeline

# Quick description - summary of video content
./venv/Scripts/aicp.exe analyze-video -i video.mp4 -t describe

# Transcription - audio transcription with timestamps
./venv/Scripts/aicp.exe analyze-video -i video.mp4 -t transcribe
```

**Model Options:**
```bash
# Gemini 3 Pro (default, recommended) - highest quality
./venv/Scripts/aicp.exe analyze-video -i video.mp4 -m gemini-3-pro

# Gemini 2.5 Flash - faster, cost-effective
./venv/Scripts/aicp.exe analyze-video -i video.mp4 -m gemini-2.5-flash

# Gemini 2.5 Pro - detailed reasoning
./venv/Scripts/aicp.exe analyze-video -i video.mp4 -m gemini-2.5-pro

# Gemini Direct - local files, no upload required
./venv/Scripts/aicp.exe analyze-video -i video.mp4 -m gemini-direct
```

**List Available Models:**
```bash
# Windows
./venv/Scripts/aicp.exe list-video-models

# Linux/Mac
./venv/bin/aicp list-video-models
```

**CLI Options Reference:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--input` | `-i` | required | Video file or directory path |
| `--output` | `-o` | `output/` | Output directory for results |
| `--model` | `-m` | `gemini-3-pro` | Model to use for analysis |
| `--type` | `-t` | `timeline` | Analysis type (timeline/describe/transcribe) |
| `--format` | `-f` | `both` | Output format (md/json/both) |

**Output Files:**
- `{video_name}_detailed_timeline.md` - Markdown report
- `{video_name}_detailed_timeline.json` - JSON data

### Interactive CLI (Alternative)

```bash
cd packages/services/video-tools
python video_audio_utils.py

# Select "AI Analysis" menu, then:
# 1. Analyze Videos (Gemini Direct)
# 9. Detailed Video Timeline (FAL + Gemini)
```

## Output Location

Generated files are saved to:
- Images: `output/` directory with timestamp naming
- Videos: `output/` directory
- Reports: `output/reports/` directory
- Video Analysis: `output/` as `.md` and `.json` files
