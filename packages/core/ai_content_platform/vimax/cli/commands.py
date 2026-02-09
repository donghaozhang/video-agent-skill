"""
CLI Commands for ViMax Pipelines

Provides the ``vimax`` Click subgroup, registered under the main
``aicp`` CLI.  Usage: ``aicp vimax <command>``.
"""

import click
import asyncio
import json
from pathlib import Path


def run_async(coro):
    """Run async function in sync context."""
    return asyncio.run(coro)


@click.group()
def vimax():
    """ViMax pipeline commands for novel-to-video generation.

    Access via: aicp vimax <command>
    """
    pass


@vimax.command("idea2video")
@click.option("--idea", "-i", required=True, help="Video idea or concept")
@click.option("--output", "-o", default="media/generated/vimax/idea2video", help="Output directory")
@click.option("--duration", "-d", default=60.0, type=float, help="Target duration in seconds")
@click.option("--video-model", default="kling", help="Video generation model")
@click.option("--image-model", default="nano_banana_pro", help="Image generation model")
@click.option("--llm-model", default="kimi-k2.5", help="LLM model for scripts")
@click.option("--portraits/--no-portraits", default=True, help="Generate character portraits")
@click.option("--references/--no-references", default=True, help="Use portraits for storyboard consistency")
@click.option("--config", "-c", type=click.Path(exists=True), help="Config YAML file")
def idea2video(idea, output, duration, video_model, image_model, llm_model, portraits, references, config):
    """
    Generate video from an idea.

    Uses character portraits for visual consistency when --references is enabled.

    Example:
        aicp vimax idea2video --idea "A samurai's journey at sunrise"
        aicp vimax idea2video --idea "Epic battle" --no-references
    """
    from ..pipelines import Idea2VideoPipeline, Idea2VideoConfig

    click.echo("Starting Idea2Video pipeline...")
    click.echo(f"   Idea: {idea[:100]}...")
    click.echo(f"   Character references: {'enabled' if portraits and references else 'disabled'}")

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
            use_character_references=references,
        )

    pipeline = Idea2VideoPipeline(pipeline_config)

    async def run():
        return await pipeline.run(idea)

    result = run_async(run())

    if result.success:
        click.echo("\nPipeline completed successfully!")
        click.echo(f"   Script: {result.script.title}")
        click.echo(f"   Characters: {len(result.characters)}")
        click.echo(f"   Scenes: {result.script.scene_count}")
        if result.output and result.output.final_video:
            click.echo(f"   Video: {result.output.final_video.video_path}")
        click.echo(f"   Total cost: ${result.total_cost:.3f}")
        if result.duration is not None:
            click.echo(f"   Duration: {result.duration:.1f}s")
    else:
        click.echo("\nPipeline failed!")
        for error in result.errors:
            click.echo(f"   Error: {error}")
        raise click.Abort()


@vimax.command("script2video")
@click.option("--script", "-s", required=True, type=click.Path(exists=True), help="Script JSON file")
@click.option("--output", "-o", default="media/generated/vimax/script2video", help="Output directory")
@click.option("--video-model", default="kling", help="Video generation model")
@click.option("--image-model", default="nano_banana_pro", help="Image generation model")
@click.option("--portraits", "-p", type=click.Path(exists=True), help="Portrait registry JSON for character consistency")
@click.option("--references/--no-references", default=True, help="Use portraits for storyboard consistency")
def script2video(script, output, video_model, image_model, portraits, references):
    """
    Generate video from an existing script.

    Use --portraits to maintain character consistency across shots.

    Example:
        aicp vimax script2video --script my_script.json
        aicp vimax script2video --script my_script.json --portraits registry.json
    """
    from ..pipelines import Script2VideoPipeline, Script2VideoConfig
    from ..interfaces import CharacterPortraitRegistry

    click.echo("Starting Script2Video pipeline...")
    click.echo(f"   Script: {script}")

    # Load portrait registry if provided
    portrait_registry = None
    if portraits and references:
        with open(portraits, 'r', encoding='utf-8') as f:
            registry_data = json.load(f)
        portrait_registry = CharacterPortraitRegistry.from_dict(registry_data)
        click.echo(f"   Using portraits: {len(portrait_registry.portraits)} characters")

    config = Script2VideoConfig(
        output_dir=output,
        video_model=video_model,
        image_model=image_model,
        use_character_references=references,
    )

    pipeline = Script2VideoPipeline(config)

    async def run():
        return await pipeline.run(script, portrait_registry=portrait_registry)

    result = run_async(run())

    if result.success:
        click.echo("\nPipeline completed successfully!")
        if result.output and result.output.final_video:
            click.echo(f"   Video: {result.output.final_video.video_path}")
        click.echo(f"   Used references: {result.used_references}")
        click.echo(f"   Total cost: ${result.total_cost:.3f}")
    else:
        click.echo("\nPipeline failed!")
        for error in result.errors:
            click.echo(f"   Error: {error}")
        raise click.Abort()


