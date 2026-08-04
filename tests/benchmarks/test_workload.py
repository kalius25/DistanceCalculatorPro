import pytest

from app.benchmarks import RouteWorkloadGenerator

pytestmark = pytest.mark.benchmark


def test_workload_generator_creates_repeatable_requests() -> None:
    requests = list(RouteWorkloadGenerator().generate(2))

    assert [(item.origin, item.destination) for item in requests] == [
        ("Origin 0", "Destination 0"),
        ("Origin 1", "Destination 1"),
    ]


def test_workload_generator_rejects_non_positive_rows() -> None:
    with pytest.raises(ValueError, match="positive"):
        list(RouteWorkloadGenerator().generate(0))
