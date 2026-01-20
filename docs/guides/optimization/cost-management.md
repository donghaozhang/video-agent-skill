# Cost Management Guide

Understand, estimate, and control costs when using AI Content Generation Suite.

## Cost Overview

### Pricing by Category

| Category | Cost Range | Notes |
|----------|------------|-------|
| Text-to-Image | $0.001 - $0.08 | Per image |
| Image-to-Image | $0.015 - $0.05 | Per transformation |
| Image-to-Video | $0.25 - $3.60 | Per video |
| Text-to-Video | $0.08 - $6.00 | Per video |
| Image Analysis | $0.001 - $0.002 | Per analysis |
| Text-to-Speech | $0.03 - $0.08 | Per request |
| Video Processing | $0.05 - $1.50 | Per operation |

### Model-Specific Pricing

#### Text-to-Image

| Model | Cost/Image | Best For |
|-------|------------|----------|
| `flux_schnell` | $0.001 | Testing, prototyping |
| `nano_banana_pro` | $0.002 | Fast, quality balance |
| `seedream_v3` | $0.002 | Artistic styles |
| `flux_dev` | $0.003 | High quality |
| `gpt_image_1_5` | $0.003 | Complex prompts |
| `imagen4` | $0.004 | Photorealistic |
| `gen4` | $0.08 | Premium, multi-reference |

#### Image-to-Video

| Model | Cost/Video | Duration | Quality |
|-------|------------|----------|---------|
| `kling_2_1` | $0.25-0.50 | 5s | Good |
| `hailuo` | $0.30-0.50 | 6s | Good |
| `veo_3_1_fast` | $0.40-0.80 | 5-8s | Great + Audio |
| `kling_2_6_pro` | $0.50-1.00 | 5-10s | Excellent |
| `sora_2` | $0.40-1.20 | 4-12s | Excellent |
| `sora_2_pro` | $1.20-3.60 | 4-20s | Premium |

#### Text-to-Video

| Model | Cost/Video | Duration | Notes |
|-------|------------|----------|-------|
| `hailuo_pro` | $0.08 | 6s fixed | Best budget |
| `kling_2_6_pro` | $0.35-1.40 | 5-10s | With audio |
| `sora_2` | $0.40-1.20 | 4-12s | High quality |
| `sora_2_pro` | $1.20-6.00 | 4-20s | Premium |

## Cost Estimation

### CLI Estimation

Before running a pipeline:

```bash
# Estimate cost for pipeline
ai-content-pipeline estimate-cost --config pipeline.yaml
```

Output:
```
Pipeline Cost Estimate
═══════════════════════════════════════════
Step                    Model           Cost
───────────────────────────────────────────
generate_image         flux_dev        $0.003
create_video           kling_2_6_pro   $0.500
add_narration          elevenlabs      $0.050
───────────────────────────────────────────
Total Estimated Cost:                  $0.553
═══════════════════════════════════════════
```

### Python API Estimation

```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()

# Estimate before running
estimate = manager.estimate_cost("pipeline.yaml")

print(f"Total estimated cost: ${estimate.total:.2f}")
print(f"Breakdown:")
for step, cost in estimate.breakdown.items():
    print(f"  {step}: ${cost:.4f}")

# Decide whether to proceed
if estimate.total < 1.00:
    results = manager.run_pipeline("pipeline.yaml")
else:
    print("Cost exceeds budget, aborting")
```

## Cost Control

### Setting Cost Limits

#### YAML Configuration

```yaml
settings:
  cost_management:
    max_cost_per_run: 10.00    # Maximum cost in USD
    warn_threshold: 5.00       # Warn before expensive operations
    require_confirmation: true  # Prompt before execution
```

#### Python API

```python
manager = AIPipelineManager(
    max_cost=10.00,
    cost_warning_threshold=5.00
)
```

### Cost Tracking

Track costs across sessions:

```python
# Track costs
with manager.track_costs() as tracker:
    manager.generate_image(prompt="test 1")
    manager.generate_image(prompt="test 2")
    manager.create_video(prompt="test 3")

print(f"Session cost: ${tracker.total:.2f}")
print(f"Operations: {tracker.count}")

# Export cost report
tracker.export("cost_report.json")
```

## Budget-Conscious Strategies

### 1. Use Mock Mode for Testing

Test configuration without API calls:

```bash
# Validate configuration (FREE)
ai-content-pipeline generate-image --text "test" --mock
ai-content-pipeline run-chain --config pipeline.yaml --dry-run
```

