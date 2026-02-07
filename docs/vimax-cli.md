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

Generate storyboard images from a screenplay. Supports character reference images for visual consistency across shots by matching camera angles to portrait views.

```bash
# Basic: text-to-image only (no character references)
vimax generate-storyboard --script script.json --output storyboard/

# With character references for consistency
vimax generate-storyboard --script script.json --portraits registry.json --output storyboard/

# Photorealistic style (override default "storyboard panel" look)
vimax generate-storyboard --script script.json --portraits registry.json --style "photorealistic, cinematic lighting, " --output storyboard/

# High-quality with strong reference matching
vimax generate-storyboard --script script.json --portraits registry.json --reference-strength 0.8 --image-model flux_dev --output storyboard/
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--script` | `-s` | required | Screenplay JSON file (see format below) |
| `--output` | `-o` | `media/generated/vimax/storyboard` | Output directory for generated images |
| `--image-model` | | `nano_banana_pro` | Image generation model |
| `--style` | | `storyboard panel, cinematic composition, ` | Style prefix prepended to every prompt |
| `--portraits` | `-p` | none | Portrait registry JSON for character consistency |
| `--reference-model` | | `nano_banana_pro` | Model used for reference-based generation (image-to-image) |
| `--reference-strength` | | `0.6` | How strongly to match reference images (0.0-1.0) |

**How `--style` works:** The style string is prepended to every shot's `image_prompt`. The default `"storyboard panel, cinematic composition, "` produces illustrated storyboard panels. To get photorealistic output, change it:

| Style Value | Result |
|-------------|--------|
| `"storyboard panel, cinematic composition, "` (default) | Illustrated storyboard panels |
| `"photorealistic, cinematic lighting, "` | Photorealistic film stills |
| `"anime, cel shaded, "` | Anime-style frames |
| `"cinematic, "` | General cinematic look |
| `""` (empty string) | No style prefix, uses raw image_prompt |

**How reference images work:**
1. When `--portraits` is provided, each shot's `characters` list is checked against the registry
2. The `camera_angle` is mapped to a portrait view (see mapping below)
3. The best matching portrait is used as input to an image-to-image model (`--reference-model`)
4. Without `--portraits`, plain text-to-image is used (~$0.002/image vs ~$0.15/image with references)

**Camera angle to portrait view mapping:**

| camera_angle in script | Portrait view used |
|------------------------|-------------------|
| `front`, `eye_level`, `straight_on`, `face_on` | `front_view` |
| `side`, `profile`, `left`, `right` | `side_view` |
| `back`, `behind`, `rear` | `back_view` |
| `three_quarter`, `45_degree`, `angled` | `three_quarter_view` |

If the preferred view is not available, falls back to `front_view`, then any available view.

**Shot types** (affects reference view preference):

| shot_type | Preferred views | Notes |
|-----------|----------------|-------|
| `close_up` | front, three_quarter | Strong reference influence (face fills frame) |
| `extreme_close_up` | front | Very strong reference influence |
| `medium` | front, three_quarter, side | Good reference influence |
| `two_shot` | front, three_quarter, side | Uses first character's portrait as primary |
| `wide` | front, side, back | Weak reference influence (character is small) |
| `establishing` | front, side | Weak reference influence |
| `over_the_shoulder` | back, three_quarter | Back/side view works best |
| `pov` | (none) | No reference used |
| `insert` | (none) | No reference used |

##### Script JSON Format

The `--script` file must be a JSON with this structure:

```json
{
  "title": "The Meeting",
  "logline": "Optional one-line summary.",
  "scenes": [
    {
      "scene_id": "scene_001",
      "title": "The Arrival",
      "description": "Scene description for context.",
      "location": "Warm coffee shop with large windows",
      "time": "Morning, golden hour light",
      "shots": [
        {
          "shot_id": "shot_001",
          "shot_type": "wide",
          "description": "Miranda walks through the front door.",
          "camera_movement": "static",
          "camera_angle": "eye_level",
          "characters": ["Miranda"],
          "duration_seconds": 5.0,
          "image_prompt": "Cinematic wide shot of a warm cozy coffee shop, a woman in a gray blazer walks through the door, morning sunlight"
        }
      ]
    }
  ],
  "total_duration": 17.0
}
```

**Required fields per shot:** `shot_id`, `description`

**Optional fields:** `shot_type` (default: `medium`), `camera_movement` (default: `static`), `camera_angle` (default: `eye_level`), `characters` (default: `[]`), `duration_seconds` (default: `5.0`), `image_prompt` (if omitted, `description` is used)

**Camera movements:** `static`, `pan`, `tilt`, `zoom`, `dolly`, `tracking`, `crane`, `handheld`

##### Portrait Registry JSON Format

The `--portraits` file maps character names to portrait image paths:

```json
{
  "project_id": "my_project",
  "portraits": {
    "Miranda": {
      "character_name": "Miranda",
      "front_view": "path/to/miranda_front.png",
      "side_view": null,
      "back_view": null,
      "three_quarter_view": "path/to/miranda_3quarter.png"
    },
    "Elena": {
      "character_name": "Elena",
      "front_view": "path/to/elena_front.png",
      "side_view": null,
      "back_view": null,
      "three_quarter_view": null
    }
  }
}
```

Portrait paths can be local file paths (absolute or relative) — they are uploaded to FAL at runtime. Only provide views you have images for; set others to `null`.

##### Cost Breakdown

| Mode | Cost per image | When used |
|------|---------------|-----------|
| Text-to-image (no portraits) | ~$0.002 | `--portraits` not provided |
| Reference-based (`nano_banana_pro`) | ~$0.15 | `--portraits` provided, character found in shot |
| Reference-based (`flux_kontext`) | ~$0.025 | Using `--reference-model flux_kontext` |

##### Example: Full Storyboard Workflow

```bash
# 1. Create script.json (manually or via generate-script)
vimax generate-script --idea "Two friends reunite at a coffee shop" --output script.json

# 2. Create portraits (manually or via generate-portraits pipeline)
#    Place character images in a folder, create registry.json pointing to them

# 3. Generate storyboard - photorealistic with strong character matching
vimax generate-storyboard \
  --script script.json \
  --portraits registry.json \
  --style "photorealistic, cinematic lighting, shallow depth of field, " \
  --reference-strength 0.8 \
  --output storyboard/

# 4. Check output
ls storyboard/  # One .png per shot
```

**Tips:**
- Use `--reference-strength 0.8` for close-ups to get strong face matching
- Use `--reference-strength 0.4-0.6` for wide shots to allow more creative freedom
- The default `--style` produces storyboard panel illustrations — change it for photorealistic output
- Character names in `script.json` shots must exactly match keys in `registry.json` portraits
- More portrait views = better angle matching (provide at least `front_view`)

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
