# Frequently Asked Questions (FAQ)

Common questions and answers about AI Content Generation Suite.

> **Having errors or issues?** See the **[Troubleshooting Guide](troubleshooting.md)** for error solutions and diagnostics.

## General Questions

### What is AI Content Generation Suite?

AI Content Generation Suite is a unified Python package that provides access to 40+ AI models for generating images, videos, and audio. It supports:
- Text-to-image generation
- Image-to-video conversion
- Text-to-video generation
- Image analysis
- Text-to-speech
- Video processing

### Which AI providers are supported?

- **FAL AI** - Primary provider for image and video generation
- **Google** - Gemini for image analysis, Veo for video
- **ElevenLabs** - Text-to-speech
- **OpenRouter** - Alternative models
- **Replicate** - Additional models

### What are the system requirements?

- Python 3.10 or higher
- 4GB RAM minimum (8GB+ recommended)
- Internet connection for API calls
- API keys from supported providers

### Is it free to use?

The package itself is free and open-source. However, using the AI models requires API credits from the respective providers. See the [Cost Management Guide](cost-management.md) for pricing details.

---

## Installation & Setup

### How do I install the package?

```bash
pip install video-ai-studio
```

Or from source:
```bash
git clone https://github.com/donghaozhang/video-agent-skill.git
cd video-agent-skill
pip install -e .
```

### Where do I get API keys?

