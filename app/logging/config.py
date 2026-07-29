"""
Logging configuration.

This module contains only logging configuration constants.
Business modules must not import the standard logging package directly
for configuration purposes.
"""

from __future__ import annotations

from pathlib import Path

# -----------------------------------------------------------------------------
# Directory
# -----------------------------------------------------------------------------

LOG_DIRECTORY = Path("logs")
LOG_FILENAME = "distance_calculator.log"

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------

LOGGER_NAME = "DistanceCalculatorPro"

# -----------------------------------------------------------------------------
# Level
# -----------------------------------------------------------------------------

LOG_LEVEL = "INFO"

# -----------------------------------------------------------------------------
# Formatter
# -----------------------------------------------------------------------------

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"