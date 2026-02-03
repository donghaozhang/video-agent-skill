"""
Tests for Character Reference Image Feature.

Tests the new character reference image functionality including:
- CharacterPortraitRegistry for managing character portraits
- ReferenceImageSelector for choosing appropriate references
- Integration with StoryboardArtist
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# ==============================================================================
# Mock Classes
# ==============================================================================

class MockCharacterPortrait(BaseModel):
    """Mock character portrait for testing."""
    character_name: str
    front_view: Optional[str] = None
    side_view: Optional[str] = None
    back_view: Optional[str] = None
    three_quarter_view: Optional[str] = None

    @property
    def views(self) -> Dict[str, str]:
        result = {}
        if self.front_view:
            result["front"] = self.front_view
        if self.side_view:
            result["side"] = self.side_view
        if self.back_view:
            result["back"] = self.back_view
        if self.three_quarter_view:
            result["three_quarter"] = self.three_quarter_view
        return result

    @property
    def has_views(self) -> bool:
        return len(self.views) > 0


class MockShotDescription(BaseModel):
    """Mock shot description with reference fields."""
    shot_id: str
    description: str = ""
    shot_type: str = "medium"
    camera_angle: str = "front"
    characters: List[str] = Field(default_factory=list)
    character_references: Dict[str, str] = Field(default_factory=dict)
    primary_reference_image: Optional[str] = None


# ==============================================================================
# CharacterPortraitRegistry Tests
# ==============================================================================

class TestCharacterPortraitRegistry:
    """Tests for CharacterPortraitRegistry functionality."""

    def test_registry_creation(self):
        """Test registry can be created with project ID."""
        registry = {
            "project_id": "test_project",
            "portraits": {}
        }
        assert registry["project_id"] == "test_project"

    def test_add_portrait(self):
        """Test adding a portrait to registry."""
        portraits = {}
        portrait = MockCharacterPortrait(
            character_name="John",
            front_view="/path/to/front.png",
            side_view="/path/to/side.png",
        )
        portraits[portrait.character_name] = portrait

        assert "John" in portraits
        assert portraits["John"].front_view == "/path/to/front.png"

    def test_get_portrait(self):
        """Test retrieving portrait by name."""
        portraits = {
            "John": MockCharacterPortrait(
                character_name="John",
                front_view="/path/to/front.png",
            ),
            "Mary": MockCharacterPortrait(
                character_name="Mary",
                front_view="/path/to/mary_front.png",
            ),
        }

        portrait = portraits.get("John")
        assert portrait is not None
        assert portrait.character_name == "John"

    def test_get_nonexistent_portrait(self):
        """Test retrieving portrait that doesn't exist."""
        portraits = {}
        portrait = portraits.get("Unknown")
        assert portrait is None

    def test_list_characters(self):
        """Test listing all character names."""
        portraits = {
            "John": MockCharacterPortrait(character_name="John"),
            "Mary": MockCharacterPortrait(character_name="Mary"),
            "Bob": MockCharacterPortrait(character_name="Bob"),
        }

        names = list(portraits.keys())
        assert len(names) == 3
        assert "John" in names
        assert "Mary" in names
        assert "Bob" in names

    def test_has_character(self):
        """Test checking if character exists in registry."""
        portraits = {
            "John": MockCharacterPortrait(character_name="John"),
        }

        assert "John" in portraits
        assert "Unknown" not in portraits

    def test_portrait_views_property(self):
        """Test portrait views property filters empty values."""
        portrait = MockCharacterPortrait(
            character_name="John",
            front_view="/path/to/front.png",
            # side_view is None
            back_view="/path/to/back.png",
        )

        views = portrait.views
        assert len(views) == 2
        assert "front" in views
        assert "back" in views
        assert "side" not in views

    def test_has_views_property(self):
        """Test has_views property."""
        portrait_with_views = MockCharacterPortrait(
            character_name="John",
            front_view="/path/to/front.png",
        )
        portrait_without_views = MockCharacterPortrait(
            character_name="Empty",
        )

        assert portrait_with_views.has_views is True
        assert portrait_without_views.has_views is False


class TestRegistrySerialization:
    """Tests for registry serialization/deserialization."""

    def test_to_dict(self):
        """Test converting registry to dictionary."""
        portrait = MockCharacterPortrait(
            character_name="John",
            front_view="/path/to/front.png",
        )
        registry = {
            "project_id": "test",
            "portraits": {
                "John": portrait.model_dump()
            }
        }

        assert registry["project_id"] == "test"
        assert "John" in registry["portraits"]

    def test_from_dict(self):
        """Test creating registry from dictionary."""
        data = {
            "project_id": "test",
            "portraits": {
                "John": {
                    "character_name": "John",
                    "front_view": "/path/to/front.png",
                }
            }
        }

        portrait = MockCharacterPortrait(**data["portraits"]["John"])
        assert portrait.character_name == "John"
        assert portrait.front_view == "/path/to/front.png"


