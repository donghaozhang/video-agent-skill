# Video Generation Tips

Best practices for creating high-quality AI-generated videos.

## Understanding Video Generation

### Two Approaches

**1. Text-to-Video**
- Generate video directly from text
- Models: `hailuo_pro`, `sora_2`, `kling_2_6_pro`
- Best for: Quick videos, simple scenes

**2. Image-to-Video**
- Generate image first, then animate
- More control over visual appearance
- Best for: Precise visuals, brand consistency

### When to Use Each

| Scenario | Approach | Why |
|----------|----------|-----|
| Quick social content | Text-to-video | Faster |
| Precise visuals | Image-to-video | More control |
| Brand content | Image-to-video | Consistent look |
| Experimental | Text-to-video | Explore ideas |
| Product showcase | Image-to-video | Control details |

---

## Image-to-Video Best Practices

### Choose the Right Source Image

**Good source images have:**
- Clear subject
- Space for motion
- Good composition
- High resolution

**Avoid:**
- Cluttered scenes
- Extreme close-ups (no room for motion)
- Low resolution images
- Heavy text overlays

### Aspect Ratio Matching

```yaml
# Match video aspect ratio to image
- name: "image"
  type: "text_to_image"
  params:
    aspect_ratio: "16:9"  # Landscape for video

- name: "video"
  type: "image_to_video"
  input_from: "image"
  params:
    # Video will match source image ratio
```

### Motion Prompts

Describe motion clearly:

```yaml
# Good motion prompts
params:
  prompt: "slow camera pan from left to right"
  prompt: "gentle zoom in on subject"
  prompt: "subtle movement, wind blowing hair"
  prompt: "water ripples, leaves rustling"

# Avoid vague prompts
params:
  prompt: "make it move"  # Too vague
```

---

## Model Selection Guide

### Budget Videos

**Model:** `hailuo_pro` (text-to-video) or `hailuo` (image-to-video)

```bash
ai-content-pipeline text-to-video --text "ocean waves" --model hailuo_pro
# Cost: $0.08
```

Best for:
- Testing concepts
- Social media drafts
- High volume, lower quality needs

### Quality Videos

**Model:** `kling_2_6_pro`

```bash
ai-content-pipeline image-to-video --image scene.png --model kling_2_6_pro
# Cost: $0.50-1.00
```

Best for:
- Marketing content
- Product videos
- Professional use

### Premium Videos

**Model:** `sora_2_pro`

```bash
ai-content-pipeline text-to-video --text "cinematic scene" --model sora_2_pro
# Cost: $1.20-6.00
```

Best for:
- Cinematic content
- High-end marketing
- Flagship projects

### With Audio

**Model:** `veo_3_1_fast`

```bash
ai-content-pipeline image-to-video --image scene.png --model veo_3_1_fast
# Includes generated audio
```

---

## Duration Guidelines

### Short Videos (3-5 seconds)

- Social media clips
- Product reveals
- Transition effects
- Looping content

```yaml
params:
  duration: 5
  prompt: "quick dynamic movement"
```

### Medium Videos (6-10 seconds)

- Marketing spots
- Story scenes
- Product demos
- Social ads

```yaml
params:
  duration: 8
  prompt: "smooth camera movement with action"
```

### Longer Videos (10+ seconds)

- Narrative content
- Detailed showcases
- Cinematic pieces

```yaml
params:
  duration: 12
  prompt: "slow cinematic pan with gradual reveal"
```

### Cost by Duration

| Duration | Budget Model | Quality Model |
|----------|--------------|---------------|
| 5 seconds | $0.08 | $0.50 |
| 8 seconds | $0.08 | $0.75 |
| 10 seconds | $0.12 | $1.00 |
| 15 seconds | $0.20 | $1.50 |

---

## Motion Types

### Camera Movements

| Movement | Prompt Keywords | Effect |
|----------|-----------------|--------|
| Pan | "pan left/right" | Horizontal sweep |
| Tilt | "tilt up/down" | Vertical sweep |
| Zoom | "zoom in/out" | Closer/further |
| Dolly | "dolly forward/back" | Move through scene |
| Tracking | "tracking shot" | Follow subject |
| Static | "static camera" | No camera movement |

