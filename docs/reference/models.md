# AI Models Reference

Complete reference for all 73 AI models available in the AI Content Generation Suite.

## Overview

| Category | Model Count | Providers |
|----------|-------------|-----------|
| Text-to-Image | 8 | FAL AI, Replicate |
| Image-to-Image | 8 | FAL AI |
| Text-to-Video | 10 | FAL AI, Google, OpenAI, xAI |
| Image-to-Video | 15 | FAL AI, Google, OpenAI, xAI |
| Video-to-Video | 4 | FAL AI (Kuaishou) |
| Avatar Generation | 10 | FAL AI, VEED, Kuaishou, xAI |
| Image Understanding | 7 | Google Gemini |
| Prompt Generation | 5 | OpenRouter |
| Text-to-Speech | 3 | ElevenLabs |
| Speech-to-Text | 1 | ElevenLabs (via FAL) |
| Add Audio | 1 | FAL AI |
| Upscale Video | 1 | Topaz Labs (via FAL) |
| **Total** | **73** | **Multiple** |

---

## Text-to-Image Models (8)

Generate images from text descriptions.

| Model Key | Name | Provider | Cost | Best For |
|-----------|------|----------|------|----------|
| `nano_banana_pro` | Nano Banana Pro | FAL AI | $0.002/image | Fast & high-quality |
| `gpt_image_1_5` | GPT Image 1.5 | OpenAI (via FAL) | $0.003/image | GPT-powered generation |
| `flux_dev` | FLUX.1 Dev | Black Forest Labs | $0.003/image | Highest quality (12B params) |
| `flux_schnell` | FLUX.1 Schnell | Black Forest Labs | $0.001/image | Fastest, best for testing |
| `imagen4` | Google Imagen 4 | Google (via FAL) | $0.004/image | Photorealistic output |
| `seedream_v3` | Seedream v3 | ByteDance | $0.002/image | Multilingual support |
| `seedream3` | Seedream-3 | ByteDance (via Replicate) | $0.003/image | High resolution |
| `gen4` | Runway Gen-4 | Runway (via Replicate) | $0.08/image | Multi-reference guided |

```bash
aicp generate-image --text "your prompt" --model nano_banana_pro
```

---

## Image-to-Image Models (8)

Transform and edit existing images.

| Model Key | Name | Provider | Cost | Best For |
|-----------|------|----------|------|----------|
| `photon` | Luma Photon Flash | Luma AI | $0.02/image | Fast creative modifications |
| `photon_base` | Luma Photon Base | Luma AI | $0.03/image | High-quality transformations |
| `kontext` | FLUX Kontext Dev | Black Forest Labs | $0.025/image | Contextual editing |
| `kontext_multi` | FLUX Kontext Max Multi | Black Forest Labs | $0.04/image | Multi-image editing |
| `seededit` | SeedEdit v3 | ByteDance | $0.02/image | Precise content-preserving edits |
| `clarity` | Clarity Upscaler | FAL AI | $0.05/image | Resolution enhancement (up to 4x) |
| `nano_banana_pro_edit` | Nano Banana Pro Edit | FAL AI | $0.015/image | Fast multi-image editing |
| `gpt_image_1_5_edit` | GPT Image 1.5 Edit | OpenAI (via FAL) | $0.02/image | Natural language editing |

---

## Text-to-Video Models (10)

Generate videos directly from text prompts.

| Model Key | Name | Provider | Cost | Duration | Features |
|-----------|------|----------|------|----------|----------|
| `veo3` | Google Veo 3 | Google (via FAL) | $0.50-0.75/s | 5-8s | Audio generation, 720p |
| `veo3_fast` | Google Veo 3 Fast | Google (via FAL) | $0.25-0.40/s | 5-8s | Fast processing, audio |
| `kling_3_pro` | Kling v3 Pro | Kuaishou | $0.224-0.392/s | 3-15s | Voice control, multi-prompt |
| `kling_3_standard` | Kling v3 Standard | Kuaishou | $0.168-0.308/s | 3-15s | Voice control, multi-prompt |
| `kling_2_6_pro` | Kling v2.6 Pro | Kuaishou | $0.07-0.14/s | 5-10s | Audio, multilingual |
| `kling_o3_pro_t2v` | Kling O3 Pro | Kuaishou | $0.224-0.28/s | 3-15s | Element consistency, @ syntax |
| `sora_2` | Sora 2 | OpenAI (via FAL) | $0.10/s | 4-12s | OpenAI quality |
| `sora_2_pro` | Sora 2 Pro | OpenAI (via FAL) | $0.30-0.50/s | 4-12s | 1080p support |
| `hailuo_pro` | MiniMax Hailuo-02 Pro | MiniMax | $0.08/video | 6s | Budget-friendly, 1080p |
| `grok_imagine` | Grok Imagine Video | xAI (via FAL) | $0.30/6s | 1-15s | Native audio, flexible duration |

