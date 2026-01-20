# Architecture Overview

Understanding the structure and design of the AI Content Generation Suite.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Interface                            │
│                    (ai-content-pipeline / aicp)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Pipeline Manager                            │
│              (Orchestration & Execution Engine)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│   Providers   │       │   Services    │       │    Utilities  │
│               │       │               │       │               │
│  • FAL AI     │       │  • TTS        │       │  • Config     │
│  • Google     │       │  • Video      │       │  • Logging    │
│  • Replicate  │       │    Tools      │       │  • Validation │
└───────────────┘       └───────────────┘       └───────────────┘
        │                       │
        ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        External APIs                             │
│         (FAL AI, Google Cloud, ElevenLabs, OpenRouter)          │
└─────────────────────────────────────────────────────────────────┘
```

## Package Structure

```
ai-content-pipeline/
├── packages/
│   ├── core/
│   │   └── ai_content_pipeline/      # Main pipeline package
│   │       ├── pipeline/             # Pipeline execution engine
│   │       │   ├── manager.py        # Main orchestration class
│   │       │   ├── builder.py        # Pipeline builder
│   │       │   ├── executor.py       # Step execution
│   │       │   └── parallel.py       # Parallel processing
│   │       ├── config/               # Configuration handling
│   │       │   ├── loader.py         # YAML/JSON loading
│   │       │   ├── validator.py      # Schema validation
│   │       │   └── models.py         # Pydantic models
│   │       ├── providers/            # Provider integrations
│   │       │   ├── base.py           # Base provider class
│   │       │   ├── fal.py            # FAL AI provider
│   │       │   ├── google.py         # Google provider
│   │       │   └── elevenlabs.py     # ElevenLabs provider
│   │       ├── cli/                  # Command-line interface
│   │       │   ├── main.py           # CLI entry point
│   │       │   └── commands/         # Individual commands
│   │       └── utils/                # Utilities
│   │           ├── logging.py        # Logging setup
│   │           ├── cost.py           # Cost estimation
│   │           └── files.py          # File handling
│   │
│   ├── providers/                    # Individual provider packages
│   │   ├── google/
│   │   │   └── veo/                  # Google Veo integration
│   │   └── fal/
│   │       ├── text-to-image/        # FAL text-to-image
│   │       ├── image-to-image/       # FAL image-to-image
│   │       ├── image-to-video/       # FAL image-to-video
│   │       ├── text-to-video/        # FAL text-to-video
│   │       ├── video-to-video/       # FAL video processing
│   │       └── avatar/               # FAL avatar generation
│   │
│   └── services/                     # Shared services
│       ├── text-to-speech/           # TTS integration
│       └── video-tools/              # Video utilities
│
├── docs/                             # Documentation
├── tests/                            # Test suites
├── input/                            # Input configurations
├── output/                           # Generated content
└── setup.py                          # Package installation
```

## Core Components

### 1. Pipeline Manager

The central orchestration component.

```python
class AIPipelineManager:
    """
    Responsibilities:
    - Load and validate configurations
    - Coordinate step execution
    - Manage provider connections
    - Handle errors and retries
    - Track costs and metrics
    """
```

**Key Methods:**
- `generate_image()` - Text-to-image generation
- `create_video()` - End-to-end video creation
- `run_pipeline()` - Execute YAML pipeline
- `estimate_cost()` - Cost estimation

### 2. Provider System

Abstraction layer for external APIs.

```python
class BaseProvider:
    """Base class for all providers."""

    def generate(self, params: dict) -> Result:
        raise NotImplementedError

    def estimate_cost(self, params: dict) -> float:
        raise NotImplementedError
```

**Implemented Providers:**
- `FALProvider` - FAL AI services
- `GoogleProvider` - Google Cloud/Gemini
- `ElevenLabsProvider` - Text-to-speech
- `OpenRouterProvider` - Alternative models

### 3. Configuration System

YAML/JSON configuration handling.

```python
class PipelineConfig:
    """
    Responsibilities:
    - Parse YAML/JSON configurations
    - Validate against schema
    - Resolve variable interpolation
    - Handle defaults
    """
