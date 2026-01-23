"""
Image-related step executors for AI Content Pipeline.

Contains executors for text-to-image, image understanding, prompt generation,
image-to-image, split-image, and upscale-image.
"""

import time
from pathlib import Path
from typing import Any, Dict, Optional

from .base import BaseStepExecutor


class TextToImageExecutor(BaseStepExecutor):
    """Executor for text-to-image generation steps."""

    def __init__(self, generator):
        """
        Initialize executor with generator.

        Args:
            generator: UnifiedTextToImageGenerator instance
        """
        self.generator = generator

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute text-to-image generation."""
        params = self._merge_params(step.params, chain_config, kwargs)

        result = self.generator.generate(input_data, step.model, **params)

        return {
            "success": result.success,
            "output_path": result.output_path,
            "output_url": result.output_url,
            "processing_time": result.processing_time,
            "cost": result.cost_estimate,
            "model": result.model_used,
            "metadata": result.metadata,
            "error": result.error
        }


class ImageUnderstandingExecutor(BaseStepExecutor):
    """Executor for image understanding/analysis steps."""

    def __init__(self, generator):
        """
        Initialize executor with generator.

        Args:
            generator: UnifiedImageUnderstandingGenerator instance
        """
        self.generator = generator

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute image understanding/analysis."""
        # Get analysis prompt from step params or kwargs
        analysis_prompt = step.params.get("prompt", kwargs.get("prompt", None))
        question = step.params.get("question", kwargs.get("question", None))

        params = self._merge_params(
            step.params, chain_config, kwargs,
            exclude_keys=["prompt", "question"]
        )

        # Add analysis prompt or question if provided
        if analysis_prompt:
            params["analysis_prompt"] = analysis_prompt
        if question:
            params["question"] = question

        result = self.generator.analyze(
            image_path=input_data,
            model=step.model,
            **params
        )

        return {
            "success": result.success,
            "output_text": result.output_text,
            "processing_time": result.processing_time,
            "cost": result.cost_estimate,
            "model": result.model_used,
            "metadata": result.metadata,
            "error": result.error
        }


class PromptGenerationExecutor(BaseStepExecutor):
    """Executor for prompt generation steps."""

    def __init__(self, generator):
        """
        Initialize executor with generator.

        Args:
            generator: UnifiedPromptGenerator instance
        """
        self.generator = generator

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute prompt generation from image."""
        # Get specific parameters
        background_context = step.params.get(
            "background_context", kwargs.get("background_context", "")
        )
        video_style = step.params.get("video_style", kwargs.get("video_style", ""))
        duration_preference = step.params.get(
            "duration_preference", kwargs.get("duration_preference", "")
        )

        params = self._merge_params(
            step.params, chain_config, kwargs,
            exclude_keys=["background_context", "video_style", "duration_preference"]
        )

        # Add specific parameters if provided
        if background_context:
            params["background_context"] = background_context
        if video_style:
            params["video_style"] = video_style
        if duration_preference:
            params["duration_preference"] = duration_preference

        result = self.generator.generate(
            image_path=input_data,
            model=step.model,
            **params
        )

        return {
            "success": result.success,
            "output_text": result.output_text,
            "extracted_prompt": result.extracted_prompt,
            "processing_time": result.processing_time,
            "cost": result.cost_estimate,
            "model": result.model_used,
            "metadata": result.metadata,
            "error": result.error
        }


class ImageToImageExecutor(BaseStepExecutor):
    """Executor for image-to-image transformation steps."""

    def __init__(self, generator):
        """
        Initialize executor with generator.

        Args:
            generator: UnifiedImageToImageGenerator instance
        """
        self.generator = generator

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute image-to-image transformation."""
        # Get prompt from step params or kwargs
        prompt = step.params.get("prompt", kwargs.get("prompt", "modify this image"))

        params = self._merge_params(
            step.params, chain_config, kwargs,
            exclude_keys=["prompt"]
        )

        result = self.generator.generate(
            source_image=input_data,
            prompt=prompt,
            model=step.model,
            **params
        )

        return {
            "success": result.success,
            "output_path": result.output_path,
            "output_url": result.output_url,
            "processing_time": result.processing_time,
            "cost": result.cost_estimate,
            "model": result.model_used,
            "metadata": result.metadata,
            "error": result.error
        }


class SplitImageExecutor(BaseStepExecutor):
    """Executor for splitting grid images into individual panels."""

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute image splitting.

        Splits a grid image (2x2 or 3x3) into individual panel images.
        """
        start_time = time.time()
        params = step.params or {}

        try:
            # Import here to avoid circular imports
            from ...image_splitter import split_grid_image, SplitConfig

            # Get input image path
            image_path = input_data
            if isinstance(input_data, dict):
                image_path = input_data.get("output_path") or input_data.get("path")

            if not image_path:
                return {
                    "success": False,
                    "error": "No input image provided for split_image step"
                }

            # Configure split
            config = SplitConfig(
                grid=params.get("grid", "2x2"),
                output_format=params.get("output_format", "png"),
                naming_pattern=params.get("naming", "panel_{n}"),
                quality=params.get("quality", 95),
            )

            # Determine output directory
            output_dir = chain_config.get("output_dir", "output")
            step_name = getattr(step, 'name', None) or "split_panels"
            step_output_dir = Path(output_dir) / step_name

            # Split image
            panel_paths = split_grid_image(str(image_path), str(step_output_dir), config)

            processing_time = time.time() - start_time

            return {
                "success": True,
                "output_paths": panel_paths,
                "output_path": panel_paths[0] if panel_paths else None,
                "panel_count": len(panel_paths),
                "grid": config.grid,
                "processing_time": processing_time,
                "cost": 0,  # Local operation, no API cost
                "metadata": {
                    "grid": config.grid,
                    "panels": len(panel_paths),
                    "paths": panel_paths,
                    "output_format": config.output_format,
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }


class UpscaleImageExecutor(BaseStepExecutor):
    """Executor for upscaling images using SeedVR2."""

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute image upscaling.

        Upscales an image using FAL SeedVR2 API.
        """
        start_time = time.time()
        params = step.params or {}

        try:
            # Import here to avoid circular imports
            from ...grid_generator import upscale_image

            # Get input image path
            image_path = input_data
            if isinstance(input_data, dict):
                image_path = input_data.get("output_path") or input_data.get("path")

            if not image_path:
                return {
                    "success": False,
                    "error": "No input image provided for upscale_image step"
                }

            # Determine output directory
            output_dir = chain_config.get("output_dir", "output")

            # Call upscale function
            result = upscale_image(
                image_path=str(image_path),
                factor=params.get("factor", 2),
                target=params.get("target"),
                output_dir=output_dir,
                output_format=params.get("output_format", "png"),
            )

            if not result.success:
                return {
                    "success": False,
                    "error": result.error,
                    "processing_time": time.time() - start_time,
                }

            return {
                "success": True,
                "output_path": result.local_path,
                "output_url": result.image_url,
                "upscaled_size": result.upscaled_size,
                "processing_time": result.processing_time,
                "cost": result.cost or 0,
                "metadata": result.metadata,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
            }
