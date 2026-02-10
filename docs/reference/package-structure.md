# Package Structure Reference

Detailed overview of the AI Content Generation Suite package organization.

## Top-Level Structure

```text
video-agent-skill/
├── packages/                 # Main source code
│   ├── core/                # Core pipeline functionality
│   ├── providers/           # AI provider integrations
│   └── services/            # Shared services
├── docs/                    # Documentation
├── tests/                   # Test suites
├── input/                   # Input configurations
├── output/                  # Generated content
├── .env                     # Environment configuration
├── setup.py                 # Package installation
├── requirements.txt         # Dependencies
├── CLAUDE.md                # Development guide
└── README.md                # Project overview
```

---

## Core Package

The main pipeline functionality.

```text
packages/core/
└── ai_content_pipeline/
    ├── __init__.py          # Package exports
    ├── pipeline/            # Pipeline engine
    │   ├── __init__.py
    │   ├── manager.py       # Main AIPipelineManager class
    │   ├── builder.py       # Pipeline builder
    │   ├── executor.py      # Step execution
    │   └── parallel.py      # Parallel processing
    ├── config/              # Configuration handling
    │   ├── __init__.py
    │   ├── loader.py        # YAML/JSON loading
    │   ├── validator.py     # Schema validation
    │   └── models.py        # Pydantic models
    ├── providers/           # Provider abstractions
    │   ├── __init__.py
    │   ├── base.py          # Base provider class
    │   ├── fal.py           # FAL AI provider
    │   ├── google.py        # Google provider
    │   └── elevenlabs.py    # ElevenLabs provider
    ├── cli/                 # Command-line interface
    │   ├── __init__.py
    │   ├── main.py          # CLI entry point
    │   └── commands/        # Individual commands
    │       ├── __init__.py
    │       ├── generate.py
    │       ├── pipeline.py
    │       └── utils.py
    └── utils/               # Utilities
        ├── __init__.py
        ├── logging.py       # Logging setup
        ├── cost.py          # Cost estimation
        └── files.py         # File handling
```

### Key Files

#### `pipeline/manager.py`

Main orchestration class for all pipeline operations.

```python
class AIPipelineManager:
    """Central manager for AI content pipelines."""

    def generate_image(self, prompt, model="flux_dev") -> GenerationResult:
        """Generate image from text."""

    def create_video(self, prompt, image_model, video_model) -> GenerationResult:
        """Create video from text (image + video)."""

    def run_pipeline(self, config, input_text) -> List[StepResult]:
        """Execute YAML pipeline configuration."""

    def estimate_cost(self, config) -> CostEstimate:
        """Estimate pipeline execution cost."""
```

#### `config/models.py`

Pydantic models for configuration validation.

```python
class StepConfig(BaseModel):
    name: str
    type: StepType
    model: Optional[str]
    params: Dict[str, Any]
    input_from: Optional[str]

class PipelineConfig(BaseModel):
    name: str
    description: Optional[str]
    settings: PipelineSettings
    steps: List[StepConfig]
```

#### `cli/main.py`

CLI entry point using Click framework.

```python
@click.group()
def cli():
    """AI Content Pipeline CLI."""

@cli.command()
@click.option("--text", required=True)
@click.option("--model", default="flux_dev")
def generate_image(text, model):
    """Generate image from text."""
```

---

## Providers Package

Individual AI provider integrations.

```text
packages/providers/
├── google/
│   └── veo/                 # Google Veo video generation
│       ├── __init__.py
│       ├── client.py        # Veo API client
│       └── config.py        # Veo configuration
└── fal/
    ├── text-to-image/       # FAL text-to-image
    │   ├── __init__.py
    │   ├── client.py
    │   └── models.py
    ├── image-to-image/      # FAL image-to-image
    │   ├── __init__.py
    │   ├── client.py
    │   └── models.py
    ├── image-to-video/      # FAL image-to-video
    │   ├── __init__.py
    │   ├── client.py
    │   └── models.py
    ├── text-to-video/       # FAL text-to-video
    │   ├── __init__.py
    │   ├── client.py
    │   └── models.py
    ├── video-to-video/      # FAL video processing
    │   ├── __init__.py
    │   ├── client.py
    │   └── models.py
    └── avatar/              # FAL avatar generation
        ├── __init__.py
        ├── client.py
        └── models.py
```

### Provider Structure

Each provider follows this pattern:

```python
# client.py
class FALTextToImageClient:
    """FAL AI text-to-image client."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FAL_KEY")

    def generate(self, prompt: str, model: str, **kwargs) -> GenerationResult:
        """Generate image from text prompt."""

    def get_supported_models(self) -> List[str]:
        """Return list of supported models."""

# models.py
class TextToImageRequest(BaseModel):
    prompt: str
    model: str = "flux_dev"
    width: int = 1024
    height: int = 1024

class TextToImageResponse(BaseModel):
    success: bool
    output_path: str
    cost: float
```

