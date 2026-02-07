"""Tests for CLIOutput structured output.

Tests the cli.output module which provides:
- Human-readable output (default)
- JSON mode for machine consumption
- Quiet mode suppression
- Debug/verbose output to stderr
"""

import json
import pytest

from ai_content_pipeline.cli.output import CLIOutput, SCHEMA_VERSION


class TestHumanMode:
    """Default human-readable output."""

    def test_info_prints_to_stdout(self, capsys):
        out = CLIOutput()
        out.info("Hello world")
        captured = capsys.readouterr()
        assert "Hello world" in captured.out
        assert captured.err == ""

    def test_error_prints_to_stderr(self, capsys):
        out = CLIOutput()
        out.error("something broke")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "error: something broke" in captured.err

    def test_warning_prints_to_stderr(self, capsys):
        out = CLIOutput()
        out.warning("deprecated feature")
        captured = capsys.readouterr()
        assert "warning: deprecated feature" in captured.err

    def test_verbose_hidden_by_default(self, capsys):
        out = CLIOutput()
        out.verbose("debug info")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""

    def test_result_prints_key_value(self, capsys):
        out = CLIOutput()
        out.result({"status": "ok", "count": 5})
        captured = capsys.readouterr()
        assert "status: ok" in captured.out
        assert "count: 5" in captured.out


class TestJsonMode:
    """Machine-readable JSON output."""

    def test_info_suppressed(self, capsys):
        out = CLIOutput(json_mode=True)
        out.info("Hello world")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_error_still_prints_to_stderr(self, capsys):
        out = CLIOutput(json_mode=True)
        out.error("something broke")
        captured = capsys.readouterr()
        assert "error: something broke" in captured.err

    def test_result_emits_json(self, capsys):
        out = CLIOutput(json_mode=True)
        out.result({"status": "ok", "count": 5}, command="test-cmd")
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["schema_version"] == SCHEMA_VERSION
        assert data["command"] == "test-cmd"
        assert data["status"] == "ok"
        assert data["count"] == 5

    def test_table_emits_json_array(self, capsys):
        out = CLIOutput(json_mode=True)
        rows = [{"name": "flux_dev", "cost": 0.01}, {"name": "kling", "cost": 0.50}]
        out.table(rows, command="list-models")
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["schema_version"] == SCHEMA_VERSION
        assert data["count"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["name"] == "flux_dev"

    def test_result_json_is_parseable(self, capsys):
        out = CLIOutput(json_mode=True)
        out.result({"path": "output/video.mp4"})
        captured = capsys.readouterr()
        # Must be valid JSON
        data = json.loads(captured.out)
        assert "path" in data


class TestQuietMode:
    """Quiet mode suppresses non-error output."""

    def test_info_suppressed(self, capsys):
        out = CLIOutput(quiet=True)
        out.info("Hello")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_error_still_visible(self, capsys):
        out = CLIOutput(quiet=True)
        out.error("critical")
        captured = capsys.readouterr()
        assert "error: critical" in captured.err

    def test_result_suppressed(self, capsys):
        out = CLIOutput(quiet=True)
        out.result({"status": "ok"})
        captured = capsys.readouterr()
        assert captured.out == ""


class TestDebugMode:
    """Debug mode enables verbose output."""

    def test_verbose_visible_in_debug(self, capsys):
        out = CLIOutput(debug=True)
        out.verbose("trace info")
        captured = capsys.readouterr()
        assert "debug: trace info" in captured.err

    def test_verbose_goes_to_stderr(self, capsys):
        out = CLIOutput(debug=True)
        out.verbose("trace")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "trace" in captured.err


class TestSchemaVersion:
    """Schema version is present in all JSON output."""

    def test_result_has_schema_version(self, capsys):
        out = CLIOutput(json_mode=True)
        out.result({})
        data = json.loads(capsys.readouterr().out)
        assert "schema_version" in data

    def test_table_has_schema_version(self, capsys):
        out = CLIOutput(json_mode=True)
        out.table([])
        data = json.loads(capsys.readouterr().out)
        assert "schema_version" in data
