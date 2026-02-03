"""
Storyboard Artist Agent

Generates visual storyboard images from scripts or shot descriptions.
Creates consistent visual representations for each shot.
"""

from typing import Optional, List
import logging
from pathlib import Path

from pydantic import Field

from .base import BaseAgent, AgentConfig, AgentResult
from .screenwriter import Script
from ..adapters import ImageGeneratorAdapter, ImageAdapterConfig
from ..adapters.image_adapter import ImageOutput  # Use adapter's ImageOutput
from ..interfaces import Storyboard, Scene, ShotDescription


class StoryboardResult(Storyboard):
    """Storyboard with generated images."""

    images: List[ImageOutput] = Field(default_factory=list)
    total_cost: float = 0.0


class StoryboardArtistConfig(AgentConfig):
    """Configuration for StoryboardArtist."""

    name: str = "StoryboardArtist"
    image_model: str = "nano_banana_pro"
    style_prefix: str = "storyboard panel, cinematic composition, "
    aspect_ratio: str = "16:9"
    output_dir: str = "output/vimax/storyboard"


class StoryboardArtist(BaseAgent[Script, StoryboardResult]):
    """
    Agent that generates storyboard images from scripts.

    Usage:
        artist = StoryboardArtist()
        result = await artist.process(script)
        if result.success:
            for img in result.result.images:
                print(f"Generated: {img.image_path}")
    """

    def __init__(self, config: Optional[StoryboardArtistConfig] = None):
        super().__init__(config or StoryboardArtistConfig())
        self.config: StoryboardArtistConfig = self.config
        self._image_adapter: Optional[ImageGeneratorAdapter] = None
        self.logger = logging.getLogger("vimax.agents.storyboard_artist")

    async def _ensure_adapter(self):
        if self._image_adapter is None:
            self._image_adapter = ImageGeneratorAdapter(
                ImageAdapterConfig(
                    model=self.config.image_model,
                    output_dir=self.config.output_dir,
                )
            )
            await self._image_adapter.initialize()

    def _build_prompt(self, shot: ShotDescription, scene: Scene) -> str:
        """Build image generation prompt from shot description."""
        parts = [self.config.style_prefix]

        # Add scene context
        if scene.location:
            parts.append(f"Location: {scene.location}.")
        if scene.time:
            parts.append(f"Time: {scene.time}.")

        # Add shot description
        if shot.image_prompt:
            parts.append(shot.image_prompt)
        else:
            parts.append(shot.description)

        # Add shot type context
        shot_type_hints = {
            "wide": "wide establishing shot, full scene visible",
            "medium": "medium shot, subject framed from waist up",
            "close_up": "close-up shot, face and expression detail",
            "extreme_close_up": "extreme close-up, detail shot",
        }
        if shot.shot_type.value in shot_type_hints:
            parts.append(shot_type_hints[shot.shot_type.value])

        return " ".join(parts)

    async def process(self, script: Script) -> AgentResult[StoryboardResult]:
        """
        Generate storyboard from script.

        Args:
            script: Script with scenes and shots

        Returns:
            AgentResult containing StoryboardResult with images
        """
        await self._ensure_adapter()

        self.logger.info(f"Generating storyboard for: {script.title}")

        try:
            images = []
            total_cost = 0.0

            # Create output directory
            output_dir = Path(self.config.output_dir) / script.title.replace(" ", "_")
            output_dir.mkdir(parents=True, exist_ok=True)

            shot_index = 0
            for scene in script.scenes:
                self.logger.info(f"Processing scene: {scene.title}")

                for shot in scene.shots:
                    shot_index += 1
                    self.logger.info(f"Generating shot {shot_index}: {shot.shot_id}")

                    # Build prompt
                    prompt = self._build_prompt(shot, scene)

                    # Generate image
                    output_path = str(output_dir / f"{shot.shot_id}.png")
                    result = await self._image_adapter.generate(
                        prompt=prompt,
                        aspect_ratio=self.config.aspect_ratio,
                        output_path=output_path,
                    )

                    images.append(result)
                    total_cost += result.cost

            # Build storyboard result
            storyboard = StoryboardResult(
                title=script.title,
                description=script.logline,
                scenes=script.scenes,
                images=images,
                total_cost=total_cost,
            )

            self.logger.info(
                f"Generated storyboard: {len(images)} images, "
                f"${total_cost:.3f} total cost"
            )

            return AgentResult.ok(
                storyboard,
                image_count=len(images),
                cost=total_cost,
            )

        except Exception as e:
            self.logger.error(f"Storyboard generation failed: {e}")
            return AgentResult.fail(str(e))

    async def generate_from_shots(
        self,
        shots: List[ShotDescription],
        title: str = "Storyboard",
    ) -> List[ImageOutput]:
        """
        Generate images directly from shot descriptions.

        Args:
            shots: List of shot descriptions
            title: Storyboard title

        Returns:
            List of generated images
        """
        await self._ensure_adapter()

        images = []
        output_dir = Path(self.config.output_dir) / title.replace(" ", "_")
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, shot in enumerate(shots):
            prompt = f"{self.config.style_prefix} {shot.image_prompt or shot.description}"
            output_path = str(output_dir / f"shot_{i+1:03d}.png")

            result = await self._image_adapter.generate(
                prompt=prompt,
                aspect_ratio=self.config.aspect_ratio,
                output_path=output_path,
            )
            images.append(result)

        return images
