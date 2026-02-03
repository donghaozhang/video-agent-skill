"""
Character Portraits Generator Agent

Generates multi-angle character portraits (front, side, back, 3/4)
from character descriptions to ensure visual consistency.
"""

from typing import List, Optional, Dict
import logging

from .base import BaseAgent, AgentConfig, AgentResult
from ..adapters import ImageGeneratorAdapter, ImageAdapterConfig, LLMAdapter, LLMAdapterConfig, Message
from ..interfaces import CharacterInNovel, CharacterPortrait


class PortraitsGeneratorConfig(AgentConfig):
    """Configuration for CharacterPortraitsGenerator."""

    name: str = "CharacterPortraitsGenerator"
    image_model: str = "nano_banana_pro"
    llm_model: str = "kimi-k2.5"
    views: List[str] = ["front", "side", "back", "three_quarter"]
    style: str = "detailed character portrait, professional, consistent style"
    output_dir: str = "media/generated/vimax/portraits"


PORTRAIT_PROMPT_TEMPLATE = """Create a detailed image generation prompt for a {view} view portrait.

CHARACTER INFORMATION:
Name: {name}
Description: {description}
Appearance: {appearance}
Age: {age}
Gender: {gender}

STYLE: {style}

Generate a single, detailed prompt that will create a {view} view portrait of this character.
The prompt should include specific details about pose, lighting, and composition for a {view} view.
Keep the character's appearance consistent across all views.

Respond with ONLY the image generation prompt, no other text."""


class CharacterPortraitsGenerator(BaseAgent[CharacterInNovel, CharacterPortrait]):
    """
    Agent that generates multi-angle character portraits.

    Usage:
        generator = CharacterPortraitsGenerator()
        result = await generator.process(character)
        if result.success:
            portrait = result.result
            print(f"Front view: {portrait.front_view}")
    """

    def __init__(self, config: Optional[PortraitsGeneratorConfig] = None):
        super().__init__(config or PortraitsGeneratorConfig())
        self.config: PortraitsGeneratorConfig = self.config
        self._image_adapter: Optional[ImageGeneratorAdapter] = None
        self._llm: Optional[LLMAdapter] = None
        self.logger = logging.getLogger("vimax.agents.portraits_generator")

    async def _ensure_adapters(self):
        """Initialize adapters if needed."""
        if self._image_adapter is None:
            self._image_adapter = ImageGeneratorAdapter(
                ImageAdapterConfig(
                    model=self.config.image_model,
                    output_dir=self.config.output_dir,
                )
            )
            await self._image_adapter.initialize()

        if self._llm is None:
            self._llm = LLMAdapter(LLMAdapterConfig(model=self.config.llm_model))
            await self._llm.initialize()

    async def _generate_prompt(
        self,
        character: CharacterInNovel,
        view: str,
    ) -> str:
        """Generate optimized prompt for a specific view."""
        prompt = PORTRAIT_PROMPT_TEMPLATE.format(
            view=view,
            name=character.name,
            description=character.description,
            appearance=character.appearance,
            age=character.age or "unknown",
            gender=character.gender or "unknown",
            style=self.config.style,
        )

        response = await self._llm.chat([Message(role="user", content=prompt)])
        return response.content.strip()

    async def process(self, character: CharacterInNovel) -> AgentResult[CharacterPortrait]:
        """
        Generate portraits for a character.

        Args:
            character: Character information

        Returns:
            AgentResult containing CharacterPortrait with paths to generated images
        """
        await self._ensure_adapters()

        self.logger.info(f"Generating portraits for character: {character.name}")

        try:
            portrait = CharacterPortrait(character_name=character.name)
            total_cost = 0.0

            supported_views = {"front", "side", "back", "three_quarter"}
            unknown_views = [view for view in self.config.views if view not in supported_views]
            if unknown_views:
                raise ValueError(
                    "Unsupported portrait view(s): "
                    + ", ".join(sorted(set(unknown_views)))
                )

            for view in self.config.views:
                self.logger.info(f"Generating {view} view for {character.name}")

                # Generate optimized prompt
                prompt = await self._generate_prompt(character, view)

                # Generate image
                result = await self._image_adapter.generate(
                    prompt=prompt,
                    aspect_ratio="1:1",
                )

                total_cost += result.cost

                # Set the appropriate view
                if view == "front":
                    portrait.front_view = result.image_path
                elif view == "side":
                    portrait.side_view = result.image_path
                elif view == "back":
                    portrait.back_view = result.image_path
                elif view == "three_quarter":
                    portrait.three_quarter_view = result.image_path
                else:
                    self.logger.warning(f"Unknown view '{view}' - image generated but not assigned")

            self.logger.info(f"Generated {len(portrait.views)} portraits for {character.name}")

            return AgentResult.ok(
                portrait,
                views_generated=len(portrait.views),
                cost=total_cost,
            )

        except Exception as e:
            self.logger.exception("Portrait generation failed")
            return AgentResult.fail(str(e))

    async def generate_batch(
        self,
        characters: List[CharacterInNovel],
    ) -> AgentResult[Dict[str, CharacterPortrait]]:
        """
        Generate portraits for multiple characters.

        Args:
            characters: List of characters

        Returns:
            AgentResult containing dict mapping character names to portraits and total cost
        """
        portraits = {}
        total_cost = 0.0
        errors = []

        for char in characters:
            result = await self.process(char)
            if result.success:
                portraits[char.name] = result.result
                total_cost += result.metadata.get("cost", 0)
            else:
                errors.append(f"Failed to generate portrait for {char.name}: {result.error}")

        if errors:
            self.logger.warning(f"Some portraits failed: {errors}")

        return AgentResult.ok(portraits, cost=total_cost, errors=errors if errors else None)