### 2. Start with Cheap Models

Development workflow:
1. Prototype with `flux_schnell` ($0.001)
2. Test with `flux_dev` ($0.003)
3. Final production with `imagen4` ($0.004)

```yaml
# Development config
steps:
  - type: "text_to_image"
    model: "flux_schnell"  # Cheap for testing

# Production config
steps:
  - type: "text_to_image"
    model: "imagen4"  # Quality for production
```

### 3. Use Budget Video Models

For video prototyping:

```yaml
# Budget option ($0.08/video)
- type: "text_to_video"
  model: "hailuo_pro"

# Quality option ($0.50+/video)
- type: "text_to_video"
  model: "kling_2_6_pro"
```

### 4. Batch Similar Operations

Run similar operations together to optimize:

```yaml
settings:
  parallel: true

steps:
  - type: "parallel_group"
    steps:
      # Generate all images at once
      - type: "text_to_image"
        params: { prompt: "scene 1" }
      - type: "text_to_image"
        params: { prompt: "scene 2" }
      - type: "text_to_image"
        params: { prompt: "scene 3" }
```

### 5. Cache Results

Don't regenerate existing content:

```python
import os

output_path = "output/sunset.png"

if os.path.exists(output_path):
    print("Using cached image")
else:
    manager.generate_image(prompt="sunset", output_path=output_path)
```

## Cost Comparison Examples

### Scenario 1: Single Video Creation

**Budget Approach:**
```yaml
steps:
  - type: "text_to_image"
    model: "flux_schnell"      # $0.001
  - type: "image_to_video"
    model: "hailuo"            # $0.30
# Total: ~$0.30
```

**Quality Approach:**
```yaml
steps:
  - type: "text_to_image"
    model: "flux_dev"          # $0.003
  - type: "image_to_video"
    model: "kling_2_6_pro"     # $0.50
# Total: ~$0.50
```

**Premium Approach:**
```yaml
steps:
  - type: "text_to_image"
    model: "imagen4"           # $0.004
  - type: "image_to_video"
    model: "sora_2_pro"        # $1.20
# Total: ~$1.20
```

### Scenario 2: Batch Image Generation (10 images)

**Budget:**
```yaml
# flux_schnell x 10 = $0.01
```

**Quality:**
```yaml
# flux_dev x 10 = $0.03
```

**Premium:**
```yaml
# imagen4 x 10 = $0.04
```

### Scenario 3: Content Production Pipeline

```yaml
steps:
  - type: "text_to_image"      # $0.003
    model: "flux_dev"
  - type: "image_to_video"     # $0.50
    model: "kling_2_6_pro"
  - type: "text_to_speech"     # $0.05
    model: "elevenlabs"
# Total: ~$0.55 per content piece
```

## Cost Optimization Tips

### Do's

1. **Estimate before running** - Always check costs first
2. **Use mock mode** - Test configurations for free
3. **Start cheap** - Prototype with budget models
4. **Batch operations** - Process similar tasks together
5. **Cache results** - Don't regenerate existing content
6. **Set limits** - Configure max_cost to prevent surprises

### Don'ts

1. **Don't use premium models for testing** - `sora_2_pro` is $6+/video
2. **Don't regenerate** - Cache and reuse content
3. **Don't skip estimation** - Always estimate first
4. **Don't ignore warnings** - Cost warnings exist for a reason

## Monitoring Costs

### Dashboard Links

- **FAL AI**: [fal.ai/dashboard](https://fal.ai/dashboard)
- **Google Cloud**: [console.cloud.google.com/billing](https://console.cloud.google.com/billing)
- **ElevenLabs**: [elevenlabs.io/app/usage](https://elevenlabs.io/app/usage)
- **OpenRouter**: [openrouter.ai/activity](https://openrouter.ai/activity)

### Cost Reports

Generate cost reports:

```python
# After running operations
report = manager.get_cost_report()
report.save("monthly_costs.json")
report.save("monthly_costs.csv")
```

### Alerts

Set up cost alerts in provider dashboards to get notified when spending exceeds thresholds.

## Free Tier Usage

Some providers offer free tiers:

| Provider | Free Tier |
|----------|-----------|
| FAL AI | Limited free credits for new accounts |
| Google Gemini | Free tier for analysis |
| ElevenLabs | 10,000 characters/month free |

Check each provider's current free tier offerings.

---

[Back to Documentation Index](../../index.md)
