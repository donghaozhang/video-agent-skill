# Quick Start Guide

Get started with AI Content Generation Suite in under 5 minutes.

## Prerequisites

- Python 3.10 or higher
- pip package manager
- At least one API key (FAL AI recommended)

## Step 1: Install the Package

```bash
pip install video-ai-studio
```

Or install from source:
```bash
git clone https://github.com/donghaozhang/video-agent-skill.git
cd video-agent-skill
pip install -e .
```

## Step 2: Configure API Keys

Create a `.env` file in your working directory:

```env
# Required for most functionality
FAL_KEY=your_fal_api_key_here
```

Get your FAL API key at: https://fal.ai/dashboard

## Step 3: Verify Installation

```bash
# Check if the CLI is working
ai-content-pipeline --help

# List all available models
ai-content-pipeline list-models
```

## Step 4: Generate Your First Image

```bash
ai-content-pipeline generate-image \
  --text "a majestic dragon flying over mountains at sunset" \
  --model flux_dev
```

Output will be saved to the `output/` directory.

## Step 5: Create Your First Video

```bash
ai-content-pipeline create-video \
  --text "serene mountain lake with morning mist"
```

This command:
1. Generates an image from your text
2. Converts the image to video
3. Saves the result to `output/`

## Common Commands

### Generate Images
```bash
# Basic image generation
ai-content-pipeline generate-image --text "your prompt" --model flux_dev

# Fast generation (cheaper)
ai-content-pipeline generate-image --text "your prompt" --model flux_schnell

# High quality
ai-content-pipeline generate-image --text "your prompt" --model imagen4
```

### Create Videos
```bash
# Quick video creation
ai-content-pipeline create-video --text "your description"

# From existing image
ai-content-pipeline image-to-video --image path/to/image.png --model kling_2_6_pro
```

### Run Custom Pipelines
```bash
# Create example configuration files
ai-content-pipeline create-examples

# Run a pipeline from YAML
ai-content-pipeline run-chain --config config.yaml --input "your prompt"
```

## Shorthand Command

Use `aicp` as a shortcut for `ai-content-pipeline`:

```bash
aicp list-models
aicp generate-image --text "epic space battle"
aicp create-video --text "calm ocean waves"
```

## Cost-Saving Tips

1. **Use `--mock` flag for testing** (FREE):
   ```bash
   ai-content-pipeline generate-image --text "test" --mock
   ```

2. **Start with cheaper models**:
   - `flux_schnell` - $0.001/image
   - `hailuo` - $0.30-0.50/video

3. **Estimate costs before running**:
   ```bash
   ai-content-pipeline estimate-cost --config config.yaml
   ```

## Next Steps

- [Installation Guide](installation.md) - Detailed setup instructions
- [Models Reference](../reference/models.md) - All available models
- [YAML Pipelines](yaml-pipelines.md) - Create custom workflows
- [Examples](../examples/basic-examples.md) - More usage examples

## Troubleshooting

### "Command not found"
Make sure the package is installed and your Python bin directory is in PATH:
```bash
pip install video-ai-studio
python -m ai_content_pipeline --help
```

### "API key not found"
Ensure your `.env` file is in the current working directory and contains valid keys.

### "Model not available"
Check available models with:
```bash
ai-content-pipeline list-models
```

---

[Back to Documentation Index](../index.md)
