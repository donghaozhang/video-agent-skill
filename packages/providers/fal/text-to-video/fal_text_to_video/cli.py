#!/usr/bin/env python3
"""
CLI for FAL Text-to-Video Generation.

Usage:
    python -m fal_text_to_video.cli generate --prompt "A cat playing" --model kling_2_6_pro
    python -m fal_text_to_video.cli list-models
    python -m fal_text_to_video.cli model-info kling_2_6_pro
    python -m fal_text_to_video.cli estimate-cost --model sora_2_pro --duration 8 --resolution 1080p
"""

import argparse
import sys

from .generator import FALTextToVideoGenerator


def cmd_generate(args):
    """Generate video from text prompt."""
    generator = FALTextToVideoGenerator(default_model=args.model)

    mock_label = " [MOCK]" if args.mock else ""
    print(f"🎬 Generating video with {args.model}{mock_label}...")
    print(f"   Prompt: {args.prompt[:50]}{'...' if len(args.prompt) > 50 else ''}")

    # Build kwargs based on model
    kwargs = {}

    if args.model == "kling_2_6_pro":
        kwargs["duration"] = args.duration
        kwargs["aspect_ratio"] = args.aspect_ratio
        kwargs["cfg_scale"] = args.cfg_scale
        kwargs["generate_audio"] = args.audio
        if args.negative_prompt:
            kwargs["negative_prompt"] = args.negative_prompt

    elif args.model in ["sora_2", "sora_2_pro"]:
        kwargs["duration"] = int(args.duration) if args.duration else 4
        kwargs["aspect_ratio"] = args.aspect_ratio
        kwargs["delete_video"] = not args.keep_remote
        if args.model == "sora_2_pro" and args.resolution:
            kwargs["resolution"] = args.resolution

    result = generator.generate_video(
        prompt=args.prompt,
        model=args.model,
        output_dir=args.output,
        verbose=True,
        mock=args.mock,
        **kwargs
    )

    if result.get("success"):
        print(f"\n✅ Success{'  [MOCK - No actual API call]' if result.get('mock') else ''}!")
        print(f"   📁 Output: {result.get('local_path')}")
        if result.get('mock'):
            print(f"   💰 Estimated cost: ${result.get('estimated_cost', 0):.2f} (not charged)")
        else:
            print(f"   💰 Cost: ${result.get('cost_usd', 0):.2f}")
            print(f"   🔗 URL: {result.get('video_url', 'N/A')}")
        return 0
    else:
        print(f"\n❌ Failed: {result.get('error')}")
        return 1


def cmd_list_models(args):
    """List available models."""
    generator = FALTextToVideoGenerator()

    print("📋 Available Text-to-Video Models:")
    print("=" * 60)

    comparison = generator.compare_models()
    for model_key, info in comparison.items():
        print(f"\n🎥 {info['name']} ({model_key})")
        print(f"   Provider: {info['provider']}")
        print(f"   Max duration: {info['max_duration']}s")
        print(f"   Pricing: {info['pricing']}")
        print(f"   Features: {', '.join(info['features'])}")

    return 0


