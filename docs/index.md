# AI Content Generation Suite Documentation

Welcome to the AI Content Generation Suite documentation. This comprehensive guide covers everything you need to know to generate AI content using 40+ models across 8 categories.

## Quick Navigation

### Getting Started
- [Setup Guide](guides/getting-started/setup.md) - Installation, configuration, and API keys
- [Learning Path](guides/getting-started/learning-path.md) - Structured learning journey (beginner to advanced)

### Pipelines
- [YAML Pipeline Configuration](guides/pipelines/yaml-pipelines.md) - Create custom workflows
- [Parallel Execution](guides/pipelines/parallel-execution.md) - Speed up your pipelines

### Content Creation
- [Prompting Guide](guides/content-creation/prompting.md) - Write effective prompts
- [Video Generation Tips](guides/content-creation/video-tips.md) - Create better videos
- [Video Analysis](guides/content-creation/video-analysis.md) - AI-powered video analysis

### Optimization
- [Cost Management](guides/optimization/cost-management.md) - Estimate and track costs
- [Performance Optimization](guides/optimization/performance.md) - Maximize speed and efficiency
- [Best Practices](guides/optimization/best-practices.md) - Recommended patterns

### Reference
- [Models Reference](reference/models.md) - Complete list of all 40+ AI models
- [CLI Commands](reference/cli-commands.md) - Command-line interface reference
- [API Reference](api/python-api.md) - Python API documentation
- [API Quick Reference](reference/api-quick-ref.md) - Condensed API reference
- [Provider Comparison](reference/provider-comparison.md) - Compare AI providers
- [Error Codes](reference/error-codes.md) - Error codes and troubleshooting

### Examples
- [Basic Examples](examples/basic-examples.md) - Simple use cases
- [Advanced Pipelines](examples/advanced-pipelines.md) - Complex workflows
- [Real-World Use Cases](examples/use-cases.md) - Production examples
- [Integration Examples](examples/integrations.md) - Flask, FastAPI, Celery, etc.

### Architecture
- [Architecture Overview](reference/architecture.md) - System design and structure
- [Package Structure](reference/package-structure.md) - Code organization

### Support
- [Troubleshooting](guides/support/troubleshooting.md) - Common issues and solutions
- [FAQ](guides/support/faq.md) - Frequently asked questions
- [Testing Guide](guides/support/testing.md) - How to test your pipelines
- [Security Best Practices](guides/support/security.md) - Keep your setup secure

### Contributing
- [Contributing Guide](guides/contributing/contributing.md) - How to contribute
- [Migration Guide](guides/contributing/migration.md) - Upgrading between versions
- [Changelog](CHANGELOG.md) - Version history and updates

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

## Documentation Map

Looking for something specific? See the complete [Documentation Sitemap](SITEMAP.md) for a full listing of all 33 documentation files organized by category and user type.

---

**Last updated:** January 2026
