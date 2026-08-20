from unittest.mock import MagicMock

from scripts import smoke_multi_provider_gui_acceptance as smoke


def test_wait_for_coordinator_idle_returns_immediately_when_idle() -> None:
    application = MagicMock()
    window = MagicMock()
    window._execution_coordinator.is_running = False

    assert smoke._wait_for_coordinator_idle(application, window)
    application.processEvents.assert_not_called()


def test_wait_for_coordinator_idle_observes_thread_cleanup() -> None:
    application = MagicMock()
    window = MagicMock()
    coordinator = MagicMock()
    window._execution_coordinator = coordinator

    state = {"running": True}

    type(coordinator).is_running = property(lambda _self: state["running"])

    def process_events() -> None:
        state["running"] = False

    application.processEvents.side_effect = process_events

    assert smoke._wait_for_coordinator_idle(
        application,
        window,
        timeout_ms=100,
    )
    application.processEvents.assert_called()
