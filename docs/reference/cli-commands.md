# CLI Commands Reference

Complete reference for all command-line interface commands.

## Command Overview

The package provides two command aliases:
- `ai-content-pipeline` - Full command name
- `aicp` - Shortened alias

Both commands are identical in functionality.

## Global Options

```bash
ai-content-pipeline [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |
| `--version` | Show version and exit |
| `--verbose` | Enable verbose output |
| `--quiet` | Suppress non-essential output |

---

## Core Commands

### list-models

List all available AI models.

```bash
ai-content-pipeline list-models [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--category TEXT` | Filter by category | All |
| `--provider TEXT` | Filter by provider | All |
| `--format TEXT` | Output format (table/json) | table |

**Examples:**
```bash
# List all models
ai-content-pipeline list-models

# List only image models
ai-content-pipeline list-models --category text-to-image

# List FAL AI models only
ai-content-pipeline list-models --provider fal

# Output as JSON
ai-content-pipeline list-models --format json
```

---

### generate-image

Generate an image from text description.

```bash
ai-content-pipeline generate-image [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--text TEXT` | Text prompt (required) | - |
| `--model TEXT` | Model to use | flux_dev |
| `--output TEXT` | Output file path | auto |
| `--width INT` | Image width | 1024 |
| `--height INT` | Image height | 1024 |
| `--aspect-ratio TEXT` | Aspect ratio (e.g., 16:9) | - |
| `--seed INT` | Random seed | random |
| `--mock` | Test without API call | false |

**Examples:**
```bash
# Basic image generation
ai-content-pipeline generate-image --text "a majestic dragon"

# Specify model and output
ai-content-pipeline generate-image \
  --text "sunset over mountains" \
  --model imagen4 \
  --output sunset.png

# Set aspect ratio
ai-content-pipeline generate-image \
  --text "cinematic landscape" \
  --aspect-ratio 16:9

# Test without API call
ai-content-pipeline generate-image --text "test" --mock
```

---

### create-video

Create a video from text (generates image first, then video).

```bash
ai-content-pipeline create-video [OPTIONS]
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

**Examples:**
```bash
# Basic video creation
ai-content-pipeline create-video --text "ocean waves at sunset"

# Specify models
ai-content-pipeline create-video \
  --text "dancing robot" \
  --image-model flux_dev \
  --video-model kling_2_6_pro

# Set duration
ai-content-pipeline create-video \
  --text "flowing river" \
  --duration 8
```

---

### image-to-video

Convert an existing image to video.

```bash
ai-content-pipeline image-to-video [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--image PATH` | Input image path (required) | - |
| `--model TEXT` | Video model to use | kling_2_6_pro |
| `--prompt TEXT` | Motion description | - |
| `--duration INT` | Video duration | 5 |
| `--output TEXT` | Output file path | auto |

**Examples:**
```bash
# Basic conversion
ai-content-pipeline image-to-video --image photo.png

# With motion prompt
ai-content-pipeline image-to-video \
  --image landscape.png \
  --prompt "camera slowly panning right"

# Specify model and duration
ai-content-pipeline image-to-video \
  --image portrait.png \
  --model sora_2 \
  --duration 8
```

---

### text-to-video

Generate video directly from text.

```bash
ai-content-pipeline text-to-video [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--text TEXT` | Text prompt (required) | - |
| `--model TEXT` | Model to use | hailuo_pro |
| `--duration INT` | Video duration | 6 |
| `--resolution TEXT` | Resolution (720p/1080p) | 720p |
| `--output TEXT` | Output file path | auto |

**Examples:**
```bash
# Basic text-to-video
ai-content-pipeline text-to-video --text "a cat playing piano"

# High quality
ai-content-pipeline text-to-video \
  --text "futuristic city" \
  --model sora_2_pro \
  --resolution 1080p
```

---

### run-chain

Execute a custom pipeline from YAML configuration.

```bash
ai-content-pipeline run-chain [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--config PATH` | YAML config file (required) | - |
| `--input TEXT` | Input text/prompt | - |
| `--input-file PATH` | Input from file | - |
| `--output-dir PATH` | Output directory | output/ |
| `--parallel` | Enable parallel execution | false |
| `--dry-run` | Show plan without executing | false |

**Examples:**
```bash
# Run pipeline
ai-content-pipeline run-chain --config pipeline.yaml --input "my prompt"

# With parallel execution
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain \
  --config pipeline.yaml

# Dry run to see plan
ai-content-pipeline run-chain --config pipeline.yaml --dry-run
```

---

### estimate-cost

Estimate cost before running a pipeline.

```bash
ai-content-pipeline estimate-cost [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--config PATH` | YAML config file (required) | - |
| `--format TEXT` | Output format (table/json) | table |

**Examples:**
```bash
# Estimate pipeline cost
ai-content-pipeline estimate-cost --config pipeline.yaml

# JSON output
ai-content-pipeline estimate-cost --config pipeline.yaml --format json
```

---

### create-examples

Generate example configuration files.

```bash
ai-content-pipeline create-examples [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir PATH` | Where to create files | examples/ |
| `--overwrite` | Overwrite existing files | false |

**Examples:**
```bash
# Create examples in default location
ai-content-pipeline create-examples

# Create in specific directory
ai-content-pipeline create-examples --output-dir my-configs/
```

---

### analyze-image

Analyze an image using AI.

```bash
ai-content-pipeline analyze-image [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--image PATH` | Input image (required) | - |
| `--model TEXT` | Analysis model | gemini_describe |
| `--question TEXT` | Question for QA model | - |
| `--output TEXT` | Save result to file | - |

**Examples:**
```bash
# Basic description
ai-content-pipeline analyze-image --image photo.png

# Detailed analysis
ai-content-pipeline analyze-image \
  --image photo.png \
  --model gemini_detailed

# Ask a question
ai-content-pipeline analyze-image \
  --image photo.png \
  --model gemini_qa \
  --question "What objects are in this image?"
```

---

### analyze-video

Analyze a video using AI.

```bash
ai-content-pipeline analyze-video [OPTIONS]
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
ai-content-pipeline analyze-video -i video.mp4

# Description
ai-content-pipeline analyze-video -i video.mp4 -t describe

# Transcription
ai-content-pipeline analyze-video -i video.mp4 -t transcribe
```

---

### text-to-speech

Convert text to speech.

```bash
ai-content-pipeline text-to-speech [OPTIONS]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--text TEXT` | Text to convert (required) | - |
| `--model TEXT` | TTS model | elevenlabs |
| `--voice TEXT` | Voice name | Rachel |
| `--output TEXT` | Output file path | auto |

**Examples:**
```bash
# Basic TTS
ai-content-pipeline text-to-speech --text "Hello, world!"

# Specific voice
ai-content-pipeline text-to-speech \
  --text "Welcome to our presentation" \
  --voice "Josh"
```

---

### list-video-models

List available video analysis models.

```bash
ai-content-pipeline list-video-models
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
ai-content-pipeline generate-image --text "test" --mock
```

### Verbose Output
Get detailed logging:
```bash
ai-content-pipeline --verbose generate-image --text "test"
```

### Piping Output
Combine with other tools:
```bash
ai-content-pipeline list-models --format json | jq '.[] | select(.category == "text-to-image")'
```

---

[Back to Documentation Index](../index.md)
