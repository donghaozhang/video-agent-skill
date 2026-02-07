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
              stream=None):
        """Emit a single JSONL event."""
        if not self.enabled:
            return
        if stream is None:
            stream = sys.stderr
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
        print(json.dumps(final, default=str), flush=True)


class NullEmitter:
    """No-op emitter for when streaming is disabled."""

    def pipeline_start(self, *args, **kwargs): pass
    def step_start(self, *args, **kwargs): pass
    def step_complete(self, *args, **kwargs): pass
    def step_error(self, *args, **kwargs): pass
    def pipeline_complete(self, *args, **kwargs): pass
