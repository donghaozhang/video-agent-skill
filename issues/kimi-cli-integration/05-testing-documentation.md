# Phase 5: Testing & Documentation

**Created:** 2026-01-28
**Branch:** `feature/kimi-cli-integration`
**Status:** Pending
**Estimated Effort:** 2-3 hours
**Dependencies:** Phases 1-4 complete

---

## Objective

Create comprehensive tests and documentation for the Kimi integration.

---

## Subtasks

### 5.1 Unit Tests for Kimi Client

**File:** `tests/test_kimi_client.py`

```python
"""Unit tests for Kimi client wrapper."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os


class TestKimiClient:
    """Tests for KimiClient class."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        with patch.dict(os.environ, {}, clear=True):
            from ai_content_pipeline.integrations.kimi.client import KimiClient

            client = KimiClient(api_key="test_key_123")
            assert client.api_key == "test_key_123"

    def test_init_from_env(self):
        """Test initialization from environment variable."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "env_key_456"}, clear=True):
            from ai_content_pipeline.integrations.kimi.client import KimiClient

            client = KimiClient()
            assert client.api_key == "env_key_456"

    def test_init_missing_key_raises(self):
        """Test that missing API key raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            from ai_content_pipeline.integrations.kimi.client import KimiClient

            with pytest.raises(ValueError, match="KIMI_API_KEY not provided"):
                KimiClient()

    def test_generate_success(self):
        """Test successful generation."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "test_key"}):
            from ai_content_pipeline.integrations.kimi.client import KimiClient

            client = KimiClient()

            # Mock the SDK
            mock_sdk = MagicMock()
            mock_sdk.Message = MagicMock
            mock_sdk.Kimi.return_value.generate = AsyncMock(
                return_value="Test response"
            )

            with patch(
                "ai_content_pipeline.integrations.kimi.client._get_kimi_sdk",
                return_value=mock_sdk
            ):
                result = client.generate(
                    messages=[{"role": "user", "content": "Hello"}]
                )

                assert result.success
                assert result.content == "Test response"

    def test_generate_error_handling(self):
        """Test error handling in generate."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "test_key"}):
            from ai_content_pipeline.integrations.kimi.client import KimiClient

            client = KimiClient()

            mock_sdk = MagicMock()
            mock_sdk.Message = MagicMock
            mock_sdk.Kimi.return_value.generate = AsyncMock(
                side_effect=Exception("API Error")
            )

            with patch(
                "ai_content_pipeline.integrations.kimi.client._get_kimi_sdk",
                return_value=mock_sdk
            ):
                result = client.generate(
                    messages=[{"role": "user", "content": "Hello"}]
                )

                assert not result.success
                assert "API Error" in result.error


class TestKimiIntegration:
    """Tests for KimiIntegration high-level interface."""

    def test_is_available_true(self):
        """Test is_available returns True when configured."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "test_key"}):
            from ai_content_pipeline.integrations.kimi.client import KimiIntegration

            with patch(
                "ai_content_pipeline.integrations.kimi.client._get_kimi_sdk",
                return_value=MagicMock()
            ):
                kimi = KimiIntegration()
                assert kimi.is_available()

    def test_is_available_no_key(self):
        """Test is_available returns False without key."""
        with patch.dict(os.environ, {}, clear=True):
            from ai_content_pipeline.integrations.kimi.client import KimiIntegration

            with patch(
                "ai_content_pipeline.integrations.kimi.client._get_kimi_sdk",
                return_value=MagicMock()
            ):
                # Can't instantiate without key, so check static method
                assert not os.getenv("KIMI_API_KEY")

    def test_analyze_code(self):
        """Test code analysis."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "test_key"}):
            from ai_content_pipeline.integrations.kimi.client import KimiIntegration

            kimi = KimiIntegration()

            with patch.object(kimi.client, "generate") as mock_gen:
                from ai_content_pipeline.integrations.kimi.client import KimiResponse
                mock_gen.return_value = KimiResponse(
                    success=True,
                    content="Code analysis result"
                )

                result = kimi.analyze_code(
                    code="def hello(): pass",
                    question="What does this do?",
                )

                assert result.success
                assert result.content == "Code analysis result"
                mock_gen.assert_called_once()

    def test_generate_code(self):
        """Test code generation."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "test_key"}):
            from ai_content_pipeline.integrations.kimi.client import KimiIntegration

            kimi = KimiIntegration()

            with patch.object(kimi.client, "generate") as mock_gen:
                from ai_content_pipeline.integrations.kimi.client import KimiResponse
                mock_gen.return_value = KimiResponse(
                    success=True,
                    content="def add(a, b): return a + b"
                )

                result = kimi.generate_code(
                    prompt="Create a function that adds two numbers",
                )

                assert result.success
                assert "def add" in result.content


class TestKimiResponse:
    """Tests for KimiResponse dataclass."""

    def test_successful_response(self):
        """Test successful response creation."""
        from ai_content_pipeline.integrations.kimi.client import KimiResponse

        response = KimiResponse(
            success=True,
            content="Hello world",
            model_used="kimi",
        )

        assert response.success
        assert response.content == "Hello world"
        assert response.error is None

    def test_error_response(self):
        """Test error response creation."""
        from ai_content_pipeline.integrations.kimi.client import KimiResponse

        response = KimiResponse(
            success=False,
            error="Something went wrong",
        )

        assert not response.success
        assert response.content is None
        assert response.error == "Something went wrong"
```

