# Phase 5: CLI Commands & Testing

**Duration**: 2-3 days
**Dependencies**: Phase 4 completed (Pipelines)
**Outcome**: CLI commands available and full test coverage

---

## Overview

Add CLI commands for ViMax pipelines and ensure comprehensive test coverage.

```
ai-content-pipeline vimax-idea2video --idea "A samurai's journey"
ai-content-pipeline vimax-script2video --script script.json
ai-content-pipeline vimax-novel2movie --novel novel.txt
```

---

## Subtask 5.1: CLI Commands

**Estimated Time**: 3-4 hours

### Description
Add CLI commands for all ViMax pipelines.

### Target File
```
packages/core/ai_content_platform/vimax/cli/commands.py
```

### Implementation

```python
"""
CLI Commands for ViMax Pipelines

Adds vimax-* commands to the ai-content-pipeline CLI.
"""

import click
import asyncio
import json
from pathlib import Path

from ..pipelines import (
    Idea2VideoPipeline, Idea2VideoConfig,
    Script2VideoPipeline, Script2VideoConfig,
    Novel2MoviePipeline, Novel2MovieConfig,
)


def run_async(coro):
    """Run async function in sync context."""
    return asyncio.get_event_loop().run_until_complete(coro)


@click.group()
def vimax():
    """ViMax pipeline commands for novel-to-video generation."""
    pass


@vimax.command("idea2video")
@click.option("--idea", "-i", required=True, help="Video idea or concept")
@click.option("--output", "-o", default="output/vimax/idea2video", help="Output directory")
@click.option("--duration", "-d", default=60.0, type=float, help="Target duration in seconds")
@click.option("--video-model", default="kling", help="Video generation model")
@click.option("--image-model", default="flux_dev", help="Image generation model")
@click.option("--llm-model", default="claude-3.5-sonnet", help="LLM model for scripts")
@click.option("--portraits/--no-portraits", default=True, help="Generate character portraits")
@click.option("--config", "-c", type=click.Path(exists=True), help="Config YAML file")
def idea2video(idea, output, duration, video_model, image_model, llm_model, portraits, config):
    """
    Generate video from an idea.

    Example:
        aicp vimax idea2video --idea "A samurai's journey at sunrise"
    """
    click.echo(f"🎬 Starting Idea2Video pipeline...")
    click.echo(f"   Idea: {idea[:100]}...")

    # Load or create config
    if config:
        pipeline_config = Idea2VideoConfig.from_yaml(config)
    else:
        pipeline_config = Idea2VideoConfig(
            output_dir=output,
            target_duration=duration,
            video_model=video_model,
            image_model=image_model,
            llm_model=llm_model,
            generate_portraits=portraits,
        )

    pipeline = Idea2VideoPipeline(pipeline_config)

    async def run():
        return await pipeline.run(idea)

    result = run_async(run())

    if result.success:
        click.echo(f"\n✅ Pipeline completed successfully!")
        click.echo(f"   📜 Script: {result.script.title}")
        click.echo(f"   🎭 Characters: {len(result.characters)}")
        click.echo(f"   🎬 Scenes: {result.script.scene_count}")
        if result.output and result.output.final_video:
            click.echo(f"   🎥 Video: {result.output.final_video.video_path}")
        click.echo(f"   💰 Total cost: ${result.total_cost:.3f}")
        click.echo(f"   ⏱️  Duration: {result.duration:.1f}s")
    else:
        click.echo(f"\n❌ Pipeline failed!")
        for error in result.errors:
            click.echo(f"   Error: {error}")
        raise click.Abort()


@vimax.command("script2video")
@click.option("--script", "-s", required=True, type=click.Path(exists=True), help="Script JSON file")
@click.option("--output", "-o", default="output/vimax/script2video", help="Output directory")
@click.option("--video-model", default="kling", help="Video generation model")
@click.option("--image-model", default="flux_dev", help="Image generation model")
def script2video(script, output, video_model, image_model):
    """
    Generate video from an existing script.

    Example:
        aicp vimax script2video --script my_script.json
    """
    click.echo(f"🎬 Starting Script2Video pipeline...")
    click.echo(f"   Script: {script}")

    config = Script2VideoConfig(
        output_dir=output,
        video_model=video_model,
        image_model=image_model,
    )

    pipeline = Script2VideoPipeline(config)

    async def run():
        return await pipeline.run(script)

    result = run_async(run())

    if result.success:
        click.echo(f"\n✅ Pipeline completed successfully!")
        if result.output and result.output.final_video:
            click.echo(f"   🎥 Video: {result.output.final_video.video_path}")
        click.echo(f"   💰 Total cost: ${result.total_cost:.3f}")
    else:
        click.echo(f"\n❌ Pipeline failed!")
        for error in result.errors:
            click.echo(f"   Error: {error}")
        raise click.Abort()


@vimax.command("novel2movie")
@click.option("--novel", "-n", required=True, type=click.Path(exists=True), help="Novel text file")
@click.option("--title", "-t", default="Untitled", help="Novel title")
@click.option("--output", "-o", default="output/vimax/novel2movie", help="Output directory")
@click.option("--max-scenes", default=10, type=int, help="Maximum scenes to generate")
@click.option("--video-model", default="kling", help="Video generation model")
@click.option("--image-model", default="flux_dev", help="Image generation model")
def novel2movie(novel, title, output, max_scenes, video_model, image_model):
    """
    Convert a novel to a movie.

    Example:
        aicp vimax novel2movie --novel my_novel.txt --title "Epic Adventure"
    """
    click.echo(f"🎬 Starting Novel2Movie pipeline...")
    click.echo(f"   Novel: {novel}")
    click.echo(f"   Title: {title}")

    # Read novel text
    with open(novel, 'r', encoding='utf-8') as f:
        novel_text = f.read()

    click.echo(f"   Length: {len(novel_text):,} characters")

    config = Novel2MovieConfig(
        output_dir=output,
        max_scenes=max_scenes,
        video_model=video_model,
        image_model=image_model,
    )

    pipeline = Novel2MoviePipeline(config)

    async def run():
        return await pipeline.run(novel_text, title)

    result = run_async(run())

    if result.success:
        click.echo(f"\n✅ Pipeline completed successfully!")
        click.echo(f"   📚 Chapters processed: {len(result.chapters)}")
        click.echo(f"   📜 Scripts generated: {len(result.scripts)}")
        click.echo(f"   🎭 Characters found: {len(result.characters)}")
        if result.output and result.output.final_video:
            click.echo(f"   🎥 Video: {result.output.final_video.video_path}")
        click.echo(f"   💰 Total cost: ${result.total_cost:.3f}")
    else:
        click.echo(f"\n❌ Pipeline failed!")
        for error in result.errors:
            click.echo(f"   Error: {error}")
        raise click.Abort()


@vimax.command("extract-characters")
@click.option("--text", "-t", required=True, help="Text to extract characters from (or file path)")
@click.option("--output", "-o", help="Output JSON file")
@click.option("--model", "-m", default="claude-3.5-sonnet", help="LLM model")
def extract_characters(text, output, model):
    """
    Extract characters from text.

    Example:
        aicp vimax extract-characters --text "John and Mary went to the park..."
        aicp vimax extract-characters --text story.txt
    """
    from ..agents import CharacterExtractor, CharacterExtractorConfig

    # Check if text is a file path
    if Path(text).exists():
        with open(text, 'r', encoding='utf-8') as f:
            text = f.read()

    click.echo(f"🔍 Extracting characters...")
    click.echo(f"   Text length: {len(text)} characters")

    config = CharacterExtractorConfig(model=model)
    extractor = CharacterExtractor(config)

    async def run():
        return await extractor.process(text)

    result = run_async(run())

    if result.success:
        click.echo(f"\n✅ Found {len(result.result)} characters:")
        for char in result.result:
            click.echo(f"   • {char.name}: {char.description[:50]}...")

        if output:
            characters_data = [c.model_dump() for c in result.result]
            with open(output, 'w') as f:
                json.dump(characters_data, f, indent=2)
            click.echo(f"\n📄 Saved to: {output}")
    else:
        click.echo(f"\n❌ Extraction failed: {result.error}")


@vimax.command("generate-script")
@click.option("--idea", "-i", required=True, help="Story idea")
@click.option("--output", "-o", help="Output JSON file")
@click.option("--duration", "-d", default=60.0, type=float, help="Target duration")
@click.option("--model", "-m", default="claude-3.5-sonnet", help="LLM model")
def generate_script(idea, output, duration, model):
    """
    Generate a screenplay from an idea.

    Example:
        aicp vimax generate-script --idea "A detective solves a mystery" --output script.json
    """
    from ..agents import Screenwriter, ScreenwriterConfig

    click.echo(f"📝 Generating screenplay...")
    click.echo(f"   Idea: {idea}")

    config = ScreenwriterConfig(
        model=model,
        target_duration=duration,
    )
    writer = Screenwriter(config)

    async def run():
        return await writer.process(idea)

    result = run_async(run())

    if result.success:
        script = result.result
        click.echo(f"\n✅ Generated screenplay:")
        click.echo(f"   📜 Title: {script.title}")
        click.echo(f"   📝 Logline: {script.logline}")
        click.echo(f"   🎬 Scenes: {script.scene_count}")
        click.echo(f"   ⏱️  Duration: {script.total_duration:.1f}s")

        if output:
            with open(output, 'w') as f:
                json.dump(script.model_dump(), f, indent=2, default=str)
            click.echo(f"\n📄 Saved to: {output}")
    else:
        click.echo(f"\n❌ Generation failed: {result.error}")


@vimax.command("list-models")
def list_models():
    """List available models for ViMax pipelines."""
    click.echo("🎨 Available Models for ViMax Pipelines\n")

    click.echo("📦 Image Generation:")
    models = [
        ("flux_dev", "FLUX.1 Dev - High quality", "$0.003"),
        ("flux_schnell", "FLUX.1 Schnell - Fast", "$0.001"),
        ("imagen4", "Imagen 4 - Photorealistic", "$0.004"),
        ("nano_banana_pro", "Nano Banana Pro - Balanced", "$0.002"),
    ]
    for model, desc, cost in models:
        click.echo(f"   • {model}: {desc} ({cost})")

    click.echo("\n📦 Video Generation:")
    models = [
        ("kling", "Kling v1 - Reliable", "~$0.15/5s"),
        ("kling_2_1", "Kling v2.1 - Improved", "~$0.15/5s"),
        ("veo3", "Veo 3 - Highest quality", "~$0.50/5s"),
        ("hailuo", "Hailuo - Cost effective", "~$0.10/5s"),
    ]
    for model, desc, cost in models:
        click.echo(f"   • {model}: {desc} ({cost})")

    click.echo("\n📦 LLM Models:")
    models = [
        ("claude-3.5-sonnet", "Claude 3.5 Sonnet - Best balance"),
        ("claude-3-opus", "Claude 3 Opus - Highest quality"),
        ("gpt-4", "GPT-4 Turbo"),
        ("gpt-4o", "GPT-4o - Fast"),
    ]
    for model, desc in models:
        click.echo(f"   • {model}: {desc}")


def register_commands(cli):
    """Register ViMax commands with main CLI."""
    cli.add_command(vimax)


# For standalone testing
if __name__ == "__main__":
    vimax()
```

