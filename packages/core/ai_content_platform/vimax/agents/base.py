"""
Base classes for ViMax agents.

All agents inherit from BaseAgent and implement the process() method.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
import logging
import json
import re

T = TypeVar('T')  # Input type
R = TypeVar('R')  # Result type
ResultT = TypeVar('ResultT')  # For AgentResult generic


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_retries: int = 3
    timeout: float = 60.0
    extra: Dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel, Generic[ResultT]):
    """
    Result from an agent execution.

    Generic over the result type for type-safe agent outputs.
    Example: AgentResult[List[Character]] for character extraction.
    """

    success: bool
    result: Optional[ResultT] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def ok(cls, result: ResultT, **metadata) -> "AgentResult[ResultT]":
        """Create a successful result."""
        return cls(success=True, result=result, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata) -> "AgentResult[ResultT]":
        """Create a failed result."""
        return cls(success=False, error=error, metadata=metadata)


class BaseAgent(ABC, Generic[T, R]):
    """
    Base class for all ViMax agents.

    Agents are responsible for specific tasks in the pipeline:
    - CharacterExtractor: Extract characters from text
    - Screenwriter: Generate screenplay from idea
    - StoryboardArtist: Create visual storyboard
    - etc.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig(name=self.__class__.__name__)
        self.logger = logging.getLogger(f"vimax.agents.{self.config.name}")

    @abstractmethod
    async def process(self, input_data: T) -> AgentResult:
        """
        Process input data and return result.

        Args:
            input_data: Input data specific to this agent

        Returns:
            AgentResult containing the processed output or error
        """
        pass

    def validate_input(self, input_data: T) -> bool:
        """Validate input data before processing. Override if needed."""
        return input_data is not None

    async def __call__(self, input_data: T) -> AgentResult:
        """Convenience method to call process()."""
        if not self.validate_input(input_data):
            return AgentResult.fail("Invalid input data")
        return await self.process(input_data)


def parse_llm_json(text: str, expect: str = "object") -> Any:
    """
    Parse JSON from LLM response text, handling common LLM quirks.

    Handles: markdown code fences, trailing commas, extra text before/after
    JSON, and single quotes instead of double quotes.

    Args:
        text: Raw LLM response text.
        expect: "object" for {}, "array" for [].

    Returns:
        Parsed JSON data (dict or list).

    Raises:
        ValueError: If no valid JSON can be extracted.
    """
    # Step 1: Try parsing the raw text directly
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Step 2: Strip markdown code fences
    fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if fence_match:
        cleaned = fence_match.group(1)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Continue with cleaned text for further fixing
            text_to_fix = cleaned
    else:
        text_to_fix = text

    # Step 3: Extract the outermost JSON structure (greedy)
    if expect == "array":
        match = re.search(r'\[[\s\S]*\]', text_to_fix)
    else:
        match = re.search(r'\{[\s\S]*\}', text_to_fix)

    if match:
        json_str = match.group()

        # Try as-is first
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Step 4: Fix trailing commas (e.g. ",]" or ",}")
        fixed = re.sub(r',\s*([}\]])', r'\1', json_str)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Step 5: Fix unescaped newlines inside strings
        fixed2 = re.sub(r'(?<=": ")(.*?)(?="[,}\]])', _escape_newlines, fixed)
        try:
            return json.loads(fixed2)
        except json.JSONDecodeError:
            pass

        # Step 6: Try line-by-line repair — remove lines that break JSON
        lines = fixed.split('\n')
        for i in range(len(lines) - 1, -1, -1):
            attempt = '\n'.join(lines[:i] + lines[i+1:])
            try:
                return json.loads(attempt)
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Could not parse JSON {expect} from LLM response")


def _escape_newlines(match: re.Match) -> str:
    """Escape literal newlines inside JSON string values."""
    return match.group(0).replace('\n', '\\n')
