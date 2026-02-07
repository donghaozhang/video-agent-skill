#!/usr/bin/env python3
"""
AI Content Pipeline CLI Interface

Allows running the module directly from command line:
    python -m ai_content_pipeline [command] [options]
"""

import argparse
import sys
import os
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

from .pipeline.manager import AIPipelineManager
from .config.constants import SUPPORTED_MODELS, MODEL_RECOMMENDATIONS
from .cli.exit_codes import error_exit, EXIT_INVALID_ARGS, EXIT_MISSING_CONFIG
from .cli.interactive import confirm, is_interactive
from .cli.output import CLIOutput, read_input

# Try to import FAL Avatar Generator
try:
    from fal_avatar import FALAvatarGenerator
    FAL_AVATAR_AVAILABLE = True
except ImportError:
    FAL_AVATAR_AVAILABLE = False

# Import video analysis module
from .video_analysis import (
    analyze_video_command,
    list_video_models,
    MODEL_MAP as VIDEO_MODEL_MAP,
    ANALYSIS_TYPES as VIDEO_ANALYSIS_TYPES,
)

# Import motion transfer module
from .motion_transfer import (
    transfer_motion_command,
    list_motion_models,
    ORIENTATION_OPTIONS,
)

# Import speech-to-text module
from .speech_to_text import (
    transcribe_command,
    list_speech_models,
)

# Import grid generator module
from .grid_generator import (
    generate_grid_command,
    upscale_image_command,
    GRID_CONFIGS,
    UPSCALE_TARGETS,
)

# Import project structure CLI commands
from .project_structure_cli import (
    init_project_command,
    organize_project_command,
    structure_info_command,
)


def _check_save_json_deprecation(args, output):
    """Emit deprecation warning if --save-json is used."""
    if getattr(args, 'save_json', None):
        output.warning(
            "--save-json is deprecated and will be removed in a future release. "
            "Use '--json' to emit structured output to stdout, then redirect: "
            "aicp <command> --json > result.json"
        )


def print_models(output):
    """Print information about all supported models."""
    output.info("\n🎨 AI Content Pipeline Supported Models")
    output.info("=" * 50)
    
    manager = AIPipelineManager(quiet=True)
    available_models = manager.get_available_models()

    if output.json_mode:
        output.table(
            [{"category": k, "models": v} for k, v in available_models.items()],
            command="list-models",
        )
        return

    for step_type, models in available_models.items():
        output.info(f"\n📦 {step_type.replace('_', '-').title()}")

        if models:
            for model in models:
                if step_type == "text_to_image":
                    info = manager.text_to_image.get_model_info(model)
                    output.info(f"   • {model}")
                    if info:
                        output.info(f"     Name: {info.get('name', 'N/A')}")
                        output.info(f"     Provider: {info.get('provider', 'N/A')}")
                        output.info(f"     Best for: {info.get('best_for', 'N/A')}")
                        output.info(f"     Cost: {info.get('cost_per_image', 'N/A')}")
                else:
                    output.info(f"   • {model}")
        else:
            output.info("   No models available (integration pending)")


def setup_env(args, output):
    """Handle setup command to create .env file."""
    env_path = Path(args.output_dir) / ".env" if args.output_dir else Path(".env")
    env_example_path = Path(__file__).parent.parent.parent.parent.parent / ".env.example"
    
    # Check if .env.example exists in the package
    if not env_example_path.exists():
        # Create a basic .env template
        template_content = """# AI Content Pipeline - Environment Configuration
# Add your API keys below

# Required for most functionality
FAL_KEY=your_fal_api_key_here

# Optional - add as needed
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Get API keys from:
# FAL AI: https://fal.ai/dashboard
# Google Gemini: https://makersuite.google.com/app/apikey
# OpenRouter: https://openrouter.ai/keys
# ElevenLabs: https://elevenlabs.io/app/settings
"""
    else:
        with open(env_example_path, 'r') as f:
            template_content = f.read()
    
    if env_path.exists():
        if not confirm(f".env file already exists at {env_path}. Overwrite?"):
            output.info("Setup cancelled.")
            return

    try:
        with open(env_path, 'w') as f:
            f.write(template_content)
        output.info(f"✅ Created .env file at {env_path}")
        output.info("📝 Please edit the file and add your API keys:")
        output.info(f"   nano {env_path}")
        output.info("\n🔑 Get your API keys from:")
        output.info("   • FAL AI: https://fal.ai/dashboard")
        output.info("   • Google Gemini: https://makersuite.google.com/app/apikey")
        output.info("   • OpenRouter: https://openrouter.ai/keys")
        output.info("   • ElevenLabs: https://elevenlabs.io/app/settings")
    except Exception as e:
        output.error(f"Error creating .env file: {e}")


