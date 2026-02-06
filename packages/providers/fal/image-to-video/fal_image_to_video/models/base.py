"""
Base model interface for FAL Image-to-Video models.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import fal_client

from ai_content_pipeline.registry import ModelRegistry
import ai_content_pipeline.registry_data  # side-effect: registers models
from ..utils.file_utils import download_video, ensure_output_directory


class BaseVideoModel(ABC):
    """
    Abstract base class for all FAL Image-to-Video models.
    """

    def __init__(self, model_key: str):
        """
        Initialize base model.

        Args:
            model_key: Model identifier (e.g., "hailuo", "sora_2")
        """
        self.model_key = model_key
        self._definition = ModelRegistry.get_by_provider_key(model_key)
        self.endpoint = self._definition.endpoint
        self.display_name = self._definition.name
        self.price_per_second = self._definition.pricing

    @abstractmethod
    def validate_parameters(self, **kwargs) -> Dict[str, Any]:
        """
        Validate model-specific parameters.

        Returns:
            Dictionary of validated parameters

        Raises:
            ValueError: If parameters are invalid
        """
        pass

    @abstractmethod
    def prepare_arguments(
        self,
        prompt: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare API arguments for the model.

        Args:
            prompt: Text description for video generation
            image_url: URL of input image
            **kwargs: Model-specific parameters

        Returns:
            Dictionary of API arguments
        """
        pass

    def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process API response and extract video info.

        Args:
            response: Raw API response

        Returns:
            Processed video information
        """
        video_info = response.get("video", {})
        return {
            "url": video_info.get("url"),
            "content_type": video_info.get("content_type"),
            "file_name": video_info.get("file_name"),
            "file_size": video_info.get("file_size"),
            "duration": video_info.get("duration"),
            "fps": video_info.get("fps"),
            "width": video_info.get("width"),
            "height": video_info.get("height")
        }

    def generate(
        self,
        prompt: str,
        image_url: str,
        output_dir: Optional[str] = None,
        output_filename: Optional[str] = None,
        use_async: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video using the model.

        Args:
            prompt: Text description for video generation
            image_url: URL of input image
            output_dir: Custom output directory
            output_filename: Custom output filename (e.g., "scene_1.mp4")
            use_async: Whether to use async processing
            **kwargs: Model-specific parameters

        Returns:
            Dictionary containing generation results
        """
        try:
            # Validate parameters
            validated_params = self.validate_parameters(**kwargs)

            # Prepare API arguments
            arguments = self.prepare_arguments(prompt, image_url, **validated_params)

            # Log generation info
            self._log_generation_start(prompt, image_url, **validated_params)

            # Make API call
            start_time = time.time()

            def on_queue_update(update):
                if hasattr(update, 'logs') and update.logs:
                    for log in update.logs:
                        print(f"  {log.get('message', str(log))}")

            if use_async:
                result = self._generate_async(arguments)
            else:
                result = fal_client.subscribe(
                    self.endpoint,
                    arguments=arguments,
                    with_logs=True,
                    on_queue_update=on_queue_update
                )

            processing_time = time.time() - start_time
            print(f"✅ Generation completed in {processing_time:.2f} seconds")

            # Process response
            video_info = self.process_response(result)
            if not video_info.get("url"):
                raise Exception("No video URL in response")

            # Download video
            output_directory = ensure_output_directory(output_dir)
            local_path = download_video(
                video_info["url"],
                output_directory,
                self.model_key,
                filename=output_filename
            )

            # Calculate cost estimate using model-specific estimate_cost method
            duration = validated_params.get("duration", 5)
            if isinstance(duration, str):
                duration = int(duration.replace("s", ""))
            # Remove duration from kwargs to avoid duplicate argument error
            cost_params = {k: v for k, v in validated_params.items() if k != "duration"}
            cost_estimate = self.estimate_cost(duration, **cost_params)

            return {
                "success": True,
                "model": self.display_name,
                "model_key": self.model_key,
                "prompt": prompt,
                "video": video_info,
                "local_path": local_path,
                "processing_time": processing_time,
                "cost_estimate": cost_estimate,
                **validated_params
            }

        except Exception as e:
            print(f"❌ Error during video generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.display_name,
                "model_key": self.model_key,
                "prompt": prompt
            }

    def _generate_async(
        self,
        arguments: Dict[str, Any],
        timeout: int = 600,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Handle async generation with polling.

        Args:
            arguments: API arguments for generation
            timeout: Maximum wait time in seconds (default: 600 = 10 minutes)
            poll_interval: Time between status checks in seconds (default: 5)

        Returns:
            API result dictionary

        Raises:
            TimeoutError: If generation exceeds timeout
            Exception: If generation fails
        """
        handler = fal_client.submit(self.endpoint, arguments=arguments)
        request_id = handler.request_id
        print(f"📤 Request submitted: {request_id}")

        start_time = time.time()
        max_iterations = timeout // poll_interval

        for iteration in range(max_iterations):
            elapsed = time.time() - start_time
            status = fal_client.status(self.endpoint, request_id, with_logs=True)
            print(f"   Status: {status.status} ({elapsed:.0f}s elapsed)")

            if status.status == "COMPLETED":
                return fal_client.result(self.endpoint, request_id)
            elif status.status == "FAILED":
                raise Exception(f"Generation failed: {status}")

            time.sleep(poll_interval)

        # Timeout reached
        elapsed = time.time() - start_time
        raise TimeoutError(
            f"Generation timed out after {elapsed:.0f}s (request_id: {request_id}). "
            f"The request may still be processing - check FAL dashboard."
        )

    def _log_generation_start(self, prompt: str, image_url: str, **params):
        """Log generation start with parameters."""
        print(f"🎬 Generating video with {self.display_name}...")
        print(f"   Prompt: {prompt[:100]}...")
        print(f"   Image: {image_url[:50]}...")
        for key, value in params.items():
            if value is not None:
                print(f"   {key}: {value}")

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and capabilities."""
        pass

    def estimate_cost(self, duration: int, **kwargs) -> float:
        """Estimate cost for generation."""
        price = self.price_per_second
        if isinstance(price, dict):
            if kwargs.get("generate_audio") and "cost_with_audio" in price:
                price = price["cost_with_audio"]
            elif "cost_no_audio" in price:
                price = price["cost_no_audio"]
            elif "cost" in price:
                price = price["cost"]
            else:
                # Use first numeric value found
                for v in price.values():
                    if isinstance(v, (int, float)):
                        price = v
                        break
                else:
                    return 0.0
        return price * duration
