# AI Content Pipeline - Detailed Reference

## Complete Model Reference

### Text-to-Image Models

#### FLUX.1 Dev (`flux_dev`)
- **Provider**: FAL AI
- **Parameters**: 12B
- **Best for**: High-quality, detailed images
- **Cost**: ~$0.003 per image
- **Options**: width, height, num_inference_steps, guidance_scale

#### FLUX.1 Schnell (`flux_schnell`)
- **Provider**: FAL AI
- **Best for**: Fast prototyping, batch generation
- **Cost**: ~$0.001 per image
- **Speed**: 4x faster than Dev

#### Imagen 4 (`imagen_4`)
- **Provider**: Google Cloud
- **Best for**: Photorealistic images
- **Requires**: GCP authentication

#### Seedream v3 (`seedream_v3`)
- **Provider**: FAL AI
- **Best for**: Multilingual prompts, artistic styles

#### Nano Banana Pro (`nano_banana_pro`)
- **Provider**: FAL AI
- **Best for**: Fast, high-quality generation
- **Cost**: ~$0.002 per image
- **Speed**: Optimized for quick inference

#### GPT Image 1.5 (`gpt_image_1_5`)
- **Provider**: FAL AI
- **Best for**: Natural language understanding, creative prompts
- **Cost**: ~$0.003 per image

### Image-to-Video Models

#### Veo 3 (`veo_3`)
- **Provider**: Google Cloud
- **Best for**: Highest quality video generation
- **Cost**: ~$0.50-6.00 per video
- **Duration**: Up to 8 seconds
- **Resolution**: Up to 1080p
- **Requires**: GCP Project with Veo API enabled

#### Veo 2 (`veo_2`)
- **Provider**: Google Cloud
- **Best for**: Budget-conscious high-quality video
- **Cost**: ~$0.30-2.00 per video

#### Hailuo (`hailuo`)
- **Provider**: FAL AI (MiniMax)
- **Best for**: Consistent motion, character animation
- **Cost**: ~$0.08-0.15 per video

#### Kling (`kling`)
- **Provider**: FAL AI
- **Best for**: Creative video effects
- **Cost**: ~$0.10-0.20 per video

### Image-to-Image Models

#### Photon Flash (`photon_flash`)
- **Best for**: Quick creative modifications
- **Strength**: 0.0-1.0 (higher = more change)

#### Photon Base (`photon_base`)
- **Best for**: Standard image transformations

#### Clarity Upscaler (`clarity_upscaler`)
- **Best for**: 2x-4x resolution enhancement
- **Preserves**: Original image details

#### Nano Banana Pro Edit (`nano_banana_pro_edit`)
- **Provider**: FAL AI
- **Best for**: Fast image editing
- **Cost**: ~$0.015 per image
- **Strength**: 0.0-1.0

#### GPT Image 1.5 Edit (`gpt_image_1_5_edit`)
- **Provider**: FAL AI
- **Best for**: GPT-powered image editing, natural language
- **Cost**: ~$0.02 per image

### Image Understanding Models

#### Gemini Flash (`gemini_flash`)
- **Tasks**: Description, classification, OCR
- **Speed**: Fastest response time

#### Gemini Pro (`gemini_pro`)
- **Tasks**: Complex analysis, detailed Q&A
- **Quality**: Highest accuracy

### Prompt Generation Models

#### Claude via OpenRouter (`claude_openrouter`)
- **Best for**: Video prompt optimization
- **Output**: Detailed, cinematic prompts

## Pipeline Configuration Options

### Step Types
- `text-to-image`: Generate image from text
- `image-to-image`: Transform existing image
- `image-to-video`: Create video from image
- `text-to-video`: Full text-to-video pipeline
- `image-understanding`: Analyze/describe image
- `prompt-generation`: Optimize prompts
- `text-to-speech`: Generate audio
- `video-upscale`: Enhance video quality

### Common Parameters

#### Image Generation
```yaml
params:
  prompt: "Your prompt here"
  negative_prompt: "What to avoid"
  width: 1920
  height: 1080
  num_inference_steps: 30
  guidance_scale: 7.5
  seed: 12345  # For reproducibility
```

#### Video Generation
```yaml
params:
  image: "{{step_N.output}}"  # or file path
  prompt: "Motion description"
  duration: 5  # seconds
  fps: 24
  aspect_ratio: "16:9"
```

### Parallel Execution

Enable for independent steps:
```bash
PIPELINE_PARALLEL_ENABLED=true aicp run-chain --config config.yaml
```

Benefits:
- 2-3x speedup for multi-step pipelines
- Automatic dependency resolution
- Thread-based execution

## Troubleshooting

### Common Issues

**"API key not found"**
- Check `.env` file exists in project root
- Verify variable names match expected format
- Restart terminal after adding keys

**"Model not available"**
- Verify model name spelling
- Check provider API status
- Confirm account has access

**"Output directory not found"**
- Pipeline creates `output/` automatically
- Check write permissions

**"GCP authentication failed"**
- Run `gcloud auth login`
- Run `gcloud auth application-default login`
- Verify PROJECT_ID in .env

### Debug Mode

Run with verbose output:
```bash
LOG_LEVEL=DEBUG aicp run-chain --config config.yaml
```

## Output Organization

Generated files are saved to:
```
output/
├── YYYY-MM-DD_HHMMSS/
│   ├── step_1_image.png
│   ├── step_2_video.mp4
│   └── pipeline_results.json
```

Results JSON contains:
- Step execution times
- Model parameters used
- Output file paths
- Cost breakdown
