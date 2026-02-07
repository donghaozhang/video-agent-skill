# Subtask 1: Exit Codes & Error Model

**Parent**: [plan-unix-style-migration.md](plan-unix-style-migration.md)
**Branch**: `feat/unix-linux-style-framework-migration`
**Estimated Time**: 40 minutes

---

## Objective

Replace all `sys.exit(1)` with semantic exit codes. Route all errors to stderr. Show stack traces only with `--debug` (which already exists at `__main__.py:598`).

---

## Step-by-Step Implementation

### Step 1: Create `cli/` package

Create directory structure:

```
packages/core/ai_content_pipeline/ai_content_pipeline/cli/
├── __init__.py
└── exit_codes.py
```

### Step 2: Implement `exit_codes.py`

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/cli/exit_codes.py`

```python
"""
Stable exit codes for the AI Content Pipeline CLI.

Unix convention: 0 = success, 1 = general error, 2+ = specific errors.
These codes are part of the public API and must not change without a major version bump.
"""

import sys
import traceback

# Exit code constants
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_INVALID_ARGS = 2
EXIT_MISSING_CONFIG = 3
EXIT_PROVIDER_ERROR = 4
EXIT_PIPELINE_ERROR = 5
# 10+ reserved for tool-specific failures

# Map exception types to exit codes
_EXCEPTION_EXIT_CODES = {}


def register_exception(exc_type, exit_code):
    """Register an exception type to an exit code."""
    _EXCEPTION_EXIT_CODES[exc_type] = exit_code


def exit_code_for(error):
    """Return the exit code for an exception, or EXIT_GENERAL_ERROR."""
    for exc_type, code in _EXCEPTION_EXIT_CODES.items():
        if isinstance(error, exc_type):
            return code
    return EXIT_GENERAL_ERROR


def error_exit(error, debug=False):
    """Print a one-line error to stderr and exit with the mapped code.

    Args:
        error: The exception or error message.
        debug: If True, print full traceback to stderr.
    """
    code = exit_code_for(error) if isinstance(error, Exception) else EXIT_GENERAL_ERROR
    msg = str(error)
    print(f"error: {msg}", file=sys.stderr)
    if debug and isinstance(error, Exception):
        traceback.print_exc(file=sys.stderr)
    sys.exit(code)


def _register_known_exceptions():
    """Register built-in exception mappings.

    Called at import time. Provider-specific exceptions can be registered
    later via register_exception().
    """
    # Standard library
    register_exception(ValueError, EXIT_INVALID_ARGS)
    register_exception(FileNotFoundError, EXIT_MISSING_CONFIG)
    register_exception(PermissionError, EXIT_MISSING_CONFIG)

    # Framework exceptions from ai_content_platform/core/exceptions.py
    # (try-import to avoid hard dependency)
    try:
        from ai_content_platform.core.exceptions import (
            ValidationError,           # line 39
            ConfigurationError,        # line 44
            PipelineConfigurationError,  # line 9
            PipelineExecutionError,    # line 49
            StepExecutionError,        # line 14
            ServiceNotAvailableError,  # line 19
            APIKeyError,               # line 24
        )
        register_exception(ValidationError, EXIT_INVALID_ARGS)
        register_exception(ConfigurationError, EXIT_MISSING_CONFIG)
        register_exception(PipelineConfigurationError, EXIT_MISSING_CONFIG)
        register_exception(APIKeyError, EXIT_MISSING_CONFIG)
        register_exception(ServiceNotAvailableError, EXIT_PROVIDER_ERROR)
        register_exception(StepExecutionError, EXIT_PIPELINE_ERROR)
        register_exception(PipelineExecutionError, EXIT_PIPELINE_ERROR)
    except ImportError:
        pass

    # Provider errors
    try:
        from fal_client import FalError
        register_exception(FalError, EXIT_PROVIDER_ERROR)
    except ImportError:
        pass


_register_known_exceptions()
```

### Step 3: Modify `__main__.py` error handling

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

**Current pattern** (found at lines 189-194, 315-320, 372-377, 387-389, 478-483):
```python
except Exception as e:
    print(f"\n❌ Error: {e}")
    if args.debug:
        import traceback
        traceback.print_exc()
    sys.exit(1)
```

**New pattern**:
```python
from .cli.exit_codes import error_exit

except Exception as e:
    error_exit(e, debug=getattr(args, 'debug', False))
