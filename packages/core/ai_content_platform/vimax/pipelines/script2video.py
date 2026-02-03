"""
Script to Video Pipeline

Converts an existing script into a video:
1. Parse script
2. Generate storyboard
3. Generate videos
4. Concatenate to final video
"""

from typing import Optional, Union
from pathlib import Path
import logging
import json
from datetime import datetime

from pydantic import BaseModel, Field

from ..agents import (
    Script,
    StoryboardArtist, StoryboardArtistConfig,
    CameraImageGenerator, CameraGeneratorConfig,
)
from ..interfaces import PipelineOutput, CharacterPortraitRegistry


class Script2VideoConfig(BaseModel):
    """Configuration for Script2Video pipeline."""

    output_dir: str = "output/vimax/script2video"
    video_model: str = "kling"
    image_model: str = "nano_banana_pro"
    use_character_references: bool = True  # Use portraits for storyboard consistency

    storyboard_artist: Optional[StoryboardArtistConfig] = None
    camera_generator: Optional[CameraGeneratorConfig] = None


class Script2VideoResult(BaseModel):
    """Result from Script2Video pipeline."""

    success: bool
    script: Script
    portrait_registry: Optional[CharacterPortraitRegistry] = None
    used_references: bool = False
    output: Optional[PipelineOutput] = None
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_cost: float = 0.0
    errors: list = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}


class Script2VideoPipeline:
    """
    Pipeline that converts a script into a video.

    Usage:
        pipeline = Script2VideoPipeline(config)
        result = await pipeline.run(script)
        if result.success:
            print(f"Video: {result.output.final_video.video_path}")
    """

    def __init__(self, config: Optional[Script2VideoConfig] = None):
        self.config = config or Script2VideoConfig()
        self.logger = logging.getLogger("vimax.pipelines.script2video")
        self._init_agents()

    def _init_agents(self):
        """Initialize agents."""
        storyboard_config = self.config.storyboard_artist or StoryboardArtistConfig(
            image_model=self.config.image_model,
            output_dir=f"{self.config.output_dir}/storyboard",
        )
        self.storyboard_artist = StoryboardArtist(storyboard_config)

        camera_config = self.config.camera_generator or CameraGeneratorConfig(
            video_model=self.config.video_model,
            output_dir=f"{self.config.output_dir}/videos",
        )
        self.camera_generator = CameraImageGenerator(camera_config)

    async def run(
        self,
        script: Union[Script, dict, str],
        portrait_registry: Optional[CharacterPortraitRegistry] = None,
    ) -> Script2VideoResult:
        """
        Run the pipeline.

        Args:
            script: Script object, dict, or path to JSON file
            portrait_registry: Optional registry of character portraits for consistency

        Returns:
            Script2VideoResult
        """
        # Parse script input
        if isinstance(script, str):
            script = self._load_script(script)
        elif isinstance(script, dict):
            script = Script(**script)

        result = Script2VideoResult(script=script, success=False)

        # Store registry if provided
        if portrait_registry and self.config.use_character_references:
            result.portrait_registry = portrait_registry
            result.used_references = len(portrait_registry.portraits) > 0
            self.logger.info(
                f"Using portrait registry with {len(portrait_registry.portraits)} characters"
            )

        self.logger.info(f"Starting Script2Video pipeline for: {script.title}")

        try:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Step 1: Generate Storyboard
            self.logger.info("Step 1/2: Generating storyboard...")
            storyboard_result = await self.storyboard_artist.process(
                script,
                portrait_registry=result.portrait_registry,
            )
            if not storyboard_result.success:
                result.errors.append(f"Storyboard failed: {storyboard_result.error}")
                return result
            result.total_cost += storyboard_result.metadata.get("cost", 0)

            # Step 2: Generate Videos
            self.logger.info("Step 2/2: Generating videos...")
            video_result = await self.camera_generator.process(storyboard_result.result)
            if not video_result.success:
                result.errors.append(f"Video generation failed: {video_result.error}")
                return result

            result.output = video_result.result
            result.total_cost += video_result.metadata.get("cost", 0)
            result.success = True
            result.completed_at = datetime.now()

            self.logger.info(f"Pipeline completed! Cost: ${result.total_cost:.3f}")

        except Exception as e:
            self.logger.exception("Pipeline failed")
            result.errors.append(str(e))

        return result

    def _load_script(self, path: str) -> Script:
        """Load script from JSON file."""
        try:
            with open(path) as f:
                data = json.load(f)
            return Script(**data)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Script file not found: {path}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in script file {path}: {e}") from e
