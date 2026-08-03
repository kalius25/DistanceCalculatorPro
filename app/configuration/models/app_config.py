"""
Application configuration model.

The AppConfig object is the root configuration object of the application.
It aggregates all configuration sections into a single immutable object.
"""

from __future__ import annotations

from dataclasses import dataclass

from .browser_config import BrowserConfig
from .debug_config import DebugConfig
from .excel_config import ExcelConfig
from .google_maps_config import GoogleMapsConfig
from .logging_config import LoggingConfig
from .provider_config import ProviderConfig


@dataclass(frozen=True, slots=True)
class AppConfig:
    """
    Root application configuration.

    Business objects should receive only the configuration section they
    require instead of receiving the entire AppConfig.
    """

    browser: BrowserConfig
    google_maps: GoogleMapsConfig
    provider: ProviderConfig
    logging: LoggingConfig
    excel: ExcelConfig
    debug: DebugConfig
