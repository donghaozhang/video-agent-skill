# AI Content Generation Suite

A comprehensive AI content generation package with multiple providers and services, consolidated into a single installable package.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/video-ai-studio)](https://pypi.org/project/video-ai-studio/)

> **Production-ready Python package with comprehensive CLI, parallel execution, and enterprise-grade architecture**

## Demo Video

[![AI Content Generation Suite Demo](https://img.youtube.com/vi/xzvPrlKnXqk/maxresdefault.jpg)](https://www.youtube.com/watch?v=xzvPrlKnXqk)

*Click to watch the complete demo of AI Content Generation Suite in action*

## Available AI Models

**73 AI models across 12 categories** - showing top picks below. See [full models reference](docs/reference/models.md) for complete list.

### Text-to-Image (Top Picks)
| Model | Cost | Best For |
|-------|------|----------|
| `nano_banana_pro` | $0.002 | Fast & high-quality |
| `gpt_image_1_5` | $0.003 | GPT-powered generation |
| `flux_dev` | $0.004 | Highest quality (12B params) |

### Text-to-Video (Top Picks)
| Model | Cost | Best For |
|-------|------|----------|
| `veo3` | $2.50-6.00 | Google's latest with audio |
| `sora_2` | $0.40-1.20 | OpenAI quality |
| `kling_2_6_pro` | $0.35-1.40 | Professional quality |

### Image-to-Video (Top Picks)
| Model | Cost | Best For |
|-------|------|----------|
| `veo_3_1_fast` | $2.50-6.00 | Google's latest i2v |
| `sora_2` | $0.40-1.20 | OpenAI quality |
| `kling_3_pro` | $0.50-1.00 | Latest Kling generation |

> **Cost-Saving Tip:** Use `--mock` flag for FREE validation: `aicp generate-image --text "test" --mock`

See [full models reference](docs/reference/models.md) for all 73 models with pricing.

## Latest Release

[![PyPI Version](https://img.shields.io/pypi/v/video-ai-studio)](https://pypi.org/project/video-ai-studio/)
[![GitHub Release](https://img.shields.io/github/v/release/donghaozhang/video-agent-skill)](https://github.com/donghaozhang/video-agent-skill/releases)

### What's New in v1.0.21
- Unix-style CLI: `--json`, `--quiet`, `--stream`, `--input` flags for scripting and CI
- Cross-platform binary builds (Linux, macOS ARM64/x86_64, Windows)
- Central model registry with 73 models across 12 categories
- Automated releases via GitHub Actions on every merge to main

## Installation

### From PyPI
```bash
pip install video-ai-studio
```

### Binary (no Python required)
Download standalone binaries from [GitHub Releases](https://github.com/donghaozhang/video-agent-skill/releases):
```bash
# Linux
curl -L https://github.com/donghaozhang/video-agent-skill/releases/download/latest/aicp-linux-x86_64 -o aicp
chmod +x aicp

# macOS (Apple Silicon)
curl -L https://github.com/donghaozhang/video-agent-skill/releases/download/latest/aicp-macos-arm64 -o aicp
chmod +x aicp

# Windows
curl -L https://github.com/donghaozhang/video-agent-skill/releases/download/latest/aicp-windows-x64.exe -o aicp.exe
```

### Development Mode
```bash
git clone https://github.com/donghaozhang/video-agent-skill.git
cd video-agent-skill
pip install -e .
```

### API Keys Setup

After installation, configure your API keys:

1. **Create a `.env` file:**
   ```bash
   curl -o .env https://raw.githubusercontent.com/donghaozhang/video-agent-skill/main/.env.example
   ```

2. **Add your API keys:**
   ```env
   # Required for most functionality
   FAL_KEY=your_fal_api_key_here

   # Optional - add as needed
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

3. **Get API keys from:**
   - **FAL AI**: https://fal.ai/dashboard (required for most models)
   - **Google Gemini**: https://makersuite.google.com/app/apikey
   - **OpenRouter**: https://openrouter.ai/keys
   - **ElevenLabs**: https://elevenlabs.io/app/settings

## Quick Start

### CLI Commands
```bash
# List all available AI models
aicp list-models

# Generate image from text
aicp generate-image --text "epic space battle" --model flux_dev

# Create video (text -> image -> video)
aicp create-video --text "serene mountain lake"

# Run custom pipeline from YAML config
aicp run-chain --config config.yaml --input "cyberpunk city"

# Analyze video with AI
aicp analyze-video -i video.mp4

# Generate avatar with lipsync
aicp generate-avatar --audio speech.mp3 --image portrait.jpg

# Transcribe audio
aicp transcribe --input audio.mp3

# Generate image grid
aicp generate-grid --text "mountain landscape" --layout 2x2

# Create example configurations
aicp create-examples
```

### Unix-Style Flags
All commands support machine-readable output for scripting and CI:
```bash
# JSON output for piping to jq
aicp list-models --json | jq '.text_to_video[]'

# Quiet mode (suppress non-essential output)
aicp create-video --text "sunset" --quiet

# Read prompt from stdin
echo "cinematic drone shot" | aicp create-video --input -

# Stream progress as JSONL events
aicp run-chain --config pipeline.yaml --stream

# Combine for CI usage
aicp run-chain --config pipeline.yaml --json --quiet | jq -r '.outputs.final.path'
```

### Python API
```python
from ai_content_pipeline.pipeline.manager import AIPipelineManager

# Initialize manager
manager = AIPipelineManager()

# Quick video creation
result = manager.quick_create_video(
    text="serene mountain lake",
    image_model="flux_dev",
    video_model="auto"
)

# Run custom chain
chain = manager.create_chain_from_config("config.yaml")
result = manager.execute_chain(chain, "input text")
```

## Available Commands

### Content Generation
| Command | Description |
|---------|-------------|
| `generate-image` | Generate image from text |
| `create-video` | Create video from text (text -> image -> video) |
| `run-chain` | Run custom YAML pipeline |
| `generate-avatar` | Generate avatar/lipsync video |
| `generate-grid` | Generate 2x2/3x3 image grid |
| `upscale-image` | Upscale image using SeedVR2 |
| `transfer-motion` | Transfer motion from video to image |
| `transcribe` | Transcribe audio using ElevenLabs |

### Discovery & Setup
| Command | Description |
|---------|-------------|
| `list-models` | List all available models |
| `list-avatar-models` | List avatar generation models |
| `list-video-models` | List video analysis models |
| `list-motion-models` | List motion transfer models |
| `list-speech-models` | List speech-to-text models |
| `analyze-video` | Analyze video with AI (Gemini) |
| `setup` | Create .env file with API key templates |
| `create-examples` | Create example configuration files |

### Project Management
| Command | Description |
|---------|-------------|
| `init-project` | Initialize project structure |
| `organize-project` | Organize files into project structure |
| `structure-info` | Show project structure info |

## Package Structure

### Core Packages
- **[ai_content_pipeline](packages/core/ai_content_pipeline/)** - Main unified pipeline with central model registry and parallel execution

### Provider Packages

#### FAL AI Services
- **[fal-text-to-video](packages/providers/fal/text-to-video/)** - Text-to-video (Veo 3, Kling v3, Sora 2, Hailuo Pro)
- **[fal-image-to-video](packages/providers/fal/image-to-video/)** - Image-to-video (Veo 3.1, Kling, Sora 2, Wan v2.6)
- **[fal-text-to-image](packages/providers/fal/text-to-image/)** - Text-to-image (FLUX.1, Imagen 4, Seedream v3)
- **[fal-image-to-image](packages/providers/fal/image-to-image/)** - Image transformation (Photon, FLUX Kontext, Clarity)
- **[fal-video-to-video](packages/providers/fal/video-to-video/)** - Video editing (Kling O3 Edit/V2V)
- **[fal-avatar](packages/providers/fal/avatar-generation/)** - Avatar creation (OmniHuman, VEED Fabric, Kling O1)
- **[fal-speech-to-text](packages/providers/fal/speech-to-text/)** - Speech transcription (ElevenLabs Scribe v2)

#### Google Services
- **[google-veo](packages/providers/google/veo/)** - Google Veo video generation (Vertex AI)

### Service Packages
- **[text-to-speech](packages/services/text-to-speech/)** - ElevenLabs TTS integration (20+ voices)
- **[video-tools](packages/services/video-tools/)** - Video processing utilities with AI analysis

## Configuration

### YAML Pipeline Configuration
```yaml
name: "Text to Video Pipeline"
description: "Generate video from text prompt"
steps:
  - name: "generate_image"
    type: "text_to_image"
    model: "flux_dev"
    aspect_ratio: "16:9"

  - name: "create_video"
    type: "image_to_video"
    model: "kling_video"
    input_from: "generate_image"
    duration: 8
```

### Parallel Execution
Enable parallel processing for 2-3x speedup:
```bash
PIPELINE_PARALLEL_ENABLED=true aicp run-chain --config config.yaml
```

## Cost Management

### Typical Costs
- **Text-to-Image**: $0.001-0.004 per image
- **Image-to-Image**: $0.01-0.05 per modification
- **Text-to-Video**: $0.08-6.00 per video (model dependent)
- **Image-to-Video**: $0.08-6.00 per video (model dependent)
- **Avatar Generation**: $0.08-0.25 per video
- **Text-to-Speech**: Varies by usage (ElevenLabs pricing)
- **Video Processing**: $0.05-2.50 per video (model dependent)

### Tips
- Use cheaper models for prototyping (`flux_schnell`, `hailuo`)
- Use `--mock` flag for free validation before real API calls
- Test with small batches before large-scale generation
- Monitor costs with built-in tracking

## Testing

```bash
# Full test suite (~762 tests)
python -m pytest tests/ -v

# Quick smoke tests
python tests/test_core.py

# Registry validation
python scripts/validate_registry.py
```

## Development Workflow

### Making Changes
```bash
git add .
git commit -m "Your changes"
git push origin main
```

### Testing Installation
```bash
python3 -m venv test_env
source test_env/bin/activate  # Linux/Mac
# or: test_env\Scripts\activate  # Windows

pip install -e .
aicp --help
```

## Documentation

- **[Setup Guide](docs/guides/getting-started/setup.md)** - Installation and configuration
- **[Full Documentation](docs/index.md)** - Complete documentation index
- **[Models Reference](docs/reference/models.md)** - All 73 AI models with pricing
- **[YAML Pipeline Guide](docs/guides/pipelines/yaml-pipelines.md)** - Create custom workflows
- **[Cost Management](docs/guides/optimization/cost-management.md)** - Optimize spending
- **[Project Instructions](CLAUDE.md)** - Development guide

## Architecture

- **Central Model Registry** - Single source of truth for all 73 model definitions (`registry.py` + `registry_data.py`)
- **Auto-Discovery** - Generator classes use `MODEL_KEY` attributes for automatic registration
- **Unix-Style CLI** - `--json`, `--quiet`, `--stream` flags; stable exit codes; stdin/stdout piping
- **Parallel Execution** - Thread-based processing with `PIPELINE_PARALLEL_ENABLED=true`
- **Modular Design** - Each service can be used independently or through the unified pipeline
- **Cross-Platform Binaries** - Standalone `aicp` binaries via PyInstaller (no Python required)

## Resources

### AI Content Pipeline
- [Pipeline Documentation](packages/core/ai_content_pipeline/docs/README.md)
- [Getting Started Guide](packages/core/ai_content_pipeline/docs/GETTING_STARTED.md)
- [YAML Configuration Reference](packages/core/ai_content_pipeline/docs/YAML_CONFIGURATION.md)
- [Parallel Execution Design](packages/core/ai_content_pipeline/docs/parallel_pipeline_design.md)

### Provider Documentation
- [FAL AI Platform](https://fal.ai/)
- [Google Vertex AI / Veo](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation)
- [ElevenLabs API](https://elevenlabs.io/docs/capabilities/text-to-speech)
- [OpenRouter Platform](https://openrouter.ai/)

## Contributing

1. Follow the development patterns in [CLAUDE.md](CLAUDE.md)
2. Add tests for new features
3. Update documentation as needed
4. Test installation in fresh virtual environment
5. Commit with descriptive messages
