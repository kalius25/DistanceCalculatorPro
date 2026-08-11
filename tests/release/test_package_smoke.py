from pathlib import Path

from app.release.package_smoke import main, validate_distribution


def _make_distribution(root: Path) -> None:
    (root / "DistanceCalculatorPro.exe").write_bytes(b"exe")
    required = (
        "app/presentation/styles/light.qss",
        "app/presentation/styles/dark.qss",
        "app/presentation/resources/icons/app_icon.svg",
        "app/presentation/resources/splash.svg",
    )
    for relative in required:
        path = root / "_internal" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("resource", encoding="utf-8")


def test_validate_distribution_passes_complete_build(tmp_path: Path) -> None:
    distribution = tmp_path / "DistanceCalculatorPro"
    distribution.mkdir()
    _make_distribution(distribution)

    assert validate_distribution(distribution) == ()


def test_validate_distribution_reports_missing_files(tmp_path: Path) -> None:
    distribution = tmp_path / "DistanceCalculatorPro"
    distribution.mkdir()

    issues = validate_distribution(distribution)

    assert len(issues) == 5
    assert issues[0].startswith("Missing executable:")
    assert all("Missing " in issue for issue in issues)


def test_package_smoke_main_returns_success(
    tmp_path: Path,
    capsys,
) -> None:
    distribution = tmp_path / "DistanceCalculatorPro"
    distribution.mkdir()
    _make_distribution(distribution)

    assert main([str(distribution)]) == 0
    output = capsys.readouterr().out
    assert "Packaging smoke: PASS" in output


def test_package_smoke_main_returns_failure(
    tmp_path: Path,
    capsys,
) -> None:
    distribution = tmp_path / "DistanceCalculatorPro"
    distribution.mkdir()

    assert main([str(distribution)]) == 1
    output = capsys.readouterr().out
    assert "Packaging smoke: FAIL" in output
