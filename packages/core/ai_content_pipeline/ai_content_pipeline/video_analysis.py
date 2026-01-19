"""
Video analysis CLI command implementation.

Provides analyze-video command for AI-powered video understanding
using Gemini models via FAL OpenRouter or direct Gemini API.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv


# Model mapping: CLI key -> (provider, full_model_id)
MODEL_MAP = {
    "gemini-3-pro": ("fal", "google/gemini-3-pro-preview"),
    "gemini-2.5-pro": ("fal", "google/gemini-2.5-pro"),
    "gemini-2.5-flash": ("fal", "google/gemini-2.5-flash"),
    "gemini-direct": ("gemini", "gemini-2.0-flash-exp"),
}

# Analysis type mapping
ANALYSIS_TYPES = {
    "timeline": "Detailed second-by-second timeline",
    "describe": "Video description and summary",
    "transcribe": "Audio transcription with timestamps",
}


def get_video_tools_path() -> Path:
    """Get path to video-tools package."""
    # Navigate from ai_content_pipeline to services/video-tools
    current = Path(__file__).parent
    # packages/core/ai_content_pipeline/ai_content_pipeline -> packages/services/video-tools
    return current.parent.parent.parent / "services" / "video-tools"


def analyze_video_command(args) -> None:
    """Handle analyze-video CLI command.

    Args:
        args: Parsed argparse arguments with:
            - input: Input video file or directory path
            - output: Output directory (default: output/)
            - model: Model key (default: gemini-3-pro)
            - type: Analysis type (default: timeline)
            - format: Output format (md, json, both)
    """
    # Load environment variables
    load_dotenv()

    # Resolve model
    model_key = args.model
    if model_key not in MODEL_MAP:
        print(f"❌ Unknown model: {model_key}")
        print(f"   Available: {', '.join(MODEL_MAP.keys())}")
        sys.exit(1)

    provider, model_id = MODEL_MAP[model_key]

    # Check API keys
    if provider == "fal" and not os.getenv("FAL_KEY"):
        print("❌ FAL_KEY environment variable not set")
        print("   Set it in your .env file or export FAL_KEY=your_key")
        sys.exit(1)
    elif provider == "gemini" and not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Set it in your .env file or export GEMINI_API_KEY=your_key")
        sys.exit(1)

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input not found: {args.input}")
        sys.exit(1)

    # Get analysis type and output dir
    analysis_type = args.type
    output_dir = args.output

    print(f"🎬 VIDEO ANALYSIS - {ANALYSIS_TYPES.get(analysis_type, analysis_type)}")
    print("=" * 60)
    print(f"📹 Input: {args.input}")
    print(f"📁 Output: {output_dir}")
    print(f"🤖 Model: {model_key} ({model_id})")
    print(f"📊 Type: {analysis_type}")
    print()

    try:
        # Add video-tools to path
        video_tools_path = get_video_tools_path()
        if str(video_tools_path) not in sys.path:
            sys.path.insert(0, str(video_tools_path))

        if analysis_type == "timeline":
            from video_utils.ai_commands import cmd_detailed_timeline_with_params
            result = cmd_detailed_timeline_with_params(
                input_path=str(input_path),
                output_path=output_dir,
                provider=provider,
                model=model_id
            )
        elif analysis_type == "describe":
            from video_utils.ai_commands import cmd_describe_videos_with_params
            result = cmd_describe_videos_with_params(
                input_path=str(input_path),
                output_path=output_dir,
                format_type="describe-video"
            )
        elif analysis_type == "transcribe":
            from video_utils.ai_commands import cmd_transcribe_videos_with_params
            result = cmd_transcribe_videos_with_params(
                input_path=str(input_path),
                output_path=output_dir,
                format_type="describe-video"
            )
        else:
            print(f"❌ Unknown analysis type: {analysis_type}")
            sys.exit(1)

        if result:
            print("\n✅ Analysis complete!")
        else:
            print("\n❌ Analysis failed or returned no results")
            sys.exit(1)

    except ImportError as e:
        print(f"❌ Failed to import video analysis module: {e}")
        print("   Ensure video-tools package is available")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def list_video_models() -> None:
    """Print available video analysis models."""
    print("\n🎬 Video Analysis Models")
    print("=" * 50)

    for key, (provider, model_id) in MODEL_MAP.items():
        print(f"\n  {key}")
        print(f"    Provider: {provider.upper()}")
        print(f"    Model ID: {model_id}")

    print("\n📊 Analysis Types")
    print("=" * 50)
    for key, desc in ANALYSIS_TYPES.items():
        print(f"  {key}: {desc}")

    print("\n💡 Usage Examples")
    print("=" * 50)
    print("  aicp analyze-video -i video.mp4")
    print("  aicp analyze-video -i video.mp4 -m gemini-3-pro -t timeline")
    print("  aicp analyze-video -i video.mp4 -m gemini-2.5-flash -t describe")
    print("  aicp analyze-video -i videos/ -t transcribe -o output/")
