"""Deterministic route provider for end-to-end reliability scenarios."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass

from app.exceptions import ErrorCode
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider


@dataclass(frozen=True, slots=True)
class FakeRouteOutcome:
    """One scripted response returned by :class:`ScriptedRouteProvider`."""

    success: bool
    distance_km: float = 0.0
    duration_minutes: int = 0
    error: str = ""
    error_code: ErrorCode | None = None
    exception: Exception | None = None

    @classmethod
    def route(
        cls,
        distance_km: float,
        duration_minutes: int = 10,
    ) -> FakeRouteOutcome:
        return cls(True, distance_km, duration_minutes)

    @classmethod
    def failure(
        cls,
        message: str,
        error_code: ErrorCode = ErrorCode.PROVIDER_ERROR,
    ) -> FakeRouteOutcome:
        return cls(False, error=message, error_code=error_code)


class ScriptedRouteProvider(BaseProvider):
    """Return predictable outcomes without browser, network, or Google Maps."""

    def __init__(
        self,
        scripts: dict[tuple[str, str], Iterable[FakeRouteOutcome]] | None = None,
        *,
        default_distance_km: float = 1.0,
    ) -> None:
        self._scripts: defaultdict[
            tuple[str, str],
            deque[FakeRouteOutcome],
        ] = defaultdict(deque)
        for key, outcomes in (scripts or {}).items():
            self._scripts[key].extend(outcomes)
        self._default_distance_km = default_distance_km
        self.requests = 0
        self.batches_started = 0
        self.batches_finished = 0

    def start_batch(self) -> None:
        self.batches_started += 1

    def finish_batch(self) -> None:
        self.batches_finished += 1

    def calculate(self, request: RouteRequest) -> RouteResult:
        self.requests += 1
        key = (request.origin, request.destination)
        outcomes = self._scripts[key]
        outcome = (
            outcomes.popleft()
            if outcomes
            else FakeRouteOutcome.route(self._default_distance_km)
        )
        if outcome.exception is not None:
            raise outcome.exception
        if not outcome.success:
            return RouteResult(
                False,
                request,
                "scripted_e2e",
                error=outcome.error,
                error_code=outcome.error_code,
            )
        route = RouteOption(
            summary=f"{request.origin} to {request.destination}",
            distance_text=f"{outcome.distance_km:g} km",
            distance_km=outcome.distance_km,
            duration_text=f"{outcome.duration_minutes} min",
            duration_minutes=outcome.duration_minutes,
        )
        return RouteResult(True, request, "scripted_e2e", routes=[route])


__all__ = ["FakeRouteOutcome", "ScriptedRouteProvider"]
