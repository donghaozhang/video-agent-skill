"""Single source of truth for the package version.

CI workflows read and patch this file for dev/release builds.
Both setup.py and __init__.py import from here.
"""

__version__ = "1.0.24"
