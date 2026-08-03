"""Startup environment validation for the desktop application."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from playwright.sync_api import sync_playwright

from app.configuration.models import AppConfig

BrowserExecutableResolver = Callable[[], Path]


@dataclass(frozen=True, slots=True)
class StartupIssue:
    """One actionable startup validation failure."""

    component: str
    message: str


class StartupValidationError(RuntimeError):
    """Raised when the application cannot safely start."""

    def __init__(self, issues: tuple[StartupIssue, ...]) -> None:
        self.issues = issues
        details = "\n".join(f"- {issue.component}: {issue.message}" for issue in issues)
        super().__init__(f"Startup validation failed:\n{details}")


class StartupValidator:
    """Validate configuration, writable directories and Chromium availability."""

    def __init__(
        self,
        browser_executable_resolver: BrowserExecutableResolver | None = None,
    ) -> None:
        self._browser_executable_resolver = (
            browser_executable_resolver or self._resolve_browser_executable
        )

    def validate(self, configuration: AppConfig) -> None:
        issues: list[StartupIssue] = []
        self._validate_configuration(configuration, issues)
        self._validate_directory("Logging", configuration.logging.directory, issues)
        self._validate_directory("Output", configuration.excel.export_directory, issues)
        self._validate_browser(issues)
        if issues:
            raise StartupValidationError(tuple(issues))

    @staticmethod
    def _validate_configuration(
        configuration: AppConfig,
        issues: list[StartupIssue],
    ) -> None:
        if configuration.browser.timeout <= 0:
            issues.append(StartupIssue("Browser", "Timeout must be greater than zero."))
        if configuration.google_maps.action_timeout <= 0:
            issues.append(
                StartupIssue("Google Maps", "Action timeout must be greater than zero.")
            )
        if configuration.browser.viewport_width <= 0:
            issues.append(StartupIssue("Browser", "Viewport width must be positive."))
        if configuration.browser.viewport_height <= 0:
            issues.append(StartupIssue("Browser", "Viewport height must be positive."))

    @staticmethod
    def _validate_directory(
        component: str,
        directory: str,
        issues: list[StartupIssue],
    ) -> None:
        path = Path(directory)
        try:
            path.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=path, prefix=".dcp-write-test-", delete=True):
                pass
        except OSError as error:
            issues.append(
                StartupIssue(component, f"Directory is not writable: {path} ({error})")
            )

    def _validate_browser(self, issues: list[StartupIssue]) -> None:
        try:
            executable = self._browser_executable_resolver()
        except Exception as error:
            issues.append(
                StartupIssue("Playwright", f"Unable to inspect Chromium: {error}")
            )
            return
        if not executable.is_file():
            issues.append(
                StartupIssue(
                    "Chromium",
                    "Browser executable is missing. Run: playwright install chromium",
                )
            )

    @staticmethod
    def _resolve_browser_executable() -> Path:
        with sync_playwright() as playwright:
            return Path(playwright.chromium.executable_path)
