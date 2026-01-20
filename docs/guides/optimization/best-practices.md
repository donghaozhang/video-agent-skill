# Best Practices Guide

Recommended patterns and practices for using AI Content Generation Suite effectively.

## Project Organization

### Directory Structure

Organize your AI content projects:

```
my-project/
├── .env                    # API keys (never commit)
├── .gitignore              # Ignore .env, output/
├── pipelines/              # YAML configurations
│   ├── production.yaml
│   ├── development.yaml
│   └── templates/
│       ├── video-pipeline.yaml
│       └── image-pipeline.yaml
├── output/                 # Generated content
│   ├── images/
│   ├── videos/
│   └── audio/
├── scripts/                # Automation scripts
│   └── batch_generate.py
└── README.md
```

### Configuration Management

**Separate configurations by environment:**

```yaml
# pipelines/development.yaml
name: "Dev Pipeline"
settings:
  parallel: false
  log_level: "DEBUG"
steps:
  - type: "text_to_image"
    model: "flux_schnell"  # Cheap for testing
```

```yaml
# pipelines/production.yaml
name: "Production Pipeline"
settings:
  parallel: true
  log_level: "INFO"
steps:
  - type: "text_to_image"
    model: "flux_dev"  # Higher quality
```

---

## Prompting Best Practices

### Be Specific

```bash
# Vague (poor results)
ai-content-pipeline generate-image --text "a dog"

# Specific (better results)
ai-content-pipeline generate-image --text "golden retriever puppy playing in autumn leaves, natural lighting, shallow depth of field, professional photography"
```

### Use Style Descriptors

Include style and quality keywords:

```yaml
params:
  prompt: "{{input}}, professional photography, 4k resolution, sharp focus, natural lighting"
```

**Common style descriptors:**
- Quality: "4k", "8k", "high resolution", "detailed"
- Lighting: "natural lighting", "studio lighting", "golden hour", "dramatic shadows"
- Style: "photorealistic", "cinematic", "artistic", "minimalist"
- Composition: "rule of thirds", "centered", "wide angle", "close-up"

### Structure Complex Prompts

For complex scenes, structure your prompt:

```
[Subject], [Action], [Environment], [Lighting], [Style], [Quality]
```

Example:
```
"A young woman reading a book, sitting in a cozy cafe, warm afternoon sunlight through windows, film photography style, 35mm, sharp focus"
```

### Negative Prompts (When Supported)

Some models support negative prompts:

```yaml
params:
  prompt: "beautiful landscape, mountains, clear sky"
  negative_prompt: "blurry, low quality, distorted"
```

---

## Cost Optimization

### Development vs Production

| Phase | Model Choice | Why |
|-------|--------------|-----|
| Prototyping | `flux_schnell` | $0.001, fast |
| Testing | `flux_dev` | $0.003, quality check |
| Production | `imagen4` | $0.004, best quality |

### Batch Efficiently

```yaml
# Inefficient: Multiple pipeline runs
# ai-content-pipeline run-chain --config single.yaml  (repeat 10 times)

# Efficient: Batch in parallel
settings:
  parallel: true

steps:
  - type: "parallel_group"
    steps:
      - type: "text_to_image"
        params: { prompt: "scene 1" }
      - type: "text_to_image"
        params: { prompt: "scene 2" }
      # ... up to 10 images at once
```

### Cache Results

Don't regenerate existing content:

```python
import os
from pathlib import Path

def generate_if_missing(prompt: str, output_name: str):
    output_path = Path(f"output/{output_name}.png")

    if output_path.exists():
        print(f"Using cached: {output_path}")
        return output_path

    result = manager.generate_image(
        prompt=prompt,
        output_path=str(output_path)
    )
    return result.output_path
```

### Use Appropriate Resolution

Don't generate larger than needed:

```yaml
# Social media post (1080x1080 is enough)
params:
  width: 1080
  height: 1080

# Print material (need higher resolution)
params:
  width: 2048
  height: 2048
```

---

## Pipeline Design

### Keep Pipelines Focused

One pipeline per purpose:

```yaml
# Good: Single purpose
name: "Product Image Generator"
steps:
  - type: "text_to_image"
    model: "imagen4"
    params:
      prompt: "{{input}}, product photography, white background"
```