---

### 5.2 Unit Tests for Pipeline Generator

**File:** `tests/test_kimi_pipeline_generator.py`

```python
"""Unit tests for Kimi pipeline generator."""

import pytest
import yaml
from unittest.mock import patch, MagicMock
import os


class TestPipelineGenerator:
    """Tests for PipelineGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create generator with mocked Kimi."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "test_key"}):
            from ai_content_pipeline.integrations.kimi.pipeline_generator import (
                PipelineGenerator
            )
            return PipelineGenerator()

    def test_validate_valid_pipeline(self, generator):
        """Test validation of valid pipeline."""
        valid_yaml = """
name: "Test Pipeline"
description: "A test pipeline"

steps:
  - name: "step1"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "A sunset"
    output: "image"
"""
        result = generator.validate(valid_yaml)

        assert result["valid"]
        assert len(result["errors"]) == 0

    def test_validate_missing_name(self, generator):
        """Test validation catches missing name."""
        invalid_yaml = """
steps:
  - name: "step1"
    type: "text_to_image"
"""
        result = generator.validate(invalid_yaml)

        assert not result["valid"]
        assert any("name" in err for err in result["errors"])

    def test_validate_missing_steps(self, generator):
        """Test validation catches missing steps."""
        invalid_yaml = """
name: "Test"
description: "No steps"
"""
        result = generator.validate(invalid_yaml)

        assert not result["valid"]
        assert any("steps" in err for err in result["errors"])

    def test_validate_step_missing_type(self, generator):
        """Test validation catches step without type."""
        invalid_yaml = """
name: "Test"
steps:
  - name: "step1"
    model: "flux_dev"
"""
        result = generator.validate(invalid_yaml)

        assert not result["valid"]
        assert any("type" in err for err in result["errors"])

    def test_estimate_cost(self, generator):
        """Test cost estimation."""
        yaml_content = """
name: "Test"
steps:
  - name: "image"
    type: "text_to_image"
    model: "flux_dev"
  - name: "video"
    type: "image_to_video"
    model: "veo_3"
"""
        result = generator.estimate_cost(yaml_content)

        assert "total" in result
        assert result["total"] > 0
        assert len(result["breakdown"]) == 2

    def test_extract_yaml_from_code_block(self, generator):
        """Test YAML extraction from markdown code block."""
        content = """Here's your pipeline:

```yaml
name: "Test"
steps: []
```

That should work!"""

        extracted = generator._extract_yaml(content)
        assert extracted.startswith("name:")
        assert "```" not in extracted

    def test_extract_yaml_plain(self, generator):
        """Test YAML extraction from plain text."""
        content = """name: "Test"
steps: []
"""
        extracted = generator._extract_yaml(content)
        assert extracted == content.strip()


