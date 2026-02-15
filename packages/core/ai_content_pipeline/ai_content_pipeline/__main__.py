#!/usr/bin/env python3
"""
AI Content Pipeline CLI Interface

Allows running the module directly from command line:
    python -m ai_content_pipeline [command] [options]
"""

import sys

# Reason: Windows defaults to cp1252 which can't encode emoji characters
# used throughout the codebase. Force UTF-8 so print() calls don't crash.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from .cli.click_app import cli


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
