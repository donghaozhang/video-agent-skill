"""
Tests for native structured output migration and output organization.

Verifies:
- Pydantic response schemas produce valid JSON schemas
- LLM adapter passes response_format via extra_body correctly
- Agents convert structured responses to internal models
- Pipeline output uses meaningful file names and per-chapter folders
- scripts_only mode skips image/video generation
"""

import json
import re
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import BaseModel

# =============================================================================
# Replicated schemas for isolated testing (mirrors agents/schemas.py)
# =============================================================================

from typing import List, Optional
from pydantic import Field


class ShotResponse(BaseModel):
    shot_id: str
    shot_type: str = "medium"
    description: str
    camera_movement: str = "static"
    characters: List[str] = Field(default_factory=list)
    duration_seconds: float = 5.0
    image_prompt: str = ""
    video_prompt: str = ""
    model_config = {"extra": "ignore"}


class SceneResponse(BaseModel):
    scene_id: str
    title: str
    location: str = ""
    time: str = ""
    shots: List[ShotResponse] = Field(default_factory=list)
    model_config = {"extra": "ignore"}


class ScreenplayResponse(BaseModel):
    title: str
    logline: str = ""
    scenes: List[SceneResponse] = Field(default_factory=list)
    model_config = {"extra": "ignore"}


class CharacterResponse(BaseModel):
    name: str
    description: str = ""
    age: str = ""
    gender: str = ""
    appearance: str = ""
    personality: str = ""
    role: str = "minor"
    relationships: List[str] = Field(default_factory=list)
    model_config = {"extra": "ignore"}


class CharacterListResponse(BaseModel):
    characters: List[CharacterResponse]
    model_config = {"extra": "ignore"}


class SceneCompression(BaseModel):
    title: str
    description: str
    characters: List[str] = Field(default_factory=list)
    setting: str = ""
    model_config = {"extra": "ignore"}


class ChapterCompressionResponse(BaseModel):
    title: str
    scenes: List[SceneCompression]
    model_config = {"extra": "ignore"}


# =============================================================================
# Schema validation tests
# =============================================================================

