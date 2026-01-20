# Prompting Guide

Master the art of writing effective prompts for AI content generation.

## Prompt Fundamentals

### The Basic Formula

```
[Subject] + [Action/State] + [Environment] + [Style] + [Quality]
```

**Example:**
```
"A golden retriever puppy, playing in autumn leaves, park setting, natural photography, sharp focus"
```

### Key Components

| Component | Purpose | Examples |
|-----------|---------|----------|
| Subject | What to generate | person, animal, object, scene |
| Action | What's happening | running, sitting, flying |
| Environment | Where it is | forest, studio, city |
| Style | Visual style | photorealistic, anime, oil painting |
| Quality | Technical specs | 4k, detailed, sharp |

---

## Image Generation Prompts

### Photorealistic Images

```
"Professional headshot of a business executive, studio lighting,
neutral gray background, sharp focus, 85mm portrait lens, 4k quality"
```

**Key elements:**
- Specific subject description
- Lighting specification
- Background details
- Technical camera terms

### Artistic Images

```
"Impressionist painting of a Parisian cafe at dusk,
soft brushstrokes, warm golden light, Monet style,
oil on canvas texture"
```

**Key elements:**
- Art movement reference
- Technique description
- Lighting mood
- Artist style reference

### Product Photography

```
"Minimalist product photo of a luxury watch,
white background, soft studio lighting,
reflection on surface, commercial photography, 8k detail"
```

**Key elements:**
- Product type
- Background specification
- Professional lighting
- Commercial purpose

### Landscape Photography

```
"Panoramic view of mountain range at golden hour,
dramatic clouds, snow-capped peaks,
foreground wildflowers, National Geographic style, HDR"
```

---

## Video Generation Prompts

### Motion Description

For image-to-video, describe the motion:

```
"Slow cinematic camera pan from left to right,
gentle breeze moving leaves,
soft focus transition, atmospheric"
```

**Motion keywords:**
- Camera: pan, tilt, zoom, dolly, tracking
- Speed: slow, gentle, fast, dynamic
- Style: cinematic, smooth, handheld

### Scene Animation

```
"Ocean waves gently rolling onto shore,
foam dissipating on sand,
seagulls flying in background,
peaceful morning atmosphere"
```

### Character Animation

```
"Person walking through city street,
confident stride, looking around,
bustling crowd in background,
natural movement"
```

---

## Style Keywords Reference

### Photography Styles

| Style | Keywords | Best For |
|-------|----------|----------|
| Portrait | "85mm, shallow DOF, studio lighting" | People |
| Landscape | "wide angle, golden hour, HDR" | Scenery |
| Product | "white background, soft light, commercial" | Objects |
| Street | "candid, urban, documentary style" | City scenes |
| Fashion | "editorial, high fashion, dramatic lighting" | Clothing |

### Art Styles

| Style | Keywords | Result |
|-------|----------|--------|
| Photorealistic | "hyperrealistic, photograph, detailed" | Like a photo |
| Digital Art | "digital painting, concept art, detailed" | Digital illustration |
| Oil Painting | "oil on canvas, brushstrokes, classical" | Traditional painting |
| Watercolor | "watercolor, soft edges, flowing colors" | Soft, dreamy |
| Anime | "anime style, cel shaded, vibrant" | Japanese animation |
| 3D Render | "3D render, octane, ray tracing" | Computer graphics |

### Quality Keywords

```
High Quality: "4k", "8k", "high resolution", "detailed", "sharp focus"
Professional: "professional", "commercial", "editorial", "studio"
Artistic: "masterpiece", "award-winning", "museum quality"
```

---

## Prompt Patterns

### Pattern 1: Subject-First

```
"[Subject], [details], [environment], [style], [quality]"

Example:
"A red vintage sports car, 1960s Corvette, desert highway at sunset,
cinematic photography, dramatic lighting, 4k"
```

### Pattern 2: Scene-First

```
"[Environment/Scene], [subject within], [style], [mood]"

Example:
"Cozy coffee shop interior, young woman reading book by window,
warm afternoon light streaming in, lifestyle photography, peaceful mood"
```

### Pattern 3: Style-First

```
"[Style] of [subject], [details], [quality]"

Example:
"Oil painting style portrait of elderly fisherman,
weathered face, wise eyes, Rembrandt lighting, museum quality"
```

### Pattern 4: Cinematic