```bash
aicp create-video --text "cinematic sunset over mountains"
```

---

## Image-to-Video Models (15)

Convert images into animated videos.

| Model Key | Name | Provider | Cost | Duration | Features |
|-----------|------|----------|------|----------|----------|
| `veo_3_1_fast` | Veo 3.1 Fast | Google (via FAL) | ~$1.20 | 4-8s | Audio generation, fast |
| `kling_3_pro_i2v` | Kling v3 Pro | Kuaishou | $0.224-0.392/s | 5-12s | Voice control, multi-prompt |
| `kling_3_standard_i2v` | Kling v3 Standard | Kuaishou | $0.168-0.308/s | 5-12s | Voice control, multi-prompt |
| `kling_2_6_pro_i2v` | Kling v2.6 Pro | Kuaishou | ~$1.00 | 5-10s | Professional quality |
| `kling_2_1` | Kling v2.1 | Kuaishou | ~$0.50 | 5-10s | Budget Kling option |
| `kling_o3_pro_i2v` | Kling O3 Pro | Kuaishou | $0.224-0.28/s | 3-15s | Element consistency |
| `kling_o3_standard_i2v` | Kling O3 Standard | Kuaishou | $0.168-0.224/s | 3-15s | Element consistency |
| `kling_o3_pro_ref` | Kling O3 Pro Ref | Kuaishou | $0.224-0.28/s | 3-15s | @ syntax, reference images |
| `kling_o3_standard_ref` | Kling O3 Standard Ref | Kuaishou | $0.084-0.112/s | 3-15s | @ syntax, budget O3 |
| `sora_2_i2v` | Sora 2 | OpenAI (via FAL) | ~$0.40 | 4-12s | OpenAI quality |
| `sora_2_pro_i2v` | Sora 2 Pro | OpenAI (via FAL) | ~$2.00 | 4-12s | 1080p support |
| `seedance_1_5_pro` | Seedance v1.5 Pro | ByteDance | ~$0.80 | 5-10s | Motion synthesis |
| `hailuo` | MiniMax Hailuo-02 | MiniMax | ~$0.08 | 6-10s | Budget option |
| `wan_2_6` | Wan v2.6 | Wan | ~$0.50 | 5-15s | Multi-shot, audio input |
| `grok_imagine_i2v` | Grok Imagine Video | xAI (via FAL) | ~$0.30 | 1-15s | Native audio, flexible |

---

## Video-to-Video Models (4)

Edit and transform existing videos.

| Model Key | Name | Provider | Cost | Duration | Features |
|-----------|------|----------|------|----------|----------|
| `kling_o3_pro_edit` | Kling O3 Pro Edit | Kuaishou | $0.336/s | 3-15s | Professional element replacement |
| `kling_o3_standard_edit` | Kling O3 Standard Edit | Kuaishou | $0.252/s | 3-15s | Element replacement, @ syntax |
| `kling_o3_pro_v2v_ref` | Kling O3 Pro V2V Ref | Kuaishou | $0.336/s | 3-15s | Style transfer, audio preservation |
| `kling_o3_standard_v2v_ref` | Kling O3 Standard V2V Ref | Kuaishou | $0.252/s | 3-15s | Style transfer, budget option |

---

## Avatar Generation Models (10)

Generate talking avatar videos with lip-sync, motion transfer, and video editing.

| Model Key | Name | Provider | Cost | Features |
|-----------|------|----------|------|----------|
| `omnihuman_v1_5` | OmniHuman v1.5 | ByteDance | $0.16/s | Premium audio-driven animation |
| `fabric_1_0` | VEED Fabric 1.0 | VEED | $0.08-0.15 | Cost-effective lip-sync |
| `fabric_1_0_fast` | VEED Fabric 1.0 Fast | VEED | $0.10-0.19 | Speed-optimized lip-sync |
| `fabric_1_0_text` | VEED Fabric 1.0 Text | VEED | $0.08-0.15 | Text-to-speech + lip-sync |
| `kling_ref_to_video` | Kling O1 Ref-to-Video | Kuaishou | $0.112/s | Character consistency |
| `kling_v2v_reference` | Kling O1 V2V Reference | Kuaishou | $0.168/s | Style-guided transformation |
| `kling_v2v_edit` | Kling O1 V2V Edit | Kuaishou | $0.168/s | Targeted video editing |
| `kling_motion_control` | Kling v2.6 Motion Control | Kuaishou | $0.06/s | Motion transfer from video |
| `multitalk` | AI Avatar Multi | FAL AI | $0.10-0.25 | Multi-person conversations |
| `grok_video_edit` | Grok Video Edit | xAI (via FAL) | ~$0.36 | AI-powered video editing |

