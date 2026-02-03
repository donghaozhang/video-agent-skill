"""
Screenwriter Agent

Generates screenplay/script content from ideas, outlines, or stories.
Produces structured scripts with scenes, dialogue, and action descriptions.
"""

from typing import Optional, List
import logging
import json
import re

from pydantic import BaseModel, Field

from .base import BaseAgent, AgentConfig, AgentResult
from ..adapters import LLMAdapter, LLMAdapterConfig, Message
from ..interfaces import Scene, ShotDescription, ShotType, CameraMovement


class Script(BaseModel):
    """Generated script structure."""

    title: str
    logline: str = ""  # One-sentence summary
    scenes: List[Scene] = Field(default_factory=list)
    total_duration: float = 0.0

    @property
    def scene_count(self) -> int:
        """Return the number of scenes in the script.

        Returns:
            int: The count of scenes.
        """
        return len(self.scenes)


class ScreenwriterConfig(AgentConfig):
    """Configuration for Screenwriter."""

    name: str = "Screenwriter"
    model: str = "kimi-k2.5"  # Default: Kimi K2.5
    target_duration: float = 60.0  # Target video duration in seconds
    shots_per_scene: int = 3
    style: str = "cinematic, visually descriptive"


SCREENPLAY_PROMPT = """You are an expert screenwriter specializing in visual storytelling for AI video generation.

Create a detailed screenplay from this idea:
{idea}

Requirements:
- Target duration: {duration} seconds
- Style: {style}
- Number of scenes: {num_scenes}
- Shots per scene: {shots_per_scene}

For each scene, provide:
1. Scene title and location
2. Time of day and lighting
3. Multiple shots with:
   - Shot type (wide, medium, close_up, etc.)
   - Visual description (what we SEE)
   - Camera movement if any
   - Duration in seconds

Format your response as JSON with this structure:
{{
    "title": "Video Title",
    "logline": "One sentence summary",
    "scenes": [
        {{
            "scene_id": "scene_001",
            "title": "Scene Title",
            "location": "Location description",
            "time": "Time of day",
            "shots": [
                {{
                    "shot_id": "shot_001",
                    "shot_type": "wide",
                    "description": "Visual description",
                    "camera_movement": "static",
                    "duration_seconds": 5,
                    "image_prompt": "Detailed prompt for image generation",
                    "video_prompt": "Motion/animation description"
                }}
            ]
        }}
    ]
}}

Focus on VISUAL descriptions - what the camera sees, not dialogue or internal thoughts.
Each image_prompt should be detailed enough for AI image generation.
Each video_prompt should describe the motion/animation for that shot."""


