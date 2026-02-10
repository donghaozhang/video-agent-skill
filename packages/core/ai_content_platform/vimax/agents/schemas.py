"""
Pydantic response schemas for native structured output.

These models define the JSON shape the LLM should produce. Fields use
``str`` instead of ``Literal`` so that unexpected LLM values don't cause
validation failures — enum mapping is handled in the agent layer.

When native ``response_format`` is enforced by the provider, the JSON
schema (via ``model_json_schema()``) still documents the expected values
in field descriptions, guiding the model without hard-rejecting surprises.

Usage:
    response = await llm.chat_with_structured_output(
        messages, output_schema=ScreenplayResponse
    )
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# =============================================================================
# Screenwriter response schema
# =============================================================================

class ShotResponse(BaseModel):
    """Single shot in a screenplay scene."""

    shot_id: str
    shot_type: str = "medium"  # Expected: wide, medium, close_up, etc.
    description: str
    camera_movement: str = "static"  # Expected: static, pan, tilt, dolly, etc.
    characters: List[str] = Field(default_factory=list)  # Character names in this shot
    duration_seconds: float = 5.0
    image_prompt: str = ""
    video_prompt: str = ""

    model_config = {"extra": "ignore"}


class SceneResponse(BaseModel):
    """Single scene in a screenplay."""

    scene_id: str
    title: str
    location: str = ""
    time: str = ""
    shots: List[ShotResponse] = Field(default_factory=list)

    model_config = {"extra": "ignore"}


class ScreenplayResponse(BaseModel):
    """Full screenplay returned by the LLM."""

    title: str
    logline: str = ""
    scenes: List[SceneResponse] = Field(default_factory=list)

    model_config = {"extra": "ignore"}


# =============================================================================
# Character Extractor response schema
# =============================================================================

class CharacterResponse(BaseModel):
    """Single character extracted from text."""

    name: str
    description: str = ""
    age: str = ""
    gender: str = ""
    appearance: str = ""
    personality: str = ""
    role: str = "minor"  # Expected: protagonist, antagonist, supporting, minor
    relationships: List[str] = Field(default_factory=list)

    model_config = {"extra": "ignore"}


class CharacterListResponse(BaseModel):
    """List of characters extracted from text.

    Wrapped in an object because json_schema mode requires a top-level object,
    not a bare array.
    """

    characters: List[CharacterResponse]

    model_config = {"extra": "ignore"}


# =============================================================================
# Novel Compression response schema
# =============================================================================

class SceneCompression(BaseModel):
    """Single scene from novel compression."""

    title: str
    description: str
    characters: List[str] = Field(default_factory=list)
    setting: str = ""

    model_config = {"extra": "ignore"}


class ChapterCompressionResponse(BaseModel):
    """Compressed chapter with key visual scenes."""

    title: str
    scenes: List[SceneCompression]

    model_config = {"extra": "ignore"}
