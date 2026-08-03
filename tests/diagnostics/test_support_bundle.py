from __future__ import annotations

import json
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.diagnostics import (
    SupportBundleBuilder,
    SupportBundleError,
    SupportBundlePolicy,
)


def test_policy_rejects_invalid_limits() -> None:
    with pytest.raises(ValueError, match="max_bundle_bytes"):
        SupportBundlePolicy(max_bundle_bytes=0)
    with pytest.raises(ValueError, match="max_source_file_bytes"):
        SupportBundlePolicy(max_source_file_bytes=0)
    with pytest.raises(ValueError, match="max_files"):
        SupportBundlePolicy(max_files=0)


def test_builder_creates_redacted_bundle_and_manifest(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    diagnostics = logs / "debug"
    logs.mkdir()
    diagnostics.mkdir()
    (logs / "application.log").write_text(
        "route=10.762622,106.660172 email=user@example.com token=abc\n",
        encoding="utf-8",
    )
    (diagnostics / "parser.json").write_text(
        '{"password":"secret","phone":"0901234567"}',
        encoding="utf-8",
    )
    (diagnostics / "page.html").write_text("<html>private</html>", encoding="utf-8")
    (diagnostics / "screen.png").write_bytes(b"png")

    output = tmp_path / "support.zip"
    result = SupportBundleBuilder(
        app_name="DistanceCalculatorPro",
        app_version="1.2.0-rc4",
        log_directory=logs,
        diagnostics_directory=diagnostics,
    ).build(output)

    assert result.output_path == output
    assert result.bundle_size_bytes == output.stat().st_size
    assert any("HTML excluded" in item for item in result.skipped)
    assert any("screenshot excluded" in item for item in result.skipped)

    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
        assert "manifest.json" in names
        assert "README.txt" in names
        assert "logs/application.log" in names
        text = archive.read("logs/application.log").decode("utf-8")
        assert "10.762622,106.660172" not in text
        assert "[COORDINATES_REDACTED]" in text
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["application"]["version"] == "1.2.0-rc4"
        assert manifest["privacy"]["workbook_included"] is False


def test_builder_skips_missing_locked_large_and_unsupported_files(
    tmp_path: Path,
) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    large = logs / "large.log"
    large.write_text("x" * 20, encoding="utf-8")
    unsupported = logs / "data.bin"
    unsupported.write_bytes(b"data")
    locked = logs / "locked.log"
    locked.write_text("locked", encoding="utf-8")

    builder = SupportBundleBuilder(
        app_name="DCP",
        app_version="test",
        log_directory=logs,
        diagnostics_directory=tmp_path / "missing",
        policy=SupportBundlePolicy(max_source_file_bytes=10),
    )

    original_read_text = Path.read_text

    def read_text(path: Path, *args: object, **kwargs: object) -> str:
        if path.name == "locked.log":
            raise PermissionError("locked")
        return original_read_text(path, *args, **kwargs)

    with patch.object(Path, "read_text", read_text):
        result = builder.build(tmp_path / "support.zip")

    assert any("source file too large" in item for item in result.skipped)
    assert any("unsupported artifact type" in item for item in result.skipped)
    assert any("unavailable" in item for item in result.skipped)


def test_builder_enforces_file_and_bundle_limits(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "one.log").write_text("one", encoding="utf-8")
    (logs / "two.log").write_text("two", encoding="utf-8")

    limited = SupportBundleBuilder(
        app_name="DCP",
        app_version="test",
        log_directory=logs,
        diagnostics_directory=tmp_path / "missing",
        policy=SupportBundlePolicy(max_files=1),
    ).build(tmp_path / "limited.zip")
    assert len(limited.included) == 1
    assert any("file limit reached" in item for item in limited.skipped)

    builder = SupportBundleBuilder(
        app_name="DCP",
        app_version="test",
        log_directory=logs,
        diagnostics_directory=tmp_path / "missing",
        policy=SupportBundlePolicy(max_bundle_bytes=1),
    )
    with pytest.raises(SupportBundleError, match="size limit"):
        builder.build(tmp_path / "too-small.zip")
    assert not (tmp_path / "too-small.zip").exists()


def test_builder_wraps_os_errors_and_cleans_temporary_file(tmp_path: Path) -> None:
    builder = SupportBundleBuilder(
        app_name="DCP",
        app_version="test",
        log_directory=tmp_path / "missing",
        diagnostics_directory=tmp_path / "missing-debug",
    )
    output = tmp_path / "support.zip"

    with patch("app.diagnostics.support_bundle.os.replace", side_effect=OSError("no")):
        with pytest.raises(SupportBundleError, match="Unable to create"):
            builder.build(output)

    assert not output.exists()
    assert not list(tmp_path.glob(".*.tmp"))


def test_builder_exposes_policy_and_can_include_screenshot(tmp_path: Path) -> None:
    diagnostics = tmp_path / "debug"
    diagnostics.mkdir()
    screenshot = diagnostics / "screen.png"
    screenshot.write_bytes(b"png")
    policy = SupportBundlePolicy(include_screenshots=True)
    builder = SupportBundleBuilder(
        app_name="DCP",
        app_version="test",
        log_directory=tmp_path / "missing",
        diagnostics_directory=diagnostics,
        policy=policy,
    )

    assert builder.policy is policy
    result = builder.build(tmp_path / "support.zip")

    assert result.included[0].archive_path == "diagnostics/screen.png"
    assert result.included[0].redacted is False


def test_builder_checks_final_archive_size_after_manifest(tmp_path: Path) -> None:
    builder = SupportBundleBuilder(
        app_name="DCP",
        app_version="test",
        log_directory=tmp_path / "missing",
        diagnostics_directory=tmp_path / "missing-debug",
        policy=SupportBundlePolicy(max_bundle_bytes=10),
    )

    with pytest.raises(SupportBundleError, match="size limit"):
        builder.build(tmp_path / "support.zip")


def test_builder_cleans_up_and_reraises_unexpected_error(tmp_path: Path) -> None:
    builder = SupportBundleBuilder(
        app_name="DCP",
        app_version="test",
        log_directory=tmp_path / "missing",
        diagnostics_directory=tmp_path / "missing-debug",
    )

    with patch(
        "app.diagnostics.support_bundle.zipfile.ZipFile",
        side_effect=RuntimeError("unexpected"),
    ):
        with pytest.raises(RuntimeError, match="unexpected"):
            builder.build(tmp_path / "support.zip")

    assert not list(tmp_path.glob(".*.tmp"))