```yaml
# Avoid: Multi-purpose pipeline
name: "Do Everything"
steps:
  - type: "text_to_image"
  - type: "image_to_video"
  - type: "text_to_speech"
  - type: "analyze_image"
  # Too complex, hard to debug
```

### Use Meaningful Step Names

```yaml
# Good
steps:
  - name: "hero_image"
  - name: "thumbnail_variation"
  - name: "social_media_crop"

# Bad
steps:
  - name: "step1"
  - name: "step2"
  - name: "step3"
```

### Document Your Pipelines

```yaml
name: "Marketing Video Pipeline"
description: |
  Creates marketing videos from product descriptions.

  Input: Product description text
  Output:
    - Product image (16:9)
    - 8-second video with motion
    - Voice-over narration

  Estimated cost: $0.55 per run

steps:
  # ...
```

---

## Error Handling

### Validate Before Running

```bash
# Always dry-run first
ai-content-pipeline run-chain --config pipeline.yaml --dry-run

# Estimate costs
ai-content-pipeline estimate-cost --config pipeline.yaml
```

### Handle Failures Gracefully

```python
from packages.core.ai_content_pipeline.exceptions import APIError, RateLimitError

def safe_generate(prompt: str, retries: int = 3):
    for attempt in range(retries):
        try:
            return manager.generate_image(prompt=prompt)
        except RateLimitError:
            print(f"Rate limited, waiting... (attempt {attempt + 1})")
            time.sleep(30)
        except APIError as e:
            print(f"API error: {e}")
            if attempt == retries - 1:
                raise
    return None
```

### Log Operations

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_with_logging(prompt: str):
    logger.info(f"Starting generation: {prompt[:50]}...")
    try:
        result = manager.generate_image(prompt=prompt)
        logger.info(f"Success: {result.output_path}")
        return result
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise
```

---

## Quality Assurance

### Review Generated Content

Always review AI-generated content before use:
- Check for artifacts or distortions
- Verify prompt adherence
- Ensure brand consistency

### Use Seeds for Reproducibility

```yaml
params:
  prompt: "product photo"
  seed: 42  # Same seed = same result
```

### A/B Test Variations

```yaml
steps:
  - type: "parallel_group"
    steps:
      - name: "variation_a"
        params:
          prompt: "{{input}}, style A"
          seed: 1001
      - name: "variation_b"
        params:
          prompt: "{{input}}, style B"
          seed: 1002
```

---

## Performance

### Enable Parallel When Possible

```bash
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml
```

### Choose Appropriate Workers

```yaml
settings:
  parallel: true
  max_workers: 4  # Balance between speed and rate limits
```

### Use Fast Models for Previews

```yaml
# Quick preview
- type: "text_to_image"
  model: "flux_schnell"  # Fast

# Final version
- type: "text_to_image"
  model: "flux_dev"  # Quality
```

---

## Integration Patterns

### Webhook-Driven Generation

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json

    # Validate input
    if not data.get('prompt'):
        return {'error': 'Prompt required'}, 400

    # Generate with timeout
    try:
        result = manager.generate_image(
            prompt=data['prompt'],
            model=data.get('model', 'flux_dev')
        )
        return {'success': True, 'path': result.output_path}
    except Exception as e:
        return {'error': str(e)}, 500
```

### Queue-Based Processing

```python
from queue import Queue
from threading import Thread

generation_queue = Queue()

def worker():
    while True:
        task = generation_queue.get()
        try:
            manager.generate_image(**task)
        except Exception as e:
            print(f"Task failed: {e}")
        generation_queue.task_done()

# Start worker threads
for _ in range(4):
    Thread(target=worker, daemon=True).start()

# Add tasks
generation_queue.put({'prompt': 'cat', 'model': 'flux_schnell'})
generation_queue.put({'prompt': 'dog', 'model': 'flux_schnell'})

# Wait for completion
generation_queue.join()
```

---

## Checklist

### Before Starting a Project

- [ ] API keys configured in `.env`
- [ ] `.env` added to `.gitignore`
- [ ] Output directory created
- [ ] Test with mock mode works

### Before Running Production Pipelines

- [ ] Dry-run validates successfully
- [ ] Cost estimate is acceptable
- [ ] Prompts are well-crafted
- [ ] Error handling is in place

### After Generation

- [ ] Review output quality
- [ ] Verify correct files generated
- [ ] Check costs match estimate
- [ ] Archive or organize outputs

---

[Back to Documentation Index](../../index.md)
