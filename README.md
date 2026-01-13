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

### Text-to-Image Models
| Model Name | Provider | Cost per Image | Resolution | Special Features |
|------------|----------|----------------|------------|------------------|
| `nano_banana_pro` | FAL AI | $0.002 | 1024x1024 | **Fast & high-quality, recommended** |
| `flux_dev` | FAL AI | $0.003 | 1024x1024 | High quality, FLUX.1 Dev |
| `flux_schnell` | FAL AI | $0.001 | 1024x1024 | Fast generation, FLUX.1 Schnell |
| `imagen4` | FAL AI | $0.004 | 1024x1024 | Google Imagen 4, photorealistic |
| `seedream_v3` | FAL AI | $0.002 | 1024x1024 | Seedream v3, bilingual support |
| `seedream3` | Replicate | $0.003 | Up to 2048px | ByteDance Seedream-3, high-res |
| `gen4` | Replicate | $0.08 | 720p/1080p | **Runway Gen-4, multi-reference guidance** |
| `gpt_image_1_5` | FAL AI | $0.003 | 1024x1024 | GPT-powered image generation |

### Image-to-Image Models
| Model Name | Provider | Cost per Image | Special Features |
|------------|----------|----------------|------------------|
| `nano_banana_pro_edit` | FAL AI | $0.015 | **Fast editing, recommended** |
| `photon_flash` | FAL AI | $0.02 | Luma Photon Flash, creative & fast |
| `photon_base` | FAL AI | $0.03 | Luma Photon Base, high quality |
| `flux_kontext` | FAL AI | $0.025 | FLUX Kontext Dev, contextual editing |
| `flux_kontext_multi` | FAL AI | $0.04 | FLUX Kontext Multi, multi-image |
| `seededit_v3` | FAL AI | $0.02 | ByteDance SeedEdit v3, precise editing |
| `clarity_upscaler` | FAL AI | $0.05 | Clarity AI upscaler |
| `gpt_image_1_5_edit` | FAL AI | $0.02 | GPT-powered image editing |

### Image-to-Video Models
| Model Name | Provider | Cost per Video | Resolution | Special Features |
|------------|----------|----------------|------------|------------------|
| `veo3` | FAL AI | $3.00 | Up to 1080p | Google Veo 3.0, latest model |
| `veo3_fast` | FAL AI | $2.00 | Up to 1080p | Google Veo 3.0 Fast |
| `veo2` | FAL AI | $2.50 | Up to 1080p | Google Veo 2.0 |
| `hailuo` | FAL AI | $0.08 | 720p | MiniMax Hailuo-02, budget-friendly |
| `kling` | FAL AI | $0.10 | 720p | Kling Video 2.1 |
| `wan_2_6` | FAL AI | $0.50-2.25 | 720p/1080p | Wan v2.6, multi-shot, audio input |

### Text-to-Video Models
| Model Name | Provider | Cost per Video | Resolution | Special Features |
|------------|----------|----------------|------------|------------------|
| `hailuo_pro` | FAL AI | $0.40-0.80 | 720p | MiniMax Hailuo-02 Pro, 5-10s |
| `kling_2_6_pro` | FAL AI | $0.35-1.40 | 720p | Kling v2.6 Pro, audio generation |
| `sora_2` | FAL AI | $0.40-1.20 | 720p | OpenAI Sora 2, 4-12s duration |
| `sora_2_pro` | FAL AI | $1.20-6.00 | 720p/1080p | OpenAI Sora 2 Pro, professional |

> **💡 Cost-Saving Tips:** Start with `kling_2_6_pro` (5s, no audio) for cheapest testing at ~$0.35. Use `--mock` flag for FREE parameter validation: `python -m fal_text_to_video.cli generate --prompt "test" --mock`. Premium models like `sora_2_pro` can cost up to $6.00/video.

### Image Understanding Models
| Model Name | Provider | Cost per Analysis | Special Features |
|------------|----------|-------------------|------------------|
| `gemini_describe` | Google | $0.001 | Basic image description |
| `gemini_detailed` | Google | $0.002 | Detailed image analysis |
| `gemini_classify` | Google | $0.001 | Image classification |
| `gemini_objects` | Google | $0.002 | Object detection |
| `gemini_ocr` | Google | $0.001 | Text extraction (OCR) |
| `gemini_composition` | Google | $0.002 | Artistic & technical analysis |
| `gemini_qa` | Google | $0.001 | Question & answer system |

### Text-to-Speech Models
| Model Name | Provider | Cost per Request | Special Features |
|------------|----------|------------------|------------------|
| `elevenlabs` | ElevenLabs | $0.05 | High quality TTS |
| `elevenlabs_turbo` | ElevenLabs | $0.03 | Fast generation |
| `elevenlabs_v3` | ElevenLabs | $0.08 | Latest v3 model |

### Prompt Generation Models
| Model Name | Provider | Cost per Request | Special Features |
|------------|----------|------------------|------------------|
| `openrouter_video_prompt` | OpenRouter | $0.002 | General video prompts |
| `openrouter_video_cinematic` | OpenRouter | $0.002 | Cinematic style prompts |
| `openrouter_video_realistic` | OpenRouter | $0.002 | Realistic style prompts |
| `openrouter_video_artistic` | OpenRouter | $0.002 | Artistic style prompts |
| `openrouter_video_dramatic` | OpenRouter | $0.002 | Dramatic style prompts |

### Audio & Video Processing
| Model Name | Provider | Cost per Request | Special Features |
|------------|----------|------------------|------------------|
| `thinksound` | FAL AI | $0.05 | AI audio generation |
| `topaz` | FAL AI | $1.50 | Video upscaling |

### 🌟 **Featured Model: Runway Gen-4**
The **`gen4`** model is our most advanced text-to-image model, offering unique capabilities:
- **Multi-Reference Guidance**: Use up to 3 reference images with tagging
- **Cinematic Quality**: Premium model for high-end generation  
- **@ Syntax**: Reference tagged elements in prompts (`@woman`, `@park`)
- **Variable Pricing**: $0.05 (720p) / $0.08 (1080p)

**Total Models: 40+ AI models across 8 categories**

## 🏷️ Latest Release

[![PyPI Version](https://img.shields.io/pypi/v/video-ai-studio?label=v1.0.15)](https://pypi.org/project/video-ai-studio/1.0.15/) 
[![GitHub Release](https://img.shields.io/github/v/release/donghaozhang/veo3-fal-video-ai?label=v1.0.15)](https://github.com/donghaozhang/veo3-fal-video-ai/releases/tag/v1.0.15)

### What's New in v1.0.15
- ✅ Enhanced GitHub deployment tracking for better release visibility
- 🧪 Improved mock mode testing infrastructure across all generators
- 🎯 All 40+ AI models with comprehensive parallel processing support

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
   curl -o .env https://raw.githubusercontent.com/donghaozhang/veo3-fal-video-ai/main/.env.example
   
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

- **[Project Instructions](CLAUDE.md)** - Comprehensive development guide
- **[Cursor AI Rules](.cursor/.cursorrules)** - Detailed project architecture and implementation patterns for AI assistants
- **[Documentation](docs/)** - Additional documentation and guides
- **Package READMEs** - Each package has its own README with specific instructions

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
