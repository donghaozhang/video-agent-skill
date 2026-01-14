"""Setup for FAL Text-to-Video Generator package."""

from setuptools import setup, find_packages

setup(
    name="fal-text-to-video",
    version="1.0.0",
    description="FAL AI Text-to-Video Generator (Sora 2, Kling, Veo)",
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
            "fal-text-to-video=fal_text_to_video.cli:main",
        ],
    },
)
