# Character Reference Image Support for Storyboard Generation

> Implementation plan for supporting character reference images in each shot of the storyboard to ensure visual consistency.

---

## Overview

### Current State
The current ViMax implementation generates storyboard shots using **text prompts only**, without using character reference images. This results in inconsistent character appearances across different shots.

### Goal
Enable the storyboard generation pipeline to use pre-generated character portraits as reference images, ensuring visual consistency of characters across all shots.

### Key Benefits
- **Character Consistency**: Same character looks the same across all shots
- **Better Quality**: Reference images guide the AI to maintain specific features
- **Professional Output**: Matches industry-standard storyboard workflows

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Character Reference Image Flow                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. CharacterExtractor                                                   │
│     └── Extracts character info from script                              │
│                    │                                                     │
│                    ▼                                                     │
│  2. CharacterPortraitsGenerator                                          │
│     └── Generates multi-angle portraits (front/side/back/3-4)            │
│                    │                                                     │
│                    ▼                                                     │
│  3. CharacterPortraitRegistry (NEW)                                      │
│     └── Stores and indexes all character portraits                       │
│                    │                                                     │
│                    ▼                                                     │
│  4. ReferenceImageSelector (NEW)                                         │
│     └── Selects best portrait for each shot based on:                    │
│         - Characters in shot                                             │
│         - Camera angle                                                   │
│         - Shot type (close-up, medium, wide)                             │
│                    │                                                     │
│                    ▼                                                     │
│  5. StoryboardArtist (ENHANCED)                                          │
│     └── Generates shot images using:                                     │
│         - Text prompt                                                    │
│         - Character reference images                                     │
│                    │                                                     │
│                    ▼                                                     │
│  6. Final Storyboard with Consistent Characters                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Subtasks

### Subtask 1: Extend Data Models with Reference Image Fields

**Estimated Duration**: 30 minutes

**Description**: Add reference image fields to `ShotDescription` and create `CharacterPortraitRegistry` model.

**Files to Modify**:
- `packages/core/ai_content_platform/vimax/interfaces/shot.py`
- `packages/core/ai_content_platform/vimax/interfaces/character.py`
- `packages/core/ai_content_platform/vimax/interfaces/__init__.py`

**Changes**:

```python
# shot.py - Add to ShotDescription
class ShotDescription(BaseModel):
    # ... existing fields ...

    # NEW: Reference images for characters in this shot
    character_references: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of character name to reference image path"
    )

    # NEW: Selected reference image for IP-Adapter
    primary_reference_image: Optional[str] = Field(
        default=None,
        description="Primary reference image path for this shot"
    )
```

```python
# character.py - Add CharacterPortraitRegistry
class CharacterPortraitRegistry(BaseModel):
    """Registry of all character portraits for a project."""

    project_id: str
    portraits: Dict[str, CharacterPortrait] = Field(default_factory=dict)

    def get_portrait(self, name: str) -> Optional[CharacterPortrait]:
        """Get portrait by character name."""
        return self.portraits.get(name)

    def get_best_view(self, name: str, camera_angle: str) -> Optional[str]:
        """Get best view image path based on camera angle."""
        portrait = self.get_portrait(name)
        if not portrait:
            return None

        # Map camera angles to portrait views
        angle_to_view = {
            "front": "front_view",
            "side": "side_view",
            "back": "back_view",
            "three_quarter": "three_quarter_view",
            "eye_level": "front_view",
            "profile": "side_view",
        }
        view = angle_to_view.get(camera_angle, "front_view")
        return getattr(portrait, view, portrait.front_view)
```

**Unit Tests**:
- `tests/unit/vimax/test_interfaces.py` - Add tests for new fields and registry

---

### Subtask 2: Create ReferenceImageSelector Agent

**Estimated Duration**: 1 hour

**Description**: Create a new agent that intelligently selects the best reference image for each shot.

**Files to Create**:
- `packages/core/ai_content_platform/vimax/agents/reference_selector.py`

**Files to Modify**:
- `packages/core/ai_content_platform/vimax/agents/__init__.py`

**Implementation**:

