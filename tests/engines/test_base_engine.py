import pytest

from app.engines.base_engine import BaseEngine


class DummyEngine(BaseEngine):
    def find_routes(self, page, request):
        return super().find_routes(page, request)


def test_find_routes_not_implemented():
    engine = DummyEngine()

    with pytest.raises(NotImplementedError):
        engine.find_routes(None, None)
