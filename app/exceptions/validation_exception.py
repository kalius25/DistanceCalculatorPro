from __future__ import annotations

from app.exceptions.base_exception import DistanceCalculatorError
from app.exceptions.error_code import ErrorCode


class ValidationException(DistanceCalculatorError):
    """Raised when application input validation fails."""

    DEFAULT_ERROR_CODE = ErrorCode.VALIDATION_ERROR