from unittest.mock import MagicMock

import pytest


@pytest.fixture
def page():
    return MagicMock()


@pytest.fixture
def locator():
    return MagicMock()