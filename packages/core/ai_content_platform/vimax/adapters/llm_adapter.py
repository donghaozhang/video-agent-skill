"""
LLM Adapter for ViMax agents.

Uses litellm for unified access to multiple LLM providers:
- OpenRouter (Claude, GPT-4, etc.)
- OpenAI
- Anthropic
- Google (Gemini)
"""

import os
import json
from typing import Optional, Dict, Any, List, Union
import logging

from pydantic import BaseModel, Field

from .base import BaseAdapter, AdapterConfig

# Try to import litellm
try:
    import litellm
    from litellm import acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    acompletion = None


class LLMAdapterConfig(AdapterConfig):
    """Configuration for LLM adapter."""

    model: str = "openrouter/moonshotai/kimi-k2.5"  # Default: Kimi K2.5
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 60.0


class Message(BaseModel):
    """Chat message."""
    role: str  # system, user, assistant
    content: str


class LLMResponse(BaseModel):
    """LLM response."""
    content: str
    model: str
    usage: Dict[str, int] = Field(default_factory=dict)
    cost: float = 0.0


class LLMAdapter(BaseAdapter[List[Message], LLMResponse]):
    """
    Adapter for LLM calls.

    Uses litellm for unified access to multiple providers.

    Usage:
        adapter = LLMAdapter(config)
        response = await adapter.chat([
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Write a short story."),
        ])
    """

    # Common model aliases
    MODEL_ALIASES = {
        "kimi-k2.5": "openrouter/moonshotai/kimi-k2.5",
        "kimi": "openrouter/moonshotai/kimi-k2.5",
        "claude-3.5-sonnet": "openrouter/anthropic/claude-3.5-sonnet",
        "claude-3-opus": "openrouter/anthropic/claude-3-opus",
        "gpt-4": "openrouter/openai/gpt-4-turbo",
        "gpt-4o": "openrouter/openai/gpt-4o",
        "gemini-pro": "openrouter/google/gemini-pro",
    }

    def __init__(self, config: Optional[LLMAdapterConfig] = None):
        super().__init__(config or LLMAdapterConfig())
        self.config: LLMAdapterConfig = self.config
        self.logger = logging.getLogger("vimax.adapters.llm")

    async def initialize(self) -> bool:
        """Initialize LLM adapter."""
        if not LITELLM_AVAILABLE:
            self.logger.warning("litellm not available - using mock mode")

        # Check for API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            self.logger.warning("OPENROUTER_API_KEY not set - using mock mode")

        self.logger.info(f"LLM adapter initialized with model: {self.config.model}")
        return True

    async def execute(self, messages: List[Message]) -> LLMResponse:
        """Execute LLM call."""
        return await self.chat(messages)

    async def chat(
        self,
        messages: List[Union[Message, Dict[str, str]]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Send chat messages to LLM.

        Args:
            messages: List of messages
            model: Model to use (default from config)
            temperature: Temperature (default from config)
            max_tokens: Max tokens (default from config)
            **kwargs: Additional parameters

        Returns:
            LLMResponse with generated content
        """
        await self.ensure_initialized()

        # Resolve model alias
        model = model or self.config.model
        model = self.MODEL_ALIASES.get(model, model)

        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        # Convert messages to dict format
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, Message):
                formatted_messages.append({"role": msg.role, "content": msg.content})
            else:
                formatted_messages.append(msg)

        self.logger.debug(f"Calling LLM: model={model}, messages={len(formatted_messages)}")

        # Check if litellm is available and API key is set
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not LITELLM_AVAILABLE or not api_key:
            return self._mock_chat(formatted_messages, model)

        try:
            response = await acompletion(
                model=model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.config.timeout,
                **kwargs,
            )

            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            # Estimate cost
            cost = self._estimate_cost(model, usage)

            return LLMResponse(
                content=content,
                model=model,
                usage=usage,
                cost=cost,
            )

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    def _mock_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
    ) -> LLMResponse:
        """Mock LLM response for testing without API keys."""
        self.logger.info("Using mock LLM response")

        # Generate a simple mock response based on the last user message
        user_messages = [m for m in messages if m.get("role") == "user"]
        last_message = user_messages[-1]["content"] if user_messages else ""

        # Detect if this is a screenplay request and return valid JSON
        if "screenplay" in last_message.lower() or '"scenes"' in last_message:
            mock_content = json.dumps({
                "title": "Mock Screenplay",
                "logline": "A mock screenplay for testing purposes.",
                "scenes": [
                    {
                        "scene_id": "scene_001",
                        "title": "Opening Scene",
                        "location": "Mountain summit at dawn",
                        "time": "Dawn",
                        "shots": [
                            {
                                "shot_id": "shot_001",
                                "shot_type": "wide",
                                "description": "Panoramic view of misty mountains",
                                "camera_movement": "pan",
                                "duration_seconds": 5,
                                "image_prompt": "Panoramic view of misty mountains at dawn, golden light, cinematic",
                                "video_prompt": "Camera slowly pans across mountain range, mist rising"
                            },
                            {
                                "shot_id": "shot_002",
                                "shot_type": "medium",
                                "description": "Silhouette figure against sunrise",
                                "camera_movement": "static",
                                "duration_seconds": 4,
                                "image_prompt": "Silhouette of person against golden sunrise, mountains background",
                                "video_prompt": "Figure stands still, wind moves their clothing"
                            }
                        ]
                    },
                    {
                        "scene_id": "scene_002",
                        "title": "The Journey",
                        "location": "Forest path",
                        "time": "Morning",
                        "shots": [
                            {
                                "shot_id": "shot_003",
                                "shot_type": "tracking",
                                "description": "Following character through trees",
                                "camera_movement": "tracking",
                                "duration_seconds": 6,
                                "image_prompt": "Person walking through forest path, dappled sunlight, green foliage",
                                "video_prompt": "Camera tracks forward following walking figure through forest"
                            }
                        ]
                    }
                ]
            }, indent=2)
        # Detect character extraction request
        elif "character" in last_message.lower() and ("extract" in last_message.lower() or "find" in last_message.lower()):
            mock_content = json.dumps([
                {
                    "name": "John",
                    "description": "A brave adventurer with kind eyes",
                    "role": "protagonist",
                    "visual_traits": ["tall", "dark hair", "leather jacket"]
                },
                {
                    "name": "Mary",
                    "description": "A wise guide with ancient knowledge",
                    "role": "supporting",
                    "visual_traits": ["silver hair", "long robes", "gentle smile"]
                }
            ], indent=2)
        else:
            # Simple mock response
            mock_content = f"Mock LLM response for: {last_message[:100]}..."

        return LLMResponse(
            content=mock_content,
            model=model,
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            cost=0.0,
        )

    async def chat_with_structured_output(
        self,
        messages: List[Message],
        output_schema: type,
        **kwargs,
    ) -> Any:
        """
        Chat with structured JSON output.

        Args:
            messages: Chat messages
            output_schema: Pydantic model for output
            **kwargs: Additional parameters

        Returns:
            Parsed Pydantic model instance
        """
        # Add schema instruction to system message
        schema_instruction = f"""
You must respond with valid JSON matching this schema:
{json.dumps(output_schema.model_json_schema(), indent=2)}

Respond ONLY with the JSON, no other text.
"""

        # Prepend or append schema instruction
        messages_copy = list(messages)
        if messages_copy and messages_copy[0].role == "system":
            messages_copy[0] = Message(
                role="system",
                content=messages_copy[0].content + "\n\n" + schema_instruction,
            )
        else:
            messages_copy.insert(0, Message(role="system", content=schema_instruction))

        response = await self.chat(messages_copy, **kwargs)

        # Parse JSON response
        try:
            # Try to extract JSON from response
            content = response.content.strip()

            # Handle code blocks
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])

            data = json.loads(content)
            return output_schema(**data)
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse structured output: {e}")
            raise ValueError(f"LLM response was not valid JSON: {response.content[:200]}")

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Simple text generation.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))

        response = await self.chat(messages, **kwargs)
        return response.content

    def _estimate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """Estimate cost based on model and token usage."""
        # Approximate costs per 1K tokens (input, output)
        costs = {
            "openrouter/moonshotai/kimi-k2.5": (0.0005, 0.0028),  # $0.50/$2.80 per 1M tokens
            "openrouter/anthropic/claude-3.5-sonnet": (0.003, 0.015),
            "openrouter/anthropic/claude-3-opus": (0.015, 0.075),
            "openrouter/openai/gpt-4-turbo": (0.01, 0.03),
            "openrouter/openai/gpt-4o": (0.005, 0.015),
            "openrouter/google/gemini-pro": (0.00025, 0.0005),
        }

        if model in costs:
            input_cost, output_cost = costs[model]
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            return (prompt_tokens * input_cost + completion_tokens * output_cost) / 1000

        return 0.0


# Convenience functions
async def chat(
    messages: List[Union[Message, Dict[str, str]]],
    model: str = "kimi-k2.5",
    **kwargs,
) -> str:
    """Quick function for LLM chat."""
    adapter = LLMAdapter(LLMAdapterConfig(model=model))
    response = await adapter.chat(messages, **kwargs)
    return response.content


async def generate(prompt: str, model: str = "kimi-k2.5", **kwargs) -> str:
    """Quick function for text generation."""
    adapter = LLMAdapter(LLMAdapterConfig(model=model))
    return await adapter.generate_text(prompt, **kwargs)
