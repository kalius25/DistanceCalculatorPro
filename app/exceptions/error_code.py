"""
Standard error codes for DistanceCalculatorPro.

This module defines application-wide error codes used by
DistanceCalculatorError and its subclasses.
"""

from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    """Application error codes."""

    UNKNOWN = "UNKNOWN"

    # Configuration
    CONFIG_ERROR = "CONFIG_ERROR"

    # Browser / Engine
    ENGINE_ERROR = "ENGINE_ERROR"

    # Parser
    PARSER_ERROR = "PARSER_ERROR"

    # Provider
    PROVIDER_ERROR = "PROVIDER_ERROR"

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"

    # File
    FILE_ERROR = "FILE_ERROR"

    # Network
    NETWORK_ERROR = "NETWORK_ERROR"

    # Internal
    INTERNAL_ERROR = "INTERNAL_ERROR"
