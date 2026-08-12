"""Resolve the Chromium executable used by DistanceCalculatorPro."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

_BUNDLED_BROWSER_RELATIVE_PATH = Path("app/browser/chromium/chrome.exe")


def bundled_browser_executable() -> Path | None:
    """Return packaged Chromium when running from a PyInstaller build."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if not isinstance(frozen_root, str) or not frozen_root:
        return None

    executable = (Path(frozen_root) / _BUNDLED_BROWSER_RELATIVE_PATH).resolve()
    if executable.is_file():
        return executable
    return None


def playwright_browser_executable() -> Path:
    """Return the Chromium executable managed by Playwright."""
    with sync_playwright() as playwright:
        return Path(playwright.chromium.executable_path).resolve()


def resolve_browser_executable() -> Path:
    """Prefer packaged Chromium, then fall back to Playwright's browser."""
    bundled = bundled_browser_executable()
    if bundled is not None:
        return bundled
    return playwright_browser_executable()
