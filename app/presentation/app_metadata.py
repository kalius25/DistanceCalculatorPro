from dataclasses import dataclass

from app.version import __version__


@dataclass(frozen=True, slots=True)
class AppMetadata:
    """Immutable application identity shown by the presentation layer."""

    name: str = "DistanceCalculatorPro"
    version: str = __version__
    organization: str = "DistanceCalculatorPro"
    domain: str = "distancecalculatorpro.local"
