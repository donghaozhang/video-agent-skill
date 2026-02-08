"""
ViMax CLI Commands

Click subgroup registered under the main ``aicp`` CLI.
Usage: ``aicp vimax <command>``.
"""

from .commands import vimax, register_commands

__all__ = ["vimax", "register_commands"]
