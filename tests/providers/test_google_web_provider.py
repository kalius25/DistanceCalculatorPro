from unittest.mock import MagicMock, patch

import pytest

from app.engines.performance_models import ProviderPerformancePolicy
from app.exceptions import EngineException, ErrorCode
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.providers.google_web_provider import GoogleWebProvider


def make_request() -> RouteRequest:
    return RouteRequest(origin="A", destination="B")


def make_route() -> RouteOption:
    return RouteOption(
        summary="Fastest",
        distance_text="10 km",
        duration_text="15 phút",
        distance_km=10,
        duration_minutes=15,
    )


def test_batch_lifecycle_starts_and_closes_browser_once():
    browser = MagicMock()
    engine = MagicMock()
    provider = GoogleWebProvider(browser, engine)

    provider.start_batch()
    provider.start_batch()
    assert provider._batch_started
    browser.start.assert_called_once_with()

    provider.finish_batch()
    provider.finish_batch()
    assert not provider._batch_started
    browser.close.assert_called_once_with()


def test_calculate_reuses_batch_browser_and_closes_page():
    request = make_request()
    page = MagicMock()
    page.is_closed.return_value = False
    browser = MagicMock()
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)

    provider.start_batch()
    result = provider.calculate(request)

    assert result.success
    browser.start.assert_called_once_with()
    browser.close.assert_not_called()
    browser.new_page.assert_called_once_with()
    engine.find_routes.assert_called_once_with(page, request)
    page.close.assert_not_called()

    provider.finish_batch()
    page.close.assert_called_once_with()
    browser.close.assert_called_once_with()


def test_calculate_owns_browser_outside_batch():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)

    result = provider.calculate(make_request())

    assert result.success
    browser.start.assert_called_once_with()
    browser.close.assert_called_once_with()
    page.close.assert_called_once_with()


def test_calculate_engine_exception_returns_failed_result():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.side_effect = EngineException(
        "Google timeout",
        error_code=ErrorCode.ENGINE_ERROR,
        context={"timeout": 30},
    )
    provider = GoogleWebProvider(browser, engine)

    result = provider.calculate(make_request())

    assert not result.success
    assert result.provider == "google_web"
    assert result.error == "Google timeout"
    assert result.context == {"timeout": 30}
    page.close.assert_called_once_with()
    browser.close.assert_called_once_with()


def test_calculate_unexpected_exception_closes_resources():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.side_effect = RuntimeError("Unexpected bug")
    provider = GoogleWebProvider(browser, engine)

    with pytest.raises(RuntimeError, match="Unexpected bug"):
        provider.calculate(make_request())

    page.close.assert_called_once_with()
    browser.close.assert_called_once_with()


def test_calculate_closes_owned_browser_when_page_creation_fails():
    browser = MagicMock()
    browser.new_page.side_effect = RuntimeError("Page failed")
    provider = GoogleWebProvider(browser, MagicMock())

    with pytest.raises(RuntimeError, match="Page failed"):
        provider.calculate(make_request())

    browser.close.assert_called_once_with()


def test_constructor_uses_injected_dependencies_only():
    browser = MagicMock()
    engine = MagicMock()
    with (
        patch("app.providers.google_web_provider.BrowserManager") as browser_type,
        patch("app.providers.google_web_provider.GoogleMapsEngine") as engine_type,
    ):
        provider = GoogleWebProvider(browser, engine)
    browser_type.assert_not_called()
    engine_type.assert_not_called()
    assert provider._browser is browser
    assert provider._engine is engine


def test_calculate_does_not_close_already_closed_page():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = True
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)

    result = provider.calculate(make_request())

    assert result.success
    page.close.assert_not_called()
    browser.close.assert_called_once_with()


def test_calculate_ignores_playwright_error_while_closing_page():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    page.close.side_effect = __import__(
        "playwright.sync_api", fromlist=["Error"]
    ).Error("already closed")
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)

    result = provider.calculate(make_request())

    assert result.success
    browser.close.assert_called_once_with()


def test_calculate_prepares_recovery_and_records_page() -> None:
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    recovery = MagicMock()
    provider = GoogleWebProvider(browser, engine, recovery=recovery)

    result = provider.calculate(make_request())

    assert result.success
    recovery.prepare.assert_called_once_with()
    recovery.record_page_created.assert_called_once_with()
    recovery.recover.assert_not_called()


def test_engine_failure_requests_smart_recovery() -> None:
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    error = EngineException(
        "Target page, context or browser has been closed",
        error_code=ErrorCode.ENGINE_ERROR,
    )
    engine = MagicMock()
    engine.find_routes.side_effect = error
    recovery = MagicMock()
    provider = GoogleWebProvider(browser, engine, recovery=recovery)

    result = provider.calculate(make_request())

    assert not result.success
    recovery.recover.assert_called_once_with(error)


