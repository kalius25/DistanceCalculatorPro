from pathlib import Path
from unittest.mock import patch

from app.release.stable_release_gate import (
    STABLE_VERSION,
    main,
    validate_stable_release,
)


def _write_pyproject(root: Path, version: str) -> None:
    (root / "pyproject.toml").write_text(
        "[project]\n" 'name = "DistanceCalculatorPro"\n' f'version = "{version}"\n',
        encoding="utf-8",
    )


def test_stable_release_gate_accepts_stable_metadata(
    tmp_path: Path,
) -> None:
    _write_pyproject(tmp_path, STABLE_VERSION)

    with patch(
        "app.release.stable_release_gate.__version__",
        STABLE_VERSION,
    ):
        assert validate_stable_release(tmp_path) == ()


def test_stable_release_gate_reports_runtime_mismatch(
    tmp_path: Path,
) -> None:
    _write_pyproject(tmp_path, STABLE_VERSION)

    with patch(
        "app.release.stable_release_gate.__version__",
        "1.2.0-rc25",
    ):
        issues = validate_stable_release(tmp_path)

    assert issues == ("Runtime version must be 1.2.0; found 1.2.0-rc25.",)


def test_stable_release_gate_reports_missing_pyproject(
    tmp_path: Path,
) -> None:
    with patch(
        "app.release.stable_release_gate.__version__",
        STABLE_VERSION,
    ):
        issues = validate_stable_release(tmp_path)

    assert issues == (f"Missing package metadata: {tmp_path / 'pyproject.toml'}",)


def test_stable_release_gate_reports_package_mismatch(
    tmp_path: Path,
) -> None:
    _write_pyproject(tmp_path, "1.2.0rc25")

    with patch(
        "app.release.stable_release_gate.__version__",
        STABLE_VERSION,
    ):
        issues = validate_stable_release(tmp_path)

    assert issues == ("Package version must be 1.2.0; found '1.2.0rc25'.",)


def test_stable_release_gate_main_passes(
    tmp_path: Path,
    capsys,
) -> None:
    _write_pyproject(tmp_path, STABLE_VERSION)

    with patch(
        "app.release.stable_release_gate.__version__",
        STABLE_VERSION,
    ):
        result = main([str(tmp_path)])

    assert result == 0
    assert "Stable release gate: PASS (1.2.0)" in capsys.readouterr().out


def test_stable_release_gate_main_fails(
    tmp_path: Path,
    capsys,
) -> None:
    _write_pyproject(tmp_path, "1.2.0rc25")

    with patch(
        "app.release.stable_release_gate.__version__",
        STABLE_VERSION,
    ):
        result = main([str(tmp_path)])

    assert result == 1
    output = capsys.readouterr().out
    assert "Stable release gate: FAIL" in output
    assert "Package version must be 1.2.0" in output
