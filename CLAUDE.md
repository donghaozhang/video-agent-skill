# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Workflow Commands

**Always run after each successful implementation:**
```bash
git add .
git commit -m "descriptive commit message"
git push origin main
```

## Project Overview

This is the **AI Content Pipeline** - a unified Python package for multi-modal AI content generation.

### 🚀 **AI Content Pipeline Package**
- **Unified Interface**: Single package with console commands `ai-content-pipeline` and `aicp`
- **YAML Configuration**: Multi-step content generation workflows
- **Parallel Execution**: 2-3x speedup with thread-based parallel processing
- **Multi-Model Support**: 73 AI models across 12 categories
- **Central Model Registry**: Single source of truth in `registry.py` + `registry_data.py`
- **Cost Management**: Built-in cost estimation and tracking
- **Organized Output**: Structured output directories with proper file management

## Environment Setup

### Python Virtual Environment (Required)
```bash
# Create and activate virtual environment (run from project root)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install all dependencies from root
pip install -r requirements.txt
```

**Memory**: Virtual environment at project root `venv/`. Always activate before running scripts (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on Linux/Mac).

## Common Commands

### 🚀 AI Content Pipeline Commands
```bash
# Activate venv first: source venv/bin/activate

# List available AI models
ai-content-pipeline list-models

# Run pipeline from YAML config
ai-content-pipeline run-chain --config input/pipelines/config.yaml

# Run with parallel execution (2-3x speedup)
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml

# Generate single image
ai-content-pipeline generate-image --text "A beautiful sunset" --model flux_dev

# Create video from text (text → image → video)
ai-content-pipeline create-video --text "A beautiful sunset"

# Shortened alias
aicp --help

# Analyze video with AI (Gemini 3 Pro via FAL)
ai-content-pipeline analyze-video -i video.mp4

# Analyze with specific model and type
ai-content-pipeline analyze-video -i video.mp4 -m gemini-3-pro -t timeline

# Available models: gemini-3-pro, gemini-2.5-pro, gemini-2.5-flash, gemini-direct
# Available types: timeline, describe, transcribe

# List video analysis models
ai-content-pipeline list-video-models
```

### 🧪 Testing Commands
```bash
# Run full pytest suite (~572 tests, ~25s)
python -m pytest tests/ -v

# Registry tests only
python -m pytest tests/test_registry.py tests/test_registry_data.py tests/test_auto_discovery.py -v

# Quick smoke tests (30 seconds)
python tests/test_core.py

# Full integration tests (2-3 minutes)
python tests/test_integration.py

# Interactive demonstration
python tests/demo.py --interactive

# Validate registry consistency
python scripts/validate_registry.py
```

## Architecture

### Package Structure
```
ai-content-pipeline/
├── packages/
│   ├── core/
│   │   ├── ai_content_pipeline/     # Main unified pipeline + central registry
│   │   │   ├── registry.py          # ModelDefinition + ModelRegistry (source of truth)
│   │   │   └── registry_data.py     # All 73 model registrations
│   │   └── ai_content_platform/     # Platform framework + vimax subgroup (aicp vimax)
│   ├── providers/
│   │   ├── google/veo/              # Google Veo integration
│   │   └── fal/                     # FAL AI services
│   │       ├── text-to-image/       # Image generation (8 models)
│   │       ├── image-to-image/      # Image transformation (8 models)
│   │       ├── text-to-video/       # Video generation (10 models, Click CLI)
│   │       ├── image-to-video/      # Image-to-video (15 models, Click CLI)
│   │       ├── video-to-video/      # Video-to-video (4 models)
│   │       ├── avatar-generation/   # Avatar creation (10 models)
│   │       └── speech-to-text/      # Speech transcription (1 model)
│   └── services/
│       ├── text-to-speech/          # ElevenLabs TTS
│       └── video-tools/             # Video processing
├── scripts/                         # Validation scripts
├── input/                           # Configuration files
├── output/                          # Generated content
├── tests/                           # Test suites (pytest)
├── docs/                            # Documentation
└── setup.py                         # Package installation
```

### AI Content Pipeline Architecture
- **Unified Package**: Single installable package with console commands (`ai-content-pipeline`, `aicp`); vimax available as `aicp vimax` subgroup
- **Central Model Registry**: `registry.py` + `registry_data.py` — single source of truth for all model metadata
- **Auto-Discovery**: Generator classes use `MODEL_KEY` class attributes for automatic model registration
- **Provider CLIs**: Provider-level CLIs use Click framework (`fal-text-to-video`, `fal-image-to-video`)
- **YAML Configuration**: Multi-step workflow definitions
- **Parallel Execution**: Thread-based processing with `PIPELINE_PARALLEL_ENABLED=true`
- **Multi-Model Support**: 73 AI models across 12 categories
- **Cost Management**: Built-in estimation and tracking
- **Organized Output**: Structured file management

