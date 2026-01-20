# Migration Guide

Instructions for upgrading between versions of AI Content Generation Suite.

## Checking Your Version

```bash
ai-content-pipeline --version
```

Or in Python:
```python
import packages.core.ai_content_pipeline as pipeline
print(pipeline.__version__)
```

## Upgrade Process

### Standard Upgrade

```bash
pip install --upgrade video-ai-studio
```

### From Source

```bash
cd video-agent-skill
git pull origin main
pip install -e .
```

---

## Version-Specific Migration

### Upgrading to 1.0.18

**From 1.0.17:**

No breaking changes. Simply upgrade:
```bash
pip install --upgrade video-ai-studio
```

**New features:**
- Automated PyPI publishing
- Comprehensive documentation

---

### Upgrading to 1.0.15+

**From 1.0.14 or earlier:**

**New Video Analysis:**

The video analysis feature was added. New commands available:

```bash
# New command
ai-content-pipeline analyze-video -i video.mp4

# New models
ai-content-pipeline list-video-models
```

**No breaking changes** - existing code continues to work.

---

### Upgrading to 1.0.12+

**From 1.0.11 or earlier:**

**Parallel Execution:**

Parallel execution was added. To enable:

```bash
# New environment variable
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml
```

Or in YAML:
```yaml
settings:
  parallel: true
```

**New step type:**
```yaml
steps:
  - type: "parallel_group"  # New
    steps:
      - type: "text_to_image"
        params: { prompt: "cat" }
      - type: "text_to_image"
        params: { prompt: "dog" }
```

**No breaking changes** - parallel is opt-in.

---

### Upgrading to 1.0.11+

**From 1.0.10 or earlier:**

**Cost Management:**

New cost estimation feature:

```bash
# New command
ai-content-pipeline estimate-cost --config config.yaml
```

Python API:
```python
# New method
estimate = manager.estimate_cost("pipeline.yaml")
print(f"Total: ${estimate.total:.2f}")
```

**New configuration option:**
```yaml
settings:
  cost_management:
    max_cost_per_run: 10.00
```

**No breaking changes** - cost management is opt-in.

---

### Upgrading to 1.0.10+

**From 1.0.9 or earlier:**

**YAML Configuration Changes:**

The YAML format was standardized. If you have existing configs:

**Old format (deprecated but still works):**
```yaml
steps:
  - model: flux_dev
    prompt: "test"
```

**New format (recommended):**
```yaml
steps:
  - name: "generate"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "test"
```

**Migration steps:**
1. Add `name` to each step
2. Add `type` field
3. Move parameters into `params` block

---

### Upgrading to 1.0.6+

**From 1.0.5 or earlier:**

**Model Naming Changes:**

Some model names were standardized:

| Old Name | New Name |
|----------|----------|
| `flux-dev` | `flux_dev` |
| `flux-schnell` | `flux_schnell` |
| `imagen-4` | `imagen4` |

**Update your code:**
```python
# Old
manager.generate_image(model="flux-dev")

# New
manager.generate_image(model="flux_dev")
```

**Update YAML configs:**
```yaml
# Old
model: flux-dev

# New
model: flux_dev
```

---

### Upgrading to 1.0.5+

**From 1.0.4 or earlier:**

**CLI Changes:**

The CLI was introduced. New commands available:

```bash
# New commands
ai-content-pipeline --help
ai-content-pipeline list-models
ai-content-pipeline generate-image --text "test"
```

**Python API unchanged** - no migration needed for Python code.

---

## Common Migration Issues

### "Model not found" after upgrade

Model names may have changed. List available models:
```bash
ai-content-pipeline list-models
```

### "Invalid configuration" after upgrade

YAML format may have changed. Validate your config:
```bash
ai-content-pipeline run-chain --config config.yaml --dry-run
```

### Import errors

Package structure may have changed:
```python
# Old imports may not work
# from old.path import Something

# Check new import paths in documentation
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager
```

### API key issues

Environment variable names should remain consistent:
```env
FAL_KEY=your_key
GEMINI_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
```

---

## Rollback Instructions

If an upgrade causes issues:

### Using pip

```bash
# Install specific version
pip install video-ai-studio==1.0.17
```

### Using git

```bash
cd video-agent-skill
git checkout v1.0.17
pip install -e .
```

---

## Deprecation Notices

### Deprecated in 1.0.10

- Direct parameter passing in steps (use `params` block instead)
- Will be removed in 2.0.0

### Deprecated in 1.0.6

- Hyphenated model names (`flux-dev`)
- Use underscored names (`flux_dev`)
- Old names still work but will be removed in 2.0.0

---

## Future Breaking Changes

### Planned for 2.0.0

- Remove deprecated parameter formats
- Remove old model name aliases
- New default output directory structure
- Updated Python minimum version (3.11+)

**Estimated release:** Q2 2026

---

## Getting Help

If you encounter migration issues:

1. Check the [Troubleshooting Guide](../support/troubleshooting.md)
2. Search [GitHub Issues](https://github.com/donghaozhang/video-agent-skill/issues)
3. Open a new issue with:
   - Previous version
   - New version
   - Error message
   - Steps to reproduce

---

[Back to Documentation Index](../../index.md) | [Changelog](../../CHANGELOG.md)
