from pathlib import Path

import qtawesome as qta
from PySide6.QtCore import QByteArray, QModelIndex, Qt, Signal
from PySide6.QtGui import (
    QCloseEvent,
    QDragEnterEvent,
    QDragLeaveEvent,
    QDropEvent,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from app.batch.progress import ProgressSnapshot
from app.batch.summary import BatchSummary
from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode
from app.models.excel_table_model import ExcelTableModel
from app.models.preview_row_status import PreviewRowStatus
from app.models.preview_status_filter_proxy import PreviewStatusFilterProxyModel
from app.presentation.workspace_configuration import (
    ColumnMapping,
    ProviderConfiguration,
    WorkspaceConfiguration,
)
from app.providers.catalog import (
    PROVIDER_DEFINITIONS,
    ProviderDefinition,
    provider_definition,
)
from app.workbooks.models import WorkbookInfo, WorksheetInfo
from app.workbooks.virtual_reader import (
    VirtualWorksheetDataSourceFactory,
)


def _provider_tooltip(definition: ProviderDefinition) -> str:
    if definition.execution_enabled:
        return "Available for calculation"
    if definition.engine_ready:
        return "Navigation engine ready; result parsing starts in Sprint " + str(
            definition.roadmap_sprint
        )
    return "Provider foundation ready; engine starts in Sprint " + str(
        definition.roadmap_sprint
    )


class HomePage(QWidget):
    """File workspace with selection, recent files and workbook preview."""

    browse_requested = Signal()
    clear_recent_requested = Signal()
    file_selected = Signal(str)
    sheet_changed = Signal(str)
    column_mapping_changed = Signal(str, str, str, str)
    provider_configuration_changed = Signal(str, str, bool, bool, bool)
    workspace_configuration_changed = Signal(object)
    workspace_ready_changed = Signal(bool)
    retry_failed_requested = Signal()
    source_panels_visibility_changed = Signal(bool)
    workspace_splitter_state_changed = Signal(object)

    SUPPORTED_EXTENSIONS = frozenset({".xlsx", ".xlsm", ".csv"})

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected_file: str | None = None
        self._workbook_info: WorkbookInfo | None = None
        self._current_worksheet: WorksheetInfo | None = None
        self._mapping_valid = False
        self._provider_valid = False
        self._workspace_ready = False
        self._workspace_locked = False
        self._theme_name = "light"
        self._virtual_source_factory = VirtualWorksheetDataSourceFactory()
        self.setObjectName("pageWorkspace")
        self.setAcceptDrops(True)
        self._create_widgets()
        self._create_layout()
        self._connect_signals()
        self._apply_initial_state()

    @property
    def selected_file(self) -> str | None:
        return self._selected_file

    @property
    def workbook_info(self) -> WorkbookInfo | None:
        return self._workbook_info

    @property
    def selected_sheet_name(self) -> str | None:
        if self._current_worksheet is None:
            return None
        return self._current_worksheet.name

    @property
    def column_mapping(self) -> ColumnMapping | None:
        if not self._mapping_valid:
            return None
        return ColumnMapping(
            origin_column=str(self._origin_column_selector.currentData()),
            destination_column=str(self._destination_column_selector.currentData()),
            result_column=str(self._result_column_selector.currentData()),
            result_duration_column=str(
                self._result_duration_column_selector.currentData()
            ),
        )

    @property
    def provider_configuration(self) -> ProviderConfiguration | None:
        if not self._provider_valid:
            return None
        return ProviderConfiguration(
            provider=ProviderType(str(self._provider_selector.currentData())),
            travel_mode=TravelMode(str(self._travel_mode_selector.currentData())),
            avoid_tolls=self._avoid_tolls_checkbox.isChecked(),
            avoid_highways=self._avoid_highways_checkbox.isChecked(),
            avoid_ferries=self._avoid_ferries_checkbox.isChecked(),
        )

    @property
    def workspace_configuration(self) -> WorkspaceConfiguration | None:
        mapping = self.column_mapping
        provider = self.provider_configuration
        if mapping is None or provider is None:
            return None
        return WorkspaceConfiguration(
            mapping,
            provider,
            skip_existing_results=(self._skip_existing_results_checkbox.isChecked()),
        )

    @property
    def workspace_ready(self) -> bool:
        return self._workspace_ready

    @property
    def workspace_locked(self) -> bool:
        return self._workspace_locked

    @classmethod
    def accepts_file(cls, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in cls.SUPPORTED_EXTENSIONS

    def set_selected_file(self, file_path: str) -> None:
        normalized_path = str(Path(file_path))
        path = Path(normalized_path)
        self._selected_file = normalized_path
        self._selected_file_name.setText(path.name)
        self._selected_file_path.setText(normalized_path)
        self._selected_file_path.setToolTip(normalized_path)
        self._inspector_file_path_value.setText(normalized_path)
        self._inspector_file_path_value.setToolTip(normalized_path)
        self._inspector_file_size_value.setText("Inspecting…")
        self._file_information_frame.setVisible(True)
        self._empty_file_information.setVisible(False)
        self._file_ready_label.setText("Inspecting workbook…")
        self.clear_inspection()
        self._workspace_status.setText("Inspecting workbook…")

    def clear_selected_file(self) -> None:
        self._selected_file = None
        self._selected_file_name.clear()
        self._selected_file_path.clear()
        self._inspector_file_path_value.setText("—")
        self._inspector_file_path_value.setToolTip("")
        self._inspector_file_size_value.setText("—")
        self._file_information_frame.setVisible(False)
        self._empty_file_information.setVisible(True)
        self._workspace_status.setText("No workbook selected")
        self.clear_inspection()

    def set_inspection(self, workbook_info: WorkbookInfo) -> None:
        self._workbook_info = workbook_info
        self._file_type_value.setText(workbook_info.file_type)
        formatted_size = (
            f"{self._format_file_size(workbook_info.file_size_bytes)} "
            f"({workbook_info.file_size_bytes:,} bytes)"
        )
        self._file_size_value.setText(formatted_size)
        self._inspector_file_size_value.setText(formatted_size)
        self._inspector_file_path_value.setText(workbook_info.file_path)
        self._inspector_file_path_value.setToolTip(workbook_info.file_path)
        self._modified_value.setText(
            workbook_info.modified_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        self._file_ready_label.setText("Ready to inspect")
        self._file_ready_label.setProperty("ready", True)
        self._refresh_style(self._file_ready_label)

        self._sheet_selector.blockSignals(True)
        self._sheet_selector.clear()
        self._sheet_selector.addItems(
            [sheet.name for sheet in workbook_info.worksheets]
        )
        self._sheet_selector.blockSignals(False)

        # A successfully inspected workbook becomes the primary workspace view.
        # Source panels remain one click away through Show File Panels.
        self._toggle_source_panels_button.blockSignals(True)
        self._toggle_source_panels_button.setChecked(True)
        self._toggle_source_panels_button.blockSignals(False)
        self._apply_source_panels_state(True, emit_signal=False)

        if workbook_info.worksheets:
            self._show_worksheet(workbook_info.worksheets[0])
            self._workspace_status.setText(
                f"Workbook ready · {len(workbook_info.worksheets)} sheet(s)"
            )
        else:
            self._clear_worksheet_details()
            self._headers_status_value.setText("No")
            self._workspace_status.setText("Workbook contains no worksheets")

    def set_inspection_error(self, message: str) -> None:
        self.clear_inspection()
        self._file_ready_label.setText("Inspection failed")
        self._file_ready_label.setProperty("ready", False)
        self._refresh_style(self._file_ready_label)
        self._workspace_status.setText(f"Inspection failed · {message}")

    def clear_inspection(self) -> None:
        self._workbook_info = None
        self._current_worksheet = None
        if hasattr(self, "_inspector_frame"):
            self._inspector_frame.setVisible(False)
            self._sheet_selector.clear()
            self.release_resources()
        if hasattr(self, "_origin_column_selector"):
            self._populate_column_mapping(())
        if hasattr(self, "_workspace_readiness_status"):
            self._update_workspace_readiness()
        if hasattr(self, "_source_panels_container"):
            self._toggle_source_panels_button.blockSignals(True)
            self._toggle_source_panels_button.setChecked(False)
            self._toggle_source_panels_button.blockSignals(False)
            self._apply_source_panels_state(False, emit_signal=False)

    def release_resources(self) -> None:
        """Release preview data sources and cached worksheet blocks."""
        if hasattr(self, "_preview_model"):
            self._preview_model.clear_source()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self.release_resources()
        super().closeEvent(event)

    def set_recent_files(self, file_paths: list[str]) -> None:
        self._recent_files.clear()
        if not file_paths:
            item = QListWidgetItem("No recent workbooks")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self._recent_files.addItem(item)
            self._clear_recent_button.setEnabled(False)
            return

        self._clear_recent_button.setEnabled(True)
        for file_path in file_paths:
            path = Path(file_path)
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)
            self._recent_files.addItem(item)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if self._event_file_path(event) is not None:
            event.acceptProposedAction()
            self._drop_zone.setProperty("dragActive", True)
            self._refresh_style(self._drop_zone)
            return
        event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:  # noqa: N802
        self._reset_drop_zone()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        file_path = self._event_file_path(event)
        self._reset_drop_zone()
        if file_path is None:
            event.ignore()
            return
        event.acceptProposedAction()
        self.file_selected.emit(file_path)

    def _create_widgets(self) -> None:
        self._title_label = QLabel("File Workspace", self)
        self._title_label.setObjectName("lblPageTitle")
        self._description_label = QLabel(
            "Select an Excel or CSV workbook to begin a distance-calculation job.",
            self,
        )
        self._description_label.setObjectName("lblPageDescription")
        self._toggle_source_panels_button = QPushButton("Hide File Panels", self)
        self._toggle_source_panels_button.setObjectName("btnToggleSourcePanels")
        self._toggle_source_panels_button.setCheckable(True)
        self._toggle_source_panels_button.setIcon(
            qta.icon("fa5s.chevron-left", color="#111827")
        )
        self._toggle_source_panels_button.setToolTip(
            "Hide Drag & Drop and Recent Workbooks"
        )
        self._toggle_source_panels_button.setEnabled(False)

        self._selection_frame = self._create_section_frame("frmSelectionPanel")
        selection_layout = QVBoxLayout(self._selection_frame)
        selection_layout.setContentsMargins(16, 14, 16, 16)
        selection_layout.setSpacing(10)
        selection_layout.addWidget(self._section_title("Select Workbook"))

        self._drop_zone = QFrame(self._selection_frame)
        self._drop_zone.setObjectName("frmDropZone")
        drop_layout = QVBoxLayout(self._drop_zone)
        drop_layout.setContentsMargins(18, 18, 18, 18)
        drop_layout.setSpacing(7)
        self._drop_icon = QLabel(self._drop_zone)
        self._drop_icon.setObjectName("lblDropIcon")
        self._set_drop_icon_color("#2563EB")
        self._drop_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_title = QLabel("Drag & drop a workbook here", self._drop_zone)
        self._drop_title.setObjectName("lblDropTitle")
        self._drop_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_hint = QLabel(
            "Supported formats: .xlsx, .xlsm, .csv", self._drop_zone
        )
        self._drop_hint.setObjectName("lblDropHint")
        self._drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(self._drop_icon)
        drop_layout.addWidget(self._drop_title)
        drop_layout.addWidget(self._drop_hint)
        selection_layout.addWidget(self._drop_zone, 1)

        or_layout = QHBoxLayout()
        or_layout.addStretch(1)
        or_label = QLabel("or", self._selection_frame)
        or_label.setObjectName("lblDropHint")
        or_layout.addWidget(or_label)
        or_layout.addStretch(1)
        selection_layout.addLayout(or_layout)
        self._browse_button = QPushButton("Browse files…", self._selection_frame)
        self._browse_button.setObjectName("btnBrowseWorkbook")
        self._browse_button.setIcon(qta.icon("fa5s.folder-open"))
        selection_layout.addWidget(
            self._browse_button, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self._recent_frame = self._create_section_frame("frmRecentPanel")
        recent_layout = QVBoxLayout(self._recent_frame)
        recent_layout.setContentsMargins(0, 14, 0, 0)
        recent_layout.setSpacing(8)
        recent_title = self._section_title("Recent Workbooks")
        recent_title.setContentsMargins(16, 0, 16, 0)
        recent_layout.addWidget(recent_title)
        self._recent_files = QListWidget(self._recent_frame)
        self._recent_files.setObjectName("lstRecentWorkbooks")
        self._recent_files.setAlternatingRowColors(True)
        recent_layout.addWidget(self._recent_files, 1)
        self._clear_recent_button = QPushButton("Clear Recent List", self._recent_frame)
        self._clear_recent_button.setObjectName("btnClearRecent")
        self._clear_recent_button.setIcon(qta.icon("fa5s.trash-alt"))
        recent_layout.addWidget(self._clear_recent_button)

        self._file_panel = self._create_section_frame("frmFilePanel")
        file_panel_layout = QVBoxLayout(self._file_panel)
        file_panel_layout.setContentsMargins(16, 14, 16, 16)
        file_panel_layout.setSpacing(10)
        file_panel_layout.addWidget(self._section_title("File Information"))
        self._empty_file_information = QLabel(
            "Select a workbook to view its information.", self._file_panel
        )
        self._empty_file_information.setObjectName("lblWorkspaceEmptyState")
        self._empty_file_information.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_file_information.setWordWrap(True)
        file_panel_layout.addWidget(self._empty_file_information, 1)

        self._file_information_frame = QFrame(self._file_panel)
        self._file_information_frame.setObjectName("frmSelectedFile")
        file_info_layout = QVBoxLayout(self._file_information_frame)
        file_info_layout.setContentsMargins(12, 12, 12, 12)
        file_info_layout.setSpacing(9)
        file_heading = QHBoxLayout()
        self._selected_icon = QLabel(self._file_information_frame)
        self._selected_icon.setPixmap(qta.icon("fa5s.file-excel").pixmap(34, 34))
        heading_text = QVBoxLayout()
        self._selected_file_name = QLabel(self._file_information_frame)
        self._selected_file_name.setObjectName("lblSelectedFileName")
        self._file_ready_label = QLabel(self._file_information_frame)
        self._file_ready_label.setObjectName("lblFileReady")
        heading_text.addWidget(self._selected_file_name)
        heading_text.addWidget(self._file_ready_label)
        file_heading.addWidget(self._selected_icon)
        file_heading.addLayout(heading_text, 1)
        file_info_layout.addLayout(file_heading)

        detail_grid = QGridLayout()
        detail_grid.setHorizontalSpacing(12)
        detail_grid.setVerticalSpacing(9)
        self._file_type_value = QLabel(self._file_information_frame)
        self._file_size_value = QLabel(self._file_information_frame)
        self._modified_value = QLabel(self._file_information_frame)
        self._selected_file_path = QLabel(self._file_information_frame)
        self._selected_file_path.setWordWrap(True)
        for row, (caption, value) in enumerate(
            (
                ("Type:", self._file_type_value),
                ("Size:", self._file_size_value),
                ("Modified:", self._modified_value),
                ("Path:", self._selected_file_path),
            )
        ):
            caption_label = QLabel(caption, self._file_information_frame)
            caption_label.setObjectName("lblInspectorCaption")
            value.setObjectName("lblInspectorValue")
            detail_grid.addWidget(caption_label, row, 0)
            detail_grid.addWidget(value, row, 1)
        detail_grid.setColumnStretch(1, 1)
        file_info_layout.addLayout(detail_grid)
        file_panel_layout.addWidget(self._file_information_frame, 1)
        # Retained only for backwards-compatible internal state.  File details are
        # now rendered directly inside Workbook Inspector.
        self._file_panel.setVisible(False)

        self._create_inspector_widgets()
        self._create_summary_widgets()
        self._workspace_status = QLabel(self)
        self._workspace_status.setObjectName("lblWorkspaceStatus")

    def _create_inspector_widgets(self) -> None:
        self._inspector_frame = self._create_section_frame("frmWorkbookInspector")
        inspector_layout = QVBoxLayout(self._inspector_frame)
        inspector_layout.setContentsMargins(10, 10, 10, 10)
        inspector_layout.setSpacing(10)

        self._inspector_controls_frame = QFrame(self._inspector_frame)
        self._inspector_controls_frame.setObjectName("frmWorkbookInspectorControls")
        controls_layout = QVBoxLayout(self._inspector_controls_frame)
        controls_layout.setContentsMargins(6, 4, 6, 4)
        controls_layout.setSpacing(10)

        inspector_header = QHBoxLayout()
        inspector_header.setSpacing(8)
        inspector_header.addWidget(self._section_title("Workbook Inspector"))
        inspector_header.addStretch(1)
        self._toggle_config_button = QPushButton("Hide Config", self._inspector_frame)
        self._toggle_config_button.setObjectName("btnToggleConfig")
        self._toggle_config_button.setCheckable(True)
        self._toggle_config_button.setIcon(qta.icon("fa5s.chevron-up", color="#111827"))
        self._toggle_config_button.setToolTip(
            "Hide Column Mapping and Route Provider configuration"
        )
        inspector_header.addWidget(self._toggle_config_button)
        controls_layout.addLayout(inspector_header)

        file_details_layout = QGridLayout()
        file_details_layout.setHorizontalSpacing(12)
        file_details_layout.setVerticalSpacing(6)
        file_path_caption = QLabel("File Path", self._inspector_frame)
        file_path_caption.setObjectName("lblInspectorCaption")
        self._inspector_file_path_value = QLabel("—", self._inspector_frame)
        self._inspector_file_path_value.setObjectName("lblInspectorValue")
        self._inspector_file_path_value.setWordWrap(True)
        file_size_caption = QLabel("File Size", self._inspector_frame)
        file_size_caption.setObjectName("lblInspectorCaption")
        self._inspector_file_size_value = QLabel("—", self._inspector_frame)
        self._inspector_file_size_value.setObjectName("lblInspectorValue")
        file_details_layout.addWidget(file_path_caption, 0, 0)
        file_details_layout.addWidget(self._inspector_file_path_value, 0, 1)
        file_details_layout.addWidget(file_size_caption, 1, 0)
        file_details_layout.addWidget(self._inspector_file_size_value, 1, 1)
        file_details_layout.setColumnStretch(1, 1)
        controls_layout.addLayout(file_details_layout)

        summary_layout = QHBoxLayout()
        worksheet_layout = QVBoxLayout()
        worksheet_caption = QLabel("Worksheet", self._inspector_frame)
        worksheet_caption.setObjectName("lblInspectorCaption")
        self._sheet_selector = QComboBox(self._inspector_frame)
        self._sheet_selector.setObjectName("cmbWorksheet")
        worksheet_layout.addWidget(worksheet_caption)
        worksheet_layout.addWidget(self._sheet_selector)
        summary_layout.addLayout(worksheet_layout, 3)

        self._row_count_value = self._summary_value("Rows", summary_layout)
        self._column_count_value = self._summary_value("Columns", summary_layout)
        self._headers_status_value = self._summary_value(
            "Detected headers", summary_layout
        )
        summary_layout.addStretch(1)
        controls_layout.addLayout(summary_layout)

        self._mapping_frame = QFrame(self._inspector_frame)
        self._mapping_frame.setObjectName("frmColumnMapping")
        mapping_layout = QGridLayout(self._mapping_frame)
        mapping_layout.setContentsMargins(12, 10, 12, 10)
        mapping_layout.setHorizontalSpacing(12)
        mapping_layout.setVerticalSpacing(6)
        mapping_title = QLabel("Column Mapping", self._mapping_frame)
        mapping_title.setObjectName("lblSectionTitle")
        mapping_layout.addWidget(mapping_title, 0, 0, 1, 3)
        self._origin_column_selector = self._mapping_selector(
            "Origin column", "cmbOriginColumn", mapping_layout, 1
        )
        self._destination_column_selector = self._mapping_selector(
            "Destination column", "cmbDestinationColumn", mapping_layout, 2
        )
        self._result_column_selector = self._mapping_selector(
            "Result distance", "cmbResultColumn", mapping_layout, 3
        )
        self._result_duration_column_selector = self._mapping_selector(
            "Result duration", "cmbResultDurationColumn", mapping_layout, 4
        )
        self._mapping_status = QLabel(self._mapping_frame)
        self._mapping_status.setObjectName("lblMappingStatus")
        mapping_layout.addWidget(self._mapping_status, 4, 0, 1, 4)
        for column in range(4):
            mapping_layout.setColumnStretch(column, 1)
        self._provider_frame = QFrame(self._inspector_frame)
        self._provider_frame.setObjectName("frmProviderConfiguration")
        provider_layout = QGridLayout(self._provider_frame)
        provider_layout.setContentsMargins(12, 10, 12, 10)
        provider_layout.setHorizontalSpacing(12)
        provider_layout.setVerticalSpacing(6)
        provider_title = QLabel("Route Provider", self._provider_frame)
        provider_title.setObjectName("lblSectionTitle")
        provider_layout.addWidget(provider_title, 0, 0, 1, 3)

        provider_caption = QLabel("Provider", self._provider_frame)
        provider_caption.setObjectName("lblInspectorCaption")
        self._provider_selector = QComboBox(self._provider_frame)
        self._provider_selector.setObjectName("cmbRouteProvider")
        for definition in PROVIDER_DEFINITIONS:
            self._provider_selector.addItem(
                definition.display_name,
                definition.provider.value,
            )
            index = self._provider_selector.count() - 1
            tooltip = _provider_tooltip(definition)
            self._provider_selector.setItemData(
                index,
                tooltip,
                Qt.ItemDataRole.ToolTipRole,
            )
        provider_layout.addWidget(provider_caption, 1, 0)
        provider_layout.addWidget(self._provider_selector, 2, 0)

        travel_caption = QLabel("Travel mode", self._provider_frame)
        travel_caption.setObjectName("lblInspectorCaption")
        self._travel_mode_selector = QComboBox(self._provider_frame)
        self._travel_mode_selector.setObjectName("cmbTravelMode")
        for label, mode in (
            ("Driving", TravelMode.DRIVING),
            ("Walking", TravelMode.WALKING),
        ):
            self._travel_mode_selector.addItem(label, mode.value)
        provider_layout.addWidget(travel_caption, 1, 1)
        provider_layout.addWidget(self._travel_mode_selector, 2, 1)

        avoid_caption = QLabel("Route options", self._provider_frame)
        avoid_caption.setObjectName("lblInspectorCaption")
        provider_layout.addWidget(avoid_caption, 1, 2)
        avoid_layout = QHBoxLayout()
        self._avoid_tolls_checkbox = QCheckBox("Avoid tolls", self._provider_frame)
        self._avoid_tolls_checkbox.setObjectName("chkAvoidTolls")
        self._avoid_highways_checkbox = QCheckBox(
            "Avoid highways", self._provider_frame
        )
        self._avoid_highways_checkbox.setObjectName("chkAvoidHighways")
        self._avoid_ferries_checkbox = QCheckBox("Avoid ferries", self._provider_frame)
        self._avoid_ferries_checkbox.setObjectName("chkAvoidFerries")
        avoid_layout.addWidget(self._avoid_tolls_checkbox)
        avoid_layout.addWidget(self._avoid_highways_checkbox)
        avoid_layout.addWidget(self._avoid_ferries_checkbox)
        avoid_layout.addStretch(1)
        provider_layout.addLayout(avoid_layout, 2, 2)

        self._skip_existing_results_checkbox = QCheckBox(
            "Skip rows already containing a result",
            self._provider_frame,
        )
        self._skip_existing_results_checkbox.setObjectName("chkSkipExistingResults")
        self._skip_existing_results_checkbox.setChecked(True)
        provider_layout.addWidget(self._skip_existing_results_checkbox, 3, 0, 1, 3)

        self._provider_status = QLabel(self._provider_frame)
        self._provider_status.setObjectName("lblProviderStatus")
        provider_layout.addWidget(self._provider_status, 4, 0, 1, 3)

        self._workspace_readiness_status = QLabel(self._provider_frame)
        self._workspace_readiness_status.setObjectName("lblWorkspaceReadinessStatus")
        provider_layout.addWidget(self._workspace_readiness_status, 5, 0, 1, 3)
        provider_layout.setColumnStretch(0, 1)
        provider_layout.setColumnStretch(1, 1)
        provider_layout.setColumnStretch(2, 3)
        configuration_row = QHBoxLayout()
        configuration_row.setSpacing(10)
        configuration_row.addWidget(self._mapping_frame, 1)
        configuration_row.addWidget(self._provider_frame, 1)
        controls_layout.addLayout(configuration_row)
        inspector_layout.addWidget(self._inspector_controls_frame, 0)

        self._preview_frame = QFrame(self._inspector_frame)
        self._preview_frame.setObjectName("frmPreviewPanel")
        preview_layout = QVBoxLayout(self._preview_frame)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        preview_layout.setSpacing(8)
        preview_header_layout = QHBoxLayout()
        preview_header_layout.setContentsMargins(0, 0, 0, 0)
        self._preview_title = QLabel("Data Preview", self._preview_frame)
        self._preview_title.setObjectName("lblPreviewTitle")
        preview_header_layout.addWidget(self._preview_title, 1)
        self._preview_auto_scroll_checkbox = QCheckBox(
            "Auto-scroll", self._preview_frame
        )
        self._preview_auto_scroll_checkbox.setObjectName("chkPreviewAutoScroll")
        self._preview_auto_scroll_checkbox.setChecked(True)
        preview_header_layout.addWidget(self._preview_auto_scroll_checkbox, 0)
        self._preview_status_filter = QComboBox(self._preview_frame)
        self._preview_status_filter.setObjectName("cmbPreviewStatusFilter")
        self._preview_status_filter.setToolTip(
            "Filter Data Preview by processing status"
        )
        self._preview_status_filter_labels = (
            "All statuses",
            "Active",
            "Success",
            "Failed",
            "Skipped",
            "Invalid",
            "Retried",
            "Pending",
        )
        self._preview_status_filter.addItem("All statuses", None)
        self._preview_status_filter.addItem("Active", "active")
        self._preview_status_filter.addItem("Success", PreviewRowStatus.SUCCESS)
        self._preview_status_filter.addItem("Failed", PreviewRowStatus.FAILED)
        self._preview_status_filter.addItem("Skipped", PreviewRowStatus.SKIPPED)
        self._preview_status_filter.addItem("Invalid", PreviewRowStatus.INVALID)
        self._preview_status_filter.addItem("Retried", PreviewRowStatus.RETRIED)
        self._preview_status_filter.addItem("Pending", PreviewRowStatus.PENDING)
        self._preview_status_filter_counted_index = -1
        preview_header_layout.addWidget(self._preview_status_filter, 0)
        preview_layout.addLayout(preview_header_layout)
        self._preview_table = QTableView(self._preview_frame)
        self._preview_table.setObjectName("tblDataPreview")
        self._preview_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._preview_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._preview_table.setAlternatingRowColors(True)
        self._preview_table.verticalHeader().setDefaultSectionSize(24)
        self._preview_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self._preview_table.horizontalHeader().setStretchLastSection(True)
        self._preview_model = ExcelTableModel(show_status_column=True)
        self._preview_filter_model = PreviewStatusFilterProxyModel()
        self._preview_filter_model.setSourceModel(self._preview_model)
        self._preview_table.setModel(self._preview_filter_model)
        self._refresh_selected_preview_status_filter_count()
        preview_layout.addWidget(self._preview_table, 1)
        inspector_layout.addWidget(self._preview_frame, 1)

    def _create_summary_widgets(self) -> None:
        self._summary_frame = self._create_section_frame("frmBatchSummary")
        self._summary_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._summary_frame.setMinimumWidth(300)
        summary_layout = QHBoxLayout(self._summary_frame)
        summary_layout.setContentsMargins(14, 8, 14, 8)
        summary_layout.setSpacing(8)
        self._summary_label = QLabel("No batch summary available", self._summary_frame)
        self._summary_label.setObjectName("lblBatchSummary")
        self._summary_label.setWordWrap(False)
        summary_layout.addWidget(self._summary_label, 1)
        self._summary_values: tuple[int, int, int, int, int, int] | None = None
        self._summary_frame.setVisible(False)

    @staticmethod
    def _summary_html(
        state: str,
        total: int,
        successful: int,
        failed: int,
        skipped: int,
        invalid: int,
        retried: int,
    ) -> str:
        return (
            f"{state} · "
            f"<span style='color:#16A34A;font-weight:600'>"
            f"{successful:,}/{total:,} Successful</span>&nbsp;&nbsp; "
            f"<span style='color:#DC2626;font-weight:600'>"
            f"{failed:,} Failed</span>&nbsp;&nbsp; "
            f"<span style='color:#CA8A04;font-weight:600'>"
            f"{skipped:,} Skipped</span>&nbsp;&nbsp; "
            f"<span style='color:#EA580C;font-weight:600'>"
            f"{invalid:,} Invalid</span>&nbsp;&nbsp; "
            f"<span style='color:#2563EB;font-weight:600'>"
            f"{retried:,} Retried</span>"
        )

    def _render_batch_summary_state(self, state: str) -> None:
        if self._summary_values is None:
            return
        total, successful, failed, skipped, invalid, retried = self._summary_values
        self._summary_label.setText(
            self._summary_html(
                state,
                total,
                successful,
                failed,
                skipped,
                invalid,
                retried,
            )
        )
        self._summary_frame.setVisible(True)

    def start_batch_summary(self, total: int) -> None:
        """Show zeroed counters immediately when batch execution starts."""
        self._summary_values = (total, 0, 0, 0, 0, 0)
        self._render_batch_summary_state("Running")

    def set_batch_summary_state(self, state: str) -> None:
        """Change only the live execution state while preserving counters."""
        self._render_batch_summary_state(state)

    def set_preview_row_status(
        self,
        row: int,
        status: PreviewRowStatus,
    ) -> None:
        """Update one zero-based Data Preview row processing status."""
        self._preview_model.set_row_status(row, status)
        self._refresh_selected_preview_status_filter_count()

    def reset_preview_row_statuses(self) -> None:
        """Reset visible processing state without reloading worksheet data."""
        self._preview_model.reset_row_statuses()
        self._refresh_selected_preview_status_filter_count()

    @property
    def preview_status_counts(self) -> dict[PreviewRowStatus, int]:
        """Return current Data Preview status counts."""
        return self._preview_model.status_counts()

    def _preview_status_filter_count(self, value: object) -> int:
        """Return only the count required by the currently selected filter."""
        if value == "active":
            return self._preview_model.status_count(PreviewRowStatus.RUNNING) + (
                self._preview_model.status_count(PreviewRowStatus.RETRIED)
            )
        if isinstance(value, PreviewRowStatus):
            return self._preview_model.status_count(value)
        return self._preview_model.rowCount()

    def _refresh_selected_preview_status_filter_count(self) -> None:
        """Refresh only the selected filter label to minimize live UI work."""
        index = self._preview_status_filter.currentIndex()
        previous_index = self._preview_status_filter_counted_index
        self._preview_status_filter.blockSignals(True)
        if previous_index >= 0 and previous_index != index:
            self._preview_status_filter.setItemText(
                previous_index,
                self._preview_status_filter_labels[previous_index],
            )
        value = self._preview_status_filter.currentData()
        count = self._preview_status_filter_count(value)
        self._preview_status_filter.setItemText(
            index,
            f"{self._preview_status_filter_labels[index]} ({count:,})",
        )
        self._preview_status_filter_counted_index = index
        self._preview_status_filter.blockSignals(False)

    @property
    def preview_status_filter(self) -> frozenset[PreviewRowStatus] | None:
        """Return the active Data Preview status filter."""
        return self._preview_filter_model.statuses

    def set_preview_status_filter(
        self,
        statuses: set[PreviewRowStatus] | frozenset[PreviewRowStatus] | None,
    ) -> None:
        """Filter Data Preview rows without changing worksheet data."""
        self._preview_filter_model.set_statuses(statuses)
        self._preview_table.clearSelection()
        self._preview_table.setCurrentIndex(QModelIndex())
        self._preview_table.scrollToTop()

    def _on_preview_status_filter_changed(self, _index: int) -> None:
        value = self._preview_status_filter.currentData()
        if value == "active":
            statuses = {PreviewRowStatus.RUNNING, PreviewRowStatus.RETRIED}
        elif isinstance(value, PreviewRowStatus):
            statuses = {value}
        else:
            statuses = None
        self.set_preview_status_filter(statuses)
        self._refresh_selected_preview_status_filter_count()

    @property
    def preview_auto_scroll_enabled(self) -> bool:
        """Return whether live processing should follow the running row."""
        return self._preview_auto_scroll_checkbox.isChecked()

    def focus_preview_row(self, row: int) -> None:
        """Highlight a processing row and optionally bring it into view."""
        if row < 0 or row >= self._preview_model.rowCount():
            return
        source_index = self._preview_model.index(row, 0)
        proxy_index = self._preview_filter_model.mapFromSource(source_index)
        if proxy_index.isValid():
            self._preview_table.selectRow(proxy_index.row())
            if self.preview_auto_scroll_enabled:
                self._preview_table.scrollTo(
                    proxy_index,
                    QAbstractItemView.ScrollHint.PositionAtCenter,
                )
            else:
                self._preview_table.setFocus()
        else:
            self._preview_table.clearSelection()

    def set_preview_activity(self, text: str) -> None:
        """Compatibility no-op; live preview text was removed for performance."""
        _ = text

    def set_live_batch_summary(self, metrics: ProgressSnapshot) -> None:
        """Update summary counters from a live progress snapshot."""
        self._summary_values = (
            metrics.total,
            metrics.successful,
            metrics.failed,
            metrics.skipped,
            metrics.invalid,
            metrics.retried,
        )
        self._render_batch_summary_state("Running")

    def set_batch_summary(self, summary: BatchSummary) -> None:
        """Render the latest final batch summary."""
        self._summary_values = (
            summary.total,
            summary.successful,
            summary.failed,
            summary.skipped,
            summary.invalid,
            summary.retry_count,
        )
        state = "Stopped" if summary.stopped else "Completed"
        self._render_batch_summary_state(state)

    def clear_batch_summary(self) -> None:
        """Clear the visible batch summary."""
        self._summary_values = None
        self._summary_label.setText("No batch summary available")
        self._summary_frame.setVisible(False)

    def _create_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Keep the workspace heading and status in a dedicated, non-collapsible
        # container. Hiding the source panels must never reflow these labels.
        self._workspace_header = QFrame(self)
        self._workspace_header.setObjectName("frmWorkspaceHeader")
        self._workspace_header.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        header_layout = QVBoxLayout(self._workspace_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        heading_layout = QHBoxLayout()
        heading_layout.addWidget(self._title_label)
        heading_layout.addStretch(1)
        heading_layout.addWidget(self._summary_frame, 2)
        heading_layout.addWidget(self._toggle_source_panels_button)
        header_layout.addLayout(heading_layout)
        self._description_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._workspace_status.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        header_layout.addWidget(self._description_label)
        header_layout.addWidget(self._workspace_status)
        layout.addWidget(
            self._workspace_header,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        self._source_panels_container = QWidget(self)
        source_layout = QVBoxLayout(self._source_panels_container)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(10)
        # Startup workspace: Drag & Drop uses roughly one third of the height,
        # while Recent Workbooks receives the remaining two thirds.
        source_layout.addWidget(self._selection_frame, 1)
        source_layout.addWidget(self._recent_frame, 2)

        self._workspace_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._workspace_splitter.setObjectName("splWorkspace")
        self._workspace_splitter.setChildrenCollapsible(False)
        self._workspace_splitter.addWidget(self._source_panels_container)
        self._workspace_splitter.addWidget(self._inspector_frame)
        self._workspace_splitter.setStretchFactor(0, 2)
        self._workspace_splitter.setStretchFactor(1, 7)
        self._workspace_splitter.setSizes([320, 820])
        layout.addWidget(self._workspace_splitter, 1)

    def _connect_signals(self) -> None:
        self._browse_button.clicked.connect(self.browse_requested.emit)
        self._clear_recent_button.clicked.connect(self.clear_recent_requested.emit)
        self._recent_files.itemActivated.connect(self._on_recent_file_activated)
        self._sheet_selector.currentTextChanged.connect(self._on_sheet_changed)
        for selector in (
            self._origin_column_selector,
            self._destination_column_selector,
            self._result_column_selector,
            self._result_duration_column_selector,
        ):
            selector.currentTextChanged.connect(self._on_mapping_changed)
        self._provider_selector.currentTextChanged.connect(
            self._on_provider_configuration_changed
        )
        self._travel_mode_selector.currentTextChanged.connect(
            self._on_provider_configuration_changed
        )
        for checkbox in (
            self._avoid_tolls_checkbox,
            self._avoid_highways_checkbox,
            self._avoid_ferries_checkbox,
        ):
            checkbox.toggled.connect(self._on_provider_option_toggled)
        self._skip_existing_results_checkbox.toggled.connect(
            self._on_resume_option_toggled
        )
        self._toggle_source_panels_button.toggled.connect(
            self._set_source_panels_hidden
        )
        self._toggle_config_button.toggled.connect(self._set_config_hidden)
        self._preview_status_filter.currentIndexChanged.connect(
            self._on_preview_status_filter_changed
        )
        self._workspace_splitter.splitterMoved.connect(
            self._on_workspace_splitter_moved
        )

    def _apply_initial_state(self) -> None:
        self.clear_selected_file()
        self.set_recent_files([])
        self._sync_route_option_availability()
        self._validate_provider_configuration()
        self._update_workspace_readiness()
        self.clear_batch_summary()

    def _show_worksheet(self, worksheet: WorksheetInfo) -> None:
        self._current_worksheet = worksheet
        self._row_count_value.setText(f"{worksheet.row_count:,}")
        self._column_count_value.setText(f"{worksheet.column_count:,}")
        has_headers = bool(worksheet.headers and any(worksheet.headers))
        self._headers_status_value.setText("Yes" if has_headers else "No")
        self._populate_column_mapping(worksheet.headers)
        self._render_preview(worksheet)

    def _render_preview(self, worksheet: WorksheetInfo) -> None:
        workbook_info = self._workbook_info
        if workbook_info is not None and Path(workbook_info.file_path).is_file():
            try:
                source = self._virtual_source_factory.create(
                    workbook_info.file_path,
                    worksheet.name,
                )
            except Exception:
                self._render_legacy_preview(worksheet)
                return

            self._preview_model.set_source(source)
            self._update_preview_title(
                row_count=self._preview_model.rowCount(),
                virtual=True,
            )
            self._refresh_selected_preview_status_filter_count()
            self._refresh_preview_view()
            return

        self._render_legacy_preview(worksheet)

    def _render_legacy_preview(self, worksheet: WorksheetInfo) -> None:
        headers = list(worksheet.headers)
        column_count = max(
            worksheet.column_count,
            len(headers),
            max((len(row) for row in worksheet.preview_rows), default=0),
        )
        if not headers:
            headers = [f"Column {index}" for index in range(1, column_count + 1)]
        elif len(headers) < column_count:
            headers.extend(
                f"Column {index}" for index in range(len(headers) + 1, column_count + 1)
            )
        rows = [
            list(row) + [""] * (column_count - len(row))
            for row in worksheet.preview_rows
        ]
        self._preview_model.set_data(headers, rows)
        self._update_preview_title(
            row_count=self._preview_model.rowCount(),
            virtual=False,
        )
        self._refresh_selected_preview_status_filter_count()
        self._refresh_preview_view()

    def _update_preview_title(
        self,
        *,
        row_count: int,
        virtual: bool,
    ) -> None:
        if row_count == 0:
            self._preview_title.setText("Data Preview (no data rows)")
            return

        suffix = "data rows" if virtual else "cached rows"
        self._preview_title.setText(f"Data Preview ({row_count:,} {suffix})")

    def _refresh_preview_view(self) -> None:
        """Reset selection and viewport after the preview model changes."""
        self._preview_table.selectionModel().clearSelection()
        self._preview_table.setCurrentIndex(QModelIndex())
        self._preview_table.scrollToTop()
        self._resize_preview_columns()

    def set_source_panels_visible(self, visible: bool) -> None:
        """Select the source-panels or workbook-inspector workspace view."""
        hidden = not visible
        self._toggle_source_panels_button.blockSignals(True)
        self._toggle_source_panels_button.setChecked(hidden)
        self._toggle_source_panels_button.blockSignals(False)
        self._apply_source_panels_state(hidden, emit_signal=False)

    def update_theme_icons(self, theme_name: str) -> None:
        """Refresh theme-sensitive workspace icons."""
        self._theme_name = theme_name
        upload_color = "#2563EB" if theme_name == "light" else "#60A5FA"
        control_color = "#111827" if theme_name == "light" else "#F9FAFB"
        self._set_drop_icon_color(upload_color)

        source_icon = (
            "fa5s.chevron-right"
            if self._toggle_source_panels_button.isChecked()
            else "fa5s.chevron-left"
        )
        config_icon = (
            "fa5s.chevron-down"
            if self._toggle_config_button.isChecked()
            else "fa5s.chevron-up"
        )
        self._toggle_source_panels_button.setIcon(
            qta.icon(source_icon, color=control_color)
        )
        self._toggle_config_button.setIcon(qta.icon(config_icon, color=control_color))

    def _set_drop_icon_color(self, color: str) -> None:
        self._drop_icon.setPixmap(qta.icon("fa5s.upload", color=color).pixmap(36, 36))

    @property
    def source_panels_visible(self) -> bool:
        return not self._toggle_source_panels_button.isChecked()

    def workspace_splitter_state(self) -> QByteArray:
        return self._workspace_splitter.saveState()

    def restore_workspace_splitter_state(self, state: object) -> bool:
        if isinstance(state, QByteArray):
            return self._workspace_splitter.restoreState(state)
        if isinstance(state, (bytes, bytearray, memoryview)):
            return self._workspace_splitter.restoreState(QByteArray(bytes(state)))
        return False

    def _set_source_panels_hidden(self, hidden: bool) -> None:
        self._apply_source_panels_state(hidden, emit_signal=True)

    def _apply_source_panels_state(
        self,
        hidden: bool,
        *,
        emit_signal: bool,
    ) -> None:
        workbook_loaded = self._workbook_info is not None
        # Before a workbook exists there is no inspector view to switch to.
        if not workbook_loaded:
            hidden = False
            self._toggle_source_panels_button.blockSignals(True)
            self._toggle_source_panels_button.setChecked(False)
            self._toggle_source_panels_button.blockSignals(False)

        self._update_workspace_panel_visibility()
        self._toggle_source_panels_button.setText(
            "Show File Panels" if hidden else "Hide File Panels"
        )
        self._toggle_source_panels_button.setToolTip(
            "Show Drag & Drop and Recent Workbooks"
            if hidden
            else "Hide Drag & Drop and Recent Workbooks"
        )
        icon_name = "fa5s.chevron-right" if hidden else "fa5s.chevron-left"
        icon_color = "#111827" if self._theme_name == "light" else "#F9FAFB"
        self._toggle_source_panels_button.setIcon(qta.icon(icon_name, color=icon_color))
        if emit_signal:
            self.source_panels_visibility_changed.emit(not hidden)

    def _update_workspace_panel_visibility(self) -> None:
        workbook_loaded = self._workbook_info is not None
        source_panels_hidden = (
            workbook_loaded and self._toggle_source_panels_button.isChecked()
        )
        self._toggle_source_panels_button.setEnabled(workbook_loaded)
        self._source_panels_container.setVisible(not source_panels_hidden)
        self._inspector_frame.setVisible(source_panels_hidden)
        self._inspector_controls_frame.setVisible(source_panels_hidden)
        self._preview_frame.setVisible(source_panels_hidden)

    def _set_config_hidden(self, hidden: bool) -> None:
        self._mapping_frame.setVisible(not hidden)
        self._provider_frame.setVisible(not hidden)
        self._toggle_config_button.setText("Show Config" if hidden else "Hide Config")
        self._toggle_config_button.setToolTip(
            "Show Column Mapping and Route Provider configuration"
            if hidden
            else "Hide Column Mapping and Route Provider configuration"
        )
        icon_name = "fa5s.chevron-down" if hidden else "fa5s.chevron-up"
        icon_color = "#111827" if self._theme_name == "light" else "#F9FAFB"
        self._toggle_config_button.setIcon(qta.icon(icon_name, color=icon_color))

    def _on_workspace_splitter_moved(self, _position: int, _index: int) -> None:
        self.workspace_splitter_state_changed.emit(self._workspace_splitter.saveState())

    def _resize_preview_columns(self) -> None:
        header = self._preview_table.horizontalHeader()
        for column in range(self._preview_model.columnCount()):
            label = str(
                self._preview_model.headerData(column, Qt.Orientation.Horizontal) or ""
            )
            width = min(max(120, len(label) * 9 + 28), 360)
            header.resizeSection(column, width)

    def _clear_worksheet_details(self) -> None:
        self._current_worksheet = None
        for label in (
            self._row_count_value,
            self._column_count_value,
            self._headers_status_value,
        ):
            label.setText("0")
        self._preview_model.clear()
        self._update_preview_title(row_count=0, virtual=False)
        self._refresh_preview_view()
        self._populate_column_mapping(())

    def _on_sheet_changed(self, sheet_name: str) -> None:
        if self._workbook_info is None:
            return
        worksheet = next(
            (
                sheet
                for sheet in self._workbook_info.worksheets
                if sheet.name == sheet_name
            ),
            None,
        )
        if worksheet is not None:
            self._show_worksheet(worksheet)
            self.sheet_changed.emit(sheet_name)

    def _on_recent_file_activated(self, item: QListWidgetItem) -> None:
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(file_path, str):
            self.file_selected.emit(file_path)

    def _event_file_path(self, event: QDragEnterEvent | QDropEvent) -> str | None:
        urls = event.mimeData().urls()
        if len(urls) != 1 or not urls[0].isLocalFile():
            return None
        file_path = urls[0].toLocalFile()
        return file_path if self.accepts_file(file_path) else None

    def _reset_drop_zone(self) -> None:
        self._drop_zone.setProperty("dragActive", False)
        self._refresh_style(self._drop_zone)

    @staticmethod
    def _refresh_style(widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _mapping_selector(
        self,
        caption: str,
        object_name: str,
        layout: QGridLayout,
        column: int,
    ) -> QComboBox:
        label = QLabel(caption, self._mapping_frame)
        label.setObjectName("lblInspectorCaption")
        selector = QComboBox(self._mapping_frame)
        selector.setObjectName(object_name)
        layout.addWidget(label, 1, column - 1)
        layout.addWidget(selector, 2, column - 1)
        return selector

    def _populate_column_mapping(self, headers: tuple[str, ...]) -> None:
        selectors = (
            self._origin_column_selector,
            self._destination_column_selector,
            self._result_column_selector,
            self._result_duration_column_selector,
        )
        for selector in selectors:
            selector.blockSignals(True)
            selector.clear()
            selector.addItem("Select column…", "")
            for index, header in enumerate(headers, start=1):
                display_name = header or f"Column {index}"
                selector.addItem(display_name, display_name)
            selector.blockSignals(False)
        self._auto_detect_mapping(headers)
        self._validate_mapping()

    def _auto_detect_mapping(self, headers: tuple[str, ...]) -> None:
        normalized = {header.casefold().strip(): header for header in headers if header}
        keyword_groups = (
            (
                self._origin_column_selector,
                ("origin", "from", "điểm đi", "nơi đi", "tọa độ nơi đi"),
            ),
            (
                self._destination_column_selector,
                (
                    "destination",
                    "to",
                    "điểm đến",
                    "nơi đến",
                    "tọa độ nơi đến",
                ),
            ),
            (
                self._result_column_selector,
                (
                    "result distance",
                    "distance",
                    "kilomet",
                    "kilometer",
                    "kilometre",
                    "km",
                    "khoảng cách",
                    "quãng đường",
                    "kết quả",
                ),
            ),
            (
                self._result_duration_column_selector,
                (
                    "result duration",
                    "duration",
                    "travel time",
                    "time",
                    "thời gian di chuyển",
                    "thời gian",
                    "thoi gian di chuyen",
                    "thoi gian",
                ),
            ),
        )
        for selector, keywords in keyword_groups:
            match = next(
                (
                    header
                    for key, header in normalized.items()
                    if any(word in key for word in keywords)
                ),
                None,
            )
            if match is not None:
                selector.setCurrentText(match)

        self._auto_detect_result_columns_from_blank_data(headers)

    def _auto_detect_result_columns_from_blank_data(
        self,
        headers: tuple[str, ...],
    ) -> None:
        if (
            self._result_column_selector.currentData()
            and self._result_duration_column_selector.currentData()
        ):
            return

        worksheet = self._current_worksheet
        if worksheet is None or not worksheet.preview_rows:
            return

        used_columns = {
            value
            for value in (
                self._origin_column_selector.currentData(),
                self._destination_column_selector.currentData(),
            )
            if isinstance(value, str) and value
        }
        result_distance = self._result_column_selector.currentData()
        result_duration = self._result_duration_column_selector.currentData()
        for value in (result_distance, result_duration):
            if isinstance(value, str) and value:
                used_columns.add(value)

        ranked_columns: list[tuple[int, int, str]] = []
        for index, header in enumerate(headers):
            display_name = header or f"Column {index + 1}"
            if display_name in used_columns:
                continue
            blank_count = sum(
                self._is_blank_preview_value(row[index] if index < len(row) else "")
                for row in worksheet.preview_rows
            )
            ranked_columns.append((-blank_count, index, display_name))

        ranked_columns.sort()
        candidates = [name for _blank, _index, name in ranked_columns]

        if not self._result_column_selector.currentData() and candidates:
            distance_column = candidates.pop(0)
            self._result_column_selector.setCurrentText(distance_column)

        if not self._result_duration_column_selector.currentData() and candidates:
            duration_column = candidates.pop(0)
            self._result_duration_column_selector.setCurrentText(duration_column)

    @staticmethod
    def _is_blank_preview_value(value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        return False

    def _on_mapping_changed(self, _value: str) -> None:
        self._validate_mapping()

    def _validate_mapping(self) -> None:
        origin = self._origin_column_selector.currentData() or ""
        destination = self._destination_column_selector.currentData() or ""
        result = self._result_column_selector.currentData() or ""
        duration = self._result_duration_column_selector.currentData() or ""
        selected = [value for value in (origin, destination, result, duration) if value]
        self._mapping_valid = len(selected) == 4 and len(set(selected)) == 4
        if self._mapping_valid:
            self._mapping_status.setText("Mapping ready")
            self._mapping_status.setProperty("valid", True)
            self.column_mapping_changed.emit(origin, destination, result, duration)
        elif len(selected) != len(set(selected)):
            self._mapping_status.setText("Each role must use a different column")
            self._mapping_status.setProperty("valid", False)
        else:
            self._mapping_status.setText(
                (
                    "Select origin, destination, result distance "
                    "and result duration columns"
                )
            )
            self._mapping_status.setProperty("valid", False)
        self._refresh_style(self._mapping_status)
        self._update_workspace_readiness()

    def _on_resume_option_toggled(self, _checked: bool) -> None:
        self._update_workspace_readiness()

    def _on_provider_configuration_changed(self, _value: str) -> None:
        self._sync_route_option_availability()
        self._validate_provider_configuration()

    def _selected_provider_definition(
        self,
    ) -> ProviderDefinition | None:
        provider_value = self._provider_selector.currentData()
        if not provider_value:
            return None
        return provider_definition(ProviderType(str(provider_value)))

    def _sync_route_option_availability(self) -> None:
        definition = self._selected_provider_definition()
        if definition is None or not definition.execution_enabled:
            for checkbox in (
                self._avoid_tolls_checkbox,
                self._avoid_highways_checkbox,
                self._avoid_ferries_checkbox,
            ):
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            return

        mode = self._travel_mode_selector.currentData()
        walking = mode == TravelMode.WALKING.value
        tolls_enabled = definition.supports_avoid_tolls and not walking
        highways_enabled = definition.supports_avoid_highways and not walking
        ferries_enabled = definition.supports_avoid_ferries

        for checkbox, enabled in (
            (self._avoid_tolls_checkbox, tolls_enabled),
            (self._avoid_highways_checkbox, highways_enabled),
            (self._avoid_ferries_checkbox, ferries_enabled),
        ):
            checkbox.setEnabled(enabled)
            if not enabled:
                checkbox.setChecked(False)

    def _on_provider_option_toggled(self, _checked: bool) -> None:
        self._sync_route_option_availability()
        self._validate_provider_configuration()

    def _current_provider_values(self) -> tuple[object, object]:
        provider = self._provider_selector.currentData()
        travel_mode = self._travel_mode_selector.currentData()
        return provider, travel_mode

    def _validate_provider_configuration(self) -> None:
        provider, travel_mode = self._current_provider_values()
        definition = self._selected_provider_definition()
        if definition is None:
            self._provider_valid = False
            self._provider_status.setText("Select a provider and travel mode")
            self._provider_status.setProperty("valid", False)
        elif not travel_mode:
            self._provider_valid = False
            self._provider_status.setText("Select a provider and travel mode")
            self._provider_status.setProperty("valid", False)
        elif not definition.execution_enabled:
            self._provider_valid = False
            if definition.engine_ready:
                status = (
                    f"{definition.display_name} engine ready; "
                    "result parsing starts in Sprint "
                    f"{definition.roadmap_sprint}"
                )
            else:
                status = (
                    f"{definition.display_name} foundation ready; "
                    f"engine starts in Sprint {definition.roadmap_sprint}"
                )
            self._provider_status.setText(status)
            self._provider_status.setProperty("valid", False)
        else:
            self._provider_valid = True
            self._provider_status.setText("Provider ready")
            self._provider_status.setProperty("valid", True)
            self.provider_configuration_changed.emit(
                provider,
                travel_mode,
                self._avoid_tolls_checkbox.isChecked(),
                self._avoid_highways_checkbox.isChecked(),
                self._avoid_ferries_checkbox.isChecked(),
            )

        self._refresh_style(self._provider_status)
        self._update_workspace_readiness()

    def _update_workspace_readiness(self) -> None:
        configuration = self.workspace_configuration
        ready = configuration is not None
        if ready:
            self._workspace_readiness_status.setText("Setup ready for calculation")
            self._workspace_readiness_status.setProperty("valid", True)
            self.workspace_configuration_changed.emit(configuration)
        elif not self._mapping_valid and not self._provider_valid:
            self._workspace_readiness_status.setText(
                "Complete column mapping and provider configuration"
            )
            self._workspace_readiness_status.setProperty("valid", False)
        elif not self._mapping_valid:
            self._workspace_readiness_status.setText("Complete column mapping")
            self._workspace_readiness_status.setProperty("valid", False)
        else:
            self._workspace_readiness_status.setText("Complete provider configuration")
            self._workspace_readiness_status.setProperty("valid", False)

        if ready != self._workspace_ready:
            self._workspace_ready = ready
            self.workspace_ready_changed.emit(ready)
        self._refresh_style(self._workspace_readiness_status)

    def set_workspace_locked(self, locked: bool) -> None:
        """Lock or unlock all inputs that define a calculation job."""
        self._workspace_locked = locked
        enabled = not locked
        self._source_panels_container.setEnabled(enabled)
        self._sheet_selector.setEnabled(enabled)
        self._mapping_frame.setEnabled(enabled)
        self._provider_frame.setEnabled(enabled)

    def _create_section_frame(self, object_name: str) -> QFrame:
        frame = QFrame(self)
        frame.setObjectName(object_name)
        return frame

    def _section_title(self, text: str) -> QLabel:
        label = QLabel(text, self)
        label.setObjectName("lblSectionTitle")
        return label

    def _summary_value(self, caption: str, parent_layout: QHBoxLayout) -> QLabel:
        block = QVBoxLayout()
        caption_label = QLabel(caption, self._inspector_frame)
        caption_label.setObjectName("lblInspectorCaption")
        value = QLabel("0", self._inspector_frame)
        value.setObjectName("lblSummaryValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        block.addWidget(caption_label, alignment=Qt.AlignmentFlag.AlignCenter)
        block.addWidget(value, alignment=Qt.AlignmentFlag.AlignCenter)
        parent_layout.addLayout(block, 1)
        return value
