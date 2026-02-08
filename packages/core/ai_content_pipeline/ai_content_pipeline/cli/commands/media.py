"""
Media CLI commands.

Commands: generate-avatar, list-avatar-models, analyze-video, list-video-models.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import click

from ..exit_codes import error_exit


def _check_save_json_deprecation(save_json, output):
    """Emit deprecation warning if --save-json is used."""
    if save_json:
        output.warning(
            "--save-json is deprecated and will be removed in a future release. "
            "Use '--json' to emit structured output to stdout, then redirect: "
            "aicp <command> --json > result.json"
        )


@click.command("generate-avatar")
@click.option("--image-url", default=None, help="Portrait image URL for avatar generation")
@click.option("--audio-url", default=None, help="Audio URL for lipsync (use with --image-url)")
@click.option("--text", default=None, help="Text for TTS avatar (use with --image-url)")
@click.option("--video-url", default=None, help="Video URL for transformation")
@click.option("--reference-images", multiple=True, help="Reference images for video generation (max 4)")
@click.option("--prompt", default=None, help="Prompt for generation/transformation")
@click.option("--model", default=None, help="Model to use (default: auto-selected based on inputs)")
@click.option("--duration", default="5", help="Video duration in seconds")
@click.option("--aspect-ratio", default="16:9", help="Aspect ratio")
@click.option("--save-json", default=None, help="Save result as JSON")
@click.pass_context
def generate_avatar_cmd(ctx, image_url, audio_url, text, video_url,
                        reference_images, prompt, model, duration, aspect_ratio, save_json):
    """Generate avatar/lipsync video."""
    output = ctx.obj["output"]

    try:
        from fal_avatar import FALAvatarGenerator
    except ImportError:
        error_exit(ImportError(
            "FAL Avatar module not available. "
            "Ensure fal_avatar package is in path and fal-client is installed."
        ))

    _check_save_json_deprecation(save_json, output)

    try:
        generator = FALAvatarGenerator()

        if video_url:
            output.info(f"Transforming video with model: {model or 'auto'}")
            mode = "edit" if model == "kling_v2v_edit" else "reference"
            result = generator.transform_video(
                video_url=video_url,
                prompt=prompt or "Transform this video",
                mode=mode,
            )
        elif reference_images:
            output.info(f"Generating video from {len(reference_images)} reference images")
            result = generator.generate_reference_video(
                prompt=prompt or "Generate a video with these references",
                reference_images=list(reference_images),
                duration=duration,
                aspect_ratio=aspect_ratio,
            )
        elif image_url:
            if text and not audio_url:
                model = model or "fabric_1_0_text"
                output.info(f"Generating TTS avatar with model: {model}")
            else:
                model = model or "omnihuman_v1_5"
                output.info(f"Generating lipsync avatar with model: {model}")

            result = generator.generate_avatar(
                image_url=image_url,
                audio_url=audio_url,
                text=text,
                model=model,
            )
        else:
            error_exit(ValueError("No input provided. Use --image-url, --video-url, or --reference-images."))

        result_dict = {
            "success": result.success,
            "model": result.model_used,
            "video_url": result.video_url,
            "duration": result.duration,
            "cost": result.cost,
            "processing_time": result.processing_time,
            "error": result.error,
            "metadata": result.metadata,
        }

        if output.json_mode:
            output.result(result_dict, command="generate-avatar")
        elif result.success:
            output.info("\nAvatar generation successful!")
            output.info(f"Model: {result.model_used}")
            if result.video_url:
                output.info(f"Video URL: {result.video_url}")
            if result.duration:
                output.info(f"Duration: {result.duration:.1f} seconds")
            if result.cost:
                output.info(f"Cost: ${result.cost:.3f}")
            if result.processing_time:
                output.info(f"Processing time: {result.processing_time:.1f} seconds")
        else:
            output.error(f"Avatar generation failed: {result.error}")

        if save_json:
            json_path = Path(save_json)
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            output.info(f"\nResult saved to: {json_path}")

    except Exception as e:
        error_exit(e, debug=ctx.obj["debug"])


@click.command("list-avatar-models")
@click.pass_context
def list_avatar_models_cmd(ctx):
    """List available avatar generation models."""
    output = ctx.obj["output"]

    try:
        from fal_avatar import FALAvatarGenerator
    except ImportError:
        output.error("FAL Avatar module not available. Ensure fal_avatar package is in path and fal-client is installed.")
        sys.exit(1)

    generator = FALAvatarGenerator()
    categories = generator.list_models_by_category()

    if output.json_mode:
        rows = []
        for category, models in categories.items():
            for model in models:
                info = generator.get_model_info(model)
                rows.append({"category": category, "model": model, **info})
        output.table(rows, command="list-avatar-models")
        return

    output.info("\nFAL Avatar Generation Models")
    output.info("=" * 50)

    for category, models in categories.items():
        output.info(f"\n{category.replace('_', ' ').title()}")
        for model in models:
            info = generator.get_model_info(model)
            display_name = generator.get_display_name(model)
            output.info(f"   {model}")
            output.info(f"     Name: {display_name}")
            output.info(f"     Best for: {', '.join(info.get('best_for', []))}")
            if 'pricing' in info:
                pricing = info['pricing']
                if 'per_second' in pricing:
                    output.info(f"     Cost: ${pricing['per_second']}/second")
                elif '720p' in pricing:
                    output.info(f"     Cost: ${pricing.get('480p', 'N/A')}/s (480p), ${pricing.get('720p', 'N/A')}/s (720p)")


@click.command("analyze-video")
@click.option("-i", "--input", "input_path", required=True, help="Input video file or directory")
@click.option("-o", "--output", "output_dir", default="output", help="Output directory")
@click.option("-m", "--model", default="gemini-3-pro", help="Model to use")
@click.option("-t", "--type", "analysis_type", default="timeline", help="Analysis type")
@click.option("-f", "--format", "output_format", default="both",
              type=click.Choice(["md", "json", "both"]), help="Output format")
@click.pass_context
def analyze_video_cmd(ctx, input_path, output_dir, model, analysis_type, output_format):
    """Analyze video content using AI (Gemini via FAL/Direct)."""
    from ...video_analysis import analyze_video_command, MODEL_MAP, ANALYSIS_TYPES

    # Build args namespace for the existing handler
    args = SimpleNamespace(
        input=input_path,
        output=output_dir,
        model=model,
        type=analysis_type,
        format=output_format,
        debug=ctx.obj["debug"],
    )
    analyze_video_command(args)


@click.command("list-video-models")
def list_video_models_cmd():
    """List available video analysis models."""
    from ...video_analysis import list_video_models
    list_video_models()


def register_media_commands(group):
    """Register all media commands with the CLI group."""
    group.add_command(generate_avatar_cmd)
    group.add_command(list_avatar_models_cmd)
    group.add_command(analyze_video_cmd)
    group.add_command(list_video_models_cmd)
