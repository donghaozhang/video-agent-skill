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
| `kling_3_pro` | $0.50-1.12 | Latest Kling generation |

### Image-to-Video (Top Picks)
| Model | Cost | Best For |
|-------|------|----------|
| `veo_3_1_fast` | $1.20 | Google's latest i2v |
| `sora_2` | $0.40-1.20 | OpenAI quality |
| `kling_3_pro` | $0.50-1.12 | Latest Kling generation |

> **Cost-Saving Tip:** Use `--mock` flag for FREE validation: `aicp generate-image --text "test" --mock`

See [full models reference](docs/reference/models.md) for all 73 models with pricing.

## Latest Release

[![PyPI Version](https://img.shields.io/pypi/v/video-ai-studio)](https://pypi.org/project/video-ai-studio/)
[![GitHub Release](https://img.shields.io/github/v/release/donghaozhang/video-agent-skill)](https://github.com/donghaozhang/video-agent-skill/releases)

### What's New in v1.0.23
- Click-based CLI with `aicp vimax` subgroup for novel-to-video pipelines
- Unix-style flags: `--json`, `--quiet`, `--stream`, `--input` for scripting and CI
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

## Documentation

For detailed guides and references, see the [full documentation](docs/index.md):

| Topic | Link |
|-------|------|
| Setup & Installation | [Setup Guide](docs/guides/getting-started/setup.md) |
| All 73 AI Models | [Models Reference](docs/reference/models.md) |
| CLI Commands | [CLI Reference](docs/reference/cli-commands.md) |
| YAML Pipelines | [Pipeline Guide](docs/guides/pipelines/yaml-pipelines.md) |
| Cost Management | [Cost Guide](docs/guides/optimization/cost-management.md) |
| Architecture | [Architecture Overview](docs/reference/architecture.md) |
| Package Structure | [Package Reference](docs/reference/package-structure.md) |
| Testing | [Testing Guide](docs/guides/support/testing.md) |
| Python API | [API Reference](docs/api/python-api.md) |
| Troubleshooting | [FAQ & Troubleshooting](docs/guides/support/troubleshooting.md) |
| Contributing | [Contributing Guide](docs/guides/contributing/contributing.md) |
| Changelog | [Version History](docs/CHANGELOG.md) |
| Development Guide | [CLAUDE.md](CLAUDE.md) |

## Contributing

1. Follow the development patterns in [CLAUDE.md](CLAUDE.md)
2. Add tests for new features
3. Update documentation as needed
4. Test installation in fresh virtual environment
5. Commit with descriptive messages
