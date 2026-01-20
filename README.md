# AI Content Generation Suite

A comprehensive AI content generation package with multiple providers and services, consolidated into a single installable package.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/video-ai-studio)](https://pypi.org/project/video-ai-studio/)

> **⚡ Production-ready Python package with comprehensive CLI, parallel execution, and enterprise-grade architecture**

## 🎬 **Demo Video**

[![AI Content Generation Suite Demo](https://img.youtube.com/vi/xzvPrlKnXqk/maxresdefault.jpg)](https://www.youtube.com/watch?v=xzvPrlKnXqk)

*Click to watch the complete demo of AI Content Generation Suite in action*

## 🎨 Available AI Models

**40+ AI models across 8 categories** - showing top picks below. See [full models reference](docs/reference/models.md) for complete list.

### Text-to-Image (Top Picks)
| Model | Cost | Best For |
|-------|------|----------|
| `nano_banana_pro` | $0.002 | Fast & high-quality |
| `gpt_image_1_5` | $0.003 | GPT-powered generation |

### Image-to-Video (Top Picks)
| Model | Cost | Best For |
|-------|------|----------|
| `sora_2` | $0.40-1.20 | OpenAI quality |
| `kling_2_6_pro` | $0.50-1.00 | Professional quality |

### Text-to-Video (Top Picks)
| Model | Cost | Best For |
|-------|------|----------|
| `sora_2` | $0.40-1.20 | OpenAI quality |
| `kling_2_6_pro` | $0.35-1.40 | Quality + audio |

> **💡 Cost-Saving Tip:** Use `--mock` flag for FREE validation: `ai-content-pipeline generate-image --text "test" --mock`

📚 **[View all 40+ models →](docs/reference/models.md)**

## 🏷️ Latest Release

[![PyPI Version](https://img.shields.io/pypi/v/video-ai-studio)](https://pypi.org/project/video-ai-studio/)
[![GitHub Release](https://img.shields.io/github/v/release/donghaozhang/video-agent-skill)](https://github.com/donghaozhang/video-agent-skill/releases)

### What's New in v1.0.18
- ✅ Automated PyPI publishing via GitHub Actions
- 🔧 Consolidated setup files for cleaner package structure
- 🎯 All 40+ AI models with comprehensive parallel processing support
- 📦 Improved CI/CD workflow with skip-existing option

## 🚀 **FLAGSHIP: AI Content Pipeline**

The unified AI content generation pipeline with parallel execution support, multi-model integration, and YAML-based configuration.

### Core Capabilities
- **🔄 Unified Pipeline Architecture** - YAML/JSON-based configuration for complex multi-step workflows
- **⚡ Parallel Execution Engine** - 2-3x performance improvement with thread-based parallel processing
- **🎯 Type-Safe Configuration** - Pydantic models with comprehensive validation
- **💰 Cost Management** - Real-time cost estimation and tracking across all services
- **📊 Rich Logging** - Beautiful console output with progress tracking and performance metrics

### AI Service Integrations
- **🖼️ FAL AI** - Text-to-image, image-to-image, text-to-video, video generation, avatar creation
- **🗣️ ElevenLabs** - Professional text-to-speech with 20+ voice options
- **🎥 Google Vertex AI** - Veo video generation and Gemini text generation  
- **🔗 OpenRouter** - Alternative TTS and chat completion services

### Developer Experience
- **🛠️ Professional CLI** - Comprehensive command-line interface with Click
- **📦 Modular Architecture** - Clean separation of concerns with extensible design
- **🧪 Comprehensive Testing** - Unit and integration tests with pytest
- **📚 Type Hints** - Full type coverage for excellent IDE support

## 📦 Installation

### Quick Start
```bash
# Install from PyPI
pip install video-ai-studio

# Or install in development mode
pip install -e .
```

### 🔑 API Keys Setup

After installation, you need to configure your API keys:

1. **Download the example configuration:**
   ```bash
   # Option 1: Download from GitHub
   curl -o .env https://raw.githubusercontent.com/donghaozhang/video-agent-skill/main/.env.example
   
   # Option 2: Create manually
   touch .env
   ```

2. **Add your API keys to `.env`:**
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

### 📋 Dependencies
The package installs core dependencies automatically. See [requirements.txt](requirements.txt) for the complete list.

## 🛠️ Quick Start

### Console Commands
```bash
# List all available AI models
ai-content-pipeline list-models

# Generate image from text
ai-content-pipeline generate-image --text "epic space battle" --model flux_dev

# Create video (text → image → video)
ai-content-pipeline create-video --text "serene mountain lake"

# Run custom pipeline from YAML config
ai-content-pipeline run-chain --config config.yaml --input "cyberpunk city"

# Create example configurations
ai-content-pipeline create-examples

# Shortened command alias
aicp --help
```

### Python API
```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

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

## 📚 Package Structure

### Core Packages
- **[ai_content_pipeline](packages/core/ai_content_pipeline/)** - Main unified pipeline with parallel execution

### Provider Packages

#### Google Services
- **[google-veo](packages/providers/google/veo/)** - Google Veo video generation (Vertex AI)

#### FAL AI Services
- **[fal-video](packages/providers/fal/video/)** - Video generation (MiniMax Hailuo-02, Kling Video 2.1)
- **[fal-text-to-video](packages/providers/fal/text-to-video/)** - Text-to-video (Hailuo Pro, Veo 3, Kling v2.6 Pro, Sora 2/Pro)
- **[fal-image-to-video](packages/providers/fal/image-to-video/)** - Image-to-video (Veo 3, Hailuo, Kling, Wan v2.6)
- **[fal-avatar](packages/providers/fal/avatar/)** - Avatar generation with TTS integration
- **[fal-text-to-image](packages/providers/fal/text-to-image/)** - Text-to-image (Imagen 4, Seedream v3, FLUX.1)
- **[fal-image-to-image](packages/providers/fal/image-to-image/)** - Image transformation (Luma Photon Flash)
- **[fal-video-to-video](packages/providers/fal/video-to-video/)** - Video processing (ThinksSound + Topaz)

### Service Packages
- **[text-to-speech](packages/services/text-to-speech/)** - ElevenLabs TTS integration (20+ voices)
- **[video-tools](packages/services/video-tools/)** - Video processing utilities with AI analysis

## 🔧 Configuration

### Environment Setup
Create a `.env` file in the project root:
```env
# FAL AI API Configuration
FAL_KEY=your_fal_api_key

# Google Cloud Configuration (for Veo)
PROJECT_ID=your-project-id
OUTPUT_BUCKET_PATH=gs://your-bucket/veo_output/

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Optional: Gemini for AI analysis
GEMINI_API_KEY=your_gemini_api_key

# Optional: OpenRouter for additional models
OPENROUTER_API_KEY=your_openrouter_api_key
```

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
# Enable parallel execution
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml
```

Example parallel pipeline configuration:
```yaml
name: "Parallel Processing Example"
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
      - type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "A bird"
```

## 💰 Cost Management

### Cost Estimation
Always estimate costs before running pipelines:
```bash
# Estimate cost for a pipeline
ai-content-pipeline estimate-cost --config config.yaml
```

### Typical Costs
- **Text-to-Image**: $0.001-0.004 per image
- **Image-to-Image**: $0.01-0.05 per modification  
- **Text-to-Video**: $0.08-6.00 per video (model dependent)
- **Avatar Generation**: $0.02-0.05 per video
- **Text-to-Speech**: Varies by usage (ElevenLabs pricing)
- **Video Processing**: $0.05-2.50 per video (model dependent)

### Cost-Conscious Usage
- Use cheaper models for prototyping (`flux_schnell`, `hailuo`)
- Test with small batches before large-scale generation
- Monitor costs with built-in tracking

## 🧪 Testing

```bash
# Quick tests
python tests/run_all_tests.py --quick
```

📋 See [tests/README.md](tests/README.md) for complete testing guide.

## 💰 Cost Management

### Estimation
- **FAL AI Video**: ~$0.05-0.10 per video
- **FAL AI Text-to-Video**: ~$0.08 (MiniMax) to $2.50-6.00 (Google Veo 3)
- **FAL AI Avatar**: ~$0.02-0.05 per video
- **FAL AI Images**: ~$0.001-0.01 per image
- **Text-to-Speech**: Varies by usage (ElevenLabs pricing)

### Best Practices
1. Always run `test_setup.py` first (FREE)
2. Use cost estimation in pipeline manager
3. Start with cheaper models for testing
4. Monitor usage through provider dashboards

## 🔄 Development Workflow

### Making Changes
```bash
# Make your changes to the codebase
git add .
git commit -m "Your changes"
git push origin main
```

### Testing Installation
```bash
# Create test environment
python3 -m venv test_env
source test_env/bin/activate

# Install and test
pip install -e .
ai-content-pipeline --help
```

## 📋 Available Commands

### AI Content Pipeline Commands
- `ai-content-pipeline list-models` - List all available models
- `ai-content-pipeline generate-image` - Generate image from text
- `ai-content-pipeline create-video` - Create video from text
- `ai-content-pipeline run-chain` - Run custom YAML pipeline
- `ai-content-pipeline create-examples` - Create example configs
- `aicp` - Shortened alias for all commands

### Individual Package Commands
See [CLAUDE.md](CLAUDE.md) for detailed commands for each package.

## 📚 Documentation

- **[Quick Start Guide](docs/guides/getting-started/quick-start.md)** - Get running in 5 minutes
- **[Full Documentation](docs/index.md)** - Complete documentation index
- **[Models Reference](docs/reference/models.md)** - All 40+ AI models with pricing
- **[YAML Pipeline Guide](docs/guides/pipelines/yaml-pipelines.md)** - Create custom workflows
- **[Project Instructions](CLAUDE.md)** - Development guide

## 🏗️ Architecture

- **Unified Package Structure** - Single `setup.py` with consolidated dependencies
- **Consolidated Configuration** - Single `.env` file for all services
- **Modular Design** - Each service can be used independently or through the unified pipeline
- **Parallel Execution** - Optional parallel processing for improved performance
- **Cost-Conscious Design** - Built-in cost estimation and management

## 📚 Resources

### 🚀 AI Content Pipeline Resources
- [Pipeline Documentation](packages/core/ai_content_pipeline/docs/README.md)
- [Getting Started Guide](packages/core/ai_content_pipeline/docs/GETTING_STARTED.md)
- [YAML Configuration Reference](packages/core/ai_content_pipeline/docs/YAML_CONFIGURATION.md)
- [Parallel Execution Design](packages/core/ai_content_pipeline/docs/parallel_pipeline_design.md)

### Google Veo Resources
- [Veo API Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation)
- [Google GenAI SDK](https://github.com/google/generative-ai-python)
- [Vertex AI Console](https://console.cloud.google.com/vertex-ai)

### FAL AI Resources
- [FAL AI Platform](https://fal.ai/)
- [MiniMax Hailuo Documentation](https://fal.ai/models/fal-ai/minimax-video-01)
- [Kling Video 2.1 Documentation](https://fal.ai/models/fal-ai/kling-video/v2.1/standard/image-to-video/api)
- [Kling v2.6 Pro Documentation](https://fal.ai/models/fal-ai/kling-video/v2.6/pro/text-to-video/api)
- [Wan v2.6 Documentation](https://fal.ai/models/wan/v2.6/image-to-video)
- [Sora 2 Documentation](https://fal.ai/models/openai/sora/v2/text-to-video)
- [FAL AI Avatar Documentation](https://fal.ai/models/fal-ai/avatar-video)
- [ThinksSound API Documentation](https://fal.ai/models/fal-ai/thinksound/api)
- [Topaz Video Upscale Documentation](https://fal.ai/models/fal-ai/topaz/upscale/video/api)

### Text-to-Speech Resources
- [ElevenLabs API Documentation](https://elevenlabs.io/docs/capabilities/text-to-speech)
- [OpenRouter Platform](https://openrouter.ai/)
- [ElevenLabs Voice Library](https://elevenlabs.io/app/speech-synthesis/text-to-speech)
- [Text-to-Dialogue Documentation](https://elevenlabs.io/docs/cookbooks/text-to-dialogue)
- [Package Migration Guide](packages/services/text-to-speech/docs/MIGRATION_GUIDE.md)

### Additional Documentation
- [Project Instructions](CLAUDE.md) - Comprehensive development guide
- [Documentation](docs/) - Additional documentation and guides
- [Package Organization](docs/repository_organization_guide.md) - Package structure guide

## 🤝 Contributing

1. Follow the development patterns in [CLAUDE.md](CLAUDE.md)
2. Add tests for new features
3. Update documentation as needed
4. Test installation in fresh virtual environment
5. Commit with descriptive messages