@vimax.command("novel2movie")
@click.option("--novel", "-n", required=True, type=click.Path(exists=True), help="Novel text file")
@click.option("--title", "-t", default="Untitled", help="Novel title")
@click.option("--output", "-o", default="media/generated/vimax/novel2movie", help="Output directory")
@click.option("--max-scenes", default=10, type=int, help="Maximum scenes to generate")
@click.option("--video-model", default="kling", help="Video generation model")
@click.option("--image-model", default="nano_banana_pro", help="Image generation model")
@click.option("--storyboard-only", is_flag=True, default=False, help="Stop after storyboard (skip video generation)")
def novel2movie(novel, title, output, max_scenes, video_model, image_model, storyboard_only):
    """
    Convert a novel to a movie.

    Example:
        aicp vimax novel2movie --novel my_novel.txt --title "Epic Adventure"
    """
    from ..pipelines import Novel2MoviePipeline, Novel2MovieConfig

    mode = "storyboard only (steps 1-5)" if storyboard_only else "full pipeline"
    click.echo(f"Starting Novel2Movie pipeline ({mode})...")
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
        storyboard_only=storyboard_only,
    )

    pipeline = Novel2MoviePipeline(config)

    async def run():
        return await pipeline.run(novel_text, title)

    result = run_async(run())

    if result.success:
        click.echo("\nPipeline completed successfully!")
        click.echo(f"   Chapters processed: {len(result.chapters)}")
        click.echo(f"   Scripts generated: {len(result.scripts)}")
        click.echo(f"   Characters found: {len(result.characters)}")
        if result.output and result.output.final_video:
            click.echo(f"   Video: {result.output.final_video.video_path}")
        click.echo(f"   Total cost: ${result.total_cost:.3f}")
    else:
        click.echo("\nPipeline failed!")
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

    click.echo("Extracting characters...")
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

    click.echo("Generating screenplay...")
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
        click.echo("\nGenerated screenplay:")
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


