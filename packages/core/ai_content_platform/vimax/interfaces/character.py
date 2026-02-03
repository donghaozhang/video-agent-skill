"""
Character data models for ViMax pipeline.

Handles character information at different levels:
- CharacterInNovel: Full character description from novel
- CharacterInScene: Character appearance in a scene
- CharacterInEvent: Character involvement in an event
- CharacterPortraitRegistry: Registry for storing character portraits
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict


class CharacterBase(BaseModel):
    """Base character model with common fields."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Character name")
    description: str = Field(default="", description="Character description")


class CharacterInNovel(CharacterBase):
    """Full character description extracted from novel."""

    age: Optional[str] = Field(default=None, description="Character age or age range")
    gender: Optional[str] = Field(default=None, description="Character gender")
    appearance: str = Field(default="", description="Physical appearance description")
    personality: str = Field(default="", description="Personality traits")
    role: str = Field(default="", description="Role in the story (protagonist, antagonist, etc.)")
    relationships: List[str] = Field(default_factory=list, description="Relationships with other characters")


class CharacterInScene(CharacterBase):
    """Character appearance in a specific scene."""

    scene_id: Optional[str] = Field(default=None, description="Scene identifier")
    position: Optional[str] = Field(default=None, description="Position in scene")
    action: str = Field(default="", description="What the character is doing")
    emotion: str = Field(default="", description="Emotional state")
    dialogue: Optional[str] = Field(default=None, description="Character dialogue")


class CharacterInEvent(CharacterBase):
    """Character involvement in a specific event."""

    event_id: Optional[str] = Field(default=None, description="Event identifier")
    involvement: str = Field(default="", description="How character is involved")
    importance: int = Field(default=1, ge=1, le=5, description="Importance level 1-5")


class CharacterPortrait(BaseModel):
    """Generated character portrait with multiple angles."""

    character_name: str
    front_view: Optional[str] = Field(default=None, description="Path to front view image")
    side_view: Optional[str] = Field(default=None, description="Path to side view image")
    back_view: Optional[str] = Field(default=None, description="Path to back view image")
    three_quarter_view: Optional[str] = Field(default=None, description="Path to 3/4 view image")

    @property
    def views(self) -> dict:
        """Return all available views as dict."""
        return {
            k: v for k, v in {
                "front": self.front_view,
                "side": self.side_view,
                "back": self.back_view,
                "three_quarter": self.three_quarter_view,
            }.items() if v is not None
        }

    @property
    def has_views(self) -> bool:
        """Check if any views are available."""
        return len(self.views) > 0

    def get_view(self, view_name: str) -> Optional[str]:
        """Get a specific view by name."""
        return self.views.get(view_name)


class CharacterPortraitRegistry(BaseModel):
    """
    Registry of all character portraits for a project.

    Stores and indexes character portraits for easy retrieval
    during storyboard generation.
    """

    project_id: str = Field(..., description="Unique project identifier")
    portraits: Dict[str, CharacterPortrait] = Field(
        default_factory=dict,
        description="Map of character name to portrait"
    )

    # Camera angle to portrait view mapping
    ANGLE_TO_VIEW: Dict[str, str] = {
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

    def add_portrait(self, portrait: CharacterPortrait) -> None:
        """Add a portrait to the registry."""
        self.portraits[portrait.character_name] = portrait

    def get_portrait(self, name: str) -> Optional[CharacterPortrait]:
        """Get portrait by character name."""
        return self.portraits.get(name)

    def get_best_view(self, name: str, camera_angle: str) -> Optional[str]:
        """
        Get best view image path based on camera angle.

        Args:
            name: Character name
            camera_angle: Camera angle (e.g., "front", "side", "profile")

        Returns:
            Path to the best matching portrait view, or None if not found
        """
        portrait = self.get_portrait(name)
        if not portrait:
            return None

        # Get preferred view from camera angle
        preferred_view = self.ANGLE_TO_VIEW.get(camera_angle.lower(), "front")

        # Get available views
        views = portrait.views

        # Try preferred view first
        if preferred_view in views:
            return views[preferred_view]

        # Fall back to front view if available
        if "front" in views:
            return views["front"]

        # Last resort: any available view
        return next(iter(views.values()), None)

    def list_characters(self) -> List[str]:
        """List all character names in the registry."""
        return list(self.portraits.keys())

    def has_character(self, name: str) -> bool:
        """Check if a character exists in the registry."""
        return name in self.portraits

    def to_dict(self) -> dict:
        """Serialize registry to dict for JSON storage."""
        return {
            "project_id": self.project_id,
            "portraits": {
                name: portrait.model_dump()
                for name, portrait in self.portraits.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterPortraitRegistry":
        """Deserialize registry from dict."""
        if "project_id" not in data:
            raise ValueError("Registry data must contain 'project_id'")
        portraits = {
            name: CharacterPortrait(**portrait_data)
            for name, portrait_data in data.get("portraits", {}).items()
        }
        return cls(
            project_id=data["project_id"],
            portraits=portraits,
        )
