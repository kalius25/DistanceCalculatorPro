from app.configuration import ConfigurationLoader
from app.enums.provider_type import ProviderType


def test_browser_default_values():
    config = ConfigurationLoader.load()

    assert config.browser.headless is False
    assert config.browser.timeout == 30_000
    assert config.browser.slow_mo == 0
    assert config.browser.viewport_width == 1920
    assert config.browser.viewport_height == 1080
    assert config.browser.user_agent is None
    assert config.browser.locale == "vi-VN"


def test_provider_default_values():
    config = ConfigurationLoader.load()

    assert config.provider.retry_count == 3
    assert config.provider.retry_delay == 1.0
    assert (
        config.provider.default_provider
        is ProviderType.GOOGLE_MAPS_WEB
    )


def test_logging_default_values():
    config = ConfigurationLoader.load()

    assert config.logging.level == "INFO"
    assert config.logging.directory == "logs"
    assert config.logging.filename == "distance_calculator.log"


def test_excel_default_values():
    config = ConfigurationLoader.load()

    assert config.excel.export_directory == "output"
    assert config.excel.auto_fit_columns is True


def test_debug_default_values():
    config = ConfigurationLoader.load()

    assert config.debug.save_html is False
    assert config.debug.save_screenshot is False
    assert config.debug.save_json is False