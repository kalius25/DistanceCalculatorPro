"""
Base exception for DistanceCalculatorPro.

All application-specific exceptions inherit from DistanceCalculatorError.

This exception supports:
- Human-readable error message.
- Stable machine-readable error code.
- Original exception chaining (cause).
- Additional diagnostic context.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.exceptions.error_code import ErrorCode


class DistanceCalculatorError(Exception):
    """
    Base exception for all application-specific errors.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: ErrorCode = ErrorCode.UNKNOWN,
        cause: Exception | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.cause = cause
        self.context: dict[str, Any] = dict(context or {})

    @property
    def details(self) -> dict[str, Any]:
        """
        Structured diagnostic information for logging or debugging.
        """
        return {
            "message": self.message,
            "error_code": self.error_code,
            "cause": self.cause,
            "context": self.context,
        }

    def __str__(self) -> str:
        return self.message
