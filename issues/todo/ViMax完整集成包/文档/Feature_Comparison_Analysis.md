# ViMax vs video-agent-skill Feature Comparison Analysis

> This document provides a comparative analysis of the feature overlap and differences between the ViMax and video-agent-skill projects.

---

## 📊 Overall Comparison

| Feature | ViMax | video-agent-skill |
|---------|-------|-------------------|
| **Positioning** | End-to-end video generation framework | AI content generation toolkit |
| **Core Function** | Idea/Script → Complete video | Single AI model calls + pipeline composition |
| **Intelligence Level** | High (multi-agent collaboration) | Low (API wrapper) |
| **Number of Models** | ~5 | 40+ |
| **Usage Method** | Python API | CLI + Python API |
| **Configuration** | YAML (simple) | YAML (complex pipelines) |

---

## 🏗️ Architecture Comparison

### ViMax Architecture
```
User Input (Idea/Script)
         │
         ▼
┌─────────────────────────────────┐
│      Multi-Agent Pipeline       │
│  ┌───────────┐  ┌───────────┐  │
│  │Screenwriter│  │Storyboard │  │
│  │            │  │  Artist   │  │
│  └───────────┘  └───────────┘  │
│  ┌───────────┐  ┌───────────┐  │
│  │ Character │  │ Reference │  │
│  │ Extractor │  │ Selector  │  │
│  └───────────┘  └───────────┘  │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│         Tools Layer             │
│  • ImageGenerator (Google/Doubao)│
│  • VideoGenerator (Veo/Doubao)  │
└─────────────────────────────────┘
         │
         ▼
     Complete Video
```

### video-agent-skill Architecture
```
User Input (Text/Image/Video)
         │
         ▼
┌─────────────────────────────────┐
│       YAML Pipeline Config      │
│  step1 → step2 → step3 → ...   │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│      Provider Integrations      │
│  ┌─────────┐  ┌─────────┐      │
│  │ FAL AI  │  │ Google  │      │
│  │(40+models)│ │  Veo    │      │
│  └─────────┘  └─────────┘      │
│  ┌─────────┐  ┌─────────┐      │
│  │ElevenLabs│ │OpenRouter│      │
│  │  (TTS)   │  │ (Chat)  │      │
│  └─────────┘  └─────────┘      │
└─────────────────────────────────┘
         │
         ▼
    Generated Content
```

---

## 🔄 Overlapping Features

### 1. Image Generation (Text-to-Image)

| Feature | ViMax | video-agent-skill |
|---------|-------|-------------------|
| **Implementation** | `ImageGeneratorNanobananaGoogleAPI` | `fal_text_to_image` module |
| **Models** | Google Imagen | FLUX, Imagen 4, Seedream, GPT Image, etc. 8+ models |
| **Difference** | Google API only | Multi-provider support, more choices |

### 2. Video Generation (Image-to-Video)

| Feature | ViMax | video-agent-skill |
|---------|-------|-------------------|
| **Implementation** | `VideoGeneratorVeoGoogleAPI` | `fal_image_to_video` module |
| **Models** | Google Veo | Veo 2/3, Hailuo, Kling, Sora 2, etc. 12+ models |
| **Difference** | Veo only | Multi-provider support, more choices |

### 3. Parallel Processing

| Feature | ViMax | video-agent-skill |
|---------|-------|-------------------|
| **Implementation** | `asyncio.gather()` | `PIPELINE_PARALLEL_ENABLED` |
| **Granularity** | Shot-level parallelism | Step-level parallelism |
| **Difference** | Deep integration | Optional toggle |

### 4. Cost Management

| Feature | ViMax | video-agent-skill |
|---------|-------|-------------------|
| **Implementation** | `RateLimiter` | `cost_calculator.py` |
| **Function** | Rate limiting | Estimation + rate limiting |
| **Difference** | Basic rate limiting | Complete cost tracking |

---

## ✅ ViMax Unique Features

### 1. 🤖 Multi-Agent Collaboration System

**Core features not in video-agent-skill:**

