"""Google Maps web provider implementation."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from app.diagnostics import DiagnosticsManager
from app.engines.browser_manager import BrowserManager
from app.engines.browser_recovery import BrowserRecoveryManager
from app.engines.google_maps_engine import GoogleMapsEngine
from app.engines.performance_models import (
    ProviderPerformanceMetrics,
    ProviderPerformancePolicy,
    ProviderPerformanceSnapshot,
)
from app.exceptions import EngineException
from app.logging import LoggingManager
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider

logger = LoggingManager.get_logger(__name__)
Clock = Callable[[], float]


class GoogleWebProvider(BaseProvider):
    """Calculate routes with a shared browser and adaptively recycled page."""

    PROVIDER_NAME = "google_web"

    def __init__(
        self,
        browser: BrowserManager,
        engine: GoogleMapsEngine,
        recovery: BrowserRecoveryManager | None = None,
        diagnostics: DiagnosticsManager | None = None,
        performance_policy: ProviderPerformancePolicy | None = None,
        clock: Clock = perf_counter,
    ) -> None:
        self._browser = browser
        self._engine = engine
        self._diagnostics = diagnostics or DiagnosticsManager()
        self._recovery = recovery or BrowserRecoveryManager(
            browser,
            diagnostics=self._diagnostics,
            logger=logger,
        )
        self._performance_policy = performance_policy or ProviderPerformancePolicy()
        self._clock = clock
        self._performance = ProviderPerformanceMetrics()
        self._batch_started = False
        self._page: Page | None = None
        self._requests_on_page = 0

    @property
    def performance_metrics(self) -> ProviderPerformanceSnapshot:
        """Return an immutable snapshot of current provider metrics."""
        return self._performance.snapshot

    def start_batch(self) -> None:
        if self._batch_started:
            return
        self._performance = ProviderPerformanceMetrics()
        self._browser.start()
        self._batch_started = True

    def finish_batch(self) -> None:
        if not self._batch_started:
            return
        self._discard_page(recycled=False)
        self._browser.close()
        self._batch_started = False

    def calculate(self, request: RouteRequest) -> RouteResult:
        """Calculate one route while reusing a healthy page within the batch."""
        owns_browser = not self._batch_started
        if owns_browser:
            self.start_batch()

        started_at = self._clock()
        self._performance.requests_started += 1
        try:
            self._recovery.prepare()
            page = self._acquire_page()
            routes = self._engine.find_routes(page, request)
            self._record_page_use()
            self._performance.requests_completed += 1
            return RouteResult(
                success=True,
                request=request,
                provider=self.PROVIDER_NAME,
                routes=routes,
            )
        except EngineException as exc:
            self._performance.requests_failed += 1
            self._recovery.recover(exc)
            self._discard_page(recycled=True)
            return RouteResult(
                success=False,
                request=request,
                provider=self.PROVIDER_NAME,
                error=str(exc),
                error_code=exc.error_code,
                context=exc.context,
                exception=exc,
            )
        except PlaywrightError as exc:
            self._performance.requests_failed += 1
            self._recovery.recover(exc)
            self._discard_page(recycled=True)
            raise
        except Exception:
            self._performance.requests_failed += 1
            self._discard_page(recycled=True)
            raise
        finally:
            elapsed = self._clock() - started_at
            self._performance.record_duration(elapsed)
            if elapsed >= self._performance_policy.slow_request_threshold_seconds:
                self._performance.slow_requests += 1
                self._discard_page(recycled=True)
            elif self._requests_on_page >= (
                self._performance_policy.page_recycle_interval
            ):
                self._discard_page(recycled=True)
            if owns_browser:
                self.finish_batch()

    def _acquire_page(self) -> Page:
        if self._page is not None:
            try:
                if not self._page.is_closed():
                    return self._page
            except PlaywrightError:
                pass
            self._page = None
            self._requests_on_page = 0

        self._page = self._browser.new_page()
        self._requests_on_page = 0
        self._performance.pages_created += 1
        self._recovery.record_page_created()
        return self._page

    def _discard_page(self, *, recycled: bool) -> None:
        page, self._page = self._page, None
        self._requests_on_page = 0
        if page is None:
            return
        try:
            if not page.is_closed():
                page.close()
        except PlaywrightError:
            pass
        if recycled:
            self._performance.pages_recycled += 1
            self._diagnostics.trace_browser(
                logger,
                "PAGE_RECYCLED",
                pages_recycled=self._performance.pages_recycled,
            )

    def _record_page_use(self) -> None:
        self._requests_on_page += 1
