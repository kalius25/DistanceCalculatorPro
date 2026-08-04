from unittest.mock import patch

import pytest

from app.benchmarks import MemorySampler

pytestmark = pytest.mark.benchmark


def test_memory_sampler_owns_and_stops_new_trace_session() -> None:
    sampler = MemorySampler()

    with patch("app.benchmarks.memory_sampler.tracemalloc") as tracing:
        tracing.is_tracing.side_effect = [False, True, True]
        tracing.get_traced_memory.return_value = (10, 20)

        sampler.start()
        assert sampler.peak_bytes() == 20
        sampler.stop()

    tracing.start.assert_called_once_with()
    tracing.reset_peak.assert_called_once_with()
    tracing.stop.assert_called_once_with()


def test_memory_sampler_preserves_existing_trace_and_handles_inactive_state() -> None:
    sampler = MemorySampler()

    with patch("app.benchmarks.memory_sampler.tracemalloc") as tracing:
        tracing.is_tracing.side_effect = [True, False, True]

        sampler.start()
        assert sampler.peak_bytes() == 0
        sampler.stop()

    tracing.start.assert_not_called()
    tracing.stop.assert_not_called()
