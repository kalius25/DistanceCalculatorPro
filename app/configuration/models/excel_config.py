from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExcelConfig:
    export_directory: str
    auto_fit_columns: bool