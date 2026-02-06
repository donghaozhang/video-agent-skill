#!/usr/bin/env python3
"""
CLI for FAL Image-to-Video Generation.

Usage:
    fal-image-to-video generate --image path/to/image.png --model kling_2_6_pro --prompt "..."
    fal-image-to-video interpolate --start-frame start.png --end-frame end.png --prompt "..."
    fal-image-to-video list-models
    fal-image-to-video model-info kling_2_6_pro
"""

import sys

import click

from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # side-effect: registers models

from .generator import FALImageToVideoGenerator

I2V_MODELS = ModelRegistry.provider_keys_for_category("image_to_video")


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """FAL Image-to-Video Generation CLI."""
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())


@cli.command()
@click.option("--image", "-i", required=True, help="Input image path or URL")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(I2V_MODELS, case_sensitive=True),
              help="Model to use (default: kling_2_6_pro)")
@click.option("--prompt", "-p", required=True, help="Text prompt for video generation")
@click.option("--duration", "-d", default="5", help="Video duration (default: 5)")
@click.option("--output", "-o", default="output", help="Output directory")
@click.option("--end-frame", default=None, help="End frame for interpolation (Kling only)")
@click.option("--negative-prompt", default="blur, distortion, low quality", help="Negative prompt")
@click.option("--cfg-scale", type=float, default=0.5, help="CFG scale (0-1)")
@click.option("--audio", is_flag=True, help="Generate audio (Veo only)")
def generate(image, model, prompt, duration, output, end_frame,
             negative_prompt, cfg_scale, audio):
    """Generate video from image."""
    generator = FALImageToVideoGenerator()

    # Determine image source
    image_url = image
    start_frame = None

    # If it's a local file path, pass it via start_frame parameter.
    # The generator will upload the local file and use it as the image source.
    # image_url is ignored when start_frame is provided (see generator.py:141-153).
    if not image_url.startswith(('http://', 'https://')):
        start_frame = image_url
        image_url = None

    print(f"\U0001f3ac Generating video with {model}...")
    print(f"   Image: {image}")
    print(f"   Duration: {duration}")
    if end_frame:
        print(f"   End frame: {end_frame}")

    result = generator.generate_video(
        prompt=prompt,
        image_url=image_url,
        model=model,
        start_frame=start_frame,
        end_frame=end_frame,
        duration=duration,
        output_dir=output,
        negative_prompt=negative_prompt,
        cfg_scale=cfg_scale,
        generate_audio=audio if audio else None,
    )

    if result.get("success"):
        print(f"\n\u2705 Success!")
        print(f"   \U0001f4c1 Output: {result.get('local_path')}")
        print(f"   \U0001f4b0 Cost: ${result.get('cost_estimate', 0):.2f}")
        print(f"   \u23f1\ufe0f Time: {result.get('processing_time', 0):.1f}s")
        sys.exit(0)
    else:
        print(f"\n\u274c Failed: {result.get('error')}")
        sys.exit(1)


@cli.command()
@click.option("--start-frame", "-s", required=True, help="Start frame image")
@click.option("--end-frame", "-e", required=True, help="End frame image")
@click.option("--model", "-m", default="kling_2_6_pro",
              type=click.Choice(["kling_2_1", "kling_2_6_pro", "kling_3_standard", "kling_3_pro"]),
              help="Model for interpolation (Kling only)")
@click.option("--prompt", "-p", required=True, help="Text prompt")
@click.option("--duration", "-d", default="5", help="Duration")
def interpolate(start_frame, end_frame, model, prompt, duration):
    """Generate video interpolating between two frames."""
    generator = FALImageToVideoGenerator()

    print(f"\U0001f3ac Generating interpolation video...")
    print(f"   Start frame: {start_frame}")
    print(f"   End frame: {end_frame}")
    print(f"   Model: {model}")

    result = generator.generate_with_interpolation(
        prompt=prompt,
        start_frame=start_frame,
        end_frame=end_frame,
        model=model,
        duration=duration,
    )

    if result.get("success"):
        print(f"\n\u2705 Success!")
        print(f"   \U0001f4c1 Output: {result.get('local_path')}")
        print(f"   \U0001f4b0 Cost: ${result.get('cost_estimate', 0):.2f}")
        sys.exit(0)
    else:
        print(f"\n\u274c Failed: {result.get('error')}")
        sys.exit(1)


@cli.command("list-models")
def list_models():
    """List available image-to-video models."""
    generator = FALImageToVideoGenerator()

    print("\U0001f4cb Available Image-to-Video Models:")
    print("=" * 60)

    comparison = generator.compare_models()
    for model_key, info in comparison.items():
        print(f"\n\U0001f3a5 {info['name']} ({model_key})")
        print(f"   Provider: {info['provider']}")
        # Handle both simple float and dict pricing structures
        price = info['price_per_second']
        if isinstance(price, dict):
            prices = [f"{k}: ${v:.3f}" for k, v in price.items() if isinstance(v, (int, float))]
            if prices:
                print(f"   Price: {' / '.join(prices)}/second")
            else:
                print(f"   Price: see model details")
        else:
            print(f"   Price: ${price:.2f}/second")
        print(f"   Max duration: {info['max_duration']}s")
        print(f"   Features: {', '.join(info['features'])}")


@cli.command("model-info")
@click.argument("model")
def model_info(model):
    """Show detailed model information."""
    generator = FALImageToVideoGenerator()

    try:
        info = generator.get_model_info(model)
        features = generator.get_model_features(model)

        print(f"\n\U0001f4cb Model: {info.get('name', model)}")
        print("=" * 50)
        print(f"Provider: {info.get('provider', 'Unknown')}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Endpoint: {info.get('endpoint', 'N/A')}")
        # Handle both simple float and dict pricing structures
        price = info.get('price_per_second', 0)
        if isinstance(price, dict):
            print("Pricing (per second):")
            for tier, cost in price.items():
                if isinstance(cost, (int, float)):
                    print(f"   - {tier}: ${cost:.3f}")
        else:
            print(f"Price: ${price:.2f}/second")
        print(f"Max duration: {info.get('max_duration', 'N/A')}s")

        print(f"\nFeatures:")
        for feature in info.get('features', []):
            print(f"   \u2022 {feature}")

        print(f"\nExtended Parameters:")
        for param, supported in features.items():
            status = "\u2705" if supported else "\u274c"
            print(f"   {status} {param}")

    except ValueError as e:
        print(f"\u274c Error: {e}")
        sys.exit(1)


def main():
    """Entry point for console_scripts."""
    cli()


if __name__ == "__main__":
    main()
