"""
Distance Calculator Pro.

Controller for reading Excel input and building route requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from app.models.route_request import RouteRequest
from app.services.excel_service import ExcelService

PreviewHeaders: TypeAlias = list[str]
PreviewRows: TypeAlias = list[list[object]]
PreviewResult: TypeAlias = tuple[
    PreviewHeaders,
    PreviewRows,
]


@dataclass(frozen=True, slots=True)
class ColumnMapping:
    """
    Map Excel columns to route-calculation fields.

    Parameters
    ----------
    origin:
        Column containing the route origin.
    destination:
        Column containing the route destination.
    distance:
        Column in which calculated distance will be written.
    duration:
        Column in which calculated duration will be written.
    """

    origin: str
    destination: str
    distance: str
    duration: str


class CalculationController:
    """
    Coordinate Excel input operations for route calculations.

    The controller receives ExcelService through constructor injection.
    It does not create or configure the Excel service.
    """

    def __init__(
        self,
        excel_service: ExcelService,
    ) -> None:
        """
        Initialize the controller.

        Parameters
        ----------
        excel_service:
            Service responsible for accessing the active workbook.
        """
        self._excel = excel_service

    @property
    def excel_service(self) -> ExcelService:
        """
        Return the injected Excel service.

        This compatibility property exposes the dependency without
        allowing the controller to recreate or replace it internally.
        """
        return self._excel

    def get_sheet_names(self) -> list[str]:
        """
        Return all worksheet names from the active workbook.
        """
        return self._excel.get_sheet_names()

    def get_headers(
        self,
        sheet_name: str,
    ) -> list[str]:
        """
        Return the header row of a worksheet.

        Parameters
        ----------
        sheet_name:
            Name of the worksheet to read.
        """
        return self._excel.read_headers(sheet_name)

    def get_preview(
        self,
        sheet_name: str,
        max_rows: int = 100,
    ) -> PreviewResult:
        """
        Return worksheet headers and preview rows.

        Parameters
        ----------
        sheet_name:
            Name of the worksheet to preview.
        max_rows:
            Maximum number of data rows to return.
        """
        headers = self._excel.read_headers(
            sheet_name,
        )

        rows = self._excel.read_preview(
            sheet_name,
            max_rows=max_rows,
        )

        return headers, rows

    @staticmethod
    def validate_mapping(
        mapping: ColumnMapping,
    ) -> tuple[bool, str]:
        """
        Validate a column mapping.

        Returns
        -------
        tuple[bool, str]
            Validation status and an error message. The message is empty
            when the mapping is valid.
        """
        if not mapping.origin:
            return False, "Chưa chọn Origin."

        if not mapping.destination:
            return False, "Chưa chọn Destination."

        if mapping.origin == mapping.destination:
            return (
                False,
                "Origin và Destination không được trùng.",
            )

        if not mapping.distance:
            return False, "Chưa chọn cột Distance."

        if not mapping.duration:
            return False, "Chưa chọn cột Duration."

        return True, ""

    def build_requests(
        self,
        sheet_name: str,
        mapping: ColumnMapping,
    ) -> list[RouteRequest]:
        """
        Build route requests from all data rows in a worksheet.

        Each generated request contains the original Excel row number in
        ``metadata["row_number"]``. Excel data starts at row 2 because
        row 1 contains the headers.

        Parameters
        ----------
        sheet_name:
            Name of the worksheet containing route data.
        mapping:
            Mapping between worksheet columns and route fields.

        Raises
        ------
        ValueError
            If the supplied column mapping is invalid.
        """
        is_valid, error_message = self.validate_mapping(
            mapping,
        )

        if not is_valid:
            raise ValueError(error_message)

        headers = self._excel.read_headers(
            sheet_name,
        )

        rows = self._excel.read_all(
            sheet_name,
        )

        header_index = {header: index for index, header in enumerate(headers)}

        requests: list[RouteRequest] = []

        for excel_row, values in enumerate(
            rows,
            start=2,
        ):
            origin = values[header_index[mapping.origin]]

            destination = values[header_index[mapping.destination]]

            requests.append(
                RouteRequest(
                    origin=str(origin).strip(),
                    destination=str(destination).strip(),
                    metadata={
                        "row_number": excel_row,
                    },
                )
            )

        return requests


__all__ = [
    "CalculationController",
    "ColumnMapping",
    "PreviewHeaders",
    "PreviewResult",
    "PreviewRows",
]
