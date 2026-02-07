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
from pathlib import Path
from typing import Any, Dict, Optional


SCHEMA_VERSION = "1"


def read_input(input_arg: Optional[str], fallback: Optional[str] = None) -> Optional[str]:
    """Read input from a file path, stdin ('-'), or use fallback.

    Args:
        input_arg: File path, '-' for stdin, or None.
        fallback: Value to return if input_arg is None.

    Returns:
        The input text, or None if no input available.

    Raises:
        ValueError: If stdin is requested but is a terminal.
        FileNotFoundError: If the input file doesn't exist.
    """
    if input_arg == "-":
        if sys.stdin.isatty():
            raise ValueError("--input - requires piped input (stdin is a terminal)")
        return sys.stdin.read().strip()
    elif input_arg:
        path = Path(input_arg)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {input_arg}")
        return path.read_text().strip()
    return fallback


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
                "data": data,
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
                if isinstance(row, dict) and headers:
                    print("  ".join(f"{str(row.get(h, '')):<20}" for h in headers))
                elif isinstance(row, dict):
                    print("  ".join(f"{str(v):<20}" for v in row.values()))
                else:
                    print(str(row))
