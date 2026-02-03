"""
ViMax CLI Commands

Command-line interface for ViMax pipelines.
"""

from .commands import vimax, register_commands

__all__ = ["vimax", "register_commands"]