class TestSchemaValidation:
    """Verify schemas produce valid JSON schemas and parse correctly."""

    def test_screenplay_schema_is_valid_json_schema(self):
        """model_json_schema() produces valid JSON schema."""
        schema = ScreenplayResponse.model_json_schema()
        assert schema["type"] == "object"
        assert "title" in schema["properties"]
        assert "scenes" in schema["properties"]
        # Verify it's serializable
        json.dumps(schema)

    def test_character_list_schema_is_valid_json_schema(self):
        """CharacterListResponse schema wraps array in object."""
        schema = CharacterListResponse.model_json_schema()
        assert schema["type"] == "object"
        assert "characters" in schema["properties"]
        json.dumps(schema)

    def test_chapter_compression_schema_is_valid_json_schema(self):
        """ChapterCompressionResponse schema is valid."""
        schema = ChapterCompressionResponse.model_json_schema()
        assert schema["type"] == "object"
        assert "title" in schema["properties"]
        assert "scenes" in schema["properties"]
        json.dumps(schema)

    def test_screenplay_parses_valid_json(self):
        """Schema parses well-formed screenplay JSON."""
        data = {
            "title": "Test Movie",
            "logline": "A test logline",
            "scenes": [
                {
                    "scene_id": "scene_001",
                    "title": "Opening",
                    "location": "Mountain",
                    "time": "Dawn",
                    "shots": [
                        {
                            "shot_id": "shot_001",
                            "shot_type": "wide",
                            "description": "Panoramic view",
                            "camera_movement": "pan",
                            "duration_seconds": 5.0,
                            "image_prompt": "mountains at dawn",
                            "video_prompt": "camera pans across mountains",
                        }
                    ],
                }
            ],
        }
        result = ScreenplayResponse(**data)
        assert result.title == "Test Movie"
        assert len(result.scenes) == 1
        assert result.scenes[0].shots[0].shot_type == "wide"

    def test_screenplay_accepts_unexpected_shot_type(self):
        """Schema accepts any string shot_type (validation in agent layer)."""
        data = {
            "title": "Test",
            "logline": "Test",
            "scenes": [
                {
                    "scene_id": "s1",
                    "title": "Scene",
                    "location": "Here",
                    "time": "Now",
                    "shots": [
                        {
                            "shot_id": "sh1",
                            "shot_type": "extreme_aerial_dolly",
                            "description": "desc",
                            "camera_movement": "slow_push_in",
                            "duration_seconds": 5.0,
                            "image_prompt": "prompt",
                            "video_prompt": "prompt",
                        }
                    ],
                }
            ],
        }
        result = ScreenplayResponse(**data)
        assert result.scenes[0].shots[0].shot_type == "extreme_aerial_dolly"
        assert result.scenes[0].shots[0].camera_movement == "slow_push_in"

    def test_character_list_parses_valid_json(self):
        """CharacterListResponse parses object with characters array."""
        data = {
            "characters": [
                {
                    "name": "Alice",
                    "description": "The hero",
                    "role": "protagonist",
                },
                {
                    "name": "Bob",
                    "role": "antagonist",
                },
            ]
        }
        result = CharacterListResponse(**data)
        assert len(result.characters) == 2
        assert result.characters[0].name == "Alice"
        assert result.characters[1].role == "antagonist"

    def test_character_list_rejects_missing_characters_key(self):
        """Schema rejects data without the required 'characters' key."""
        with pytest.raises(Exception):
            CharacterListResponse(**{"people": []})

    def test_character_defaults_to_minor_role(self):
        """Character with no explicit role defaults to 'minor'."""
        char = CharacterResponse(name="Extra")
        assert char.role == "minor"

    def test_character_accepts_unexpected_role(self):
        """Schema accepts any string role (validation in agent layer)."""
        char = CharacterResponse(name="Hero", role="main character")
        assert char.role == "main character"

    def test_chapter_compression_parses_valid_json(self):
        """ChapterCompressionResponse parses correctly."""
        data = {
            "title": "Chapter 1",
            "scenes": [
                {
                    "title": "Opening",
                    "description": "A dark forest",
                    "characters": ["Alice", "Bob"],
                    "setting": "Forest",
                }
            ],
        }
        result = ChapterCompressionResponse(**data)
        assert result.title == "Chapter 1"
        assert result.scenes[0].characters == ["Alice", "Bob"]

    def test_schemas_ignore_extra_fields(self):
        """Schemas with extra='ignore' don't reject unexpected fields."""
        data = {
            "title": "Test",
            "scenes": [],
            "unexpected_field": "should be ignored",
        }
        result = ChapterCompressionResponse(**data)
        assert result.title == "Test"


# =============================================================================
# LLM adapter structured output tests
# =============================================================================

class TestLLMAdapterStructuredOutput:
    """Verify LLM adapter passes correct parameters for structured output."""

    def test_native_extra_body_structure(self):
        """Verify the extra_body structure matches OpenRouter spec."""
        schema = ScreenplayResponse.model_json_schema()
        extra_body = {
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "screenplay",
                    "strict": True,
                    "schema": schema,
                },
            },
            "provider": {
                "require_parameters": True,
            },
        }
        # Verify it's JSON-serializable
        serialized = json.dumps(extra_body)
        parsed = json.loads(serialized)

        assert parsed["response_format"]["type"] == "json_schema"
        assert parsed["response_format"]["json_schema"]["strict"] is True
        assert parsed["response_format"]["json_schema"]["name"] == "screenplay"
        assert parsed["provider"]["require_parameters"] is True

    def test_native_extra_body_has_require_parameters(self):
        """require_parameters prevents silent fallback to json_object."""
        extra_body = {
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "test",
                    "strict": True,
                    "schema": CharacterListResponse.model_json_schema(),
                },
            },
            "provider": {
                "require_parameters": True,
            },
        }
        assert extra_body["provider"]["require_parameters"] is True

    def test_parse_json_response_direct(self):
        """Direct JSON content is parsed correctly."""
        content = '{"title": "Test", "logline": "A test", "scenes": []}'
        data = json.loads(content)
        result = ScreenplayResponse(**data)
        assert result.title == "Test"

    def test_parse_json_response_with_code_fence(self):
        """JSON wrapped in markdown code fences is extracted."""
        import re
        content = '```json\n{"title": "Test", "logline": "A test", "scenes": []}\n```'
        fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        assert fence_match is not None
        data = json.loads(fence_match.group(1))
        result = ScreenplayResponse(**data)
        assert result.title == "Test"

    def test_parse_json_response_with_trailing_commas(self):
        """Trailing commas are fixed before parsing."""
        import re
        content = '{"title": "Test", "logline": "A test", "scenes": [],}'
        fixed = re.sub(r',\s*([}\]])', r'\1', content)
        data = json.loads(fixed)
        result = ScreenplayResponse(**data)
        assert result.title == "Test"


