"""Centralized custom exceptions for the application."""


class ModelLoadError(Exception):
    """Raised when the ML model cannot be loaded."""

    pass


class PredictionError(Exception):
    """Raised when prediction fails."""

    pass
