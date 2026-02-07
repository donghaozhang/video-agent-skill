#!/usr/bin/env python3
"""PyInstaller entry point for the aicp binary.

This wrapper exists because __main__.py uses relative imports
which require a package context. PyInstaller runs the entry script
as a top-level module, so relative imports fail. This script
imports from the installed package instead.
"""

from ai_content_pipeline.__main__ import main

main()
