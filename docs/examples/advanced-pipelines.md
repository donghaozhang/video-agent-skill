# Advanced Pipeline Examples

Complex, production-ready pipeline configurations for various use cases.

## Multi-Stage Video Production

Complete video production with image, video, and audio.

```yaml
name: "Video Production Pipeline"
description: "Generate professional video content with narration"
version: "1.0"

settings:
  parallel: true
  output_dir: "output/video_production"
  log_level: "INFO"

steps:
  # Stage 1: Generate base image
  - name: "hero_image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}, cinematic composition, dramatic lighting, 8k quality"
      aspect_ratio: "16:9"

  # Stage 2: Create variations and video in parallel
  - type: "parallel_group"
    name: "content_generation"
    steps:
      - name: "main_video"
        type: "image_to_video"
        model: "kling_2_6_pro"
        input_from: "hero_image"
        params:
          duration: 8
          prompt: "slow cinematic camera movement, atmospheric"

      - name: "thumbnail"
        type: "image_to_image"
        model: "photon_flash"
        input_from: "hero_image"
        params:
          prompt: "add vibrant colors and text overlay space"
          strength: 0.3

      - name: "narration"
        type: "text_to_speech"
        model: "elevenlabs"
        params:
          text: "{{input}}"
          voice: "Josh"
          stability: 0.6

  # Stage 3: Analyze results
  - name: "video_analysis"
    type: "analyze_image"
    model: "gemini_detailed"
    input_from: "hero_image"
```

---

## A/B Testing Pipeline

Generate multiple versions for comparison testing.

```yaml
name: "A/B Testing Pipeline"
description: "Generate variations for A/B testing"

settings:
  parallel: true

steps:
  # Generate multiple style variations
  - type: "parallel_group"
    name: "style_variations"
    steps:
      - name: "version_a"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "{{input}}, professional, clean, minimal"
          seed: 1001

      - name: "version_b"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "{{input}}, vibrant, energetic, bold colors"
          seed: 1002

      - name: "version_c"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "{{input}}, warm, friendly, inviting"
          seed: 1003

  # Create videos for each version
  - type: "parallel_group"
    name: "video_versions"
    steps:
      - name: "video_a"
        type: "image_to_video"
        model: "hailuo"
        input_from: "version_a"

      - name: "video_b"
        type: "image_to_video"
        model: "hailuo"
        input_from: "version_b"

      - name: "video_c"
        type: "image_to_video"
        model: "hailuo"
        input_from: "version_c"
```

---

## Multi-Platform Content Pipeline

Generate content optimized for different platforms.

```yaml
name: "Multi-Platform Content"
description: "Create content for various social platforms"

settings:
  parallel: true
  output_dir: "output/multi_platform"

steps:
  # Base high-quality image
  - name: "master_image"
    type: "text_to_image"
    model: "imagen4"
    params:
      prompt: "{{input}}, professional photography, high quality"
      width: 2048
      height: 2048

  # Platform-specific versions in parallel
  - type: "parallel_group"
    name: "platform_versions"
    steps:
      # Instagram Square (1:1)
      - name: "instagram_square"
        type: "image_to_image"
        model: "photon_flash"
        input_from: "master_image"
        params:
          aspect_ratio: "1:1"
          prompt: "optimize for social media, vibrant"

      # Instagram Story (9:16)
      - name: "instagram_story"
        type: "image_to_image"
        model: "photon_flash"
        input_from: "master_image"
        params:
          aspect_ratio: "9:16"
          prompt: "optimize for mobile viewing"

      # YouTube Thumbnail (16:9)
      - name: "youtube_thumbnail"
        type: "image_to_image"
        model: "photon_flash"
        input_from: "master_image"
        params:
          aspect_ratio: "16:9"
          prompt: "eye-catching, thumbnail optimized"

      # Twitter/X Header (3:1)
      - name: "twitter_header"
        type: "image_to_image"
        model: "photon_flash"
        input_from: "master_image"
        params:
          width: 1500
          height: 500
          prompt: "banner format, centered composition"

  # Create short video for TikTok/Reels
  - name: "short_video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "instagram_story"
    params:
      duration: 5
      prompt: "dynamic motion, engaging"
```

---

## Model Comparison Pipeline

Compare outputs from different models.

```yaml
name: "Model Comparison"
description: "Compare same prompt across different models"

settings:
  parallel: true

steps:
  - type: "parallel_group"
    name: "image_models"
    steps:
      - name: "flux_dev_result"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "{{input}}"
          seed: 42

      - name: "flux_schnell_result"
        type: "text_to_image"
        model: "flux_schnell"
        params:
          prompt: "{{input}}"
          seed: 42

      - name: "imagen4_result"
        type: "text_to_image"
        model: "imagen4"
        params:
          prompt: "{{input}}"
          seed: 42

      - name: "seedream_result"
        type: "text_to_image"
        model: "seedream_v3"
        params:
          prompt: "{{input}}"
          seed: 42

  # Analyze each result
  - type: "parallel_group"
    name: "analyses"
    steps:
      - name: "flux_dev_analysis"
        type: "analyze_image"
        model: "gemini_detailed"
        input_from: "flux_dev_result"

      - name: "flux_schnell_analysis"
        type: "analyze_image"
        model: "gemini_detailed"
        input_from: "flux_schnell_result"

      - name: "imagen4_analysis"
        type: "analyze_image"
        model: "gemini_detailed"
        input_from: "imagen4_result"

      - name: "seedream_analysis"
        type: "analyze_image"
        model: "gemini_detailed"
        input_from: "seedream_result"
```

