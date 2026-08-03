from app.configuration import ConfigurationLoader


def test_multiple_loads_return_equal_configs():
    config1 = ConfigurationLoader.load()
    config2 = ConfigurationLoader.load()

    assert config1 == config2


def test_multiple_loads_return_different_instances():
    config1 = ConfigurationLoader.load()
    config2 = ConfigurationLoader.load()

    assert config1 is not config2
