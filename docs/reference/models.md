# AI Models Reference

Complete reference for all 51 AI models available in the AI Content Generation Suite.

## Overview

| Category | Model Count | Providers |
|----------|-------------|-----------|
| Text-to-Image | 8 | FAL AI, Replicate |
| Image-to-Image | 8 | FAL AI |
| Image-to-Video | 8 | FAL AI, Google |
| Text-to-Video | 4 | FAL AI |
| Image Understanding | 7 | Google Gemini |
| Text-to-Speech | 3 | ElevenLabs |
| Prompt Generation | 5 | OpenRouter |
| Audio/Video Processing | 2 | FAL AI |
| Avatar Generation | 9 | FAL AI |
| Speech-to-Text | 1 | FAL AI (ElevenLabs) |
| **Total** | **51*** | **Multiple** |

*\*Some models support multiple input modes (e.g., sora_2 supports both image-to-video and text-to-video). Total counts unique models.*

---

## Text-to-Image Models

Generate images from text descriptions.

### nano_banana_pro
**Provider:** FAL AI | **Cost:** $0.002/image | **Resolution:** 1024x1024

Fast and high-quality generation. **Recommended for most use cases.**

```bash
ai-content-pipeline generate-image --text "your prompt" --model nano_banana_pro
```

**Features:**
- Fast inference speed
- High-quality output
- Good prompt adherence
- Cost-effective

---

### gpt_image_1_5
**Provider:** FAL AI | **Cost:** $0.003/image | **Resolution:** Up to 1536px

GPT-powered image generation with excellent prompt understanding.

```bash
ai-content-pipeline generate-image --text "your prompt" --model gpt_image_1_5
```

**Features:**
- GPT-powered understanding
- Variable resolution support
- Complex prompt handling

---

### flux_dev
**Provider:** FAL AI | **Cost:** $0.003/image | **Resolution:** 1024x1024

High-quality FLUX.1 Dev model for professional results.

```bash
ai-content-pipeline generate-image --text "your prompt" --model flux_dev
```

**Features:**
- 12B parameter model
- Excellent detail rendering
- Professional quality
- Good for product shots

---

### flux_schnell
**Provider:** FAL AI | **Cost:** $0.001/image | **Resolution:** 1024x1024

Fastest FLUX model, perfect for prototyping and testing.

```bash
ai-content-pipeline generate-image --text "your prompt" --model flux_schnell
```

**Features:**
- Fastest inference
- Lowest cost
- Good quality-to-speed ratio
- **Best for testing**

---

### imagen4
**Provider:** FAL AI | **Cost:** $0.004/image | **Resolution:** 1024x1024

Google Imagen 4 with photorealistic output.

```bash
ai-content-pipeline generate-image --text "your prompt" --model imagen4
```

**Features:**
- Photorealistic style
- Excellent text rendering
- Natural lighting
- Google quality

---

### seedream_v3
**Provider:** FAL AI | **Cost:** $0.002/image | **Resolution:** 1024x1024

ByteDance Seedream v3 with bilingual support.

```bash
ai-content-pipeline generate-image --text "your prompt" --model seedream_v3
```

**Features:**
- Bilingual prompts (English/Chinese)
- Artistic styles
- Good character consistency

---

### seedream3
**Provider:** Replicate | **Cost:** $0.003/image | **Resolution:** Up to 2048px

High-resolution ByteDance model.

```bash
ai-content-pipeline generate-image --text "your prompt" --model seedream3
```

**Features:**
- High resolution up to 2048px
- Detailed output
- Good for large prints

---

### gen4
**Provider:** Replicate | **Cost:** $0.08/image | **Resolution:** 720p/1080p

Runway Gen-4 with multi-reference guidance. **Premium model.**

```bash
ai-content-pipeline generate-image --text "@person in @location" --model gen4 \
  --reference person:path/to/person.jpg \
  --reference location:path/to/place.jpg
```

**Features:**
- Multi-reference guidance (up to 3 images)
- @ syntax for tagged references
- Cinematic quality
- Variable pricing by resolution

---

## Image-to-Image Models

Transform and edit existing images.

### nano_banana_pro_edit
**Provider:** FAL AI | **Cost:** $0.015/image

Fast image editing. **Recommended for edits.**

```bash
ai-content-pipeline edit-image --image input.png --text "make it sunset" --model nano_banana_pro_edit
```

---

### gpt_image_1_5_edit
**Provider:** FAL AI | **Cost:** $0.02/image

GPT-powered image editing with excellent instruction following.

---

### photon_flash
**Provider:** FAL AI | **Cost:** $0.02/image

Luma Photon Flash for creative, fast transformations.

---

### photon_base
**Provider:** FAL AI | **Cost:** $0.03/image

Luma Photon Base for high-quality transformations.

