"""
Character data models for ViMax pipeline.

Handles character information at different levels:
- CharacterInNovel: Full character description from novel
- CharacterInScene: Character appearance in a scene
- CharacterInEvent: Character involvement in an event
"""

from typing import Optional, List
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
