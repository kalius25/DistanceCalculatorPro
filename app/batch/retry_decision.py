"""Classify route failures as retryable or terminal."""

from __future__ import annotations

from app.exceptions import (
    EngineException,
    ErrorCode,
    ParserException,
    ProviderException,
    ValidationException,
)
from app.models.route_result import RouteResult


class RetryDecision:
    """Centralize retry classification for results and raised exceptions."""

    _RETRYABLE_CODES = {
        ErrorCode.ENGINE_ERROR,
        ErrorCode.NETWORK_ERROR,
        ErrorCode.PROVIDER_ERROR,
    }
    _RETRYABLE_MESSAGE_PARTS = (
        "timeout",
        "timed out",
        "network",
        "connection",
        "target page",
        "target closed",
        "browser has been closed",
        "429",
        "503",
        "temporarily unavailable",
    )

    def should_retry_result(self, result: RouteResult) -> bool:
        """Return whether a failed result represents a transient failure."""
        if result.success:
            return False
        if result.error_code in self._RETRYABLE_CODES:
            return True
        if result.exception is not None:
            return self.should_retry_exception(result.exception)
        return self._message_is_retryable(result.error)

    def should_retry_exception(self, error: Exception) -> bool:
        """Return whether an unexpected raised exception is transient."""
        if isinstance(error, (ParserException, ValidationException)):
            return False
        if isinstance(
            error,
            (EngineException, ProviderException, TimeoutError, ConnectionError),
        ):
            return True
        return self._message_is_retryable(str(error))

    @classmethod
    def _message_is_retryable(cls, message: str) -> bool:
        normalized = message.casefold()
        return any(part in normalized for part in cls._RETRYABLE_MESSAGE_PARTS)
