"""
Idea to Video Pipeline

Complete workflow from a text idea to a final video:
1. Screenwriter: Idea -> Script
2. CharacterExtractor: Script -> Characters
3. CharacterPortraitsGenerator: Characters -> Portraits
4. StoryboardArtist: Script -> Storyboard images
5. CameraImageGenerator: Storyboard -> Videos
6. Concatenation: Videos -> Final video
"""

from typing import Optional, Dict
from pathlib import Path
import logging
import json
from datetime import datetime

import yaml
from pydantic import BaseModel, Field

from ..agents import (
    Screenwriter, ScreenwriterConfig, Script,
    CharacterExtractor, CharacterExtractorConfig,
    CharacterPortraitsGenerator, PortraitsGeneratorConfig,
    StoryboardArtist, StoryboardArtistConfig, StoryboardResult,
    CameraImageGenerator, CameraGeneratorConfig,
)
from ..interfaces import PipelineOutput, CharacterPortrait, CharacterInNovel, CharacterPortraitRegistry


class Idea2VideoConfig(BaseModel):
    """Configuration for Idea2Video pipeline."""

    # Output settings
    output_dir: str = "output/vimax/idea2video"
    save_intermediate: bool = True

    # Target settings
    target_duration: float = 60.0  # seconds
    video_model: str = "kling"
    image_model: str = "nano_banana_pro"
    llm_model: str = "kimi-k2.5"

    # Agent configs (optional overrides)
    screenwriter: Optional[ScreenwriterConfig] = None
    character_extractor: Optional[CharacterExtractorConfig] = None
    portraits_generator: Optional[PortraitsGeneratorConfig] = None
    storyboard_artist: Optional[StoryboardArtistConfig] = None
    camera_generator: Optional[CameraGeneratorConfig] = None

    # Feature flags
    generate_portraits: bool = True
    use_character_references: bool = True  # Use portraits for storyboard consistency
    parallel_generation: bool = False

    @classmethod
    def from_yaml(cls, path: str) -> "Idea2VideoConfig":
        """Load config from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


class Idea2VideoResult(BaseModel):
    """Result from Idea2Video pipeline."""

    success: bool
    idea: str
    script: Optional[Script] = None
    characters: list = Field(default_factory=list)
    portraits: Dict[str, CharacterPortrait] = Field(default_factory=dict)
    portrait_registry: Optional[CharacterPortraitRegistry] = None
    storyboard: Optional[StoryboardResult] = None
    output: Optional[PipelineOutput] = None

    # Timing and cost
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_cost: float = 0.0
    errors: list = Field(default_factory=list)

    @property
    def duration(self) -> Optional[float]:
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    model_config = {"arbitrary_types_allowed": True}


class Idea2VideoPipeline:
    """
    Pipeline that converts an idea into a video.

    Usage:
        pipeline = Idea2VideoPipeline(config)
        result = await pipeline.run("A samurai's journey at sunrise")
        if result.success:
            print(f"Video: {result.output.final_video.video_path}")
    """

    def __init__(self, config: Optional[Idea2VideoConfig] = None):
        self.config = config or Idea2VideoConfig()
        self.logger = logging.getLogger("vimax.pipelines.idea2video")

        # Initialize agents with config
        self._init_agents()

    def _init_agents(self):
        """Initialize all agents with configuration."""
        # Screenwriter
        screenwriter_config = self.config.screenwriter or ScreenwriterConfig(
            model=self.config.llm_model,
            target_duration=self.config.target_duration,
        )
        self.screenwriter = Screenwriter(screenwriter_config)

        # Character Extractor
        extractor_config = self.config.character_extractor or CharacterExtractorConfig(
            model=self.config.llm_model,
        )
        self.character_extractor = CharacterExtractor(extractor_config)

        # Portraits Generator
        portraits_config = self.config.portraits_generator or PortraitsGeneratorConfig(
            image_model=self.config.image_model,
            llm_model=self.config.llm_model,
            output_dir=f"{self.config.output_dir}/portraits",
        )
        self.portraits_generator = CharacterPortraitsGenerator(portraits_config)

        # Storyboard Artist
        storyboard_config = self.config.storyboard_artist or StoryboardArtistConfig(
            image_model=self.config.image_model,
            output_dir=f"{self.config.output_dir}/storyboard",
        )
        self.storyboard_artist = StoryboardArtist(storyboard_config)

        # Camera Generator
        camera_config = self.config.camera_generator or CameraGeneratorConfig(
            video_model=self.config.video_model,
            output_dir=f"{self.config.output_dir}/videos",
        )
        self.camera_generator = CameraImageGenerator(camera_config)

    async def run(self, idea: str) -> Idea2VideoResult:
        """
        Run the complete pipeline.

        Args:
            idea: Text idea or concept for the video

        Returns:
            Idea2VideoResult with all generated content
        """
        result = Idea2VideoResult(idea=idea, success=False)

        self.logger.info(f"Starting Idea2Video pipeline for: {idea[:100]}...")

        try:
            # Create output directory
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Step 1: Generate Script
            self.logger.info("Step 1/5: Generating script...")
            script_result = await self.screenwriter.process(idea)
            if not script_result.success:
                result.errors.append(f"Script generation failed: {script_result.error}")
                return result
            result.script = script_result.result
            result.total_cost += script_result.metadata.get("cost", 0)

            if self.config.save_intermediate:
                self._save_script(result.script, output_dir / "script.json")

            # Step 2: Extract Characters
            self.logger.info("Step 2/5: Extracting characters...")
            # Use script content for character extraction
            script_text = self._script_to_text(result.script)
            char_result = await self.character_extractor.process(script_text)
            if char_result.success:
                result.characters = char_result.result
                result.total_cost += char_result.metadata.get("cost", 0)
            else:
                self.logger.warning(f"Character extraction failed: {char_result.error}")

            # Step 3: Generate Character Portraits (optional)
            if self.config.generate_portraits and result.characters:
                self.logger.info("Step 3/5: Generating character portraits...")
                portraits_result = await self.portraits_generator.generate_batch(
                    result.characters[:5]  # Limit to main characters
                )
                result.portraits = portraits_result.result or {}
                result.total_cost += portraits_result.metadata.get("cost", 0)

                # Create portrait registry for storyboard reference
                if result.portraits and self.config.use_character_references:
                    result.portrait_registry = CharacterPortraitRegistry(
                        project_id=result.script.title.replace(" ", "_")
                    )
                    for name, portrait in result.portraits.items():
                        result.portrait_registry.add_portrait(portrait)
                    self.logger.info(
                        f"Created portrait registry with {len(result.portraits)} characters"
                    )

            # Step 4: Generate Storyboard
            self.logger.info("Step 4/5: Generating storyboard...")
            storyboard_result = await self.storyboard_artist.process(
                result.script,
                portrait_registry=result.portrait_registry,
            )
            if not storyboard_result.success:
                result.errors.append(f"Storyboard generation failed: {storyboard_result.error}")
                return result
            result.storyboard = storyboard_result.result
            result.total_cost += storyboard_result.metadata.get("cost", 0)

            # Step 5: Generate Videos
            self.logger.info("Step 5/5: Generating videos...")
            video_result = await self.camera_generator.process(result.storyboard)
            if not video_result.success:
                result.errors.append(f"Video generation failed: {video_result.error}")
                return result
            result.output = video_result.result
            result.total_cost += video_result.metadata.get("cost", 0)

            # Mark success
            result.success = True
            result.completed_at = datetime.now()

            self.logger.info(
                f"Pipeline completed successfully! "
                f"Duration: {result.duration:.1f}s, "
                f"Cost: ${result.total_cost:.3f}"
            )

            # Save summary
            if self.config.save_intermediate:
                self._save_summary(result, output_dir / "summary.json")

        except Exception as e:
            self.logger.error(f"Pipeline failed with error: {e}")
            result.errors.append(str(e))

        return result

    def _script_to_text(self, script: Script) -> str:
        """Convert script to text for character extraction."""
        parts = [f"Title: {script.title}", f"Logline: {script.logline}", ""]

        for scene in script.scenes:
            parts.append(f"Scene: {scene.title}")
            parts.append(f"Location: {scene.location}")
            for shot in scene.shots:
                parts.append(f"- {shot.description}")
            parts.append("")

        return "\n".join(parts)

    def _save_script(self, script: Script, path: Path):
        """Save script to JSON file."""
        with open(path, "w") as f:
            json.dump(script.model_dump(), f, indent=2, default=str)

    def _save_summary(self, result: Idea2VideoResult, path: Path):
        """Save pipeline summary to JSON file."""
        summary = {
            "success": result.success,
            "idea": result.idea,
            "script_title": result.script.title if result.script else None,
            "scene_count": result.script.scene_count if result.script else 0,
            "character_count": len(result.characters),
            "portrait_count": len(result.portraits),
            "used_character_references": result.portrait_registry is not None,
            "video_count": len(result.output.videos) if result.output else 0,
            "final_video": result.output.final_video.video_path if result.output and result.output.final_video else None,
            "total_cost": result.total_cost,
            "duration_seconds": result.duration,
            "errors": result.errors,
        }
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)


# Factory function
def create_pipeline(config_path: Optional[str] = None) -> Idea2VideoPipeline:
    """Create pipeline from config file or defaults."""
    if config_path:
        config = Idea2VideoConfig.from_yaml(config_path)
    else:
        config = Idea2VideoConfig()
    return Idea2VideoPipeline(config)
