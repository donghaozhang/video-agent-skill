# Python API Reference

Complete reference for using the AI Content Generation Suite programmatically.

## Quick Start

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

# Initialize
manager = AIPipelineManager()

# Generate image
result = manager.generate_image(
    prompt="a beautiful sunset",
    model="flux_dev"
)
print(f"Image saved to: {result.output_path}")
```

---

## AIPipelineManager

Main class for all pipeline operations.

### Initialization

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager(
    output_dir="output",      # Output directory
    parallel=False,           # Enable parallel processing
    log_level="INFO"          # Logging level
)
```

### Methods

#### generate_image()

Generate an image from text.

```python
result = manager.generate_image(
    prompt: str,              # Text prompt (required)
    model: str = "flux_dev",  # Model to use
    width: int = 1024,        # Image width
    height: int = 1024,       # Image height
    aspect_ratio: str = None, # Alternative to width/height
    seed: int = None,         # Random seed
    output_path: str = None   # Custom output path
)
```

**Returns:** `GenerationResult`

**Example:**
```python
result = manager.generate_image(
    prompt="epic dragon in flight",
    model="flux_dev",
    aspect_ratio="16:9"
)
print(f"Image: {result.output_path}")
print(f"Cost: ${result.cost:.4f}")
```

---

#### create_video()

Create video from text (image + video generation).

```python
result = manager.create_video(
    prompt: str,                      # Text prompt (required)
    image_model: str = "flux_dev",    # Image model
    video_model: str = "auto",        # Video model
    duration: int = 5,                # Video duration
    output_path: str = None           # Custom output path
)
```

**Returns:** `GenerationResult`

**Example:**
```python
result = manager.create_video(
    prompt="serene mountain lake",
    video_model="kling_2_6_pro",
    duration=8
)
```

---

#### image_to_video()

Convert existing image to video.

```python
result = manager.image_to_video(
    image_path: str,                  # Input image (required)
    model: str = "kling_2_6_pro",     # Video model
    prompt: str = None,               # Motion description
    duration: int = 5,                # Video duration
    output_path: str = None           # Custom output path
)
```

**Returns:** `GenerationResult`

**Example:**
```python
result = manager.image_to_video(
    image_path="photo.png",
    model="sora_2",
    prompt="gentle camera pan",
    duration=8
)
```

---

#### text_to_video()

Generate video directly from text.

```python
result = manager.text_to_video(
    prompt: str,                  # Text prompt (required)
    model: str = "hailuo_pro",    # Video model
    duration: int = 6,            # Video duration
    resolution: str = "720p",     # Resolution
    output_path: str = None       # Custom output path
)
```

**Returns:** `GenerationResult`

---

#### analyze_image()

Analyze image with AI.

```python
result = manager.analyze_image(
    image_path: str,                  # Input image (required)
    model: str = "gemini_describe",   # Analysis model
    question: str = None              # Question for QA model
)
```

**Returns:** `AnalysisResult`

**Example:**
```python
result = manager.analyze_image(
    image_path="photo.png",
    model="gemini_qa",
    question="What objects are visible?"
)
print(result.description)
```

---

#### text_to_speech()

Convert text to speech.

```python
result = manager.text_to_speech(
    text: str,                    # Text to convert (required)
    model: str = "elevenlabs",    # TTS model
    voice: str = "Rachel",        # Voice name
    output_path: str = None       # Custom output path
)
```

**Returns:** `GenerationResult`

---

#### run_pipeline()

Execute a complete pipeline from configuration.

```python
results = manager.run_pipeline(
    config: Union[str, dict],     # YAML path or config dict
    input_text: str = None,       # Input for {{input}} variable
    parallel: bool = False        # Enable parallel execution
)
```

**Returns:** `List[StepResult]`

**Example:**
```python
# From YAML file
results = manager.run_pipeline(
    config="pipeline.yaml",
    input_text="beautiful landscape"
)

# From dict
results = manager.run_pipeline(
    config={
        "name": "Quick Pipeline",
        "steps": [
            {
                "type": "text_to_image",
                "model": "flux_schnell",
                "params": {"prompt": "{{input}}"}
            }
        ]
    },
    input_text="ocean sunset"
)
```

---

#### estimate_cost()

Estimate pipeline cost before execution.

```python
estimate = manager.estimate_cost(
    config: Union[str, dict]      # YAML path or config dict
)
```

**Returns:** `CostEstimate`

**Example:**
```python
estimate = manager.estimate_cost("pipeline.yaml")
print(f"Estimated cost: ${estimate.total:.2f}")
print(f"Steps: {estimate.breakdown}")
```

