"""
Stable exit codes for the AI Content Pipeline CLI.

Unix convention: 0 = success, 1 = general error, 2+ = specific errors.
These codes are part of the public API and must not change without a major version bump.
"""

import sys
import traceback as _traceback

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
    """Register an exception type to an exit code.

    Args:
        exc_type: Exception class to map.
        exit_code: Integer exit code to return for this exception.
    """
    _EXCEPTION_EXIT_CODES[exc_type] = exit_code


def exit_code_for(error):
    """Return the exit code for an exception, or EXIT_GENERAL_ERROR.

    Args:
        error: An exception instance.

    Returns:
        Integer exit code.
    """
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
        _traceback.print_exc(file=sys.stderr)
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
    try:
        from ai_content_platform.core.exceptions import (
            ValidationError,
            ConfigurationError,
            PipelineConfigurationError,
            PipelineExecutionError,
            StepExecutionError,
            ServiceNotAvailableError,
            APIKeyError,
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