@vimax.command("generate-storyboard")
@click.option("--script", "-s", required=True, type=click.Path(exists=True), help="Script JSON file")
@click.option("--output", "-o", default="media/generated/vimax/storyboard", help="Output directory")
@click.option("--image-model", default="nano_banana_pro", help="Image generation model")
@click.option("--style", default="photorealistic, cinematic lighting, film still, ", help="Style prefix for prompts")
@click.option("--portraits", "-p", type=click.Path(exists=True), help="Portrait registry JSON file for character consistency")
@click.option("--reference-model", default="nano_banana_pro", help="Model for reference-based generation")
@click.option("--reference-strength", default=0.6, type=float, help="Reference image strength (0.0-1.0)")
def generate_storyboard(script, output, image_model, style, portraits, reference_model, reference_strength):
    """
    Generate storyboard images from a script.

    Use --portraits to maintain character consistency across shots.

    Example:
        aicp vimax generate-storyboard --script script.json --output storyboard/
        aicp vimax generate-storyboard --script script.json --portraits registry.json
    """
    from ..agents import StoryboardArtist, StoryboardArtistConfig
    from ..agents.screenwriter import Script
    from ..interfaces import CharacterPortraitRegistry

    click.echo("Generating storyboard...")
    click.echo(f"   Script: {script}")
    click.echo(f"   Output: {output}")
    click.echo(f"   Model: {image_model}")

    # Load script
    with open(script, 'r', encoding='utf-8') as f:
        script_data = json.load(f)

    script_obj = Script(**script_data)
    click.echo(f"   Title: {script_obj.title}")
    click.echo(f"   Shots: {sum(s.shot_count for s in script_obj.scenes)}")

    # Load portrait registry if provided
    portrait_registry = None
    if portraits:
        with open(portraits, 'r', encoding='utf-8') as f:
            registry_data = json.load(f)
        portrait_registry = CharacterPortraitRegistry.from_dict(registry_data)
        click.echo(f"   Using portraits: {len(portrait_registry.portraits)} characters")
        click.echo(f"   Reference model: {reference_model}")
        click.echo(f"   Reference strength: {reference_strength}")

    # Detect inline references already in the script JSON
    has_inline_refs = any(
        shot.primary_reference_image or shot.character_references
        for scene in script_obj.scenes
        for shot in scene.shots
    )
    if has_inline_refs and not portrait_registry:
        inline_count = sum(
            1 for scene in script_obj.scenes
            for shot in scene.shots
            if shot.primary_reference_image or shot.character_references
        )
        click.echo(f"   Inline references: {inline_count} shots have reference images in script")
        click.echo(f"   Reference model: {reference_model}")
        click.echo(f"   Reference strength: {reference_strength}")

    config = StoryboardArtistConfig(
        image_model=image_model,
        style_prefix=style,
        output_dir=output,
        use_character_references=portrait_registry is not None or has_inline_refs,
        reference_model=reference_model,
        reference_strength=reference_strength,
    )
    artist = StoryboardArtist(config)

    async def run():
        # Check for inline references already present in the script JSON
        has_inline_refs = any(
            shot.primary_reference_image or shot.character_references
            for scene in script_obj.scenes
            for shot in scene.shots
        )
        # Pre-resolve references from registry (only if no inline refs already exist)
        if portrait_registry and len(portrait_registry.portraits) > 0 and not has_inline_refs:
            resolved = await artist.resolve_references(script_obj, portrait_registry)
            return resolved, await artist.process(script_obj, portrait_registry=portrait_registry)
        # Inline refs or no refs — process directly
        return 0, await artist.process(script_obj, portrait_registry=portrait_registry if portrait_registry else None)

    _resolved_count, result = run_async(run())

    # Display reference mappings per shot (from registry resolution or inline)
    ref_shots = [
        shot
        for scene in script_obj.scenes
        for shot in scene.shots
        if shot.character_references or shot.primary_reference_image
    ]
    if ref_shots or portrait_registry:
        label = "Inline" if has_inline_refs else "Resolved"
        if ref_shots:
            click.echo(f"\n   {label} references for {len(ref_shots)} shots:")
        else:
            click.echo("\n   No character references matched from portrait registry.")
        for scene in script_obj.scenes:
            for shot in scene.shots:
                if shot.character_references:
                    refs = ", ".join(
                        f"{name} -> {path}" for name, path in shot.character_references.items()
                    )
                    click.echo(f"     {shot.shot_id}: {refs}")
                elif shot.primary_reference_image:
                    click.echo(f"     {shot.shot_id}: {shot.primary_reference_image}")
                elif shot.characters:
                    click.echo(f"     {shot.shot_id}: (no matching portraits for {shot.characters})")

    if result.success:
        click.echo("\nStoryboard generated successfully!")
        click.echo(f"   Images: {len(result.result.images)}")
        click.echo(f"   Total cost: ${result.result.total_cost:.3f}")
        click.echo(f"   Used references: {result.metadata.get('used_references', False)}")
        click.echo(f"   Output: {output}")
        for img in result.result.images[:3]:  # Show first 3
            click.echo(f"   - {img.image_path}")
        if len(result.result.images) > 3:
            click.echo(f"   ... and {len(result.result.images) - 3} more")
    else:
        click.echo(f"\nStoryboard generation failed: {result.error}")


