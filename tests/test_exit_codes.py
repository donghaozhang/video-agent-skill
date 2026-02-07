"""Tests for CLI exit codes and error model.

Tests the exit_codes module which provides:
- Stable exit code constants (0-5)
- Exception-to-exit-code mapping
- error_exit() helper for uniform error handling
"""

import sys
import pytest
from unittest.mock import patch

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
    """Exit code values must be stable (public API)."""

    def test_success_is_zero(self):
        assert EXIT_SUCCESS == 0

    def test_general_error_is_one(self):
        assert EXIT_GENERAL_ERROR == 1

    def test_invalid_args_is_two(self):
        assert EXIT_INVALID_ARGS == 2

    def test_missing_config_is_three(self):
        assert EXIT_MISSING_CONFIG == 3

    def test_provider_error_is_four(self):
        assert EXIT_PROVIDER_ERROR == 4

    def test_pipeline_error_is_five(self):
        assert EXIT_PIPELINE_ERROR == 5


class TestExitCodeForBuiltins:
    """Built-in exception mappings registered at import time."""

    def test_value_error_maps_to_invalid_args(self):
        assert exit_code_for(ValueError("bad input")) == EXIT_INVALID_ARGS

    def test_file_not_found_maps_to_missing_config(self):
        assert exit_code_for(FileNotFoundError("no such file")) == EXIT_MISSING_CONFIG

    def test_permission_error_maps_to_missing_config(self):
        assert exit_code_for(PermissionError("denied")) == EXIT_MISSING_CONFIG

    def test_unknown_exception_maps_to_general_error(self):
        assert exit_code_for(RuntimeError("oops")) == EXIT_GENERAL_ERROR

    def test_type_error_maps_to_general_error(self):
        assert exit_code_for(TypeError("wrong type")) == EXIT_GENERAL_ERROR


class TestExitCodeForFrameworkExceptions:
    """Framework exception mappings via register_exception().

    The auto-registration in _register_known_exceptions() may fail at import
    time if ai_content_platform's __init__.py chain has unmet dependencies
    (e.g., 'rich'). These tests verify the mapping *mechanism* works by
    explicitly registering exceptions when auto-registration was skipped.
    """

    @staticmethod
    def _ensure_registered():
        """Re-register framework exceptions if auto-registration was skipped."""
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
            pytest.skip("ai_content_platform.core.exceptions not importable")

    def test_validation_error_maps_to_invalid_args(self):
        self._ensure_registered()
        from ai_content_platform.core.exceptions import ValidationError
        assert exit_code_for(ValidationError("invalid")) == EXIT_INVALID_ARGS

    def test_configuration_error_maps_to_missing_config(self):
        self._ensure_registered()
        from ai_content_platform.core.exceptions import ConfigurationError
        assert exit_code_for(ConfigurationError("missing")) == EXIT_MISSING_CONFIG

    def test_pipeline_config_error_maps_to_missing_config(self):
        self._ensure_registered()
        from ai_content_platform.core.exceptions import PipelineConfigurationError
        assert exit_code_for(PipelineConfigurationError("bad pipeline")) == EXIT_MISSING_CONFIG

    def test_api_key_error_maps_to_missing_config(self):
        self._ensure_registered()
        from ai_content_platform.core.exceptions import APIKeyError
        assert exit_code_for(APIKeyError("no key")) == EXIT_MISSING_CONFIG

    def test_service_not_available_maps_to_provider_error(self):
        self._ensure_registered()
        from ai_content_platform.core.exceptions import ServiceNotAvailableError
        assert exit_code_for(ServiceNotAvailableError("down")) == EXIT_PROVIDER_ERROR

    def test_step_execution_error_maps_to_pipeline_error(self):
        self._ensure_registered()
        from ai_content_platform.core.exceptions import StepExecutionError
        assert exit_code_for(StepExecutionError("step failed")) == EXIT_PIPELINE_ERROR

    def test_pipeline_execution_error_maps_to_pipeline_error(self):
        self._ensure_registered()
        from ai_content_platform.core.exceptions import PipelineExecutionError
        assert exit_code_for(PipelineExecutionError("pipe failed")) == EXIT_PIPELINE_ERROR


class TestRegisterException:
    """Custom exception registration."""

    def test_register_custom_exception(self):
        class MyCustomError(Exception):
            pass

        register_exception(MyCustomError, 42)
        assert exit_code_for(MyCustomError("test")) == 42

    def test_subclass_inherits_mapping(self):
        class BaseError(Exception):
            pass

        class ChildError(BaseError):
            pass

        register_exception(BaseError, 10)
        # isinstance check catches subclasses
        assert exit_code_for(ChildError("child")) == 10


class TestErrorExit:
    """error_exit() prints to stderr and calls sys.exit."""

    def test_exits_with_mapped_code_for_value_error(self):
        with pytest.raises(SystemExit) as exc_info:
            error_exit(ValueError("bad input"))
        assert exc_info.value.code == EXIT_INVALID_ARGS

    def test_exits_with_mapped_code_for_file_not_found(self):
        with pytest.raises(SystemExit) as exc_info:
            error_exit(FileNotFoundError("missing.yaml"))
        assert exc_info.value.code == EXIT_MISSING_CONFIG

    def test_exits_with_general_error_for_unknown_exception(self):
        with pytest.raises(SystemExit) as exc_info:
            error_exit(RuntimeError("unexpected"))
        assert exc_info.value.code == EXIT_GENERAL_ERROR

    def test_exits_with_general_error_for_string_message(self):
        with pytest.raises(SystemExit) as exc_info:
            error_exit("plain string error")
        assert exc_info.value.code == EXIT_GENERAL_ERROR

    def test_prints_error_to_stderr(self, capsys):
        with pytest.raises(SystemExit):
            error_exit(ValueError("bad value"))
        captured = capsys.readouterr()
        assert "error: bad value" in captured.err
        assert captured.out == ""

    def test_debug_mode_prints_traceback(self, capsys):
        try:
            raise ValueError("debug test")
        except ValueError as e:
            with pytest.raises(SystemExit):
                error_exit(e, debug=True)
        captured = capsys.readouterr()
        assert "error: debug test" in captured.err
        assert "Traceback" in captured.err

    def test_no_traceback_without_debug(self, capsys):
        try:
            raise ValueError("no debug")
        except ValueError as e:
            with pytest.raises(SystemExit):
                error_exit(e, debug=False)
        captured = capsys.readouterr()
        assert "error: no debug" in captured.err
        assert "Traceback" not in captured.err
