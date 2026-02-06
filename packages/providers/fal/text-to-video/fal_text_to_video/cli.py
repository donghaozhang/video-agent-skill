#!/usr/bin/env python3
"""
CLI for FAL Text-to-Video Generation.

Usage:
    fal-text-to-video generate --prompt "A cat playing" --model kling_2_6_pro
    fal-text-to-video list-models
    fal-text-to-video model-info kling_2_6_pro
    fal-text-to-video estimate-cost --model sora_2_pro --duration 8 --resolution 1080p
"""

import sys

import click

from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # side-effect: registers models

from .generator import FALTextToVideoGenerator

T2V_MODELS = ModelRegistry.keys_for_category("text_to_video")


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """FAL Text-to-Video Generation CLI."""
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())


@cli.command()
@click.option("--prompt", "-p", required=True, help="Text prompt for video generation")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(T2V_MODELS, case_sensitive=True),
              help="Model to use (default: kling_2_6_pro)")
@click.option("--duration", "-d", default=None, help="Video duration (default: model-specific)")
@click.option("--aspect-ratio", "-a", default="16:9",
              type=click.Choice(["16:9", "9:16", "1:1", "4:3", "3:2", "2:3", "3:4"]),
              help="Aspect ratio (default: 16:9)")
@click.option("--resolution", "-r", default="720p",
              type=click.Choice(["480p", "720p", "1080p"]),
              help="Resolution (default: 720p)")
@click.option("--output", "-o", default="output", help="Output directory")
@click.option("--negative-prompt", default=None, help="Negative prompt (Kling only)")
@click.option("--cfg-scale", type=float, default=0.5, help="CFG scale 0-1 (Kling only)")
@click.option("--audio", is_flag=True, help="Generate audio (Kling only)")
@click.option("--keep-remote", is_flag=True, help="Keep video on remote server (Sora only)")
@click.option("--mock", is_flag=True, help="Mock mode: simulate without API call (FREE)")
def generate(prompt, model, duration, aspect_ratio, resolution, output,
             negative_prompt, cfg_scale, audio, keep_remote, mock):
    """Generate video from text prompt."""
    generator = FALTextToVideoGenerator(default_model=model)

    mock_label = " [MOCK]" if mock else ""
    print(f"\U0001f3ac Generating video with {model}{mock_label}...")
    print(f"   Prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

    kwargs = {}

    model_def = ModelRegistry.get(model)
    if duration:
        kwargs["duration"] = duration
    else:
        kwargs["duration"] = model_def.defaults.get("duration", "5")
    kwargs["aspect_ratio"] = aspect_ratio
    if cfg_scale is not None:
        kwargs["cfg_scale"] = cfg_scale
    if audio:
        kwargs["generate_audio"] = True
    if negative_prompt:
        kwargs["negative_prompt"] = negative_prompt
    if resolution:
        kwargs["resolution"] = resolution
    if keep_remote:
        kwargs["delete_video"] = False

    result = generator.generate_video(
        prompt=prompt,
        model=model,
        output_dir=output,
        verbose=True,
        mock=mock,
        **kwargs
    )

    if result.get("success"):
        print(f"\n\u2705 Success{'  [MOCK - No actual API call]' if result.get('mock') else ''}!")
        print(f"   \U0001f4c1 Output: {result.get('local_path')}")
        if result.get('mock'):
            print(f"   \U0001f4b0 Estimated cost: ${result.get('estimated_cost', 0):.2f} (not charged)")
        else:
            print(f"   \U0001f4b0 Cost: ${result.get('cost_usd', 0):.2f}")
            print(f"   \U0001f517 URL: {result.get('video_url', 'N/A')}")
        sys.exit(0)
    else:
        print(f"\n\u274c Failed: {result.get('error')}")
        sys.exit(1)


@cli.command("list-models")
def list_models():
    """List available text-to-video models."""
    generator = FALTextToVideoGenerator()

    print("\U0001f4cb Available Text-to-Video Models:")
    print("=" * 60)

    comparison = generator.compare_models()
    for model_key, info in comparison.items():
        print(f"\n\U0001f3a5 {info['name']} ({model_key})")
        print(f"   Provider: {info['provider']}")
        print(f"   Max duration: {info['max_duration']}s")
        print(f"   Pricing: {info['pricing']}")
        print(f"   Features: {', '.join(info['features'])}")


@cli.command("model-info")
@click.argument("model", type=click.Choice(T2V_MODELS, case_sensitive=True))
def model_info(model):
    """Show detailed model information."""
    generator = FALTextToVideoGenerator()

    try:
        info = generator.get_model_info(model)

        print(f"\n\U0001f4cb Model: {info.get('name', model)}")
        print("=" * 50)
        print(f"Provider: {info.get('provider', 'Unknown')}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Endpoint: {info.get('endpoint', 'N/A')}")
        print(f"Max duration: {info.get('max_duration', 'N/A')}s")

        print("\nFeatures:")
        for feature in info.get('features', []):
            print(f"   \u2022 {feature}")

        print("\nPricing:")
        pricing = info.get('pricing', {})
        for key, value in pricing.items():
            print(f"   \u2022 {key}: ${value}")

    except ValueError as e:
        print(f"\u274c Error: {e}")
        sys.exit(1)


@cli.command("estimate-cost")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(T2V_MODELS, case_sensitive=True),
              help="Model to estimate (default: kling_2_6_pro)")
@click.option("--duration", "-d", default=None, help="Video duration (default: model-specific)")
@click.option("--resolution", "-r", default="720p",
              type=click.Choice(["720p", "1080p"]),
              help="Resolution (Sora 2 Pro only)")
@click.option("--audio", is_flag=True, help="Include audio (Kling only)")
def estimate_cost(model, duration, resolution, audio):
    """Estimate cost for video generation."""
    generator = FALTextToVideoGenerator()

    try:
        kwargs = {}

        model_def = ModelRegistry.get(model)
        if duration:
            kwargs["duration"] = duration
        else:
            kwargs["duration"] = model_def.defaults.get("duration", "5")
        if audio:
            kwargs["generate_audio"] = True
        if resolution:
            kwargs["resolution"] = resolution

        cost = generator.estimate_cost(model=model, **kwargs)

        print(f"\n\U0001f4b0 Cost Estimate for {model}:")
        print(f"   Estimated cost: ${cost:.2f}")
        print(f"   Parameters: {kwargs}")

    except ValueError as e:
        print(f"\u274c Error: {e}")
        sys.exit(1)


def main():
    """Entry point for console_scripts."""
    cli()


if __name__ == "__main__":
    main()
