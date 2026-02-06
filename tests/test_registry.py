"""Tests for the central model registry."""

import pytest
from ai_content_pipeline.registry import ModelDefinition, ModelRegistry


@pytest.fixture(autouse=True)
def clean_registry():
    """Save and restore registry state around each test."""
    saved = dict(ModelRegistry._models)
    yield
    ModelRegistry._models = saved


def _make_model(key="test_model", categories=None, **kwargs):
    """Helper to create a ModelDefinition with sensible defaults."""
    defaults = dict(
        key=key,
        name="Test Model",
        provider="TestProvider",
        endpoint="fal-ai/test/endpoint",
        categories=categories or ["test_category"],
        description="A test model",
        pricing={"base": 0.1},
        duration_options=[5, 10],
        aspect_ratios=["16:9"],
    )
    defaults.update(kwargs)
    return ModelDefinition(**defaults)


def test_register_and_get():
    """Register a model and retrieve it by key."""
    model = _make_model()
    ModelRegistry.register(model)
    retrieved = ModelRegistry.get("test_model")
    assert retrieved.name == "Test Model"
    assert retrieved.endpoint == "fal-ai/test/endpoint"


def test_get_unknown_raises():
    """get() raises ValueError for unknown model."""
    with pytest.raises(ValueError, match="Unknown model"):
        ModelRegistry.get("nonexistent_model_xyz_12345")


def test_has():
    """has() returns True for registered, False for unknown."""
    model = _make_model(key="has_test")
    ModelRegistry.register(model)
    assert ModelRegistry.has("has_test")
    assert not ModelRegistry.has("no_such_model_xyz")


def test_list_by_category():
    """list_by_category returns models matching the category."""
    ModelRegistry.register(_make_model(key="cat_a", categories=["alpha"]))
    ModelRegistry.register(_make_model(key="cat_b", categories=["beta"]))
    ModelRegistry.register(_make_model(key="cat_ab", categories=["alpha", "beta"]))

    alpha = ModelRegistry.list_by_category("alpha")
    alpha_keys = [m.key for m in alpha]
    assert "cat_a" in alpha_keys
    assert "cat_ab" in alpha_keys
    assert "cat_b" not in alpha_keys


def test_keys_for_category():
    """keys_for_category returns only matching keys."""
    ModelRegistry.register(_make_model(key="kfc_1", categories=["video"]))
    ModelRegistry.register(_make_model(key="kfc_2", categories=["image"]))
    keys = ModelRegistry.keys_for_category("video")
    assert "kfc_1" in keys
    assert "kfc_2" not in keys


def test_all_keys():
    """all_keys returns all registered model keys."""
    ModelRegistry.register(_make_model(key="ak_1"))
    ModelRegistry.register(_make_model(key="ak_2"))
    keys = ModelRegistry.all_keys()
    assert "ak_1" in keys
    assert "ak_2" in keys


def test_duplicate_key_overwrites():
    """Duplicate key registration overwrites cleanly."""
    ModelRegistry.register(_make_model(key="dup", name="V1"))
    ModelRegistry.register(_make_model(key="dup", name="V2"))
    assert ModelRegistry.get("dup").name == "V2"


def test_get_supported_models():
    """get_supported_models returns category -> [keys] dict."""
    ModelRegistry.register(_make_model(key="sm_1", categories=["t2v"]))
    ModelRegistry.register(_make_model(key="sm_2", categories=["t2v", "i2v"]))
    supported = ModelRegistry.get_supported_models()
    assert "sm_1" in supported.get("t2v", [])
    assert "sm_2" in supported.get("t2v", [])
    assert "sm_2" in supported.get("i2v", [])
    assert "sm_1" not in supported.get("i2v", [])


def test_get_cost_estimates():
    """get_cost_estimates returns category -> {key: cost} dict."""
    ModelRegistry.register(_make_model(key="ce_1", categories=["t2v"], cost_estimate=1.50))
    costs = ModelRegistry.get_cost_estimates()
    assert costs.get("t2v", {}).get("ce_1") == 1.50


def test_get_processing_times():
    """get_processing_times returns category -> {key: seconds} dict."""
    ModelRegistry.register(_make_model(key="pt_1", categories=["t2v"], processing_time=120))
    times = ModelRegistry.get_processing_times()
    assert times.get("t2v", {}).get("pt_1") == 120


def test_count():
    """count() returns number of registered models."""
    initial = ModelRegistry.count()
    ModelRegistry.register(_make_model(key="count_1"))
    ModelRegistry.register(_make_model(key="count_2"))
    assert ModelRegistry.count() == initial + 2


def test_clear():
    """clear() removes all models."""
    ModelRegistry.register(_make_model(key="clear_test"))
    ModelRegistry.clear()
    assert ModelRegistry.count() == 0
    assert not ModelRegistry.has("clear_test")


def test_model_definition_defaults():
    """ModelDefinition has correct default values."""
    model = _make_model()
    assert model.resolutions == ["720p"]
    assert model.defaults == {}
    assert model.features == []
    assert model.max_duration == 15
    assert model.extended_params == []
    assert model.extended_features == {}
    assert model.input_requirements == {}
    assert model.model_info == {}
    assert model.cost_estimate == 0.0
    assert model.processing_time == 60