def test_playwright_page_creation_failure_requests_recovery() -> None:
    error_type = __import__("playwright.sync_api", fromlist=["Error"]).Error
    browser = MagicMock()
    error = error_type("browser disconnected")
    browser.new_page.side_effect = error
    recovery = MagicMock()
    provider = GoogleWebProvider(browser, MagicMock(), recovery=recovery)

    with pytest.raises(error_type):
        provider.calculate(make_request())

    recovery.recover.assert_called_once_with(error)


def test_batch_reuses_page_until_recycle_interval() -> None:
    browser = MagicMock()
    page_one = MagicMock()
    page_one.is_closed.return_value = False
    page_two = MagicMock()
    page_two.is_closed.return_value = False
    browser.new_page.side_effect = [page_one, page_two]
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    policy = ProviderPerformancePolicy(
        page_recycle_interval=2,
        slow_request_threshold_seconds=10.0,
    )
    provider = GoogleWebProvider(
        browser,
        engine,
        performance_policy=policy,
        clock=MagicMock(side_effect=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0]),
    )

    provider.start_batch()
    provider.calculate(make_request())
    provider.calculate(make_request())
    provider.calculate(make_request())

    assert browser.new_page.call_count == 2
    assert engine.find_routes.call_args_list[0].args[0] is page_one
    assert engine.find_routes.call_args_list[1].args[0] is page_one
    assert engine.find_routes.call_args_list[2].args[0] is page_two
    page_one.close.assert_called_once_with()

    metrics = provider.performance_metrics
    assert metrics.requests_started == 3
    assert metrics.requests_completed == 3
    assert metrics.requests_failed == 0
    assert metrics.pages_created == 2
    assert metrics.pages_recycled == 1
    assert metrics.total_request_seconds == 3.0
    assert metrics.average_request_seconds == 1.0
    assert metrics.maximum_request_seconds == 1.0

    provider.finish_batch()
    page_two.close.assert_called_once_with()


def test_slow_request_recycles_page() -> None:
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    diagnostics = MagicMock()
    provider = GoogleWebProvider(
        browser,
        engine,
        diagnostics=diagnostics,
        performance_policy=ProviderPerformancePolicy(
            page_recycle_interval=50,
            slow_request_threshold_seconds=2.0,
        ),
        clock=MagicMock(side_effect=[10.0, 13.0]),
    )

    provider.start_batch()
    result = provider.calculate(make_request())

    assert result.success
    page.close.assert_called_once_with()
    assert provider.performance_metrics.slow_requests == 1
    assert provider.performance_metrics.pages_recycled == 1
    diagnostics.trace_browser.assert_called_once()


def test_closed_reused_page_is_replaced() -> None:
    browser = MagicMock()
    closed_page = MagicMock()
    closed_page.is_closed.return_value = True
    replacement = MagicMock()
    replacement.is_closed.return_value = False
    browser.new_page.return_value = replacement
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)
    provider._page = closed_page

    provider.start_batch()
    result = provider.calculate(make_request())

    assert result.success
    browser.new_page.assert_called_once_with()
    engine.find_routes.assert_called_once_with(replacement, result.request)


def test_page_health_error_replaces_page() -> None:
    error_type = __import__("playwright.sync_api", fromlist=["Error"]).Error
    browser = MagicMock()
    broken_page = MagicMock()
    broken_page.is_closed.side_effect = error_type("page failed")
    replacement = MagicMock()
    replacement.is_closed.return_value = False
    browser.new_page.return_value = replacement
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)
    provider._page = broken_page

    provider.start_batch()
    result = provider.calculate(make_request())

    assert result.success
    engine.find_routes.assert_called_once_with(replacement, result.request)


def test_unexpected_failure_records_metrics_and_recycles_page() -> None:
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.side_effect = RuntimeError("unexpected")
    provider = GoogleWebProvider(browser, engine)

    provider.start_batch()
    with pytest.raises(RuntimeError, match="unexpected"):
        provider.calculate(make_request())

    metrics = provider.performance_metrics
    assert metrics.requests_started == 1
    assert metrics.requests_failed == 1
    assert metrics.pages_recycled == 1
    page.close.assert_called_once_with()


def test_starting_new_batch_resets_performance_metrics() -> None:
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)

    provider.start_batch()
    provider.calculate(make_request())
    assert provider.performance_metrics.requests_completed == 1
    provider.finish_batch()

    provider.start_batch()

    assert provider.performance_metrics.requests_started == 0
    assert provider.performance_metrics.requests_completed == 0
    provider.finish_batch()
