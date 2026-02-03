"""
Base classes for ViMax agents.

All agents inherit from BaseAgent and implement the process() method.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
import logging

T = TypeVar('T')  # Input type
R = TypeVar('R')  # Result type


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_retries: int = 3
    timeout: float = 60.0
    extra: Dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Result from an agent execution."""

    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def ok(cls, result: Any, **metadata) -> "AgentResult":
        """Create a successful result."""
        return cls(success=True, result=result, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata) -> "AgentResult":
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
