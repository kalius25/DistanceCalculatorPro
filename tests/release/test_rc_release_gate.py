from pathlib import Path
from unittest.mock import patch

from app.release import rc_release_gate


def _write_pyproject(root: Path, version: str) -> None:
    root.joinpath("pyproject.toml").write_text(
        "[project]\n" 'name = "DistanceCalculatorPro"\n' f'version = "{version}"\n',
        encoding="utf-8",
    )


def test_validate_rc_release_passes(tmp_path: Path) -> None:
    _write_pyproject(tmp_path, rc_release_gate.RC_PACKAGE_VERSION)

    assert rc_release_gate.validate_rc_release(tmp_path) == ()


def test_validate_rc_release_reports_runtime_version(
    tmp_path: Path,
) -> None:
    _write_pyproject(tmp_path, rc_release_gate.RC_PACKAGE_VERSION)

    with patch.object(rc_release_gate, "__version__", "1.2.0"):
        issues = rc_release_gate.validate_rc_release(tmp_path)

    assert issues == ("Runtime version must be 1.3.0-rc1; found 1.2.0.",)


def test_validate_rc_release_reports_missing_pyproject(
    tmp_path: Path,
) -> None:
    issues = rc_release_gate.validate_rc_release(tmp_path)

    assert issues == (f"Missing package metadata: {tmp_path / 'pyproject.toml'}",)


def test_validate_rc_release_reports_package_version(
    tmp_path: Path,
) -> None:
    _write_pyproject(tmp_path, "1.2.0")

    issues = rc_release_gate.validate_rc_release(tmp_path)

    assert issues == ("Package version must be 1.3.0rc1; found '1.2.0'.",)


def test_main_passes_and_fails(tmp_path: Path, capsys: object) -> None:
    _write_pyproject(tmp_path, rc_release_gate.RC_PACKAGE_VERSION)
    assert rc_release_gate.main([str(tmp_path)]) == 0

    _write_pyproject(tmp_path, "1.2.0")
    assert rc_release_gate.main([str(tmp_path)]) == 1
