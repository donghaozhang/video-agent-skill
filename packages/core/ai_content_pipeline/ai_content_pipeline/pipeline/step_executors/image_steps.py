"""
Image-related step executors for AI Content Pipeline.

Contains executors for text-to-image, image understanding, prompt generation, and image-to-image.
"""

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
