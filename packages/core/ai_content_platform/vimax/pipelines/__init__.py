"""
ViMax Pipelines

End-to-end content generation workflows.
"""

from .idea2video import (
    Idea2VideoPipeline,
    Idea2VideoConfig,
    Idea2VideoResult,
    create_pipeline,
)
from .script2video import (
    Script2VideoPipeline,
    Script2VideoConfig,
    Script2VideoResult,
)
from .novel2movie import (
    Novel2MoviePipeline,
    Novel2MovieConfig,
    Novel2MovieResult,
    ChapterSummary,
)

__all__ = [
    # Idea2Video
    "Idea2VideoPipeline",
    "Idea2VideoConfig",
    "Idea2VideoResult",
    "create_pipeline",
    # Script2Video
    "Script2VideoPipeline",
    "Script2VideoConfig",
    "Script2VideoResult",
    # Novel2Movie
    "Novel2MoviePipeline",
    "Novel2MovieConfig",
    "Novel2MovieResult",
    "ChapterSummary",
]
