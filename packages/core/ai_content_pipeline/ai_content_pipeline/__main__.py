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
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()