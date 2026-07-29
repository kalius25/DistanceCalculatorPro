"""
Configuration package.

This package defines immutable configuration models and the configuration
loader used by the application.

Architecture:
    ConfigurationLoader
            │
            ▼
        AppConfig
            │
            ├── BrowserConfig
            ├── ProviderConfig
            ├── LoggingConfig
            ├── ExcelConfig
            └── DebugConfig
"""

from .configuration_loader import ConfigurationLoader
from .models.app_config import AppConfig
from .models.browser_config import BrowserConfig
from .models.debug_config import DebugConfig
from .models.excel_config import ExcelConfig
from .models.logging_config import LoggingConfig
from .models.provider_config import ProviderConfig

__all__ = [
    "AppConfig",
    "BrowserConfig",
    "ProviderConfig",
    "LoggingConfig",
    "ExcelConfig",
    "DebugConfig",
    "ConfigurationLoader",
]