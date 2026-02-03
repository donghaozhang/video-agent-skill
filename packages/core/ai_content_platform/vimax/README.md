# ViMax Integration Module

Novel-to-video pipeline integration for the AI Content Pipeline.

## Quick Start

```bash
# Generate video from an idea
ai-content-pipeline vimax idea2video --idea "A samurai's journey at sunrise"

# Generate from existing script
ai-content-pipeline vimax script2video --script my_script.json

# Convert a novel to movie
ai-content-pipeline vimax novel2movie --novel my_novel.txt --title "Epic Adventure"
```

## Features

- **Character Extraction**: Automatically extract characters from text
- **Character Portraits**: Generate consistent multi-angle character portraits
- **Screenplay Generation**: Convert ideas into structured screenplays
- **Storyboard Creation**: Generate visual storyboards from scripts
- **Video Generation**: Create videos from storyboard images
- **Full Pipelines**: End-to-end workflows from text to video

## Pipelines

### Idea2Video Pipeline

Converts a text idea into a complete video:

```python
from ai_content_platform.vimax.pipelines import Idea2VideoPipeline, Idea2VideoConfig

config = Idea2VideoConfig(
    output_dir="output/my_video",
    target_duration=60.0,
    video_model="kling",
)

pipeline = Idea2VideoPipeline(config)
result = await pipeline.run("A detective solves a mystery in a rainy city")

if result.success:
    print(f"Video: {result.output.final_video.video_path}")
```

### Script2Video Pipeline

Generates video from an existing script:

```python
from ai_content_platform.vimax.pipelines import Script2VideoPipeline

pipeline = Script2VideoPipeline()
result = await pipeline.run("path/to/script.json")
```

### Novel2Movie Pipeline

Converts long-form content into a movie:

```python
from ai_content_platform.vimax.pipelines import Novel2MoviePipeline

pipeline = Novel2MoviePipeline()
result = await pipeline.run(novel_text, title="My Novel")
```

## Agents

Individual agents can be used standalone:

```python
from ai_content_platform.vimax.agents import (
    CharacterExtractor,
    Screenwriter,
    StoryboardArtist,
)

# Extract characters
extractor = CharacterExtractor()
result = await extractor.process(story_text)
characters = result.result

# Generate screenplay
writer = Screenwriter()
result = await writer.process("A love story in Paris")
script = result.result

# Create storyboard
artist = StoryboardArtist()
result = await artist.process(script)
storyboard = result.result
```

## Configuration

### YAML Configuration

```yaml
# config.yaml
output_dir: output/vimax
target_duration: 60.0
video_model: kling
image_model: flux_dev
llm_model: claude-3.5-sonnet
generate_portraits: true
save_intermediate: true
```

### Environment Variables

```bash
FAL_KEY=your_fal_key
OPENROUTER_API_KEY=your_openrouter_key  # For LLM calls
GEMINI_API_KEY=your_gemini_key          # Optional
```

## Cost Estimation

| Component | Model | Approximate Cost |
|-----------|-------|------------------|
| Script Generation | Claude 3.5 Sonnet | $0.01-0.03 |
| Character Portraits | FLUX.1 Dev | $0.003/image |
| Storyboard Images | FLUX.1 Dev | $0.003/image |
| Video Generation | Kling | $0.03/second |

**Example**: A 60-second video with 12 shots:
- Script: ~$0.02
- 12 storyboard images: ~$0.04
- 12 videos (5s each): ~$1.80
- **Total: ~$1.86**

## CLI Commands

```bash
# Main commands
ai-content-pipeline vimax idea2video --idea "..." [options]
ai-content-pipeline vimax script2video --script file.json [options]
ai-content-pipeline vimax novel2movie --novel file.txt [options]

# Utility commands
ai-content-pipeline vimax extract-characters --text "..."
ai-content-pipeline vimax generate-script --idea "..."
ai-content-pipeline vimax list-models

# Options
--output, -o      Output directory
--duration, -d    Target duration in seconds
--video-model     Video generation model (kling, veo3, etc.)
--image-model     Image generation model (flux_dev, etc.)
--config, -c      Path to YAML config file
```

## Testing

```bash
# Run unit tests
pytest tests/unit/vimax/ -v

# Run all tests
pytest tests/ -k vimax -v
```

## Architecture

```
vimax/
├── interfaces/       # Data models (Character, Shot, Scene, etc.)
├── adapters/         # Service wrappers (Image, Video, LLM)
├── agents/           # LLM-powered components
│   ├── character_extractor.py
│   ├── character_portraits.py
│   ├── screenwriter.py
│   ├── storyboard_artist.py
│   └── camera_generator.py
├── pipelines/        # End-to-end workflows
│   ├── idea2video.py
│   ├── script2video.py
│   └── novel2movie.py
└── cli/              # Command-line interface
```
