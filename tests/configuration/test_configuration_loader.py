from app.configuration import (
    AppConfig,
    BrowserConfig,
    ConfigurationLoader,
    DebugConfig,
    ExcelConfig,
    LoggingConfig,
    ProviderConfig,
)


def test_load_returns_app_config():
    config = ConfigurationLoader.load()

    assert isinstance(config, AppConfig)


def test_load_creates_all_configuration_sections():
    config = ConfigurationLoader.load()

    assert isinstance(config.browser, BrowserConfig)
    assert isinstance(config.provider, ProviderConfig)
    assert isinstance(config.logging, LoggingConfig)
    assert isinstance(config.excel, ExcelConfig)
    assert isinstance(config.debug, DebugConfig)


def test_load_returns_new_instance_each_time():
    config1 = ConfigurationLoader.load()
    config2 = ConfigurationLoader.load()

    assert config1 is not config2
    assert config1 == config2