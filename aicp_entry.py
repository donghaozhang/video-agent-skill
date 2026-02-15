#!/usr/bin/env python3
"""PyInstaller entry point for the aicp binary.

This wrapper exists because __main__.py uses relative imports
which require a package context. PyInstaller runs the entry script
as a top-level module, so relative imports fail. This script
imports from the installed package instead.
"""

import sys

# Reason: Windows defaults to cp1252 which can't encode emoji characters
# used throughout the codebase. Force UTF-8 for stdout/stderr so print()
# calls with ✅/⚠️/❌ don't crash inside the PyInstaller binary.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from ai_content_pipeline.__main__ import main

main()
