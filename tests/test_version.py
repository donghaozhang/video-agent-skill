"""Tests for single source of truth version management.

Verifies that _version.py is the canonical version and that
setup.py and __init__.py both derive from it consistently.

File paths:
    - Source: packages/core/ai_content_pipeline/ai_content_pipeline/_version.py
    - setup.py (reads via regex parse)
    - packages/core/ai_content_pipeline/ai_content_pipeline/__init__.py (imports)
"""

import re
from pathlib import Path

import pytest


# Resolve project root (tests/ is one level below root)
PROJECT_ROOT = Path(__file__).parent.parent


def _read_version_from_version_py():
    """Read __version__ from _version.py by parsing text."""
    version_file = (
        PROJECT_ROOT
        / "packages"
        / "core"
        / "ai_content_pipeline"
        / "ai_content_pipeline"
        / "_version.py"
    )
    text = version_file.read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    assert match, "_version.py must contain __version__ = '...'"
    return match.group(1)


def _read_version_from_setup_py():
    """Read VERSION as parsed by setup.py (same regex approach)."""
    setup_file = PROJECT_ROOT / "setup.py"
    text = setup_file.read_text(encoding="utf-8")
    # setup.py reads _version.py, so we verify it references _version.py
    assert "_version.py" in text, "setup.py must read version from _version.py"
    # Return the version from _version.py (same source)
    return _read_version_from_version_py()


class TestVersionSingleSource:
    """Verify _version.py is the single source of truth."""

    def test_version_file_exists(self):
        """_version.py must exist at the expected path."""
        version_file = (
            PROJECT_ROOT
            / "packages"
            / "core"
            / "ai_content_pipeline"
            / "ai_content_pipeline"
            / "_version.py"
        )
        assert version_file.exists(), f"Missing {version_file}"

    def test_version_is_valid_pep440(self):
        """Version string must conform to PEP 440."""
        version = _read_version_from_version_py()
        # PEP 440 pattern: N.N.N with optional pre/post/dev suffixes
        pep440_re = re.compile(
            r"^(\d+)(\.\d+)*"
            r"(\.?(a|b|rc)\d+)?"
            r"(\.post\d+)?"
            r"(\.dev\d+)?$"
        )
        assert pep440_re.match(version), (
            f"Version '{version}' does not match PEP 440 format"
        )

    def test_init_imports_from_version_py(self):
        """__init__.py must import __version__ from _version, not hardcode it."""
        init_file = (
            PROJECT_ROOT
            / "packages"
            / "core"
            / "ai_content_pipeline"
            / "ai_content_pipeline"
            / "__init__.py"
        )
        text = init_file.read_text(encoding="utf-8")
        assert "from ._version import __version__" in text, (
            "__init__.py must import __version__ from ._version"
        )
        # Ensure no hardcoded version remains
        hardcoded = re.search(r'^__version__\s*=\s*["\']', text, re.MULTILINE)
        assert hardcoded is None, (
            "__init__.py must not contain a hardcoded __version__ assignment"
        )

    def test_setup_py_reads_from_version_py(self):
        """setup.py must read version from _version.py, not hardcode it."""
        setup_file = PROJECT_ROOT / "setup.py"
        text = setup_file.read_text(encoding="utf-8")
        assert "_version.py" in text, "setup.py must reference _version.py"
        # Ensure no hardcoded VERSION = "x.y.z" remains
        hardcoded = re.search(r'^VERSION\s*=\s*["\']\d+\.', text, re.MULTILINE)
        assert hardcoded is None, (
            "setup.py must not contain a hardcoded VERSION = 'x.y.z'"
        )

    def test_package_version_matches(self):
        """ai_content_pipeline.__version__ must match _version.py."""
        from ai_content_pipeline._version import __version__ as canonical
        import ai_content_pipeline

        assert ai_content_pipeline.__version__ == canonical, (
            f"__init__.__version__ ({ai_content_pipeline.__version__}) "
            f"!= _version.__version__ ({canonical})"
        )

    def test_version_not_placeholder(self):
        """Version must not be a placeholder like 0.0.0 or 0.0.1."""
        version = _read_version_from_version_py()
        assert version not in ("0.0.0", "0.0.1", "0.1.0"), (
            f"Version '{version}' looks like a placeholder"
        )