---

## Subtask 5.2: Register CLI Commands

**Estimated Time**: 1 hour

### Description
Register ViMax commands with the main CLI.

### File to Modify
```
packages/core/ai_content_platform/cli/main.py
```

### Changes to Add

```python
# Add import at top
from ..vimax.cli.commands import register_commands as register_vimax_commands

# Add in main() or CLI setup
register_vimax_commands(cli)
```

### Alternative: Separate Entry Point

**File**: `packages/core/ai_content_platform/vimax/cli/__init__.py`

```python
"""
ViMax CLI Module
"""

from .commands import vimax, register_commands

__all__ = ["vimax", "register_commands"]
```

---

## Subtask 5.3: Integration Tests

**Estimated Time**: 3-4 hours

### Description
Create comprehensive integration tests for the full pipeline.

### Target File
```
tests/integration/test_vimax_e2e.py
```

### Implementation

```python
"""
End-to-End Integration Tests for ViMax Pipelines

These tests run the full pipeline with mocked external services.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
import json

from ai_content_platform.vimax.pipelines import (
    Idea2VideoPipeline,
    Idea2VideoConfig,
    Script2VideoPipeline,
    Script2VideoConfig,
)
from ai_content_platform.vimax.agents import (
    Script,
    AgentResult,
)
from ai_content_platform.vimax.interfaces import (
    Scene, ShotDescription, ImageOutput, VideoOutput, PipelineOutput,
    CharacterInNovel,
)


class TestIdea2VideoE2E:
    """End-to-end tests for Idea2Video pipeline."""

    @pytest.fixture
    def output_dir(self, tmp_path):
        return tmp_path / "output"

    @pytest.fixture
    def mock_script(self):
        return Script(
            title="Samurai at Sunrise",
            logline="A lone samurai reflects on his journey",
            scenes=[
                Scene(
                    scene_id="scene_001",
                    title="Dawn",
                    location="Mountain peak",
                    time="Dawn",
                    shots=[
                        ShotDescription(
                            shot_id="shot_001",
                            description="Wide shot of samurai silhouette against sunrise",
                            duration_seconds=5,
                            image_prompt="Lone samurai silhouette, mountain peak, dramatic sunrise",
                            video_prompt="Subtle wind movement, clouds drifting slowly",
                        ),
                        ShotDescription(
                            shot_id="shot_002",
                            description="Close-up of samurai's face",
                            duration_seconds=3,
                            image_prompt="Samurai face close-up, determined expression, golden light",
                            video_prompt="Gentle breathing, eyes slowly opening",
                        ),
                    ],
                ),
            ],
            total_duration=8.0,
        )

    @pytest.fixture
    def mock_characters(self):
        return [
            CharacterInNovel(
                name="Takeshi",
                description="A veteran samurai",
                age="45",
                gender="male",
                appearance="Weathered face, gray-streaked hair",
                personality="Stoic but wise",
                role="protagonist",
            ),
        ]

    @pytest.mark.asyncio
    async def test_full_pipeline_flow(self, output_dir, mock_script, mock_characters):
        """Test complete pipeline from idea to video."""
        config = Idea2VideoConfig(
            output_dir=str(output_dir),
            generate_portraits=False,
            target_duration=10.0,
        )

        pipeline = Idea2VideoPipeline(config)

        # Mock external calls
        with patch.multiple(
            pipeline,
            screenwriter=MagicMock(),
            character_extractor=MagicMock(),
            storyboard_artist=MagicMock(),
            camera_generator=MagicMock(),
        ):
            # Configure mocks
            pipeline.screenwriter.process = AsyncMock(
                return_value=AgentResult.ok(mock_script, cost=0.01)
            )
            pipeline.character_extractor.process = AsyncMock(
                return_value=AgentResult.ok(mock_characters, cost=0.005)
            )

            from ai_content_platform.vimax.agents.storyboard_artist import StoryboardResult
            mock_storyboard = StoryboardResult(
                title=mock_script.title,
                scenes=mock_script.scenes,
                images=[
                    ImageOutput(image_path=str(output_dir / "shot_001.png"), prompt="test"),
                    ImageOutput(image_path=str(output_dir / "shot_002.png"), prompt="test"),
                ],
            )
            pipeline.storyboard_artist.process = AsyncMock(
                return_value=AgentResult.ok(mock_storyboard, cost=0.006)
            )

            mock_output = PipelineOutput(
                pipeline_name="test",
                videos=[
                    VideoOutput(video_path=str(output_dir / "shot_001.mp4"), duration=5),
                    VideoOutput(video_path=str(output_dir / "shot_002.mp4"), duration=3),
                ],
                final_video=VideoOutput(
                    video_path=str(output_dir / "final.mp4"),
                    duration=8,
                ),
            )
            pipeline.camera_generator.process = AsyncMock(
                return_value=AgentResult.ok(mock_output, cost=0.30)
            )

            # Run pipeline
            result = await pipeline.run("A samurai's journey at sunrise")

            # Assertions
            assert result.success
            assert result.script.title == "Samurai at Sunrise"
            assert len(result.characters) == 1
            assert result.output.final_video is not None
            assert result.total_cost > 0

            # Verify all agents were called
            pipeline.screenwriter.process.assert_called_once()
            pipeline.character_extractor.process.assert_called_once()
            pipeline.storyboard_artist.process.assert_called_once()
            pipeline.camera_generator.process.assert_called_once()

    @pytest.mark.asyncio
    async def test_pipeline_handles_agent_failure(self, output_dir):
        """Test pipeline handles agent failures gracefully."""
        config = Idea2VideoConfig(output_dir=str(output_dir))
        pipeline = Idea2VideoPipeline(config)

        with patch.object(pipeline, 'screenwriter') as mock_writer:
            mock_writer.process = AsyncMock(
                return_value=AgentResult.fail("LLM service unavailable")
            )

            result = await pipeline.run("Test idea")

            assert not result.success
            assert "Script generation failed" in result.errors[0]

    @pytest.mark.asyncio
    async def test_pipeline_cost_tracking(self, output_dir, mock_script, mock_characters):
        """Test that costs are properly accumulated."""
        config = Idea2VideoConfig(
            output_dir=str(output_dir),
            generate_portraits=False,
        )
        pipeline = Idea2VideoPipeline(config)

        costs = {
            "script": 0.015,
            "characters": 0.008,
            "storyboard": 0.009,
            "video": 0.45,
        }

        with patch.multiple(pipeline, screenwriter=MagicMock(), character_extractor=MagicMock(),
                           storyboard_artist=MagicMock(), camera_generator=MagicMock()):
            pipeline.screenwriter.process = AsyncMock(
                return_value=AgentResult.ok(mock_script, cost=costs["script"])
            )
            pipeline.character_extractor.process = AsyncMock(
                return_value=AgentResult.ok(mock_characters, cost=costs["characters"])
            )

            from ai_content_platform.vimax.agents.storyboard_artist import StoryboardResult
            pipeline.storyboard_artist.process = AsyncMock(
                return_value=AgentResult.ok(
                    StoryboardResult(title="test", scenes=[], images=[]),
                    cost=costs["storyboard"]
                )
            )
            pipeline.camera_generator.process = AsyncMock(
                return_value=AgentResult.ok(
                    PipelineOutput(
                        pipeline_name="test",
                        final_video=VideoOutput(video_path="/tmp/test.mp4", duration=5)
                    ),
                    cost=costs["video"]
                )
            )

            result = await pipeline.run("Test idea")

            expected_total = sum(costs.values())
            assert abs(result.total_cost - expected_total) < 0.001


class TestCLICommands:
    """Tests for CLI commands."""

    def test_idea2video_command_exists(self):
        """Test that idea2video command is registered."""
        from ai_content_platform.vimax.cli.commands import vimax

        # Check command exists
        assert "idea2video" in [cmd.name for cmd in vimax.commands.values()]

    def test_script2video_command_exists(self):
        """Test that script2video command is registered."""
        from ai_content_platform.vimax.cli.commands import vimax

        assert "script2video" in [cmd.name for cmd in vimax.commands.values()]

    def test_list_models_command(self):
        """Test list-models command output."""
        from click.testing import CliRunner
        from ai_content_platform.vimax.cli.commands import vimax

        runner = CliRunner()
        result = runner.invoke(vimax, ["list-models"])

        assert result.exit_code == 0
        assert "flux_dev" in result.output
        assert "kling" in result.output


class TestConfigLoading:
    """Tests for configuration loading."""

    def test_load_config_from_yaml(self, tmp_path):
        """Test loading config from YAML file."""
        config_content = """
output_dir: output/test
target_duration: 30.0
video_model: veo3
image_model: imagen4
llm_model: gpt-4
generate_portraits: false
"""
        config_path = tmp_path / "config.yaml"
        config_path.write_text(config_content)

        config = Idea2VideoConfig.from_yaml(str(config_path))

        assert config.output_dir == "output/test"
        assert config.target_duration == 30.0
        assert config.video_model == "veo3"
        assert config.generate_portraits is False

    def test_default_config_values(self):
        """Test default configuration values."""
        config = Idea2VideoConfig()

        assert config.target_duration == 60.0
        assert config.video_model == "kling"
        assert config.image_model == "flux_dev"
        assert config.generate_portraits is True
```

