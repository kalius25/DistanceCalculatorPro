"""
Provider exception.
"""

from __future__ import annotations

from app.exceptions.base_exception import DistanceCalculatorError


class ProviderException(DistanceCalculatorError):
    """
    Raised when a map provider fails to calculate routes.
    """