```python
# reference_selector.py
"""
Reference Image Selector Agent

Intelligently selects the best character reference image for each shot
based on camera angle, shot type, and visible characters.
"""

from typing import List, Optional, Dict
from pydantic import Field

from .base import BaseAgent, AgentConfig, AgentResult
from ..interfaces import (
    ShotDescription,
    CharacterPortrait,
    CharacterPortraitRegistry,
)


class ReferenceSelectorConfig(AgentConfig):
    """Configuration for ReferenceImageSelector."""

    name: str = "ReferenceImageSelector"
    use_llm_for_selection: bool = False  # Use heuristics by default
    llm_model: str = "kimi-k2.5"  # For complex selections


class ReferenceSelectionResult(BaseModel):
    """Result of reference selection for a shot."""

    shot_id: str
    selected_references: Dict[str, str]  # character_name -> image_path
    primary_reference: Optional[str] = None
    selection_reason: str = ""


class ReferenceImageSelector(BaseAgent):
    """
    Selects best reference images for shots.

    Selection Strategy:
    1. For each character in the shot, find their portrait
    2. Choose the view that best matches the camera angle
    3. For multiple characters, select primary based on importance
    """

    # Camera angle to portrait view mapping
    ANGLE_TO_VIEW = {
        "front": "front",
        "eye_level": "front",
        "straight_on": "front",
        "side": "side",
        "profile": "side",
        "left": "side",
        "right": "side",
        "back": "back",
        "behind": "back",
        "three_quarter": "three_quarter",
        "45_degree": "three_quarter",
    }

    # Shot type hints for view selection
    SHOT_TYPE_PREFERENCE = {
        "close_up": ["front", "three_quarter"],
        "extreme_close_up": ["front"],
        "medium": ["front", "three_quarter", "side"],
        "wide": ["front", "side", "back"],
        "over_the_shoulder": ["back", "three_quarter"],
        "pov": [],  # No reference needed for POV
    }

    async def select_for_shot(
        self,
        shot: ShotDescription,
        registry: CharacterPortraitRegistry,
    ) -> ReferenceSelectionResult:
        """Select best references for a single shot."""

        selected = {}
        reasons = []

        for char_name in shot.characters:
            portrait = registry.get_portrait(char_name)
            if not portrait:
                reasons.append(f"No portrait found for {char_name}")
                continue

            # Determine best view based on camera angle and shot type
            best_view = self._select_best_view(
                portrait,
                shot.camera_angle,
                shot.shot_type.value,
            )

            if best_view:
                selected[char_name] = best_view
                reasons.append(f"{char_name}: {best_view} (angle={shot.camera_angle})")

        # Select primary reference (first character or most important)
        primary = list(selected.values())[0] if selected else None

        return ReferenceSelectionResult(
            shot_id=shot.shot_id,
            selected_references=selected,
            primary_reference=primary,
            selection_reason="; ".join(reasons),
        )

    def _select_best_view(
        self,
        portrait: CharacterPortrait,
        camera_angle: str,
        shot_type: str,
    ) -> Optional[str]:
        """Select best portrait view for camera settings."""

        # Get preferred view from camera angle
        preferred_view = self.ANGLE_TO_VIEW.get(
            camera_angle.lower(), "front"
        )

        # Get available views
        views = portrait.views

        # Try preferred view first
        if preferred_view in views:
            return views[preferred_view]

        # Fall back to shot type preferences
        preferences = self.SHOT_TYPE_PREFERENCE.get(shot_type, ["front"])
        for pref in preferences:
            if pref in views:
                return views[pref]

        # Last resort: any available view
        return next(iter(views.values()), None)
```

**Unit Tests**:
- `tests/unit/vimax/test_reference_selector.py`

---

### Subtask 3: Add Image-to-Image Support to ImageAdapter

**Estimated Duration**: 1.5 hours

**Description**: Extend `ImageGeneratorAdapter` to support image-to-image generation with reference images using IP-Adapter or similar techniques.

**Files to Modify**:
- `packages/core/ai_content_platform/vimax/adapters/image_adapter.py`

**Changes**:

```python
# Add to ImageAdapterConfig
class ImageAdapterConfig(AdapterConfig):
    # ... existing fields ...

    # NEW: IP-Adapter settings
    ip_adapter_model: str = "ip-adapter-plus"
    ip_adapter_scale: float = 0.6  # 0.0-1.0, how much to follow reference
    reference_strength: float = 0.5  # Strength of reference image influence


# Add new models that support image references
MODEL_MAP_WITH_REFERENCE = {
    "flux_kontext": "fal-ai/flux-kontext/max/image-to-image",
    "flux_redux": "fal-ai/flux-pro/v1.1-ultra/redux",
    "seededit_v3": "fal-ai/seededit-v3",
    "photon_flash": "fal-ai/photon/flash",
}


# Add new method to ImageGeneratorAdapter
async def generate_with_reference(
    self,
    prompt: str,
    reference_image: str,
    model: Optional[str] = None,
    reference_strength: float = 0.6,
    aspect_ratio: Optional[str] = None,
    output_path: Optional[str] = None,
    **kwargs,
) -> ImageOutput:
    """
    Generate image using a reference image for consistency.

    Args:
        prompt: Text description
        reference_image: Path or URL to reference image
        model: Model to use (must support image-to-image)
        reference_strength: How much to follow reference (0.0-1.0)
        aspect_ratio: Output aspect ratio
        output_path: Where to save output

    Returns:
        ImageOutput with generated image
    """
    await self.ensure_initialized()

    model = model or "flux_kontext"  # Default to Kontext for references

    # Convert local path to URL if needed
    if reference_image and not reference_image.startswith("http"):
        reference_image = self._upload_to_fal(reference_image)

    endpoint = self.MODEL_MAP_WITH_REFERENCE.get(
        model,
        "fal-ai/flux-kontext/max/image-to-image"
    )

    arguments = {
        "prompt": prompt,
        "image_url": reference_image,
        "strength": reference_strength,
        "image_size": self._aspect_to_size(aspect_ratio or "16:9"),
        "num_inference_steps": kwargs.get("num_inference_steps", 28),
    }

    # Call FAL with reference
    result = fal_client.subscribe(endpoint, arguments=arguments)

    # ... process result same as generate() ...


async def generate_with_multiple_references(
    self,
    prompt: str,
    reference_images: List[str],
    weights: Optional[List[float]] = None,
    **kwargs,
) -> ImageOutput:
    """
    Generate image using multiple reference images.

    Useful for shots with multiple characters.
    """
    # Combine references with IP-Adapter style composition
    # or use model-specific multi-reference support
    pass
```

