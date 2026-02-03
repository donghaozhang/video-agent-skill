"""
Tests for ViMax interface models.
"""

import pytest
import sys
import os
import importlib.util


def load_module_directly(module_path: str, module_name: str):
    """Load a module directly from file path without going through package imports."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Get paths
vimax_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages', 'core', 'ai_content_platform', 'vimax')
interfaces_path = os.path.join(vimax_path, 'interfaces')

# Load interface modules directly
character_mod = load_module_directly(
    os.path.join(interfaces_path, 'character.py'),
    'vimax_interfaces_character'
)
shot_mod = load_module_directly(
    os.path.join(interfaces_path, 'shot.py'),
    'vimax_interfaces_shot'
)
output_mod = load_module_directly(
    os.path.join(interfaces_path, 'output.py'),
    'vimax_interfaces_output'
)

# Get classes
CharacterInNovel = character_mod.CharacterInNovel
CharacterInScene = character_mod.CharacterInScene
CharacterPortrait = character_mod.CharacterPortrait
ShotDescription = shot_mod.ShotDescription
ShotType = shot_mod.ShotType
Scene = shot_mod.Scene
Storyboard = shot_mod.Storyboard
ImageOutput = output_mod.ImageOutput
VideoOutput = output_mod.VideoOutput
PipelineOutput = output_mod.PipelineOutput


class TestCharacterModels:
    """Tests for character models."""

    def test_character_in_novel_creation(self, sample_character_data):
        """Test CharacterInNovel creation."""
        char = CharacterInNovel(**sample_character_data)
        assert char.name == "John"
        assert char.age == "25"

    def test_character_in_novel_defaults(self):
        """Test CharacterInNovel with minimal data."""
        char = CharacterInNovel(name="Test")
        assert char.name == "Test"
        assert char.description == ""
        assert char.relationships == []

    def test_character_portrait_views(self):
        """Test CharacterPortrait views property."""
        portrait = CharacterPortrait(
            character_name="John",
            front_view="/path/front.png",
            side_view="/path/side.png",
        )
        views = portrait.views
        assert "front" in views
        assert "side" in views
        assert "back" not in views

    def test_character_in_scene(self):
        """Test CharacterInScene creation."""
        char = CharacterInScene(
            name="John",
            scene_id="scene_001",
            action="walking",
            emotion="determined",
        )
        assert char.scene_id == "scene_001"
        assert char.action == "walking"


class TestShotModels:
    """Tests for shot models."""

    def test_shot_description_creation(self, sample_shot_data):
        """Test ShotDescription creation."""
        shot = ShotDescription(**sample_shot_data)
        assert shot.shot_id == "shot_001"
        assert shot.shot_type == ShotType.MEDIUM

    def test_shot_type_enum(self):
        """Test ShotType enum values."""
        assert ShotType.WIDE.value == "wide"
        assert ShotType.CLOSE_UP.value == "close_up"

    def test_scene_properties(self):
        """Test Scene properties."""
        scene = Scene(
            scene_id="scene_001",
            title="Opening",
            shots=[
                ShotDescription(shot_id="s1", description="Shot 1", duration_seconds=5),
                ShotDescription(shot_id="s2", description="Shot 2", duration_seconds=3),
            ]
        )
        assert scene.shot_count == 2
        assert scene.total_duration == 8.0

    def test_storyboard_properties(self):
        """Test Storyboard properties."""
        storyboard = Storyboard(
            title="Test Storyboard",
            scenes=[
                Scene(
                    scene_id="s1",
                    shots=[ShotDescription(shot_id="shot1", description="Shot 1")]
                ),
                Scene(
                    scene_id="s2",
                    shots=[
                        ShotDescription(shot_id="shot2", description="Shot 2"),
                        ShotDescription(shot_id="shot3", description="Shot 3"),
                    ]
                ),
            ]
        )
        assert storyboard.total_shots == 3


class TestOutputModels:
    """Tests for output models."""

    def test_image_output(self):
        """Test ImageOutput creation."""
        output = ImageOutput(
            image_path="/tmp/test.png",
            prompt="Test prompt",
            model="flux_dev",
            cost=0.003,
        )
        assert output.cost == 0.003
        assert output.model == "flux_dev"

    def test_video_output(self):
        """Test VideoOutput creation."""
        output = VideoOutput(
            video_path="/tmp/test.mp4",
            duration=5.0,
            model="kling",
        )
        assert output.duration == 5.0

    def test_pipeline_output_success(self):
        """Test PipelineOutput success property."""
        output = PipelineOutput(
            pipeline_name="test",
            final_video=VideoOutput(video_path="/tmp/test.mp4"),
        )
        assert output.success is True

    def test_pipeline_output_failure(self):
        """Test PipelineOutput failure."""
        output = PipelineOutput(
            pipeline_name="test",
            errors=["Something went wrong"],
        )
        assert output.success is False

    def test_pipeline_output_add_image(self):
        """Test adding images to pipeline output."""
        output = PipelineOutput(pipeline_name="test")
        output.add_image(ImageOutput(image_path="/tmp/1.png", cost=0.003))
        output.add_image(ImageOutput(image_path="/tmp/2.png", cost=0.003))
        assert len(output.images) == 2
        assert output.total_cost == 0.006
