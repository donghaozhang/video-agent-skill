"""Tests for GitHub Actions workflow files.

Validates that all workflow YAML files are well-formed and that
the key CI/CD workflows contain the expected structure.

File paths:
    - .github/workflows/test.yml
    - .github/workflows/publish.yml
    - .github/workflows/publish-check.yml
    - .github/workflows/binary.yml
    - .github/workflows/release.yml
"""

from pathlib import Path

import pytest
import yaml


PROJECT_ROOT = Path(__file__).parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / ".github" / "workflows"


class TestWorkflowYAMLValidity:
    """All .yml files in .github/workflows/ must be valid YAML."""

    def _workflow_files(self):
        """Return all .yml files in the workflows directory."""
        return sorted(WORKFLOWS_DIR.glob("*.yml"))

    def test_workflows_directory_exists(self):
        """The .github/workflows/ directory must exist."""
        assert WORKFLOWS_DIR.is_dir(), f"Missing {WORKFLOWS_DIR}"

    def test_all_workflow_files_are_valid_yaml(self):
        """Every .yml file must parse without errors."""
        for yml in self._workflow_files():
            text = yml.read_text(encoding="utf-8")
            try:
                data = yaml.safe_load(text)
                assert isinstance(data, dict), (
                    f"{yml.name} parsed to {type(data).__name__}, expected dict"
                )
            except yaml.YAMLError as e:
                pytest.fail(f"{yml.name} is invalid YAML: {e}")

    def test_all_workflows_have_name(self):
        """Every workflow must have a top-level 'name' field."""
        for yml in self._workflow_files():
            data = yaml.safe_load(yml.read_text(encoding="utf-8"))
            assert "name" in data, f"{yml.name} missing 'name' field"

    def test_all_workflows_have_on_trigger(self):
        """Every workflow must have an 'on' trigger."""
        for yml in self._workflow_files():
            data = yaml.safe_load(yml.read_text(encoding="utf-8"))
            assert "on" in data or True in data, (
                f"{yml.name} missing 'on' trigger"
            )


class TestTestWorkflow:
    """Verify test.yml runs the full pytest suite."""

    def test_test_yml_exists(self):
        """test.yml must exist."""
        assert (WORKFLOWS_DIR / "test.yml").exists()

    def test_test_yml_has_pytest_step(self):
        """test.yml must contain a pytest execution step."""
        text = (WORKFLOWS_DIR / "test.yml").read_text(encoding="utf-8")
        assert "pytest" in text, "test.yml must run pytest"

    def test_test_yml_has_matrix_strategy(self):
        """test.yml must test against multiple Python versions."""
        data = yaml.safe_load(
            (WORKFLOWS_DIR / "test.yml").read_text(encoding="utf-8")
        )
        jobs = data.get("jobs", {})
        test_job = jobs.get("test", {})
        strategy = test_job.get("strategy", {})
        matrix = strategy.get("matrix", {})
        versions = matrix.get("python-version", [])
        assert len(versions) >= 2, (
            f"test.yml should test multiple Python versions, found {versions}"
        )


class TestPublishCheckWorkflow:
    """Verify publish-check.yml is properly configured."""

    def test_publish_check_yml_exists(self):
        """publish-check.yml must exist."""
        assert (WORKFLOWS_DIR / "publish-check.yml").exists()

    def test_publish_check_references_test_pypi_token(self):
        """publish-check.yml must use TEST_PYPI_API_TOKEN secret."""
        text = (WORKFLOWS_DIR / "publish-check.yml").read_text(encoding="utf-8")
        assert "TEST_PYPI_API_TOKEN" in text, (
            "publish-check.yml must reference TEST_PYPI_API_TOKEN"
        )

    def test_publish_check_references_version_py(self):
        """publish-check.yml must read version from _version.py."""
        text = (WORKFLOWS_DIR / "publish-check.yml").read_text(encoding="utf-8")
        assert "_version.py" in text, (
            "publish-check.yml must reference _version.py"
        )

    def test_publish_check_triggers_on_pr(self):
        """publish-check.yml must trigger on pull_request."""
        data = yaml.safe_load(
            (WORKFLOWS_DIR / "publish-check.yml").read_text(encoding="utf-8")
        )
        triggers = data.get("on", data.get(True, {}))
        assert "pull_request" in triggers, (
            "publish-check.yml must trigger on pull_request"
        )


class TestBinaryWorkflow:
    """Verify binary.yml is properly configured."""

    def test_binary_yml_exists(self):
        """binary.yml must exist."""
        assert (WORKFLOWS_DIR / "binary.yml").exists()

    def test_binary_yml_has_matrix_with_4_targets(self):
        """binary.yml must build for 4 OS targets."""
        data = yaml.safe_load(
            (WORKFLOWS_DIR / "binary.yml").read_text(encoding="utf-8")
        )
        jobs = data.get("jobs", {})
        build_job = jobs.get("build", {})
        strategy = build_job.get("strategy", {})
        matrix = strategy.get("matrix", {})
        includes = matrix.get("include", [])
        assert len(includes) == 4, (
            f"binary.yml should have 4 matrix entries, found {len(includes)}"
        )

    def test_binary_yml_references_spec_file(self):
        """binary.yml must use aicp.spec."""
        text = (WORKFLOWS_DIR / "binary.yml").read_text(encoding="utf-8")
        assert "aicp.spec" in text, "binary.yml must reference aicp.spec"

    def test_binary_yml_has_smoke_test(self):
        """binary.yml must include a smoke test step."""
        text = (WORKFLOWS_DIR / "binary.yml").read_text(encoding="utf-8")
        assert "--help" in text, "binary.yml must include a --help smoke test"

    def test_binary_yml_triggers_on_tag(self):
        """binary.yml must trigger on tag pushes for release attachment."""
        data = yaml.safe_load(
            (WORKFLOWS_DIR / "binary.yml").read_text(encoding="utf-8")
        )
        triggers = data.get("on", data.get(True, {}))
        push_trigger = triggers.get("push", {})
        tags = push_trigger.get("tags", [])
        assert any("v*" in t for t in tags), (
            "binary.yml must trigger on v*.*.* tag pushes"
        )


class TestExistingWorkflowsUnchanged:
    """Verify we haven't broken publish.yml or release.yml."""

    def test_publish_yml_exists(self):
        """publish.yml must still exist."""
        assert (WORKFLOWS_DIR / "publish.yml").exists()

    def test_publish_yml_triggers_on_release(self):
        """publish.yml must still trigger on release events."""
        data = yaml.safe_load(
            (WORKFLOWS_DIR / "publish.yml").read_text(encoding="utf-8")
        )
        triggers = data.get("on", data.get(True, {}))
        assert "release" in triggers, (
            "publish.yml must trigger on release events"
        )

    def test_release_yml_exists(self):
        """release.yml must still exist."""
        assert (WORKFLOWS_DIR / "release.yml").exists()

    def test_release_yml_triggers_on_tags(self):
        """release.yml must still trigger on tag pushes."""
        data = yaml.safe_load(
            (WORKFLOWS_DIR / "release.yml").read_text(encoding="utf-8")
        )
        triggers = data.get("on", data.get(True, {}))
        push_trigger = triggers.get("push", {})
        tags = push_trigger.get("tags", [])
        assert len(tags) > 0, "release.yml must trigger on tag pushes"
