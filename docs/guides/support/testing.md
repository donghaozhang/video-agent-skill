# Testing Guide

How to test your AI content generation pipelines and integrations.

## Testing Strategies

### Free Testing (No API Costs)

#### Mock Mode

Test CLI commands without API calls:

```bash
# Image generation mock
ai-content-pipeline generate-image --text "test prompt" --mock

# Pipeline dry run
ai-content-pipeline run-chain --config pipeline.yaml --dry-run

# Validates configuration without executing
```

#### Configuration Validation

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('pipeline.yaml'))"

# Estimate cost (no execution)
ai-content-pipeline estimate-cost --config pipeline.yaml
```

### Cheap Testing (Minimal Cost)

Use budget models for validation:

```bash
# Cheapest image model ($0.001)
ai-content-pipeline generate-image --text "test" --model flux_schnell

# Cheapest video model ($0.08)
ai-content-pipeline text-to-video --text "test" --model hailuo_pro
```

---

## Unit Testing

### Testing Pipeline Configurations

```python
import pytest
import yaml
from packages.core.ai_content_pipeline.config.validator import validate_config

class TestPipelineConfig:
    """Test pipeline configuration validation."""

    def test_valid_config(self):
        """Test that valid config passes validation."""
        config = {
            "name": "Test Pipeline",
            "steps": [
                {
                    "name": "image",
                    "type": "text_to_image",
                    "model": "flux_dev",
                    "params": {"prompt": "test"}
                }
            ]
        }
        assert validate_config(config) is True

    def test_missing_steps(self):
        """Test that config without steps fails."""
        config = {"name": "Test Pipeline"}
        with pytest.raises(ValueError):
            validate_config(config)

    def test_invalid_model(self):
        """Test that invalid model name fails."""
        config = {
            "name": "Test",
            "steps": [
                {
                    "type": "text_to_image",
                    "model": "nonexistent_model"
                }
            ]
        }
        with pytest.raises(ValueError):
            validate_config(config)
```

### Testing with Mocks

```python
import pytest
from unittest.mock import Mock, patch
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

class TestAIPipelineManager:
    """Test pipeline manager with mocked API calls."""

    @patch('packages.core.ai_content_pipeline.providers.fal.FALProvider')
    def test_generate_image_success(self, mock_provider):
        """Test successful image generation."""
        # Setup mock
        mock_provider.return_value.generate.return_value = Mock(
            success=True,
            output_path="/tmp/test.png",
            cost=0.003
        )

        manager = AIPipelineManager()
        result = manager.generate_image(prompt="test", model="flux_dev")

        assert result.success is True
        assert result.output_path == "/tmp/test.png"

    @patch('packages.core.ai_content_pipeline.providers.fal.FALProvider')
    def test_generate_image_failure(self, mock_provider):
        """Test image generation failure handling."""
        mock_provider.return_value.generate.side_effect = Exception("API Error")

        manager = AIPipelineManager()
        with pytest.raises(Exception):
            manager.generate_image(prompt="test")
```

### Testing Prompts

```python
def test_prompt_sanitization():
    """Test prompt sanitization."""
    from packages.core.ai_content_pipeline.utils.prompts import sanitize_prompt

    # Test normal prompt
    assert sanitize_prompt("a beautiful sunset") == "a beautiful sunset"

    # Test prompt with special characters
    assert sanitize_prompt("test<script>alert()</script>") == "testalert()"

    # Test empty prompt
    with pytest.raises(ValueError):
        sanitize_prompt("")
```

---

## Integration Testing

### Testing Full Pipelines

```python
import pytest
import os
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("FAL_KEY"), reason="API key required")
class TestIntegration:
    """Integration tests (require API keys)."""

    def test_image_generation_integration(self):
        """Test actual image generation."""
        manager = AIPipelineManager()

        result = manager.generate_image(
            prompt="simple test image",
            model="flux_schnell"  # Cheapest model
        )

        assert result.success is True
        assert os.path.exists(result.output_path)
        assert result.cost > 0

    def test_pipeline_execution_integration(self):
        """Test pipeline execution."""
        manager = AIPipelineManager()

        config = {
            "name": "Integration Test",
            "steps": [
                {
                    "name": "image",
                    "type": "text_to_image",
                    "model": "flux_schnell",
                    "params": {"prompt": "test image"}
                }
            ]
        }

        results = manager.run_pipeline(config)
        assert len(results) == 1
        assert results[0].success is True
```

### Testing API Connections

```python
import pytest
import os

@pytest.mark.integration
class TestAPIConnections:
    """Test API connectivity."""

    @pytest.mark.skipif(not os.getenv("FAL_KEY"), reason="FAL_KEY required")
    def test_fal_connection(self):
        """Test FAL AI connection."""
        from packages.providers.fal.client import FALClient

        client = FALClient()
        # Just test authentication, not generation
        assert client.is_authenticated() is True

    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY required")
    def test_gemini_connection(self):
        """Test Gemini connection."""
        from packages.providers.google.client import GeminiClient

        client = GeminiClient()
        assert client.is_authenticated() is True
```

---

## Test Fixtures

### Pytest Fixtures

```python
# conftest.py
import pytest
import tempfile
import os

@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_config():
    """Provide sample pipeline configuration."""
    return {
        "name": "Test Pipeline",
        "steps": [
            {
                "name": "generate",
                "type": "text_to_image",
                "model": "flux_schnell",
                "params": {"prompt": "test"}
            }
        ]
    }

@pytest.fixture
def mock_manager():
    """Provide mocked pipeline manager."""
    from unittest.mock import Mock
    manager = Mock()
    manager.generate_image.return_value = Mock(
        success=True,
        output_path="/tmp/test.png",
        cost=0.001
    )
    return manager

@pytest.fixture
def sample_image(temp_output_dir):
    """Create sample image file for testing."""
    import PIL.Image
    img = PIL.Image.new('RGB', (100, 100), color='red')
    path = os.path.join(temp_output_dir, 'test.png')
    img.save(path)
    return path
```

---

## Running Tests

### Quick Tests

```bash
# Run quick tests (no API calls)
python tests/run_all_tests.py --quick

# Run with pytest
pytest tests/ -m "not integration"
```

### Full Tests

```bash
# Run all tests including integration
python tests/run_all_tests.py

# Run with coverage
pytest tests/ --cov=packages --cov-report=html
```

### Specific Tests

```bash
# Run single test file
pytest tests/test_manager.py

# Run single test
pytest tests/test_manager.py::TestAIPipelineManager::test_generate_image

# Run with verbose output
pytest tests/ -v
```

---

## Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── run_all_tests.py      # Test runner script
├── test_core.py          # Quick smoke tests
├── test_integration.py   # Integration tests
├── unit/
│   ├── test_config.py    # Configuration tests
│   ├── test_manager.py   # Manager tests
│   └── test_providers.py # Provider tests
├── integration/
│   ├── test_fal.py       # FAL integration
│   └── test_pipelines.py # Pipeline integration
└── fixtures/
    ├── configs/          # Test configurations
    └── images/           # Test images
```

---

## CI/CD Testing

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov

      - name: Run quick tests
        run: pytest tests/ -m "not integration" -v

      - name: Run integration tests
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        env:
          FAL_KEY: ${{ secrets.FAL_KEY }}
        run: pytest tests/ -m integration -v
```

---

## Testing Checklist

### Before Committing

- [ ] All unit tests pass
- [ ] New code has tests
- [ ] Mock mode works for new features
- [ ] No hardcoded API keys

### Before Release

- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] Example configs tested
- [ ] Cost estimates accurate

---

## Debugging Tests

### Verbose Output

```bash
pytest tests/ -v --tb=long
```

### Print Statements

```python
def test_something():
    result = some_function()
    print(f"Debug: result = {result}")  # Shows with pytest -s
    assert result is not None
```

### Debugging with pdb

```python
def test_with_debugger():
    import pdb; pdb.set_trace()
    result = some_function()
    assert result is not None
```
