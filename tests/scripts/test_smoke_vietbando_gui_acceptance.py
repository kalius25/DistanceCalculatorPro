from unittest.mock import MagicMock

from app.exceptions import EngineException, ErrorCode
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from scripts import smoke_vietbando_gui_acceptance as smoke


def test_distance_is_success_rejects_blank_and_error_cells() -> None:
    assert not smoke._distance_is_success(None)
    assert not smoke._distance_is_success("")
    assert not smoke._distance_is_success("ERROR: VietBanDo browser operation failed.")
    assert smoke._distance_is_success(128.1)
    assert smoke._distance_is_success("128.1")


def test_print_route_diagnostics_includes_engine_cause(
    capsys: object,
) -> None:
    request = RouteRequest(origin="A", destination="B")
    cause = RuntimeError("low-level browser detail")
    exception = EngineException(
        "VietBanDo browser operation failed.",
        error_code=ErrorCode.ENGINE_ERROR,
        cause=cause,
        context={"travel_mode": "driving"},
    )
    result = RouteResult(
        success=False,
        request=request,
        provider="vietbando_web",
        error=str(exception),
        error_code=ErrorCode.ENGINE_ERROR,
        context=exception.context,
        exception=exception,
    )

    smoke._print_route_diagnostics([result])

    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "success: False" in output
    assert "provider: vietbando_web" in output
    assert "ENGINE_ERROR" in output
    assert "VietBanDo browser operation failed." in output
    assert "RuntimeError: low-level browser detail" in output


def test_print_route_diagnostics_ignores_non_route_results() -> None:
    smoke._print_route_diagnostics("not-a-list")
    smoke._print_route_diagnostics([MagicMock()])
