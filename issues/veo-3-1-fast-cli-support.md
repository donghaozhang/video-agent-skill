# Veo 3.1 Fast - CLI Support Documentation

## Overview

Veo 3.1 Fast is Google's fast image-to-video model available through FAL AI. It supports native audio generation and provides quick video synthesis from static images.

**Endpoint:** `fal-ai/veo3.1/fast/image-to-video`

## API Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_url` | string | URL of the input image to animate |
| `prompt` | string | The text prompt describing the video you want to generate |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aspect_ratio` | AspectRatioEnum | `"auto"` | The aspect ratio of the generated video |
| `duration` | DurationEnum | `"8s"` | The duration of the generated video |
| `resolution` | ResolutionEnum | `"720p"` | The resolution of the generated video |
| `generate_audio` | boolean | `true` | Whether to generate audio for the video |

## Enum Values

### AspectRatioEnum

| Value | Description |
|-------|-------------|
| `auto` | Automatically determine aspect ratio from input image |
| `16:9` | Landscape/widescreen format |
| `9:16` | Portrait/vertical format (mobile-friendly) |

### DurationEnum

| Value | Description |
|-------|-------------|
| `4s` | 4 seconds - shortest, fastest generation |
| `6s` | 6 seconds - balanced duration |
| `8s` | 8 seconds - longest duration |

### ResolutionEnum

| Value | Description |
|-------|-------------|
| `720p` | 1280x720 - HD resolution |
| `1080p` | 1920x1080 - Full HD resolution |

## Pricing

| Configuration | Cost per Second |
|--------------|-----------------|
| Without audio | ~$0.10/s |
| With audio | ~$0.15/s |

### Cost Examples

| Duration | Without Audio | With Audio |
|----------|--------------|------------|
| 4s | $0.40 | $0.60 |
| 6s | $0.60 | $0.90 |
| 8s | $0.80 | $1.20 |

## CLI Usage

### Using AI Content Pipeline

```bash
# Generate video with default settings (8s, audio enabled)
ai-content-pipeline generate-video \
  --model veo_3_1_fast \
  --image-url "https://example.com/image.jpg" \
  --prompt "Camera pans across the scene"

# Generate 6s video without audio
ai-content-pipeline generate-video \
  --model veo_3_1_fast \
  --image-url "https://example.com/image.jpg" \
  --prompt "A person walks through the landscape" \
  --duration "6s" \
  --generate-audio false

# Generate 1080p video
ai-content-pipeline generate-video \
  --model veo_3_1_fast \
  --image-url "https://example.com/image.jpg" \
  --prompt "Dynamic scene with movement" \
  --resolution "1080p"
```

### Using FAL Client Directly

```python
import fal_client

result = fal_client.subscribe(
    "fal-ai/veo3.1/fast/image-to-video",
    arguments={
        "image_url": "https://example.com/image.jpg",
        "prompt": "The scene comes to life with natural movement",
        "duration": "6s",
        "aspect_ratio": "16:9",
        "resolution": "720p",
        "generate_audio": True
    }
)

video_url = result["video"]["url"]
```

## YAML Pipeline Configuration

```yaml
name: "Image to Video with Veo 3.1 Fast"
description: "Convert an image to video with audio"

steps:
  - name: "generate_video"
    type: "image-to-video"
    model: "veo_3_1_fast"
    params:
      image_url: "{{input.image_url}}"
      prompt: "The scene slowly comes alive with subtle camera movement"
      duration: "8s"
      aspect_ratio: "auto"
      resolution: "720p"
      generate_audio: true
```

## Response Format

```json
{
  "video": {
    "url": "https://fal.media/files/...",
    "content_type": "video/mp4",
    "file_name": "output.mp4",
    "file_size": 12345678
  },
  "seed": 123456,
  "has_audio": true
}
```

## Best Practices

### Prompt Writing
- Be descriptive about motion and camera movement
- Include audio cues if `generate_audio` is enabled
- Describe the mood and atmosphere for better results

### Performance Optimization
- Use `720p` for faster generation during testing
- Use `4s` duration for quick previews
- Disable audio if not needed to reduce cost

### Quality Tips
- Use high-quality input images (at least 720p)
- Match `aspect_ratio` to your input image
- Use `1080p` for final production videos

## Limitations

- Maximum duration: 8 seconds
- Supported aspect ratios: auto, 16:9, 9:16
- Input image requirements: Valid image URL accessible by FAL servers
- Audio generation adds processing time and cost

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid duration | Duration not in [4s, 6s, 8s] | Use valid duration value |
| Invalid aspect ratio | Aspect ratio not in [auto, 16:9, 9:16] | Use valid aspect ratio |
| Image upload failed | Image URL not accessible | Upload image to FAL first |
| Timeout | Long generation time | Increase timeout or use async mode |

## Related Models

| Model | Description |
|-------|-------------|
| `veo_3` | Google Cloud Veo 3 (higher quality, longer processing) |
| `veo_2` | Google Cloud Veo 2 (budget-friendly) |
| `sora_2` | OpenAI Sora 2 (alternative high-quality option) |
| `hailuo` | MiniMax Hailuo (faster, consistent motion) |
