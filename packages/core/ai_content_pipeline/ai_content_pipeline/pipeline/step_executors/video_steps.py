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

        # Prepare input data for the unified generator
        input_dict = {
            "prompt": prompt,
            "image_path": input_data
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
            print(f"Debug: video_path received = {input_data}")

            if input_data is None:
                return self._create_error_result(
                    "Video path is None - video from previous step not available",
                    step.model
                )

            # Try to import video-to-video module
            import sys
            fal_video_path = Path(__file__).parent.parent.parent.parent.parent / "fal_video_to_video"
            sys.path.insert(0, str(fal_video_path))
            from fal_video_to_video.generator import FALVideoToVideoGenerator

            generator = FALVideoToVideoGenerator()

            params = self._merge_params(step.params, chain_config, kwargs)

            # Add audio to video
            result = generator.add_audio_to_local_video(
                video_path=input_data,
                model="thinksound",
                **params
            )

            return {
                "success": result.get("success", False),
                "output_path": result.get("local_path"),
                "output_url": result.get("video_url"),
                "processing_time": result.get("processing_time", 0),
                "cost": 0.05,  # Approximate ThinksSound cost
                "model": "thinksound",
                "metadata": result.get("response", {}),
                "error": result.get("error")
            }

        except ImportError:
            return self._create_error_result(
                "Video-to-video module not available",
                step.model
            )
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
        import sys

        try:
            # Try multiple import paths for fal_video_to_video
            current_dir = os.getcwd()
            possible_paths = [
                os.path.join(os.path.dirname(current_dir), 'fal_video_to_video'),
                os.path.join(current_dir, '..', 'fal_video_to_video'),
                '/home/zdhpe/veo3-video-generation/fal_video_to_video'
            ]

            imported = False
            for fal_video_path in possible_paths:
                try:
                    if os.path.exists(fal_video_path) and fal_video_path not in sys.path:
                        sys.path.insert(0, fal_video_path)

                    from fal_video_to_video.generator import FALVideoToVideoGenerator
                    imported = True
                    break
                except ImportError:
                    continue

            if not imported:
                sys.path.insert(0, '/home/zdhpe/veo3-video-generation/fal_video_to_video')
                from fal_video_to_video.fal_video_to_video.generator import FALVideoToVideoGenerator

            # Initialize upscaler
            upscaler = FALVideoToVideoGenerator()

            # Get parameters
            upscale_factor = step.params.get("upscale_factor", 2)
            target_fps = step.params.get("target_fps", None)

            print(f"Starting video upscaling...")
            print(f"Input video: {input_data}")
            print(f"Upscale factor: {upscale_factor}x")

            # Check if video file exists
            if not os.path.exists(input_data):
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

        except ImportError as e:
            return self._create_error_result(
                f"Could not import video upscaling module: {e}",
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
        import sys

        try:
            # Import video tools subtitle generator
            video_tools_path = "/home/zdhpe/veo3-video-generation/video_tools"
            if video_tools_path not in sys.path:
                sys.path.append(video_tools_path)

            from video_utils.subtitle_generator import generate_subtitle_for_video

        except ImportError as e:
            return self._create_error_result(
                f"Could not import subtitle generation module: {e}",
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

            print(f"Starting subtitle generation...")
            print(f"Input video: {input_data}")
            print(f"Format: {format_type.upper()}")

            # Check if video file exists
            if not os.path.exists(input_data):
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
