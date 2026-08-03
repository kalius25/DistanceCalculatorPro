from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def page() -> MagicMock:
    return MagicMock()


@pytest.fixture
def locator() -> MagicMock:
    return MagicMock()