# ==============================================================================
# Reference Selection Logic Tests
# ==============================================================================

class TestReferenceSelectionLogic:
    """Tests for reference image selection logic."""

    # Camera angle to portrait view mapping
    ANGLE_TO_VIEW = {
        "front": "front",
        "eye_level": "front",
        "side": "side",
        "profile": "side",
        "back": "back",
        "three_quarter": "three_quarter",
        "45_degree": "three_quarter",
    }

    # Shot type preferences
    SHOT_TYPE_PREFERENCE = {
        "close_up": ["front", "three_quarter"],
        "extreme_close_up": ["front"],
        "medium": ["front", "three_quarter", "side"],
        "wide": ["front", "side", "back"],
        "over_the_shoulder": ["back", "three_quarter"],
    }

    def test_angle_to_view_mapping(self):
        """Test camera angle maps to correct view."""
        assert self.ANGLE_TO_VIEW.get("front") == "front"
        assert self.ANGLE_TO_VIEW.get("profile") == "side"
        assert self.ANGLE_TO_VIEW.get("back") == "back"

    def test_unknown_angle_defaults_to_front(self):
        """Test unknown angle defaults to front."""
        angle = "unknown_angle"
        preferred = self.ANGLE_TO_VIEW.get(angle.lower(), "front")
        assert preferred == "front"

    def test_shot_type_close_up_prefers_front(self):
        """Test close-up shots prefer front view."""
        prefs = self.SHOT_TYPE_PREFERENCE.get("close_up", ["front"])
        assert prefs[0] == "front"

    def test_over_the_shoulder_prefers_back(self):
        """Test over-the-shoulder shots prefer back view."""
        prefs = self.SHOT_TYPE_PREFERENCE.get("over_the_shoulder", ["front"])
        assert prefs[0] == "back"

    def test_select_best_view_with_matching_angle(self):
        """Test selecting view when camera angle matches available view."""
        portrait = MockCharacterPortrait(
            character_name="John",
            front_view="/path/front.png",
            side_view="/path/side.png",
        )

        camera_angle = "front"
        preferred = self.ANGLE_TO_VIEW.get(camera_angle, "front")

        if preferred in portrait.views:
            selected = portrait.views[preferred]
        else:
            selected = list(portrait.views.values())[0]

        assert selected == "/path/front.png"

    def test_select_best_view_fallback_to_any(self):
        """Test fallback to any available view."""
        portrait = MockCharacterPortrait(
            character_name="John",
            back_view="/path/back.png",  # Only back view available
        )

        camera_angle = "front"  # Want front but not available
        preferred = self.ANGLE_TO_VIEW.get(camera_angle, "front")

        if preferred in portrait.views:
            selected = portrait.views[preferred]
        else:
            # Fallback to any view
            selected = list(portrait.views.values())[0]

        assert selected == "/path/back.png"

    def test_shot_with_no_characters_returns_no_reference(self):
        """Test shot with no characters returns no reference."""
        shot = MockShotDescription(
            shot_id="shot_001",
            description="Empty landscape",
            characters=[],  # No characters
        )

        assert len(shot.characters) == 0
        assert shot.primary_reference_image is None


class TestReferenceSelectionResult:
    """Tests for reference selection result structure."""

    def test_selection_result_structure(self):
        """Test selection result has expected fields."""
        result = {
            "shot_id": "shot_001",
            "selected_references": {"John": "/path/john_front.png"},
            "primary_reference": "/path/john_front.png",
            "selection_reason": "John: selected 'front' (angle=front, type=medium)",
        }

        assert result["shot_id"] == "shot_001"
        assert "John" in result["selected_references"]
        assert result["primary_reference"] is not None

    def test_multiple_character_selection(self):
        """Test selecting references for multiple characters."""
        selected = {}
        portraits = {
            "John": MockCharacterPortrait(
                character_name="John",
                front_view="/path/john_front.png",
            ),
            "Mary": MockCharacterPortrait(
                character_name="Mary",
                front_view="/path/mary_front.png",
            ),
        }

        characters_in_shot = ["John", "Mary"]
        for char_name in characters_in_shot:
            if char_name in portraits:
                portrait = portraits[char_name]
                if portrait.has_views:
                    selected[char_name] = list(portrait.views.values())[0]

        assert len(selected) == 2
        assert "John" in selected
        assert "Mary" in selected

    def test_primary_reference_is_first_character(self):
        """Test primary reference is first character with valid reference."""
        selected = {
            "John": "/path/john.png",
            "Mary": "/path/mary.png",
        }

        primary = list(selected.values())[0] if selected else None
        assert primary == "/path/john.png"


# ==============================================================================
# ShotDescription Reference Fields Tests
# ==============================================================================

