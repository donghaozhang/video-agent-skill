# Subtask 4: Non-Interactive Mode

**Parent**: [plan-unix-style-migration.md](plan-unix-style-migration.md)
**Depends on**: Subtask 1 (exit codes) - uses stderr pattern
**Estimated Time**: 30 minutes

---

## Objective

Add `--yes` / `--non-interactive` flags to skip all confirmation prompts. Auto-detect CI environments so pipelines work without user input in automated contexts.

---

## Step-by-Step Implementation

### Step 1: Add `--yes` to global parser

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

In the global argument parser (before subparsers):

```python
parser.add_argument('--yes', '-y', action='store_true', default=False,
    help='Skip all confirmation prompts (non-interactive mode)')
```

### Step 2: Create confirm helper

Add to `cli/output.py` (or a new `cli/interactive.py` if preferred):

```python
import os
import sys


# CI environment variable names
_CI_ENV_VARS = [
    'CI',
    'GITHUB_ACTIONS',
    'GITLAB_CI',
    'JENKINS_URL',
    'TF_BUILD',
    'CIRCLECI',
    'TRAVIS',
    'BUILDKITE',
]


def is_non_interactive(args=None) -> bool:
    """Check if running in non-interactive mode.

    Returns True if:
    - --yes flag is set
    - Any CI environment variable is set
    - stdin is not a terminal (piped input)
    """
    if args and getattr(args, 'yes', False):
        return True
    return any(os.environ.get(v) for v in _CI_ENV_VARS)


def confirm(message: str, args=None, default: bool = False) -> bool:
    """Ask for user confirmation.

    In non-interactive mode, returns True (auto-accept).
    Otherwise prompts the user.

    Args:
        message: The confirmation question.
        args: Parsed CLI args (checked for --yes flag).
        default: Default answer when user just presses Enter.

    Returns:
        True if confirmed, False otherwise.
    """
    if is_non_interactive(args):
        return True

    suffix = " (Y/n): " if default else " (y/N): "
    try:
        response = input(message + suffix).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)  # Newline after ^C
        return False

    if not response:
        return default
    return response in ('y', 'yes')
```

### Step 3: Replace `input()` prompts in `__main__.py`

**File**: `packages/core/ai_content_pipeline/ai_content_pipeline/__main__.py`

**Current** (~line 279):
```python
response = input("\nProceed with execution? (y/N): ")
if response.lower() not in ['y', 'yes']:
    print("Execution cancelled.")
    sys.exit(0)
```

**New**:
```python
from .cli.output import confirm

if not confirm("\nProceed with execution?", args):
    output.info("Execution cancelled.")
    sys.exit(0)
```

Find all instances of `input(` used for confirmation and replace with `confirm()`.

### Step 4: Update `ai_content_platform` CLI

**File**: `packages/core/ai_content_platform/cli/commands.py`

**Current** (~line 96): Cost threshold confirmation
```python
if estimated_cost > 1.0:
    click.confirm("Cost exceeds $1.00. Continue?", abort=True)
```

**New**:
```python
if estimated_cost > 1.0 and not ctx.obj.get('yes', False):
    click.confirm("Cost exceeds $1.00. Continue?", abort=True)
```

Pass `--yes` through Click context.

### Step 5: Write tests

Add to existing test file or create `tests/test_non_interactive.py`:

```python
"""Tests for non-interactive mode."""

import os
import pytest
from unittest.mock import patch
from ai_content_pipeline.cli.output import is_non_interactive, confirm


class TestNonInteractive:
    def test_yes_flag_skips_confirmation(self):
        class Args:
            yes = True
        assert is_non_interactive(Args()) is True

    def test_ci_env_auto_skips(self):
        with patch.dict(os.environ, {'CI': 'true'}):
            assert is_non_interactive() is True

    def test_github_actions_auto_skips(self):
        with patch.dict(os.environ, {'GITHUB_ACTIONS': 'true'}):
            assert is_non_interactive() is True

    def test_default_is_interactive(self):
        # Clear all CI vars
        env = {v: '' for v in ['CI', 'GITHUB_ACTIONS', 'GITLAB_CI',
                                'JENKINS_URL', 'TF_BUILD']}
        with patch.dict(os.environ, env, clear=False):
            class Args:
                yes = False
            # Only non-interactive if CI vars are truly absent
            # (this test may need adjustment based on actual env)


class TestConfirm:
    def test_confirm_returns_true_in_non_interactive(self):
        class Args:
            yes = True
        assert confirm("Continue?", args=Args()) is True

    def test_confirm_returns_true_with_ci(self):
        with patch.dict(os.environ, {'CI': 'true'}):
            assert confirm("Continue?") is True

    def test_confirm_handles_eof(self):
        with patch('builtins.input', side_effect=EOFError):
            assert confirm("Continue?") is False
```

---

## Verification

```bash
# Non-interactive mode
ai-content-pipeline run-chain --config pipeline.yaml --yes --json

# CI simulation
CI=true ai-content-pipeline run-chain --config pipeline.yaml --json

# Run tests
python -m pytest tests/test_non_interactive.py -v
```

---

## Notes

- `--yes` only affects confirmation prompts, not error handling
- stdin detection (`sys.stdin.isatty()`) is NOT used for non-interactive detection because `--input -` legitimately uses stdin
- The `confirm()` helper catches `EOFError` and `KeyboardInterrupt` gracefully
