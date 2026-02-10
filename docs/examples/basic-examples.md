# Basic Examples

Practical examples to help you get started with AI Content Generation Suite.

## Image Generation Examples

### Simple Image Generation

```bash
# Generate a single image
ai-content-pipeline generate-image \
  --text "a majestic mountain landscape at sunset" \
  --model flux_dev
```

### Multiple Image Styles

```bash
# Photorealistic
ai-content-pipeline generate-image \
  --text "professional headshot of a business executive" \
  --model imagen4

# Artistic
ai-content-pipeline generate-image \
  --text "impressionist painting of a garden" \
  --model flux_dev

# Fast prototype
ai-content-pipeline generate-image \
  --text "concept art for a video game character" \
  --model flux_schnell
```

### Aspect Ratios

```bash
# Landscape (16:9)
ai-content-pipeline generate-image \
  --text "panoramic view of a city skyline" \
  --aspect-ratio 16:9

# Portrait (9:16)
ai-content-pipeline generate-image \
  --text "fashion model portrait" \
  --aspect-ratio 9:16

# Square (1:1)
ai-content-pipeline generate-image \
  --text "product photo of a watch" \
  --aspect-ratio 1:1
```

---

## Video Generation Examples

### Text to Video (Quick)

```bash
# Budget-friendly option
ai-content-pipeline text-to-video \
  --text "ocean waves gently crashing on a beach" \
  --model hailuo_pro
```

### Text to Video (High Quality)

```bash
# Premium quality
ai-content-pipeline text-to-video \
  --text "cinematic shot of a spaceship landing" \
  --model sora_2_pro \
  --resolution 1080p
```

### Image to Video

```bash
# Animate an existing image
ai-content-pipeline image-to-video \
  --image landscape.png \
  --model kling_2_6_pro \
  --prompt "slow camera pan with gentle breeze"
```

### Full Text to Video Pipeline

```bash
# Generate image then video
ai-content-pipeline create-video \
  --text "a cat playing piano in a cozy room" \
  --image-model flux_dev \
  --video-model kling_2_6_pro \
  --duration 5
```

---

## YAML Pipeline Examples

### Basic Image Pipeline

Create `image-pipeline.yaml`:
```yaml
name: "Simple Image Generation"
description: "Generate an image from text"

steps:
  - name: "generate"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
      aspect_ratio: "16:9"
```

Run:
```bash
ai-content-pipeline run-chain \
  --config image-pipeline.yaml \
  --input "beautiful sunset over mountains"
```

### Text to Video Pipeline

Create `video-pipeline.yaml`:
```yaml
name: "Text to Video"
description: "Generate image then convert to video"

steps:
  - name: "image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
      aspect_ratio: "16:9"

  - name: "video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "image"
    params:
      duration: 5
```

Run:
```bash
ai-content-pipeline run-chain \
  --config video-pipeline.yaml \
  --input "serene forest with morning mist"
```

### Batch Image Generation (Parallel)

Create `batch-images.yaml`:
```yaml
name: "Batch Images"
description: "Generate multiple images in parallel"

settings:
  parallel: true

steps:
  - type: "parallel_group"
    name: "batch"
    steps:
      - name: "image_1"
        type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "a red sports car"

      - name: "image_2"
        type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "a blue motorcycle"

      - name: "image_3"
        type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "a green bicycle"
```

Run:
```bash
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain \
  --config batch-images.yaml
```

---

## Python API Examples

### Basic Image Generation

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Generate single image
result = manager.generate_image(
    prompt="a futuristic city at night",
    model="flux_dev"
)

print(f"Image saved to: {result.output_path}")
print(f"Cost: ${result.cost:.4f}")
```

### Video Creation

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Create video from text
result = manager.create_video(
    prompt="dolphins swimming in crystal clear water",
    image_model="flux_dev",
    video_model="kling_2_6_pro",
    duration=5
)

print(f"Video saved to: {result.output_path}")
```

### Image Analysis

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Describe an image
result = manager.analyze_image(
    image_path="photo.png",
    model="gemini_detailed"
)

print(f"Description: {result.description}")

# Ask a question
result = manager.analyze_image(
    image_path="photo.png",
    model="gemini_qa",
    question="What colors are prominent in this image?"
)

print(f"Answer: {result.description}")
```

### Running Pipelines Programmatically

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# From YAML file
results = manager.run_pipeline(
    config="pipeline.yaml",
    input_text="beautiful landscape"
)

for result in results:
    print(f"Step: {result.step_name}, Output: {result.output}")

# From dictionary
results = manager.run_pipeline(
    config={
        "name": "Quick Pipeline",
        "steps": [
            {
                "name": "image",
                "type": "text_to_image",
                "model": "flux_schnell",
                "params": {"prompt": "{{input}}"}
            }
        ]
    },
    input_text="sunset beach"
)
```

### Cost Estimation

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Estimate before running
estimate = manager.estimate_cost("pipeline.yaml")

print(f"Estimated total cost: ${estimate.total:.2f}")
for step, cost in estimate.breakdown.items():
    print(f"  {step}: ${cost:.4f}")

# Decide whether to proceed
if estimate.total < 1.00:
    results = manager.run_pipeline("pipeline.yaml")
else:
    print("Cost too high, aborting")
```

---

## Practical Use Cases

### Social Media Content

Generate content for Instagram/TikTok:

```yaml
name: "Social Media Content"
steps:
  - name: "image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
      aspect_ratio: "9:16"  # Portrait for stories

  - name: "video"
    type: "image_to_video"
    model: "hailuo"
    input_from: "image"
    params:
      duration: 6
```

### Product Visualization

Create product mockups:

```bash
ai-content-pipeline generate-image \
  --text "minimalist product photo of a smartphone on white background, studio lighting" \
  --model imagen4 \
  --aspect-ratio 1:1
```

### Marketing Video

```yaml
name: "Marketing Video"
steps:
  - name: "scene"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}, cinematic lighting, 4k quality"

  - name: "animation"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "scene"
    params:
      duration: 8
      prompt: "smooth camera movement"
```

### Content Localization

Generate multiple versions:

```yaml
name: "Multi-Language Content"
settings:
  parallel: true

steps:
  - type: "parallel_group"
    steps:
      - name: "english_narration"
        type: "text_to_speech"
        model: "elevenlabs"
        params:
          text: "Welcome to our product"
          voice: "Rachel"

      - name: "product_image"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "professional product showcase"
```

---

## Testing Without API Costs

Use mock mode to test configurations:

```bash
# Test image generation
ai-content-pipeline generate-image --text "test" --mock

# Test pipeline
ai-content-pipeline run-chain --config pipeline.yaml --dry-run

# Estimate costs
ai-content-pipeline estimate-cost --config pipeline.yaml
```

---

## Tips and Best Practices

### Prompting Tips

1. **Be specific**: "golden retriever puppy playing in autumn leaves" > "dog"
2. **Include style**: "oil painting style", "photorealistic", "anime style"
3. **Specify lighting**: "soft natural light", "dramatic shadows"
4. **Add quality markers**: "4k", "highly detailed", "professional"

### Cost Optimization

1. Use `flux_schnell` for testing ($0.001/image)
2. Use `hailuo_pro` for budget videos ($0.08/video)
3. Always estimate costs before large batches
4. Use parallel processing to save time (not money)

### Output Management

```bash
# Specify custom output directory
ai-content-pipeline generate-image \
  --text "test" \
  --output my-outputs/image.png

# Use timestamps for organization
ai-content-pipeline run-chain \
  --config pipeline.yaml \
  --output-dir "output/$(date +%Y%m%d)"
```
