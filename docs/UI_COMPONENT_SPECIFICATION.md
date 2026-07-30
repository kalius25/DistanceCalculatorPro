# UI_COMPONENT_SPECIFICATION.md

DistanceCalculatorPro

Version 1.0

Status: Approved

---

# 1. Mục đích

Tài liệu này định nghĩa các UI Component chuẩn được sử dụng trong toàn bộ ứng dụng.

Mục tiêu:

* Component tái sử dụng.
* Giao diện thống nhất.
* Giảm lặp mã.
* Dễ kiểm thử.
* Dễ bảo trì.
* Không chứa Business Logic.

---

# 2. Quy tắc chung

Mọi component phải:

* Kế thừa từ QWidget (hoặc lớp Qt phù hợp).
* Chỉ đảm nhận một chức năng.
* Không gọi Service trực tiếp.
* Không đọc/ghi Excel.
* Không truy cập Provider.
* Không biết Selenium hoặc Engine.

Component chỉ:

* Hiển thị dữ liệu.
* Thu nhận thao tác người dùng.
* Phát Signal.

---

# 3. Danh sách Component

| ID     | Component          | Mục đích                 |
| ------ | ------------------ | ------------------------ |
| UI-001 | FileSelector       | Chọn file Excel và Sheet |
| UI-002 | ColumnMappingPanel | Ánh xạ các cột dữ liệu   |
| UI-003 | RouteSettingsPanel | Thiết lập tuyến đường    |
| UI-004 | PreviewTable       | Xem trước dữ liệu        |
| UI-005 | ProgressPanel      | Theo dõi tiến độ         |
| UI-006 | LogViewer          | Hiển thị nhật ký         |
| UI-007 | StatusIndicator    | Hiển thị trạng thái      |
| UI-008 | NavigationPanel    | Điều hướng               |
| UI-009 | ThemeSwitcher      | Chuyển Light/Dark        |
| UI-010 | VersionLabel       | Hiển thị phiên bản       |

---

# UI-001 FileSelector

## Mục đích

Cho phép người dùng chọn:

* File Excel
* Sheet

---

## Giao diện

```text
File

[________________________] [Browse]

Sheet

[Data ▼]
```

---

## Thuộc tính

| Property   | Kiểu |
| ---------- | ---- |
| file_path  | str  |
| sheet_name | str  |

---

## Signal

```text
fileSelected(path)

sheetChanged(name)
```

---

## Public Method

```python
set_file_path()

set_sheet_list()

current_file()

current_sheet()

clear()
```

---

## Không được phép

* Đọc Excel.
* Validate file.
* Mở Workbook.

---

# UI-002 ColumnMappingPanel

## Mục đích

Chọn các cột đầu vào và đầu ra.

---

## Giao diện

```text
Origin

Destination

Distance

Duration
```

---

## Property

```text
origin_column

destination_column

distance_column

duration_column
```

---

## Signal

```text
mappingChanged()
```

---

## Public Method

```python
set_headers()

mapping()

clear()
```

---

## Không được phép

* Kiểm tra dữ liệu.
* Tính toán.
* Sinh RouteRequest.

---

# UI-003 RouteSettingsPanel

## Mục đích

Thu thập toàn bộ cấu hình tuyến đường.

---

## Giao diện

```text
Provider

Travel Mode

Language

Region

Timeout

Alternative Routes

Avoid Tolls

Avoid Highways

Avoid Ferry
```

---

## Property

```text
provider

travel_mode

language

region

timeout

alternatives

avoid_tolls

avoid_highways

avoid_ferry
```

---

## Signal

```text
settingsChanged()
```

---

## Public Method

```python
settings()

reset()

load_settings()
```

---

## Output

Component này chỉ trả về:

```python
RouteSettings
```

---

# UI-004 PreviewTable

## Mục đích

Hiển thị dữ liệu preview.

---

## Widget

```text
QTableView
```

---

## Model

```text
QAbstractTableModel
```

---

## Public Method

```python
set_model()

clear()

refresh()
```

---

## Signal

```text
rowActivated()

selectionChanged()
```

---

## Không được phép

* Tự load dữ liệu.
* Tự sort Business Data.

---

