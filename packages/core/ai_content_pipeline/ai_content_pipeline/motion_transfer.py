"""
Motion transfer CLI command implementation.

Provides transfer-motion command for Kling v2.6 Motion Control model
to transfer motion from a reference video to a reference image.
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

# Try to import FAL client for file uploads
try:
    import fal_client
    FAL_CLIENT_AVAILABLE = True
except ImportError:
    FAL_CLIENT_AVAILABLE = False

# Try to import FAL Avatar Generator
try:
    from fal_avatar import FALAvatarGenerator
    from fal_avatar.models.base import AvatarGenerationResult
    FAL_AVATAR_AVAILABLE = True
except ImportError:
    FAL_AVATAR_AVAILABLE = False
    AvatarGenerationResult = None


# Orientation options with max durations
ORIENTATION_OPTIONS = {
    "video": {"max_duration": 30, "description": "Use video's character orientation (max 30s)"},
    "image": {"max_duration": 10, "description": "Use image's character orientation (max 10s)"},
}

# Default values
DEFAULTS = {
    "orientation": "video",
    "keep_sound": True,
    "output_dir": "output",
}


@dataclass
class MotionTransferResult:
    """Result from motion transfer operation."""
    success: bool
    video_url: Optional[str] = None
    local_path: Optional[str] = None
    duration: Optional[float] = None
    cost: Optional[float] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def check_dependencies() -> Tuple[bool, str]:
    """
    Check if required dependencies are available.

    Returns:
        Tuple of (success, error_message)
    """
    if not FAL_CLIENT_AVAILABLE:
        return False, "fal-client not installed. Run: pip install fal-client"
    if not FAL_AVATAR_AVAILABLE:
        return False, "fal_avatar module not available. Ensure package is installed."
    if not os.getenv("FAL_KEY"):
        return False, "FAL_KEY environment variable not set"
    return True, ""


def upload_if_local(file_path: str, file_type: str = "file") -> str:
    """
    Upload local file to FAL if it's a local path, otherwise return as-is.

    Args:
        file_path: Local file path or URL
        file_type: Description for logging ("image" or "video")

    Returns:
        URL (uploaded or original)

    Raises:
        FileNotFoundError: If local file doesn't exist
        ValueError: If upload fails
    """
    # Check if it's a URL
    if file_path.startswith(("http://", "https://")):
        return file_path

    # It's a local file
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"{file_type.title()} not found: {file_path}")

    print(f"📤 Uploading {file_type}: {path.name}")
    try:
        url = fal_client.upload_file(str(path))
        print(f"✅ {file_type.title()} uploaded: {url[:60]}...")
        return url
    except Exception as e:
        raise ValueError(f"Failed to upload {file_type}: {e}")


def download_video(url: str, output_path: Path) -> Path:
    """
    Download video from URL to local path.

    Args:
        url: Video URL
        output_path: Destination path

    Returns:
        Path to downloaded file

    Raises:
        requests.RequestException: If download fails
    """
    print(f"📥 Downloading video...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Video saved: {output_path}")
    return output_path


def transfer_motion_api(
    image_url: str,
    video_url: str,
    orientation: str = "video",
    keep_sound: bool = True,
    prompt: Optional[str] = None,
):
    """
    Call the motion transfer API.

    This is the core API function that can be used programmatically.

    Args:
        image_url: Image URL (character/background source)
        video_url: Video URL (motion source)
        orientation: "video" (max 30s) or "image" (max 10s)
        keep_sound: Keep audio from reference video
        prompt: Optional text description

    Returns:
        AvatarGenerationResult from FAL Avatar Generator
    """
    generator = FALAvatarGenerator()
    return generator.transfer_motion(
        image_url=image_url,
        video_url=video_url,
        character_orientation=orientation,
        keep_original_sound=keep_sound,
        prompt=prompt,
    )


def transfer_motion(
    image_path: str,
    video_path: str,
    output_dir: str = "output",
    orientation: str = "video",
    keep_sound: bool = True,
    prompt: Optional[str] = None,
    download: bool = True,
) -> MotionTransferResult:
    """
    Transfer motion from video to image with full workflow.

    Handles file uploads, API call, and optional download.

    Args:
        image_path: Image file path or URL
        video_path: Video file path or URL
        output_dir: Output directory for downloaded video
        orientation: "video" (max 30s) or "image" (max 10s)
        keep_sound: Keep audio from reference video
        prompt: Optional text description
        download: Whether to download result video

    Returns:
        MotionTransferResult with all operation details
    """
    # Check dependencies
    ok, error = check_dependencies()
    if not ok:
        return MotionTransferResult(success=False, error=error)

    try:
        # Upload files if local
        image_url = upload_if_local(image_path, "image")
        video_url = upload_if_local(video_path, "video")

        # Call API
        print(f"\n🎬 Starting motion transfer...")
        print(f"   Orientation: {orientation} (max {ORIENTATION_OPTIONS[orientation]['max_duration']}s)")
        print(f"   Keep sound: {keep_sound}")

        result = transfer_motion_api(
            image_url=image_url,
            video_url=video_url,
            orientation=orientation,
            keep_sound=keep_sound,
            prompt=prompt,
        )

        if not result.success:
            return MotionTransferResult(
                success=False,
                error=result.error,
                processing_time=result.processing_time,
            )

        # Download if requested
        local_path = None
        if download and result.video_url:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"motion_transfer_{timestamp}.mp4"
            local_path = str(download_video(result.video_url, output_path / filename))

        return MotionTransferResult(
            success=True,
            video_url=result.video_url,
            local_path=local_path,
            duration=result.duration,
            cost=result.cost,
            processing_time=result.processing_time,
            metadata=result.metadata,
        )

    except FileNotFoundError as e:
        return MotionTransferResult(success=False, error=str(e))
    except ValueError as e:
        return MotionTransferResult(success=False, error=str(e))
    except Exception as e:
        return MotionTransferResult(success=False, error=f"Unexpected error: {e}")


def transfer_motion_command(args) -> None:
    """
    Handle transfer-motion CLI command.

    Args:
        args: Parsed argparse arguments
    """
    load_dotenv()

    # Validate orientation
    orientation = args.orientation
    if orientation not in ORIENTATION_OPTIONS:
        print(f"❌ Invalid orientation: {orientation}")
        print(f"   Valid options: {', '.join(ORIENTATION_OPTIONS.keys())}")
        sys.exit(1)

    # Determine sound setting
    keep_sound = not args.no_sound

    # Print header
    print(f"\n🎬 KLING v2.6 MOTION CONTROL")
    print("=" * 50)
    print(f"🖼️  Image: {args.image}")
    print(f"📹 Video: {args.video}")
    print(f"📁 Output: {args.output}")
    print(f"🔄 Orientation: {orientation}")
    print(f"🔊 Keep sound: {keep_sound}")
    if args.prompt:
        print(f"📝 Prompt: {args.prompt}")
    print()

    # Execute
    result = transfer_motion(
        image_path=args.image,
        video_path=args.video,
        output_dir=args.output,
        orientation=orientation,
        keep_sound=keep_sound,
        prompt=args.prompt,
        download=True,
    )

    # Display results
    if result.success:
        print(f"\n✅ Motion transfer successful!")
        print(f"📦 Model: kling_motion_control")
        if result.duration:
            print(f"⏱️  Duration: {result.duration}s")
        if result.cost:
            print(f"💰 Cost: ${result.cost:.2f}")
        if result.processing_time:
            print(f"⏱️  Processing: {result.processing_time:.1f}s")
        if result.local_path:
            print(f"📁 Output: {result.local_path}")

        # Save JSON if requested
        if args.save_json:
            import json
            json_path = Path(args.output) / args.save_json
            with open(json_path, 'w') as f:
                json.dump({
                    "success": True,
                    "video_url": result.video_url,
                    "local_path": result.local_path,
                    "duration": result.duration,
                    "cost": result.cost,
                    "processing_time": result.processing_time,
                    "metadata": result.metadata,
                }, f, indent=2)
            print(f"📄 Metadata: {json_path}")
    else:
        print(f"\n❌ Motion transfer failed!")
        print(f"   Error: {result.error}")
        sys.exit(1)


def list_motion_models() -> None:
    """Print motion transfer model information."""
    print("\n🎬 Motion Transfer Models")
    print("=" * 50)
    print("\n  kling_motion_control")
    print("    Name: Kling v2.6 Motion Control")
    print("    Provider: FAL AI")
    print("    Cost: $0.06/second")
    print("    Max Duration: 30s (video) / 10s (image)")
    print("    Best for: dance videos, action sequences, character animation")
    print("\n  Orientation Options:")
    for key, info in ORIENTATION_OPTIONS.items():
        print(f"    • {key}: {info['description']}")