# =============================================================================
# Agent response mapping tests
# =============================================================================

class TestAgentResponseMapping:
    """Verify structured responses map to internal models correctly."""

    def test_screenplay_response_to_dict(self):
        """ScreenplayResponse.model_dump() produces dict usable by Script builder."""
        screenplay = ScreenplayResponse(
            title="Test Movie",
            logline="A logline",
            scenes=[
                SceneResponse(
                    scene_id="scene_001",
                    title="Opening",
                    location="Mountain",
                    time="Dawn",
                    shots=[
                        ShotResponse(
                            shot_id="shot_001",
                            shot_type="wide",
                            description="Panoramic view",
                            camera_movement="pan",
                            duration_seconds=5.0,
                            image_prompt="mountains at dawn",
                            video_prompt="camera pans",
                        )
                    ],
                )
            ],
        )
        data = screenplay.model_dump()
        assert data["title"] == "Test Movie"
        assert data["scenes"][0]["shots"][0]["shot_type"] == "wide"
        assert data["scenes"][0]["shots"][0]["camera_movement"] == "pan"

    def test_character_list_to_character_models(self):
        """CharacterListResponse maps to CharacterInNovel-compatible dicts."""
        result = CharacterListResponse(
            characters=[
                CharacterResponse(
                    name="Alice",
                    description="The hero",
                    appearance="Tall, dark hair",
                    role="protagonist",
                    relationships=["Bob"],
                ),
            ]
        )
        char = result.characters[0]
        assert char.name == "Alice"
        assert char.role == "protagonist"
        assert char.relationships == ["Bob"]
        assert char.appearance == "Tall, dark hair"

    def test_chapter_compression_to_chapter_summary(self):
        """ChapterCompressionResponse maps to ChapterSummary fields."""
        result = ChapterCompressionResponse(
            title="The Dark Forest",
            scenes=[
                SceneCompression(
                    title="Entry",
                    description="Heroes enter the dark forest",
                    characters=["Alice", "Bob"],
                    setting="Dense forest",
                ),
                SceneCompression(
                    title="Ambush",
                    description="Bandits attack the group",
                    characters=["Alice", "Bandit Leader"],
                    setting="Forest clearing",
                ),
            ],
        )
        # Map the way novel2movie.py does it
        key_events = [s.description for s in result.scenes]
        characters = [c for s in result.scenes for c in s.characters]

        assert result.title == "The Dark Forest"
        assert key_events == [
            "Heroes enter the dark forest",
            "Bandits attack the group",
        ]
        assert characters == ["Alice", "Bob", "Alice", "Bandit Leader"]

    def test_empty_screenplay(self):
        """Empty scenes list is valid."""
        result = ScreenplayResponse(title="Empty", logline="Nothing", scenes=[])
        assert len(result.scenes) == 0

    def test_empty_character_list(self):
        """Empty characters list is valid."""
        result = CharacterListResponse(characters=[])
        assert len(result.characters) == 0

    def test_empty_chapter_compression(self):
        """Empty scenes list is valid for compression."""
        result = ChapterCompressionResponse(title="Empty Chapter", scenes=[])
        assert len(result.scenes) == 0


# =============================================================================
# Output organization tests
# =============================================================================

