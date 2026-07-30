"""
Sensitive logging data sanitization.

This module prevents credentials, personal information and oversized
values from being written to application logs.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

_REDACTED = "[REDACTED]"
_MAX_STRING_LENGTH = 256
_MAX_COLLECTION_ITEMS = 20
_MAX_SANITIZE_DEPTH = 5


_SENSITIVE_KEYWORDS = frozenset(
    {
        "password",
        "passwd",
        "pwd",
        "secret",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "authorization",
        "auth",
        "cookie",
        "cookies",
        "session",
        "session_id",
        "private_key",
        "client_secret",
        "credit_card",
        "card_number",
        "cvv",
        "pin",
    }
)


_EMAIL_PATTERN = re.compile(
    r"\b"
    r"[A-Za-z0-9._%+-]+"
    r"@"
    r"[A-Za-z0-9.-]+"
    r"\.[A-Za-z]{2,}"
    r"\b"
)


_PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?84|0)"
    r"(?:[\s.\-]?\d)"
    r"{8,10}"
    r"(?!\d)"
)


_COORDINATE_PATTERN = re.compile(
    r"(?<![\d.])"
    r"-?\d{1,3}(?:\.\d{4,})"
    r"\s*[,;]\s*"
    r"-?\d{1,3}(?:\.\d{4,})"
    r"(?![\d.])"
)


_BEARER_TOKEN_PATTERN = re.compile(
    r"(?i)"
    r"\bBearer\s+"
    r"[A-Za-z0-9._~+/=-]+"
)


_SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)"
    r"\b"
    r"(password|passwd|pwd|secret|api[_-]?key|token)"
    r"\s*[:=]\s*"
    r"[^\s,;]+"
)


class SensitiveDataSanitizer:
    """Sanitize structured metadata before it is logged."""

    @classmethod
    def sanitize(
        cls,
        value: Any,
    ) -> Any:
        """Return a log-safe representation of a value."""

        return cls._sanitize(
            value,
            depth=0,
            key=None,
        )

    @classmethod
    def sanitize_mapping(
        cls,
        fields: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Sanitize a mapping of structured logging fields."""

        return cls._sanitize_mapping(
            fields,
            depth=0,
        )

    @classmethod
    def fingerprint(
        cls,
        value: str,
    ) -> str:
        """
        Return a short non-reversible fingerprint.

        The fingerprint allows related log events to be correlated
        without storing the original value.
        """

        normalized = value.strip().casefold()

        return hashlib.sha256(
            normalized.encode("utf-8"),
        ).hexdigest()[:16]

    @classmethod
    def _sanitize(
        cls,
        value: Any,
        *,
        depth: int,
        key: str | None,
    ) -> Any:
        """Recursively sanitize one value."""

        if cls._is_sensitive_key(key):
            return _REDACTED

        if depth >= _MAX_SANITIZE_DEPTH:
            return "[MAX_DEPTH]"

        if value is None:
            return None

        if isinstance(
            value,
            (
                bool,
                int,
                float,
            ),
        ):
            return value

        if isinstance(value, str):
            return cls._sanitize_string(value)

        if isinstance(value, Mapping):
            return cls._sanitize_mapping(
                value,
                depth=depth,
            )

        if isinstance(
            value,
            (
                bytes,
                bytearray,
            ),
        ):
            return f"[BINARY:{len(value)}]"

        if isinstance(value, Sequence):
            return cls._sanitize_sequence(
                value,
                depth=depth,
            )

        return cls._sanitize_string(
            str(value),
        )

    @classmethod
    def _sanitize_mapping(
        cls,
        value: Mapping[Any, Any],
        *,
        depth: int,
    ) -> dict[str, Any]:
        """Sanitize dictionary-like data."""

        sanitized: dict[str, Any] = {}

        for index, (
            raw_key,
            raw_value,
        ) in enumerate(value.items()):
            if index >= _MAX_COLLECTION_ITEMS:
                sanitized["_truncated"] = True
                break

            key = str(raw_key)

            sanitized[key] = cls._sanitize(
                raw_value,
                depth=depth + 1,
                key=key,
            )

        return sanitized

    @classmethod
    def _sanitize_sequence(
        cls,
        value: Sequence[Any],
        *,
        depth: int,
    ) -> list[Any]:
        """Sanitize sequence values."""

        sanitized = [
            cls._sanitize(
                item,
                depth=depth + 1,
                key=None,
            )
            for item in value[
                :_MAX_COLLECTION_ITEMS
            ]
        ]

        if len(value) > _MAX_COLLECTION_ITEMS:
            sanitized.append("[TRUNCATED]")

        return sanitized

    @classmethod
    def _sanitize_string(
        cls,
        value: str,
    ) -> str:
        """Sanitize potentially sensitive text."""

        sanitized = value

        sanitized = _BEARER_TOKEN_PATTERN.sub(
            "Bearer [REDACTED]",
            sanitized,
        )

        sanitized = _SECRET_ASSIGNMENT_PATTERN.sub(
            lambda match: (
                f"{match.group(1)}={_REDACTED}"
            ),
            sanitized,
        )

        sanitized = _EMAIL_PATTERN.sub(
            cls._mask_email,
            sanitized,
        )

        sanitized = _PHONE_PATTERN.sub(
            cls._mask_phone,
            sanitized,
        )

        sanitized = _COORDINATE_PATTERN.sub(
            "[COORDINATES_REDACTED]",
            sanitized,
        )

        if len(sanitized) > _MAX_STRING_LENGTH:
            sanitized = (
                sanitized[:_MAX_STRING_LENGTH]
                + "...[TRUNCATED]"
            )

        return sanitized

    @staticmethod
    def _is_sensitive_key(
        key: str | None,
    ) -> bool:
        """Return whether a field name is sensitive."""

        if key is None:
            return False

        normalized = (
            key.strip()
            .casefold()
            .replace("-", "_")
            .replace(" ", "_")
        )

        if normalized in _SENSITIVE_KEYWORDS:
            return True

        return any(
            keyword in normalized
            for keyword in _SENSITIVE_KEYWORDS
        )

    @staticmethod
    def _mask_email(
        match: re.Match[str],
    ) -> str:
        """Mask an email address."""

        value = match.group(0)
        local_part, domain = value.split(
            "@",
            maxsplit=1,
        )

        if len(local_part) <= 1:
            masked_local = "*"
        else:
            masked_local = (
                local_part[0]
                + "***"
            )

        return f"{masked_local}@{domain}"

    @staticmethod
    def _mask_phone(
        match: re.Match[str],
    ) -> str:
        """Mask a phone number while keeping its final digits."""

        value = match.group(0)

        digits = "".join(
            character
            for character in value
            if character.isdigit()
        )

        return (
            "***"
            + digits[-4:]
        )


__all__ = [
    "SensitiveDataSanitizer",
]