class TestAdvancedPipelineGenerator:
    """Tests for AdvancedPipelineGenerator."""

    @pytest.fixture
    def generator(self):
        """Create advanced generator."""
        with patch.dict(os.environ, {"KIMI_API_KEY": "test_key"}):
            from ai_content_pipeline.integrations.kimi.advanced_generator import (
                AdvancedPipelineGenerator
            )
            return AdvancedPipelineGenerator()

    def test_list_templates(self, generator):
        """Test template listing."""
        templates = generator.list_templates()

        assert len(templates) > 0
        assert "image_generation" in templates
        assert "text_to_video" in templates

    def test_generate_from_template(self, generator):
        """Test template-based generation."""
        result = generator.generate_from_template(
            "image_generation",
            {
                "description": "Test image",
                "model": "flux_dev",
                "prompt": "A sunset",
                "width": 1024,
                "height": 1024,
            }
        )

        assert result.success
        assert "flux_dev" in result.content
        assert result.parsed is not None

    def test_generate_from_invalid_template(self, generator):
        """Test error on invalid template."""
        result = generator.generate_from_template(
            "nonexistent_template",
            {}
        )

        assert not result.success
        assert "Unknown template" in result.error

    def test_analyze_prompt_avatar(self, generator):
        """Test prompt analysis detects avatar."""
        from ai_content_pipeline.integrations.kimi.advanced_generator import (
            OptimizationGoal
        )

        template, params = generator._analyze_prompt(
            "Create a talking avatar from my portrait",
            OptimizationGoal.QUALITY,
        )

        # Should detect avatar-related template
        assert template is not None or "avatar" in str(params).lower()

    def test_analyze_prompt_video(self, generator):
        """Test prompt analysis detects video."""
        from ai_content_pipeline.integrations.kimi.advanced_generator import (
            OptimizationGoal
        )

        template, params = generator._analyze_prompt(
            "Generate a video of a sunset",
            OptimizationGoal.BALANCED,
        )

        assert template is not None


class TestPipelineTools:
    """Tests for pipeline tools."""

    def test_list_models(self):
        """Test model listing tool."""
        from ai_content_pipeline.integrations.kimi.tools import PipelineTools

        tools = PipelineTools()
        result = tools.list_models()

        assert result.success
        assert isinstance(result.data, dict)

    def test_validate_pipeline_config(self):
        """Test pipeline validation tool."""
        from ai_content_pipeline.integrations.kimi.tools import PipelineTools

        tools = PipelineTools()

        # Valid config
        valid_config = {
            "name": "Test",
            "steps": [
                {"name": "step1", "type": "text_to_image"}
            ]
        }
        result = tools.validate_pipeline_config(valid_config)
        assert result.success
        assert result.data["valid"]

        # Invalid config (missing steps)
        invalid_config = {"name": "Test"}
        result = tools.validate_pipeline_config(invalid_config)
        assert result.success  # Tool succeeded
        assert not result.data["valid"]  # But validation failed

    def test_estimate_pipeline_cost(self):
        """Test cost estimation tool."""
        from ai_content_pipeline.integrations.kimi.tools import PipelineTools

        tools = PipelineTools()
        config = {
            "steps": [
                {"name": "step1", "model": "flux_dev"},
            ]
        }

        result = tools.estimate_pipeline_cost(config)
        assert result.success
        assert "total_estimated_cost" in result.data
```

---

### 5.3 Integration Tests

**File:** `tests/test_kimi_integration.py`

```python
"""Integration tests for Kimi (requires API key)."""

import pytest
import os


# Skip all tests if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("KIMI_API_KEY"),
    reason="KIMI_API_KEY not set"
)


class TestKimiIntegrationLive:
    """Live integration tests (requires API key)."""

    def test_simple_chat(self):
        """Test basic chat functionality."""
        from ai_content_pipeline.integrations.kimi import KimiIntegration

        kimi = KimiIntegration()
        result = kimi.chat("Say 'test successful' and nothing else.")

        assert result.success
        assert "test" in result.content.lower() or "successful" in result.content.lower()

    def test_code_analysis(self):
        """Test code analysis."""
        from ai_content_pipeline.integrations.kimi import KimiIntegration

        kimi = KimiIntegration()
        result = kimi.analyze_code(
            code="def add(a, b): return a + b",
            question="What does this function do?",
        )

        assert result.success
        assert len(result.content) > 10  # Should have some explanation

    def test_pipeline_generation(self):
        """Test pipeline generation from prompt."""
        from ai_content_pipeline.integrations.kimi.pipeline_generator import (
            PipelineGenerator
        )

        generator = PipelineGenerator()
        result = generator.generate_from_prompt(
            "Create a simple image generation pipeline"
        )

        assert result.success
        assert "name:" in result.content or "steps:" in result.content
```

---

### 5.4 Update Documentation

**Update:** `CLAUDE.md`

Add section:

```markdown
### Kimi AI Integration

```bash
# Check Kimi status
ai-content-pipeline kimi-status

# Chat with Kimi
ai-content-pipeline kimi-chat -p "Explain this code" -c src/main.py

# Generate pipeline from description
ai-content-pipeline generate-pipeline -p "Create an avatar from text"

# Interactive pipeline builder
ai-content-pipeline pipeline-builder --goal quality

# List available templates
ai-content-pipeline list-templates
```