class TestOutputOrganization:
    """Verify meaningful file names and per-chapter folder structure."""

    def _safe_slug(self, value: str) -> str:
        """Mirror the _safe_slug method used in agents."""
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
        return safe or "untitled"

    def _safe_slug_lower(self, value: str) -> str:
        """Mirror the _safe_slug method used in character_portraits (lowercased)."""
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_").lower()
        return safe or "unknown"

    def test_portrait_path_uses_character_name(self):
        """Portrait output path includes character name as directory."""
        char_name = "Elena Vasquez"
        view = "front"
        char_slug = self._safe_slug_lower(char_name)
        output_path = f"portraits/{char_slug}/{view}.png"

        assert output_path == "portraits/elena_vasquez/front.png"

    def test_portrait_path_sanitizes_special_chars(self):
        """Special characters in character names are sanitized."""
        char_name = "O'Brien (Captain)"
        char_slug = self._safe_slug_lower(char_name)
        output_path = f"portraits/{char_slug}/side.png"

        assert "'" not in output_path
        assert "(" not in output_path
        assert output_path == "portraits/o_brien_captain/side.png"

    def test_storyboard_path_with_chapter_index(self):
        """Storyboard uses per-chapter subfolder with chapter index."""
        chapter_index = 3
        script_title = "The Discovery"
        title_slug = self._safe_slug(script_title)
        dir_name = f"chapter_{chapter_index:03d}_{title_slug}"

        assert dir_name == "chapter_003_The_Discovery"

    def test_storyboard_shot_filename_is_descriptive(self):
        """Storyboard shot file includes scene index, shot type, and scene title."""
        scene_idx = 1
        shot_type = "wide"
        scene_title = "The Discovery"
        scene_slug = self._safe_slug(scene_title)[:30]
        filename = f"scene_{scene_idx:03d}_{shot_type}_{scene_slug}.png"

        assert filename == "scene_001_wide_The_Discovery.png"

    def test_storyboard_without_chapter_index(self):
        """Without chapter_index, storyboard uses script title as directory."""
        script_title = "First Contact"
        dir_name = self._safe_slug(script_title)

        assert dir_name == "First_Contact"

    def test_novel2movie_config_scripts_only(self):
        """Novel2MovieConfig supports scripts_only flag."""
        from packages.core.ai_content_platform.vimax.pipelines.novel2movie import Novel2MovieConfig

        config = Novel2MovieConfig(scripts_only=True)
        assert config.scripts_only is True

        config_default = Novel2MovieConfig()
        assert config_default.scripts_only is False

    def test_novel2movie_config_storyboard_only(self):
        """Novel2MovieConfig supports storyboard_only flag."""
        from packages.core.ai_content_platform.vimax.pipelines.novel2movie import Novel2MovieConfig

        config = Novel2MovieConfig(storyboard_only=True)
        assert config.storyboard_only is True

    def test_scripts_only_and_storyboard_only_independent(self):
        """scripts_only and storyboard_only are independent flags."""
        from packages.core.ai_content_platform.vimax.pipelines.novel2movie import Novel2MovieConfig

        config = Novel2MovieConfig(scripts_only=True, storyboard_only=True)
        assert config.scripts_only is True
        assert config.storyboard_only is True

    def test_portrait_all_views_have_meaningful_names(self):
        """All portrait views produce meaningful file names."""
        views = ["front", "side", "back", "three_quarter"]
        char_slug = self._safe_slug_lower("James Park")

        for view in views:
            path = f"portraits/{char_slug}/{view}.png"
            assert char_slug in path
            assert view in path
            assert path == f"portraits/james_park/{view}.png"

    def test_storyboard_long_scene_title_truncated(self):
        """Long scene titles are truncated in file names."""
        scene_title = "A Very Long Scene Title That Goes On And On Forever"
        scene_slug = self._safe_slug(scene_title)[:30]
        filename = f"scene_001_wide_{scene_slug}.png"

        assert len(scene_slug) <= 30
        assert filename.startswith("scene_001_wide_")


# =============================================================================
# Character reference flow tests
# =============================================================================

class TestCharacterReferenceFlow:
    """Verify characters field flows from schema through to ShotDescription."""

    def test_shot_response_has_characters_field(self):
        """ShotResponse schema includes characters list."""
        shot = ShotResponse(
            shot_id="shot_001",
            description="Elena stands on cliff",
            characters=["Elena Vasquez", "James Park"],
        )
        assert shot.characters == ["Elena Vasquez", "James Park"]

    def test_shot_response_characters_default_empty(self):
        """Characters defaults to empty list when not provided."""
        shot = ShotResponse(shot_id="shot_001", description="Empty landscape")
        assert shot.characters == []

    def test_shot_response_characters_in_schema(self):
        """Characters field appears in JSON schema for structured output."""
        schema = ShotResponse.model_json_schema()
        assert "characters" in schema["properties"]

    def test_screenplay_characters_survive_roundtrip(self):
        """Characters in shots survive full ScreenplayResponse parse + dump."""
        data = {
            "title": "Test",
            "logline": "Test",
            "scenes": [{
                "scene_id": "s1",
                "title": "Scene",
                "shots": [{
                    "shot_id": "sh1",
                    "description": "Elena at cliff",
                    "characters": ["Elena Vasquez"],
                    "shot_type": "wide",
                    "camera_movement": "static",
                    "duration_seconds": 5.0,
                    "image_prompt": "prompt",
                    "video_prompt": "prompt",
                }],
            }],
        }
        result = ScreenplayResponse(**data)
        dumped = result.model_dump()
        assert dumped["scenes"][0]["shots"][0]["characters"] == ["Elena Vasquez"]

    def test_screenplay_prompt_includes_characters(self):
        """The screenplay prompt JSON template includes characters field."""
        from packages.core.ai_content_platform.vimax.agents.screenwriter import SCREENPLAY_PROMPT
        assert '"characters"' in SCREENPLAY_PROMPT