- **FAL AI**: [fal.ai/dashboard](https://fal.ai/dashboard)
- **Google Gemini**: [makersuite.google.com](https://makersuite.google.com)
- **ElevenLabs**: [elevenlabs.io/app/settings](https://elevenlabs.io/app/settings)
- **OpenRouter**: [openrouter.ai/keys](https://openrouter.ai/keys)

### How do I configure API keys?

Create a `.env` file in your project root:

```env
FAL_KEY=your_fal_api_key
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### Why isn't my API key working?

1. Check the key is correctly copied (no extra spaces)
2. Verify the key hasn't expired
3. Ensure the `.env` file is in your current directory
4. Check your account has sufficient credits

---

## Usage Questions

### How do I generate an image?

**CLI:**
```bash
ai-content-pipeline generate-image --text "a sunset over mountains" --model flux_dev
```

**Python:**
```python
from packages.core.ai_content_pipeline.pipeline.manager import AIPipelineManager

manager = AIPipelineManager()
result = manager.generate_image(prompt="a sunset over mountains")
print(result.output_path)
```

### How do I create a video from text?

```bash
ai-content-pipeline create-video --text "ocean waves on a beach"
```

This generates an image first, then converts it to video.

### How do I convert an existing image to video?

```bash
ai-content-pipeline image-to-video --image photo.png --model kling_2_6_pro
```

### How do I run a custom pipeline?

1. Create a YAML configuration file
2. Run with the CLI:
```bash
ai-content-pipeline run-chain --config pipeline.yaml --input "your prompt"
```

### How do I test without using API credits?

Use mock mode:
```bash
ai-content-pipeline generate-image --text "test" --mock
```

Or dry run for pipelines:
```bash
ai-content-pipeline run-chain --config pipeline.yaml --dry-run
```

---

## Model Questions

### Which model should I use for images?

| Model | Best For | Cost |
|-------|----------|------|
| `flux_schnell` | Testing, prototyping | $0.001 |
| `flux_dev` | General high quality | $0.003 |
| `imagen4` | Photorealistic | $0.004 |
| `nano_banana_pro` | Fast + quality balance | $0.002 |

### Which model should I use for videos?

| Model | Best For | Cost |
|-------|----------|------|
| `hailuo_pro` | Budget, quick tests | $0.08 |
| `hailuo` | Budget image-to-video | $0.30 |
| `kling_2_6_pro` | Quality production | $0.50+ |
| `sora_2_pro` | Premium quality | $1.20+ |

### What's the difference between text-to-video and image-to-video?

- **Text-to-video**: Generates video directly from text description
- **Image-to-video**: Converts an existing image into an animated video

Image-to-video typically gives you more control over the visual appearance.

### Can I use my own reference images?

Yes, several models support reference images:
- Use `image_to_image` for transformations
- Use `image_to_video` for animation
- The `gen4` model supports multi-reference guidance

---

## Pipeline Questions

### What is a pipeline?

A pipeline is a series of AI operations defined in a YAML file. It allows you to chain multiple steps together, like generating an image and then converting it to video.

### How do I create a pipeline?

Create a YAML file:
```yaml
name: "My Pipeline"
steps:
  - name: "image"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}"

  - name: "video"
    type: "image_to_video"
    input_from: "image"
```

### How do I pass data between steps?

Use `input_from` to reference a previous step's output:
```yaml
- name: "video"
  type: "image_to_video"
  input_from: "image"  # Uses output from "image" step
```

### How do I run steps in parallel?

Use a `parallel_group`:
```yaml
- type: "parallel_group"
  steps:
    - type: "text_to_image"
      params: { prompt: "cat" }
    - type: "text_to_image"
      params: { prompt: "dog" }
```

And enable parallel execution:
```bash
PIPELINE_PARALLEL_ENABLED=true ai-content-pipeline run-chain --config pipeline.yaml
```

---

## Cost Questions

### How much does it cost?

Costs vary by model:
- **Text-to-Image**: $0.001 - $0.08 per image
- **Image-to-Video**: $0.25 - $3.60 per video
- **Text-to-Video**: $0.08 - $6.00 per video

See the [Cost Management Guide](cost-management.md) for detailed pricing.

### How do I estimate costs before running?

```bash
ai-content-pipeline estimate-cost --config pipeline.yaml
```

### How do I set a cost limit?

In YAML:
```yaml
settings:
  cost_management:
    max_cost_per_run: 10.00
```

### Which is the cheapest model for testing?

- **Images**: `flux_schnell` at $0.001/image
- **Videos**: `hailuo_pro` at $0.08/video

---

## Troubleshooting

### "Command not found: ai-content-pipeline"

The package isn't installed or not in PATH:
```bash
pip install video-ai-studio
```

### "API key not found"

Ensure your `.env` file exists and contains the correct key format:
```env
FAL_KEY=your_key_here
```

### "Model not found"

Check available models:
```bash
ai-content-pipeline list-models
```

### "Rate limit exceeded"

- Wait and retry
- Reduce parallel workers
- Contact provider for higher limits

### "Generation timeout"

- Use a faster model
- Check network connectivity
- Retry the operation

### My output file is corrupted

- Check disk space
- Verify API response was complete
- Retry the generation

---

## Performance Questions

### How do I speed up generation?

1. Enable parallel processing
2. Use faster models (e.g., `flux_schnell`)
3. Batch similar operations

### How many parallel operations can I run?

Typically 4-8 workers work well. More can hit API rate limits.

### Does parallel processing save money?

No, parallel processing saves time but not money. You pay per operation regardless of how they're executed.

---

## Output Questions

### Where are generated files saved?

By default, files are saved to the `output/` directory in your current working directory.

### Can I customize the output path?

Yes:
```bash
ai-content-pipeline generate-image --text "test" --output custom/path/image.png
```

### What formats are supported?

- **Images**: PNG, JPEG
- **Videos**: MP4
- **Audio**: MP3, WAV

---

## Security Questions

### Are my prompts stored?

Prompts are sent to the respective AI providers (FAL AI, Google, etc.). Check each provider's privacy policy for their data retention policies.

### Are my API keys secure?

API keys should be stored in `.env` files or environment variables. Never commit them to version control.

### Can I use this for commercial projects?

Yes, the package is MIT licensed. However, check each AI provider's terms of service for their usage policies.

---

## Getting Help

### Where can I get more help?

- **Documentation**: https://github.com/donghaozhang/video-agent-skill/tree/main/docs
- **Issues**: https://github.com/donghaozhang/video-agent-skill/issues
- **Discussions**: GitHub Discussions

### How do I report a bug?

Open an issue on GitHub with:
1. Python version
2. Package version
3. Steps to reproduce
4. Full error message

---

[Back to Documentation Index](../../index.md)
