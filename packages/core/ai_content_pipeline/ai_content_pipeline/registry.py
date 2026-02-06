"""
Central Model Registry - Single source of truth for all AI model metadata.

This module provides the ModelDefinition dataclass and ModelRegistry class
that serve as the canonical source of model configuration. All provider
constants files and generators derive their data from this registry.

Usage:
    from ai_content_pipeline.registry import ModelDefinition, ModelRegistry

    # Register a model
    ModelRegistry.register(ModelDefinition(
        key="kling_3_standard",
        name="Kling Video v3 Standard",
        ...
    ))

    # Look up a model
    model = ModelRegistry.get("kling_3_standard")

    # List models by category
    t2v_models = ModelRegistry.keys_for_category("text_to_video")
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ModelDefinition:
    """Single source of truth for one AI model.

    Args:
        key: Unique model identifier (e.g., "kling_3_standard_i2v").
        name: Human-readable display name.
        provider: Provider company name.
        endpoint: FAL API endpoint string.
        categories: List of pipeline categories this model belongs to.
        description: Human-readable description of model capabilities.
        pricing: Pricing info - dict or float depending on model.
        duration_options: Valid duration values (strings or ints).
        aspect_ratios: Supported aspect ratios.
        provider_key: The key used by the provider package (defaults to key).
            When a model exists in multiple providers with different endpoints
            (e.g., kling_3_standard in both t2v and i2v), the registry key
            is unique (kling_3_standard_i2v) but provider_key matches the
            original provider constant (kling_3_standard).
        resolutions: Supported resolutions.
        defaults: Default parameter values.
        features: List of feature strings.
        max_duration: Maximum duration in seconds.
        extended_params: Extra API parameter names.
        extended_features: Capability flags for extended features.
        input_requirements: Required/optional input parameters.
        model_info: Additional metadata for MODEL_INFO dicts.
        cost_estimate: Default pipeline cost estimate (USD).
        processing_time: Estimated processing time (seconds).
    """
    key: str
    name: str
    provider: str
    endpoint: str
    categories: List[str]
    description: str
    pricing: Any
    duration_options: List[Any]
    aspect_ratios: List[str]
    provider_key: str = ""  # Defaults to key via __post_init__
    resolutions: List[str] = field(default_factory=lambda: ["720p"])
    defaults: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    max_duration: int = 15
    extended_params: List[str] = field(default_factory=list)
    extended_features: Dict[str, bool] = field(default_factory=dict)
    input_requirements: Dict[str, List[str]] = field(default_factory=dict)
    model_info: Dict[str, Any] = field(default_factory=dict)
    cost_estimate: float = 0.0
    processing_time: int = 60

    def __post_init__(self):
        """Set provider_key to key if not explicitly provided."""
        if not self.provider_key:
            self.provider_key = self.key


class ModelRegistry:
    """Central registry for all AI models.

    Class-level registry that all provider packages read from.
    Models are registered at import time via registry_data.py.
    """
    _models: Dict[str, ModelDefinition] = {}

    @classmethod
    def register(cls, model: ModelDefinition):
        """Register a model definition.

        Args:
            model: ModelDefinition to register.
        """
        cls._models[model.key] = model

    @classmethod
    def get(cls, key: str) -> ModelDefinition:
        """Get model by key.

        Args:
            key: Model identifier string.

        Returns:
            ModelDefinition for the given key.

        Raises:
            ValueError: If key is not registered.
        """
        if key not in cls._models:
            available = list(cls._models.keys())
            raise ValueError(f"Unknown model: {key}. Available: {available}")
        return cls._models[key]

    @classmethod
    def has(cls, key: str) -> bool:
        """Check if a model key is registered.

        Args:
            key: Model identifier string.

        Returns:
            True if model exists in registry.
        """
        return key in cls._models

    @classmethod
    def list_by_category(cls, category: str) -> List[ModelDefinition]:
        """Get all models in a category.

        Args:
            category: Category string (e.g., "text_to_video").

        Returns:
            List of ModelDefinition objects matching the category.
        """
        return [m for m in cls._models.values() if category in m.categories]

    @classmethod
    def all_keys(cls) -> List[str]:
        """Get all registered model keys.

        Returns:
            List of all model key strings.
        """
        return list(cls._models.keys())

    @classmethod
    def keys_for_category(cls, category: str) -> List[str]:
        """Get model keys for a category.

        Args:
            category: Category string (e.g., "text_to_video").

        Returns:
            List of model key strings in that category.
        """
        return [m.key for m in cls._models.values() if category in m.categories]

    @classmethod
    def get_supported_models(cls) -> Dict[str, List[str]]:
        """Get SUPPORTED_MODELS dict (category -> [keys]).

        Returns:
            Dict mapping category strings to lists of model keys.
        """
        result: Dict[str, List[str]] = {}
        for m in cls._models.values():
            for cat in m.categories:
                result.setdefault(cat, []).append(m.key)
        return result

    @classmethod
    def get_cost_estimates(cls) -> Dict[str, Dict[str, float]]:
        """Get COST_ESTIMATES dict (category -> {key: cost}).

        Returns:
            Dict mapping categories to dicts of model key -> cost estimate.
        """
        result: Dict[str, Dict[str, float]] = {}
        for m in cls._models.values():
            for cat in m.categories:
                result.setdefault(cat, {})[m.key] = m.cost_estimate
        return result

    @classmethod
    def get_processing_times(cls) -> Dict[str, Dict[str, int]]:
        """Get PROCESSING_TIME_ESTIMATES dict (category -> {key: seconds}).

        Returns:
            Dict mapping categories to dicts of model key -> processing seconds.
        """
        result: Dict[str, Dict[str, int]] = {}
        for m in cls._models.values():
            for cat in m.categories:
                result.setdefault(cat, {})[m.key] = m.processing_time
        return result

    @classmethod
    def provider_keys_for_category(cls, category: str) -> List[str]:
        """Get provider-facing model keys for a category.

        Uses provider_key (which may differ from registry key) so that
        provider constants files expose the same keys as before.

        Args:
            category: Category string (e.g., "image_to_video").

        Returns:
            List of provider key strings in that category.
        """
        return [m.provider_key for m in cls._models.values() if category in m.categories]

    @classmethod
    def list_by_category_as_provider_dict(cls, category: str) -> Dict[str, 'ModelDefinition']:
        """Get models in a category keyed by provider_key.

        Args:
            category: Category string.

        Returns:
            Dict mapping provider_key -> ModelDefinition.
        """
        return {m.provider_key: m for m in cls._models.values() if category in m.categories}

    @classmethod
    def get_by_provider_key(cls, provider_key: str) -> 'ModelDefinition':
        """Get model by provider_key (falls back to registry key lookup).

        Useful for provider packages where the local model key differs
        from the global registry key (e.g., i2v "kling_3_standard" maps
        to registry key "kling_3_standard_i2v").

        Args:
            provider_key: Provider-facing model key string.

        Returns:
            ModelDefinition matching the provider_key.

        Raises:
            ValueError: If no model matches.
        """
        # Fast path: check if it's a direct registry key
        if provider_key in cls._models:
            return cls._models[provider_key]
        # Slow path: search by provider_key field
        for m in cls._models.values():
            if m.provider_key == provider_key:
                return m
        available = list(cls._models.keys())
        raise ValueError(f"Unknown model: {provider_key}. Available: {available}")

    @classmethod
    def clear(cls):
        """Clear all registered models. Used for testing."""
        cls._models = {}

    @classmethod
    def count(cls) -> int:
        """Get total number of registered models.

        Returns:
            Number of models in the registry.
        """
        return len(cls._models)