@vimax.command("generate-portraits")
@click.option("--characters", "-c", required=True, type=click.Path(exists=True), help="Characters JSON file")
@click.option("--output", "-o", default="media/generated/vimax/portraits", help="Output directory")
@click.option("--image-model", default="nano_banana_pro", help="Image generation model")
@click.option("--llm-model", default="kimi-k2.5", help="LLM model for prompt optimization")
@click.option("--views", default="front,side,back,three_quarter", help="Comma-separated list of views")
@click.option("--max-characters", default=5, type=int, help="Maximum characters to process")
@click.option("--save-registry/--no-registry", default=True, help="Save portrait registry JSON")
def generate_portraits(characters, output, image_model, llm_model, views, max_characters, save_registry):
    """
    Generate multi-view character portraits for visual consistency.

    Creates front, side, back, and 3/4 view portraits for each character.
    Optionally saves a registry JSON for use with generate-storyboard.

    Example:
        aicp vimax generate-portraits --characters chars.json --output portraits/
        aicp vimax generate-portraits -c chars.json -o portraits/ --views front,side
    """
    from ..agents import CharacterPortraitsGenerator, PortraitsGeneratorConfig
    from ..interfaces import CharacterInNovel, CharacterPortraitRegistry

    click.echo("Generating character portraits...")
    click.echo(f"   Characters file: {characters}")
    click.echo(f"   Output: {output}")
    click.echo(f"   Image model: {image_model}")

    # Load characters
    with open(characters, 'r', encoding='utf-8') as f:
        char_data = json.load(f)

    # Handle both list and dict formats
    if isinstance(char_data, list):
        char_list = [CharacterInNovel(**c) for c in char_data[:max_characters]]
    else:
        char_list = [CharacterInNovel(**char_data)]

    click.echo(f"   Characters: {len(char_list)}")
    for char in char_list:
        click.echo(f"   - {char.name}")

    # Parse views
    view_list = [v.strip() for v in views.split(",")]
    click.echo(f"   Views: {', '.join(view_list)}")

    config = PortraitsGeneratorConfig(
        image_model=image_model,
        llm_model=llm_model,
        output_dir=output,
        views=view_list,
    )
    generator = CharacterPortraitsGenerator(config)

    async def run():
        result = await generator.generate_batch(char_list)
        return result.result if result.success else {}

    portraits = run_async(run())

    if portraits:
        click.echo("\nPortraits generated successfully!")
        total_images = 0
        for name, portrait in portraits.items():
            view_count = len(portrait.views)
            total_images += view_count
            click.echo(f"   {name}: {view_count} views")
            for view_name, path in portrait.views.items():
                click.echo(f"      - {view_name}: {path}")

        click.echo(f"\n   Total images: {total_images}")

        # Save registry if requested
        if save_registry:
            registry = CharacterPortraitRegistry(
                project_id=Path(output).name
            )
            for name, portrait in portraits.items():
                registry.add_portrait(portrait)

            registry_path = Path(output) / "portrait_registry.json"
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(registry_path, 'w') as f:
                json.dump(registry.to_dict(), f, indent=2)
            click.echo(f"   Registry saved: {registry_path}")
    else:
        click.echo("\nNo portraits generated!")


