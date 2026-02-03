"""
Base classes for ViMax adapters.

Adapters bridge ViMax agents to the underlying generators/services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
import logging

T = TypeVar('T')  # Input type
R = TypeVar('R')  # Result type


class AdapterConfig(BaseModel):
    """Configuration for an adapter."""

    provider: str = "fal"  # fal, replicate, google, openrouter
    model: str = ""
    timeout: float = 120.0
    max_retries: int = 3
    extra: Dict[str, Any] = Field(default_factory=dict)


class BaseAdapter(ABC, Generic[T, R]):
    """
    Base class for all ViMax adapters.

    Adapters translate between ViMax agent interfaces and
    underlying service APIs (FAL, Replicate, OpenRouter, etc.)
    """

    def __init__(self, config: Optional[AdapterConfig] = None):
        self.config = config or AdapterConfig()
        self.logger = logging.getLogger(f"vimax.adapters.{self.__class__.__name__}")
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the adapter (connect to services, etc.)."""
        pass

    @abstractmethod
    async def execute(self, input_data: T) -> R:
        """Execute the adapter's main function."""
        pass

    async def ensure_initialized(self):
        """Ensure adapter is initialized before use."""
        if not self._initialized:
            self._initialized = await self.initialize()
            if not self._initialized:
                raise RuntimeError(f"Failed to initialize {self.__class__.__name__}")

    async def __call__(self, input_data: T) -> R:
        """Convenience method to execute."""
        await self.ensure_initialized()
        return await self.execute(input_data)
