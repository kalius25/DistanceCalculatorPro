from dataclasses import FrozenInstanceError

import pytest

from app.configuration import ConfigurationLoader


def test_browser_configuration_is_immutable():
    config = ConfigurationLoader.load()

    with pytest.raises(FrozenInstanceError):
        config.browser.timeout = 60


def test_provider_configuration_is_immutable():
    config = ConfigurationLoader.load()

    with pytest.raises(FrozenInstanceError):
        config.provider.retry_count = 5


def test_logging_configuration_is_immutable():
    config = ConfigurationLoader.load()

    with pytest.raises(FrozenInstanceError):
        config.logging.level = "DEBUG"


def test_excel_configuration_is_immutable():
    config = ConfigurationLoader.load()

    with pytest.raises(FrozenInstanceError):
        config.excel.export_directory = "temp"


def test_debug_configuration_is_immutable():
    config = ConfigurationLoader.load()

    with pytest.raises(FrozenInstanceError):
        config.debug.save_html = True


def test_google_maps_configuration_is_immutable():
    config = ConfigurationLoader.load()

    with pytest.raises(FrozenInstanceError):
        config.google_maps.action_timeout = 60_000
