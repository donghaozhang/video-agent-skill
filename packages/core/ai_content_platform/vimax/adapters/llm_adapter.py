"""
LLM Adapter for ViMax agents.

Uses litellm for unified access to multiple LLM providers:
- OpenRouter (Claude, GPT-4, etc.)
- OpenAI
- Anthropic
- Google (Gemini)
"""

import os
import re
import json
from typing import Optional, Dict, Any, List, Union
import logging

from pydantic import BaseModel, Field, ValidationError

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
    max_tokens: int = 8192
    timeout: float = 60.0
    use_native_structured_output: bool = True  # Use OpenRouter response_format API


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
        """Send chat messages to LLM.

        Args:
            messages: List of Message objects or dicts with role/content keys.
            model: Model to use (default from config).
            temperature: Sampling temperature (default from config).
            max_tokens: Maximum tokens in response (default from config).
            **kwargs: Additional parameters passed to litellm.

        Returns:
            LLMResponse: Response containing content, usage stats, and cost.

        Cost:
            One LLM API call. Cost varies by model (see _estimate_cost).
            Returns mock response with zero cost if API key not configured.
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
            self.logger.exception("LLM call failed")
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
        schema_name: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Chat with structured JSON output.

        Uses native OpenRouter response_format when available (default),
        falling back to prompt-injection for models without support.

        Args:
            messages: Chat messages.
            output_schema: Pydantic model class for output parsing.
            schema_name: Name for the JSON schema (defaults to class name).
            **kwargs: Additional parameters passed to chat().

        Returns:
            Parsed instance of output_schema.

        Raises:
            ValueError: If LLM response is not valid JSON matching schema.

        Cost:
            One LLM API call (delegates to chat()).
        """
        if self.config.use_native_structured_output:
            return await self._structured_output_native(
                messages, output_schema, schema_name, **kwargs
            )
        return await self._structured_output_legacy(
            messages, output_schema, **kwargs
        )

    async def _structured_output_native(
        self,
        messages: List[Message],
        output_schema: type,
        schema_name: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Native structured output via OpenRouter response_format API.

        Passes a JSON schema via extra_body so the provider constrains
        token generation to valid JSON matching the schema.

        Args:
            messages: Chat messages.
            output_schema: Pydantic model class for output parsing.
            schema_name: Name for the JSON schema (defaults to class name).
            **kwargs: Additional parameters passed to chat().

        Returns:
            Parsed instance of output_schema.
        """
        name = schema_name or output_schema.__name__

        # Build extra_body with response_format for OpenRouter
        # Reason: litellm may strip response_format for OpenRouter, so we
        # pass it via extra_body which is forwarded verbatim to the provider.
        extra_body = {
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": name,
                    "strict": True,
                    "schema": output_schema.model_json_schema(),
                },
            },
            "provider": {
                "require_parameters": True,
            },
        }

        response = await self.chat(messages, extra_body=extra_body, **kwargs)

        try:
            data = json.loads(response.content)
            return output_schema(**data)
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(
                "Native structured output parse failed, trying legacy: %s", e
            )
            # Fallback: try legacy parsing on the same response
            return self._parse_json_response(response.content, output_schema)

    async def _structured_output_legacy(
        self,
        messages: List[Message],
        output_schema: type,
        **kwargs,
    ) -> Any:
        """Legacy structured output via prompt injection.

        Appends the JSON schema to the system message and parses the
        response with regex extraction.

        Args:
            messages: Chat messages.
            output_schema: Pydantic model class for output parsing.
            **kwargs: Additional parameters passed to chat().

        Returns:
            Parsed instance of output_schema.
        """
        schema_instruction = f"""
You must respond with valid JSON matching this schema:
{json.dumps(output_schema.model_json_schema(), indent=2)}

Respond ONLY with the JSON, no other text.
"""
        messages_copy = list(messages)
        if messages_copy and messages_copy[0].role == "system":
            messages_copy[0] = Message(
                role="system",
                content=messages_copy[0].content + "\n\n" + schema_instruction,
            )
        else:
            messages_copy.insert(0, Message(role="system", content=schema_instruction))

        response = await self.chat(messages_copy, **kwargs)
        return self._parse_json_response(response.content, output_schema)

    def _parse_json_response(self, content: str, output_schema: type) -> Any:
        """Parse JSON from LLM response text, handling common quirks.

        Tries multiple extraction strategies in order:
        1. Direct json.loads
        2. Markdown code fence extraction
        3. Outermost {…} extraction with trailing-comma fix

        Args:
            content: Raw LLM response text.
            output_schema: Pydantic model class for validation.

        Returns:
            Parsed instance of output_schema.

        Raises:
            ValueError: If response cannot be parsed as valid JSON.
        """
        content = content.strip()

        def _try_parse(json_str: str, label: str) -> Any:
            """Try to parse JSON and validate against schema."""
            # Fix trailing commas before parsing
            fixed = re.sub(r',\s*([}\]])', r'\1', json_str)
            try:
                data = json.loads(fixed)
                return output_schema(**data)
            except json.JSONDecodeError as e:
                self.logger.debug("JSON parse failed (%s): %s", label, e)
            except ValidationError as e:
                self.logger.debug("Schema validation failed (%s): %s", label, e)
            return None

        # Step 1: Try direct parse
        result = _try_parse(content, "direct")
        if result is not None:
            return result

        # Step 2: Try extracting from markdown code fence
        fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if fence_match:
            result = _try_parse(fence_match.group(1), "code_fence")
            if result is not None:
                return result

        # Step 3: Try extracting outermost JSON object
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            result = _try_parse(match.group(0), "outermost_braces")
            if result is not None:
                return result

        raise ValueError(f"LLM response was not valid JSON: {content[:200]}")

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Simple text generation.

        Args:
            prompt: User prompt text.
            system_prompt: Optional system prompt for context.
            **kwargs: Additional parameters passed to chat().

        Returns:
            str: Generated text content.

        Cost:
            One LLM API call (delegates to chat()).
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
    """Quick function for LLM chat.

    Args:
        messages: List of chat messages.
        model: Model alias or full name.
        **kwargs: Additional parameters.

    Returns:
        str: Generated response content.

    Cost:
        One LLM API call.
    """
    adapter = LLMAdapter(LLMAdapterConfig(model=model))
    response = await adapter.chat(messages, **kwargs)
    return response.content


async def generate(prompt: str, model: str = "kimi-k2.5", **kwargs) -> str:
    """Quick function for text generation.

    Args:
        prompt: Text prompt.
        model: Model alias or full name.
        **kwargs: Additional parameters.

    Returns:
        str: Generated text.

    Cost:
        One LLM API call.
    """
    adapter = LLMAdapter(LLMAdapterConfig(model=model))
    return await adapter.generate_text(prompt, **kwargs)
