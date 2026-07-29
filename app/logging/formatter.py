"""
Logging formatter.

Provides the default formatter used throughout the application.
"""

from __future__ import annotations

import logging

from .config import DATE_FORMAT, LOG_FORMAT


class DefaultFormatter(logging.Formatter):
    """Default formatter for DistanceCalculatorPro."""

    def __init__(self) -> None:
        super().__init__(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )