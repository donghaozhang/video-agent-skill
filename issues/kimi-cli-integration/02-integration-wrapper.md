# Phase 2: Create Integration Wrapper

**Created:** 2026-01-28
**Branch:** `feature/kimi-cli-integration`
**Status:** Pending
**Estimated Effort:** 3-4 hours
**Dependencies:** Phase 1 complete

---

## Objective

Create a wrapper layer that integrates the Kimi SDK with our existing patterns, providing both sync and async interfaces.

---

## Subtasks

### 2.1 Create Kimi Client Wrapper

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/integrations/kimi/client.py`

```python
"""
Kimi SDK client wrapper for AI Content Pipeline.

Provides sync and async interfaces to Kimi's AI capabilities.
"""

import os
import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from functools import wraps

# Lazy import to avoid requiring kimi-sdk if not used
_kimi_sdk = None


def _get_kimi_sdk():
    """Lazy import of kimi_sdk."""
    global _kimi_sdk
    if _kimi_sdk is None:
        try:
            import kimi_sdk
            _kimi_sdk = kimi_sdk
        except ImportError:
            raise ImportError(
                "kimi-sdk not installed. Run: pip install kimi-sdk"
            )
    return _kimi_sdk


@dataclass
class KimiResponse:
    """Standardized response from Kimi operations."""
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    model_used: str = "kimi"
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class KimiClient:
    """
    Low-level client for Kimi SDK operations.

    Handles authentication, API calls, and error handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize Kimi client.

        Args:
            api_key: Kimi API key (defaults to KIMI_API_KEY env var)
            base_url: API base URL (defaults to KIMI_BASE_URL env var)
        """
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        self.base_url = base_url or os.getenv("KIMI_BASE_URL")

        if not self.api_key:
            raise ValueError(
                "KIMI_API_KEY not provided. Set environment variable or pass api_key."
            )

        self._client = None

    @property
    def client(self):
        """Lazy initialization of Kimi client."""
        if self._client is None:
            sdk = _get_kimi_sdk()
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = sdk.Kimi(**kwargs)
        return self._client

    async def generate_async(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        on_message_part: Optional[Callable] = None,
    ) -> KimiResponse:
        """
        Generate completion asynchronously.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            on_message_part: Optional callback for streaming

        Returns:
            KimiResponse with generated content
        """
        sdk = _get_kimi_sdk()

        try:
            # Convert to SDK Message format
            sdk_messages = [
                sdk.Message(role=m["role"], content=m["content"])
                for m in messages
            ]

            kwargs = {"messages": sdk_messages}
            if system_prompt:
                kwargs["system_prompt"] = system_prompt
            if on_message_part:
                kwargs["on_message_part"] = on_message_part

            response = await self.client.generate(**kwargs)

            return KimiResponse(
                success=True,
                content=response if isinstance(response, str) else str(response),
                model_used="kimi",
            )

        except Exception as e:
            return KimiResponse(
                success=False,
                error=str(e),
                model_used="kimi",
            )

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> KimiResponse:
        """
        Generate completion synchronously.

        Wrapper around async generate for sync contexts.
        """
        return asyncio.run(
            self.generate_async(messages, system_prompt)
        )

    async def step_async(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[Any] = None,
        system_prompt: Optional[str] = None,
    ) -> KimiResponse:
        """
        Execute single agent step with optional tool use.

        Args:
            messages: Conversation messages
            tools: Optional SimpleToolset for tool calling
            system_prompt: Optional system prompt

        Returns:
            KimiResponse with step result
        """
        sdk = _get_kimi_sdk()

        try:
            sdk_messages = [
                sdk.Message(role=m["role"], content=m["content"])
                for m in messages
            ]

            kwargs = {"messages": sdk_messages}
            if tools:
                kwargs["toolset"] = tools
            if system_prompt:
                kwargs["system_prompt"] = system_prompt

            result = await self.client.step(**kwargs)

            return KimiResponse(
                success=True,
                content=str(result),
                model_used="kimi",
                metadata={"step_result": result},
            )

        except Exception as e:
            return KimiResponse(
                success=False,
                error=str(e),
                model_used="kimi",
            )

    def step(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[Any] = None,
        system_prompt: Optional[str] = None,
    ) -> KimiResponse:
        """Synchronous step execution."""
        return asyncio.run(
            self.step_async(messages, tools, system_prompt)
        )


class KimiIntegration:
    """
    High-level integration class for AI Content Pipeline.

    Provides convenient methods for common use cases.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize Kimi integration."""
        self.client = KimiClient(api_key=api_key, base_url=base_url)

    def analyze_code(
        self,
        code: str,
        question: Optional[str] = None,
        language: str = "python",
    ) -> KimiResponse:
        """
        Analyze code and answer questions about it.

        Args:
            code: Source code to analyze
            question: Optional specific question
            language: Programming language

        Returns:
            KimiResponse with analysis
        """
        prompt = f"Analyze this {language} code"
        if question:
            prompt += f" and answer: {question}"

        messages = [
            {"role": "user", "content": f"{prompt}\n\n```{language}\n{code}\n```"}
        ]

        system = (
            f"You are a code analysis expert specializing in {language}. "
            "Provide clear, actionable insights."
        )

        return self.client.generate(messages, system_prompt=system)

    def generate_code(
        self,
        prompt: str,
        language: str = "python",
        context: Optional[str] = None,
    ) -> KimiResponse:
        """
        Generate code from natural language description.

        Args:
            prompt: Description of what code should do
            language: Target programming language
            context: Optional existing code context

        Returns:
            KimiResponse with generated code
        """
        user_message = prompt
        if context:
            user_message = f"Context:\n```{language}\n{context}\n```\n\n{prompt}"

        messages = [{"role": "user", "content": user_message}]

        system = (
            f"You are a {language} code generation expert. "
            "Generate clean, well-documented code. "
            "Return only code blocks, no explanations unless asked."
        )

        return self.client.generate(messages, system_prompt=system)

    def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
    ) -> KimiResponse:
        """
        Simple chat interface.

        Args:
            message: User message
            history: Optional conversation history
            system_prompt: Optional system prompt

        Returns:
            KimiResponse with assistant reply
        """
        messages = history or []
        messages.append({"role": "user", "content": message})

        return self.client.generate(messages, system_prompt=system_prompt)

    async def chat_async(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
    ) -> KimiResponse:
        """Async chat interface."""
        messages = history or []
        messages.append({"role": "user", "content": message})

        return await self.client.generate_async(messages, system_prompt=system_prompt)

    def is_available(self) -> bool:
        """Check if Kimi SDK is available and configured."""
        try:
            _get_kimi_sdk()
            return bool(os.getenv("KIMI_API_KEY"))
        except ImportError:
            return False
