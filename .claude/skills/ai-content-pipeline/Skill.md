---
name: AI Content Pipeline
description: Generate AI content (images, videos, audio, avatars) and analyze videos with detailed timelines using YAML pipelines with 51 models across 8 categories. Includes video analysis with Gemini 3 Pro.
dependencies: python>=3.10
---

# AI Content Pipeline Skill

Generate AI content (images, videos, audio) and analyze videos using this unified Python package.

**Reference files** (load when needed for details):
- `REFERENCE.md` - Complete model specifications, API endpoints, troubleshooting
- `EXAMPLES.md` - YAML pipeline configuration examples

## First-Time Setup

### Step 1: Install the Package

```bash
# Option A: Install directly (recommended)
pip install git+https://github.com/donghaozhang/video-agent-skill.git

# Option B: Clone and install (for development)
git clone https://github.com/donghaozhang/video-agent-skill.git
cd video-agent-skill && pip install -e .
```

### Step 2: Configure API Keys

Create a `.env` file:
```bash
FAL_KEY=your_fal_api_key              # Required for most models
ELEVENLABS_API_KEY=your_key           # Optional: transcription
GEMINI_API_KEY=your_key               # Optional: video analysis
```

### Step 3: Verify Installation

```bash
aicp --help
aicp list-models
```

## Quick Commands

### Transcribe Audio (Primary Feature)

Transcribe audio/video files with word-level timestamps, speaker diarization, and audio event detection.

```bash
# Basic transcription
aicp transcribe -i audio.mp3
aicp transcribe -i video.mp4              # Extracts audio automatically

# With JSON output and custom settings
aicp transcribe -i audio.mp3 -o output_folder --save-json transcript.json

# Full options
aicp transcribe -i audio.mp3 --diarize --tag-events --language eng
```

**For word-level timestamps**, use the Python API directly (see `REFERENCE.md` for details):
```python
import fal_client
result = fal_client.subscribe("fal-ai/elevenlabs/speech-to-text",
    arguments={"audio_url": fal_client.upload_file("audio.mp3"), "diarize": True})
# result["words"] contains word-level timestamps with speaker IDs
```

**See `REFERENCE.md`** for complete CLI options, Python API details, and JSON structure.

---

### Generate Image
```bash
# Fast & cheap ($0.002)
aicp generate-image --text "A cute banana character" --model nano_banana_pro

# High quality
aicp generate-image --text "epic space battle" --model flux_dev
```

### Generate Video
```bash
aicp create-video --text "A serene mountain lake at sunset"
```

### Generate Avatar (Lipsync)
```bash
aicp generate-avatar --image-url "https://..." --audio-url "https://..." --model omnihuman_v1_5
```

### Transfer Motion
```bash
aicp transfer-motion -i person.jpg -v dance.mp4
```

### Analyze Video
```bash
aicp analyze-video -i video.mp4
```

### Run Pipeline
```bash
PIPELINE_PARALLEL_ENABLED=true aicp run-chain --config pipeline.yaml
```

### List Models
```bash
aicp list-models           # All models
aicp list-avatar-models    # Avatar/lipsync models
aicp list-video-models     # Video analysis models
aicp list-motion-models    # Motion transfer models
aicp list-speech-models    # Speech-to-text models
```

## Available Models (47 Total)

| Category | Count | Examples |
|----------|-------|----------|
| Text-to-Image | 8 | `nano_banana_pro`, `flux_dev`, `flux_schnell`, `gpt_image_1_5` |
| Image-to-Image | 8 | `nano_banana_pro_edit`, `flux_kontext`, `clarity_upscaler` |
| Image-to-Video | 11 | `veo_3`, `sora_2`, `kling_2_6_pro`, `hailuo` |
| Image Understanding | 7 | `gemini_describe`, `gemini_ocr`, `gemini_qa` |
| Avatar/Lipsync | 9 | `omnihuman_v1_5`, `fabric_1_0`, `multitalk` |
| Motion Transfer | 1 | `kling_motion_control` |
| Speech-to-Text | 1 | `scribe_v2` |
| Video Processing | 2 | `thinksound`, `topaz` |

**See `REFERENCE.md` for complete model specifications and pricing.**

## Cost Quick Reference

| Task | Model | Cost |
|------|-------|------|
| Image (fast) | nano_banana_pro | $0.002 |
| Image (quality) | flux_dev | $0.003 |
| Video (budget) | hailuo | $0.05/s |
| Video (quality) | veo3 | $0.50-6.00 |
| Avatar | omnihuman_v1_5 | $0.08-0.25 |
| Transcription | scribe_v2 | $0.008/min |

## Output Folder Structure

Generated content follows QCut's standard project structure:
```text
media/generated/
├── images/    # AI-generated images
├── videos/    # AI-generated videos
└── audio/     # AI-generated audio/speech
```

This aligns with the organize-project skill for consistent project organization.

## FAL API Direct Access

For custom scripts calling FAL API directly:

| Model Key | Endpoint |
|-----------|----------|
| `nano_banana_pro` | `https://fal.run/fal-ai/nano-banana-pro` |
| `flux_dev` | `https://fal.run/fal-ai/flux/dev` |

**Note:** Model keys use underscores, API endpoints use hyphens.

**See `REFERENCE.md` for complete endpoint reference.**