## Configuration Requirements

### Package Installation
```bash
# Install the package
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

### Environment Variables
Configure a single root `.env` file:
```
# FAL AI (required for most models)
FAL_KEY=your_fal_api_key

# Google Cloud (for Veo models)
PROJECT_ID=your-project-id
OUTPUT_BUCKET_PATH=gs://your-bucket/output/

# ElevenLabs (for TTS)
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# OpenRouter (for prompt generation)
OPENROUTER_API_KEY=your_openrouter_api_key

# Gemini (for image understanding)
GEMINI_API_KEY=your_gemini_api_key
```

### Google Cloud Setup (for Veo models)
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project your-project-id
```

## Development Patterns

### Error Handling
- Comprehensive try-catch blocks with detailed error messages
- Graceful failure handling with meaningful error responses
- Built-in validation for all inputs and configurations

### Authentication
- API key-based authentication for most services
- Environment variable configuration via `.env` file
- Automatic credential management where possible

### File Management
- Organized output in `output/` directory with timestamped folders
- Automatic file naming and organization
- Support for both local and remote file inputs

## Testing Strategy

### Test Structure
- **`tests/test_registry.py`** - Central registry unit tests
- **`tests/test_registry_data.py`** - Registry data validation tests
- **`tests/test_auto_discovery.py`** - Model auto-discovery tests
- **`tests/test_t2v_cli_click.py`** - Text-to-video Click CLI tests
- **`tests/test_i2v_cli_click.py`** - Image-to-video Click CLI tests
- **`tests/test_core.py`** - Quick smoke tests
- **`tests/test_integration.py`** - Comprehensive integration tests
- **`tests/unit/`** - Unit tests for pipeline, vimax, and utilities

### Test Commands
```bash
# Full pytest suite (~572 tests, ~25s)
python -m pytest tests/ -v

# Registry tests only
python -m pytest tests/test_registry.py tests/test_registry_data.py tests/test_auto_discovery.py -v

# Validate registry consistency
python scripts/validate_registry.py

# Quick smoke tests
python tests/test_core.py
```

## Available AI Models (73 models, 12 categories)

### 📦 Text-to-Image (8 models)
- **FLUX.1 Dev** - Highest quality, 12B parameter model
- **FLUX.1 Schnell** - Fastest inference speed
- **Runway Gen-4** - Runway's latest generation model
- **Imagen 4** - Google's photorealistic model
- **Seedream v3 / v3 Fast** - Multilingual support
- **Nano Banana Pro** - Fast, high-quality generation
- **GPT Image 1.5** - GPT-powered image generation

### 📦 Image-to-Image (8 models)
- **Photon Flash / Base** - Creative modifications and standard transformations
- **FLUX Kontext Pro / Max** - Advanced image editing
- **Clarity Upscaler** - Resolution enhancement
- **Nano Banana Pro Edit** - Fast image editing
- **GPT Image 1.5 Edit** - GPT-powered image editing
- **SeedEdit v3** - ByteDance image editing

### 📦 Text-to-Video (10 models)
- **Veo 3 / Veo 3 Fast** - Google's latest video models
- **Kling v2.6 Pro** - High-quality Kling video
- **Kling v3 Standard / Pro** - Latest Kling generation
- **Kling O3 Pro** - Omni 3 with element-based character consistency
- **Sora 2 / Sora 2 Pro** - OpenAI video generation
- **Hailuo Pro** - MiniMax video generation
- **Grok Imagine** - xAI text-to-video with audio

### 📦 Image-to-Video (15 models)
- **Veo 3.1 Fast** - Google's latest i2v model
- **Hailuo** - MiniMax i2v generation
- **Kling v2.1 / v2.6 Pro / v3 Standard / v3 Pro** - Kling i2v variants
- **Kling O3 Standard / O3 Pro** - Omni 3 i2v with element consistency
- **Seedance v1.5 Pro** - ByteDance dance/motion video
- **Sora 2 / Sora 2 Pro** - OpenAI i2v generation
- **Wan v2.6** - Alibaba i2v generation
- **Grok Imagine** - xAI i2v with audio

