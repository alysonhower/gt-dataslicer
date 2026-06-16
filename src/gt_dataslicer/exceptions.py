"""Application-specific exceptions and exit codes."""

from __future__ import annotations


class DataSlicerError(Exception):
    """Base class for expected user-facing errors."""

    exit_code = 1


class ConfigError(DataSlicerError):
    """Raised when a configuration file or CLI option is invalid."""

    exit_code = 2


class FilterSyntaxError(DataSlicerError):
    """Raised when a filter expression cannot be parsed."""

    exit_code = 2


class FilterValidationError(DataSlicerError):
    """Raised when a parsed filter references invalid columns or values."""

    exit_code = 2


class CsvReadError(DataSlicerError):
    """Raised when the input CSV cannot be read safely."""

    exit_code = 3


class InputReadError(DataSlicerError):
    """Raised when an input file cannot be resolved or read."""

    exit_code = 3


class ZipPasswordRequiredError(InputReadError):
    """Raised when a ZIP archive needs a password that was not provided."""

    exit_code = 3


class QueryExecutionError(DataSlicerError):
    """Raised when DuckDB cannot execute the compiled query."""

    exit_code = 1


class ExportLimitError(DataSlicerError):
    """Raised when output cannot fit within configured Excel limits."""

    exit_code = 4