---

## Subtask 5.4: Documentation

**Estimated Time**: 2 hours

### Target File
```
packages/core/ai_content_platform/vimax/README.md
```

### Implementation

```markdown
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

# Run integration tests
pytest tests/integration/test_vimax_e2e.py -v

# Run all tests
pytest tests/ -k vimax -v
```
```

---

## Subtask 5.5: Example Configurations

**Estimated Time**: 1 hour

### Target Files
```
input/pipelines/vimax/
├── idea2video_basic.yaml
├── idea2video_high_quality.yaml
├── script2video.yaml
└── novel2movie.yaml
```

### File: `input/pipelines/vimax/idea2video_basic.yaml`

```yaml
# Basic Idea2Video Configuration
# Usage: aicp vimax idea2video --idea "..." --config input/pipelines/vimax/idea2video_basic.yaml

output_dir: output/vimax/basic
target_duration: 30.0
save_intermediate: true

# Models (cost-effective)
video_model: kling
image_model: nano_banana_pro
llm_model: claude-3.5-sonnet

# Features
generate_portraits: false
```

### File: `input/pipelines/vimax/idea2video_high_quality.yaml`

```yaml
# High Quality Idea2Video Configuration
# Usage: aicp vimax idea2video --idea "..." --config input/pipelines/vimax/idea2video_high_quality.yaml

