#!/usr/bin/env python3
"""
AI Content Pipeline CLI Interface

Allows running the module directly from command line:
    python -m ai_content_pipeline [command] [options]
"""

from .cli.click_app import cli


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
