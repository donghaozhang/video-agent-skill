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


def print_models():
    """Print information about all supported models."""
    print("\n🎨 AI Content Pipeline Supported Models")
    print("=" * 50)
    
    manager = AIPipelineManager()
    available_models = manager.get_available_models()
    
    for step_type, models in available_models.items():
        print(f"\n📦 {step_type.replace('_', '-').title()}")
        
        if models:
            for model in models:
                # Get model info if available
                if step_type == "text_to_image":
                    info = manager.text_to_image.get_model_info(model)
                    print(f"   • {model}")
                    if info:
                        print(f"     Name: {info.get('name', 'N/A')}")
                        print(f"     Provider: {info.get('provider', 'N/A')}")
                        print(f"     Best for: {info.get('best_for', 'N/A')}")
                        print(f"     Cost: {info.get('cost_per_image', 'N/A')}")
                else:
                    print(f"   • {model}")
        else:
            print("   No models available (integration pending)")


def setup_env(args):
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
        response = input(f"⚠️  .env file already exists at {env_path}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return
    
    try:
        with open(env_path, 'w') as f:
            f.write(template_content)
        print(f"✅ Created .env file at {env_path}")
        print("📝 Please edit the file and add your API keys:")
        print(f"   nano {env_path}")
        print("\n🔑 Get your API keys from:")
        print("   • FAL AI: https://fal.ai/dashboard")
        print("   • Google Gemini: https://makersuite.google.com/app/apikey")
        print("   • OpenRouter: https://openrouter.ai/keys")
        print("   • ElevenLabs: https://elevenlabs.io/app/settings")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")


def create_video(args):
    """Handle create-video command."""
    try:
        manager = AIPipelineManager(args.base_dir)
        
        # Create quick video chain
        result = manager.quick_create_video(
            text=args.text,
            image_model=args.image_model,
            video_model=args.video_model,
            output_dir=args.output_dir
        )
        
        # Display results
        if result.success:
            print(f"\n✅ Video creation successful!")
            print(f"📦 Steps completed: {result.steps_completed}/{result.total_steps}")
            print(f"💰 Total cost: ${result.total_cost:.3f}")
            print(f"⏱️  Total time: {result.total_time:.1f} seconds")
            
            if result.outputs:
                print(f"\n📁 Outputs:")
                for step_name, output in result.outputs.items():
                    if output.get("path"):
                        print(f"   {step_name}: {output['path']}")
        else:
            print(f"\n❌ Video creation failed!")
            print(f"Error: {result.error}")
        
        # Save full result if requested
        if args.save_json:
            result_dict = {
                "success": result.success,
                "steps_completed": result.steps_completed,
                "total_steps": result.total_steps,
                "total_cost": result.total_cost,
                "total_time": result.total_time,
                "outputs": result.outputs,
                "error": result.error
            }
            
            # Save JSON file in output directory
            json_path = manager.output_dir / args.save_json
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            print(f"\n📄 Full result saved to: {json_path}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_chain(args):
    """Handle run-chain command."""
    try:
        manager = AIPipelineManager(args.base_dir)
        
        # Load chain configuration
        chain = manager.create_chain_from_config(args.config)
        
        print(f"📋 Loaded chain: {chain.name}")
        
        # Determine input data based on pipeline input type
        input_data = args.input_text
        initial_input_type = chain.get_initial_input_type()
        
        # Priority: --input-text > --prompt-file > config prompt/input_video/input_image
        if not input_data and args.prompt_file:
            # Try to read from prompt file
            try:
                with open(args.prompt_file, 'r') as f:
                    input_data = f.read().strip()
                    print(f"📝 Using prompt from file ({args.prompt_file}): {input_data}")
            except FileNotFoundError:
                print(f"❌ Prompt file not found: {args.prompt_file}")
                sys.exit(1)
            except Exception as e:
                print(f"❌ Error reading prompt file: {e}")
                sys.exit(1)
        
        if not input_data:
            # Try to get input from chain config based on input type
            if initial_input_type == "text":
                config_input = chain.config.get("prompt")
                if config_input:
                    input_data = config_input
                    print(f"📝 Using prompt from config: {input_data}")
                else:
                    print("❌ No input text provided. Use --input-text, --prompt-file, or add 'prompt' field to config.")
                    sys.exit(1)
            elif initial_input_type == "video":
                config_input = chain.config.get("input_video")
                if config_input:
                    input_data = config_input
                    print(f"📹 Using video from config: {input_data}")
                else:
                    print("❌ No input video provided. Use --input-text or add 'input_video' field to config.")
                    sys.exit(1)
            elif initial_input_type == "image":
                config_input = chain.config.get("input_image")
                if config_input:
                    input_data = config_input
                    print(f"🖼️ Using image from config: {input_data}")
                else:
                    print("❌ No input image provided. Use --input-text or add 'input_image' field to config.")
                    sys.exit(1)
            elif initial_input_type == "any":
                # For parallel groups that accept any input type
                config_input = chain.config.get("prompt")
                if config_input:
                    input_data = config_input
                    print(f"📝 Using prompt from config: {input_data}")
                else:
                    print("❌ No input provided for parallel group. Add 'prompt' field to config or use --input-text.")
                    sys.exit(1)
            else:
                print(f"❌ Unknown input type: {initial_input_type}")
                sys.exit(1)
        elif args.input_text:
            print(f"📝 Using input text: {input_data}")
        
        # Validate chain
        errors = chain.validate()
        if errors:
            print(f"❌ Chain validation failed:")
            for error in errors:
                print(f"   • {error}")
            sys.exit(1)
        
        # Show cost estimate
        cost_info = manager.estimate_chain_cost(chain)
        print(f"💰 Estimated cost: ${cost_info['total_cost']:.3f}")
        
        if not args.no_confirm:
            response = input("\nProceed with execution? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("Execution cancelled.")
                sys.exit(0)
        
        # Execute chain
        result = manager.execute_chain(chain, input_data)
        
        # Display results
        if result.success:
            print(f"\n✅ Chain execution successful!")
            print(f"📦 Steps completed: {result.steps_completed}/{result.total_steps}")
            print(f"💰 Total cost: ${result.total_cost:.3f}")
            print(f"⏱️  Total time: {result.total_time:.1f} seconds")
        else:
            print(f"\n❌ Chain execution failed!")
            print(f"Error: {result.error}")
        
        # Save results if requested
        if args.save_json:
            result_dict = {
                "success": result.success,
                "steps_completed": result.steps_completed,
                "total_steps": result.total_steps,
                "total_cost": result.total_cost,
                "total_time": result.total_time,
                "outputs": result.outputs,
                "error": result.error
            }
            
            # Save JSON file in output directory
            json_path = manager.output_dir / args.save_json
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            print(f"\n📄 Results saved to: {json_path}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def generate_image(args):
    """Handle generate-image command."""
    try:
        manager = AIPipelineManager(args.base_dir)

        # Build generation parameters
        gen_params = {
            "prompt": args.text,
            "model": args.model,
            "aspect_ratio": args.aspect_ratio,
            "output_dir": args.output_dir or "output"
        }

        # Add resolution if specified (for models that support it)
        if hasattr(args, 'resolution') and args.resolution:
            gen_params["resolution"] = args.resolution

        # Generate image
        result = manager.text_to_image.generate(**gen_params)
        
        # Display results
        if result.success:
            print(f"\n✅ Image generation successful!")
            print(f"📦 Model: {result.model_used}")
            if result.output_path:
                print(f"📁 Output: {result.output_path}")
            print(f"💰 Cost: ${result.cost_estimate:.3f}")
            print(f"⏱️  Processing time: {result.processing_time:.1f} seconds")
        else:
            print(f"\n❌ Image generation failed!")
            print(f"Error: {result.error}")
        
        # Save result if requested
        if args.save_json:
            result_dict = {
                "success": result.success,
                "model": result.model_used,
                "output_path": result.output_path,
                "cost": result.cost_estimate,
                "processing_time": result.processing_time,
                "error": result.error
            }
            
            # Save JSON file in output directory
            json_path = manager.output_dir / args.save_json
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            print(f"\n📄 Result saved to: {json_path}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def create_examples(args):
    """Handle create-examples command."""
    try:
        manager = AIPipelineManager(args.base_dir)
        manager.create_example_configs(args.output_dir)
        print("✅ Example configurations created successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def generate_avatar(args):
    """Handle generate-avatar command."""
    if not FAL_AVATAR_AVAILABLE:
        print("❌ FAL Avatar module not available.")
        print("   Ensure fal_avatar package is in path and fal-client is installed.")
        sys.exit(1)

    try:
        generator = FALAvatarGenerator()

        # Determine which method to use based on inputs
        if args.video_url:
            # Video transformation mode
            print(f"🎬 Transforming video with model: {args.model or 'auto'}")
            mode = "edit" if args.model == "kling_v2v_edit" else "reference"
            result = generator.transform_video(
                video_url=args.video_url,
                prompt=args.prompt or "Transform this video",
                mode=mode,
            )
        elif args.reference_images:
            # Reference-to-video mode
            print(f"🖼️ Generating video from {len(args.reference_images)} reference images")
            result = generator.generate_reference_video(
                prompt=args.prompt or "Generate a video with these references",
                reference_images=args.reference_images,
                duration=args.duration,
                aspect_ratio=args.aspect_ratio,
            )
        elif args.image_url:
            # Avatar/lipsync mode
            model = args.model
            if args.text and not args.audio_url:
                model = model or "fabric_1_0_text"
                print(f"🎤 Generating TTS avatar with model: {model}")
            else:
                model = model or "omnihuman_v1_5"
                print(f"🎭 Generating lipsync avatar with model: {model}")

            result = generator.generate_avatar(
                image_url=args.image_url,
                audio_url=args.audio_url,
                text=args.text,
                model=model,
            )
        else:
            print("❌ No input provided. Use one of:")
            print("   --image-url    : Portrait image for avatar generation")
            print("   --video-url    : Video for transformation")
            print("   --reference-images : Reference images for video generation")
            sys.exit(1)

        # Display results
        if result.success:
            print("\n✅ Avatar generation successful!")
            print(f"📦 Model: {result.model_used}")
            if result.video_url:
                print(f"🎬 Video URL: {result.video_url}")
            if result.duration:
                print(f"⏱️ Duration: {result.duration:.1f} seconds")
            if result.cost:
                print(f"💰 Cost: ${result.cost:.3f}")
            if result.processing_time:
                print(f"⏱️ Processing time: {result.processing_time:.1f} seconds")
        else:
            print("\n❌ Avatar generation failed!")
            print(f"Error: {result.error}")

        # Save result if requested
        if args.save_json:
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

            json_path = Path(args.save_json)
            with open(json_path, 'w') as f:
                json.dump(result_dict, f, indent=2)
            print(f"\n📄 Result saved to: {json_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def list_avatar_models(args):
    """Handle list-avatar-models command."""
    if not FAL_AVATAR_AVAILABLE:
        print("❌ FAL Avatar module not available.")
        print("   Ensure fal_avatar package is in path and fal-client is installed.")
        sys.exit(1)

    generator = FALAvatarGenerator()

    print("\n🎭 FAL Avatar Generation Models")
    print("=" * 50)

    # Group by category
    categories = generator.list_models_by_category()
    for category, models in categories.items():
        print(f"\n📦 {category.replace('_', ' ').title()}")
        for model in models:
            info = generator.get_model_info(model)
            display_name = generator.get_display_name(model)
            print(f"   • {model}")
            print(f"     Name: {display_name}")
            print(f"     Best for: {', '.join(info.get('best_for', []))}")
            if 'pricing' in info:
                pricing = info['pricing']
                if 'per_second' in pricing:
                    print(f"     Cost: ${pricing['per_second']}/second")
                elif '720p' in pricing:
                    print(f"     Cost: ${pricing.get('480p', 'N/A')}/s (480p), ${pricing.get('720p', 'N/A')}/s (720p)")


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
        """
    )
    
    # Global options
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--base-dir", default=".", help="Base directory for operations")
    
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
    image_parser.add_argument("--output-dir", help="Output directory")
    image_parser.add_argument("--save-json", help="Save result as JSON")
    
    # Create video command
    video_parser = subparsers.add_parser("create-video", help="Create video from text (text → image → video)")
    video_parser.add_argument("--text", required=True, help="Text prompt for content creation")
    video_parser.add_argument("--image-model", default="auto", help="Model for text-to-image")
    video_parser.add_argument("--video-model", default="auto", help="Model for image-to-video")
    video_parser.add_argument("--output-dir", help="Output directory")
    video_parser.add_argument("--save-json", help="Save result as JSON")
    
    # Run chain command
    chain_parser = subparsers.add_parser("run-chain", help="Run custom chain from configuration")
    chain_parser.add_argument("--config", required=True, help="Path to chain configuration (YAML/JSON)")
    chain_parser.add_argument("--input-text", help="Input text for the chain (optional if prompt defined in config)")
    chain_parser.add_argument("--prompt-file", help="Path to text file containing the prompt")
    chain_parser.add_argument("--no-confirm", action="store_true", default=True, help="Skip confirmation prompt")
    chain_parser.add_argument("--save-json", help="Save results as JSON")
    
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
        help="Upscale factor 2-10 (default: 2)"
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

    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "list-models":
        print_models()
    elif args.command == "setup":
        setup_env(args)
    elif args.command == "generate-image":
        generate_image(args)
    elif args.command == "create-video":
        create_video(args)
    elif args.command == "run-chain":
        run_chain(args)
    elif args.command == "create-examples":
        create_examples(args)
    elif args.command == "generate-avatar":
        generate_avatar(args)
    elif args.command == "list-avatar-models":
        list_avatar_models(args)
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
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()