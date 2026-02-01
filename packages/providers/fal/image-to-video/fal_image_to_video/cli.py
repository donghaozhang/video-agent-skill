#!/usr/bin/env python3
"""
CLI for FAL Image-to-Video Generation.

Usage:
    python -m fal_image_to_video.cli generate --image path/to/image.png --model kling_2_6_pro --prompt "..."
    python -m fal_image_to_video.cli list-models
    python -m fal_image_to_video.cli model-info kling_2_6_pro
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .generator import FALImageToVideoGenerator


def cmd_generate(args):
    """Generate video from image."""
    generator = FALImageToVideoGenerator()

    # Determine image source
    image_url = args.image
    start_frame = None

    # If it's a local file path, pass it via start_frame parameter.
    # The generator will upload the local file and use it as the image source.
    # image_url is ignored when start_frame is provided (see generator.py:141-153).
    if not image_url.startswith(('http://', 'https://')):
        start_frame = image_url
        image_url = None

    print(f"🎬 Generating video with {args.model}...")
    print(f"   Image: {args.image}")
    print(f"   Duration: {args.duration}")
    if args.end_frame:
        print(f"   End frame: {args.end_frame}")

    result = generator.generate_video(
        prompt=args.prompt,
        image_url=image_url,
        model=args.model,
        start_frame=start_frame,
        end_frame=args.end_frame,
        duration=args.duration,
        output_dir=args.output,
        negative_prompt=args.negative_prompt,
        cfg_scale=args.cfg_scale if hasattr(args, 'cfg_scale') else None,
        generate_audio=args.audio if hasattr(args, 'audio') else None,
    )

    if result.get("success"):
        print(f"\n✅ Success!")
        print(f"   📁 Output: {result.get('local_path')}")
        print(f"   💰 Cost: ${result.get('cost_estimate', 0):.2f}")
        print(f"   ⏱️ Time: {result.get('processing_time', 0):.1f}s")
        return 0
    else:
        print(f"\n❌ Failed: {result.get('error')}")
        return 1


def cmd_interpolate(args):
    """Generate video interpolating between two frames."""
    generator = FALImageToVideoGenerator()

    print(f"🎬 Generating interpolation video...")
    print(f"   Start frame: {args.start_frame}")
    print(f"   End frame: {args.end_frame}")
    print(f"   Model: {args.model}")

    result = generator.generate_with_interpolation(
        prompt=args.prompt,
        start_frame=args.start_frame,
        end_frame=args.end_frame,
        model=args.model,
        duration=args.duration,
    )

    if result.get("success"):
        print(f"\n✅ Success!")
        print(f"   📁 Output: {result.get('local_path')}")
        print(f"   💰 Cost: ${result.get('cost_estimate', 0):.2f}")
        return 0
    else:
        print(f"\n❌ Failed: {result.get('error')}")
        return 1


def cmd_list_models(args):
    """List available models."""
    generator = FALImageToVideoGenerator()

    print("📋 Available Image-to-Video Models:")
    print("=" * 60)

    comparison = generator.compare_models()
    for model_key, info in comparison.items():
        print(f"\n🎥 {info['name']} ({model_key})")
        print(f"   Provider: {info['provider']}")
        print(f"   Price: ${info['price_per_second']:.2f}/second")
        print(f"   Max duration: {info['max_duration']}s")
        print(f"   Features: {', '.join(info['features'])}")

    return 0


def cmd_model_info(args):
    """Show detailed model information."""
    generator = FALImageToVideoGenerator()

    try:
        info = generator.get_model_info(args.model)
        features = generator.get_model_features(args.model)

        print(f"\n📋 Model: {info.get('name', args.model)}")
        print("=" * 50)
        print(f"Provider: {info.get('provider', 'Unknown')}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Endpoint: {info.get('endpoint', 'N/A')}")
        print(f"Price: ${info.get('price_per_second', 0):.2f}/second")
        print(f"Max duration: {info.get('max_duration', 'N/A')}s")

        print(f"\nFeatures:")
        for feature in info.get('features', []):
            print(f"   • {feature}")

        print(f"\nExtended Parameters:")
        for param, supported in features.items():
            status = "✅" if supported else "❌"
            print(f"   {status} {param}")

        return 0
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FAL Image-to-Video CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate video from local image
  python -m fal_image_to_video.cli generate \\
    --image output/beach.png \\
    --model kling_2_6_pro \\
    --prompt "Woman walks on beach" \\
    --duration 5

  # Generate with frame interpolation
  python -m fal_image_to_video.cli interpolate \\
    --start-frame start.png \\
    --end-frame end.png \\
    --model kling_2_6_pro \\
    --prompt "Smooth transition"

  # List available models
  python -m fal_image_to_video.cli list-models

  # Show model info
  python -m fal_image_to_video.cli model-info kling_2_6_pro
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate video from image")
    gen_parser.add_argument("--image", "-i", required=True, help="Input image path or URL")
    gen_parser.add_argument("--model", "-m", default="kling_2_6_pro",
                           choices=["hailuo", "kling_2_1", "kling_2_6_pro",
                                   "seedance_1_5_pro", "sora_2", "sora_2_pro",
                                   "veo_3_1_fast", "wan_2_6", "grok_imagine"],
                           help="Model to use (default: kling_2_6_pro)")
    gen_parser.add_argument("--prompt", "-p", required=True, help="Text prompt for video generation")
    gen_parser.add_argument("--duration", "-d", default="5", help="Video duration (default: 5)")
    gen_parser.add_argument("--output", "-o", default="output", help="Output directory")
    gen_parser.add_argument("--end-frame", help="End frame for interpolation (Kling only)")
    gen_parser.add_argument("--negative-prompt", default="blur, distortion, low quality",
                           help="Negative prompt")
    gen_parser.add_argument("--cfg-scale", type=float, default=0.5, help="CFG scale (0-1)")
    gen_parser.add_argument("--audio", action="store_true", help="Generate audio (Veo only)")
    gen_parser.set_defaults(func=cmd_generate)

    # Interpolate command
    interp_parser = subparsers.add_parser("interpolate", help="Generate video interpolating between frames")
    interp_parser.add_argument("--start-frame", "-s", required=True, help="Start frame image")
    interp_parser.add_argument("--end-frame", "-e", required=True, help="End frame image")
    interp_parser.add_argument("--model", "-m", default="kling_2_6_pro",
                              choices=["kling_2_1", "kling_2_6_pro"],
                              help="Model (Kling only)")
    interp_parser.add_argument("--prompt", "-p", required=True, help="Text prompt")
    interp_parser.add_argument("--duration", "-d", default="5", help="Duration")
    interp_parser.set_defaults(func=cmd_interpolate)

    # List models command
    list_parser = subparsers.add_parser("list-models", help="List available models")
    list_parser.set_defaults(func=cmd_list_models)

    # Model info command
    info_parser = subparsers.add_parser("model-info", help="Show model information")
    info_parser.add_argument("model", help="Model key")
    info_parser.set_defaults(func=cmd_model_info)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
