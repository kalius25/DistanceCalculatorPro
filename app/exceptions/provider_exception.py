from __future__ import annotations

from app.exceptions.base_exception import DistanceCalculatorError
from app.exceptions.error_code import ErrorCode


class ProviderException(DistanceCalculatorError):
    """Raised when a map provider operation fails."""

    DEFAULT_ERROR_CODE = ErrorCode.PROVIDER_ERROR