output_dir: output/vimax/hq
target_duration: 60.0
save_intermediate: true

# Models (high quality)
video_model: veo3
image_model: flux_dev
llm_model: claude-3.5-sonnet

# Features
generate_portraits: true

# Agent overrides
screenwriter:
  shots_per_scene: 4
  style: "cinematic, dramatic lighting, film quality"

storyboard_artist:
  style_prefix: "high quality film still, cinematic composition, 4K detail, "
  aspect_ratio: "16:9"
```

---

## Phase 5 Completion Checklist

- [ ] **5.1** CLI commands implemented
- [ ] **5.2** Commands registered with main CLI
- [ ] **5.3** Integration tests passing
- [ ] **5.4** Documentation complete
- [ ] **5.5** Example configurations created

### Verification Commands

```bash
# Test CLI commands
ai-content-pipeline vimax --help
ai-content-pipeline vimax list-models
ai-content-pipeline vimax idea2video --help

# Run all tests
pytest tests/unit/vimax/ -v
pytest tests/integration/test_vimax_e2e.py -v

# Test with example config
ai-content-pipeline vimax idea2video \
  --idea "A samurai at sunrise" \
  --config input/pipelines/vimax/idea2video_basic.yaml
```

---

## Final Integration Checklist

### Code Complete
- [ ] All 5 phases implemented
- [ ] All tests passing
- [ ] Documentation complete

### Quality Assurance
- [ ] No breaking changes to existing CLI
- [ ] Error handling comprehensive
- [ ] Logging adequate
- [ ] Cost tracking accurate

### Deployment Ready
- [ ] Example configs provided
- [ ] README updated
- [ ] Version bumped if needed

---

*Previous Phase*: [PHASE_4_PIPELINES.md](./PHASE_4_PIPELINES.md)
*Main Plan*: [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