---

## Iterative Refinement Pipeline

Progressively refine content through multiple passes.

```yaml
name: "Iterative Refinement"
description: "Refine image through multiple enhancement passes"

steps:
  # Initial generation
  - name: "draft"
    type: "text_to_image"
    model: "flux_schnell"
    params:
      prompt: "{{input}}, rough concept"

  # First refinement
  - name: "refined_v1"
    type: "image_to_image"
    model: "flux_kontext"
    input_from: "draft"
    params:
      prompt: "enhance details, improve composition"
      strength: 0.5

  # Second refinement
  - name: "refined_v2"
    type: "image_to_image"
    model: "photon_base"
    input_from: "refined_v1"
    params:
      prompt: "add professional lighting, polish details"
      strength: 0.4

  # Final upscale
  - name: "final"
    type: "image_to_image"
    model: "clarity_upscaler"
    input_from: "refined_v2"
```

---

## Storyboard Generator

Generate multiple scenes for a story.

```yaml
name: "Storyboard Generator"
description: "Create visual storyboard from scene descriptions"

settings:
  parallel: true

steps:
  # Generate all scenes in parallel
  - type: "parallel_group"
    name: "scenes"
    steps:
      - name: "scene_1_opening"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "Scene 1: {{input}} - establishing shot, wide angle, cinematic"
          aspect_ratio: "16:9"

      - name: "scene_2_action"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "Scene 2: {{input}} - action sequence, dynamic composition"
          aspect_ratio: "16:9"

      - name: "scene_3_dialogue"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "Scene 3: {{input}} - character close-up, emotional"
          aspect_ratio: "16:9"

      - name: "scene_4_climax"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "Scene 4: {{input}} - climactic moment, dramatic lighting"
          aspect_ratio: "16:9"

      - name: "scene_5_resolution"
        type: "text_to_image"
        model: "flux_dev"
        params:
          prompt: "Scene 5: {{input}} - resolution, peaceful, satisfying"
          aspect_ratio: "16:9"

  # Create animated versions
  - type: "parallel_group"
    name: "animations"
    steps:
      - name: "anim_1"
        type: "image_to_video"
        model: "hailuo"
        input_from: "scene_1_opening"
        params:
          duration: 4
          prompt: "slow establishing pan"

      - name: "anim_2"
        type: "image_to_video"
        model: "hailuo"
        input_from: "scene_2_action"
        params:
          duration: 4
          prompt: "fast dynamic movement"

      - name: "anim_3"
        type: "image_to_video"
        model: "hailuo"
        input_from: "scene_3_dialogue"
        params:
          duration: 4
          prompt: "subtle face movements"

      - name: "anim_4"
        type: "image_to_video"
        model: "hailuo"
        input_from: "scene_4_climax"
        params:
          duration: 4
          prompt: "intense dramatic motion"

      - name: "anim_5"
        type: "image_to_video"
        model: "hailuo"
        input_from: "scene_5_resolution"
        params:
          duration: 4
          prompt: "gentle calming motion"
```

---

## Conditional Pipeline

Pipeline with error handling and fallbacks.

```yaml
name: "Robust Pipeline"
description: "Pipeline with fallback handling"

settings:
  fail_fast: false  # Continue on errors

steps:
  # Primary attempt with premium model
  - name: "primary_image"
    type: "text_to_image"
    model: "imagen4"
    params:
      prompt: "{{input}}"
    on_error: "continue"  # Don't stop on failure

  # Fallback with reliable model
  - name: "fallback_image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"
    condition: "primary_image.failed"  # Only if primary failed

  # Video from whichever succeeded
  - name: "video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "primary_image OR fallback_image"
```

---

## Batch Processing Pipeline

Process multiple inputs efficiently.

```yaml
name: "Batch Processor"
description: "Process multiple prompts from file"

settings:
  parallel: true
  max_workers: 4
  input_file: "prompts.txt"  # One prompt per line

steps:
  - type: "batch"
    name: "batch_images"
    for_each: "{{input_lines}}"
    step:
      type: "text_to_image"
      model: "flux_schnell"
      params:
        prompt: "{{item}}"
```

Usage:
```bash
# prompts.txt contains:
# a sunset over the ocean
# a mountain landscape
# a city at night

ai-content-pipeline run-chain --config batch.yaml
```

---

## Dynamic Template Pipeline

Use templates for consistent branding.

```yaml
name: "Brand Template"
description: "Generate branded content"

variables:
  brand_style: "modern, professional, blue and white color scheme"
  brand_suffix: "corporate style, clean lines, minimalist"

steps:
  - name: "branded_image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}, {{brand_style}}, {{brand_suffix}}"

  - name: "branded_video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "branded_image"
    params:
      prompt: "professional corporate motion, subtle animation"
```

---

## Running Advanced Pipelines

```bash
# Run with input
ai-content-pipeline run-chain --config advanced.yaml --input "your prompt"

# Estimate cost first
ai-content-pipeline estimate-cost --config advanced.yaml

# Run with parallel execution
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config advanced.yaml

# Dry run to validate
ai-content-pipeline run-chain --config advanced.yaml --dry-run
```
