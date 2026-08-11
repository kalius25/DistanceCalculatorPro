import re
import tomllib
from pathlib import Path

from app.presentation.app_metadata import AppMetadata
from app.version import __version__


def _pep440_display_version(version: str) -> str:
    match = re.fullmatch(r"(\d+\.\d+\.\d+)rc(\d+)", version)
    if match is None:
        return version
    base, release_candidate = match.groups()
    return f"{base}-rc{release_candidate}"


def test_app_metadata_uses_runtime_version() -> None:
    assert AppMetadata().version == __version__


def test_package_and_runtime_versions_are_synchronized() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    package_version = pyproject["project"]["version"]

    assert _pep440_display_version(package_version) == __version__


def test_runtime_version_is_release_candidate_25() -> None:
    assert __version__ == "1.2.0-rc25"
