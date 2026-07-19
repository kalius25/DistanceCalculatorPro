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

APP_MODE = AppMode.DEVELOPMENT


# =============================================================================
# Project Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Browser
# =============================================================================

HEADLESS = False

BROWSER_TIMEOUT = 30_000

PAGE_LOAD_WAIT = 3_000


# =============================================================================
# Google Maps
# =============================================================================

GOOGLE_LANGUAGE = "vi"

GOOGLE_REGION = "VN"

GOOGLE_MAPS_URL = "https://www.google.com/maps/dir/?api=1"


# =============================================================================
# Parser
# =============================================================================

PARSER_TIMEOUT = 15_000

PARSER_MAX_ROUTES = 5


# =============================================================================
# Logging
# =============================================================================

LOG_LEVEL = "INFO"

LOG_FILE = LOG_DIR / "app.log"

SAVE_HTML_ON_ERROR = True

SAVE_SCREENSHOT_ON_ERROR = True

SAVE_LAST_URL_ON_ERROR = True

SAVE_PARSER_REPORT = True


# =============================================================================
# Retry
# =============================================================================

MAX_RETRY = 2