---

#### list_models()

Get available models.

```python
models = manager.list_models(
    category: str = None,     # Filter by category
    provider: str = None      # Filter by provider
)
```

**Returns:** `List[ModelInfo]`

---

## Data Classes

### GenerationResult

```python
@dataclass
class GenerationResult:
    success: bool           # Whether generation succeeded
    output_path: str        # Path to output file
    model: str              # Model used
    cost: float             # Cost in USD
    duration: float         # Time taken in seconds
    metadata: dict          # Additional metadata
    error: str = None       # Error message if failed
```

### AnalysisResult

```python
@dataclass
class AnalysisResult:
    success: bool           # Whether analysis succeeded
    description: str        # Analysis result text
    model: str              # Model used
    cost: float             # Cost in USD
    metadata: dict          # Additional metadata
```

### StepResult

```python
@dataclass
class StepResult:
    step_name: str          # Name of the step
    step_type: str          # Type of step
    success: bool           # Whether step succeeded
    output: Any             # Step output
    cost: float             # Step cost
    duration: float         # Step duration
```

### CostEstimate

```python
@dataclass
class CostEstimate:
    total: float            # Total estimated cost
    breakdown: dict         # Per-step breakdown
    warnings: List[str]     # Any cost warnings
```

### ModelInfo

```python
@dataclass
class ModelInfo:
    name: str               # Model identifier
    display_name: str       # Human-readable name
    category: str           # Model category
    provider: str           # Provider name
    cost: float             # Cost per unit
    description: str        # Model description
```

---

## Error Handling

```python
from packages.core.ai_content_pipeline.exceptions import (
    PipelineError,
    ModelNotFoundError,
    APIError,
    ConfigurationError
)

try:
    result = manager.generate_image(prompt="test", model="invalid_model")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
except APIError as e:
    print(f"API error: {e}")
except PipelineError as e:
    print(f"Pipeline error: {e}")
```

### Exception Types

| Exception | Description |
|-----------|-------------|
| `PipelineError` | Base exception for all pipeline errors |
| `ModelNotFoundError` | Specified model doesn't exist |
| `APIError` | Error from external API |
| `ConfigurationError` | Invalid configuration |
| `CostLimitExceeded` | Operation exceeds cost limit |

---

## Advanced Usage

### Building Pipelines Programmatically

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Build pipeline using dict configuration
config = {
    "name": "Custom Pipeline",
    "steps": [
        {
            "name": "generate",
            "type": "text_to_image",
            "model": "flux_dev",
            "params": {"prompt": "{{input}}"}
        },
        {
            "name": "animate",
            "type": "image_to_video",
            "model": "kling_2_6_pro",
            "input_from": "generate",
            "params": {"duration": 5}
        }
    ]
}

results = manager.run_pipeline(config, input_text="sunset beach")
```

### Parallel Processing

```python
# Enable parallel for specific run
results = manager.run_pipeline(
    config="pipeline.yaml",
    parallel=True
)

# Or set globally
manager.parallel = True
```

### Event Callbacks

```python
def on_step_complete(step_result):
    print(f"Step {step_result.step_name} completed")

def on_error(error):
    print(f"Error: {error}")

manager.on_step_complete = on_step_complete
manager.on_error = on_error

results = manager.run_pipeline("pipeline.yaml")
```

### Cost Tracking

```python
# Track costs across multiple operations
with manager.track_costs() as tracker:
    manager.generate_image(prompt="test 1")
    manager.generate_image(prompt="test 2")
    manager.create_video(prompt="test 3")

print(f"Total cost: ${tracker.total:.2f}")
print(f"Operations: {tracker.count}")
```

---

## Integration Examples

### Flask Web App

```python
from flask import Flask, request, jsonify
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

app = Flask(__name__)
manager = AIPipelineManager()

@app.route('/generate-image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt')
    result = manager.generate_image(prompt=prompt)
    return jsonify({
        'success': result.success,
        'path': result.output_path,
        'cost': result.cost
    })
```

### Concurrent Usage with Threading

```python
from concurrent.futures import ThreadPoolExecutor
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

def generate(prompt):
    return manager.generate_image(prompt=prompt)

# Parallel generation using threads
prompts = ["cat", "dog", "bird"]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(generate, prompts))

for result in results:
    print(result.output_path)
```

> **Note:** For built-in parallel execution, use YAML pipelines with `parallel_group` or enable `PIPELINE_PARALLEL_ENABLED=true`.
