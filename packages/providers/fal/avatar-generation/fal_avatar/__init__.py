"""FAL Avatar Generation Package.

This package provides unified access to FAL avatar and video generation models:
- OmniHuman v1.5 - Audio-driven human animation
- VEED Fabric 1.0 - Lipsync video generation
- VEED Fabric 1.0 Text - Text-to-speech avatar
- Kling O1 Reference-to-Video - Character consistency
- Kling O1 V2V Reference - Style-guided video
- Kling O1 V2V Edit - Targeted video modifications
"""

from .generator import FALAvatarGenerator
from .models import (
    BaseAvatarModel,
    AvatarGenerationResult,
    OmniHumanModel,
    FabricModel,
    FabricTextModel,
    KlingRefToVideoModel,
    KlingV2VReferenceModel,
    KlingV2VEditModel,
)

__all__ = [
    "FALAvatarGenerator",
    "BaseAvatarModel",
    "AvatarGenerationResult",
    "OmniHumanModel",
    "FabricModel",
    "FabricTextModel",
    "KlingRefToVideoModel",
    "KlingV2VReferenceModel",
    "KlingV2VEditModel",
]

__version__ = "1.0.0"