class Screenwriter(BaseAgent[str, Script]):
    """
    Agent that generates screenplays from ideas.

    Usage:
        writer = Screenwriter()
        result = await writer.process("A samurai's journey at sunrise")
        if result.success:
            script = result.result
            for scene in script.scenes:
                print(f"Scene: {scene.title}")
    """

    def __init__(self, config: Optional[ScreenwriterConfig] = None):
        """Initialize the Screenwriter.

        Args:
            config: Optional configuration overriding defaults.

        Returns:
            None

        Cost:
            None. Initialization does not call external services.

        Example:
            >>> writer = Screenwriter()
        """
        super().__init__(config or ScreenwriterConfig())
        self.config: ScreenwriterConfig = self.config
        self._llm: Optional[LLMAdapter] = None
        self.logger = logging.getLogger("vimax.agents.screenwriter")

    async def _ensure_llm(self):
        """Initialize the LLM adapter lazily.

        Args:
            None

        Returns:
            None

        Cost:
            None. Adapter initialization does not perform LLM inference.

        Example:
            >>> await writer._ensure_llm()
        """
        if self._llm is None:
            self._llm = LLMAdapter(LLMAdapterConfig(model=self.config.model))
            await self._llm.initialize()

    async def process(self, idea: str) -> AgentResult[Script]:
        """
        Generate screenplay from idea.

        Args:
            idea: Story idea or concept

        Returns:
            AgentResult containing generated Script

        Cost:
            One LLM chat call. Billed according to the configured provider/model.

        Example:
            >>> writer = Screenwriter()
            >>> result = await writer.process("A samurai's journey at sunrise")
            >>> result.success
            True
        """
        await self._ensure_llm()

        self.logger.info(f"Generating screenplay for: {idea[:100]}...")

        try:
            # Validate config values to prevent ZeroDivisionError
            if self.config.target_duration <= 0:
                raise ValueError(f"target_duration must be > 0, got {self.config.target_duration}")
            if self.config.shots_per_scene <= 0:
                raise ValueError(f"shots_per_scene must be > 0, got {self.config.shots_per_scene}")

            # Calculate scene count based on target duration
            avg_shot_duration = 5.0
            total_shots = self.config.target_duration / avg_shot_duration
            num_scenes = max(1, int(total_shots / self.config.shots_per_scene))

            prompt = SCREENPLAY_PROMPT.format(
                idea=idea,
                duration=self.config.target_duration,
                style=self.config.style,
                num_scenes=num_scenes,
                shots_per_scene=self.config.shots_per_scene,
            )

            response = await self._llm.chat(
                [Message(role="user", content=prompt)],
                temperature=0.7,
            )

            # Parse response
            content = response.content
            # Extract JSON from response - first try code fence, then raw JSON
            json_text = None
            fence_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if fence_match:
                json_text = fence_match.group(1)
            else:
                # Fall back to finding JSON object directly (greedy for nested objects)
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    json_text = match.group()

            if json_text:
                try:
                    data = json.loads(json_text)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in screenplay response: {e}") from e
            else:
                raise ValueError("Could not find JSON in screenplay response")

            # Build Script object
            scenes = []
            total_duration = 0.0

            for scene_data in data.get("scenes", []):
                shots = []
                for shot_data in scene_data.get("shots", []):
                    shot_type_str = shot_data.get("shot_type", "medium")
                    # Handle various shot type formats
                    try:
                        shot_type = ShotType(shot_type_str.lower().replace(" ", "_").replace("-", "_"))
                    except ValueError:
                        shot_type = ShotType.MEDIUM

                    # Handle various camera movement formats
                    camera_movement_str = shot_data.get("camera_movement", "static")
                    try:
                        # Normalize: "slow push in" -> "dolly", "push in" -> "dolly", etc.
                        cm_lower = camera_movement_str.lower().replace(" ", "_").replace("-", "_")
                        # Map common variations to valid enum values
                        cm_mapping = {
                            "push_in": "dolly", "push_out": "dolly", "slow_push_in": "dolly",
                            "pull_back": "dolly", "move_forward": "dolly", "move_back": "dolly",
                            "follow": "tracking", "track": "tracking",
                            "pan_left": "pan", "pan_right": "pan", "slow_pan": "pan",
                            "tilt_up": "tilt", "tilt_down": "tilt",
                            "zoom_in": "zoom", "zoom_out": "zoom",
                            "crane_up": "crane", "crane_down": "crane",
                            "steady": "static", "fixed": "static", "locked": "static",
                        }
                        if cm_lower in cm_mapping:
                            cm_lower = cm_mapping[cm_lower]
                        camera_movement = CameraMovement(cm_lower)
                    except ValueError:
                        camera_movement = CameraMovement.STATIC

                    shot = ShotDescription(
                        shot_id=shot_data.get("shot_id", f"shot_{len(shots)+1}"),
                        shot_type=shot_type,
                        description=shot_data.get("description", ""),
                        camera_movement=camera_movement,
                        duration_seconds=shot_data.get("duration_seconds", 5.0),
                        image_prompt=shot_data.get("image_prompt"),
                        video_prompt=shot_data.get("video_prompt"),
                    )
                    shots.append(shot)
                    total_duration += shot.duration_seconds

                scene = Scene(
                    scene_id=scene_data.get("scene_id", f"scene_{len(scenes)+1}"),
                    title=scene_data.get("title", ""),
                    description=scene_data.get("description", ""),
                    location=scene_data.get("location", ""),
                    time=scene_data.get("time", ""),
                    shots=shots,
                )
                scenes.append(scene)

            script = Script(
                title=data.get("title", "Untitled"),
                logline=data.get("logline", ""),
                scenes=scenes,
                total_duration=total_duration,
            )

            self.logger.info(
                f"Generated screenplay: {script.scene_count} scenes, "
                f"{sum(s.shot_count for s in script.scenes)} shots, "
                f"{total_duration:.1f}s total"
            )

            return AgentResult.ok(
                script,
                scene_count=script.scene_count,
                shot_count=sum(s.shot_count for s in script.scenes),
                duration=total_duration,
                cost=response.cost,
            )

        except Exception as e:
            self.logger.exception("Screenplay generation failed")
            return AgentResult.fail(str(e))
