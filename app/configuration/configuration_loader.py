from __future__ import annotations

from app.configuration.models import (
    AppConfig,
    BrowserConfig,
    DebugConfig,
    ExcelConfig,
    LoggingConfig,
    ProviderConfig,
)
from app.enums.provider_type import ProviderType


class ConfigurationLoader:
    """
    Create and assemble the immutable application configuration.

    Responsibilities
    ----------------
    * Create configuration model instances.
    * Assemble and return AppConfig.

    Non-responsibilities
    --------------------
    * Configuration validation.
    * Logging.
    * Reading environment variables.
    * Reading JSON, YAML, or INI files.
    * Singleton or cache management.
    """

    @staticmethod
    def load() -> AppConfig:
        """
        Create a new application configuration.

        Returns
        -------
        AppConfig
            A fully assembled immutable application configuration.
        """

        return AppConfig(
            browser=BrowserConfig(
                headless=False,
                timeout=30_000,
                slow_mo=0,
                viewport_width=1920,
                viewport_height=1080,
                user_agent=None,
                locale="vi-VN",
            ),
            provider=ProviderConfig(
                retry_count=3,
                retry_delay=1.0,
                default_provider=ProviderType.GOOGLE_MAPS_WEB,
            ),
            logging=LoggingConfig(
                level="INFO",
                directory="logs",
                filename="distance_calculator.log",
            ),
            excel=ExcelConfig(
                export_directory="output",
                auto_fit_columns=True,
            ),
            debug=DebugConfig(
                save_html=False,
                save_screenshot=False,
                save_json=False,
            ),
        )