| Agent | Function | video-agent-skill Alternative |
|-------|----------|------------------------------|
| **Screenwriter** | Idea → Story → Script | ❌ None (manual script writing needed) |
| **CharacterExtractor** | Auto-extract character info | ❌ None (manual definition needed) |
| **StoryboardArtist** | Auto-design storyboard | ❌ None (manual design needed) |
| **CharacterPortraitsGenerator** | Generate character consistency refs | ❌ None |
| **ReferenceImageSelector** | Smart reference image selection | ❌ None |
| **CameraImageGenerator** | Build camera tree + transitions | ❌ None |

### 2. 🎬 End-to-End Video Generation

```
ViMax:     Idea ──────────────────────────────────► Complete Video
           (one sentence input)                     (multi-shot, consistent)

video-agent-skill: Requires user to manually design each step
           Text → Image → Video (each step manually configured)
```

### 3. 🎭 Character Consistency Guarantee

| Feature | ViMax | video-agent-skill |
|---------|-------|-------------------|
| Character Portrait Generation | ✅ Front/Side/Back | ❌ |
| Cross-shot Consistency | ✅ Reference image selection mechanism | ❌ |
| Camera Dependency Tree | ✅ Auto-build | ❌ |

### 4. 📝 Professional Storyboard Design

ViMax auto-generates professional storyboards including:
- Shot types (close-up/medium/wide)
- Camera angles (high/eye-level/low)
- Camera movements (push/pull/pan/track)
- Audio descriptions (dialogue/sound effects)

video-agent-skill requires users to manually specify all these parameters.

---

## ✅ video-agent-skill Unique Features

### 1. 🎤 Text-to-Speech (TTS)

| Feature | video-agent-skill | ViMax |
|---------|-------------------|-------|
| **Provider** | ElevenLabs | ❌ None |
| **Voices** | 20+ preset voices | ❌ None |
| **Multi-character Dialogue** | ✅ | ❌ None |

```bash
# video-agent-skill supports
ai-content-pipeline tts --text "Hello" --voice "Rachel"
```

### 2. 📊 Video Analysis

| Feature | video-agent-skill | ViMax |
|---------|-------------------|-------|
| **Models** | Gemini 3 Pro, Gemini 2.5 | ❌ None |
| **Functions** | Timeline analysis, description, transcription | ❌ None |

```bash
# video-agent-skill supports
ai-content-pipeline analyze-video -i video.mp4 -t timeline
```

### 3. 🔊 Speech-to-Text (STT)

| Feature | video-agent-skill | ViMax |
|---------|-------------------|-------|
| **Model** | ElevenLabs Scribe v2 | ❌ None |
| **Functions** | Transcription + speaker diarization | ❌ None |

### 4. 🖼️ Image Editing (Image-to-Image)

| Feature | video-agent-skill | ViMax |
|---------|-------------------|-------|
| **Models** | 8+ (Photon, FLUX, Clarity, etc.) | ❌ None |
| **Functions** | Edit, upscale, style transfer | ❌ None |

### 5. 👤 Digital Human/Avatar Generation

| Feature | video-agent-skill | ViMax |
|---------|-------------------|-------|
| **Models** | OmniHuman, VEED Fabric, Kling, etc. 9+ | ❌ None |
| **Functions** | Lip sync, motion transfer | ❌ None |

### 6. 🎥 Video Processing Tools

| Feature | video-agent-skill | ViMax |
|---------|-------------------|-------|
| **Audio Addition** | ThinksSound | ❌ None |
| **Video Upscaling** | Topaz | ❌ None |
| **Video Concatenation** | ✅ | ✅ (basic) |

### 7. 💻 CLI Tools

```bash
# video-agent-skill rich CLI
ai-content-pipeline list-models          # List all models
ai-content-pipeline generate-image       # Generate image
ai-content-pipeline create-video         # Create video
ai-content-pipeline estimate-cost        # Estimate cost
aicp --help                              # Short command
```

ViMax has no CLI, can only be used through Python scripts.

### 8. 📋 YAML Pipeline Configuration

video-agent-skill supports complex YAML pipelines:

```yaml
name: "Custom Pipeline"
steps:
  - type: "parallel_group"
    steps:
      - type: "text_to_image"
        model: "flux_schnell"
      - type: "text_to_image"
        model: "imagen_4"
  - type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "step_0"
```

ViMax's YAML is only for API configuration, doesn't support custom pipelines.

---

## 📈 Model Support Comparison

### Image Generation Models

