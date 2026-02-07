# Subtask 6: Stream-Friendly Pipeline Execution

**Parent**: [plan-unix-style-migration.md](plan-unix-style-migration.md)
**Depends on**: Subtask 1 (exit codes), Subtask 2 (JSON output)
**Estimated Time**: 50 minutes

---

## Objective

Add `--stream` mode for long-running pipeline commands. Emits JSON Lines progress events to stderr during execution and a final result event to stdout. Enables real-time monitoring and composition with shell tools.

---

## Step-by-Step Implementation

### Step 1: Create `cli/stream.py`

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/cli/stream.py`

```python
"""
JSONL streaming output for pipeline execution.

Events are emitted to stderr as JSON Lines (one JSON object per line).
The final result is emitted to stdout for piping.

Event types:
- pipeline_start: Pipeline metadata
- step_start: Step begins execution
- step_complete: Step finished successfully
- step_error: Step failed
- pipeline_complete: Final result (to stdout)
"""

import json
import sys
import time
from typing import Any, Dict, Optional


SCHEMA_VERSION = "1"


class StreamEmitter:
    """Emits JSONL progress events during pipeline execution."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.start_time = time.time()

    def _emit(self, event_type: str, data: Dict[str, Any],
              stream=sys.stderr):
        """Emit a single JSONL event."""
        if not self.enabled:
            return
        event = {
            "schema_version": SCHEMA_VERSION,
            "event": event_type,
            "timestamp": time.time(),
            "elapsed_seconds": round(time.time() - self.start_time, 3),
            **data,
        }
        print(json.dumps(event, default=str), file=stream, flush=True)

    def pipeline_start(self, name: str, total_steps: int,
                       config: Optional[str] = None):
        """Emit when pipeline execution begins."""
        self._emit("pipeline_start", {
            "name": name,
            "total_steps": total_steps,
            "config": config,
        })

    def step_start(self, step_index: int, step_type: str,
                   model: Optional[str] = None):
        """Emit when a step begins execution."""
        self._emit("step_start", {
            "step": step_index,
            "type": step_type,
            "model": model,
        })

    def step_complete(self, step_index: int, cost: float = 0.0,
                      output_path: Optional[str] = None,
                      duration: float = 0.0):
        """Emit when a step completes successfully."""
        self._emit("step_complete", {
            "step": step_index,
            "cost": cost,
            "output": output_path,
            "duration_seconds": round(duration, 3),
        })

    def step_error(self, step_index: int, error: str,
                   step_type: Optional[str] = None):
        """Emit when a step fails."""
        self._emit("step_error", {
            "step": step_index,
            "type": step_type,
            "error": error,
        })

    def pipeline_complete(self, result: Dict[str, Any]):
        """Emit final result to stdout (not stderr).

        This is the only event that goes to stdout so it can be piped.
        """
        if not self.enabled:
            return
        final = {
            "schema_version": SCHEMA_VERSION,
            "event": "pipeline_complete",
            "elapsed_seconds": round(time.time() - self.start_time, 3),
            **result,
        }
        print(json.dumps(final, default=str), file=sys.stdout, flush=True)


class NullEmitter:
    """No-op emitter for when streaming is disabled."""

    def pipeline_start(self, *args, **kwargs): pass
    def step_start(self, *args, **kwargs): pass
    def step_complete(self, *args, **kwargs): pass
    def step_error(self, *args, **kwargs): pass
    def pipeline_complete(self, *args, **kwargs): pass
```

### Step 2: Add `--stream` flag to `__main__.py`

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

In `run-chain` subparser:

```python
run_chain_parser.add_argument('--stream', action='store_true', default=False,
    help='Emit JSONL progress events to stderr')
```

In `run_chain()` handler:

```python
from .cli.stream import StreamEmitter, NullEmitter

def run_chain(args, manager, output):
    emitter = StreamEmitter(enabled=args.stream) if args.stream else NullEmitter()

    # Load config
    chain = manager.create_chain_from_config(args.config)

    emitter.pipeline_start(
        name=chain.name,
        total_steps=len(chain.steps),
        config=args.config,
    )

    # Execute with callbacks
    result = manager.execute_chain(chain, stream_emitter=emitter)

    if args.stream:
        emitter.pipeline_complete({
            "success": result.success,
            "steps_completed": result.steps_completed,
            "total_steps": result.total_steps,
            "total_cost": result.total_cost,
            "total_time": result.total_time,
            "outputs": result.outputs,
            "error": result.error,
        })
    else:
        # Normal output (JSON or human)
        output.result({...}, command="run-chain")
```

### Step 3: Add callback support to executor

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/pipeline/executor.py`

In `ChainExecutor.execute()`, accept an optional emitter:

```python
def execute(self, chain, input_data=None, stream_emitter=None, **kwargs):
    """Execute a content creation chain.

    Args:
        chain: The pipeline chain to execute.
        input_data: Optional initial input.
        stream_emitter: Optional StreamEmitter for progress events.
    """
    emitter = stream_emitter or NullEmitter()

    for i, step in enumerate(chain.steps):
        emitter.step_start(i, step.step_type.value, step.model)

        try:
            step_result = self._execute_step(step, context, **kwargs)
            emitter.step_complete(
                i,
                cost=step_result.get('cost', 0),
                output_path=step_result.get('output_path'),
                duration=step_result.get('duration', 0),
            )
        except Exception as e:
            emitter.step_error(i, str(e), step.step_type.value)
            raise
```

### Step 4: Write tests

**File**: `tests/test_stream_output.py`

```python
"""Tests for JSONL streaming output."""

import json
import pytest
from io import StringIO
from unittest.mock import patch

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
        assert captured.out == ""  # Nothing on stdout
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
        assert captured.err == ""  # Not on stderr
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
            event = json.loads(line)  # Each line is valid JSON
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
        import time
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
```

---

## Usage Examples

```bash
# Stream progress to terminal, pipe final result to jq
aicp run-chain --config pipeline.yaml --stream 2>/dev/null | jq '.outputs'

# Log progress events to file, capture result
aicp run-chain --config pipeline.yaml --stream 2>progress.jsonl | jq -r '.outputs.final.path'

# Watch progress live with jq formatting
aicp run-chain --config pipeline.yaml --stream 2>&1 >/dev/null | \
  jq -r '"[\(.elapsed_seconds)s] \(.event): step \(.step // "N/A")"'

# Monitor cost accumulation
aicp run-chain --config pipeline.yaml --stream 2>&1 >/dev/null | \
  jq -r 'select(.event == "step_complete") | "Step \(.step): $\(.cost)"'
```

---

## Verification

```bash
# Run tests
python -m pytest tests/test_stream_output.py -v

# Manual test (with a simple pipeline)
aicp run-chain --config input/pipelines/example.yaml --stream

# Verify JSONL format
aicp run-chain --config input/pipelines/example.yaml --stream 2>&1 | \
  python -c "import sys,json; [json.loads(l) for l in sys.stdin]"
```

---

## Notes

- Progress events go to stderr so stdout stays clean for the final result
- `NullEmitter` uses the Null Object pattern to avoid if-checks throughout executor code
- Schema version `"1"` is included in every event for future format evolution
- `flush=True` ensures events appear immediately (not buffered) for real-time monitoring
- The `default=str` in `json.dumps` handles Path objects, datetimes, etc. gracefully
