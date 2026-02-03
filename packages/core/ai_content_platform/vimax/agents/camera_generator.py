"""
Camera Image Generator Agent

Generates videos from storyboard images, applying camera movements
and animations based on shot descriptions.
"""

from typing import Optional, List
from datetime import datetime
import logging
from pathlib import Path

from .base import BaseAgent, AgentConfig, AgentResult
from .storyboard_artist import StoryboardResult
from ..adapters import VideoGeneratorAdapter, VideoAdapterConfig
from ..interfaces import (
    ShotDescription, ImageOutput, VideoOutput, PipelineOutput,
)


class CameraGeneratorConfig(AgentConfig):
    """Configuration for CameraImageGenerator."""

    name: str = "CameraImageGenerator"
    video_model: str = "kling"
    default_duration: float = 5.0
    output_dir: str = "media/generated/vimax/videos"


class CameraImageGenerator(BaseAgent[StoryboardResult, PipelineOutput]):
    """
    Agent that generates videos from storyboard images.

    Usage:
        generator = CameraImageGenerator()
        result = await generator.process(storyboard)
        if result.success:
            print(f"Final video: {result.result.final_video.video_path}")
    """

    def __init__(self, config: Optional[CameraGeneratorConfig] = None) -> None:
        """Initialize the CameraImageGenerator.

        Args:
            config: Optional configuration overriding defaults.

        Returns:
            None
        """
        super().__init__(config or CameraGeneratorConfig())
        self.config: CameraGeneratorConfig = self.config
        self._video_adapter: Optional[VideoGeneratorAdapter] = None
        self.logger = logging.getLogger("vimax.agents.camera_generator")

    async def _ensure_adapter(self):
        """Initialize the video adapter lazily.

        Creates and initializes the VideoGeneratorAdapter on first use.
        """
        if self._video_adapter is None:
            self._video_adapter = VideoGeneratorAdapter(
                VideoAdapterConfig(
                    model=self.config.video_model,
                    output_dir=self.config.output_dir,
                )
            )
            await self._video_adapter.initialize()

    def _get_motion_prompt(self, shot: ShotDescription) -> str:
        """Generate motion prompt from shot description."""
        parts = []

        # Use video_prompt if available
        if shot.video_prompt:
            parts.append(shot.video_prompt)
        else:
            # Build from shot description
            parts.append(shot.description)

        # Add camera movement hints
        movement_hints = {
            "pan": "smooth horizontal camera pan",
            "tilt": "smooth vertical camera tilt",
            "zoom": "gradual zoom",
            "dolly": "camera moving forward/backward",
            "tracking": "camera tracking subject movement",
            "static": "subtle ambient motion, no camera movement",
        }

        movement = shot.camera_movement
        if hasattr(movement, 'value'):
            movement = movement.value

        if movement in movement_hints:
            parts.append(movement_hints[movement])

        return ", ".join(parts)

    async def process(self, storyboard: StoryboardResult) -> AgentResult[PipelineOutput]:
        """
        Generate videos from storyboard.

        Args:
            storyboard: Storyboard with images

        Returns:
            AgentResult containing PipelineOutput with videos
        """
        await self._ensure_adapter()

        self.logger.info(f"Generating videos for: {storyboard.title}")

        try:
            output = PipelineOutput(
                pipeline_name=f"camera_generator_{storyboard.title}",
                output_directory=self.config.output_dir,
            )

            # Create output directory
            output_dir = Path(self.config.output_dir) / storyboard.title.replace(" ", "_")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Match images with shots
            image_index = 0
            for scene in storyboard.scenes:
                for shot in scene.shots:
                    if image_index >= len(storyboard.images):
                        break

                    image = storyboard.images[image_index]
                    image_index += 1

                    self.logger.info(f"Generating video for shot: {shot.shot_id}")

                    # Get motion prompt
                    motion_prompt = self._get_motion_prompt(shot)

                    # Generate video
                    output_path = str(output_dir / f"{shot.shot_id}.mp4")
                    video = await self._video_adapter.generate(
                        image_path=image.image_path,
                        prompt=motion_prompt,
                        duration=shot.duration_seconds or self.config.default_duration,
                        output_path=output_path,
                    )

                    output.add_video(video)

            # Concatenate all videos
            if output.videos:
                final_path = str(output_dir / "final_video.mp4")
                final_video = await self._video_adapter.concatenate_videos(
                    output.videos,
                    final_path,
                )
                output.final_video = final_video

            output.completed_at = datetime.now()

            final_duration = output.final_video.duration if output.final_video else 0
            self.logger.info(
                f"Generated {len(output.videos)} videos, "
                f"final duration: {final_duration:.1f}s"
            )

            return AgentResult.ok(
                output,
                video_count=len(output.videos),
                total_duration=final_duration,
                cost=output.total_cost,
            )

        except Exception as e:
            self.logger.exception("Video generation failed")
            return AgentResult.fail(str(e))

    async def generate_from_images(
        self,
        images: List[ImageOutput],
        prompts: List[str],
        durations: Optional[List[float]] = None,
    ) -> List[VideoOutput]:
        """
        Generate videos from images with prompts.

        Args:
            images: List of input images
            prompts: Motion prompts for each image
            durations: Optional durations for each video

        Returns:
            List of generated videos
        """
        await self._ensure_adapter()

        if len(images) != len(prompts):
            raise ValueError("Number of images must match number of prompts")

        durations = durations or [self.config.default_duration] * len(images)

        videos = []
        for i, (img, prompt, duration) in enumerate(zip(images, prompts, durations)):
            video = await self._video_adapter.generate(
                image_path=img.image_path,
                prompt=prompt,
                duration=duration,
            )
            videos.append(video)

        return videos