```
"Cinematic shot of [subject], [camera angle], [lighting], [mood]"

Example:
"Cinematic wide shot of lone astronaut on Mars surface,
low angle, dramatic sunset lighting, epic scale, IMAX quality"
```

---

## Common Mistakes

### Too Vague

```
❌ "a dog"
✅ "Golden retriever puppy playing fetch in park, sunny day, action shot"
```

### Too Long

```
❌ "A very beautiful extremely detailed highly realistic photograph of a
    magnificent majestic powerful strong muscular..."
✅ "Majestic lion portrait, golden savanna, National Geographic style"
```

### Contradictory

```
❌ "Photorealistic anime style" (contradictory styles)
✅ "Anime-inspired character design with realistic lighting"
```

### Missing Context

```
❌ "Person sitting"
✅ "Young professional sitting at modern desk, laptop open,
    office environment, natural window light"
```

---

## Model-Specific Tips

### FLUX Models

- Responds well to detailed descriptions
- Good with artistic styles
- Use specific art references

```
"Baroque-style digital painting of royal court scene,
rich velvet textures, gold accents, dramatic chiaroscuro lighting"
```

### Imagen4

- Excellent for photorealism
- Best with clear, descriptive prompts
- Handles text in images well

```
"Product packaging design for organic tea brand,
clean typography, natural elements, professional commercial photo"
```

### Video Models (Kling, Sora)

- Focus on motion description
- Keep prompts concise for video
- Describe camera movement

```
"Drone shot slowly rising above misty forest at dawn,
revealing mountain peaks, cinematic, smooth motion"
```

---

## Prompt Templates

### Portrait Template

```yaml
prompt: |
  [Age] [gender] [ethnicity] portrait,
  [expression/emotion],
  [clothing/style],
  [lighting type] lighting,
  [background],
  professional photography, sharp focus
```

### Product Template

```yaml
prompt: |
  [Product type] product photo,
  [color/material],
  [background color] background,
  [lighting style] lighting,
  commercial photography, [resolution]
```

### Landscape Template

```yaml
prompt: |
  [Location type] landscape,
  [time of day],
  [weather/atmosphere],
  [foreground elements],
  [photography style], [quality]
```

### Video Template

```yaml
prompt: |
  [Camera movement] shot of [subject],
  [action/motion],
  [environment],
  [speed] motion, [mood] atmosphere
```

---

## Advanced Techniques

### Weighted Emphasis

Some models support emphasis syntax:

```
"(beautiful sunset:1.2), ocean, (palm trees:0.8)"
```

### Negative Prompts

When supported:

```yaml
prompt: "professional portrait, studio lighting"
negative_prompt: "blurry, low quality, distorted, ugly"
```

### Multi-Subject Composition

```
"Split composition: left side shows modern city skyline,
right side shows ancient ruins,
dramatic contrast, surreal atmosphere"
```

### Specific Aspect Ratios

Match prompt to aspect ratio:

```yaml
# For 16:9 (landscape)
prompt: "Wide panoramic view of mountain range..."

# For 9:16 (portrait)
prompt: "Vertical composition of tall redwood tree..."

# For 1:1 (square)
prompt: "Centered portrait composition..."
```

---

## Practice Exercises

### Exercise 1: Improve This Prompt

```
Original: "cat on couch"

Improved: "Fluffy orange tabby cat curled up on vintage velvet couch,
warm afternoon sunlight through window, cozy home interior,
shallow depth of field, lifestyle photography"
```

### Exercise 2: Style Conversion

Convert to different styles:

```
Base subject: "mountain landscape"

Photorealistic: "Rocky mountain peaks at golden hour,
dramatic clouds, pristine alpine lake reflection,
National Geographic photography, 4k"

Oil painting: "Mountain landscape in the style of Albert Bierstadt,
dramatic lighting, romantic era painting, oil on canvas"

Anime: "Anime-style mountain scenery, Studio Ghibli inspired,
soft clouds, vibrant colors, peaceful atmosphere"
```

---

## Quick Reference Card

### Must-Have Elements
- Clear subject
- Style specification
- Quality keywords

### Good-to-Have Elements
- Lighting description
- Environment/background
- Mood/atmosphere
- Camera/lens specs (for photos)

### Avoid
- Contradictory styles
- Excessive length
- Vague descriptions
- Repeated keywords

---

[Back to Documentation Index](../index.md)