def cmd_model_info(args):
    """Show detailed model information."""
    generator = FALTextToVideoGenerator()

    try:
        info = generator.get_model_info(args.model)

        print(f"\n📋 Model: {info.get('name', args.model)}")
        print("=" * 50)
        print(f"Provider: {info.get('provider', 'Unknown')}")
        print(f"Description: {info.get('description', 'N/A')}")
        print(f"Endpoint: {info.get('endpoint', 'N/A')}")
        print(f"Max duration: {info.get('max_duration', 'N/A')}s")

        print(f"\nFeatures:")
        for feature in info.get('features', []):
            print(f"   • {feature}")

        print(f"\nPricing:")
        pricing = info.get('pricing', {})
        for key, value in pricing.items():
            print(f"   • {key}: ${value}")

        return 0
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_estimate_cost(args):
    """Estimate cost for video generation."""
    generator = FALTextToVideoGenerator()

    try:
        kwargs = {}

        if args.model == "kling_2_6_pro":
            kwargs["duration"] = args.duration
            kwargs["generate_audio"] = args.audio

        elif args.model in ["sora_2", "sora_2_pro"]:
            kwargs["duration"] = int(args.duration) if args.duration else 4
            if args.model == "sora_2_pro" and args.resolution:
                kwargs["resolution"] = args.resolution

        cost = generator.estimate_cost(model=args.model, **kwargs)

        print(f"\n💰 Cost Estimate for {args.model}:")
        print(f"   Estimated cost: ${cost:.2f}")
        print(f"   Parameters: {kwargs}")

        return 0
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FAL Text-to-Video CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate video with Kling v2.6 Pro
  python -m fal_text_to_video.cli generate \\
    --prompt "A cat playing with a ball of yarn" \\
    --model kling_2_6_pro \\
    --duration 5 \\
    --audio

  # Generate video with Sora 2
  python -m fal_text_to_video.cli generate \\
    --prompt "A beautiful sunset over mountains" \\
    --model sora_2 \\
    --duration 8

  # Generate video with Sora 2 Pro (1080p)
  python -m fal_text_to_video.cli generate \\
    --prompt "Cinematic shot of a futuristic city" \\
    --model sora_2_pro \\
    --duration 12 \\
    --resolution 1080p

  # List available models
  python -m fal_text_to_video.cli list-models

  # Show model info
  python -m fal_text_to_video.cli model-info sora_2_pro

  # Estimate cost
  python -m fal_text_to_video.cli estimate-cost \\
    --model sora_2_pro \\
    --duration 8 \\
    --resolution 1080p
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate video from text")
    gen_parser.add_argument("--prompt", "-p", required=True,
                           help="Text prompt for video generation")
    gen_parser.add_argument("--model", "-m", default="kling_2_6_pro",
                           choices=["kling_2_6_pro", "sora_2", "sora_2_pro"],
                           help="Model to use (default: kling_2_6_pro)")
    gen_parser.add_argument("--duration", "-d", default="5",
                           help="Video duration (default: 5)")
    gen_parser.add_argument("--aspect-ratio", "-a", default="16:9",
                           choices=["16:9", "9:16", "1:1"],
                           help="Aspect ratio (default: 16:9)")
    gen_parser.add_argument("--resolution", "-r", default="720p",
                           choices=["720p", "1080p"],
                           help="Resolution for Sora 2 Pro (default: 720p)")
    gen_parser.add_argument("--output", "-o", default="output",
                           help="Output directory")
    gen_parser.add_argument("--negative-prompt", help="Negative prompt (Kling only)")
    gen_parser.add_argument("--cfg-scale", type=float, default=0.5,
                           help="CFG scale 0-1 (Kling only)")
    gen_parser.add_argument("--audio", action="store_true",
                           help="Generate audio (Kling only)")
    gen_parser.add_argument("--keep-remote", action="store_true",
                           help="Keep video on remote server (Sora only)")
    gen_parser.add_argument("--mock", action="store_true",
                           help="Mock mode: simulate API call without actual generation (FREE)")
    gen_parser.set_defaults(func=cmd_generate)

    # List models command
    list_parser = subparsers.add_parser("list-models", help="List available models")
    list_parser.set_defaults(func=cmd_list_models)

    # Model info command
    info_parser = subparsers.add_parser("model-info", help="Show model information")
    info_parser.add_argument("model", choices=["kling_2_6_pro", "sora_2", "sora_2_pro"],
                            help="Model key")
    info_parser.set_defaults(func=cmd_model_info)

    # Estimate cost command
    cost_parser = subparsers.add_parser("estimate-cost", help="Estimate generation cost")
    cost_parser.add_argument("--model", "-m", default="kling_2_6_pro",
                            choices=["kling_2_6_pro", "sora_2", "sora_2_pro"],
                            help="Model to estimate (default: kling_2_6_pro)")
    cost_parser.add_argument("--duration", "-d", default="5",
                            help="Video duration")
    cost_parser.add_argument("--resolution", "-r", default="720p",
                            choices=["720p", "1080p"],
                            help="Resolution (Sora 2 Pro only)")
    cost_parser.add_argument("--audio", action="store_true",
                            help="Include audio (Kling only)")
    cost_parser.set_defaults(func=cmd_estimate_cost)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