```

**Changes**:
1. Add `from .cli.exit_codes import error_exit` at top of file (line ~17)
2. Replace the 5 except blocks listed above with `error_exit(e, debug=...)`
3. `--debug` flag already exists at line 598: `parser.add_argument("--debug", action="store_true", help="Enable debug output")`
4. Change error `print()` calls at lines 56-58 (video_analysis), 219-223 (run_chain missing file), 233-234, 241-242, 249-250, 258-259, 261-262 to use `file=sys.stderr`
5. Also update `video_analysis.py:56-58` which uses `print()` + `sys.exit(1)` directly

### Step 4: Update provider CLIs

**File**: `packages/providers/fal/text-to-video/fal_text_to_video/cli.py`

The t2v CLI has `sys.exit(1)` at lines 98 and 148, and `sys.exit(0)` at line 95.

Add at top (after line 14):
```python
from ai_content_pipeline.cli.exit_codes import error_exit
```

Replace line 97-98:
```python
    # Before:
    print(f"\n❌ Failed: {result.get('error')}")
    sys.exit(1)
    # After:
    error_exit(Exception(result.get('error', 'Unknown error')))
```

Replace line 146-148 (`model-info` ValueError handler):
```python
    # Before:
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    # After:
    except ValueError as e:
        error_exit(e)
```

**File**: `packages/providers/fal/image-to-video/fal_image_to_video/cli.py`

Has `sys.exit(1)` at lines 87, 122, 188 and `sys.exit(0)` at lines 84, 119. Same pattern of changes.

### Step 5: Write tests

**File**: `tests/test_exit_codes.py`

```python
"""Tests for CLI exit codes and error handling."""

import pytest
from ai_content_pipeline.cli.exit_codes import (
    EXIT_SUCCESS,
    EXIT_GENERAL_ERROR,
    EXIT_INVALID_ARGS,
    EXIT_MISSING_CONFIG,
    EXIT_PROVIDER_ERROR,
    EXIT_PIPELINE_ERROR,
    exit_code_for,
    error_exit,
    register_exception,
)


class TestExitCodeConstants:
    def test_success_is_zero(self):
        assert EXIT_SUCCESS == 0

    def test_codes_are_unique(self):
        codes = [EXIT_SUCCESS, EXIT_GENERAL_ERROR, EXIT_INVALID_ARGS,
                 EXIT_MISSING_CONFIG, EXIT_PROVIDER_ERROR, EXIT_PIPELINE_ERROR]
        assert len(codes) == len(set(codes))

    def test_codes_are_positive_integers(self):
        for code in [EXIT_GENERAL_ERROR, EXIT_INVALID_ARGS, EXIT_MISSING_CONFIG,
                     EXIT_PROVIDER_ERROR, EXIT_PIPELINE_ERROR]:
            assert isinstance(code, int)
            assert code > 0


class TestExitCodeMapping:
    def test_value_error_maps_to_invalid_args(self):
        assert exit_code_for(ValueError("bad")) == EXIT_INVALID_ARGS

    def test_file_not_found_maps_to_missing_config(self):
        assert exit_code_for(FileNotFoundError("missing")) == EXIT_MISSING_CONFIG

    def test_unknown_error_returns_general(self):
        assert exit_code_for(RuntimeError("unknown")) == EXIT_GENERAL_ERROR

    def test_custom_exception_registration(self):
        class CustomError(Exception):
            pass
        register_exception(CustomError, 10)
        assert exit_code_for(CustomError("test")) == 10


class TestErrorExit:
    def test_error_exit_prints_to_stderr(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            error_exit(ValueError("bad input"))
        assert exc_info.value.code == EXIT_INVALID_ARGS
        captured = capsys.readouterr()
        assert captured.out == ""  # Nothing on stdout
        assert "error: bad input" in captured.err

    def test_error_exit_with_debug_shows_traceback(self, capsys):
        try:
            raise ValueError("bad input")
        except ValueError as e:
            with pytest.raises(SystemExit):
                error_exit(e, debug=True)
        captured = capsys.readouterr()
        assert "Traceback" in captured.err

    def test_error_exit_without_debug_no_traceback(self, capsys):
        with pytest.raises(SystemExit):
            error_exit(ValueError("bad input"), debug=False)
        captured = capsys.readouterr()
        assert "Traceback" not in captured.err
```

---

## Verification

```bash
# Run new tests
python -m pytest tests/test_exit_codes.py -v

# Run full suite to ensure no regressions
python -m pytest tests/ -v

# Manual verification
ai-content-pipeline create-video --text ""  # Should exit 2
ai-content-pipeline run-chain --config nonexistent.yaml  # Should exit 3
```

---

## Rollback

If issues arise, the `cli/exit_codes.py` module is additive-only. Reverting `__main__.py` changes restores the old `sys.exit(1)` behavior with no side effects.
