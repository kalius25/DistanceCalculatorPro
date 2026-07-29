"""
Application configuration model.

The AppConfig object is the root configuration object of the application.
It aggregates all configuration sections into a single immutable object.

Architecture:

    AppConfig
    ├── BrowserConfig
    ├── ProviderConfig
    ├── LoggingConfig
    ├── ExcelConfig
    └── DebugConfig

Notes
-----
- Immutable (frozen dataclass).
- Contains no business logic.
- Created only by ConfigurationLoader.
"""

from __future__ import annotations

from dataclasses import dataclass

from .browser_config import BrowserConfig
from .debug_config import DebugConfig
from .excel_config import ExcelConfig
from .logging_config import LoggingConfig
from .provider_config import ProviderConfig


@dataclass(frozen=True, slots=True)
class AppConfig:
    """
    Root application configuration.

    This object groups all configuration models required by the application.

    Business objects should receive only the configuration section they need
    instead of the whole AppConfig whenever possible.
    """

    browser: BrowserConfig
    provider: ProviderConfig
    logging: LoggingConfig
    excel: ExcelConfig
    debug: DebugConfig