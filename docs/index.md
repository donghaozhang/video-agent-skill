# AI Content Generation Suite Documentation

Welcome to the AI Content Generation Suite documentation. This comprehensive guide covers everything you need to know to generate AI content using 40+ models across 8 categories.

## Quick Navigation

### Getting Started
- [Quick Start Guide](guides/quick-start.md) - Get up and running in 5 minutes
- [Installation Guide](guides/installation.md) - Detailed installation instructions
- [Configuration Guide](guides/configuration.md) - Environment setup and API keys

### Reference
- [Models Reference](reference/models.md) - Complete list of all 40+ AI models
- [CLI Commands](reference/cli-commands.md) - Command-line interface reference
- [API Reference](api/python-api.md) - Python API documentation

### Guides
- [YAML Pipeline Configuration](guides/yaml-pipelines.md) - Create custom workflows
- [Parallel Execution](guides/parallel-execution.md) - Speed up your pipelines
- [Cost Management](guides/cost-management.md) - Estimate and track costs

### Examples
- [Basic Examples](examples/basic-examples.md) - Simple use cases
- [Advanced Pipelines](examples/advanced-pipelines.md) - Complex workflows
- [Real-World Use Cases](examples/use-cases.md) - Production examples

### Architecture
- [Architecture Overview](reference/architecture.md) - System design and structure
- [Package Structure](reference/package-structure.md) - Code organization

### Support
- [Troubleshooting](guides/troubleshooting.md) - Common issues and solutions
- [FAQ](guides/faq.md) - Frequently asked questions
- [Contributing](guides/contributing.md) - How to contribute

## Feature Highlights

### Multi-Model Support
Access 40+ AI models from leading providers:
- **FAL AI** - Text-to-image, image-to-video, video processing
- **Google** - Veo video generation, Gemini image understanding
- **ElevenLabs** - Professional text-to-speech
- **OpenRouter** - Alternative AI services

### Unified Pipeline
Create complex workflows with simple YAML configuration:
```yaml
name: "Text to Video"
steps:
  - type: "text_to_image"
    model: "flux_dev"
  - type: "image_to_video"
    model: "kling_2_6_pro"
```

### Parallel Execution
Speed up your pipelines with parallel processing:
```bash
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config config.yaml
```

### Cost Management
Built-in cost estimation before execution:
```bash
ai-content-pipeline estimate-cost --config config.yaml
```

## Quick Example

```bash
# Install the package
pip install video-ai-studio

# Generate an image
ai-content-pipeline generate-image --text "epic space battle" --model flux_dev

# Create a video
ai-content-pipeline create-video --text "serene mountain lake"
```

## Version Information

- **Current Version**: 1.0.18
- **Python**: 3.10+
- **License**: MIT

## External Resources

- [GitHub Repository](https://github.com/donghaozhang/video-agent-skill)
- [PyPI Package](https://pypi.org/project/video-ai-studio/)
- [Demo Video](https://www.youtube.com/watch?v=xzvPrlKnXqk)

---

*Last updated: January 2026*
