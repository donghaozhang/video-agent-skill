"""
Storyboard Artist Agent

Generates visual storyboard images from scripts or shot descriptions.
Creates consistent visual representations for each shot.

Supports character reference images for visual consistency across shots.
"""

from typing import Optional, List
import logging
import re
from pathlib import Path

from pydantic import Field

from .base import BaseAgent, AgentConfig, AgentResult
from .screenwriter import Script
from ..adapters import ImageGeneratorAdapter, ImageAdapterConfig
from ..adapters.image_adapter import ImageOutput  # Use adapter's ImageOutput
from ..interfaces import Storyboard, Scene, ShotDescription, CharacterPortraitRegistry


def _is_safe_reference_path(path: str) -> bool:
    """Validate that a reference image path is safe (no traversal or absolute paths)."""
    p = Path(path)
    return not p.is_absolute() and ".." not in p.parts


class StoryboardResult(Storyboard):
    """Storyboard with generated images."""

    images: List[ImageOutput] = Field(default_factory=list)
    total_cost: float = 0.0


class StoryboardArtistConfig(AgentConfig):
    """Configuration for StoryboardArtist."""

    name: str = "StoryboardArtist"
    image_model: str = "nano_banana_pro"
    style_prefix: str = "photorealistic, cinematic lighting, film still, "
    aspect_ratio: str = "16:9"
    output_dir: str = "media/generated/vimax/storyboard"

    # Reference image settings for character consistency
    use_character_references: bool = True  # Enable reference image usage
    reference_model: str = "nano_banana_pro"  # Model for image-to-image with reference
    reference_strength: float = 0.6  # How much to follow reference (0.0-1.0)


