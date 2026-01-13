"""
Base class for text-to-video models.
"""

import os
import time
import requests
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import fal_client
except ImportError:
    raise ImportError("fal-client not installed. Run: pip install fal-client")

from ..config.constants import MODEL_ENDPOINTS, MODEL_PRICING, MODEL_DISPLAY_NAMES


class BaseTextToVideoModel(ABC):
    """
    Abstract base class for text-to-video models.

    All model implementations must inherit from this class and implement
    the abstract methods.
    """

    def __init__(self, model_key: str):
        """
        Initialize the model.

        Args:
            model_key: Model identifier (e.g., "sora_2", "kling_2_6_pro")
        """
        self.model_key = model_key
        self.endpoint = MODEL_ENDPOINTS.get(model_key)
        self.display_name = MODEL_DISPLAY_NAMES.get(model_key, model_key)
        self.pricing = MODEL_PRICING.get(model_key, {})

        if not self.endpoint:
            raise ValueError(f"Unknown model: {model_key}")

    @abstractmethod
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate and normalize input parameters.

        Args:
            **kwargs: Model-specific parameters

        Returns:
            Dict with validated parameters

        Raises:
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    def prepare_arguments(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare arguments for the FAL API call.

        Args:
            prompt: Text description for video generation
            **kwargs: Additional model-specific parameters

        Returns:
            Dict of arguments for fal_client.subscribe()
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and capabilities."""
        pass

    @abstractmethod
    def estimate_cost(self, **kwargs) -> float:
        """
        Estimate cost for generation.

        Args:
            **kwargs: Parameters that affect cost (duration, resolution, etc.)

        Returns:
            Estimated cost in USD
        """
        pass

    def generate(
        self,
        prompt: str,
        output_dir: Optional[Path] = None,
        timeout: int = 600,
        verbose: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt.

        Args:
            prompt: Text description for video generation
            output_dir: Directory to save output (default: ./output)
            timeout: Maximum wait time in seconds
            verbose: Enable verbose output
            **kwargs: Model-specific parameters

        Returns:
            Dict with generation results
        """
        output_dir = output_dir or Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        cost = 0.0  # Initialize to handle errors before cost assignment

        try:
            # Validate parameters
            validated_params = self.validate_parameters(**kwargs)

            # Estimate cost
            cost = self.estimate_cost(**validated_params)

            if verbose:
                print(f"Generating video with {self.display_name}...")
                print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
                print(f"Estimated cost: ${cost:.2f}")

            # Prepare API arguments
            arguments = self.prepare_arguments(prompt, **validated_params)

            if verbose:
                print("Submitting generation request...")

            # Call FAL API
            result = fal_client.subscribe(
                self.endpoint,
                arguments=arguments,
                with_logs=verbose,
                timeout=timeout
            )

            if verbose:
                print("Video generation completed!")

            # Extract video URL
            video_url = result.get('video', {}).get('url')
            if not video_url:
                raise Exception("No video URL in response")

            # Generate filename
            timestamp = int(time.time())
            safe_prompt = "".join(
                c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')
            ).rstrip().replace(' ', '_')
            filename = f"{self.model_key}_{safe_prompt}_{timestamp}.mp4"

            # Download video
            local_path = self._download_video(video_url, output_dir / filename, verbose)

            return {
                "success": True,
                "video_url": video_url,
                "local_path": str(local_path),
                "filename": filename,
                "prompt": prompt,
                "model": self.model_key,
                "model_name": self.display_name,
                "cost_usd": cost,
                "parameters": validated_params,
                "metadata": result
            }

        except Exception as e:
            if verbose:
                print(f"Generation failed: {e}")

            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
                "model": self.model_key,
                "estimated_cost": cost
            }

    def _download_video(
        self,
        url: str,
        local_path: Path,
        verbose: bool = True
    ) -> Path:
        """Download video from URL to local file."""
        if verbose:
            print(f"Downloading video: {local_path.name}")

        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if verbose and total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rDownloading: {progress:.1f}%", end='', flush=True)

        if verbose and total_size > 0:
            print()  # New line after progress
            print(f"Download completed: {local_path}")

        return local_path
