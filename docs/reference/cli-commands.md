# CLI Commands Reference

Complete reference for all command-line interface commands.

## Command Overview

The package provides two command aliases:
- `ai-content-pipeline` - Full command name
- `aicp` - Shortened alias

Both commands are identical in functionality.

## Global Options

```bash
aicp [OPTIONS] COMMAND [ARGS]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message and exit |
| `--json` | | Emit machine-readable JSON output to stdout |
| `--quiet` | `-q` | Suppress non-essential output (errors still go to stderr) |
| `--debug` | | Enable debug output |
| `--base-dir PATH` | | Base directory for operations (default: `.`) |
| `--config-dir PATH` | | Override config directory (default: XDG_CONFIG_HOME/video-ai-studio) |
| `--cache-dir PATH` | | Override cache directory (default: XDG_CACHE_HOME/video-ai-studio) |
| `--state-dir PATH` | | Override state directory (default: XDG_STATE_HOME/video-ai-studio) |

### Unix-Style Flags for Scripting

All commands inherit the global `--json` and `--quiet` flags, making output suitable for piping and CI:

```bash
# Machine-readable JSON output
aicp list-models --json | jq '.text_to_video[]'

# Quiet mode — only errors go to stderr
aicp create-video --text "sunset" --quiet

# Read prompt from stdin or file
echo "cinematic drone shot" | aicp create-video --input -
aicp run-chain --config pipeline.yaml --input prompts.txt

# Stream progress as JSONL events
aicp run-chain --config pipeline.yaml --stream