```

---

### 2.2 Create Custom Tools for Kimi Agent

**File:** `packages/core/ai_content_pipeline/ai_content_pipeline/integrations/kimi/tools.py`

```python
"""
Custom tools for Kimi agent integration.

These tools allow Kimi to interact with AI Content Pipeline capabilities.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Result from tool execution."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class PipelineTools:
    """
    Tools that Kimi can use to interact with AI Content Pipeline.

    Example tools for:
    - Listing available models
    - Running pipeline steps
    - Analyzing outputs
    """

    def __init__(self):
        """Initialize pipeline tools."""
        self._model_cache = None

    def list_models(self, category: Optional[str] = None) -> ToolResult:
        """
        List available AI models.

        Args:
            category: Optional filter by category (image, video, avatar, etc.)

        Returns:
            ToolResult with model list
        """
        try:
            from ...config.constants import SUPPORTED_MODELS

            if category:
                models = SUPPORTED_MODELS.get(category, [])
            else:
                models = SUPPORTED_MODELS

            return ToolResult(success=True, data=models)

        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def get_model_info(self, model_name: str) -> ToolResult:
        """
        Get detailed information about a specific model.

        Args:
            model_name: Model identifier

        Returns:
            ToolResult with model details
        """
        try:
            from ...config.constants import (
                SUPPORTED_MODELS,
                MODEL_RECOMMENDATIONS,
                COST_ESTIMATES,
            )

            # Find model category
            model_category = None
            for category, models in SUPPORTED_MODELS.items():
                if model_name in models:
                    model_category = category
                    break

            if not model_category:
                return ToolResult(
                    success=False,
                    error=f"Model '{model_name}' not found"
                )

            info = {
                "name": model_name,
                "category": model_category,
                "cost_estimate": COST_ESTIMATES.get(model_category, {}).get(model_name),
            }

            return ToolResult(success=True, data=info)

        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def validate_pipeline_config(self, config: Dict[str, Any]) -> ToolResult:
        """
        Validate a pipeline configuration.

        Args:
            config: Pipeline configuration dict

        Returns:
            ToolResult with validation result
        """
        try:
            errors = []
            warnings = []

            # Check required fields
            if "name" not in config:
                errors.append("Missing required field: 'name'")

            if "steps" not in config:
                errors.append("Missing required field: 'steps'")
            elif not isinstance(config["steps"], list):
                errors.append("'steps' must be a list")
            elif len(config["steps"]) == 0:
                warnings.append("Pipeline has no steps")

            # Validate each step
            for i, step in enumerate(config.get("steps", [])):
                if "name" not in step:
                    errors.append(f"Step {i}: missing 'name'")
                if "type" not in step:
                    errors.append(f"Step {i}: missing 'type'")

            result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
            }

            return ToolResult(success=True, data=result)

        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def estimate_pipeline_cost(self, config: Dict[str, Any]) -> ToolResult:
        """
        Estimate total cost for a pipeline.

        Args:
            config: Pipeline configuration dict

        Returns:
            ToolResult with cost estimate
        """
        try:
            from ...config.constants import COST_ESTIMATES

            total_cost = 0.0
            step_costs = []

            for step in config.get("steps", []):
                step_type = step.get("type", "")
                model = step.get("model", "")

                # Get cost from constants
                category_costs = COST_ESTIMATES.get(step_type, {})
                step_cost = category_costs.get(model, 0.01)  # Default $0.01

                step_costs.append({
                    "step": step.get("name", "unnamed"),
                    "model": model,
                    "estimated_cost": step_cost,
                })
                total_cost += step_cost

            return ToolResult(
                success=True,
                data={
                    "total_estimated_cost": round(total_cost, 4),
                    "step_breakdown": step_costs,
                    "currency": "USD",
                }
            )

        except Exception as e:
            return ToolResult(success=False, error=str(e))


def create_kimi_toolset():
    """
    Create a Kimi-compatible toolset from PipelineTools.

    Returns:
        SimpleToolset configured with pipeline tools
    """
    try:
        from kimi_sdk import SimpleToolset, CallableTool2, ToolOk, ToolError
        from pydantic import BaseModel
    except ImportError:
        return None

    tools = PipelineTools()

    # Define tool parameter models
    class ListModelsParams(BaseModel):
        category: Optional[str] = None

    class GetModelInfoParams(BaseModel):
        model_name: str

    class ValidatePipelineParams(BaseModel):
        config: Dict[str, Any]

    class EstimateCostParams(BaseModel):
        config: Dict[str, Any]

    # Create callable tools
    class ListModelsTool(CallableTool2):
        name = "list_models"
        description = "List available AI models in the pipeline"
        parameters = ListModelsParams

        async def call(self, params: ListModelsParams):
            result = tools.list_models(params.category)
            if result.success:
                return ToolOk(result.data)
            return ToolError(result.error)

    class GetModelInfoTool(CallableTool2):
        name = "get_model_info"
        description = "Get detailed information about a specific AI model"
        parameters = GetModelInfoParams

        async def call(self, params: GetModelInfoParams):
            result = tools.get_model_info(params.model_name)
            if result.success:
                return ToolOk(result.data)
            return ToolError(result.error)

    class ValidatePipelineTool(CallableTool2):
        name = "validate_pipeline"
        description = "Validate a pipeline configuration for errors"
        parameters = ValidatePipelineParams

        async def call(self, params: ValidatePipelineParams):
            result = tools.validate_pipeline_config(params.config)
            if result.success:
                return ToolOk(result.data)
            return ToolError(result.error)

    class EstimateCostTool(CallableTool2):
        name = "estimate_cost"
        description = "Estimate the cost of running a pipeline"
        parameters = EstimateCostParams

        async def call(self, params: EstimateCostParams):
            result = tools.estimate_pipeline_cost(params.config)
            if result.success:
                return ToolOk(result.data)
            return ToolError(result.error)

    return SimpleToolset([
        ListModelsTool(),
        GetModelInfoTool(),
        ValidatePipelineTool(),
        EstimateCostTool(),
    ])
```

---

### 2.3 Update Package Exports

**Update:** `packages/core/ai_content_pipeline/ai_content_pipeline/__init__.py`

Add to exports:
```python
# Add to imports
from .integrations.kimi import KimiIntegration, KimiClient

# Add to __all__
__all__ = [
    # ... existing exports ...
    "KimiIntegration",
    "KimiClient",
]
```

---

## Commit Checkpoint

```bash
git add .
git commit -m "feat: Add Kimi SDK integration wrapper with tools"
git push origin feature/kimi-cli-integration
```

---

## Verification Checklist

- [ ] KimiClient class created with sync/async methods
- [ ] KimiIntegration high-level interface implemented
- [ ] PipelineTools created for Kimi agent use
- [ ] Kimi toolset factory function working
- [ ] Package exports updated
- [ ] No import errors

---

## Testing Commands

```python
# Quick integration test
from ai_content_pipeline.integrations.kimi import KimiIntegration

# Check availability
kimi = KimiIntegration()
print(f"Kimi available: {kimi.is_available()}")

# Test code analysis (requires API key)
if kimi.is_available():
    result = kimi.analyze_code("def hello(): print('world')")
    print(result.content)
```