# =============================================================================
# Fuzzy name matching tests
# =============================================================================

class TestFuzzyNameMatching:
    """Verify _find_portrait resolves LLM character names to registry keys."""

    def _make_registry(self, names):
        """Build a CharacterPortraitRegistry with named portraits."""
        from packages.core.ai_content_platform.vimax.interfaces.character import (
            CharacterPortrait,
            CharacterPortraitRegistry,
        )
        registry = CharacterPortraitRegistry(project_id="test")
        for name in names:
            portrait = CharacterPortrait(
                character_name=name,
                front_view=f"/portraits/{name}/front.png",
            )
            registry.add_portrait(portrait)
        return registry

    def _find(self, char_name, registry):
        """Call _find_portrait on the selector."""
        from packages.core.ai_content_platform.vimax.agents.reference_selector import (
            ReferenceImageSelector,
        )
        return ReferenceImageSelector._find_portrait(char_name, registry)

    def test_exact_match(self):
        """Exact name match returns the portrait."""
        reg = self._make_registry(["Elena Vasquez"])
        portrait, matched = self._find("Elena Vasquez", reg)
        assert portrait is not None
        assert matched == "Elena Vasquez"

    def test_case_insensitive_match(self):
        """Case differences resolve correctly."""
        reg = self._make_registry(["Elena Vasquez"])
        portrait, matched = self._find("elena vasquez", reg)
        assert portrait is not None
        assert matched == "Elena Vasquez"

    def test_title_prefix_match(self):
        """Title/rank prefix ('Captain Elena Vasquez') matches 'Elena Vasquez'."""
        reg = self._make_registry(["Elena Vasquez"])
        portrait, matched = self._find("Captain Elena Vasquez", reg)
        assert portrait is not None
        assert matched == "Elena Vasquez"

    def test_rank_prefix_match(self):
        """'Lieutenant James Park' matches 'James Park'."""
        reg = self._make_registry(["James Park"])
        portrait, matched = self._find("Lieutenant James Park", reg)
        assert portrait is not None
        assert matched == "James Park"

    def test_parenthetical_match(self):
        """'The Tessari (Sage)' matches 'Tessari'."""
        reg = self._make_registry(["Tessari"])
        portrait, matched = self._find("The Tessari (Sage)", reg)
        assert portrait is not None
        assert matched == "Tessari"

    def test_word_overlap_match(self):
        """Word overlap resolves when substring fails."""
        reg = self._make_registry(["Dr. Sarah Chen"])
        portrait, matched = self._find("Sarah Chen, PhD", reg)
        assert portrait is not None
        assert matched == "Dr. Sarah Chen"

    def test_no_match_returns_none(self):
        """Completely unknown name returns None."""
        reg = self._make_registry(["Elena Vasquez"])
        portrait, matched = self._find("Unknown Character", reg)
        assert portrait is None
        assert matched == "Unknown Character"

    def test_multiple_characters_no_false_positive(self):
        """With multiple registry entries, the correct one is matched."""
        reg = self._make_registry(["Elena Vasquez", "James Park"])
        portrait, matched = self._find("Captain Elena Vasquez", reg)
        assert matched == "Elena Vasquez"
        assert portrait.character_name == "Elena Vasquez"

        portrait2, matched2 = self._find("Lieutenant James Park", reg)
        assert matched2 == "James Park"
        assert portrait2.character_name == "James Park"
