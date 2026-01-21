"""FAL Avatar model exports."""

from .base import BaseAvatarModel, AvatarGenerationResult
from .omnihuman import OmniHumanModel
from .fabric import FabricModel, FabricTextModel
from .kling import KlingRefToVideoModel, KlingV2VReferenceModel, KlingV2VEditModel
from .multitalk import MultiTalkModel

__all__ = [
    "BaseAvatarModel",
    "AvatarGenerationResult",
    "OmniHumanModel",
    "FabricModel",
    "FabricTextModel",
    "KlingRefToVideoModel",
    "KlingV2VReferenceModel",
    "KlingV2VEditModel",
    "MultiTalkModel",
]