def create_video(args, output):
    """Handle create-video command."""
    _check_save_json_deprecation(args, output)
    quiet = getattr(args, 'json', False) or getattr(args, 'quiet', False)
    try:
        manager = AIPipelineManager(args.base_dir, quiet=quiet)

        # Resolve input text
        text = args.text
        if getattr(args, 'input', None):
            text = read_input(args.input, fallback=text)

        # Create quick video chain
        result = manager.quick_create_video(
            text=text,
            image_model=args.image_model,
            video_model=args.video_model,
            output_dir=args.output_dir
        )

        # Build result dict for JSON or save-json
        result_dict = {
            "success": result.success,
            "steps_completed": result.steps_completed,
            "total_steps": result.total_steps,
            "total_cost": result.total_cost,
            "total_time": result.total_time,
            "outputs": result.outputs,
            "error": result.error,
        }

        if output.json_mode:
            output.result(result_dict, command="create-video")
        elif result.success:
            output.info(f"\n✅ Video creation successful!")
            output.info(f"📦 Steps completed: {result.steps_completed}/{result.total_steps}")
            output.info(f"💰 Total cost: ${result.total_cost:.3f}")
            output.info(f"⏱️  Total time: {result.total_time:.1f} seconds")
            if result.outputs:
                output.info(f"\n📁 Outputs:")
                for step_name, step_out in result.outputs.items():
                    if step_out.get("path"):
                        output.info(f"   {step_name}: {step_out['path']}")
        else:
            output.error(f"Video creation failed: {result.error}")

        # Save full result if requested (legacy --save-json)
        if args.save_json:
            json_path = manager.output_dir / args.save_json
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            output.info(f"\n📄 Full result saved to: {json_path}")

    except Exception as e:
        error_exit(e, debug=getattr(args, 'debug', False))