@vimax.command("create-registry")
@click.option("--portraits-dir", "-p", required=True, type=click.Path(exists=True), help="Directory with portrait images")
@click.option("--output", "-o", help="Output registry JSON file (default: portraits_dir/registry.json)")
@click.option("--project-id", default="project", help="Project identifier")
def create_registry(portraits_dir, output, project_id):
    """
    Create a portrait registry from existing portrait images.

    Expects portraits organized as: portraits_dir/character_name/view.png

    Example:
        aicp vimax create-registry --portraits-dir portraits/ --output registry.json
    """
    from ..interfaces import CharacterPortrait, CharacterPortraitRegistry

    portraits_path = Path(portraits_dir)
    output_path = Path(output) if output else portraits_path / "registry.json"

    click.echo("Creating portrait registry...")
    click.echo(f"   Source: {portraits_dir}")
    click.echo(f"   Output: {output_path}")

    registry = CharacterPortraitRegistry(project_id=project_id)

    # Scan for character directories
    for char_dir in portraits_path.iterdir():
        if not char_dir.is_dir():
            continue

        char_name = char_dir.name
        portrait = CharacterPortrait(character_name=char_name)

        # Look for view images
        for view_file in char_dir.glob("*.png"):
            view_name = view_file.stem.lower()
            if view_name in ["front", "side", "back", "three_quarter"]:
                setattr(portrait, f"{view_name}_view", str(view_file))

        # Also check for jpg
        for view_file in char_dir.glob("*.jpg"):
            view_name = view_file.stem.lower()
            if view_name in ["front", "side", "back", "three_quarter"]:
                setattr(portrait, f"{view_name}_view", str(view_file))

        if portrait.has_views:
            registry.add_portrait(portrait)
            click.echo(f"   Added: {char_name} ({len(portrait.views)} views)")

    if registry.portraits:
        with open(output_path, 'w') as f:
            json.dump(registry.to_dict(), f, indent=2)
        click.echo("\nRegistry created successfully!")
        click.echo(f"   Characters: {len(registry.portraits)}")
        click.echo(f"   Saved to: {output_path}")
    else:
        click.echo(f"\nNo portraits found in {portraits_dir}")


@vimax.command("show-registry")
@click.option("--registry", "-r", required=True, type=click.Path(exists=True), help="Registry JSON file")
def show_registry(registry):
    """
    Display contents of a portrait registry.

    Example:
        aicp vimax show-registry --registry portraits/registry.json
    """
    from ..interfaces import CharacterPortraitRegistry

    with open(registry, 'r', encoding='utf-8') as f:
        data = json.load(f)

    reg = CharacterPortraitRegistry.from_dict(data)

    click.echo(f"Portrait Registry: {reg.project_id}")
    click.echo(f"Characters: {len(reg.portraits)}\n")

    for name, portrait in reg.portraits.items():
        click.echo(f"{name}:")
        for view_name, path in portrait.views.items():
            click.echo(f"   {view_name}: {path}")
        click.echo()


@vimax.command("list-models")
def list_models():
    """List available models for ViMax pipelines.

    Usage: aicp vimax list-models
    """
    click.echo("Available Models for ViMax Pipelines (aicp vimax)\n")

    click.echo("Image Generation:")
    models = [
        ("nano_banana_pro", "Nano Banana Pro - Default, balanced", "$0.002"),
        ("flux_dev", "FLUX.1 Dev - High quality", "$0.003"),
        ("flux_schnell", "FLUX.1 Schnell - Fast", "$0.001"),
        ("imagen4", "Imagen 4 - Photorealistic", "$0.004"),
    ]
    for model, desc, cost in models:
        click.echo(f"   - {model}: {desc} ({cost})")

    click.echo("\nReference Image Models (for character consistency):")
    models = [
        ("nano_banana_pro", "Nano Banana Pro - Default, cost effective reference generation", "$0.002"),
        ("flux_kontext", "FLUX Kontext - High quality reference-based generation", "$0.025"),
        ("flux_redux", "FLUX Redux - Style transfer and variation", "$0.020"),
        ("seededit_v3", "SeedEdit v3 - Precise edits with reference", "$0.025"),
        ("photon_flash", "Photon Flash - Fast reference-based generation", "$0.015"),
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


def main():
    """Entry point for vimax CLI."""
    vimax()


# For standalone testing
if __name__ == "__main__":
    main()
