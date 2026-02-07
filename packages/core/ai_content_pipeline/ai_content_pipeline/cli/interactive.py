"""
Non-interactive mode detection for AI Content Pipeline.

Automatically detects CI environments and provides a safe
wrapper around input() that errors instead of hanging in
non-interactive contexts.

Detection priority:
1. --no-confirm flag (explicit)
2. CI environment variables (CI, GITHUB_ACTIONS, JENKINS_URL, etc.)
3. sys.stdin.isatty() check
"""

import os
import sys

# Common CI environment variables
_CI_ENV_VARS = (
    "CI",
    "GITHUB_ACTIONS",
    "JENKINS_URL",
    "GITLAB_CI",
    "CIRCLECI",
    "TRAVIS",
    "BUILDKITE",
    "TF_BUILD",
    "CODEBUILD_BUILD_ID",
)


def is_interactive() -> bool:
    """Return True if the process is running in an interactive terminal.

    Returns False if:
    - Any CI environment variable is set
    - stdin is not a TTY (piped input, cron, etc.)
    """
    for var in _CI_ENV_VARS:
        if os.environ.get(var):
            return False
    if not hasattr(sys.stdin, "isatty"):
        return False
    return sys.stdin.isatty()


def confirm(prompt: str, default: bool = False) -> bool:
    """Ask for user confirmation, respecting non-interactive mode.

    In non-interactive mode, returns the default value without prompting.

    Args:
        prompt: The question to ask (e.g., "Proceed with execution?")
        default: Value to return in non-interactive mode.

    Returns:
        True if confirmed, False otherwise.
    """
    if not is_interactive():
        return default

    suffix = " (y/N): " if not default else " (Y/n): "
    try:
        response = input(prompt + suffix)
    except EOFError:
        return default

    if not response.strip():
        return default
    return response.strip().lower() in ("y", "yes")
