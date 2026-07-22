from __future__ import annotations

from unittest.mock import Mock

from app.exceptions import ErrorCode
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult


def make_request() -> RouteRequest:
    """
    Create a lightweight RouteRequest mock for RouteResult tests.
    """
    return Mock(spec=RouteRequest)


def test_route_result_defaults():
    request = make_request()

    result = RouteResult(
        success=True,
        request=request,
        provider="google_web",
    )

    assert result.success is True
    assert result.request is request
    assert result.provider == "google_web"

    assert result.routes == []
    assert result.selected_route == 0

    assert result.error == ""
    assert result.error_code is None
    assert result.context == {}


def test_best_route_returns_none_when_routes_empty():
    request = make_request()

    result = RouteResult(
        success=True,
        request=request,
        provider="google_web",
    )

    assert result.best_route is None

def test_best_route_returns_none_when_selected_route_out_of_range():
    request = make_request()

    route = Mock(spec=RouteOption)

    result = RouteResult(
        success=True,
        request=request,
        provider="google_web",
        routes=[route],
        selected_route=5,
    )

    assert result.best_route is None


def test_best_route_returns_selected_route():
    request = make_request()

    route1 = Mock(spec=RouteOption)
    route2 = Mock(spec=RouteOption)

    result = RouteResult(
        success=True,
        request=request,
        provider="google_web",
        routes=[route1, route2],
        selected_route=1,
    )

    assert result.best_route is route2


def test_route_result_error_metadata():
    request = make_request()

    result = RouteResult(
        success=False,
        request=request,
        provider="google_web",
        error="Navigation timeout",
        error_code=ErrorCode.ENGINE_ERROR,
        context={
            "timeout": 30,
            "provider": "google_web",
        },
    )

    assert result.error == "Navigation timeout"

    assert result.error_code is ErrorCode.ENGINE_ERROR

    assert result.context == {
        "timeout": 30,
        "provider": "google_web",
    }


def test_route_result_context_is_mutable():
    request = make_request()

    result = RouteResult(
        success=False,
        request=request,
        provider="google_web",
    )

    result.context["retry"] = 2

    assert result.context["retry"] == 2

def test_best_route_returns_none_when_selected_route_negative():
    request = make_request()

    route = Mock(spec=RouteOption)

    result = RouteResult(
        success=True,
        request=request,
        provider="google_web",
        routes=[route],
        selected_route=-1,
    )

    assert result.best_route is None