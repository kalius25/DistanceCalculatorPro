from __future__ import annotations

import pytest

from app.providers.base_provider import BaseProvider


class DummyProvider(BaseProvider):
    """Concrete implementation used only for testing."""

    def calculate(self, request):
        return super().calculate(request)


def test_calculate_raises_not_implemented():
    provider = DummyProvider()

    with pytest.raises(NotImplementedError):
        provider.calculate(None)