```

### 4. Execution Engine

Step execution and workflow management.

```python
class StepExecutor:
    """
    Responsibilities:
    - Execute individual steps
    - Handle step dependencies
    - Manage parallel execution
    - Collect results
    """
```

## Data Flow

### Simple Generation Flow

```
User Request → CLI Parser → Pipeline Manager → Provider → External API
                                    ↓
                              Result Handler
                                    ↓
                            Output Manager → File System
```

### Pipeline Execution Flow

```
YAML Config → Config Loader → Validator → Pipeline Builder
                                               ↓
                                    Step Execution Loop
                                    ┌─────────────────┐
                                    │ Step 1: Execute │
                                    │      ↓          │
                                    │ Step 2: Execute │
                                    │      ↓          │
                                    │ Step N: Execute │
                                    └─────────────────┘
                                           ↓
                                    Result Aggregation
                                           ↓
                                    Output Generation
```

### Parallel Execution Flow

```
Pipeline Config
      ↓
Dependency Analysis
      ↓
┌─────────────────────────────────────┐
│         Parallel Group              │
│  ┌─────┐  ┌─────┐  ┌─────┐         │
│  │Step1│  │Step2│  │Step3│         │
│  └──┬──┘  └──┬──┘  └──┬──┘         │
│     │        │        │             │
│     └────────┼────────┘             │
│              ↓                      │
│         Sync Point                  │
└─────────────────────────────────────┘
              ↓
      Next Sequential Step
```

## Design Principles

### 1. Modularity

Each component is self-contained and can be used independently:

```python
# Use just the FAL provider
from packages.providers.fal.text_to_image import FALTextToImage

generator = FALTextToImage()
result = generator.generate(prompt="test")

# Use just the pipeline manager
from packages.core.ai_content_pipeline import AIPipelineManager

manager = AIPipelineManager()
```

### 2. Extensibility

Easy to add new providers and models:

```python
class CustomProvider(BaseProvider):
    def generate(self, params):
        # Custom implementation
        pass

# Register with pipeline manager
manager.register_provider("custom", CustomProvider())
```

### 3. Type Safety

Full type hints with Pydantic validation:

```python
from pydantic import BaseModel

class GenerationParams(BaseModel):
    prompt: str
    model: str = "flux_dev"
    width: int = 1024
    height: int = 1024
```

### 4. Cost Awareness

Built-in cost tracking at every level:

```python
class CostTracker:
    def estimate(self, operation):
        return self.cost_tables[operation]

    def track(self, operation, actual_cost):
        self.history.append((operation, actual_cost))
```

## Error Handling Strategy

### Retry Logic

```python
@retry(max_attempts=3, exceptions=(APIError,))
def api_call(self, params):
    return self.provider.generate(params)
```

### Error Propagation

```
API Error → Provider Exception → Pipeline Error → User-Friendly Message
```

### Error Recovery

```python
try:
    result = step.execute()
except RecoverableError:
    result = step.execute_fallback()
except FatalError:
    pipeline.abort()
```

## Performance Optimizations

### 1. Connection Pooling

Reuse HTTP connections for efficiency:

```python
class ProviderClient:
    def __init__(self):
        self.session = httpx.Client(
            timeout=30,
            limits=httpx.Limits(max_connections=10)
        )
```

### 2. Parallel Execution

Thread-based parallelism for I/O-bound operations:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(step.execute) for step in parallel_steps]
    results = [f.result() for f in futures]
```

### 3. Lazy Loading

Load providers only when needed:

```python
@property
def fal_provider(self):
    if self._fal_provider is None:
        self._fal_provider = FALProvider()
    return self._fal_provider
```

## Security Considerations

### API Key Management

- Keys stored in environment variables or `.env` files
- Never logged or exposed in error messages
- Validated before use

### Input Validation

- All user inputs sanitized
- File paths validated
- Prompt injection protection

### Output Security

- Generated files saved with safe permissions
- No executable content in outputs

## Testing Architecture

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_manager.py
│   ├── test_providers.py
│   └── test_config.py
├── integration/          # Integration tests
│   ├── test_pipelines.py
│   └── test_api_calls.py
└── fixtures/             # Test data and mocks
    ├── configs/
    └── responses/
```

---

[Back to Documentation Index](../index.md)