### Subject Movements

```yaml
# Natural movements
"gentle breeze, hair flowing"
"subtle breathing movement"
"eyes blinking naturally"

# Dynamic movements
"walking confidently"
"running through scene"
"dancing gracefully"

# Environmental
"clouds drifting slowly"
"water flowing"
"leaves falling"
```

---

## Scene Types

### Static Scenes

Best for subtle animation:
- Portraits with eye movement
- Landscapes with weather
- Products with lighting shifts

```yaml
prompt: "subtle atmospheric movement, soft lighting changes, minimal motion"
```

### Dynamic Scenes

For action-oriented content:
- Sports moments
- Action sequences
- Energetic content

```yaml
prompt: "dynamic motion, fast movement, energetic pace"
```

### Cinematic Scenes

For professional, movie-like content:

```yaml
prompt: "cinematic camera movement, film grain, dramatic lighting, professional"
```

---

## Common Issues & Solutions

### Issue: Artifacts or Distortion

**Cause:** Complex scene or incompatible source image

**Solutions:**
- Simplify the source image
- Reduce motion intensity
- Use higher quality model
- Try different prompt

### Issue: Unrealistic Motion

**Cause:** Prompt too vague or unrealistic

**Solutions:**
```yaml
# Instead of
prompt: "person flying"

# Try
prompt: "person walking forward naturally, subtle movement"
```

### Issue: Inconsistent Animation

**Cause:** Source image has conflicting elements

**Solutions:**
- Use cleaner source image
- Specify motion direction clearly
- Reduce duration

### Issue: Low-Quality Output

**Cause:** Model or resolution mismatch

**Solutions:**
- Use higher-quality model
- Match source image resolution
- Specify quality in prompt

---

## Workflow Templates

### Product Video Workflow

```yaml
name: "Product Video"
steps:
  # High-quality product image
  - name: "product_image"
    type: "text_to_image"
    model: "imagen4"
    params:
      prompt: "{{input}}, product photography, white background, studio lighting"
      aspect_ratio: "16:9"

  # Subtle animation
  - name: "product_video"
    type: "image_to_video"
    model: "kling_2_6_pro"
    input_from: "product_image"
    params:
      duration: 5
      prompt: "slow 360 rotation, professional lighting, smooth motion"
```

### Social Media Workflow

```yaml
name: "Social Content"
steps:
  # Quick image generation
  - name: "scene"
    type: "text_to_image"
    model: "flux_schnell"
    params:
      prompt: "{{input}}, vibrant, eye-catching"
      aspect_ratio: "9:16"  # Portrait for Stories/Reels

  # Budget video
  - name: "video"
    type: "image_to_video"
    model: "hailuo"
    input_from: "scene"
    params:
      duration: 6
      prompt: "dynamic motion, energetic"
```

### Cinematic Workflow

```yaml
name: "Cinematic Content"
steps:
  # Premium image
  - name: "scene"
    type: "text_to_image"
    model: "flux_dev"
    params:
      prompt: "{{input}}, cinematic composition, dramatic lighting, film look"
      aspect_ratio: "2.39:1"  # Cinemascope

  # Premium video
  - name: "video"
    type: "image_to_video"
    model: "sora_2_pro"
    input_from: "scene"
    params:
      duration: 10
      prompt: "slow cinematic camera movement, film grain, atmospheric"
```

---

## Quality Checklist

### Before Generation

- [ ] Source image is high quality
- [ ] Aspect ratio matches intended use
- [ ] Motion prompt is specific
- [ ] Model matches quality needs
- [ ] Duration is appropriate

### After Generation

- [ ] No visible artifacts
- [ ] Motion looks natural
- [ ] Consistent throughout
- [ ] Quality meets requirements
- [ ] File format is correct

---

## Tips Summary

1. **Start with good images** - Quality in = quality out
2. **Be specific about motion** - "slow pan left" not "move"
3. **Match model to needs** - Budget for tests, premium for finals
4. **Keep durations reasonable** - Longer isn't always better
5. **Test before scaling** - Validate with cheap models first
6. **Use appropriate aspect ratios** - Match your platform
