"""
Script to run Kling Motion Control model.
Transfers motion from a video to an image.
"""

import os
import sys
import requests
from datetime import datetime

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'providers', 'fal', 'avatar-generation'))

from dotenv import load_dotenv
load_dotenv()

import fal_client
from fal_avatar import FALAvatarGenerator

def download_video(url: str, output_path: str) -> str:
    """Download video from URL to local path."""
    print(f"📥 Downloading video from: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Video saved to: {output_path}")
    return output_path

def main():
    # Input paths
    video_path = r"c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output\xixiyu_segments\xixiyu_000.mp4"
    image_path = r"c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output\cooking_lady\modified_image_1768216810_1.png"
    output_dir = r"c:\Users\zdhpe\Desktop\video-agent\veo3-fal-video-ai\output\xixiyu_segments"

    # Verify files exist
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return

    print("🎬 Kling v2.6 Motion Control")
    print("=" * 50)
    print(f"📹 Video (motion source): {video_path}")
    print(f"🖼️  Image (character source): {image_path}")
    print(f"📁 Output directory: {output_dir}")
    print()

    # Upload files to FAL
    print("📤 Uploading video to FAL...")
    video_url = fal_client.upload_file(video_path)
    print(f"✅ Video uploaded: {video_url}")

    print("📤 Uploading image to FAL...")
    image_url = fal_client.upload_file(image_path)
    print(f"✅ Image uploaded: {image_url}")

    # Initialize generator
    generator = FALAvatarGenerator()

    # Run motion transfer
    print()
    print("🚀 Starting motion transfer...")
    print("   This may take a few minutes...")

    result = generator.transfer_motion(
        image_url=image_url,
        video_url=video_url,
        character_orientation="video",  # Use video orientation for max 30s output
        keep_original_sound=True,  # Keep audio from reference video
        prompt="A woman cooking pasta in a kitchen"  # Optional description
    )

    if result.success:
        print()
        print("✅ Motion transfer successful!")
        print(f"   Video URL: {result.video_url}")
        print(f"   Duration: {result.duration}s")
        print(f"   Cost: ${result.cost:.2f}")
        print(f"   Processing time: {result.processing_time:.1f}s")

        # Download the result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"motion_transfer_{timestamp}.mp4"
        output_path = os.path.join(output_dir, output_filename)

        download_video(result.video_url, output_path)
        print()
        print(f"🎉 Done! Output saved to: {output_path}")
    else:
        print()
        print(f"❌ Motion transfer failed: {result.error}")

if __name__ == "__main__":
    main()
