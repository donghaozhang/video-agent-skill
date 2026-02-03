"""Custom exceptions for AI Content Platform."""


class AIPlatformError(Exception):
    """Base exception for AI Content Platform."""
    pass


class PipelineConfigurationError(AIPlatformError):
    """Raised when pipeline configuration is invalid."""
    pass


class StepExecutionError(AIPlatformError):
    """Raised when a pipeline step fails to execute."""
    pass


class ServiceNotAvailableError(AIPlatformError):
    """Raised when a required AI service is not available."""
    pass


class APIKeyError(AIPlatformError):
    """Raised when API key is missing or invalid."""
    pass


class CostLimitExceededError(AIPlatformError):
    """Raised when estimated cost exceeds user-defined limits."""
    pass


class ParallelExecutionError(AIPlatformError):
    """Raised when parallel execution fails."""
    pass


class ValidationError(AIPlatformError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(AIPlatformError):
    """Raised when configuration is invalid."""
    pass


class PipelineExecutionError(AIPlatformError):
    """Raised when pipeline execution fails."""
    pass


class FileOperationError(AIPlatformError):
    """Raised when file operations fail."""
    pass


class CostCalculationError(AIPlatformError):
    """Raised when cost calculation fails."""
    pass