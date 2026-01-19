"""
AI Content Generation Suite - Consolidated Setup Script

This setup.py consolidates all packages in the AI Content Generation Suite
into a single installable package with optional dependencies.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Package metadata
PACKAGE_NAME = "video_ai_studio"
VERSION = "1.0.15"
AUTHOR = "donghao zhang"
AUTHOR_EMAIL = "zdhpeter@gmail.com"
DESCRIPTION = "Comprehensive AI content generation suite with multiple providers and services"
URL = "https://github.com/donghaozhang/veo3-fal-video-ai"

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, encoding="utf-8") as f:
        long_description = f.read()

# Read requirements from root requirements.txt
def read_requirements():
    """Read requirements from root requirements.txt file."""
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        with open(req_file) as f:
            return [
                line.strip() for line in f 
                if line.strip() and not line.startswith("#")
            ]
    return []

# Base requirements (essential dependencies)
install_requires = [
    "python-dotenv>=1.0.0",
    "requests>=2.31.0", 
    "typing-extensions>=4.0.0",
    "pyyaml>=6.0",
    "pathlib2>=2.3.7",
    "argparse>=1.4.0",
    # Essential AI service clients
    "fal-client>=0.4.0",
    "replicate>=0.15.0",
    "openai>=1.0.0,<2.0.0",
    "google-generativeai>=0.2.0",
    "elevenlabs>=1.0.0",
    # Essential media processing
    "Pillow>=10.0.0",
    "httpx>=0.25.0",
    "aiohttp>=3.8.0",
]

# Optional requirements organized by functionality
extras_require = {
    # Core AI Content Pipeline
    "pipeline": [
        "pyyaml>=6.0",
        "pathlib2>=2.3.7",
    ],
    
    # Google Cloud Services (optional)
    "google-cloud": [
        "google-cloud-aiplatform>=1.38.0",
        "google-cloud-storage>=2.10.0",
        "google-auth>=2.23.0",
    ],
    
    # Video Processing
    "video": [
        "moviepy>=1.0.3",
        "ffmpeg-python>=0.2.0",
    ],
    
    # Image Processing
    "image": [
        "Pillow>=10.0.0",
    ],
    
    # Development Tools
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "black>=22.0.0",
        "flake8>=4.0.0",
        "mypy>=1.0.0",
    ],
    
    # Jupyter/Notebook Support
    "jupyter": [
        "jupyter>=1.0.0",
        "ipython>=8.0.0",
        "notebook>=7.0.0",
        "matplotlib>=3.5.0",
    ],
    
    # MCP Server Support
    "mcp": [
        "mcp>=1.0.0",
    ],
}

# Convenience groups
extras_require["all"] = list(set(
    req for group in ["pipeline", "google-cloud", "video", "dev", "jupyter", "mcp"] 
    for req in extras_require[group]
))

extras_require["cloud"] = list(set(
    req for group in ["google-cloud"] 
    for req in extras_require[group]
))

extras_require["media"] = list(set(
    req for group in ["video", "image"] 
    for req in extras_require[group]
))

# Find standard packages
standard_packages = find_packages(include=['packages', 'packages.*'])

# Add packages from hyphenated directories that find_packages can't discover
# Python package names cannot contain hyphens, so these must be manually specified
fal_subpackages = [
    # image-to-image
    'fal_image_to_image',
    'fal_image_to_image.config',
    'fal_image_to_image.models',
    'fal_image_to_image.utils',
    # image-to-video
    'fal_image_to_video',
    'fal_image_to_video.config',
    'fal_image_to_video.models',
    'fal_image_to_video.utils',
    # text-to-video
    'fal_text_to_video',
    'fal_text_to_video.config',
    'fal_text_to_video.models',
    'fal_text_to_video.utils',
    # video-to-video
    'fal_video_to_video',
    'fal_video_to_video.config',
    'fal_video_to_video.models',
    'fal_video_to_video.utils',
    # avatar-generation
    'fal_avatar',
    'fal_avatar.config',
    'fal_avatar.models',
]

all_packages = standard_packages + fal_subpackages

# Package directory mappings for hyphenated directories
package_dir = {
    'fal_image_to_image': 'packages/providers/fal/image-to-image/fal_image_to_image',
    'fal_image_to_video': 'packages/providers/fal/image-to-video/fal_image_to_video',
    'fal_text_to_video': 'packages/providers/fal/text-to-video/fal_text_to_video',
    'fal_video_to_video': 'packages/providers/fal/video-to-video/fal_video_to_video',
    'fal_avatar': 'packages/providers/fal/avatar-generation/fal_avatar',
}

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=all_packages,
    package_dir=package_dir,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires=">=3.10",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            # AI Content Pipeline
            "ai-content-pipeline=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
            "aicp=packages.core.ai_content_pipeline.ai_content_pipeline.__main__:main",
            # FAL Image-to-Video CLI
            "fal-image-to-video=fal_image_to_video.cli:main",
            # FAL Text-to-Video CLI
            "fal-text-to-video=fal_text_to_video.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "packages.core.ai_content_pipeline": [
            "config/*.yaml",
            "examples/*.yaml", 
            "examples/*.json",
            "docs/*.md",
        ],
        "packages.providers.fal.image_to_image": [
            "config/*.json",
            "docs/*.md",
            "examples/*.py",
        ],
        "packages.services.text_to_speech": [
            "config/*.json",
            "examples/*.py",
        ],
        "": [
            "input/*",
            "output/*",
            "docs/*.md",
        ],
    },
    zip_safe=False,
    keywords="ai, content generation, images, videos, audio, fal, elevenlabs, google, parallel processing, veo, pipeline",
    project_urls={
        "Documentation": f"{URL}/blob/main/README.md",
        "Source": URL,
        "Tracker": f"{URL}/issues",
        "Changelog": f"{URL}/blob/main/CHANGELOG.md",
    },
)