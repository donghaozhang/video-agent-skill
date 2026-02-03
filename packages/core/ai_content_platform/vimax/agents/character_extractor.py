"""
Character Extractor Agent

Extracts character information from scripts, novels, or story text
using LLM analysis.
"""

from typing import List, Optional
import logging
import json
import re

from .base import BaseAgent, AgentConfig, AgentResult
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

Return a JSON array of characters. Only include characters that appear in the text.
If a field cannot be determined, use an empty string or empty list.

TEXT:
{text}

Respond ONLY with a JSON array, no other text."""


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

    async def _ensure_llm(self):
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

            # Call LLM with structured output
            response = await self._llm.chat(messages, temperature=0.3)

            # Parse response
            try:
                data = json.loads(response.content)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                else:
                    raise ValueError("Could not parse character data from response")

            # Convert to CharacterInNovel objects
            characters = []
            for item in data[:self.config.max_characters]:
                char = CharacterInNovel(
                    name=item.get("name", "Unknown"),
                    description=item.get("description", ""),
                    age=item.get("age"),
                    gender=item.get("gender"),
                    appearance=item.get("appearance", ""),
                    personality=item.get("personality", ""),
                    role=item.get("role", ""),
                    relationships=item.get("relationships", []),
                )
                characters.append(char)

            self.logger.info(f"Extracted {len(characters)} characters")

            return AgentResult.ok(
                characters,
                character_count=len(characters),
                cost=response.cost,
            )

        except Exception as e:
            self.logger.error(f"Character extraction failed: {e}")
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
            if c.role.lower() in main_roles
        ]

        return main_chars[:max_characters]
