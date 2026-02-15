"""
CLI command registration hub.

Each module registers its commands with the root Click group.
"""

from .pipeline import register_pipeline_commands
from .media import register_media_commands
from .motion import register_motion_commands
from .audio import register_audio_commands
from .imaging import register_imaging_commands
from .project import register_project_commands
from .keys import register_key_commands


def register_all_commands(cli):
    """Register all command groups with the root CLI group."""
    register_pipeline_commands(cli)
    register_media_commands(cli)
    register_motion_commands(cli)
    register_audio_commands(cli)
    register_imaging_commands(cli)
    register_project_commands(cli)
    register_key_commands(cli)
