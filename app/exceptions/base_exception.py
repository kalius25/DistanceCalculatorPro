"""
Base exception for DistanceCalculatorPro.
"""

from __future__ import annotations


class DistanceCalculatorError(Exception):
    """
    Base exception for all application-specific errors.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message