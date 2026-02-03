"""
Tests for ViMax base classes.
"""

import pytest
import sys
import os
import importlib.util


def load_module_directly(module_path: str, module_name: str):
    """Load a module directly from file path without going through package imports."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Get paths
vimax_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages', 'core', 'ai_content_platform', 'vimax')

# Load modules directly to avoid relative import issues
agents_base = load_module_directly(
    os.path.join(vimax_path, 'agents', 'base.py'),
    'vimax_agents_base'
)
adapters_base = load_module_directly(
    os.path.join(vimax_path, 'adapters', 'base.py'),
    'vimax_adapters_base'
)

# Get classes
BaseAgent = agents_base.BaseAgent
AgentConfig = agents_base.AgentConfig
AgentResult = agents_base.AgentResult
BaseAdapter = adapters_base.BaseAdapter
AdapterConfig = adapters_base.AdapterConfig


class TestAgentResult:
    """Tests for AgentResult."""

    def test_ok_result(self):
        """Test successful result."""
        result = AgentResult.ok("test_data", elapsed=1.5)
        assert result.success is True
        assert result.result == "test_data"
        assert result.metadata["elapsed"] == 1.5

    def test_fail_result(self):
        """Test failed result."""
        result = AgentResult.fail("error message")
        assert result.success is False
        assert result.error == "error message"
        assert result.result is None

    def test_result_with_complex_data(self):
        """Test result with complex data."""
        data = {"characters": ["John", "Mary"], "count": 2}
        result = AgentResult.ok(data)
        assert result.success is True
        assert result.result["count"] == 2


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = AgentConfig(name="test_agent")
        assert config.name == "test_agent"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7

    def test_custom_config(self):
        """Test custom configuration."""
        config = AgentConfig(
            name="test",
            model="claude-3",
            temperature=0.5,
            max_retries=5,
        )
        assert config.model == "claude-3"
        assert config.max_retries == 5

    def test_config_extra_fields(self):
        """Test extra configuration fields."""
        config = AgentConfig(
            name="test",
            extra={"custom_param": "value"}
        )
        assert config.extra["custom_param"] == "value"


class TestAdapterConfig:
    """Tests for AdapterConfig."""

    def test_default_adapter_config(self):
        """Test default adapter config."""
        config = AdapterConfig()
        assert config.provider == "fal"
        assert config.timeout == 120.0

    def test_custom_adapter_config(self):
        """Test custom adapter config."""
        config = AdapterConfig(
            provider="replicate",
            model="flux_dev",
            timeout=60.0,
        )
        assert config.provider == "replicate"
        assert config.model == "flux_dev"
