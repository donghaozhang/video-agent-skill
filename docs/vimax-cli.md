# ViMax CLI Reference

ViMax is a standalone CLI for advanced AI video generation pipelines. It converts ideas, scripts, and novels into videos using LLM-powered agents for screenwriting, character extraction, storyboard generation, and video synthesis.

## Installation

ViMax is included in the main package:

```bash
pip install -e .
vimax --help
```

## Commands

### End-to-End Pipelines

#### `idea2video` - Idea to Video

Generate a complete video from a text idea. Runs the full pipeline: idea → screenplay → characters → portraits → storyboard → video.

```bash
vimax idea2video --idea "A samurai's journey through feudal Japan" --output output/
vimax idea2video --idea "A detective solves a mystery" --duration 30 --video-model veo3
vimax idea2video --idea "Space exploration" --no-portraits --image-model flux_dev
```

| Flag | Default | Description |
|------|---------|-------------|
| `--idea` | required | Text description of the video concept |
| `--output` | `output/` | Output directory |
| `--duration` | auto | Target video duration in seconds |
| `--video-model` | `kling` | Video generation model |
| `--image-model` | `nano_banana_pro` | Image generation model |
| `--portraits/--no-portraits` | enabled | Generate character portraits for consistency |
| `--references/--no-references` | enabled | Use reference images for visual consistency |

#### `script2video` - Script to Video

Generate video from an existing screenplay JSON file.

```bash
vimax script2video --script screenplay.json --output output/
vimax script2video --script screenplay.json --portraits registry.json --video-model veo3
```

| Flag | Default | Description |
|------|---------|-------------|
| `--script` | required | Path to screenplay JSON file |
| `--output` | `output/` | Output directory |
| `--portraits` | none | Portrait registry JSON for character consistency |
| `--video-model` | `kling` | Video generation model |
| `--image-model` | `nano_banana_pro` | Image generation model |

#### `novel2movie` - Novel to Movie

Convert a full novel into a multi-chapter movie.

```bash
vimax novel2movie --novel story.txt --title "Epic Adventure" --output output/
vimax novel2movie --novel novel.txt --title "Mystery" --max-scenes 20 --video-model veo3
```

| Flag | Default | Description |
|------|---------|-------------|
| `--novel` | required | Path to novel text file |
| `--title` | required | Movie title |
| `--output` | `output/` | Output directory |
| `--max-scenes` | auto | Maximum scenes per chapter |
| `--video-model` | `kling` | Video generation model |
| `--image-model` | `nano_banana_pro` | Image generation model |

### Individual Pipeline Steps

#### `generate-script` - Generate Screenplay

Generate a screenplay JSON from a text idea.

```bash
vimax generate-script --idea "A detective mystery in Tokyo" --output script.json
vimax generate-script --idea "Space opera" --duration 60 --model claude-3.5-sonnet
```

| Flag | Default | Description |
|------|---------|-------------|
| `--idea` | required | Text description |
| `--output` | stdout | Output JSON file |
| `--duration` | auto | Target duration in seconds |
| `--model` | `kimi-k2.5` | LLM model for generation |

#### `extract-characters` - Extract Characters

Extract character descriptions from text using an LLM.

```bash
vimax extract-characters --text "The old wizard Gandalf and the hobbit Frodo..."
vimax extract-characters --text story.txt --model gpt-4 --output characters.json
```

| Flag | Default | Description |
|------|---------|-------------|
| `--text` | required | Text content or path to file |
| `--model` | `kimi-k2.5` | LLM model |
| `--output` | stdout | Output JSON file |

#### `generate-portraits` - Generate Character Portraits

Generate multi-view portraits from character descriptions for visual consistency.

```bash
vimax generate-portraits --characters characters.json --save-registry registry.json
vimax generate-portraits --characters characters.json --image-model flux_dev --views front side
```

| Flag | Default | Description |
|------|---------|-------------|
| `--characters` | required | Characters JSON file |
| `--image-model` | `nano_banana_pro` | Image generation model |
| `--llm-model` | `kimi-k2.5` | LLM for prompt generation |
| `--views` | `front side back 3_4` | Portrait views to generate |
| `--save-registry` | none | Save as portrait registry JSON |

#### `generate-storyboard` - Generate Storyboard

Generate storyboard images from a screenplay.

