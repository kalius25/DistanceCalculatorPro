from pathlib import Path
from unittest.mock import MagicMock, patch

import app.engines.browser_executable as browser_executable


def test_bundled_browser_returns_none_outside_frozen_runtime(
    monkeypatch,
) -> None:
    import sys

    monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    assert browser_executable.bundled_browser_executable() is None


def test_bundled_browser_returns_packaged_executable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import sys

    executable = (
        tmp_path / "app" / "browser" / "chromium" / "chrome.exe"
    )
    executable.parent.mkdir(parents=True)
    executable.write_bytes(b"chrome")
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    assert (
        browser_executable.bundled_browser_executable()
        == executable.resolve()
    )


def test_bundled_browser_returns_none_when_packaged_file_missing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import sys

    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    assert browser_executable.bundled_browser_executable() is None


def test_playwright_browser_executable_returns_resolved_path(
    tmp_path: Path,
) -> None:
    executable = tmp_path / "chrome.exe"
    playwright = MagicMock()
    playwright.chromium.executable_path = str(executable)
    context = MagicMock()
    context.__enter__.return_value = playwright

    with patch.object(
        browser_executable,
        "sync_playwright",
        return_value=context,
    ):
        result = browser_executable.playwright_browser_executable()

    assert result == executable.resolve()


def test_resolve_browser_executable_prefers_bundled(
    tmp_path: Path,
) -> None:
    bundled = tmp_path / "bundled.exe"

    with (
        patch.object(
            browser_executable,
            "bundled_browser_executable",
            return_value=bundled,
        ),
        patch.object(
            browser_executable,
            "playwright_browser_executable",
        ) as playwright_resolver,
    ):
        result = browser_executable.resolve_browser_executable()

    assert result == bundled
    playwright_resolver.assert_not_called()


def test_resolve_browser_executable_falls_back_to_playwright(
    tmp_path: Path,
) -> None:
    playwright_executable = tmp_path / "chrome.exe"

    with (
        patch.object(
            browser_executable,
            "bundled_browser_executable",
            return_value=None,
        ),
        patch.object(
            browser_executable,
            "playwright_browser_executable",
            return_value=playwright_executable,
        ),
    ):
        result = browser_executable.resolve_browser_executable()

    assert result == playwright_executable



def test_bundled_browser_ignores_empty_meipass(monkeypatch) -> None:
    import sys

    monkeypatch.setattr(sys, "_MEIPASS", "", raising=False)

    assert browser_executable.bundled_browser_executable() is None


def test_bundled_browser_ignores_non_string_meipass(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import sys

    monkeypatch.setattr(sys, "_MEIPASS", tmp_path, raising=False)

    assert browser_executable.bundled_browser_executable() is None
