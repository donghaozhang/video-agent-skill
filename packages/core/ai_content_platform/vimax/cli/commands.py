"""
CLI Commands for ViMax Pipelines

Adds vimax-* commands to the ai-content-pipeline CLI.
"""

import click
import asyncio
import json
from pathlib import Path


def run_async(coro):
    """Run async function in sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


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
@click.option("--llm-model", default="kimi-k2.5", help="LLM model for scripts")
@click.option("--portraits/--no-portraits", default=True, help="Generate character portraits")
@click.option("--config", "-c", type=click.Path(exists=True), help="Config YAML file")
def idea2video(idea, output, duration, video_model, image_model, llm_model, portraits, config):
    """
    Generate video from an idea.

    Example:
        aicp vimax idea2video --idea "A samurai's journey at sunrise"
    """
    from ..pipelines import Idea2VideoPipeline, Idea2VideoConfig

    click.echo(f"Starting Idea2Video pipeline...")
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
        click.echo(f"\nPipeline completed successfully!")
        click.echo(f"   Script: {result.script.title}")
        click.echo(f"   Characters: {len(result.characters)}")
        click.echo(f"   Scenes: {result.script.scene_count}")
        if result.output and result.output.final_video:
            click.echo(f"   Video: {result.output.final_video.video_path}")
        click.echo(f"   Total cost: ${result.total_cost:.3f}")
        click.echo(f"   Duration: {result.duration:.1f}s")
    else:
        click.echo(f"\nPipeline failed!")
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
    from ..pipelines import Script2VideoPipeline, Script2VideoConfig

    click.echo(f"Starting Script2Video pipeline...")
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
        click.echo(f"\nPipeline completed successfully!")
        if result.output and result.output.final_video:
            click.echo(f"   Video: {result.output.final_video.video_path}")
        click.echo(f"   Total cost: ${result.total_cost:.3f}")
    else:
        click.echo(f"\nPipeline failed!")
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
    from ..pipelines import Novel2MoviePipeline, Novel2MovieConfig

    click.echo(f"Starting Novel2Movie pipeline...")
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
        click.echo(f"\nPipeline completed successfully!")
        click.echo(f"   Chapters processed: {len(result.chapters)}")
        click.echo(f"   Scripts generated: {len(result.scripts)}")
        click.echo(f"   Characters found: {len(result.characters)}")
        if result.output and result.output.final_video:
            click.echo(f"   Video: {result.output.final_video.video_path}")
        click.echo(f"   Total cost: ${result.total_cost:.3f}")
    else:
        click.echo(f"\nPipeline failed!")
        for error in result.errors:
            click.echo(f"   Error: {error}")
        raise click.Abort()


@vimax.command("extract-characters")
@click.option("--text", "-t", required=True, help="Text to extract characters from (or file path)")
@click.option("--output", "-o", help="Output JSON file")
@click.option("--model", "-m", default="kimi-k2.5", help="LLM model")
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

    click.echo(f"Extracting characters...")
    click.echo(f"   Text length: {len(text)} characters")

    config = CharacterExtractorConfig(model=model)
    extractor = CharacterExtractor(config)

    async def run():
        return await extractor.process(text)

    result = run_async(run())

    if result.success:
        click.echo(f"\nFound {len(result.result)} characters:")
        for char in result.result:
            desc = char.description[:50] if char.description else "No description"
            click.echo(f"   - {char.name}: {desc}...")

        if output:
            characters_data = [c.model_dump() for c in result.result]
            with open(output, 'w') as f:
                json.dump(characters_data, f, indent=2)
            click.echo(f"\nSaved to: {output}")
    else:
        click.echo(f"\nExtraction failed: {result.error}")


@vimax.command("generate-script")
@click.option("--idea", "-i", required=True, help="Story idea")
@click.option("--output", "-o", help="Output JSON file")
@click.option("--duration", "-d", default=60.0, type=float, help="Target duration")
@click.option("--model", "-m", default="kimi-k2.5", help="LLM model")
def generate_script(idea, output, duration, model):
    """
    Generate a screenplay from an idea.

    Example:
        aicp vimax generate-script --idea "A detective solves a mystery" --output script.json
    """
    from ..agents import Screenwriter, ScreenwriterConfig

    click.echo(f"Generating screenplay...")
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
        click.echo(f"\nGenerated screenplay:")
        click.echo(f"   Title: {script.title}")
        click.echo(f"   Logline: {script.logline}")
        click.echo(f"   Scenes: {script.scene_count}")
        click.echo(f"   Duration: {script.total_duration:.1f}s")

        if output:
            with open(output, 'w') as f:
                json.dump(script.model_dump(), f, indent=2, default=str)
            click.echo(f"\nSaved to: {output}")
    else:
        click.echo(f"\nGeneration failed: {result.error}")


@vimax.command("list-models")
def list_models():
    """List available models for ViMax pipelines."""
    click.echo("Available Models for ViMax Pipelines\n")

    click.echo("Image Generation:")
    models = [
        ("flux_dev", "FLUX.1 Dev - High quality", "$0.003"),
        ("flux_schnell", "FLUX.1 Schnell - Fast", "$0.001"),
        ("imagen4", "Imagen 4 - Photorealistic", "$0.004"),
        ("nano_banana_pro", "Nano Banana Pro - Balanced", "$0.002"),
    ]
    for model, desc, cost in models:
        click.echo(f"   - {model}: {desc} ({cost})")

    click.echo("\nVideo Generation:")
    models = [
        ("kling", "Kling v1 - Reliable", "~$0.15/5s"),
        ("kling_2_1", "Kling v2.1 - Improved", "~$0.15/5s"),
        ("veo3", "Veo 3 - Highest quality", "~$0.50/5s"),
        ("hailuo", "Hailuo - Cost effective", "~$0.10/5s"),
    ]
    for model, desc, cost in models:
        click.echo(f"   - {model}: {desc} ({cost})")

    click.echo("\nLLM Models:")
    models = [
        ("kimi-k2.5", "Kimi K2.5 - Default, cost effective ($0.50/$2.80 per 1M tokens)"),
        ("claude-3.5-sonnet", "Claude 3.5 Sonnet - High quality"),
        ("claude-3-opus", "Claude 3 Opus - Highest quality"),
        ("gpt-4", "GPT-4 Turbo"),
        ("gpt-4o", "GPT-4o - Fast"),
    ]
    for model, desc in models:
        click.echo(f"   - {model}: {desc}")


def register_commands(cli):
    """Register ViMax commands with main CLI."""
    cli.add_command(vimax)


# For standalone testing
if __name__ == "__main__":
    vimax()
