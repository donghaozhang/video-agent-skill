"""
AI Content Generation Suite - Consolidated Setup Script

This setup.py consolidates all packages in the AI Content Generation Suite
into a single installable package with optional dependencies.
"""

import re
from setuptools import setup, find_packages
from pathlib import Path

# Read version from the single source of truth (_version.py)
# Reason: We parse the file as text instead of importing to avoid triggering
# the full package import chain (which requires installed dependencies).
_version_file = Path(__file__).parent / "packages" / "core" / "ai_content_pipeline" / "ai_content_pipeline" / "_version.py"
_version_match = re.search(
    r'^__version__\s*=\s*["\']([^"\']+)["\']',
    _version_file.read_text(encoding="utf-8"),
    re.MULTILINE,
)
if not _version_match:
    raise RuntimeError("Unable to find __version__ in _version.py")
VERSION = _version_match.group(1)

# Package metadata
PACKAGE_NAME = "video_ai_studio"
AUTHOR = "donghao zhang"
AUTHOR_EMAIL = "zdhpeter@gmail.com"
DESCRIPTION = "Comprehensive AI content generation suite with multiple providers and services"
URL = "https://github.com/donghaozhang/video-agent-skill"

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
    "click>=8.0.0",
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

# Package directory mappings for hyphenated directories and nested packages
# Reason: find_packages() can't discover packages inside hyphenated directories,
# so we define the mapping first, then auto-discover subpackages from each path.
package_dir = {
    # Map ai_content_platform packages to their location
    'ai_content_platform': 'packages/core/ai_content_platform',
    # FAL provider packages
    'fal_image_to_image': 'packages/providers/fal/image-to-image/fal_image_to_image',
    'fal_image_to_video': 'packages/providers/fal/image-to-video/fal_image_to_video',
    'fal_text_to_video': 'packages/providers/fal/text-to-video/fal_text_to_video',
    'fal_video_to_video': 'packages/providers/fal/video-to-video/fal_video_to_video',
    'fal_avatar': 'packages/providers/fal/avatar-generation/fal_avatar',
    'fal_speech_to_text': 'packages/providers/fal/speech-to-text/fal_speech_to_text',
    'fal_text_to_image': 'packages/providers/fal/text-to-image/fal_text_to_image',
    # AI Content Pipeline (central registry)
    'ai_content_pipeline': 'packages/core/ai_content_pipeline/ai_content_pipeline',
}

# Auto-discover all packages instead of maintaining a manual list.
# 1) Standard packages under packages/ tree
all_packages = find_packages(include=['packages', 'packages.*'])

# 2) Packages from hyphenated directories (mapped via package_dir)
for pkg_name, pkg_path in package_dir.items():
    if Path(pkg_path).is_dir():
        all_packages.append(pkg_name)
        sub_pkgs = find_packages(where=pkg_path)
        all_packages.extend(f"{pkg_name}.{sub}" for sub in sub_pkgs)

# 3) ai_content_platform (vimax CLI) from packages/core/
all_packages.extend(
    find_packages(where='packages/core', include=['ai_content_platform', 'ai_content_platform.*'])
)

# Deduplicate
all_packages = sorted(set(all_packages))

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
            # ViMax integrated as aicp subgroup (no standalone entry point)
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