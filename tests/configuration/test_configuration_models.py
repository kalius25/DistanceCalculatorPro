from dataclasses import FrozenInstanceError

import pytest

from app.configuration.models import (
    AppConfig,
    BrowserConfig,
    DebugConfig,
    ExcelConfig,
    LoggingConfig,
    ProviderConfig,
)
from app.enums.provider_type import ProviderType


def test_browser_config_equality():
    config1 = BrowserConfig(
        headless=True,
        timeout=30_000,
        slow_mo=0,
        viewport_width=1920,
        viewport_height=1080,
        user_agent=None,
        locale="vi-VN",
    )

    config2 = BrowserConfig(
        headless=True,
        timeout=30_000,
        slow_mo=0,
        viewport_width=1920,
        viewport_height=1080,
        user_agent=None,
        locale="vi-VN",
    )

    assert config1 == config2


def test_browser_config_repr_contains_class_name():
    config = BrowserConfig(
        headless=True,
        timeout=30_000,
        slow_mo=0,
        viewport_width=1920,
        viewport_height=1080,
        user_agent=None,
        locale="vi-VN",
    )

    assert "BrowserConfig" in repr(config)


def test_browser_config_is_frozen():
    config = BrowserConfig(
        headless=True,
        timeout=30_000,
        slow_mo=0,
        viewport_width=1920,
        viewport_height=1080,
        user_agent=None,
        locale="vi-VN",
    )

    with pytest.raises(FrozenInstanceError):
        config.timeout = 60


def test_app_config_creation():
    app_config = AppConfig(
        browser=BrowserConfig(
            headless=True,
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
            filename="app.log",
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

    assert app_config.browser.timeout == 30_000
    assert app_config.provider.retry_count == 3
    assert (
        app_config.provider.default_provider
        is ProviderType.GOOGLE_MAPS_WEB
    )


def test_app_config_is_frozen():
    app_config = AppConfig(
        browser=BrowserConfig(
            headless=True,
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
            filename="app.log",
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

    with pytest.raises(FrozenInstanceError):
        app_config.browser = BrowserConfig(
            headless=True,
            timeout=30_000,
            slow_mo=0,
            viewport_width=1920,
            viewport_height=1080,
            user_agent=None,
            locale="vi-VN",
        )


def test_configuration_models_use_slots():
    browser_config = BrowserConfig(
        headless=True,
        timeout=30_000,
        slow_mo=0,
        viewport_width=1920,
        viewport_height=1080,
        user_agent=None,
        locale="vi-VN",
    )

    assert not hasattr(browser_config, "__dict__")