"""
File and image handling utilities
"""

import os
import time
import base64
import requests
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
import fal_client


def upload_local_image(image_path: str) -> str:
    """
    Upload a local image to FAL AI and return the URL.
    
    Args:
        image_path: Path to local image file
        
    Returns:
        URL of uploaded image
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        Exception: If upload fails
    """
    image_file = Path(image_path)
    if not image_file.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        # Upload file to FAL AI
        url = fal_client.upload_file(str(image_file))
        print(f"✅ Image uploaded successfully: {url}")
        return url
    except Exception as e:
        raise Exception(f"Failed to upload image: {e}")


def download_image(image_url: str, output_path: Path) -> str:
    """
    Download an image from URL to local file.

    Supports both HTTP/HTTPS URLs and base64 data URLs.

    Args:
        image_url: URL of the image to download (HTTP URL or data: URL)
        output_path: Local path to save the image

    Returns:
        Path to downloaded file

    Raises:
        Exception: If download fails
    """
    try:
        # Handle base64 data URLs (e.g., "data:image/png;base64,...")
        if image_url.startswith("data:"):
            return save_base64_image(image_url, output_path)

        # Handle regular HTTP/HTTPS URLs
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        return str(output_path)
    except Exception as e:
        raise Exception(f"Failed to download image from {image_url[:100]}...: {e}")


def save_base64_image(data_url: str, output_path: Path) -> str:
    """
    Save a base64 data URL to a local file.

    Args:
        data_url: Base64 data URL (e.g., "data:image/png;base64,...")
        output_path: Local path to save the image

    Returns:
        Path to saved file

    Raises:
        ValueError: If data URL format is invalid
    """
    try:
        # Parse the data URL
        # Format: data:[<mediatype>][;base64],<data>
        header, encoded_data = data_url.split(",", 1)

        # Decode and save
        image_data = base64.b64decode(encoded_data)

        with open(output_path, 'wb') as f:
            f.write(image_data)

        print(f"💾 Saved base64 image ({len(image_data) / 1024:.1f} KB)")
        return str(output_path)

    except Exception as e:
        raise ValueError(f"Failed to decode base64 image: {e}")


def download_images(images: List[dict], output_dir: Path, prefix: str = "modified_image") -> List[str]:
    """
    Download multiple images from API response.

    Handles both regular URLs and base64 data URLs.

    Args:
        images: List of image dictionaries from API response
        output_dir: Directory to save images
        prefix: Filename prefix for saved images

    Returns:
        List of downloaded file paths
    """
    output_dir.mkdir(exist_ok=True)
    downloaded_files = []

    for i, image_info in enumerate(images):
        image_url = image_info.get("url")
        if image_url:
            # Generate filename with appropriate extension
            timestamp = int(time.time())
            ext = get_extension_from_url(image_url)
            filename = f"{prefix}_{timestamp}_{i+1}{ext}"
            file_path = output_dir / filename

            # Download image
            try:
                download_image(image_url, file_path)
                downloaded_files.append(str(file_path))
                print(f"✅ Image saved: {file_path}")
            except Exception as e:
                print(f"❌ Failed to download image {i+1}: {e}")

    return downloaded_files


def get_extension_from_url(url: str) -> str:
    """
    Determine file extension from URL or data URL.

    Args:
        url: Image URL or data URL

    Returns:
        File extension (e.g., ".png", ".jpg")
    """
    if url.startswith("data:"):
        # Parse MIME type from data URL header
        if "image/png" in url:
            return ".png"
        elif "image/jpeg" in url or "image/jpg" in url:
            return ".jpg"
        elif "image/webp" in url:
            return ".webp"
        elif "image/gif" in url:
            return ".gif"
        else:
            return ".png"  # Default
    else:
        # Parse URL and extract extension from path component
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            # Use os.path.splitext to properly extract extension
            _, ext = os.path.splitext(path)
            if ext in [".jpg", ".jpeg"]:
                return ".jpg"
            elif ext == ".webp":
                return ".webp"
            elif ext == ".gif":
                return ".gif"
            elif ext == ".png":
                return ".png"
            else:
                return ".png"  # Default for unknown extensions
        except Exception:
            return ".png"  # Default on parse failure


def ensure_output_directory(output_dir: Optional[str] = None) -> Path:
    """
    Ensure output directory exists and return Path object.
    
    Args:
        output_dir: Custom output directory path
        
    Returns:
        Path object for output directory
    """
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path("output")
    
    output_path.mkdir(exist_ok=True)
    return output_path


def get_file_size_kb(file_path: str) -> float:
    """
    Get file size in kilobytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in KB
    """
    return Path(file_path).stat().st_size / 1024