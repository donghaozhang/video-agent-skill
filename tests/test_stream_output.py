"""Tests for JSONL streaming output.

Tests the cli.stream module which provides:
- StreamEmitter for JSONL progress events to stderr
- Pipeline final result to stdout
- NullEmitter no-op pattern
"""

import json
import time
import pytest

from ai_content_pipeline.cli.stream import StreamEmitter, NullEmitter


class TestStreamEmitter:
    def test_disabled_emits_nothing(self, capsys):
        emitter = StreamEmitter(enabled=False)
        emitter.pipeline_start("test", 3)
        emitter.step_start(0, "text_to_image")
        captured = capsys.readouterr()
        assert captured.err == ""
        assert captured.out == ""

    def test_step_start_emits_to_stderr(self, capsys):
        emitter = StreamEmitter(enabled=True)
        emitter.step_start(0, "text_to_image", model="flux_dev")
        captured = capsys.readouterr()
        assert captured.out == ""
        event = json.loads(captured.err.strip())
        assert event["event"] == "step_start"
        assert event["step"] == 0
        assert event["type"] == "text_to_image"
        assert event["model"] == "flux_dev"

    def test_step_complete_emits_to_stderr(self, capsys):
        emitter = StreamEmitter(enabled=True)
        emitter.step_complete(0, cost=0.004, output_path="/tmp/out.png")
        captured = capsys.readouterr()
        event = json.loads(captured.err.strip())
        assert event["event"] == "step_complete"
        assert event["cost"] == 0.004

    def test_pipeline_complete_emits_to_stdout(self, capsys):
        emitter = StreamEmitter(enabled=True)
        emitter.pipeline_complete({"success": True, "total_cost": 0.05})
        captured = capsys.readouterr()
        assert captured.err == ""
        event = json.loads(captured.out.strip())
        assert event["event"] == "pipeline_complete"
        assert event["success"] is True

    def test_events_are_valid_jsonl(self, capsys):
        emitter = StreamEmitter(enabled=True)
        emitter.pipeline_start("test", 2)
        emitter.step_start(0, "text_to_image")
        emitter.step_complete(0, cost=0.01)
        emitter.step_start(1, "text_to_video")
        emitter.step_complete(1, cost=0.50)
        captured = capsys.readouterr()
        lines = captured.err.strip().split("\n")
        assert len(lines) == 5
        for line in lines:
            event = json.loads(line)
            assert "schema_version" in event
            assert "event" in event
            assert "timestamp" in event

    def test_schema_version_is_present(self, capsys):
        emitter = StreamEmitter(enabled=True)
        emitter.step_start(0, "test")
        captured = capsys.readouterr()
        event = json.loads(captured.err.strip())
        assert event["schema_version"] == "1"

    def test_elapsed_seconds_increases(self, capsys):
        emitter = StreamEmitter(enabled=True)
        emitter.step_start(0, "test")
        time.sleep(0.05)
        emitter.step_complete(0)
        captured = capsys.readouterr()
        lines = captured.err.strip().split("\n")
        start_event = json.loads(lines[0])
        end_event = json.loads(lines[1])
        assert end_event["elapsed_seconds"] >= start_event["elapsed_seconds"]

    def test_step_error_includes_message(self, capsys):
        emitter = StreamEmitter(enabled=True)
        emitter.step_error(0, "API timeout", step_type="text_to_video")
        captured = capsys.readouterr()
        event = json.loads(captured.err.strip())
        assert event["event"] == "step_error"
        assert event["error"] == "API timeout"


class TestNullEmitter:
    def test_no_output(self, capsys):
        emitter = NullEmitter()
        emitter.pipeline_start("test", 3)
        emitter.step_start(0, "test")
        emitter.step_complete(0)
        emitter.step_error(0, "fail")
        emitter.pipeline_complete({"success": True})
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""
