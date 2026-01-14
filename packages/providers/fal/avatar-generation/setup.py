"""Setup for fal_avatar package."""

from setuptools import setup, find_packages

setup(
    name="fal_avatar",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fal-client",
        "python-dotenv",
        "requests",
    ],
    python_requires=">=3.8",
)
