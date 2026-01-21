# Setup Guide

Complete guide to installing and configuring the AI Content Generation Suite.

## System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB for package, additional space for generated content
- **Network**: Internet connection for API calls

### Recommended Setup
- Python 3.11 or 3.12
- 16GB RAM for parallel processing
- SSD storage for faster I/O

---

## Installation

### Method 1: Install from PyPI (Recommended)

```bash
pip install video-ai-studio

# Verify installation
ai-content-pipeline --version
```

### Method 2: Install from Source

```bash
git clone https://github.com/donghaozhang/video-agent-skill.git
cd video-agent-skill
pip install -e .
```

### Method 3: Install with Optional Dependencies

```bash
pip install video-ai-studio[all]   # All dependencies
pip install video-ai-studio[dev]   # Development tools
pip install video-ai-studio[test]  # Testing tools
```

---

## Virtual Environment Setup

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install video-ai-studio
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install video-ai-studio
```

### Using conda

```bash
conda create -n ai-content python=3.11
conda activate ai-content
pip install video-ai-studio
```

---

## API Keys Configuration

### Required API Keys

| Provider | Key Name | Required For | Get Key At |
|----------|----------|--------------|------------|
| FAL AI | `FAL_KEY` | Most models | <https://fal.ai/dashboard> |
| Google | `GEMINI_API_KEY` | Image analysis | <https://makersuite.google.com> |
| ElevenLabs | `ELEVENLABS_API_KEY` | Text-to-speech | <https://elevenlabs.io/app/settings> |
| OpenRouter | `OPENROUTER_API_KEY` | Alternative models | <https://openrouter.ai/keys> |

### .env File Setup

Create a `.env` file in your project root:

```env
# =============================================================================
# FAL AI (Required for most functionality)
# =============================================================================
FAL_KEY=your_fal_api_key_here

# =============================================================================
# Google Cloud (For Veo and Gemini)
# =============================================================================
GEMINI_API_KEY=your_gemini_api_key_here
PROJECT_ID=your-gcp-project-id
OUTPUT_BUCKET_PATH=gs://your-bucket/output/

# =============================================================================
# ElevenLabs (For Text-to-Speech)
# =============================================================================
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# =============================================================================
# OpenRouter (For Alternative Models)
# =============================================================================
OPENROUTER_API_KEY=your_openrouter_api_key_here

# =============================================================================
# Pipeline Settings
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

### Google Cloud Setup (For Veo Models)

```bash
# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project your-project-id

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
```

---

## Verifying Installation

```bash
# Check CLI is available
ai-content-pipeline --help

# List available models
ai-content-pipeline list-models

# Test with mock mode (no API calls)
ai-content-pipeline generate-image --text "test" --mock

# Test actual API connection (uses credits)
ai-content-pipeline generate-image --text "test image" --model flux_schnell
```

### Python Import Test

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager
manager = AIPipelineManager()
print("Installation successful!")
```

---

## YAML Pipeline Configuration

### Basic Structure

```yaml
name: "My Pipeline"
description: "Description of what this pipeline does"

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

output_dir: "output"
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

```yaml
steps:
  - name: "generate"
    type: "text_to_image"
    params:
      prompt: "{{input}}"  # From CLI --input

  - name: "animate"
    type: "image_to_video"
    input_from: "generate"  # Output from previous step
```

> **Note**: Use `input_from` to pass files between steps. Use `{{input}}` for the initial text prompt from CLI.

---

## Parallel Execution

### Enable Parallel Processing

```bash
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml
```

### Parallel Group Configuration

```yaml
steps:
  - type: "parallel_group"
    name: "batch_generation"
    max_workers: 4
    steps:
      - type: "text_to_image"
        params: { prompt: "Image 1" }
      - type: "text_to_image"
        params: { prompt: "Image 2" }
      - type: "text_to_image"
        params: { prompt: "Image 3" }
```

---

## Model-Specific Configuration

### Text-to-Image Options

```yaml
- type: "text_to_image"
  model: "flux_dev"
  params:
    prompt: "Your prompt here"
    aspect_ratio: "16:9"
    seed: 12345
```

### Image-to-Video Options

```yaml
- type: "image_to_video"
  model: "kling_2_6_pro"
  params:
    duration: 5
    fps: 24
```

### Text-to-Speech Options

```yaml
- type: "text_to_speech"
  model: "elevenlabs"
  params:
    voice: "Rachel"
    stability: 0.5
```

---

## Output Configuration

```yaml
output_dir: "output"
temp_dir: "temp"
cleanup_temp: true
save_intermediates: false
```

Result structure:
```text
output/
├── 2026-01-21_143052/
│   ├── step_1_image.png
│   ├── step_2_video.mp4
│   └── pipeline_log.json
```

---

## Logging Configuration

```bash
PIPELINE_LOG_LEVEL=DEBUG ai-content-pipeline run-chain --config config.yaml
```

| Level | Description |
|-------|-------------|
| `DEBUG` | Detailed debugging information |
| `INFO` | General operational information |
| `WARNING` | Warning messages |
| `ERROR` | Error messages only |

---

## Configuration Validation

```bash
# Check configuration without running
ai-content-pipeline run-chain --config config.yaml --dry-run

# Estimate cost before running
ai-content-pipeline estimate-cost --config config.yaml
```

---

## Upgrading

```bash
pip install --upgrade video-ai-studio
```

---

## Troubleshooting

### Python Version Issues

```bash
python --version  # Check version
python3.11 -m pip install video-ai-studio  # Use specific version
```

### Permission Errors

```bash
pip install --user video-ai-studio  # User installation
# Or use virtual environment (recommended)
```

### Dependency Conflicts

```bash
python -m venv fresh_env
source fresh_env/bin/activate
pip install video-ai-studio
```

### Common Validation Errors

| Error | Solution |
|-------|----------|
| "Model not found" | Check model name in [Models Reference](../../reference/models.md) |
| "Missing required param" | Add required parameter to step |
| "Invalid step reference" | Ensure `input_from` matches existing step name |

---

## Platform-Specific Notes

### Windows
- Use PowerShell or Command Prompt
- Ensure Python is in PATH

### macOS
- Install Python via Homebrew: `brew install python@3.11`
- May need Xcode command line tools: `xcode-select --install`

### Linux
- May need `python3-venv` package: `sudo apt install python3-venv`

---

[Back to Documentation Index](../../index.md) | [Next: Learning Path](learning-path.md)
