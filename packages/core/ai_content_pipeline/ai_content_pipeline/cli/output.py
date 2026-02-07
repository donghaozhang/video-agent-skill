"""
Structured CLI output for AI Content Pipeline.

Provides a CLIOutput class that routes output based on mode:
- Human mode (default): Pretty-printed with emojis to stdout
- JSON mode (--json): Machine-readable JSON to stdout, logs to stderr
- Quiet mode (--quiet): Only errors to stderr

All human-readable output goes through this class so that --json mode
can suppress it and emit structured data instead.
"""

import json
import sys
from typing import Any, Dict, Optional


SCHEMA_VERSION = "1"


class CLIOutput:
    """Routes CLI output based on mode flags.

    Args:
        json_mode: Emit machine-readable JSON to stdout.
        quiet: Suppress non-error output.
        debug: Show verbose/debug output.
    """

    def __init__(self, json_mode: bool = False, quiet: bool = False,
                 debug: bool = False):
        self.json_mode = json_mode
        self.quiet = quiet
        self.debug = debug

    def info(self, message: str) -> None:
        """Print informational message (human mode only)."""
        if self.quiet or self.json_mode:
            return
        print(message)

    def error(self, message: str) -> None:
        """Print error message to stderr (always visible)."""
        print(f"error: {message}", file=sys.stderr)

    def warning(self, message: str) -> None:
        """Print warning to stderr (always visible)."""
        print(f"warning: {message}", file=sys.stderr)

    def verbose(self, message: str) -> None:
        """Print debug/verbose message (debug mode only)."""
        if not self.debug:
            return
        print(f"debug: {message}", file=sys.stderr)

    def result(self, data: Dict[str, Any], command: Optional[str] = None) -> None:
        """Emit the final result.

        In JSON mode: prints JSON to stdout.
        In human mode: prints a formatted summary.

        Args:
            data: Result dictionary.
            command: Command name for context.
        """
        if self.json_mode:
            envelope = {
                "schema_version": SCHEMA_VERSION,
                "command": command,
                **data,
            }
            print(json.dumps(envelope, default=str, indent=2))
        elif not self.quiet:
            # Human-readable fallback for commands that use result()
            for key, value in data.items():
                print(f"  {key}: {value}")

    def table(self, rows: list, headers: Optional[list] = None,
              command: Optional[str] = None) -> None:
        """Emit tabular data.

        In JSON mode: prints JSON array to stdout.
        In human mode: prints formatted table.

        Args:
            rows: List of dicts (one per row).
            headers: Column headers for human display.
            command: Command name for context.
        """
        if self.json_mode:
            envelope = {
                "schema_version": SCHEMA_VERSION,
                "command": command,
                "items": rows,
                "count": len(rows),
            }
            print(json.dumps(envelope, default=str, indent=2))
        elif not self.quiet:
            if headers:
                print("  ".join(f"{h:<20}" for h in headers))
                print("-" * (22 * len(headers)))
            for row in rows:
                if isinstance(row, dict):
                    print("  ".join(f"{str(v):<20}" for v in row.values()))
                else:
                    print(str(row))
