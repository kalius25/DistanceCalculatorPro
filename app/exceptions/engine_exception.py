from __future__ import annotations

from app.exceptions.base_exception import DistanceCalculatorError
from app.exceptions.error_code import ErrorCode


class EngineException(DistanceCalculatorError):
    """Raised when browser or engine operations fail."""

    DEFAULT_ERROR_CODE = ErrorCode.ENGINE_ERROR