---

## Services Package

Shared services and utilities.

```text
packages/services/
├── text-to-speech/          # ElevenLabs TTS
│   ├── __init__.py
│   ├── client.py            # TTS client
│   ├── voices.py            # Voice definitions
│   └── docs/
│       ├── MIGRATION_GUIDE.md
│       └── elevenlabs_controls_guide.md
└── video-tools/             # Video processing
    ├── __init__.py
    ├── analysis.py          # Video analysis
    ├── processing.py        # Video processing
    └── docs/
        ├── API_REFERENCE.md
        └── ARCHITECTURE_OVERVIEW.md
```

---

## Tests Structure

```text
tests/
├── __init__.py
├── run_all_tests.py         # Test runner
├── test_core.py             # Quick smoke tests
├── test_integration.py      # Integration tests
├── demo.py                  # Interactive demo
├── unit/                    # Unit tests
│   ├── test_manager.py
│   ├── test_providers.py
│   └── test_config.py
├── integration/             # Integration tests
│   ├── test_pipelines.py
│   └── test_api_calls.py
└── fixtures/                # Test data
    ├── configs/
    │   └── test_pipeline.yaml
    └── responses/
        └── mock_response.json
```

---

## Documentation Structure

```text
docs/
├── index.md                 # Main navigation
├── guides/                  # How-to guides
│   ├── quick-start.md
│   ├── installation.md
│   ├── configuration.md
│   ├── yaml-pipelines.md
│   ├── parallel-execution.md
│   ├── cost-management.md
│   ├── troubleshooting.md
│   ├── faq.md
│   └── contributing.md
├── reference/               # Reference documentation
│   ├── models.md
│   ├── cli-commands.md
│   ├── architecture.md
│   └── package-structure.md
├── examples/                # Example code
│   ├── basic-examples.md
│   ├── advanced-pipelines.md
│   └── use-cases.md
└── api/                     # API documentation
    └── python-api.md
```

---

## Configuration Files

### setup.py

Package installation configuration.

```python
from setuptools import setup, find_packages

setup(
    name="video-ai-studio",
    version="1.0.18",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.0",
        "rich>=13.0.0",
        "PyYAML>=6.0",
        "fal-client>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-content-pipeline=packages.core.ai_content_pipeline.cli.main:cli",
            "aicp=packages.core.ai_content_pipeline.cli.main:cli",
        ],
    },
)
```

### requirements.txt

Full dependencies list.

```text
click>=8.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
httpx>=0.24.0
rich>=13.0.0
PyYAML>=6.0
fal-client>=0.4.0
google-cloud-aiplatform>=1.38.0
elevenlabs>=0.2.0
```

### .env

Environment configuration (not committed).

```env
FAL_KEY=your_fal_api_key
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
PROJECT_ID=your-gcp-project-id
```

---

## Import Examples

### Using Core Pipeline

```python
# Import main manager (note: double ai_content_pipeline in path)
from packages.core.ai_content_pipeline.ai_content_pipeline.pipeline.manager import AIPipelineManager

# Import configuration models
from packages.core.ai_content_pipeline.ai_content_pipeline.config.models import PipelineConfig, StepConfig

# Import utilities
from packages.core.ai_content_pipeline.ai_content_pipeline.utils.logging import setup_logging
```

### Using FAL Providers Directly

FAL packages use top-level underscore names (configured in setup.py):

```python
# FAL image-to-video
from fal_image_to_video import ImageToVideoClient
from fal_image_to_video.cli import main as i2v_cli

# FAL text-to-video
from fal_text_to_video import TextToVideoClient
from fal_text_to_video.cli import main as t2v_cli

# FAL video-to-video
from fal_video_to_video import VideoToVideoClient

# FAL avatar generation
from fal_avatar import AvatarClient
```

### Using Google Veo

```python
# Google Veo video generation
from packages.providers.google.veo.google_veo import VeoClient
```

### Using Services

```python
# Text-to-speech (ElevenLabs)
from packages.services.text_to_speech.text_to_speech import TextToSpeechClient

# Video tools
from packages.services.video_tools.video_tools import VideoAnalyzer, VideoProcessor
```

---

## Module Dependencies

```text
ai_content_pipeline
├── config (models, loader, validator)
├── utils (logging, cost, files)
├── providers (base → fal, google, elevenlabs)
├── pipeline (manager → builder → executor → parallel)
└── cli (main → commands)
```

The dependency flow is:
1. `config` and `utils` are foundational (no internal deps)
2. `providers` depend on `config` and `utils`
3. `pipeline` depends on `providers`, `config`, and `utils`
4. `cli` depends on `pipeline`
