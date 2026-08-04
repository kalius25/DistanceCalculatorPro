from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppMetadata:
    """Immutable application identity shown by the presentation layer."""

    name: str = "DistanceCalculatorPro"
    version: str = "1.2.0-rc8"
    organization: str = "DistanceCalculatorPro"
    domain: str = "distancecalculatorpro.local"