class StoryboardArtist(BaseAgent[Script, StoryboardResult]):
    """
    Agent that generates storyboard images from scripts.

    Supports character reference images for visual consistency:
    - Pass a CharacterPortraitRegistry to process() or process_with_references()
    - The agent will automatically select and use the best reference image
      for each shot based on camera angle and shot type

    Usage:
        artist = StoryboardArtist()

        # Without reference images (basic mode)
        result = await artist.process(script)

        # With reference images (consistency mode)
        result = await artist.process_with_references(script, portrait_registry)

        if result.success:
            for img in result.result.images:
                print(f"Generated: {img.image_path}")
    """

    def __init__(
        self,
        config: Optional[StoryboardArtistConfig] = None,
        portrait_registry: Optional[CharacterPortraitRegistry] = None,
    ):
        super().__init__(config or StoryboardArtistConfig())
        self.config: StoryboardArtistConfig = self.config
        self._image_adapter: Optional[ImageGeneratorAdapter] = None
        self._portrait_registry = portrait_registry
        self._reference_selector = None  # Lazy init
        self.logger = logging.getLogger("vimax.agents.storyboard_artist")

    async def _ensure_adapter(self):
        if self._image_adapter is None:
            self._image_adapter = ImageGeneratorAdapter(
                ImageAdapterConfig(
                    model=self.config.image_model,
                    output_dir=self.config.output_dir,
                    reference_model=self.config.reference_model,
                    reference_strength=self.config.reference_strength,
                )
            )
            await self._image_adapter.initialize()

    async def _ensure_reference_selector(self):
        """Lazy initialize the reference selector."""
        if self._reference_selector is None:
            from .reference_selector import ReferenceImageSelector, ReferenceSelectorConfig
            self._reference_selector = ReferenceImageSelector(ReferenceSelectorConfig())
            await self._reference_selector.initialize()

    def _build_prompt(
        self,
        shot: ShotDescription,
        scene: Scene,
        registry: Optional[CharacterPortraitRegistry] = None,
    ) -> str:
        """Build image generation prompt from shot description.

        When character references have been resolved on the shot, appends
        per-character appearance descriptions (dress, face, look) and an
        instruction telling the model to use the input image for each character.
        """
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

        # Add character appearance + reference instructions
        if shot.character_references:
            for name in shot.character_references:
                desc = ""
                if registry:
                    portrait = registry.get_portrait(name)
                    if portrait and portrait.description:
                        desc = portrait.description
                if desc:
                    parts.append(f"{name}: {desc}.")
                if shot.primary_reference_image:
                    parts.append(f"Use the input image for {name}.")

        return " ".join(parts)

    def _safe_slug(self, value: str) -> str:
        """Sanitize a string for use in filesystem paths."""
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
        return safe or "untitled"

    async def resolve_references(
        self,
        script: Script,
        registry: CharacterPortraitRegistry,
    ) -> int:
        """
        Pre-populate character_references on all shots from the portrait registry.

        Iterates through every shot in the script. For each character listed in a
        shot, the best portrait view is selected based on camera angle and shot type,
        then written into ``shot.character_references`` and ``shot.primary_reference_image``.

        Args:
            script: Script whose shots will be enriched in-place.
            registry: Portrait registry to resolve references from.

        Returns:
            Number of shots that received at least one reference.
        """
        await self._ensure_reference_selector()

        resolved_count = 0
        for scene in script.scenes:
            for shot in scene.shots:
                if not shot.characters:
                    continue
                ref_result = await self._reference_selector.select_for_shot(
                    shot, registry
                )
                if ref_result.selected_references:
                    shot.character_references = ref_result.selected_references
                if ref_result.primary_reference and _is_safe_reference_path(ref_result.primary_reference):
                    shot.primary_reference_image = ref_result.primary_reference
                if ref_result.selected_references or ref_result.primary_reference:
                    resolved_count += 1
                    self.logger.debug(
                        f"Resolved {shot.shot_id}: {ref_result.selection_reason}"
                    )
        return resolved_count

    async def process(
        self,
        script: Script,
        portrait_registry: Optional[CharacterPortraitRegistry] = None,
    ) -> AgentResult[StoryboardResult]:
        """
        Generate storyboard from script.

        Args:
            script: Script with scenes and shots
            portrait_registry: Optional registry of character portraits for consistency

        Returns:
            AgentResult containing StoryboardResult with images
        """
        await self._ensure_adapter()

        # Use provided registry or fall back to instance registry
        registry = portrait_registry or self._portrait_registry
        has_registry = registry is not None and len(registry.portraits) > 0

        # Check for inline references already present in the script JSON
        has_inline_refs = any(
            shot.primary_reference_image
            for scene in script.scenes
            for shot in scene.shots
        )

        use_refs = self.config.use_character_references and (has_registry or has_inline_refs)

        if use_refs and has_registry and not has_inline_refs:
            # Registry provided but shots not yet resolved — resolve now
            resolved = await self.resolve_references(script, registry)
            self.logger.info(
                f"Generating storyboard for: {script.title} "
                f"(resolved references for {resolved} shots "
                f"from {len(registry.portraits)} characters)"
            )
        elif use_refs:
            # References already on shots (inline from JSON or pre-resolved by CLI)
            resolved = sum(
                1 for scene in script.scenes
                for shot in scene.shots
                if shot.primary_reference_image
            )
            self.logger.info(
                f"Generating storyboard for: {script.title} "
                f"(using {'inline' if not has_registry else 'pre-resolved'} "
                f"references for {resolved} shots)"
            )
        else:
            self.logger.info(f"Generating storyboard for: {script.title} (no references)")

        try:
            images = []
            total_cost = 0.0

            # Create output directory
            output_dir = Path(self.config.output_dir) / self._safe_slug(script.title)
            output_dir.mkdir(parents=True, exist_ok=True)

            shot_index = 0
            for scene in script.scenes:
                self.logger.info(f"Processing scene: {scene.title}")

                for shot in scene.shots:
                    shot_index += 1
                    self.logger.info(f"Generating shot {shot_index}: {shot.shot_id}")

                    # Build prompt (pass registry for character descriptions)
                    prompt = self._build_prompt(shot, scene, registry=registry)
                    output_path = str(output_dir / f"{self._safe_slug(shot.shot_id)}.png")

                    # Use pre-resolved reference from shot.primary_reference_image
                    reference_image = shot.primary_reference_image if use_refs else None
                    # Reason: Validate at consumption point to catch inline refs from JSON
                    if reference_image and not _is_safe_reference_path(reference_image):
                        self.logger.warning(f"Skipping unsafe reference path: {reference_image}")
                        reference_image = None

                    # Generate image with or without reference
                    if reference_image:
                        result = await self._image_adapter.generate_with_reference(
                            prompt=prompt,
                            reference_image=reference_image,
                            model=self.config.reference_model,
                            reference_strength=self.config.reference_strength,
                            aspect_ratio=self.config.aspect_ratio,
                            output_path=output_path,
                        )
                    else:
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
                used_references=use_refs,
            )

        except Exception as e:
            self.logger.exception("Storyboard generation failed")
            return AgentResult.fail(str(e))

    async def process_with_references(
        self,
        script: Script,
        portrait_registry: CharacterPortraitRegistry,
    ) -> AgentResult[StoryboardResult]:
        """
        Generate storyboard from script with character reference images.

        This is a convenience method that explicitly requires a portrait registry.

        Args:
            script: Script with scenes and shots
            portrait_registry: Registry of character portraits (required)

        Returns:
            AgentResult containing StoryboardResult with images
        """
        if not portrait_registry or len(portrait_registry.portraits) == 0:
            self.logger.warning(
                "process_with_references called but registry is empty, "
                "falling back to basic generation"
            )
        return await self.process(script, portrait_registry)

    async def generate_from_shots(
        self,
        shots: List[ShotDescription],
        title: str = "Storyboard",
        portrait_registry: Optional[CharacterPortraitRegistry] = None,
    ) -> List[ImageOutput]:
        """
        Generate images directly from shot descriptions.

        Args:
            shots: List of shot descriptions
            title: Storyboard title
            portrait_registry: Optional registry of character portraits

        Returns:
            List of generated images
        """
        await self._ensure_adapter()

        registry = portrait_registry or self._portrait_registry
        has_registry = registry is not None and len(registry.portraits) > 0
        has_inline_refs = any(shot.primary_reference_image for shot in shots)
        use_refs = self.config.use_character_references and (has_registry or has_inline_refs)

        # Pre-populate references from registry if not already inline
        if use_refs and has_registry and not has_inline_refs:
            await self._ensure_reference_selector()
            for shot in shots:
                if not shot.characters:
                    continue
                ref_result = await self._reference_selector.select_for_shot(shot, registry)
                if ref_result.selected_references:
                    shot.character_references = ref_result.selected_references
                if ref_result.primary_reference and _is_safe_reference_path(ref_result.primary_reference):
                    shot.primary_reference_image = ref_result.primary_reference

        images = []
        output_dir = Path(self.config.output_dir) / self._safe_slug(title)
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, shot in enumerate(shots):
            prompt = f"{self.config.style_prefix} {shot.image_prompt or shot.description}"
            if shot.character_references:
                for name in shot.character_references:
                    desc = ""
                    if registry:
                        portrait = registry.get_portrait(name)
                        if portrait and portrait.description:
                            desc = portrait.description
                    if desc:
                        prompt += f" {name}: {desc}."
                    if use_refs and shot.primary_reference_image:
                        prompt += f" Use the input image for {name}."
            output_path = str(output_dir / f"shot_{i+1:03d}.png")

            # Use pre-resolved reference from shot
            reference_image = shot.primary_reference_image if use_refs else None
            if reference_image and not _is_safe_reference_path(reference_image):
                self.logger.warning(f"Skipping unsafe reference path: {reference_image}")
                reference_image = None

            # Generate with or without reference
            if reference_image:
                result = await self._image_adapter.generate_with_reference(
                    prompt=prompt,
                    reference_image=reference_image,
                    model=self.config.reference_model,
                    reference_strength=self.config.reference_strength,
                    aspect_ratio=self.config.aspect_ratio,
                    output_path=output_path,
                )
            else:
                result = await self._image_adapter.generate(
                    prompt=prompt,
                    aspect_ratio=self.config.aspect_ratio,
                    output_path=output_path,
                )

            images.append(result)

        return images

    def set_portrait_registry(self, registry: CharacterPortraitRegistry) -> None:
        """Set the portrait registry for reference image selection."""
        self._portrait_registry = registry
        self.logger.info(f"Set portrait registry with {len(registry.portraits)} characters")
