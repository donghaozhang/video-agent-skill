"""
File utility functions for FAL Image-to-Video.
"""

import os
import time
import requests
import fal_client
from pathlib import Path
from typing import Optional, List

# Supported file formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi', '.webm', '.mkv']


def ensure_output_directory(output_dir: Optional[str] = None) -> Path:
    """
    Ensure output directory exists.

    Args:
        output_dir: Custom output directory path

    Returns:
        Path object for the output directory
    """
    if output_dir is None:
        output_dir = "output"

    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def download_video(
    video_url: str,
    output_dir: Path,
    model_key: str,
    filename: Optional[str] = None
) -> Optional[str]:
    """
    Download video from URL to local folder.

    Args:
        video_url: URL of the video to download
        output_dir: Output directory path
        model_key: Model identifier for filename
        filename: Optional custom filename

    Returns:
        Local path of the downloaded video or None if failed
    """
    try:
        if filename is None:
            # Use nanoseconds for unique filenames in parallel execution
            timestamp = time.time_ns()
            filename = f"{model_key}_video_{timestamp}.mp4"

        print("📥 Downloading video...")
        response = requests.get(video_url, stream=True, timeout=300)
        response.raise_for_status()

        local_path = output_dir / filename
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        absolute_path = str(local_path.absolute())
        print(f"✅ Video saved: {absolute_path}")
        return absolute_path

    except Exception as e:
        print(f"❌ Error downloading video: {e}")
        return None


def upload_image(image_path: str) -> Optional[str]:
    """
    Upload a local image file to FAL AI.

    Args:
        image_path: Path to the local image file

    Returns:
        URL of the uploaded image or None if failed
    """
    try:
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return None

        print(f"📤 Uploading image: {image_path}")
        url = fal_client.upload_file(image_path)
        print(f"✅ Image uploaded: {url[:50]}...")
        return url

    except Exception as e:
        print(f"❌ Error uploading image: {e}")
        return None


def is_url(path: str) -> bool:
    """
    Check if path is a URL.

    Args:
        path: Path or URL string

    Returns:
        True if path is a URL
    """
    return path.startswith(('http://', 'https://'))


def validate_file_format(
    file_path: str,
    supported_formats: List[str],
    file_type: str
) -> None:
    """
    Validate file format against supported formats.

    Args:
        file_path: Path to validate
        supported_formats: List of supported extensions
        file_type: Type description for error message

    Raises:
        ValueError: If format is not supported
    """
    if is_url(file_path):
        return  # URLs are assumed valid

    ext = Path(file_path).suffix.lower()
    if ext not in supported_formats:
        raise ValueError(
            f"Unsupported {file_type} format: {ext}. "
            f"Supported formats: {supported_formats}"
        )


def upload_file(file_path: str) -> Optional[str]:
    """
    Upload any local file to FAL AI.

    Args:
        file_path: Path to local file or URL

    Returns:
        URL of uploaded file, or original URL if already a URL
    """
    if is_url(file_path):
        return file_path

    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None

        print(f"📤 Uploading file: {file_path}")
        url = fal_client.upload_file(file_path)
        print(f"✅ File uploaded: {url[:50]}...")
        return url

    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None


def upload_images(image_paths: List[str]) -> List[str]:
    """
    Upload multiple images and return URLs.

    Args:
        image_paths: List of image paths or URLs

    Returns:
        List of image URLs

    Raises:
        ValueError: If any upload fails
    """
    urls = []
    for path in image_paths:
        validate_file_format(path, SUPPORTED_IMAGE_FORMATS, "image")
        url = upload_file(path)
        if url:
            urls.append(url)
        else:
            raise ValueError(f"Failed to upload image: {path}")
    return urls


def upload_audio(audio_path: str) -> Optional[str]:
    """
    Upload audio file and return URL.

    Args:
        audio_path: Path to audio file or URL

    Returns:
        URL of uploaded audio
    """
    validate_file_format(audio_path, SUPPORTED_AUDIO_FORMATS, "audio")
    return upload_file(audio_path)


def upload_video(video_path: str) -> Optional[str]:
    """
    Upload video file and return URL.

    Args:
        video_path: Path to video file or URL

    Returns:
        URL of uploaded video
    """
    validate_file_format(video_path, SUPPORTED_VIDEO_FORMATS, "video")
    return upload_file(video_path)
