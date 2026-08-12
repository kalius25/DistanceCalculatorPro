from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.configuration.configuration_loader import ConfigurationLoader
from app.presentation.startup import (
    StartupIssue,
    StartupValidationError,
    StartupValidator,
)


def test_startup_validation_error_formats_all_issues() -> None:
    error = StartupValidationError(
        (
            StartupIssue("Logging", "not writable"),
            StartupIssue("Chromium", "missing"),
        )
    )

    assert error.issues[0].component == "Logging"
    assert str(error) == (
        "Startup validation failed:\n" "- Logging: not writable\n" "- Chromium: missing"
    )


def test_validator_accepts_valid_configuration(tmp_path: Path) -> None:
    configuration = ConfigurationLoader.load()
    configuration = configuration.__class__(
        browser=configuration.browser,
        google_maps=configuration.google_maps,
        provider=configuration.provider,
        logging=configuration.logging.__class__(
            level="INFO",
            directory=str(tmp_path / "logs"),
            filename="app.log",
        ),
        excel=configuration.excel.__class__(
            export_directory=str(tmp_path / "output"),
            auto_fit_columns=True,
        ),
        debug=configuration.debug,
    )
    executable = tmp_path / "chromium.exe"
    executable.touch()

    StartupValidator(lambda: executable).validate(configuration)

    assert (tmp_path / "logs").is_dir()
    assert (tmp_path / "output").is_dir()


def test_validator_reports_configuration_directory_and_browser_issues(
    tmp_path: Path,
) -> None:
    configuration = ConfigurationLoader.load()
    blocked = tmp_path / "blocked"
    blocked.write_text("not a directory", encoding="utf-8")
    browser = configuration.browser.__class__(
        headless=configuration.browser.headless,
        timeout=0,
        slow_mo=configuration.browser.slow_mo,
        viewport_width=0,
        viewport_height=0,
        user_agent=configuration.browser.user_agent,
        locale=configuration.browser.locale,
    )
    maps = configuration.google_maps.__class__(
        base_url=configuration.google_maps.base_url,
        action_timeout=0,
    )
    configuration = configuration.__class__(
        browser=browser,
        google_maps=maps,
        provider=configuration.provider,
        logging=configuration.logging.__class__(
            level="INFO",
            directory=str(blocked),
            filename="app.log",
        ),
        excel=configuration.excel.__class__(
            export_directory=str(tmp_path / "output"),
            auto_fit_columns=True,
        ),
        debug=configuration.debug,
    )

    with pytest.raises(StartupValidationError) as captured:
        StartupValidator(lambda: tmp_path / "missing-browser").validate(configuration)

    messages = [issue.message for issue in captured.value.issues]
    assert "Timeout must be greater than zero." in messages
    assert "Action timeout must be greater than zero." in messages
    assert "Viewport width must be positive." in messages
    assert "Viewport height must be positive." in messages
    assert any("Directory is not writable" in message for message in messages)
    assert any("playwright install chromium" in message for message in messages)


def test_validator_reports_browser_inspection_failure(tmp_path: Path) -> None:
    configuration = ConfigurationLoader.load()
    configuration = configuration.__class__(
        browser=configuration.browser,
        google_maps=configuration.google_maps,
        provider=configuration.provider,
        logging=configuration.logging.__class__(
            level="INFO",
            directory=str(tmp_path / "logs"),
            filename="app.log",
        ),
        excel=configuration.excel.__class__(
            export_directory=str(tmp_path / "output"),
            auto_fit_columns=True,
        ),
        debug=configuration.debug,
    )

    def fail() -> Path:
        raise RuntimeError("Playwright unavailable")

    with pytest.raises(StartupValidationError, match="Playwright unavailable"):
        StartupValidator(fail).validate(configuration)


def test_validate_can_skip_browser_check(tmp_path: Path) -> None:
    configuration = MagicMock()
    configuration.browser.timeout = 30
    configuration.browser.viewport_width = 1280
    configuration.browser.viewport_height = 720
    configuration.google_maps.action_timeout = 10
    configuration.logging.directory = str(tmp_path / "logs")
    configuration.excel.export_directory = str(tmp_path / "output")

    resolver = MagicMock(side_effect=RuntimeError("browser unavailable"))
    validator = StartupValidator(resolver)

    validator.validate(configuration, validate_browser=False)

    resolver.assert_not_called()