| Model | ViMax | video-agent-skill |
|-------|:-----:|:-----------------:|
| Google Imagen | ✅ | ✅ |
| FLUX.1 Dev | ❌ | ✅ |
| FLUX.1 Schnell | ❌ | ✅ |
| Imagen 4 | ❌ | ✅ |
| Seedream v3 | ❌ | ✅ |
| Nano Banana Pro | ✅ | ✅ |
| GPT Image 1.5 | ❌ | ✅ |
| Doubao Seedream | ✅ | ❌ |

### Video Generation Models

| Model | ViMax | video-agent-skill |
|-------|:-----:|:-----------------:|
| Google Veo | ✅ | ✅ |
| Google Veo 2 | ❌ | ✅ |
| Google Veo 3 | ❌ | ✅ |
| Sora 2 | ❌ | ✅ |
| Kling Video | ❌ | ✅ |
| Hailuo | ❌ | ✅ |
| Wan v2.6 | ❌ | ✅ |
| Doubao Seedance | ✅ | ❌ |

---

## 🎯 Use Case Recommendations

### When to Use ViMax

1. **Creative Video Creation** — Only have an idea, need complete creative workflow
2. **Story-Driven Videos** — Need character consistency, storyboard design
3. **Batch Scene Generation** — Auto scene splitting, auto shot design
4. **Non-Technical Users** — Don't want to manually configure each step

### When to Use video-agent-skill

1. **Fine-Grained Control** — Need complete control over each step
2. **Multi-Model Selection** — Need to compare different model effects
3. **Audio Needs** — Need TTS, voiceover, sound effects
4. **Video Post-Processing** — Need upscaling, analysis, editing
5. **Digital Human Production** — Need Avatar/lip sync
6. **CLI Workflows** — Prefer command-line operations

---

## 🔧 Integration Suggestions

### Option 1: ViMax Uses video-agent-skill as Tools Layer

```python
# Replace ViMax's tools/ directory
# Use video-agent-skill's multi-model support

# Before (ViMax):
from tools import ImageGeneratorNanobananaGoogleAPI

# After (integrated):
from packages.core.ai_content_pipeline import AIPipelineManager
manager = AIPipelineManager()
image = manager.generate_image(prompt, model="flux_dev")  # More model choices
```

**Advantage**: ViMax gains 40+ model support

### Option 2: video-agent-skill Adds Agent Layer

```python
# Add to video-agent-skill:
# packages/agents/
#   ├── screenwriter.py
#   ├── storyboard_artist.py
#   └── ...

# New CLI command:
ai-content-pipeline idea-to-video --idea "A story about friendship between a cat and dog"
```

**Advantage**: video-agent-skill gains end-to-end capabilities

### Option 3: Complementary Use

```
┌─────────────────────────────────────────────────────┐
│                    ViMax                            │
│  (Idea → Story → Script → Storyboard → Frame Desc) │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│              video-agent-skill                      │
│  (Frame Desc → Image Gen → Video Gen → TTS → Merge)│
└─────────────────────────────────────────────────────┘
```

**Advantage**: Best of both worlds, optimal combination

---

## 📝 Summary

| Dimension | ViMax Advantage | video-agent-skill Advantage |
|-----------|----------------|----------------------------|
| **Intelligence** | ⭐⭐⭐⭐⭐ Fully automated creation | ⭐⭐ Requires manual orchestration |
| **Number of Models** | ⭐⭐ ~5 | ⭐⭐⭐⭐⭐ 40+ |
| **Ease of Use** | ⭐⭐⭐⭐ One-click generation | ⭐⭐⭐ Requires configuration |
| **Flexible Control** | ⭐⭐ Fixed workflow | ⭐⭐⭐⭐⭐ Fully customizable |
| **Audio Support** | ⭐ Basic | ⭐⭐⭐⭐⭐ TTS/STT |
| **CLI Tools** | ⭐ None | ⭐⭐⭐⭐⭐ Complete |
| **Consistency Guarantee** | ⭐⭐⭐⭐⭐ Character/Scene | ⭐ None |

**Conclusion**: The two projects have different positioning and complement each other. ViMax is the "director", video-agent-skill is the "toolbox". Best practice is to integrate and use together.

---

*Last Updated: 2026-02-03*
