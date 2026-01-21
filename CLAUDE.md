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
- **Multi-Model Support**: 50 AI models across 8 categories
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

**Memory**: Virtual environment created at `/home/zdhpe/veo3-video-generation/venv/` with all dependencies installed. Always activate before running scripts.

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
# Quick smoke tests (30 seconds)
python tests/test_core.py

# Full integration tests (2-3 minutes)
python tests/test_integration.py

# Interactive demonstration
python tests/demo.py --interactive

# Run all tests
python tests/run_all_tests.py

# Quick test mode
python tests/run_all_tests.py --quick
```

## Architecture

### Package Structure
```
ai-content-pipeline/
├── packages/
│   ├── core/
│   │   ├── ai_content_pipeline/     # Main unified pipeline
│   │   └── ai_content_platform/     # Platform framework
│   ├── providers/
│   │   ├── google/veo/              # Google Veo integration
│   │   └── fal/                     # FAL AI services
│   │       ├── text-to-image/       # Image generation
│   │       ├── image-to-image/      # Image transformation
│   │       ├── text-to-video/       # Video generation
│   │       └── avatar-generation/   # Avatar creation
│   └── services/
│       ├── text-to-speech/          # ElevenLabs TTS
│       └── video-tools/             # Video processing
├── input/                           # Configuration files
├── output/                          # Generated content
├── tests/                           # Test suites
├── docs/                            # Documentation
└── setup.py                         # Package installation
```

### AI Content Pipeline Architecture
- **Unified Package**: Single installable package with console commands
- **YAML Configuration**: Multi-step workflow definitions
- **Parallel Execution**: Thread-based processing with `PIPELINE_PARALLEL_ENABLED=true`
- **Multi-Model Support**: 50 AI models across 8 categories
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
- **`tests/test_core.py`** - Quick smoke tests (30 seconds)
- **`tests/test_integration.py`** - Comprehensive integration tests (2-3 minutes)
- **`tests/demo.py`** - Interactive demonstration and examples
- **`tests/run_all_tests.py`** - Test runner with `--quick` option

### Test Commands
```bash
# Quick development check
python tests/test_core.py

# Full validation
python tests/test_integration.py

# Interactive demo
python tests/demo.py --interactive

# Run all tests
python tests/run_all_tests.py

# Quick mode (core tests only)
python tests/run_all_tests.py --quick
```

## Available AI Models

### 📦 Text-to-Image (8 models)
- **FLUX.1 Dev** - Highest quality, 12B parameter model
- **FLUX.1 Schnell** - Fastest inference speed
- **Imagen 4** - Google's photorealistic model
- **Seedream v3** - Multilingual support
- **Nano Banana Pro** - Fast, high-quality generation
- **GPT Image 1.5** - GPT-powered image generation

### 📦 Image-to-Image (8 models)
- **Photon Flash** - Creative modifications
- **Photon Base** - Standard transformations
- **FLUX variants** - Advanced image editing
- **Clarity Upscaler** - Resolution enhancement
- **Nano Banana Pro Edit** - Fast image editing
- **GPT Image 1.5 Edit** - GPT-powered image editing

### 📦 Image-to-Video (11 models)
- **Veo 3** - Google's latest video model
- **Veo 2** - Previous generation Veo
- **Hailuo** - MiniMax video generation
- **Kling** - High-quality video synthesis

### 📦 Image Understanding (7 models)
- **Gemini variants** - Description, classification, OCR, Q&A

### 📦 Prompt Generation (5 models)
- **OpenRouter models** - Video prompt optimization

### 📦 Audio/Video Processing (2 models)
- **ThinksSound** - Audio generation
- **Topaz** - Video upscaling

### 📦 Avatar Generation (9 models)
- **OmniHuman v1.5** - High-quality audio-driven animation (ByteDance)
- **VEED Fabric 1.0** - Cost-effective lip-sync
- **VEED Fabric 1.0 Fast** - Speed-optimized lip-sync
- **VEED Fabric 1.0 Text** - Text-to-speech + lip-sync
- **Kling O1 Ref-to-Video** - Character consistency
- **Kling O1 V2V Reference** - Style transfer
- **Kling O1 V2V Edit** - Video editing
- **Kling v2.6 Motion Control** - Motion transfer from video to image
- **AI Avatar Multi** - Multi-person conversations

## Key Features

### 🎯 **Unified Interface**
- Single package installation with `pip install -e .`
- Console commands: `ai-content-pipeline` and `aicp`
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
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASK.md`** before starting a new task. If the task isn't listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.
- **Use venv_linux** (the virtual environment) whenever executing Python commands, including for unit tests.

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
- **Mark completed tasks in `TASK.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASK.md` under a "Discovered During Work" section.

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