**Unit Tests**:
- `tests/unit/vimax/test_adapters.py` - Add tests for reference image generation

---

### Subtask 4: Enhance StoryboardArtist to Use Reference Images

**Estimated Duration**: 1 hour

**Description**: Update `StoryboardArtist` to integrate reference images during shot generation.

**Files to Modify**:
- `packages/core/ai_content_platform/vimax/agents/storyboard_artist.py`

**Changes**:

```python
# Add to StoryboardArtistConfig
class StoryboardArtistConfig(AgentConfig):
    # ... existing fields ...

    # NEW: Reference image settings
    use_character_references: bool = True
    reference_strength: float = 0.6
    reference_model: str = "flux_kontext"  # Model that supports references


# Add to StoryboardArtist
class StoryboardArtist(BaseAgent):

    def __init__(self, config, portrait_registry: Optional[CharacterPortraitRegistry] = None):
        super().__init__(config)
        self.portrait_registry = portrait_registry
        self._reference_selector = ReferenceImageSelector()

    async def process(
        self,
        script: Script,
        portrait_registry: Optional[CharacterPortraitRegistry] = None,
    ) -> AgentResult[StoryboardResult]:
        """Generate storyboard with optional character references."""

        registry = portrait_registry or self.portrait_registry

        for scene in script.scenes:
            for shot in scene.shots:
                # Select reference images if registry available
                if registry and self.config.use_character_references:
                    ref_result = await self._reference_selector.select_for_shot(
                        shot, registry
                    )
                    shot.character_references = ref_result.selected_references
                    shot.primary_reference_image = ref_result.primary_reference

                # Generate with or without reference
                if shot.primary_reference_image:
                    image = await self._image_adapter.generate_with_reference(
                        prompt=self._build_prompt(shot, scene),
                        reference_image=shot.primary_reference_image,
                        reference_strength=self.config.reference_strength,
                        model=self.config.reference_model,
                    )
                else:
                    image = await self._image_adapter.generate(
                        prompt=self._build_prompt(shot, scene),
                    )

                # ... rest of processing ...
```

**Unit Tests**:
- `tests/unit/vimax/test_storyboard_artist.py` - Add tests for reference integration

---

### Subtask 5: Update Pipelines to Pass Portrait Registry

**Estimated Duration**: 45 minutes

**Description**: Update `Idea2VideoPipeline` and `Script2VideoPipeline` to generate portraits and pass them to storyboard generation.

**Files to Modify**:
- `packages/core/ai_content_platform/vimax/pipelines/idea2video.py`
- `packages/core/ai_content_platform/vimax/pipelines/script2video.py`

**Changes**:

```python
# idea2video.py
class Idea2VideoPipeline:

    async def run(self, idea: str, ...) -> Idea2VideoResult:
        # ... existing steps ...

        # Step 3: Generate Character Portraits
        self.logger.info("Step 3: Generating character portraits...")
        portrait_registry = CharacterPortraitRegistry(project_id=self.project_id)

        for character in characters:
            portrait_result = await self.portraits_generator.process(character)
            if portrait_result.success:
                portrait_registry.portraits[character.name] = portrait_result.result

        # Step 4: Generate Storyboard WITH portrait registry
        self.logger.info("Step 4: Generating storyboard with character consistency...")
        storyboard_result = await self.storyboard_artist.process(
            script,
            portrait_registry=portrait_registry,  # NEW: Pass registry
        )
```

**Unit Tests**:
- `tests/unit/vimax/test_pipelines.py` - Update pipeline tests