# UI-005 ProgressPanel

## Mục đích

Hiển thị trạng thái chạy.

---

## Thành phần

```text
Progress Bar

Processed

Success

Failed

Elapsed

ETA

Buttons
```

---

## Buttons

```text
Start

Pause

Stop

Retry Failed
```

---

## Signal

```text
startClicked()

pauseClicked()

stopClicked()

retryClicked()
```

---

## Public Method

```python
update_progress()

update_eta()

update_statistics()

reset()
```

---

# UI-006 LogViewer

## Mục đích

Hiển thị Activity Log.

---

## Public Method

```python
append_info()

append_warning()

append_error()

clear()
```

---

## Signal

Không có.

---

## Không được phép

* Ghi file log.
* Logging Framework.

---

# UI-007 StatusIndicator

## Mục đích

Hiển thị trạng thái hiện tại.

Ví dụ

```text
Ready

Running

Paused

Completed

Cancelled
```

---

## Public Method

```python
set_status()

set_color()
```

---

# UI-008 NavigationPanel

## Mục đích

Điều hướng giữa các màn hình.

---

## Màn hình

```text
Home

History

Settings

About
```

---

## Signal

```text
pageChanged()
```

---

# UI-009 ThemeSwitcher

## Mục đích

Chuyển Theme.

---

## Public Method

```python
current_theme()

set_theme()
```

---

## Signal

```text
themeChanged()
```

---

# UI-010 VersionLabel

## Mục đích

Hiển thị

```text
DistanceCalculatorPro

v1.2.0
```

---

## Public Method

```python
set_version()
```

---

# 4. Quy tắc Signal

Signal chỉ mô tả **sự kiện**, không mô tả hành động.

Đúng:

```text
startClicked

themeChanged

mappingChanged
```

Sai:

```text
calculateDistance

loadExcel

openGoogle
```

---

# 5. Quy tắc Public Method

Public method chỉ dùng để:

* Thiết lập dữ liệu.
* Đọc trạng thái.
* Làm mới giao diện.

Không dùng để thực hiện nghiệp vụ.

---

# 6. State Management

Mỗi component phải hỗ trợ các trạng thái sau (nếu phù hợp):

* Empty
* Ready
* Loading
* Disabled
* Error

Việc chuyển trạng thái chỉ ảnh hưởng đến giao diện, không thay đổi dữ liệu nghiệp vụ.

---

# 7. Dependency Rule

```text
MainWindow
    │
    ├── FileSelector
    ├── ColumnMappingPanel
    ├── RouteSettingsPanel
    ├── PreviewTable
    ├── ProgressPanel
    ├── LogViewer
    └── StatusIndicator
```

Các component không được phụ thuộc lẫn nhau.

Mọi trao đổi phải thông qua:

* MainWindow
* ViewModel (nếu sử dụng)

---

# 8. Component Communication

Luồng chuẩn:

```text
User Action
      ↓
Component Signal
      ↓
MainWindow
      ↓
ViewModel
      ↓
Controller
      ↓
Service
```

Khi có kết quả:

```text
Service
      ↓
Controller
      ↓
ViewModel
      ↓
MainWindow
      ↓
Component.set_...
```

Không cho phép component gọi trực tiếp component khác.

---

# 9. Naming Convention

Tên class:

```text
FileSelector
RouteSettingsPanel
ProgressPanel
PreviewTable
```

Tên file:

```text
file_selector.py
route_settings_panel.py
progress_panel.py
preview_table.py
```

Tên widget:

```text
btnStart
cmbProvider
chkAvoidFerry
tblPreview
prgCalculation
```

---

# 10. Definition of Done

Một UI Component chỉ được xem là hoàn thành khi:

* Có một nhiệm vụ duy nhất.
* Không chứa Business Logic.
* Không phụ thuộc component khác.
* Có Signal rõ ràng.
* Có Public API rõ ràng.
* Hỗ trợ các trạng thái cần thiết.
* Tuân thủ DESIGN_SYSTEM.md.
* Tuân thủ UI_STYLE_GUIDE.md.
* Có thể tái sử dụng ở nhiều màn hình.
* Có Unit Test cho hành vi của component (nếu có logic UI).
