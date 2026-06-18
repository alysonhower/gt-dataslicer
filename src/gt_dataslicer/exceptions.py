"""Application-specific exceptions and exit codes."""

from __future__ import annotations

from typing import Any


class DataSlicerError(Exception):
    """Base class for expected user-facing errors."""

    exit_code = 1
    error_code = "data_slicer_error"

    def __init__(
        self,
        message: str = "",
        *,
        code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code or self.error_code
        self.context = dict(context or {})


class ConfigError(DataSlicerError):
    """Raised when a configuration file or CLI option is invalid."""

    exit_code = 2
    error_code = "config_error"


class FilterSyntaxError(DataSlicerError):
    """Raised when a filter expression cannot be parsed."""

    exit_code = 2
    error_code = "filter_syntax_error"


class FilterValidationError(DataSlicerError):
    """Raised when a parsed filter references invalid columns or values."""

    exit_code = 2
    error_code = "filter_validation_error"


class CsvReadError(DataSlicerError):
    """Raised when the input CSV cannot be read safely."""

    exit_code = 3
    error_code = "csv_read_error"


class InputReadError(DataSlicerError):
    """Raised when an input file cannot be resolved or read."""

    exit_code = 3
    error_code = "input_read_error"


class ZipPasswordRequiredError(InputReadError):
    """Raised when a ZIP archive needs a password that was not provided."""

    exit_code = 3
    error_code = "zip_password_required"


class QueryExecutionError(DataSlicerError):
    """Raised when DuckDB cannot execute the compiled query."""

    exit_code = 1
    error_code = "query_execution_error"


class ExportLimitError(DataSlicerError):
    """Raised when output cannot fit within configured Excel limits."""

    exit_code = 4
    error_code = "export_limit_error"