# Combine for CI usage
aicp run-chain --config pipeline.yaml --json --quiet | jq -r '.outputs.final.path'
```

---

## Core Commands

### list-models

List all available AI models.

```bash
aicp list-models [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--category TEXT` | Filter by category | All |
| `--provider TEXT` | Filter by provider | All |

**Examples:**
```bash
# List all models
aicp list-models

# List only image models
aicp list-models --category text-to-image

# List FAL AI models only
aicp list-models --provider fal

# JSON output
aicp list-models --json
```

---

### generate-image

Generate an image from text description.

```bash
aicp generate-image [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--text TEXT` | Text prompt (required) | - |
| `--model TEXT` | Model to use | nano_banana_pro |
| `--output TEXT` | Output file path | auto |
| `--aspect-ratio TEXT` | Aspect ratio (e.g., 16:9) | - |
| `--seed INT` | Random seed | random |
| `--mock` | Test without API call | false |

**Examples:**
```bash
# Basic image generation
aicp generate-image --text "a majestic dragon"

# Specify model and output
aicp generate-image --text "sunset over mountains" --model imagen4 --output sunset.png

# Set aspect ratio
aicp generate-image --text "cinematic landscape" --aspect-ratio 16:9

# Test without API call
aicp generate-image --text "test" --mock
```

---

### create-video

Create a video from text (generates image first, then video).

```bash
aicp create-video [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--text TEXT` | Text prompt (required) | - |
| `--image-model TEXT` | Model for image | flux_dev |
| `--video-model TEXT` | Model for video | auto |
| `--duration INT` | Video duration (seconds) | 5 |
| `--output TEXT` | Output file path | auto |
| `--mock` | Test without API call | false |
| `--input TEXT` | Read prompt from file or stdin (`-`) | - |

**Examples:**
```bash
# Basic video creation
aicp create-video --text "ocean waves at sunset"

# Specify models
aicp create-video --text "dancing robot" --image-model flux_dev --video-model kling_3_pro

# Read prompt from stdin
echo "flowing river at dawn" | aicp create-video --input -
```

---

### run-chain

Execute a custom pipeline from YAML configuration.

```bash
aicp run-chain [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--config PATH` | YAML config file (required) | - |
| `--input TEXT` | Input text/prompt or file (`-` for stdin) | - |
| `--output-dir PATH` | Output directory | output/ |
| `--parallel` | Enable parallel execution | false |
| `--dry-run` | Show plan without executing | false |
| `--stream` | Stream progress as JSONL events | false |

**Examples:**
```bash
# Run pipeline
aicp run-chain --config pipeline.yaml --input "my prompt"

# With parallel execution
PIPELINE_PARALLEL_ENABLED=true aicp run-chain --config pipeline.yaml

# Stream progress
aicp run-chain --config pipeline.yaml --stream

# Dry run to see plan
aicp run-chain --config pipeline.yaml --dry-run
```

---

### generate-avatar

Generate avatar video with lip-sync from image and audio.

```bash
aicp generate-avatar [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--image-url TEXT` | Portrait image URL (required) | - |
| `--audio-url TEXT` | Audio URL (required for audio models) | - |
| `--text TEXT` | Text input (for fabric_1_0_text) | - |
| `--model TEXT` | Avatar model to use | omnihuman_v1_5 |
| `--resolution TEXT` | Output resolution | 720p |

**Examples:**
```bash
# Basic avatar generation
aicp generate-avatar --image-url "https://..." --audio-url "https://..."

# Text-to-speech avatar
aicp generate-avatar --image-url "https://..." --text "Hello world!" --model fabric_1_0_text
```

---

### analyze-video

Analyze a video using AI.

```bash
aicp analyze-video [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input PATH` | Input video (required) | - |
| `-m, --model TEXT` | Analysis model | gemini-3-pro |
| `-t, --type TEXT` | Analysis type | timeline |
| `--output TEXT` | Save result to file | - |

**Analysis Types:**
- `timeline` - Frame-by-frame timeline
- `describe` - General description
- `transcribe` - Audio transcription

**Examples:**
```bash
# Timeline analysis
aicp analyze-video -i video.mp4

# Description
aicp analyze-video -i video.mp4 -t describe

# Transcription
aicp analyze-video -i video.mp4 -t transcribe
```

---

### transcribe

Transcribe audio using ElevenLabs Scribe v2.

```bash
aicp transcribe [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--input PATH` | Input audio file (required) | - |
| `--raw-json` | Output raw JSON with word-level timestamps | false |
| `--srt` | Generate SRT subtitle file | false |

**Examples:**
```bash
# Basic transcription
aicp transcribe --input audio.mp3

# With word-level timestamps
aicp transcribe --input meeting.mp3 --raw-json

# Generate subtitles
aicp transcribe --input podcast.mp3 --srt
```

---

### generate-grid

Generate a grid of images from text.

```bash
aicp generate-grid [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--text TEXT` | Text prompt (required) | - |
| `--layout TEXT` | Grid layout (e.g., 2x2, 3x3) | 2x2 |
| `--model TEXT` | Image model to use | nano_banana_pro |

---

### upscale-image

Upscale an image using AI.

```bash
aicp upscale-image [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--image PATH` | Input image (required) | - |
| `--upscale INT` | Upscale factor (1-8) | 2 |

---

### transfer-motion

Transfer motion from a reference video to a portrait image.

```bash
aicp transfer-motion [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--image-url TEXT` | Portrait image URL (required) | - |
| `--video-url TEXT` | Reference video URL (required) | - |

---

## Discovery & Setup Commands

### list-avatar-models

List available avatar generation models.

```bash
aicp list-avatar-models
```

### list-video-models

List available video analysis models.

```bash
aicp list-video-models
```

### list-motion-models

List available motion transfer models.

```bash
aicp list-motion-models
```

### list-speech-models

List available speech-to-text models.

```bash
aicp list-speech-models
```

### setup

Create `.env` file with API key templates.

```bash
aicp setup
```

### create-examples

Generate example configuration files.

```bash
aicp create-examples [OPTIONS]
```

---

## Project Management Commands

### init-project

Initialize a new project structure.

```bash
aicp init-project [OPTIONS]
```

### organize-project

Organize files into a standard project structure.

```bash
aicp organize-project [OPTIONS]
```

### structure-info

Show current project structure information.

```bash
aicp structure-info
```

---

## ViMax Subgroup

Novel-to-video pipeline commands available under `aicp vimax`:

```bash
aicp vimax idea2video --idea "A samurai's journey at sunrise"
aicp vimax script2video --script story.txt
aicp vimax novel2movie --novel novel.txt
aicp vimax novel2movie --novel novel.txt --storyboard-only
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PIPELINE_PARALLEL_ENABLED` | Enable parallel execution |
| `FAL_KEY` | FAL AI API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `XDG_CONFIG_HOME` | Override config directory |
| `XDG_CACHE_HOME` | Override cache directory |
| `XDG_STATE_HOME` | Override state directory |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | API error |
| 4 | File not found |
| 5 | Configuration error |

---

## Tips

### Using Mock Mode
Test commands without using API credits:
```bash
aicp generate-image --text "test" --mock
```

### Debug Output
Get detailed logging:
```bash
aicp --debug generate-image --text "test"
```

### Piping Output
Combine with other tools:
```bash
aicp list-models --json | jq '.[] | select(.category == "text-to-image")'
```

---

[Back to Documentation Index](../index.md)
