"""
FAL Text-to-Video Generator using class-based model architecture.

This module provides a unified interface for text-to-video generation
using various FAL AI models (Kling v2.6 Pro, Sora 2, Sora 2 Pro).
"""

import os
from typing import Dict, Any, Optional, Type, Union
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .models import (
    BaseTextToVideoModel,
    Kling26ProModel,
    KlingV3StandardModel,
    KlingV3ProModel,
    Sora2Model,
    Sora2ProModel,
    GrokImagineModel
)
from .config import SUPPORTED_MODELS, MODEL_INFO


# Model class registry
MODEL_CLASSES: Dict[str, Type[BaseTextToVideoModel]] = {
    "kling_2_6_pro": Kling26ProModel,
    "kling_3_standard": KlingV3StandardModel,
    "kling_3_pro": KlingV3ProModel,
    "sora_2": Sora2Model,
    "sora_2_pro": Sora2ProModel,
    "grok_imagine": GrokImagineModel
}


class FALTextToVideoGenerator:
    """
    Unified FAL Text-to-Video Generator supporting multiple models.

    This generator provides a consistent interface for generating videos
    from text prompts using different FAL AI models.
    """

    def __init__(self, default_model: str = "kling_2_6_pro"):
        """
        Initialize the generator.

        Args:
            default_model: Default model to use for generation
        """
        if default_model not in MODEL_CLASSES:
            raise ValueError(
                f"Unknown model: {default_model}. "
                f"Available: {list(MODEL_CLASSES.keys())}"
            )
        self.default_model = default_model

    def _get_model(self, model_key: str) -> BaseTextToVideoModel:
        """Get model instance by key."""
        if model_key not in MODEL_CLASSES:
            raise ValueError(
                f"Unknown model: {model_key}. "
                f"Available: {list(MODEL_CLASSES.keys())}"
            )
        return MODEL_CLASSES[model_key]()

    def generate_video(
        self,
        prompt: str,
        model: Optional[str] = None,
        output_dir: Optional[Union[str, Path]] = None,
        timeout: int = 600,
        verbose: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt.

        Args:
            prompt: Text description for video generation
            model: Model key (default: self.default_model)
            output_dir: Directory to save output (str or Path)
            timeout: Maximum wait time in seconds
            verbose: Enable verbose output
            **kwargs: Model-specific parameters

        Returns:
            Dict with generation results
        """
        model_key = model or self.default_model
        model_instance = self._get_model(model_key)

        # Convert string to Path if needed
        if output_dir is not None and isinstance(output_dir, str):
            output_dir = Path(output_dir)

        return model_instance.generate(
            prompt=prompt,
            output_dir=output_dir,
            timeout=timeout,
            verbose=verbose,
            **kwargs
        )

    def estimate_cost(
        self,
        model: Optional[str] = None,
        **kwargs
    ) -> float:
        """
        Estimate cost for video generation.

        Args:
            model: Model key (default: self.default_model)
            **kwargs: Model-specific parameters affecting cost

        Returns:
            Estimated cost in USD
        """
        model_key = model or self.default_model
        model_instance = self._get_model(model_key)
        return model_instance.estimate_cost(**kwargs)

    def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get model information.

        Args:
            model: Model key (default: self.default_model)

        Returns:
            Dict with model information
        """
        model_key = model or self.default_model
        model_instance = self._get_model(model_key)
        return model_instance.get_model_info()

    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available models with their information.

        Returns:
            Dict mapping model keys to their information
        """
        result = {}
        for model_key in MODEL_CLASSES:
            model_instance = self._get_model(model_key)
            result[model_key] = model_instance.get_model_info()
        return result

    def compare_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Compare all available models.

        Returns:
            Dict with comparison information for each model
        """
        comparison = {}
        for model_key in MODEL_CLASSES:
            info = MODEL_INFO.get(model_key, {})
            model_instance = self._get_model(model_key)

            comparison[model_key] = {
                "name": info.get("name", model_key),
                "provider": info.get("provider", "FAL AI"),
                "max_duration": info.get("max_duration", "N/A"),
                "features": info.get("features", []),
                "endpoint": model_instance.endpoint,
                "pricing": model_instance.pricing
            }

        return comparison

    @staticmethod
    def get_available_models() -> list:
        """Get list of available model keys."""
        return list(MODEL_CLASSES.keys())