---

### Subtask 6: Add CLI Commands for Reference Image Management

**Estimated Duration**: 30 minutes

**Description**: Add CLI commands to manage character portraits and view reference mappings.

**Files to Modify**:
- `packages/core/ai_content_platform/vimax/cli/commands.py`

**Changes**:

```python
@vimax_cli.command()
def generate_portraits(
    script: str = typer.Argument(..., help="Path to script JSON"),
    output_dir: str = typer.Option("output/portraits", help="Output directory"),
):
    """Generate character portraits from a script."""
    pass


@vimax_cli.command()
def list_portraits(
    registry_path: str = typer.Argument(..., help="Path to portrait registry"),
):
    """List all character portraits in a registry."""
    pass


@vimax_cli.command()
def preview_references(
    script: str = typer.Argument(..., help="Path to script"),
    registry: str = typer.Argument(..., help="Path to portrait registry"),
):
    """Preview which reference images would be used for each shot."""
    pass
```

---

### Subtask 7: Write Comprehensive Unit Tests

**Estimated Duration**: 1 hour

**Description**: Create comprehensive test coverage for all new functionality.

**Files to Create**:
- `tests/unit/vimax/test_reference_selector.py`
- `tests/unit/vimax/test_portrait_registry.py`

**Files to Modify**:
- `tests/unit/vimax/test_adapters.py`
- `tests/unit/vimax/test_storyboard_artist.py`
- `tests/unit/vimax/test_pipelines.py`

**Test Cases**:

```python
# test_reference_selector.py
class TestReferenceImageSelector:

    def test_select_front_view_for_closeup(self):
        """Close-up shots should prefer front view."""
        pass

    def test_select_side_view_for_profile_angle(self):
        """Profile camera angle should select side view."""
        pass

    def test_select_back_view_for_over_shoulder(self):
        """Over-the-shoulder shots should prefer back view."""
        pass

    def test_fallback_when_preferred_view_missing(self):
        """Should fallback to available views."""
        pass

    def test_multiple_characters_selection(self):
        """Should select references for all characters in shot."""
        pass


# test_portrait_registry.py
class TestCharacterPortraitRegistry:

    def test_get_portrait_by_name(self):
        pass

    def test_get_best_view_for_camera_angle(self):
        pass

    def test_registry_serialization(self):
        """Registry should serialize to/from JSON."""
        pass
```

---

### Subtask 8: Update Documentation

**Estimated Duration**: 30 minutes

**Description**: Update documentation to explain the new character reference feature.

**Files to Modify**:
- `packages/core/ai_content_platform/vimax/README.md`
- `issues/todo/ViMax_Complete_Integration_Package/docs/User_Guide.md`

**Files to Create**:
- `issues/todo/ViMax_Complete_Integration_Package/docs/CHARACTER_CONSISTENCY_GUIDE.md`

---

## Summary

| Subtask | Duration | Files |
|---------|----------|-------|
| 1. Extend Data Models | 30 min | `interfaces/shot.py`, `interfaces/character.py` |
| 2. Create ReferenceImageSelector | 1 hour | `agents/reference_selector.py` |
| 3. Add Image-to-Image Support | 1.5 hours | `adapters/image_adapter.py` |
| 4. Enhance StoryboardArtist | 1 hour | `agents/storyboard_artist.py` |
| 5. Update Pipelines | 45 min | `pipelines/idea2video.py`, `pipelines/script2video.py` |
| 6. Add CLI Commands | 30 min | `cli/commands.py` |
| 7. Write Unit Tests | 1 hour | `tests/unit/vimax/test_*.py` |
| 8. Update Documentation | 30 min | Various `.md` files |
| **Total** | **~7 hours** | |

---

## Implementation Priority

1. **Phase 1 (Core)**: Subtasks 1-4 - Enable basic reference image support
2. **Phase 2 (Integration)**: Subtask 5 - Wire through pipelines
3. **Phase 3 (Polish)**: Subtasks 6-8 - CLI, tests, docs

---

## Technical Considerations

### Model Selection for Reference Images
- **flux_kontext**: Best for maintaining style/character consistency
- **seededit_v3**: Good for subtle modifications
- **photon_flash**: Fast but less precise reference following

### Reference Strength Tuning
- `0.3-0.4`: Subtle influence, more creative freedom
- `0.5-0.6`: Balanced (recommended default)
- `0.7-0.8`: Strong consistency, less variation
- `0.9+`: Very strict, may limit creativity

### Fallback Strategy
When reference images are unavailable:
1. Fall back to text-only generation
2. Log warning for user awareness
3. Continue pipeline without failing

---

*Document Version: 1.0*
*Created: 2026-02-03*
*Author: Claude Code*
