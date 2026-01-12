---
name: AI Content Pipeline
description: Generate AI content (images, videos, audio) using YAML pipelines with 32+ models. Run tests, estimate costs, and manage outputs.
dependencies: python>=3.10
---

# AI Content Pipeline Skill

Generate AI content (images, videos, audio) using this unified Python package.

## IMPORTANT: First-Time Setup Check

**Before running ANY pipeline commands, you MUST check if the environment is set up:**

```bash
# Check if venv exists (Windows)
if exist venv\Scripts\python.exe (echo "venv exists") else (echo "venv NOT found - run setup")

# Check if venv exists (Linux/Mac)
test -f venv/bin/python && echo "venv exists" || echo "venv NOT found - run setup"
```

**If venv does NOT exist, run this setup first:**

```bash
# Windows Setup (cmd)
python -m venv venv
venv\Scripts\activate
pip install -e .

# Windows Setup (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
pip install -e .

# Linux/Mac Setup
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Running Commands

**All commands must use the venv Python directly:**

```bash
# Windows - Use venv\Scripts\python directly
venv\Scripts\python -m packages.core.ai_content_pipeline.ai_content_pipeline --help

# Or after pip install -e . you can use:
venv\Scripts\ai-content-pipeline --help
venv\Scripts\aicp --help

# Linux/Mac
./venv/bin/python -m packages.core.ai_content_pipeline.ai_content_pipeline --help
./venv/bin/ai-content-pipeline --help
```

## Quick Commands (after setup)

### Generate Image
```bash
# Windows
venv\Scripts\ai-content-pipeline generate-image --text "your prompt" --model flux_dev

# Linux/Mac
./venv/bin/ai-content-pipeline generate-image --text "your prompt" --model flux_dev
```

### Run Pipeline
```bash
# Windows
venv\Scripts\ai-content-pipeline run-chain --config input/pipelines/config.yaml

# Linux/Mac
./venv/bin/ai-content-pipeline run-chain --config input/pipelines/config.yaml
```

### List Models
```bash
# Windows
venv\Scripts\ai-content-pipeline list-models

# Linux/Mac
./venv/bin/ai-content-pipeline list-models
```

## Available AI Models (32 Total)

### Text-to-Image (6 models)
| Model | Key | Description |
|-------|-----|-------------|
| FLUX.1 Dev | `flux_dev` | Highest quality, 12B parameters |
| FLUX.1 Schnell | `flux_schnell` | Fastest inference |
| Imagen 4 | `imagen_4` | Google's photorealistic model |
| Seedream v3 | `seedream_v3` | Multilingual support |
| Nano Banana Pro | `nano_banana_pro` | Fast, high-quality generation |
| GPT Image 1.5 | `gpt_image_1_5` | GPT-powered image generation |

### Image-to-Video (4 models)
| Model | Key | Description |
|-------|-----|-------------|
| Veo 3 | `veo_3` | Google's latest video model |
| Veo 2 | `veo_2` | Previous generation Veo |
| Hailuo | `hailuo` | MiniMax video generation |
| Kling | `kling` | High-quality video synthesis |

### Image-to-Image (8 models)
- Photon Flash, Photon Base, FLUX variants, Clarity Upscaler
- Nano Banana Pro Edit, GPT Image 1.5 Edit

### Image Understanding (7 models)
- Gemini variants for description, classification, OCR, Q&A

### Prompt Generation (5 models)
- OpenRouter models for video prompt optimization

## YAML Pipeline Configuration

Create a pipeline config file in `input/pipelines/`:

```yaml
name: "My Content Pipeline"
description: "Generate image and convert to video"

steps:
  - name: "generate_image"
    type: "text-to-image"
    model: "flux_dev"
    params:
      prompt: "A majestic mountain landscape at sunset"
      width: 1920
      height: 1080

  - name: "create_video"
    type: "image-to-video"
    model: "veo_3"
    params:
      image: "{{step_1.output}}"
      prompt: "Camera slowly pans across the landscape"
      duration: 5
```

## Environment Variables

Required in `.env` file:
```
FAL_KEY=your_fal_api_key
PROJECT_ID=your-gcp-project-id
OUTPUT_BUCKET_PATH=gs://your-bucket/output/
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENROUTER_API_KEY=your_openrouter_key
GEMINI_API_KEY=your_gemini_key
```

## Cost Estimation

- **Text-to-Image**: $0.001-0.004 per image
- **Image-to-Image**: $0.01-0.05 per modification
- **Image-to-Video**: $0.08-6.00 per video (model dependent)

## Testing

```bash
# Windows
venv\Scripts\python tests/test_core.py
venv\Scripts\python tests/run_all_tests.py --quick

# Linux/Mac
./venv/bin/python tests/test_core.py
./venv/bin/python tests/run_all_tests.py --quick
```