```bash
vimax generate-storyboard --script screenplay.json --output storyboard/
vimax generate-storyboard --script screenplay.json --portraits registry.json --style cinematic
```

| Flag | Default | Description |
|------|---------|-------------|
| `--script` | required | Screenplay JSON file |
| `--output` | `output/` | Output directory |
| `--image-model` | `nano_banana_pro` | Image generation model |
| `--style` | none | Visual style (cinematic, anime, etc.) |
| `--portraits` | none | Portrait registry for character consistency |
| `--reference-strength` | auto | How strongly to match reference images |

### Utility Commands

#### `create-registry` - Create Portrait Registry

Create a portrait registry from existing portrait images.

```bash
vimax create-registry --portraits-dir portraits/ --project-id my-project
```

#### `show-registry` - Show Registry Contents

Display the contents of a portrait registry.

```bash
vimax show-registry --registry registry.json
```

#### `list-models` - List Available Models

Show all models available for each pipeline step.

```bash
vimax list-models
```

## Available Models

### Image Generation
| Model | Cost | Notes |
|-------|------|-------|
| `nano_banana_pro` | $0.002 | Default, fast |
| `flux_dev` | $0.003 | High quality |
| `flux_schnell` | $0.001 | Fastest |
| `imagen4` | $0.004 | Photorealistic |

### Reference Image
| Model | Cost | Notes |
|-------|------|-------|
| `nano_banana_pro` | $0.002 | Cost effective |
| `flux_kontext` | $0.025 | High quality reference |
| `flux_redux` | $0.020 | Style transfer |
| `seededit_v3` | $0.025 | Precise edits |
| `photon_flash` | $0.015 | Fast reference |

### Video Generation
| Model | Cost | Notes |
|-------|------|-------|
| `kling` | ~$0.15/5s | Default, reliable |
| `kling_2_1` | ~$0.15/5s | Improved quality |
| `veo3` | ~$0.50/5s | Highest quality |
| `hailuo` | ~$0.10/5s | Cost effective |

### LLM (Screenwriting)
| Model | Notes |
|-------|-------|
| `kimi-k2.5` | Default, cost effective |
| `claude-3.5-sonnet` | High quality |
| `claude-3-opus` | Highest quality |
| `gpt-4` | GPT-4 Turbo |
| `gpt-4o` | Fast |

## Typical Workflows

### Quick video from an idea
```bash
vimax idea2video --idea "A cat exploring a magical forest" --video-model kling
```

### High-quality production
```bash
# Step 1: Generate screenplay
vimax generate-script --idea "A noir detective story" --model claude-3.5-sonnet --output script.json

# Step 2: Extract and generate character portraits
vimax extract-characters --text script.json --output characters.json
vimax generate-portraits --characters characters.json --image-model flux_dev --save-registry registry.json

# Step 3: Generate storyboard with character consistency
vimax generate-storyboard --script script.json --portraits registry.json --style cinematic --output storyboard/

# Step 4: Generate video
vimax script2video --script script.json --portraits registry.json --video-model veo3 --output final/
```

### Novel adaptation
```bash
vimax novel2movie --novel my_novel.txt --title "The Great Adventure" --video-model veo3
```

## Architecture

ViMax is built on an agent-based architecture:

```
vimax CLI (Click)
  |
  +-- Pipelines (orchestration)
  |   +-- Idea2VideoPipeline
  |   +-- Script2VideoPipeline
  |   +-- Novel2MoviePipeline
  |
  +-- Agents (LLM-powered)
  |   +-- Screenwriter
  |   +-- CharacterExtractor
  |   +-- CharacterPortraits
  |   +-- StoryboardArtist
  |   +-- CameraGenerator
  |   +-- ReferenceSelector
  |
  +-- Adapters (service integrations)
      +-- LLMAdapter (OpenRouter)
      +-- ImageAdapter (FAL AI)
      +-- VideoAdapter (FAL AI)
```

Source: `packages/core/ai_content_platform/vimax/`

## Relationship to aicp

`vimax` is a **separate CLI entry point**, not a subcommand of `aicp`:

- `aicp` — single-step content generation (images, videos, audio, pipelines)
- `vimax` — multi-step narrative pipelines (idea → screenplay → storyboard → video)

Both are installed from the same package and share the same model registry.
