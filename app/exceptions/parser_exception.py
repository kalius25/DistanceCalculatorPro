"""
Parser exception.
"""

from __future__ import annotations

from app.exceptions.base_exception import DistanceCalculatorError


class ParserException(DistanceCalculatorError):
    """
    Raised when parsing Google Maps data fails.
    """
