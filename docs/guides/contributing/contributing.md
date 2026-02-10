# Contributing Guide

How to contribute to the AI Content Generation Suite project.

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- A GitHub account
- API keys for testing (FAL AI recommended)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/video-agent-skill.git
   cd video-agent-skill
   ```

### Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### Configure Environment

Create a `.env` file for testing:
```env
FAL_KEY=your_fal_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

### 2. Make Changes

Follow the coding standards below when making changes.

### 3. Test Your Changes

```bash
# Run quick tests
python tests/run_all_tests.py --quick

# Run full test suite
python tests/run_all_tests.py

# Test with mock mode (no API costs)
ai-content-pipeline generate-image --text "test" --mock
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Test updates
- `chore:` - Maintenance

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

```python
# Use type hints
def generate_image(prompt: str, model: str = "flux_dev") -> GenerationResult:
    """Generate an image from text.

    Args:
        prompt: The text prompt for generation.
        model: Model to use for generation.

    Returns:
        GenerationResult with output path and metadata.

    Raises:
        APIError: If the API call fails.
    """
    pass
```

### Code Formatting

Use `black` for formatting:
```bash
black packages/
```

### Import Order

```python
# Standard library
import os
import json
from typing import Optional, List

# Third-party
import click
from pydantic import BaseModel

# Local
from .config import settings
from .providers import FALProvider
```

### File Length

Keep files under 500 lines. Split into modules if longer.

### Documentation

Use Google-style docstrings:
```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is invalid.

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
```

---

## Project Structure

```
video-agent-skill/
├── packages/
│   ├── core/
│   │   └── ai_content_pipeline/  # Main pipeline package
│   ├── providers/                # Provider integrations
│   │   ├── fal/
│   │   └── google/
│   └── services/                 # Shared services
├── tests/                        # Test suites
├── docs/                         # Documentation
├── input/                        # Input configurations
└── output/                       # Generated content
```

When adding new features:
- Core functionality goes in `packages/core/`
- New providers go in `packages/providers/`
- Shared services go in `packages/services/`

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_manager.py
│   └── test_providers.py
├── integration/          # Integration tests
│   └── test_pipelines.py
└── fixtures/             # Test data
```

### Writing Tests

```python
import pytest
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

class TestAIPipelineManager:
    """Tests for AIPipelineManager."""

    def test_generate_image_success(self):
        """Test successful image generation."""
        manager = AIPipelineManager()
        result = manager.generate_image(prompt="test", mock=True)
        assert result.success is True

    def test_generate_image_invalid_model(self):
        """Test with invalid model name."""
        manager = AIPipelineManager()
        with pytest.raises(ModelNotFoundError):
            manager.generate_image(prompt="test", model="invalid_model")

    def test_generate_image_empty_prompt(self):
        """Test with empty prompt."""
        manager = AIPipelineManager()
        with pytest.raises(ValueError):
            manager.generate_image(prompt="")
```

### Test Requirements

Each feature should have:
1. At least one happy path test
2. One edge case test
3. One error case test

### Running Tests

```bash
# Quick tests (no API calls)
python tests/run_all_tests.py --quick

# Full tests
python tests/run_all_tests.py

# Specific test file
pytest tests/unit/test_manager.py

# With coverage
pytest --cov=packages tests/
```

---

## Adding New Features

### Adding a New Model

1. Add model configuration in `packages/core/ai_content_pipeline/config/models.py`:
   ```python
   MODELS = {
       "new_model": {
           "provider": "fal",
           "type": "text_to_image",
           "cost": 0.003,
           "description": "New model description"
       }
   }
   ```

2. Implement provider support if needed

3. Add tests

4. Update documentation

### Adding a New Provider

1. Create provider directory in `packages/providers/`

2. Implement base provider interface:
   ```python
   from ..base import BaseProvider

   class NewProvider(BaseProvider):
       def generate(self, params: dict) -> Result:
           # Implementation
           pass

       def estimate_cost(self, params: dict) -> float:
           # Implementation
           pass
   ```

3. Register with pipeline manager

4. Add tests

5. Update documentation

### Adding a New Command

1. Create command file in `packages/core/ai_content_pipeline/cli/commands/`:
   ```python
   import click

   @click.command()
   @click.option("--param", help="Parameter description")
   def new_command(param):
       """Command description."""
       click.echo(f"Running with {param}")
   ```

2. Register in `cli/main.py`

3. Add tests

4. Update CLI documentation

---

## Documentation

### Documentation Structure

```
docs/
├── index.md              # Main navigation
├── guides/               # How-to guides
├── reference/            # API/CLI reference
├── examples/             # Example code
└── api/                  # Python API docs
```

### Writing Documentation

- Use clear, concise language
- Include code examples
- Update table of contents if needed
- Link to related pages

### Building Documentation

```bash
# Preview documentation locally
mkdocs serve

# Build static docs
mkdocs build
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Docs updated
- [ ] Code formatted with black
```

### Review Process

1. Submit PR
2. Automated tests run
3. Reviewer provides feedback
4. Address feedback
5. Merge when approved

---

## Release Process

For maintainers:

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Build package: `python -m build`
6. Publish to PyPI: `twine upload dist/*`
7. Create GitHub release
8. Merge to main

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers
- Focus on the code, not the person

---

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an Issue
- **Features**: Open an Issue first to discuss
