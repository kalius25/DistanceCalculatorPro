"""
Global application configuration.

All configurable values should be defined here.
Do not hardcode configuration values elsewhere in the project.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path


class AppMode(StrEnum):
    """Application running mode."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"


# =============================================================================
# Application
# =============================================================================

APP_MODE: AppMode = AppMode.DEVELOPMENT


# =============================================================================
# Project Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Browser
# =============================================================================

HEADLESS: bool = False

BROWSER_TIMEOUT: int = 30_000

PAGE_LOAD_WAIT: int = 3_000


# =============================================================================
# Google Maps
# =============================================================================

GOOGLE_LANGUAGE: str = "vi"

GOOGLE_REGION: str = "VN"

GOOGLE_MAPS_BASE_URL: str = "https://www.google.com/maps"

GOOGLE_MAPS_DIRECTIONS_URL: str = (
    f"{GOOGLE_MAPS_BASE_URL}/dir/?api=1"
)

GOOGLE_MAPS_SEARCH_URL: str = (
    f"{GOOGLE_MAPS_BASE_URL}/search/"
)


# =============================================================================
# Parser
# =============================================================================

PARSER_TIMEOUT: int = 15_000

PARSER_MAX_ROUTES: int = 5


# =============================================================================
# Logging
# =============================================================================

LOG_LEVEL: str = "INFO"

LOG_FILE = LOG_DIR / "app.log"

SAVE_HTML_ON_ERROR: bool = True

SAVE_SCREENSHOT_ON_ERROR: bool = True

SAVE_LAST_URL_ON_ERROR: bool = True

SAVE_PARSER_REPORT: bool = True


# =============================================================================
# Network
# =============================================================================

MAX_RETRY: int = 2


__all__ = [
    "AppMode",
    "APP_MODE",
    "PROJECT_ROOT",
    "LOG_DIR",
    "HEADLESS",
    "BROWSER_TIMEOUT",
    "PAGE_LOAD_WAIT",
    "GOOGLE_LANGUAGE",
    "GOOGLE_REGION",
    "GOOGLE_MAPS_BASE_URL",
    "GOOGLE_MAPS_DIRECTIONS_URL",
    "GOOGLE_MAPS_SEARCH_URL",
    "PARSER_TIMEOUT",
    "PARSER_MAX_ROUTES",
    "LOG_LEVEL",
    "LOG_FILE",
    "SAVE_HTML_ON_ERROR",
    "SAVE_SCREENSHOT_ON_ERROR",
    "SAVE_LAST_URL_ON_ERROR",
    "SAVE_PARSER_REPORT",
    "MAX_RETRY",
]