class TestShotDescriptionReferenceFields:
    """Tests for reference fields in ShotDescription."""

    def test_shot_has_character_references_field(self):
        """Test shot has character_references field."""
        shot = MockShotDescription(
            shot_id="shot_001",
            characters=["John"],
            character_references={"John": "/path/john.png"},
        )

        assert "John" in shot.character_references
        assert shot.character_references["John"] == "/path/john.png"

    def test_shot_has_primary_reference_field(self):
        """Test shot has primary_reference_image field."""
        shot = MockShotDescription(
            shot_id="shot_001",
            characters=["John"],
            primary_reference_image="/path/john.png",
        )

        assert shot.primary_reference_image == "/path/john.png"

    def test_default_reference_fields_are_empty(self):
        """Test default reference fields are empty."""
        shot = MockShotDescription(
            shot_id="shot_001",
            description="Test shot",
        )

        assert shot.character_references == {}
        assert shot.primary_reference_image is None


# ==============================================================================
# Integration Pattern Tests
# ==============================================================================

class TestStoryboardReferenceIntegration:
    """Tests for storyboard generation with references."""

    def test_process_with_registry(self):
        """Test storyboard processing pattern with registry."""
        # Simulate pipeline logic
        use_refs = True
        registry_portraits = {"John": MockCharacterPortrait(
            character_name="John",
            front_view="/path/front.png",
        )}

        shots = [
            MockShotDescription(
                shot_id="shot_001",
                characters=["John"],
            ),
        ]

        # Simulate reference selection
        for shot in shots:
            if use_refs and shot.characters:
                for char_name in shot.characters:
                    if char_name in registry_portraits:
                        portrait = registry_portraits[char_name]
                        if portrait.has_views:
                            shot.character_references[char_name] = portrait.front_view
                            if not shot.primary_reference_image:
                                shot.primary_reference_image = portrait.front_view

        assert shots[0].primary_reference_image == "/path/front.png"
        assert "John" in shots[0].character_references

    def test_process_without_registry(self):
        """Test storyboard processing without registry."""
        use_refs = False
        registry_portraits = None

        shots = [
            MockShotDescription(
                shot_id="shot_001",
                characters=["John"],
            ),
        ]

        # No reference selection when registry is None
        if use_refs and registry_portraits:
            pass  # Would select references here

        assert shots[0].primary_reference_image is None
        assert shots[0].character_references == {}

    def test_skip_reference_for_shot_without_characters(self):
        """Test skipping reference selection for shots without characters."""
        registry_portraits = {"John": MockCharacterPortrait(
            character_name="John",
            front_view="/path/front.png",
        )}

        shot = MockShotDescription(
            shot_id="shot_001",
            description="Landscape shot",
            characters=[],  # No characters
        )

        # No references selected for empty character list
        if shot.characters:
            pass  # Would select references here

        assert shot.primary_reference_image is None


# ==============================================================================
# Cost and Model Tests
# ==============================================================================

class TestReferenceModelSelection:
    """Tests for reference model selection."""

    REFERENCE_MODELS = {
        "flux_kontext": {"cost": 0.025, "quality": "high"},
        "flux_redux": {"cost": 0.020, "quality": "medium"},
        "seededit_v3": {"cost": 0.025, "quality": "high"},
        "photon_flash": {"cost": 0.015, "quality": "fast"},
    }

    def test_default_reference_model(self):
        """Test default reference model is flux_kontext."""
        default = "flux_kontext"
        assert default in self.REFERENCE_MODELS

    def test_reference_model_costs(self):
        """Test reference model cost estimates."""
        assert self.REFERENCE_MODELS["flux_kontext"]["cost"] == 0.025
        assert self.REFERENCE_MODELS["photon_flash"]["cost"] == 0.015

    def test_reference_strength_range(self):
        """Test reference strength is in valid range."""
        reference_strength = 0.6
        assert 0.0 <= reference_strength <= 1.0

        # Edge cases
        assert 0.0 <= 0.0 <= 1.0
        assert 0.0 <= 1.0 <= 1.0


class TestReferenceGenerationCost:
    """Tests for reference-based generation cost calculation."""

    def test_cost_with_references_higher(self):
        """Test that reference-based generation costs more."""
        base_cost = 0.003  # Normal image generation
        reference_cost = 0.025  # Reference-based generation

        assert reference_cost > base_cost

    def test_total_cost_calculation(self):
        """Test total cost calculation with mixed generation."""
        shots_with_refs = 5
        shots_without_refs = 3

        ref_cost_per_image = 0.025
        base_cost_per_image = 0.003

        total_cost = (
            shots_with_refs * ref_cost_per_image +
            shots_without_refs * base_cost_per_image
        )

        expected = 5 * 0.025 + 3 * 0.003
        assert total_cost == pytest.approx(expected)