### Environment Variables (Kimi)
```bash
KIMI_API_KEY=your_kimi_api_key
KIMI_BASE_URL=https://api.moonshot.cn  # Optional
```
```

---

**Update:** `README.md`

Add section:

```markdown
## Kimi AI Integration

The AI Content Pipeline integrates with [Kimi CLI](https://github.com/MoonshotAI/kimi-cli) for:
- Natural language pipeline generation
- Code analysis and review
- Interactive pipeline building

### Quick Start

```bash
# Install Kimi SDK
pip install kimi-sdk

# Configure API key
export KIMI_API_KEY=your_key

# Generate a pipeline
aicp generate-pipeline -p "Create a video from a portrait photo"

# Interactive mode
aicp pipeline-builder
```

### Available Commands

| Command | Description |
|---------|-------------|
| `kimi-status` | Check Kimi configuration |
| `kimi-chat` | Chat with Kimi AI |
| `generate-pipeline` | Generate YAML from description |
| `pipeline-builder` | Interactive pipeline builder |
| `list-templates` | Show available templates |
```

---

### 5.5 Create Quick Start Guide

**File:** `docs/kimi-quickstart.md`

```markdown
# Kimi Integration Quick Start

## Prerequisites

1. Python 3.8+
2. Kimi API key (get from [moonshot.cn](https://moonshot.cn))

## Installation

```bash
# Install Kimi SDK
pip install kimi-sdk

# Or install with AI Content Pipeline
pip install -e .[kimi]
```

## Configuration

Add to `.env`:
```
KIMI_API_KEY=your_api_key_here
```

Or export:
```bash
export KIMI_API_KEY=your_api_key_here
```

## Verify Setup

```bash
aicp kimi-status
```

Expected output:
```
✓ kimi-sdk installed (v1.2.0)
✓ KIMI_API_KEY set
✓ Connection successful
```

## Usage Examples

### Generate a Pipeline

```bash
# Simple image generation
aicp generate-pipeline -p "Create an image of a sunset"

# With cost estimate
aicp generate-pipeline -p "Make a talking avatar" --estimate-cost

# Save to specific file
aicp generate-pipeline -p "Create a video" -o my_pipeline.yaml
```

### Code Analysis

```bash
# Analyze a file
aicp kimi-chat -p "Review for bugs" -c src/main.py

# Save analysis
aicp kimi-chat -p "Explain this" -c code.py -o explanation.md
```

### Interactive Mode

```bash
# Start interactive builder
aicp pipeline-builder

# With quality optimization
aicp pipeline-builder --goal quality
```

## Troubleshooting

### "kimi-sdk not installed"
```bash
pip install kimi-sdk
```

### "KIMI_API_KEY not set"
```bash
export KIMI_API_KEY=your_key
# Or add to .env file
```

### "Connection failed"
- Check your API key is valid
- Ensure network connectivity to moonshot.cn
- Try with `KIMI_BASE_URL` if using custom endpoint

## Next Steps

- See [full documentation](KIMI_CLI_INTEGRATION.md)
- Explore [pipeline templates](../input/pipelines/examples/)
- Read [API reference](../packages/core/ai_content_pipeline/ai_content_pipeline/integrations/kimi/)
```

---

## Commit Checkpoint

```bash
git add .
git commit -m "feat: Add tests and documentation for Kimi integration"
git push origin feature/kimi-cli-integration
```

---

## Final Verification Checklist

- [ ] All unit tests pass: `pytest tests/test_kimi_*.py`
- [ ] Integration tests pass (with API key)
- [ ] CLAUDE.md updated
- [ ] README.md updated
- [ ] Quick start guide created
- [ ] All CLI commands documented

---

## Test Commands

```bash
# Run all Kimi tests
pytest tests/test_kimi_*.py -v

# Run with coverage
pytest tests/test_kimi_*.py --cov=ai_content_pipeline.integrations.kimi

# Run integration tests (requires API key)
KIMI_API_KEY=your_key pytest tests/test_kimi_integration.py -v

# Quick smoke test
python -c "from ai_content_pipeline.integrations.kimi import KimiIntegration; print('Import OK')"
```

---

## PR Checklist

Before creating PR:

- [ ] All phases completed
- [ ] Tests passing locally
- [ ] Documentation updated
- [ ] No sensitive data in commits
- [ ] Branch rebased on main
- [ ] Code follows project style

```bash
# Final checks
git diff main...feature/kimi-cli-integration --stat
pytest tests/ -v --tb=short
black --check packages/
```
