from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from app.exceptions.error_code import ErrorCode


class DistanceCalculatorError(Exception):
    """
    Base exception for all application-specific errors.
    """

    DEFAULT_ERROR_CODE: ClassVar[ErrorCode] = ErrorCode.UNKNOWN

    def __init__(
        self,
        message: str,
        *,
        error_code: ErrorCode | None = None,
        cause: Exception | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.error_code = error_code or self.DEFAULT_ERROR_CODE
        self.cause = cause
        self.context: dict[str, Any] = dict(context or {})

    @property
    def details(self) -> dict[str, Any]:
        return {
            "message": self.message,
            "error_code": self.error_code.value,
            "cause": repr(self.cause) if self.cause else None,
            "context": self.context,
        }

    def __str__(self) -> str:
        return self.message