```bash
aicp generate-avatar --image-url "https://..." --audio-url "https://..."
```

---

## Image Understanding Models (7)

Analyze and understand images using Google Gemini.

| Model Key | Name | Cost | Use Case |
|-----------|------|------|----------|
| `gemini_describe` | Gemini Describe | $0.001 | Basic image description |
| `gemini_detailed` | Gemini Detailed | $0.002 | Comprehensive analysis |
| `gemini_classify` | Gemini Classify | $0.001 | Image classification |
| `gemini_objects` | Gemini Objects | $0.002 | Object detection |
| `gemini_ocr` | Gemini OCR | $0.001 | Text extraction (OCR) |
| `gemini_composition` | Gemini Composition | $0.002 | Artistic composition analysis |
| `gemini_qa` | Gemini Q&A | $0.001 | Interactive Q&A about images |

---

## Prompt Generation Models (5)

Optimize and enhance video prompts using OpenRouter.

| Model Key | Name | Cost | Style |
|-----------|------|------|-------|
| `openrouter_video_prompt` | Video Prompt | $0.002 | General |
| `openrouter_video_cinematic` | Video Cinematic | $0.002 | Cinematic |
| `openrouter_video_realistic` | Video Realistic | $0.002 | Realistic |
| `openrouter_video_artistic` | Video Artistic | $0.002 | Artistic |
| `openrouter_video_dramatic` | Video Dramatic | $0.002 | Dramatic |

---

## Text-to-Speech Models (3)

Convert text to natural speech using ElevenLabs.

| Model Key | Name | Cost | Features |
|-----------|------|------|----------|
| `elevenlabs` | ElevenLabs TTS | ~$0.05 | High-quality, professional |
| `elevenlabs_turbo` | ElevenLabs Turbo | ~$0.03 | Fast generation |
| `elevenlabs_v3` | ElevenLabs v3 | ~$0.08 | Latest generation |

---

## Speech-to-Text Models (1)

Transcribe audio with speaker identification.

| Model Key | Name | Provider | Cost | Features |
|-----------|------|----------|------|----------|
| `scribe_v2` | ElevenLabs Scribe v2 | ElevenLabs (via FAL) | $0.008/min | 99 languages, speaker diarization, word timestamps |

```bash
aicp transcribe --input audio.mp3
aicp transcribe --input meeting.mp3 --raw-json   # word-level timestamps
aicp transcribe --input podcast.mp3 --srt         # subtitle file
```

---

## Add Audio Models (1)

Generate AI sound effects for videos.

| Model Key | Name | Provider | Cost | Features |
|-----------|------|----------|------|----------|
| `thinksound` | ThinkSound | FAL AI | $0.001/s | Video context understanding, prompt guidance |

---

## Upscale Video Models (1)

Professional-grade video upscaling.

| Model Key | Name | Provider | Cost | Features |
|-----------|------|----------|------|----------|
| `topaz` | Topaz Video Upscale | Topaz Labs (via FAL) | ~$1.50/video | Up to 4x upscaling, 120 FPS interpolation |

---

## Model Selection Guide

### By Use Case

| Use Case | Recommended Model | Cost |
|----------|-------------------|------|
| Quick image testing | `flux_schnell` | $0.001 |
| Production images | `nano_banana_pro` | $0.002 |
| Budget video | `hailuo_pro` | $0.08 |
| Quality video (t2v) | `kling_3_pro` | $0.50+ |
| Premium video (t2v) | `veo3` | $2.50+ |
| Quality video (i2v) | `kling_3_pro_i2v` | $0.50+ |
| Premium video (i2v) | `veo_3_1_fast` | $1.20+ |
| Avatar/lip-sync | `omnihuman_v1_5` | $0.16/s |
| Budget avatar | `fabric_1_0` | $0.08+ |
| Image analysis | `gemini_describe` | $0.001 |
| TTS | `elevenlabs` | $0.05 |
| Transcription | `scribe_v2` | $0.008/min |

### By Budget

| Budget | Image Model | Video Model (t2v) | Video Model (i2v) |
|--------|-------------|--------------------|--------------------|
| Minimal | `flux_schnell` ($0.001) | `hailuo_pro` ($0.08) | `hailuo` ($0.08) |
| Standard | `nano_banana_pro` ($0.002) | `kling_2_6_pro` ($0.35) | `kling_2_1` ($0.50) |
| Premium | `imagen4` ($0.004) | `veo3` ($4.00) | `veo_3_1_fast` ($1.20) |

---

[Back to Documentation Index](../index.md)
