from __future__ import annotations

from app.exceptions.base_exception import DistanceCalculatorError
from app.exceptions.error_code import ErrorCode


class ParserException(DistanceCalculatorError):
    """Raised when parsing provider data fails."""

    DEFAULT_ERROR_CODE = ErrorCode.PARSER_ERROR