def run_chain(args, output):
    """Handle run-chain command."""
    _check_save_json_deprecation(args, output)
    quiet = getattr(args, 'json', False) or getattr(args, 'quiet', False)
    try:
        manager = AIPipelineManager(args.base_dir, quiet=quiet)

        # Load chain configuration
        chain = manager.create_chain_from_config(args.config)

        output.info(f"📋 Loaded chain: {chain.name}")

        # Determine input data based on pipeline input type
        input_data = getattr(args, 'input_text', None)
        initial_input_type = chain.get_initial_input_type()

        # Priority: --input > --input-text > --prompt-file > config
        if getattr(args, 'input', None):
            input_data = read_input(args.input, fallback=input_data)

        if not input_data and args.prompt_file:
            try:
                with open(args.prompt_file, 'r') as f:
                    input_data = f.read().strip()
                    output.info(f"📝 Using prompt from file ({args.prompt_file}): {input_data}")
            except FileNotFoundError:
                error_exit(FileNotFoundError(f"Prompt file not found: {args.prompt_file}"))
            except Exception as e:
                error_exit(e, debug=getattr(args, 'debug', False))

        if not input_data:
            if initial_input_type == "text":
                config_input = chain.config.get("prompt")
                if config_input:
                    input_data = config_input
                    output.info(f"📝 Using prompt from config: {input_data}")
                else:
                    error_exit(ValueError("No input text provided. Use --input, --input-text, --prompt-file, or add 'prompt' field to config."))
            elif initial_input_type == "video":
                config_input = chain.config.get("input_video")
                if config_input:
                    input_data = config_input
                    output.info(f"📹 Using video from config: {input_data}")
                else:
                    error_exit(ValueError("No input video provided. Use --input-text or add 'input_video' field to config."))
            elif initial_input_type == "image":
                config_input = chain.config.get("input_image")
                if config_input:
                    input_data = config_input
                    output.info(f"🖼️ Using image from config: {input_data}")
                else:
                    error_exit(ValueError("No input image provided. Use --input-text or add 'input_image' field to config."))
            elif initial_input_type == "any":
                config_input = chain.config.get("prompt")
                if config_input:
                    input_data = config_input
                    output.info(f"📝 Using prompt from config: {input_data}")
                else:
                    error_exit(ValueError("No input provided for parallel group. Add 'prompt' field to config or use --input-text."))
            else:
                error_exit(ValueError(f"Unknown input type: {initial_input_type}"))
        elif getattr(args, 'input_text', None):
            output.info(f"📝 Using input text: {input_data}")

        # Validate chain
        errors = chain.validate()
        if errors:
            error_exit(ValueError(f"Chain validation failed: {'; '.join(errors)}"))

        # Show cost estimate
        cost_info = manager.estimate_chain_cost(chain)
        output.info(f"💰 Estimated cost: ${cost_info['total_cost']:.3f}")

        if not args.no_confirm:
            if not confirm("\nProceed with execution?"):
                output.info("Execution cancelled.")
                sys.exit(0)

        # Build emitter for --stream mode
        from .cli.stream import StreamEmitter, NullEmitter
        stream_mode = getattr(args, 'stream', False)
        emitter = StreamEmitter(enabled=True) if stream_mode else NullEmitter()

        emitter.pipeline_start(
            name=chain.name,
            total_steps=len(chain.get_enabled_steps()),
            config=args.config,
        )

        # Execute chain
        result = manager.execute_chain(chain, input_data, stream_emitter=emitter)

        # Build result dict
        result_dict = {
            "success": result.success,
            "steps_completed": result.steps_completed,
            "total_steps": result.total_steps,
            "total_cost": result.total_cost,
            "total_time": result.total_time,
            "outputs": result.outputs,
            "error": result.error,
        }

        if stream_mode:
            emitter.pipeline_complete(result_dict)
        elif output.json_mode:
            output.result(result_dict, command="run-chain")
        elif result.success:
            output.info(f"\n✅ Chain execution successful!")
            output.info(f"📦 Steps completed: {result.steps_completed}/{result.total_steps}")
            output.info(f"💰 Total cost: ${result.total_cost:.3f}")
            output.info(f"⏱️  Total time: {result.total_time:.1f} seconds")
        else:
            output.error(f"Chain execution failed: {result.error}")

        # Save results if requested (legacy --save-json)
        if args.save_json:
            json_path = manager.output_dir / args.save_json
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            output.info(f"\n📄 Results saved to: {json_path}")

    except Exception as e:
        error_exit(e, debug=getattr(args, 'debug', False))


def generate_image(args, output):
    """Handle generate-image command."""
    _check_save_json_deprecation(args, output)
    quiet = getattr(args, 'json', False) or getattr(args, 'quiet', False)
    try:
        manager = AIPipelineManager(args.base_dir, quiet=quiet)

        # Build generation parameters
        text = args.text
        if getattr(args, 'input', None):
            text = read_input(args.input, fallback=text)

        gen_params = {
            "prompt": text,
            "model": args.model,
            "aspect_ratio": args.aspect_ratio,
            "output_dir": args.output_dir or "output"
        }

        if hasattr(args, 'resolution') and args.resolution:
            gen_params["resolution"] = args.resolution

        result = manager.text_to_image.generate(**gen_params)

        result_dict = {
            "success": result.success,
            "model": result.model_used,
            "output_path": result.output_path,
            "cost": result.cost_estimate,
            "processing_time": result.processing_time,
            "error": result.error,
        }

        if output.json_mode:
            output.result(result_dict, command="generate-image")
        elif result.success:
            output.info(f"\n✅ Image generation successful!")
            output.info(f"📦 Model: {result.model_used}")
            if result.output_path:
                output.info(f"📁 Output: {result.output_path}")
            output.info(f"💰 Cost: ${result.cost_estimate:.3f}")
            output.info(f"⏱️  Processing time: {result.processing_time:.1f} seconds")
        else:
            output.error(f"Image generation failed: {result.error}")

        # Save result if requested (legacy --save-json)
        if args.save_json:
            json_path = manager.output_dir / args.save_json
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            output.info(f"\n📄 Result saved to: {json_path}")

    except Exception as e:
        error_exit(e, debug=getattr(args, 'debug', False))