---

### flux_kontext
**Provider:** FAL AI | **Cost:** $0.025/image

FLUX Kontext Dev for contextual editing.

---

### flux_kontext_multi
**Provider:** FAL AI | **Cost:** $0.04/image

FLUX Kontext Multi for multi-image editing.

---

### seededit_v3
**Provider:** FAL AI | **Cost:** $0.02/image

ByteDance SeedEdit v3 for precise editing.

---

### clarity_upscaler
**Provider:** FAL AI | **Cost:** $0.05/image

Clarity AI upscaler for resolution enhancement.

```bash
ai-content-pipeline upscale --image input.png --model clarity_upscaler
```

---

## Image-to-Video Models

Convert images to video animations.

### veo_3_1_fast
**Provider:** FAL AI | **Cost:** $0.40-0.80/video | **Resolution:** 720p/1080p

Google Veo 3.1 Fast with audio generation. **Recommended.**

```bash
ai-content-pipeline image-to-video --image input.png --model veo_3_1_fast
```

**Features:**
- Audio generation included
- Fast processing
- High quality
- 720p or 1080p output

---

### sora_2
**Provider:** FAL AI | **Cost:** $0.40-1.20/video | **Resolution:** 720p

OpenAI Sora 2 with 4-12 second duration.

```bash
ai-content-pipeline image-to-video --image input.png --model sora_2 --duration 8
```

---

### sora_2_pro
**Provider:** FAL AI | **Cost:** $1.20-3.60/video | **Resolution:** 720p/1080p

OpenAI Sora 2 Pro for professional quality.

---

### kling_2_6_pro
**Provider:** FAL AI | **Cost:** $0.50-1.00/video | **Resolution:** 720p/1080p

Kling v2.6 Pro for professional video quality.

```bash
ai-content-pipeline image-to-video --image input.png --model kling_2_6_pro
```

---

### kling_2_1
**Provider:** FAL AI | **Cost:** $0.25-0.50/video | **Resolution:** 720p/1080p

Budget-friendly Kling Video v2.1.

---

### seedance_1_5_pro
**Provider:** FAL AI | **Cost:** $0.40-0.80/video | **Resolution:** 720p/1080p

ByteDance Seedance v1.5 Pro.

---

### hailuo
**Provider:** FAL AI | **Cost:** $0.30-0.50/video | **Resolution:** 768p

MiniMax Hailuo-02, budget-friendly option.

```bash
ai-content-pipeline image-to-video --image input.png --model hailuo
```

---

### wan_2_6
**Provider:** FAL AI | **Cost:** $0.50-1.50/video | **Resolution:** 720p/1080p

Wan v2.6 with multi-shot and audio input support.

---

## Text-to-Video Models

Generate videos directly from text.

### sora_2 (text mode)
**Provider:** FAL AI | **Cost:** $0.40-1.20/video | **Resolution:** 720p

```bash
ai-content-pipeline text-to-video --text "a cat playing piano" --model sora_2
```

---

### sora_2_pro (text mode)
**Provider:** FAL AI | **Cost:** $1.20-6.00/video | **Resolution:** 720p/1080p

Professional text-to-video generation.

---

### kling_2_6_pro (text mode)
**Provider:** FAL AI | **Cost:** $0.35-1.40/video | **Resolution:** 720p

With audio generation support.

---

### hailuo_pro
**Provider:** FAL AI | **Cost:** $0.08/video | **Resolution:** 1080p

MiniMax Hailuo-02 Pro, fixed 6-second duration. **Best budget option.**

```bash
ai-content-pipeline text-to-video --text "ocean waves crashing" --model hailuo_pro
```

---

## Image Understanding Models

Analyze and understand images using AI.

### gemini_describe
**Provider:** Google | **Cost:** $0.001/analysis

Basic image description.

```bash
ai-content-pipeline analyze-image --image input.png --model gemini_describe
```

---

### gemini_detailed
**Provider:** Google | **Cost:** $0.002/analysis

Detailed image analysis with comprehensive descriptions.

---

### gemini_classify
**Provider:** Google | **Cost:** $0.001/analysis

Image classification into categories.

---

### gemini_objects
**Provider:** Google | **Cost:** $0.002/analysis

Object detection and identification.

---

### gemini_ocr
**Provider:** Google | **Cost:** $0.001/analysis

Text extraction from images (OCR).

---

### gemini_composition
**Provider:** Google | **Cost:** $0.002/analysis

Artistic and technical composition analysis.

---

### gemini_qa
**Provider:** Google | **Cost:** $0.001/analysis

Question and answer system for images.

```bash
ai-content-pipeline analyze-image --image input.png --model gemini_qa --question "What color is the car?"
```

---

## Text-to-Speech Models

Convert text to natural speech.

