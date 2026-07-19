"""
Engine exception.
"""

from __future__ import annotations

from app.exceptions.base_exception import DistanceCalculatorError


class EngineException(DistanceCalculatorError):
    """
    Raised when browser or engine operations fail.
    """