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

- **Unified Interface**: Single package with console commands `ai-content-pipeline` and `aicp`
- **73 AI models across 12 categories** — see [Models Reference](docs/reference/models.md)
- **Central Model Registry**: Single source of truth in `registry.py` + `registry_data.py`
- **Click-based CLI**: All commands use Click framework, vimax available as `aicp vimax` subgroup
- **Unix-style flags**: `--json`, `--quiet`, `--stream`, `--input` for scripting and CI
- **YAML Configuration**: Multi-step content generation workflows
- **Parallel Execution**: 2-3x speedup with `PIPELINE_PARALLEL_ENABLED=true`

## Environment Setup

### Python Virtual Environment (Required)
```bash
# Create and activate virtual environment (run from project root)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install all dependencies from root
pip install -e .
# or: pip install -r requirements.txt
```

**Memory**: Virtual environment at project root `venv/`. Always activate before running scripts (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on Linux/Mac).

## Common Commands

### CLI Commands
```bash
# List available AI models
aicp list-models

# Generate single image
aicp generate-image --text "A beautiful sunset" --model flux_dev

# Create video from text (text -> image -> video)
aicp create-video --text "A beautiful sunset"

# Run pipeline from YAML config
aicp run-chain --config input/pipelines/config.yaml

# Run with parallel execution (2-3x speedup)
PIPELINE_PARALLEL_ENABLED=true aicp run-chain --config config.yaml

# Analyze video with AI (Gemini 3 Pro via FAL)
aicp analyze-video -i video.mp4

# Generate avatar with lip-sync
aicp generate-avatar --image-url "https://..." --audio-url "https://..."

# Transcribe audio
aicp transcribe --input audio.mp3

# Generate image grid
aicp generate-grid --text "mountain landscape" --layout 2x2

# Upscale image
aicp upscale-image --image photo.png --upscale 2

# Transfer motion from video to image
aicp transfer-motion --image-url "https://..." --video-url "https://..."

# Novel-to-video pipeline (vimax subgroup)
aicp vimax idea2video --idea "A samurai's journey at sunrise"
aicp vimax novel2movie --novel novel.txt --storyboard-only

# JSON output for scripting
aicp list-models --json | jq '.text_to_video[]'
```

See [CLI Reference](docs/reference/cli-commands.md) for full command documentation.

### Testing Commands
```bash
# Run full pytest suite (~844 tests)
python -m pytest tests/ -v

# Registry tests only
python -m pytest tests/test_registry.py tests/test_registry_data.py tests/test_auto_discovery.py -v

# Click CLI tests
python -m pytest tests/test_click_app.py tests/test_main_cli_flags.py -v

# Quick smoke tests
python tests/test_core.py

# Validate registry consistency
python scripts/validate_registry.py
```

## Architecture

### Package Structure
```
ai-content-pipeline/
├── packages/
│   ├── core/
│   │   ├── ai_content_pipeline/     # Main pipeline + central registry + Click CLI
│   │   │   ├── registry.py          # ModelDefinition + ModelRegistry (source of truth)
│   │   │   ├── registry_data.py     # All 73 model registrations
│   │   │   ├── _version.py          # Single source of truth for version
│   │   │   └── cli/                 # Click CLI (click_app.py + commands/)
│   │   └── ai_content_platform/     # Platform framework + vimax subgroup (aicp vimax)
│   ├── providers/
│   │   ├── google/veo/              # Google Veo integration
│   │   └── fal/                     # FAL AI services
│   │       ├── text-to-image/       # Image generation (8 models)
│   │       ├── image-to-image/      # Image transformation (8 models)
│   │       ├── text-to-video/       # Video generation (10 models)
│   │       ├── image-to-video/      # Image-to-video (15 models)
│   │       ├── video-to-video/      # Video-to-video (4 models)
│   │       ├── avatar-generation/   # Avatar creation (10 models)
│   │       └── speech-to-text/      # Speech transcription (1 model)
│   └── services/
│       ├── text-to-speech/          # ElevenLabs TTS
│       └── video-tools/             # Video processing
├── scripts/                         # Validation scripts
├── input/                           # Configuration files
├── output/                          # Generated content
├── tests/                           # Test suites (pytest, ~844 tests)
├── docs/                            # Documentation (see docs/index.md)
└── setup.py                         # Package installation
```

See [Architecture Overview](docs/reference/architecture.md) and [Package Structure](docs/reference/package-structure.md) for details.

### Key Architecture Points
- **Central Model Registry**: `registry.py` + `registry_data.py` — single source of truth for all model metadata
- **Auto-Discovery**: Generator classes use `MODEL_KEY` class attributes for automatic model registration
- **Click CLI**: Root group in `cli/click_app.py`, commands in `cli/commands/` (6 modules, ~19 commands + vimax)
- **Version**: Single source of truth in `_version.py`, read by both `setup.py` and `__init__.py`

## Configuration Requirements

### Package Installation
```bash
pip install -e .
```

### Environment Variables
Configure a single root `.env` file:
```
FAL_KEY=your_fal_api_key                    # Required for most models
GEMINI_API_KEY=your_gemini_api_key          # Image understanding, video analysis
OPENROUTER_API_KEY=your_openrouter_api_key  # Prompt generation, ViMax LLM calls
ELEVENLABS_API_KEY=your_elevenlabs_api_key  # TTS and speech-to-text
```

### Google Cloud Setup (for Veo models only)
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project your-project-id
```

## Testing Strategy

### Test Structure
- **`tests/test_registry.py`** - Central registry unit tests
- **`tests/test_registry_data.py`** - Registry data validation tests
- **`tests/test_auto_discovery.py`** - Model auto-discovery tests
- **`tests/test_click_app.py`** - Click CLI tests
- **`tests/test_main_cli_flags.py`** - Unix-style flag tests
- **`tests/test_t2v_cli_click.py`** - Text-to-video Click CLI tests
- **`tests/test_i2v_cli_click.py`** - Image-to-video Click CLI tests
- **`tests/test_core.py`** - Quick smoke tests
- **`tests/test_integration.py`** - Comprehensive integration tests
- **`tests/unit/`** - Unit tests for pipeline, vimax, and utilities

## Documentation

Detailed documentation lives in `docs/`. Key references:
- [Models Reference](docs/reference/models.md) - All 73 AI models with pricing
- [CLI Reference](docs/reference/cli-commands.md) - Full command documentation
- [Cost Management](docs/guides/optimization/cost-management.md) - Pricing and optimization
- [YAML Pipelines](docs/guides/pipelines/yaml-pipelines.md) - Custom workflow configuration
- [Full Documentation Index](docs/index.md) - Complete docs sitemap

## Project Development Guidelines

### Code Structure & Modularity
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
  For agents this looks like:
    - `agent.py` - Main agent definition and execution logic
    - `tools.py` - Tool functions used by the agent
    - `prompts.py` - System prompts
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Use python_dotenv and load_env()** for environment variables.

### Testing & Reliability
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

### PyPI Publishing
- **Build package**: `python -m build` (creates dist/ folder)
- **Check quality**: `twine check dist/*`
- **Publish to PyPI**: `twine upload dist/* --username __token__ --password $PYPI_API_TOKEN`
- **Version**: Update in `packages/core/ai_content_pipeline/ai_content_pipeline/_version.py`
- **Install published**: `pip install video-ai-studio`
- **PyPI URL**: https://pypi.org/project/video-ai-studio/

### Task Completion
- Track tasks via GitHub Issues and PRs.
- Add new sub-tasks or TODOs discovered during development as GitHub issues.

### Style & Conventions
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

### Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

### AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to.
