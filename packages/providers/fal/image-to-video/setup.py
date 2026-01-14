"""Setup for FAL Image-to-Video Generator package."""

from setuptools import setup, find_packages

setup(
    name="fal-image-to-video",
    version="1.0.0",
    description="FAL AI Image-to-Video Generator (Veo 3.1, Sora 2, Kling, Hailuo)",
    author="AI Content Pipeline",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "fal-client>=0.5.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "fal-image-to-video=fal_image_to_video.cli:main",
        ],
    },
)