### 📦 Video-to-Video (4 models)
- **Kling O3 Pro Edit / Standard Edit** - AI video editing
- **Kling O3 Pro V2V / Standard V2V** - Video-to-video reference transfer

### 📦 Image Understanding (7 models)
- **Gemini variants** - Description, classification, OCR, Q&A, composition, objects

### 📦 Prompt Generation (5 models)
- **OpenRouter models** - Video prompt optimization (artistic, cinematic, dramatic, realistic styles)

### 📦 Add Audio (1 model)
- **ThinkSound** - AI audio generation from video

### 📦 Upscale Video (1 model)
- **Topaz** - AI video upscaling

### 📦 Avatar Generation (10 models)
- **OmniHuman v1.5** - High-quality audio-driven animation (ByteDance)
- **VEED Fabric 1.0 / Fast / Text** - Lip-sync variants
- **Kling O1 Ref-to-Video** - Character consistency
- **Kling O1 V2V Reference / Edit** - Style transfer and editing
- **Kling v2.6 Motion Control** - Motion transfer from video to image
- **Grok Video Edit** - xAI video editing
- **AI Avatar Multi** - Multi-person conversations

### 📦 Text-to-Speech (3 models)
- **ElevenLabs Standard / Turbo / v3** - Text-to-speech generation

### 📦 Speech-to-Text (1 model)
- **ElevenLabs Scribe v2** - Fast, accurate transcription with speaker diarization

## Key Features

### 🎯 **Unified Interface**
- Single package installation with `pip install -e .`
- Console commands: `ai-content-pipeline`, `aicp` (vimax available as `aicp vimax` subgroup)
- Provider CLIs: `fal-text-to-video`, `fal-image-to-video` (Click-based)
- Consistent API across all AI models

### 📋 **YAML Configuration**
- Multi-step workflow definitions
- Parameter templating with `{{step_N.output}}`
- Cost estimation before execution

### ⚡ **Parallel Execution**
- Thread-based parallel processing
- 2-3x speedup for multi-step pipelines
- Enable with `PIPELINE_PARALLEL_ENABLED=true`

### 💰 **Cost Management**
- Built-in cost estimation for all models
- Per-step and total pipeline costs
- Transparent pricing information

### 📁 **Organized Output**
- Structured output directories
- Automatic file naming and organization
- Easy result retrieval and management

## Environment Variables
- Single root `.env` file for all configurations
- Never commit `.env` files to version control
- Use environment-specific configurations as needed

## Cost Management
- Built-in cost estimation for all models
- Run `ai-content-pipeline estimate --config config.yaml` before execution
- Model pricing:
  - **Text-to-Image**: $0.001-0.004 per image
  - **Image-to-Image**: $0.01-0.05 per modification
  - **Image-to-Video**: $0.08-6.00 per video (model dependent)
  - **Avatar Generation**: $0.08-0.25 per video (resolution dependent)
  - **Audio Generation**: Varies by usage and model
- Always check costs before running large pipelines

## Project Development Guidelines

### 🔄 Project Awareness & Context
- **Always read `CLAUDE.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in this file.
- **Activate the virtual environment** (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on Linux/Mac) before executing Python commands.

### 🧱 Code Structure & Modularity
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
  For agents this looks like:
    - `agent.py` - Main agent definition and execution logic 
    - `tools.py` - Tool functions used by the agent 
    - `prompts.py` - System prompts
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Use python_dotenv and load_env()** for environment variables.

### 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case
- **Write ONE test file per task** focusing on core functionality only.
- **Test only the most critical features** - avoid over-testing edge cases.
- **Keep tests simple and fast** - complex integration tests slow development.

### 📦 PyPI Publishing
- **Build package**: `python -m build` (creates dist/ folder)
- **Check quality**: `twine check dist/*`
- **Publish to PyPI**: `twine upload dist/* --username __token__ --password $PYPI_API_TOKEN`
- **Version**: Update in setup.py before building
- **Install published**: `pip install video-ai-studio`
- **PyPI URL**: https://pypi.org/project/video-ai-studio/

### ✅ Task Completion
- Track tasks via GitHub Issues and PRs.
- Add new sub-tasks or TODOs discovered during development as GitHub issues.

### 📎 Style & Conventions
- **Use Python** as the primary language.
- **Follow PEP8**, use type hints, and format with `black`.
- **Use `pydantic` for data validation**.
- Use `FastAPI` for APIs and `SQLAlchemy` or `SQLModel` for ORM if applicable.
- Write **docstrings for every function** using the Google style:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```

### 📚 Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

### 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`.