### elevenlabs
**Provider:** ElevenLabs | **Cost:** $0.05/request

High-quality TTS with natural voices.

```bash
ai-content-pipeline text-to-speech --text "Hello world" --model elevenlabs
```

---

### elevenlabs_turbo
**Provider:** ElevenLabs | **Cost:** $0.03/request

Faster generation with good quality.

---

### elevenlabs_v3
**Provider:** ElevenLabs | **Cost:** $0.08/request

Latest v3 model with enhanced quality.

---

## Audio & Video Processing

### thinksound
**Provider:** FAL AI | **Cost:** $0.05/request

AI audio generation.

---

### topaz
**Provider:** FAL AI | **Cost:** $1.50/video

Video upscaling with AI enhancement.

```bash
ai-content-pipeline upscale-video --video input.mp4 --model topaz
```

---

## Avatar Generation Models

Generate talking avatar videos with lip-sync from images.

### omnihuman_v1_5
**Provider:** FAL AI (ByteDance) | **Cost:** $0.16/second | **Resolution:** 720p/1080p

Highest quality audio-driven human animation.

```bash
ai-content-pipeline generate-avatar --image-url "https://..." --audio-url "https://..." --model omnihuman_v1_5
```

**Features:**
- Premium quality lip-sync
- Natural facial expressions
- Turbo mode for faster generation

---

### fabric_1_0
**Provider:** FAL AI (VEED) | **Cost:** $0.08-0.15/video | **Resolution:** 480p/720p

Cost-effective lip-sync video generation.

---

### fabric_1_0_fast
**Provider:** FAL AI (VEED) | **Cost:** $0.10-0.19/video | **Resolution:** 480p/720p

Speed-optimized lip-sync generation.

---

### fabric_1_0_text
**Provider:** FAL AI (VEED) | **Cost:** $0.08-0.15/video | **Resolution:** 480p/720p

Text-to-speech with lip-sync animation.

```bash
ai-content-pipeline generate-avatar --image-url "https://..." --text "Hello world!" --model fabric_1_0_text
```

---

### kling_ref_to_video
**Provider:** FAL AI (Kling O1) | **Cost:** $0.112/second

Character-consistent video generation from reference images.

---

### kling_v2v_reference
**Provider:** FAL AI (Kling O1) | **Cost:** $0.168/second

Style-guided video transformation.

---

### kling_v2v_edit
**Provider:** FAL AI (Kling O1) | **Cost:** $0.168/second

Targeted video modifications and editing.

---

### kling_motion_control
**Provider:** FAL AI (Kling v2.6) | **Cost:** $0.06/second | **Max Duration:** 30s (video) / 10s (image)

Motion transfer from reference video to reference image. **Recommended for dance videos and action sequences.**

```bash
# Python API
from fal_avatar import FALAvatarGenerator

generator = FALAvatarGenerator()
result = generator.transfer_motion(
    image_url="https://example.com/person.jpg",
    video_url="https://example.com/dance.mp4",
    character_orientation="video",  # or "image"
    keep_original_sound=True
)
```

**Features:**
- Motion transfer from video to image
- Dual orientation modes: video (max 30s), image (max 10s)
- Audio preservation option
- Cost-effective standard tier pricing

**Best For:** Dance videos, action sequences, character animation

---

### multitalk
**Provider:** FAL AI | **Cost:** $0.10-0.25/video | **Resolution:** 480p/720p

Multi-person conversational video generation. **Recommended for conversations.**

```bash
# Python API
from fal_avatar import FALAvatarGenerator

generator = FALAvatarGenerator()
result = generator.generate_conversation(
    image_url="https://...",
    first_audio_url="https://...",
    prompt="A natural conversation",
    second_audio_url="https://..."  # Optional
)
```

**Features:**
- Native 2-person conversation support
- Resolution: 480p (base) or 720p (2x cost)
- Frames: 81-129 (>81 = 1.25x cost)
- Acceleration modes: none, regular, high

---

## Model Selection Guide

### By Use Case

| Use Case | Recommended Model | Cost |
|----------|-------------------|------|
| Quick testing | `flux_schnell` | $0.001 |
| Production images | `flux_dev` | $0.003 |
| Budget video | `hailuo_pro` | $0.08 |
| Quality video | `kling_2_6_pro` | $0.50+ |
| Premium video | `sora_2_pro` | $1.20+ |
| Image analysis | `gemini_describe` | $0.001 |
| TTS | `elevenlabs` | $0.05 |

### By Budget

| Budget | Image Model | Video Model |
|--------|-------------|-------------|
| Minimal | `flux_schnell` | `hailuo_pro` |
| Standard | `flux_dev` | `kling_2_1` |
| Premium | `imagen4` | `sora_2_pro` |

---

[Back to Documentation Index](../index.md)
