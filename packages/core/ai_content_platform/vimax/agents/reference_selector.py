"""
Reference Image Selector Agent

Intelligently selects the best character reference image for each shot
based on camera angle, shot type, and visible characters.
"""

from typing import List, Optional, Dict
import logging

from pydantic import BaseModel, Field

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
    llm_model: str = "kimi-k2.5"  # For complex selections (future use)


class ReferenceSelectionResult(BaseModel):
    """Result of reference selection for a shot."""

    shot_id: str = Field(..., description="Shot identifier")
    selected_references: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of character name to selected image path"
    )
    primary_reference: Optional[str] = Field(
        default=None,
        description="Primary reference image for the shot"
    )
    selection_reason: str = Field(
        default="",
        description="Explanation of selection choices"
    )


class ReferenceImageSelector(BaseAgent[ShotDescription, ReferenceSelectionResult]):
    """
    Selects best reference images for shots.

    Selection Strategy:
    1. For each character in the shot, find their portrait
    2. Choose the view that best matches the camera angle
    3. For multiple characters, select primary based on importance/order

    Usage:
        selector = ReferenceImageSelector()
        result = await selector.select_for_shot(shot, registry)
        if result.primary_reference:
            print(f"Using reference: {result.primary_reference}")
    """

    # Camera angle to portrait view mapping
    ANGLE_TO_VIEW: Dict[str, str] = {
        "front": "front",
        "eye_level": "front",
        "straight_on": "front",
        "face_on": "front",
        "side": "side",
        "profile": "side",
        "left": "side",
        "right": "side",
        "back": "back",
        "behind": "back",
        "rear": "back",
        "three_quarter": "three_quarter",
        "45_degree": "three_quarter",
        "angled": "three_quarter",
    }

    # Shot type hints for view selection (preference order)
    SHOT_TYPE_PREFERENCE: Dict[str, List[str]] = {
        "close_up": ["front", "three_quarter"],
        "extreme_close_up": ["front"],
        "medium": ["front", "three_quarter", "side"],
        "wide": ["front", "side", "back"],
        "establishing": ["front", "side"],
        "over_the_shoulder": ["back", "three_quarter"],
        "two_shot": ["front", "three_quarter", "side"],
        "pov": [],  # No reference needed for POV shots
        "insert": [],  # No reference needed for insert shots
    }

    def __init__(self, config: Optional[ReferenceSelectorConfig] = None):
        super().__init__(config or ReferenceSelectorConfig())
        self.logger = logging.getLogger("vimax.agents.reference_selector")

    async def initialize(self) -> bool:
        """Initialize the agent (no external dependencies needed)."""
        return True

    async def process(self, shot: ShotDescription) -> AgentResult[ReferenceSelectionResult]:
        """
        Process is not used directly - use select_for_shot instead.

        This method exists for interface compatibility.
        """
        # Return empty result since we need registry for selection
        return AgentResult.ok(
            ReferenceSelectionResult(
                shot_id=shot.shot_id,
                selection_reason="Use select_for_shot() with registry for actual selection"
            )
        )

    async def select_for_shot(
        self,
        shot: ShotDescription,
        registry: CharacterPortraitRegistry,
    ) -> ReferenceSelectionResult:
        """
        Select best references for a single shot.

        Args:
            shot: Shot description with character list
            registry: Portrait registry with available portraits

        Returns:
            ReferenceSelectionResult with selected images
        """
        selected: Dict[str, str] = {}
        reasons: List[str] = []

        self.logger.debug(
            f"Selecting references for shot {shot.shot_id} "
            f"with {len(shot.characters)} characters"
        )

        for char_name in shot.characters:
            portrait = registry.get_portrait(char_name)
            if not portrait:
                reasons.append(f"No portrait found for '{char_name}'")
                self.logger.warning(f"No portrait found for character: {char_name}")
                continue

            if not portrait.has_views:
                reasons.append(f"No views available for '{char_name}'")
                self.logger.warning(f"No views available for character: {char_name}")
                continue

            # Determine best view based on camera angle and shot type
            best_view = self._select_best_view(
                portrait=portrait,
                camera_angle=shot.camera_angle,
                shot_type=shot.shot_type.value,
            )

            if best_view:
                selected[char_name] = best_view
                reasons.append(
                    f"{char_name}: selected '{best_view}' "
                    f"(angle={shot.camera_angle}, type={shot.shot_type.value})"
                )
                self.logger.debug(f"Selected {best_view} for {char_name}")

        # Select primary reference (first character with valid reference)
        primary = list(selected.values())[0] if selected else None

        result = ReferenceSelectionResult(
            shot_id=shot.shot_id,
            selected_references=selected,
            primary_reference=primary,
            selection_reason="; ".join(reasons) if reasons else "No references selected",
        )

        self.logger.info(
            f"Shot {shot.shot_id}: selected {len(selected)} references, "
            f"primary={'yes' if primary else 'no'}"
        )

        return result

    async def select_for_shots(
        self,
        shots: List[ShotDescription],
        registry: CharacterPortraitRegistry,
    ) -> List[ReferenceSelectionResult]:
        """
        Select references for multiple shots.

        Args:
            shots: List of shot descriptions
            registry: Portrait registry

        Returns:
            List of selection results, one per shot
        """
        results = []
        for shot in shots:
            result = await self.select_for_shot(shot, registry)
            results.append(result)
        return results

    def _select_best_view(
        self,
        portrait: CharacterPortrait,
        camera_angle: str,
        shot_type: str,
    ) -> Optional[str]:
        """
        Select best portrait view for camera settings.

        Args:
            portrait: Character portrait with available views
            camera_angle: Camera angle (e.g., "front", "profile")
            shot_type: Shot type (e.g., "close_up", "medium")

        Returns:
            Path to best matching view, or None if none available
        """
        views = portrait.views

        if not views:
            return None

        # Step 1: Try to match camera angle directly
        preferred_view = self.ANGLE_TO_VIEW.get(camera_angle.lower(), "front")
        if preferred_view in views:
            return views[preferred_view]

        # Step 2: Fall back to shot type preferences
        preferences = self.SHOT_TYPE_PREFERENCE.get(shot_type, ["front"])
        for pref in preferences:
            if pref in views:
                return views[pref]

        # Step 3: Last resort - any available view
        return next(iter(views.values()))

    def get_view_preference(self, camera_angle: str, shot_type: str) -> List[str]:
        """
        Get ordered list of preferred views for given settings.

        Useful for debugging or UI display.

        Args:
            camera_angle: Camera angle
            shot_type: Shot type

        Returns:
            Ordered list of preferred view names
        """
        preferred = self.ANGLE_TO_VIEW.get(camera_angle.lower(), "front")
        shot_prefs = self.SHOT_TYPE_PREFERENCE.get(shot_type, ["front"])

        # Combine: preferred view first, then shot type preferences
        result = [preferred]
        for pref in shot_prefs:
            if pref not in result:
                result.append(pref)

        return result
