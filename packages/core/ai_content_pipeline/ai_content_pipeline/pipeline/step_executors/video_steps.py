"""
Video-related step executors for AI Content Pipeline.

Contains executors for image-to-video, add-audio, upscale-video, and subtitle generation.
"""

import os
import time
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from .base import BaseStepExecutor


class TextToVideoExecutor(BaseStepExecutor):
    """Executor for text-to-video generation steps."""

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute text-to-video generation."""
        try:
            from fal_text_to_video import FALTextToVideoGenerator
        except ImportError as e:
            return self._create_error_result(
                f"fal_text_to_video module not available. "
                f"Install: pip install -e packages/providers/fal/text-to-video. Error: {e}",
                step.model
            )

        try:
            generator = FALTextToVideoGenerator()

            # Get prompt from input_data (text input) or step params
            prompt = input_data if isinstance(input_data, str) else step.params.get("prompt", "")

            # Use generated prompt from previous step if available
            if step_context and "generated_prompt" in step_context:
                prompt = step_context["generated_prompt"]
                print(f"Using generated prompt: {prompt[:100]}...")

            if not prompt:
                return self._create_error_result(
                    "No prompt provided for text-to-video generation",
                    step.model
                )

            params = self._merge_params(
                step.params, chain_config, kwargs,
                exclude_keys=["prompt"]
            )

            # Extract output_dir from params (it's added by _merge_params)
            output_dir = params.pop("output_dir", "output")

            print(f"Generating video with {step.model}...")
            print(f"Prompt: {prompt[:100]}...")

            result = generator.generate_video(
                prompt=prompt,
                model=step.model,
                output_dir=output_dir,
                **params
            )

            if result.get("success"):
                return {
                    "success": True,
                    "output_path": result.get("local_path"),
                    "output_url": result.get("video", {}).get("url"),
                    "processing_time": result.get("processing_time", 0),
                    "cost": result.get("cost_estimate", 0),
                    "model": result.get("model", step.model),
                    "metadata": {
                        "prompt": prompt,
                        "video_info": result.get("video", {}),
                        "model_key": result.get("model_key"),
                        **{k: v for k, v in result.items()
                           if k not in ["success", "local_path", "video", "processing_time",
                                       "cost_estimate", "model", "model_key", "prompt"]}
                    },
                    "error": None
                }
            else:
                return self._create_error_result(
                    result.get("error", "Text-to-video generation failed"),
                    step.model
                )

        except Exception as e:
            return self._create_error_result(
                f"Text-to-video generation failed: {str(e)}",
                step.model
            )


class ImageToVideoExecutor(BaseStepExecutor):
    """Executor for image-to-video generation steps."""

    def __init__(self, generator):
        """
        Initialize executor with generator.

        Args:
            generator: UnifiedImageToVideoGenerator instance
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
        """Execute image-to-video generation."""
        # Get prompt from step params, kwargs, or context
        prompt = step.params.get(
            "prompt",
            kwargs.get("prompt", "Create a cinematic video from this image")
        )

        # Use generated prompt from previous step if available
        if step_context and "generated_prompt" in step_context:
            prompt = step_context["generated_prompt"]
            print(f"Using generated prompt: {prompt[:100]}...")

        params = self._merge_params(
            step.params, chain_config, kwargs,
            exclude_keys=["prompt"]
        )

        # Handle multiple images from split_image step
        if isinstance(input_data, list):
            return self._process_multiple_images(step, input_data, prompt, params)

        # Single image processing
        return self._process_single_image(step, input_data, prompt, params)

    def _process_single_image(
        self,
        step,
        image_path: str,
        prompt: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single image to video."""
        input_dict = {
            "prompt": prompt,
            "image_path": image_path
        }

        result = self.generator.generate(
            input_data=input_dict,
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

    def _process_multiple_images(
        self,
        step,
        image_paths: list,
        prompt: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process multiple images to videos (from split_image step)."""
        print(f"Processing {len(image_paths)} images to videos...")

        all_results = []
        output_paths = []
        output_urls = []
        total_time = 0
        total_cost = 0
        errors = []

        for i, image_path in enumerate(image_paths):
            print(f"\n--- Video {i+1}/{len(image_paths)}: {Path(image_path).name} ---")

            input_dict = {
                "prompt": prompt,
                "image_path": image_path
            }

            try:
                result = self.generator.generate(
                    input_data=input_dict,
                    model=step.model,
                    **params
                )

                all_results.append(result)
                if result.success:
                    output_paths.append(result.output_path)
                    output_urls.append(result.output_url)
                    total_time += result.processing_time or 0
                    total_cost += result.cost_estimate or 0
                    print(f"   Video saved: {result.output_path}")
                else:
                    errors.append(f"Image {i+1}: {result.error}")
                    print(f"   Failed: {result.error}")
            except Exception as e:
                errors.append(f"Image {i+1}: {str(e)}")
                print(f"   Exception: {str(e)}")

        success = len(output_paths) > 0

        return {
            "success": success,
            "output_path": output_paths[0] if output_paths else None,
            "output_paths": output_paths,
            "output_url": output_urls[0] if output_urls else None,
            "output_urls": output_urls,
            "processing_time": total_time,
            "cost": total_cost,
            "model": step.model,
            "metadata": {
                "total_images": len(image_paths),
                "videos_generated": len(output_paths),
                "video_paths": output_paths,
            },
            "error": "; ".join(errors) if errors else None
        }


class AddAudioExecutor(BaseStepExecutor):
    """Executor for adding audio to video steps."""

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute add-audio step."""
        try:
            if input_data is None:
                return self._create_error_result(
                    "Video path is None - video from previous step not available",
                    step.model
                )

            # Import from the properly installed fal_video_to_video package
            try:
                from fal_video_to_video.generator import FALVideoToVideoGenerator
            except ImportError as e:
                return self._create_error_result(
                    f"fal_video_to_video module not available. "
                    f"Install: pip install -e packages/providers/fal/video-to-video. Error: {e}",
                    step.model
                )

            generator = FALVideoToVideoGenerator()

            params = self._merge_params(step.params, chain_config, kwargs)

            # Add audio to video
            result = generator.add_audio_to_local_video(
                video_path=input_data,
                model="thinksound",
                **params
            )

            # ThinksSound pricing: ~$0.001/second of audio generated
            cost = result.get("cost", 0)
            if cost == 0 and result.get("duration"):
                cost = result.get("duration", 0) * 0.001

            return {
                "success": result.get("success", False),
                "output_path": result.get("local_path"),
                "output_url": result.get("video_url"),
                "processing_time": result.get("processing_time", 0),
                "cost": cost,
                "model": "thinksound",
                "metadata": result.get("response", {}),
                "error": result.get("error")
            }

        except Exception as e:
            return self._create_error_result(
                f"Audio generation failed: {str(e)}",
                step.model
            )


class UpscaleVideoExecutor(BaseStepExecutor):
    """Executor for video upscaling steps."""

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute video upscaling step."""
        try:
            # Import from the properly installed fal_video_to_video package
            from fal_video_to_video.generator import FALVideoToVideoGenerator
        except ImportError as e:
            return self._create_error_result(
                f"fal_video_to_video module not available. "
                f"Install: pip install -e packages/providers/fal/video-to-video. Error: {e}",
                step.model
            )

        try:
            # Initialize upscaler
            upscaler = FALVideoToVideoGenerator()

            # Get parameters
            upscale_factor = step.params.get("upscale_factor", 2)
            target_fps = step.params.get("target_fps", None)

            print("Starting video upscaling...")
            print(f"Input video: {input_data}")
            print(f"Upscale factor: {upscale_factor}x")

            # Check if video file exists
            if not input_data or not os.path.exists(input_data):
                return self._create_error_result(
                    f"Video file not found: {input_data}",
                    step.model
                )

            # Execute upscaling
            start_time = time.time()

            result = upscaler.upscale_local_video(
                video_path=input_data,
                upscale_factor=upscale_factor,
                target_fps=target_fps,
                output_dir=chain_config.get("output_dir", "output")
            )

            processing_time = time.time() - start_time

            if result.get("success"):
                return {
                    "success": True,
                    "output_path": result.get("local_path"),
                    "output_url": result.get("video_url"),
                    "processing_time": processing_time,
                    "cost": result.get("cost", 1.50),
                    "model": step.model,
                    "metadata": {
                        "upscale_factor": upscale_factor,
                        "target_fps": target_fps,
                        "original_path": input_data,
                        "model_response": result
                    },
                    "error": None
                }
            else:
                return self._create_error_result(
                    f"Video upscaling failed: {result.get('error', 'Unknown error')}",
                    step.model
                )

        except Exception as e:
            return self._create_error_result(
                f"Video upscaling failed: {str(e)}",
                step.model
            )


class GenerateSubtitlesExecutor(BaseStepExecutor):
    """Executor for subtitle generation steps."""

    def execute(
        self,
        step,
        input_data: Any,
        chain_config: Dict[str, Any],
        step_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute subtitle generation step."""
        try:
            # Import from the properly installed video_utils package
            from video_utils import generate_subtitle_for_video
        except ImportError as e:
            return self._create_error_result(
                f"Could not import subtitle generation module. "
                f"Install video-tools package: pip install -e packages/services/video-tools. Error: {e}",
                step.model
            )

        try:
            # Get parameters
            subtitle_text = step.params.get("subtitle_text", "")
            format_type = step.params.get("format", "srt")
            words_per_second = step.params.get("words_per_second", 2.0)
            output_dir = step.params.get(
                "output_dir",
                chain_config.get("output_dir", "output")
            )

            # Use subtitle text from context if available
            if not subtitle_text and step_context:
                subtitle_text = step_context.get("generated_prompt") or step_context.get("subtitle_text", "")

            if not subtitle_text:
                return self._create_error_result(
                    "No subtitle text provided. Use 'subtitle_text' parameter or generate from previous prompt step.",
                    step.model
                )

            print("Starting subtitle generation...")
            print(f"Input video: {input_data}")
            print(f"Format: {format_type.upper()}")

            # Check if video file exists
            if not input_data or not os.path.exists(input_data):
                return self._create_error_result(
                    f"Video file not found: {input_data}",
                    step.model
                )

            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate output filename
            video_name = Path(input_data).stem
            output_subtitle_path = output_path / f"{video_name}.{format_type}"

            # Execute subtitle generation
            start_time = time.time()

            subtitle_path = generate_subtitle_for_video(
                video_path=Path(input_data),
                text=subtitle_text,
                format_type=format_type,
                words_per_second=words_per_second,
                output_path=output_subtitle_path
            )

            processing_time = time.time() - start_time

            if subtitle_path and os.path.exists(subtitle_path):
                # Copy the video file to output directory if not already there
                output_video_path = output_path / Path(input_data).name
                if not output_video_path.exists():
                    shutil.copy2(input_data, output_video_path)

                return {
                    "success": True,
                    "output_path": str(output_video_path),
                    "subtitle_path": str(subtitle_path),
                    "processing_time": processing_time,
                    "cost": 0.0,
                    "model": step.model,
                    "metadata": {
                        "format": format_type,
                        "words_per_second": words_per_second,
                        "subtitle_text": subtitle_text,
                        "subtitle_file": str(subtitle_path),
                        "video_file": str(output_video_path),
                        "subtitle_length": len(subtitle_text)
                    },
                    "error": None
                }
            else:
                return self._create_error_result(
                    "Subtitle generation failed: No output file created",
                    step.model
                )

        except Exception as e:
            return self._create_error_result(
                f"Subtitle generation failed: {str(e)}",
                step.model
            )
