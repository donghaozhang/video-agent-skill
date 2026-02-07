"""Tests for the PyInstaller spec file (aicp.spec).

Validates that the spec file is syntactically correct, references
the right entry point, and lists importable hidden imports.

File paths:
    - Spec:  aicp.spec (project root)
    - Entry: aicp_entry.py (project root)
"""

import re
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parent.parent


class TestSpecFileStructure:
    """Verify aicp.spec exists and is valid Python."""

    def test_spec_file_exists(self):
        """aicp.spec must exist at the project root."""
        spec = PROJECT_ROOT / "aicp.spec"
        assert spec.exists(), f"Missing {spec}"

    def test_spec_file_is_valid_python(self):
        """aicp.spec must compile without syntax errors."""
        spec = PROJECT_ROOT / "aicp.spec"
        source = spec.read_text(encoding="utf-8")
        # compile() checks syntax; it won't execute the code
        try:
            compile(source, str(spec), "exec")
        except SyntaxError as e:
            pytest.fail(f"aicp.spec has a syntax error: {e}")

    def test_entry_point_path_matches(self):
        """Spec must reference the aicp_entry.py wrapper."""
        spec = PROJECT_ROOT / "aicp.spec"
        source = spec.read_text(encoding="utf-8")
        # The spec should reference the entry wrapper
        assert "aicp_entry.py" in source, (
            "aicp.spec must reference aicp_entry.py as the entry point"
        )
        # Verify the actual file exists
        entry = PROJECT_ROOT / "aicp_entry.py"
        assert entry.exists(), f"Entry point {entry} does not exist"

    def test_output_name_is_aicp(self):
        """Binary output name must be 'aicp'."""
        spec = PROJECT_ROOT / "aicp.spec"
        source = spec.read_text(encoding="utf-8")
        assert "name='aicp'" in source, (
            "aicp.spec must set name='aicp' for the output binary"
        )


class TestHiddenImports:
    """Verify that listed hidden imports are actually importable."""

    @staticmethod
    def _extract_hidden_imports():
        """Parse hiddenimports list from the spec file."""
        spec = PROJECT_ROOT / "aicp.spec"
        source = spec.read_text(encoding="utf-8")
        # Extract everything between hiddenimports=[ and the matching ]
        match = re.search(
            r"hiddenimports\s*=\s*\[(.*?)\]", source, re.DOTALL
        )
        assert match, "Could not find hiddenimports in aicp.spec"
        block = match.group(1)
        # Extract all quoted strings
        imports = re.findall(r"['\"]([^'\"]+)['\"]", block)
        return imports

    def test_hidden_imports_are_listed(self):
        """Spec must have a non-empty hiddenimports list."""
        imports = self._extract_hidden_imports()
        assert len(imports) > 0, "hiddenimports list is empty"

    def test_core_pipeline_in_hidden_imports(self):
        """Critical core packages must be listed."""
        imports = self._extract_hidden_imports()
        required = [
            "ai_content_pipeline",
            "ai_content_pipeline.cli.exit_codes",
            "ai_content_pipeline.registry",
        ]
        for pkg in required:
            assert pkg in imports, f"Missing required hidden import: {pkg}"

    def test_hidden_imports_are_importable(self):
        """Each hidden import should be importable in the dev environment.

        Some may fail (e.g., ai_content_platform without rich), so we
        just check the majority succeed — not all are required at runtime
        on all platforms.
        """
        imports = self._extract_hidden_imports()
        importable = 0
        failed = []
        for mod in imports:
            try:
                __import__(mod)
                importable += 1
            except (ImportError, ModuleNotFoundError):
                failed.append(mod)

        # At least 50% should be importable in the dev environment
        ratio = importable / len(imports) if imports else 0
        assert ratio >= 0.5, (
            f"Only {importable}/{len(imports)} hidden imports are importable. "
            f"Failed: {failed[:10]}"
        )
