"""
Character Extractor Agent

Extracts character information from scripts, novels, or story text
using LLM analysis.
"""

from typing import List, Optional
import logging

from .base import BaseAgent, AgentConfig, AgentResult
from .schemas import CharacterListResponse
from ..adapters import LLMAdapter, LLMAdapterConfig, Message
from ..interfaces import CharacterInNovel


class CharacterExtractorConfig(AgentConfig):
    """Configuration for CharacterExtractor."""

    name: str = "CharacterExtractor"
    model: str = "kimi-k2.5"
    max_characters: int = 20


EXTRACTION_PROMPT = """You are an expert story analyst. Extract all characters from the following text.

For each character, provide:
- name: Character's name
- description: Brief description
- age: Age or age range (if mentioned or can be inferred)
- gender: Gender (if mentioned or can be inferred)
- appearance: Physical appearance description
- personality: Personality traits
- role: Role in the story (protagonist, antagonist, supporting, minor)
- relationships: List of relationships with other characters

Only include characters that appear in the text.
If a field cannot be determined, use an empty string or empty list.

TEXT:
{text}

Return a JSON object with a "characters" key containing an array of characters."""


class CharacterExtractor(BaseAgent[str, List[CharacterInNovel]]):
    """
    Agent that extracts character information from text.

    Usage:
        extractor = CharacterExtractor()
        result = await extractor.process(novel_text)
        if result.success:
            for char in result.result:
                print(f"Found character: {char.name}")
    """

    def __init__(self, config: Optional[CharacterExtractorConfig] = None):
        super().__init__(config or CharacterExtractorConfig())
        self.config: CharacterExtractorConfig = self.config
        self._llm: Optional[LLMAdapter] = None
        self.logger = logging.getLogger("vimax.agents.character_extractor")

    async def _ensure_llm(self) -> None:
        """Initialize LLM adapter if needed."""
        if self._llm is None:
            self._llm = LLMAdapter(LLMAdapterConfig(model=self.config.model))
            await self._llm.initialize()

    async def process(self, text: str) -> AgentResult[List[CharacterInNovel]]:
        """
        Extract characters from text.

        Args:
            text: Story text, script, or novel content

        Returns:
            AgentResult containing list of extracted characters
        """
        await self._ensure_llm()

        self.logger.info(f"Extracting characters from text ({len(text)} chars)")

        try:
            # Build prompt
            prompt = EXTRACTION_PROMPT.format(text=text[:50000])  # Limit text length

            messages = [
                Message(role="user", content=prompt)
            ]

            # Use native structured output — API guarantees valid JSON
            result = await self._llm.chat_with_structured_output(
                messages,
                output_schema=CharacterListResponse,
                schema_name="character_list",
                temperature=0.3,
            )

            # Convert schema objects to CharacterInNovel models
            characters = []
            for item in result.characters[:self.config.max_characters]:
                char = CharacterInNovel(
                    name=item.name,
                    description=item.description,
                    age=item.age or None,
                    gender=item.gender or None,
                    appearance=item.appearance,
                    personality=item.personality,
                    role=item.role,
                    relationships=item.relationships,
                )
                characters.append(char)

            self.logger.info(f"Extracted {len(characters)} characters")

            return AgentResult.ok(
                characters,
                character_count=len(characters),
                cost=0.0,
            )

        except Exception as e:
            self.logger.exception("Character extraction failed")
            return AgentResult.fail(str(e))

    async def extract_main_characters(
        self,
        text: str,
        max_characters: int = 5,
    ) -> List[CharacterInNovel]:
        """
        Extract only main characters.

        Args:
            text: Story text
            max_characters: Maximum number of main characters

        Returns:
            List of main characters
        """
        result = await self.process(text)
        if not result.success:
            return []

        # Filter to main characters (protagonist, antagonist, supporting)
        main_roles = {"protagonist", "antagonist", "supporting"}
        main_chars = [
            c for c in result.result
            if (c.role or "").lower() in main_roles
        ]

        return main_chars[:max_characters]
