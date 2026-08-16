from pathlib import Path
from unittest.mock import patch

import pytest

from app.release.stage_browser import main, stage_browser


def test_stage_browser_copies_executable_directory(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    executable = source / "chrome.exe"
    executable.write_bytes(b"chrome")
    (source / "resources.pak").write_bytes(b"resource")
    destination = tmp_path / "destination"

    with patch(
        "app.release.stage_browser.playwright_browser_executable",
        return_value=executable,
    ):
        staged = stage_browser(destination)

    assert staged == destination / "chrome.exe"
    assert staged.read_bytes() == b"chrome"
    assert (destination / "resources.pak").read_bytes() == b"resource"


def test_stage_browser_replaces_existing_destination(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    executable = source / "chrome.exe"
    executable.write_bytes(b"new")
    destination = tmp_path / "destination"
    destination.mkdir()
    (destination / "old.txt").write_text("old", encoding="utf-8")

    with patch(
        "app.release.stage_browser.playwright_browser_executable",
        return_value=executable,
    ):
        stage_browser(destination)

    assert not (destination / "old.txt").exists()


def test_stage_browser_rejects_missing_source_executable(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing" / "chrome.exe"

    with (
        patch(
            "app.release.stage_browser.playwright_browser_executable",
            return_value=missing,
        ),
        pytest.raises(
            FileNotFoundError,
            match="Playwright Chromium executable is missing",
        ),
    ):
        stage_browser(tmp_path / "destination")


def test_stage_browser_main_reports_staged_executable(
    tmp_path: Path,
    capsys,
) -> None:
    destination = tmp_path / "destination"
    staged = destination / "chrome.exe"

    with patch(
        "app.release.stage_browser.stage_browser",
        return_value=staged,
    ):
        result = main([str(destination)])

    assert result == 0
    assert "Bundled Chromium staged:" in capsys.readouterr().out



def test_stage_browser_rejects_missing_staged_executable(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    executable = source / "chrome.exe"
    executable.write_bytes(b"chrome")
    destination = tmp_path / "destination"

    with (
        patch(
            "app.release.stage_browser.playwright_browser_executable",
            return_value=executable,
        ),
        patch("app.release.stage_browser.shutil.copytree"),
        pytest.raises(
            FileNotFoundError,
            match="Staged Chromium executable is missing",
        ),
    ):
        stage_browser(destination)