def create_examples(args, output):
    """Handle create-examples command."""
    quiet = getattr(args, 'json', False) or getattr(args, 'quiet', False)
    try:
        manager = AIPipelineManager(args.base_dir, quiet=quiet)
        manager.create_example_configs(args.output_dir)
        output.info("✅ Example configurations created successfully!")

    except Exception as e:
        error_exit(e, debug=getattr(args, 'debug', False))


def generate_avatar(args, output):
    """Handle generate-avatar command."""
    if not FAL_AVATAR_AVAILABLE:
        error_exit(ImportError("FAL Avatar module not available. Ensure fal_avatar package is in path and fal-client is installed."))

    _check_save_json_deprecation(args, output)
    try:
        generator = FALAvatarGenerator()

        # Determine which method to use based on inputs
        if args.video_url:
            output.info(f"🎬 Transforming video with model: {args.model or 'auto'}")
            mode = "edit" if args.model == "kling_v2v_edit" else "reference"
            result = generator.transform_video(
                video_url=args.video_url,
                prompt=args.prompt or "Transform this video",
                mode=mode,
            )
        elif args.reference_images:
            output.info(f"🖼️ Generating video from {len(args.reference_images)} reference images")
            result = generator.generate_reference_video(
                prompt=args.prompt or "Generate a video with these references",
                reference_images=args.reference_images,
                duration=args.duration,
                aspect_ratio=args.aspect_ratio,
            )
        elif args.image_url:
            model = args.model
            if args.text and not args.audio_url:
                model = model or "fabric_1_0_text"
                output.info(f"🎤 Generating TTS avatar with model: {model}")
            else:
                model = model or "omnihuman_v1_5"
                output.info(f"🎭 Generating lipsync avatar with model: {model}")

            result = generator.generate_avatar(
                image_url=args.image_url,
                audio_url=args.audio_url,
                text=args.text,
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
            output.info("\n✅ Avatar generation successful!")
            output.info(f"📦 Model: {result.model_used}")
            if result.video_url:
                output.info(f"🎬 Video URL: {result.video_url}")
            if result.duration:
                output.info(f"⏱️ Duration: {result.duration:.1f} seconds")
            if result.cost:
                output.info(f"💰 Cost: ${result.cost:.3f}")
            if result.processing_time:
                output.info(f"⏱️ Processing time: {result.processing_time:.1f} seconds")
        else:
            output.error(f"Avatar generation failed: {result.error}")

        # Save result if requested (legacy --save-json)
        if args.save_json:
            json_path = Path(args.save_json)
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            output.info(f"\n📄 Result saved to: {json_path}")

    except Exception as e:
        error_exit(e, debug=getattr(args, 'debug', False))


def list_avatar_models(args, output):
    """Handle list-avatar-models command."""
    if not FAL_AVATAR_AVAILABLE:
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

    output.info("\n🎭 FAL Avatar Generation Models")
    output.info("=" * 50)

    for category, models in categories.items():
        output.info(f"\n📦 {category.replace('_', ' ').title()}")
        for model in models:
            info = generator.get_model_info(model)
            display_name = generator.get_display_name(model)
            output.info(f"   • {model}")
            output.info(f"     Name: {display_name}")
            output.info(f"     Best for: {', '.join(info.get('best_for', []))}")
            if 'pricing' in info:
                pricing = info['pricing']
                if 'per_second' in pricing:
                    output.info(f"     Cost: ${pricing['per_second']}/second")
                elif '720p' in pricing:
                    output.info(f"     Cost: ${pricing.get('480p', 'N/A')}/s (480p), ${pricing.get('720p', 'N/A')}/s (720p)")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Content Pipeline - Unified content creation with multiple AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available models
  python -m ai_content_pipeline list-models

  # Generate image only
  python -m ai_content_pipeline generate-image --text "epic space battle" --model flux_dev

  # Quick video creation (text → image → video)
  python -m ai_content_pipeline create-video --text "serene mountain lake"

  # Run custom chain from config
  python -m ai_content_pipeline run-chain --config my_chain.yaml --input "cyberpunk city"

  # Create example configurations
  python -m ai_content_pipeline create-examples

  # Generate lipsync avatar (image + audio)
  python -m ai_content_pipeline generate-avatar --image-url "https://..." --audio-url "https://..."

  # Generate TTS avatar (image + text)
  python -m ai_content_pipeline generate-avatar --image-url "https://..." --text "Hello world!"

  # Generate video with reference images
  python -m ai_content_pipeline generate-avatar --reference-images img1.jpg img2.jpg --prompt "A person walking"

  # List avatar models
  python -m ai_content_pipeline list-avatar-models

  # Analyze video with AI (Gemini 3 Pro via FAL)
  python -m ai_content_pipeline analyze-video -i video.mp4

  # Analyze with specific model and type
  python -m ai_content_pipeline analyze-video -i video.mp4 -m gemini-3-pro -t timeline

  # List video analysis models
  python -m ai_content_pipeline list-video-models

  # Transfer motion from video to image
  python -m ai_content_pipeline transfer-motion -i person.jpg -v dance.mp4

  # With options
  python -m ai_content_pipeline transfer-motion -i person.jpg -v dance.mp4 -o output/ --orientation video -p "Person dancing"

  # List motion models
  python -m ai_content_pipeline list-motion-models

  # Generate 3x3 image grid from prompt file
  python -m ai_content_pipeline generate-grid --prompt-file storyboard.md

  # Generate 2x2 grid with style override
  python -m ai_content_pipeline generate-grid -f storyboard.md --grid 2x2 --style "anime style"

  # Upscale image 2x
  python -m ai_content_pipeline upscale-image -i image.png --factor 2

  # Upscale to 4K resolution
  python -m ai_content_pipeline upscale-image -i image.png --target 2160p

  # Initialize project structure
  python -m ai_content_pipeline init-project

  # Initialize in specific directory
  python -m ai_content_pipeline init-project --directory /path/to/project

  # Organize files into structure
  python -m ai_content_pipeline organize-project

  # Preview organization (dry run)
  python -m ai_content_pipeline organize-project --dry-run

  # Show project structure info
  python -m ai_content_pipeline structure-info
        """
    )
    
    # Global options
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--json", action="store_true", default=False,
                        help="Emit machine-readable JSON output to stdout")
    parser.add_argument("--quiet", "-q", action="store_true", default=False,
                        help="Suppress non-essential output (errors still go to stderr)")
    parser.add_argument("--base-dir", default=".", help="Base directory for operations")
    parser.add_argument("--config-dir", type=str, default=None,
                        help="Override config directory (default: XDG_CONFIG_HOME/video-ai-studio)")
    parser.add_argument("--cache-dir", type=str, default=None,
                        help="Override cache directory (default: XDG_CACHE_HOME/video-ai-studio)")
    parser.add_argument("--state-dir", type=str, default=None,
                        help="Override state directory (default: XDG_STATE_HOME/video-ai-studio)")
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List models command
    subparsers.add_parser("list-models", help="List all available models")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Create .env file with API key templates")
    setup_parser.add_argument("--output-dir", help="Directory to create .env file (default: current directory)")
    
    # Generate image command
    image_parser = subparsers.add_parser("generate-image", help="Generate image from text")
    image_parser.add_argument("--text", required=True, help="Text prompt for image generation")
    image_parser.add_argument("--model", default="auto", help="Model to use (default: auto)")
    image_parser.add_argument("--aspect-ratio", default="16:9",
                              help="Aspect ratio (default: 16:9). For nano_banana_pro: auto, 21:9, 16:9, 3:2, 4:3, 5:4, 1:1, 4:5, 3:4, 2:3, 9:16")
    image_parser.add_argument("--resolution", default="1K",
                              help="Resolution for supported models (default: 1K). Options: 1K, 2K, 4K. Note: 4K costs double.")
    image_parser.add_argument("--input", type=str, default=None,
                              help="Read prompt from file or stdin (use - for stdin)")
    image_parser.add_argument("--output-dir", help="Output directory")
    image_parser.add_argument("--save-json", help="Save result as JSON (deprecated, use --json)")
    
    # Create video command
    video_parser = subparsers.add_parser("create-video", help="Create video from text (text → image → video)")
    video_parser.add_argument("--text", required=True, help="Text prompt for content creation")
    video_parser.add_argument("--image-model", default="auto", help="Model for text-to-image")
    video_parser.add_argument("--video-model", default="auto", help="Model for image-to-video")
    video_parser.add_argument("--input", type=str, default=None,
                              help="Read prompt from file or stdin (use - for stdin)")
    video_parser.add_argument("--output-dir", help="Output directory")
    video_parser.add_argument("--save-json", help="Save result as JSON (deprecated, use --json)")
    
    # Run chain command
    chain_parser = subparsers.add_parser("run-chain", help="Run custom chain from configuration")
    chain_parser.add_argument("--config", required=True, help="Path to chain configuration (YAML/JSON)")
    chain_parser.add_argument("--input-text", help="Input text for the chain (optional if prompt defined in config)")
    chain_parser.add_argument("--prompt-file", help="Path to text file containing the prompt")
    chain_parser.add_argument("--input", type=str, default=None,
                              help="Read input data from file or stdin (use - for stdin)")
    chain_parser.add_argument("--no-confirm", action="store_true", default=False, help="Skip confirmation prompt (auto-set in CI)")
    chain_parser.add_argument("--stream", action="store_true", default=False,
                              help="Emit JSONL progress events to stderr during execution")
    chain_parser.add_argument("--save-json", help="Save results as JSON (deprecated, use --json)")
    
    # Create examples command
    examples_parser = subparsers.add_parser("create-examples", help="Create example configuration files")
    examples_parser.add_argument("--output-dir", help="Directory for example configs")

    # Generate avatar command
    avatar_parser = subparsers.add_parser("generate-avatar", help="Generate avatar/lipsync video")
    avatar_parser.add_argument("--image-url", help="Portrait image URL for avatar generation")
    avatar_parser.add_argument("--audio-url", help="Audio URL for lipsync (use with --image-url)")
    avatar_parser.add_argument("--text", help="Text for TTS avatar (use with --image-url)")
    avatar_parser.add_argument("--video-url", help="Video URL for transformation")
    avatar_parser.add_argument("--reference-images", nargs="+", help="Reference images for video generation (max 4)")
    avatar_parser.add_argument("--prompt", help="Prompt for generation/transformation")
    avatar_parser.add_argument("--model", help="Model to use (default: auto-selected based on inputs)")
    avatar_parser.add_argument("--duration", default="5", help="Video duration in seconds (default: 5)")
    avatar_parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)")
    avatar_parser.add_argument("--save-json", help="Save result as JSON")

    # List avatar models command
    subparsers.add_parser("list-avatar-models", help="List available avatar generation models")

    # Analyze video command
    analyze_video_parser = subparsers.add_parser(
        "analyze-video",
        help="Analyze video content using AI (Gemini via FAL/Direct)"
    )
    analyze_video_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input video file or directory"
    )
    analyze_video_parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)"
    )
    analyze_video_parser.add_argument(
        "-m", "--model",
        default="gemini-3-pro",
        choices=list(VIDEO_MODEL_MAP.keys()),
        help="Model to use (default: gemini-3-pro)"
    )
    analyze_video_parser.add_argument(
        "-t", "--type",
        default="timeline",
        choices=list(VIDEO_ANALYSIS_TYPES.keys()),
        help="Analysis type (default: timeline)"
    )
    analyze_video_parser.add_argument(
        "-f", "--format",
        default="both",
        choices=["md", "json", "both"],
        help="Output format (default: both)"
    )

    # List video models command
    subparsers.add_parser(
        "list-video-models",
        help="List available video analysis models"
    )

    # Transfer motion command
    motion_parser = subparsers.add_parser(
        "transfer-motion",
        help="Transfer motion from video to image (Kling v2.6)"
    )
    motion_parser.add_argument(
        "-i", "--image",
        required=True,
        help="Image file path or URL (character/background source)"
    )
    motion_parser.add_argument(
        "-v", "--video",
        required=True,
        help="Video file path or URL (motion source)"
    )
    motion_parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)"
    )
    motion_parser.add_argument(
        "--orientation",
        choices=list(ORIENTATION_OPTIONS.keys()),
        default="video",
        help="Character orientation: video (max 30s) or image (max 10s)"
    )
    motion_parser.add_argument(
        "--no-sound",
        action="store_true",
        help="Remove audio from output (default: keep sound)"
    )
    motion_parser.add_argument(
        "-p", "--prompt",
        help="Optional text description to guide generation"
    )
    motion_parser.add_argument(
        "--save-json",
        help="Save result metadata as JSON file"
    )

    # List motion models command
    subparsers.add_parser(
        "list-motion-models",
        help="List available motion transfer models"
    )

    # Transcribe command
    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help="Transcribe audio using ElevenLabs Scribe v2"
    )
    transcribe_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input audio file path or URL"
    )
    transcribe_parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)"
    )
    transcribe_parser.add_argument(
        "--language",
        help="Language code (e.g., eng, spa, fra). Default: auto-detect"
    )
    transcribe_parser.add_argument(
        "--diarize",
        action="store_true",
        default=True,
        help="Enable speaker diarization (default: enabled)"
    )
    transcribe_parser.add_argument(
        "--no-diarize",
        action="store_false",
        dest="diarize",
        help="Disable speaker diarization"
    )
    transcribe_parser.add_argument(
        "--tag-events",
        action="store_true",
        default=True,
        help="Tag audio events (default: enabled)"
    )
    transcribe_parser.add_argument(
        "--no-tag-events",
        action="store_false",
        dest="tag_events",
        help="Disable audio event tagging"
    )
    transcribe_parser.add_argument(
        "--keyterms",
        nargs="+",
        help="Terms to bias transcription toward (increases cost by 30%%)"
    )
    transcribe_parser.add_argument(
        "--save-json",
        metavar="FILENAME",
        help="Save detailed metadata as JSON file"
    )
    transcribe_parser.add_argument(
        "--raw-json",
        metavar="FILENAME",
        help="Save raw API response with word-level timestamps as JSON"
    )
    transcribe_parser.add_argument(
        "--srt",
        metavar="FILENAME",
        help="Generate SRT subtitle file from word timestamps"
    )
    transcribe_parser.add_argument(
        "--srt-max-words",
        type=int,
        default=8,
        help="Max words per subtitle line (default: 8)"
    )
    transcribe_parser.add_argument(
        "--srt-max-duration",
        type=float,
        default=4.0,
        help="Max seconds per subtitle (default: 4.0)"
    )

    # List speech models command
    subparsers.add_parser(
        "list-speech-models",
        help="List available speech-to-text models"
    )

    # Generate grid command
    grid_parser = subparsers.add_parser(
        "generate-grid",
        help="Generate 2x2 or 3x3 image grid from prompt file"
    )
    grid_parser.add_argument(
        "--prompt-file", "-f",
        required=True,
        help="Markdown file with panel descriptions"
    )
    grid_parser.add_argument(
        "--grid", "-g",
        choices=list(GRID_CONFIGS.keys()),
        default="3x3",
        help="Grid size: 2x2 (4 panels) or 3x3 (9 panels). Default: 3x3"
    )
    grid_parser.add_argument(
        "--style", "-s",
        help="Style override (replaces prompt file style)"
    )
    grid_parser.add_argument(
        "--model", "-m",
        default="nano_banana_pro",
        help="Model to use (default: nano_banana_pro)"
    )
    grid_parser.add_argument(
        "--upscale",
        type=float,
        help="Upscale factor after generation (e.g., 2 for 2x)"
    )
    grid_parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)"
    )
    grid_parser.add_argument(
        "--save-json",
        metavar="FILENAME",
        help="Save metadata as JSON file"
    )

    # Upscale image command
    upscale_parser = subparsers.add_parser(
        "upscale-image",
        help="Upscale image using SeedVR2"
    )
    upscale_parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input image path or URL"
    )
    upscale_parser.add_argument(
        "--factor",
        type=float,
        default=2,
        help="Upscale factor 1-8 (default: 2)"
    )
    upscale_parser.add_argument(
        "--target",
        choices=UPSCALE_TARGETS,
        help="Target resolution (720p, 1080p, 1440p, 2160p). Overrides --factor"
    )
    upscale_parser.add_argument(
        "--format",
        choices=["png", "jpg", "webp"],
        default="png",
        help="Output format (default: png)"
    )
    upscale_parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)"
    )
    upscale_parser.add_argument(
        "--save-json",
        metavar="FILENAME",
        help="Save metadata as JSON file"
    )

    # Init project command
    init_parser = subparsers.add_parser(
        "init-project",
        help="Initialize project with standard directory structure"
    )
    init_parser.add_argument(
        "-d", "--directory",
        default=".",
        help="Directory to initialize (default: current directory)"
    )
    init_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without making changes"
    )

    # Organize project command
    organize_parser = subparsers.add_parser(
        "organize-project",
        help="Organize files into standard project structure"
    )
    organize_parser.add_argument(
        "-d", "--directory",
        default=".",
        help="Project root directory (default: current directory)"
    )
    organize_parser.add_argument(
        "-s", "--source",
        help="Source directory to organize from (default: root directory)"
    )
    organize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without making changes"
    )
    organize_parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively scan subdirectories"
    )
    organize_parser.add_argument(
        "--include-output",
        action="store_true",
        help="Also organize files in output/ folder into subfolders"
    )

    # Structure info command
    info_parser = subparsers.add_parser(
        "structure-info",
        help="Show project structure information"
    )
    info_parser.add_argument(
        "-d", "--directory",
        default=".",
        help="Project directory (default: current directory)"
    )

    # Parse arguments
    args = parser.parse_args()

    # Create structured output handler
    output = CLIOutput(
        json_mode=getattr(args, 'json', False),
        quiet=getattr(args, 'quiet', False),
        debug=getattr(args, 'debug', False),
    )

    # Execute command
    if args.command == "list-models":
        print_models(output)
    elif args.command == "setup":
        setup_env(args, output)
    elif args.command == "generate-image":
        generate_image(args, output)
    elif args.command == "create-video":
        create_video(args, output)
    elif args.command == "run-chain":
        run_chain(args, output)
    elif args.command == "create-examples":
        create_examples(args, output)
    elif args.command == "generate-avatar":
        generate_avatar(args, output)
    elif args.command == "list-avatar-models":
        list_avatar_models(args, output)
    elif args.command == "analyze-video":
        analyze_video_command(args)
    elif args.command == "list-video-models":
        list_video_models()
    elif args.command == "transfer-motion":
        transfer_motion_command(args)
    elif args.command == "list-motion-models":
        list_motion_models()
    elif args.command == "transcribe":
        transcribe_command(args)
    elif args.command == "list-speech-models":
        list_speech_models()
    elif args.command == "generate-grid":
        generate_grid_command(args)
    elif args.command == "upscale-image":
        upscale_image_command(args)
    elif args.command == "init-project":
        init_project_command(args)
    elif args.command == "organize-project":
        organize_project_command(args)
    elif args.command == "structure-info":
        structure_info_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()