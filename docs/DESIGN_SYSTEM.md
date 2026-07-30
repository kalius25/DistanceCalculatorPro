# DESIGN_SYSTEM.md

DistanceCalculatorPro

Version 1.0

Status: Approved

---

# 1. Mục tiêu

Design System định nghĩa toàn bộ tiêu chuẩn giao diện của DistanceCalculatorPro nhằm đảm bảo:

* Giao diện nhất quán.
* Dễ sử dụng.
* Dễ mở rộng.
* Dễ bảo trì.
* Phù hợp với ứng dụng desktop chuyên nghiệp.

Design System áp dụng cho toàn bộ các phiên bản từ v1.2 trở đi.

---

# 2. Design Principles

## DS-001 Professional

Ưu tiên cảm giác:

* Chuyên nghiệp.
* Gọn gàng.
* Tin cậy.

Không sử dụng hiệu ứng màu mè hoặc hoạt ảnh không cần thiết.

---

## DS-002 Function First

Mọi thành phần UI phải phục vụ công việc.

Không thêm thành phần chỉ để trang trí.

---

## DS-003 Consistency

Các màn hình phải có:

* cùng khoảng cách
* cùng màu
* cùng font
* cùng kích thước nút
* cùng cách hiển thị trạng thái

---

## DS-004 Simple

Người dùng phải hiểu cách sử dụng trong vòng vài phút.

Không tạo giao diện phức tạp.

---

# 3. Theme

Hỗ trợ:

* Light
* Dark

Mọi màu đều khai báo trong file QSS.

Không hardcode màu trong Python.

---

# 4. Font

Windows

```text
Segoe UI
```

Linux

```text
Noto Sans
```

Font Size

| Thành phần   | Size |
| ------------ | ---- |
| Window Title | 18   |
| Group Title  | 13   |
| Normal Text  | 10   |
| Table        | 10   |
| Button       | 10   |
| Status Bar   | 9    |

---

# 5. Color Roles

Không sử dụng trực tiếp mã màu trong widget.

Sử dụng vai trò màu.

| Role       | Ý nghĩa            |
| ---------- | ------------------ |
| Primary    | Màu chính          |
| Secondary  | Màu phụ            |
| Success    | Thành công         |
| Warning    | Cảnh báo           |
| Error      | Lỗi                |
| Background | Nền                |
| Surface    | Panel              |
| Border     | Viền               |
| Text       | Chữ                |
| Disabled   | Thành phần vô hiệu |

Toàn bộ giá trị màu được quản lý tập trung trong theme.

---

# 6. Icon

Chỉ sử dụng:

* SVG

Bộ icon:

* Material Symbols
* Fluent Icons

Không dùng:

* PNG
* JPG
* Bitmap

---

# 7. Spacing

Đơn vị chuẩn:

```text
8 px
```

Khoảng cách tiêu chuẩn

| Thành phần      | Khoảng cách |
| --------------- | ----------- |
| Widget → Widget | 8 px        |
| Group → Group   | 16 px       |
| Page Margin     | 16 px       |
| Dialog Margin   | 20 px       |

---

# 8. Border Radius

| Thành phần | Radius |
| ---------- | ------ |
| Button     | 6      |
| TextBox    | 6      |
| ComboBox   | 6      |
| Group      | 8      |
| Dialog     | 10     |

---

# 9. Button

Chiều cao chuẩn

```text
36 px
```

Button chính

* Start
* Save
* Browse

Button phụ

* Cancel
* Close
* Reset

Button nguy hiểm

* Stop
* Delete

---

# 10. Table

Toàn bộ dữ liệu hiển thị bằng:

```text
QTableView
```

Không dùng:

```text
QTableWidget
```

Model:

```text
QAbstractTableModel
```

Để dễ mở rộng khi dữ liệu lớn.

---

# 11. Group Box

Các nhóm chức năng luôn sử dụng GroupBox.

Ví dụ

```text
FILE

COLUMN MAPPING

ROUTE SETTINGS

DATA PREVIEW

PROGRESS

LOG
```

---

# 12. Dialog

Có ba loại chuẩn.

Information

Warning

Error

Không tạo MessageBox tùy ý.

---

# 13. Status Colors

Success

Hiển thị màu Success.

Warning

Hiển thị màu Warning.

Error

Hiển thị màu Error.

Không đổi màu nền toàn bộ cửa sổ.

---

# 14. Loading

Không khóa cửa sổ.

Hiển thị:

* Progress Bar
* Spinner (nếu phù hợp)
* ETA

---

# 15. Layout

Không đặt widget bằng tọa độ tuyệt đối.

Chỉ sử dụng:

* QVBoxLayout
* QHBoxLayout
* QGridLayout
* QFormLayout

---

# 16. Navigation

Navigation cố định bên trái.

Sử dụng:

```text
QListWidget
```

hoặc

```text
QTreeWidget
```

Nội dung hiển thị bằng:

```text
QStackedWidget
```

---

# 17. Window

Kích thước mặc định

```text
1280 × 800
```

Minimum

```text
1100 × 700
```

Không cho phép resize nhỏ hơn.

---

# 18. Responsive

UI phải hoạt động tốt khi:

* 125%
* 150%
* 200%

Windows Display Scaling.

---

# 19. Keyboard

Các phím tắt mặc định

Ctrl + O

Mở Excel

Ctrl + S

Lưu

F5

Start

Esc

Cancel Dialog

---

# 20. Accessibility

Mọi Button.

Textbox.

ComboBox.

Đều có:

* Tooltip
* Accessible Name

---

# 21. Logging

Không hiển thị Exception Trace cho người dùng.

Log kỹ thuật ghi vào file.

UI chỉ hiển thị thông báo dễ hiểu.

---

# 22. Empty State

Nếu chưa mở file

Hiển thị:

```text
No Excel file selected.
```

Không hiển thị bảng rỗng.

---

# 23. Error Message

Ví dụ

Không đúng:

```text
KeyError
```

Đúng:

```text
Không tìm thấy cột "Origin".
```

---

# 24. Confirmation

Các thao tác nguy hiểm cần xác nhận.

Ví dụ

* Stop
* Overwrite
* Delete History

---

# 25. Version Display

Status Bar luôn hiển thị

```text
DistanceCalculatorPro vX.Y.Z
```

---

# 26. Resource Structure

```text
presentation/

resources/
    icons/
    images/
    fonts/

styles/
    light.qss
    dark.qss

themes/
```

---

# 27. Component Library

Các thành phần UI dùng chung phải được xây dựng thành component tái sử dụng.

Ví dụ:

* FileSelector
* ProgressPanel
* RouteSettingsPanel
* ColumnMappingPanel
* PreviewTable
* StatusIndicator
* LogViewer
* Lợi ích:

  * Giảm lặp mã.
  * Đồng nhất giao diện.
  * Dễ bảo trì.
  * Dễ kiểm thử.

---

# 28. Widget Naming Convention

Tên widget theo mẫu:

```text
<loại><ChứcNăng>
```

Ví dụ:

```text
btnStart
btnPause
btnStop

cmbProvider
cmbTravelMode

chkAvoidTolls
chkAvoidHighways
chkAvoidFerry

txtTimeout

tblPreview

lblProgress

prgCalculation

lstNavigation
```

Không sử dụng tên mặc định như:

```text
pushButton1

comboBox2

tableWidget3
```

---

# 29. Future Ready

Design System phải hỗ trợ mở rộng mà không cần thay đổi nguyên tắc cốt lõi.

Có thể bổ sung:

* Dashboard
* Multi Provider
* Logistics Intelligence
* Enterprise

mà vẫn giữ nguyên trải nghiệm người dùng.

---

# 30. Definition of Done

Một màn hình chỉ được xem là hoàn thành khi:

* Tuân thủ Design System.
* Không hardcode màu sắc.
* Không hardcode khoảng cách.
* Không dùng vị trí tuyệt đối.
* Hỗ trợ Light/Dark Theme.
* Hỗ trợ DPI Scaling.
* Widget đặt tên đúng chuẩn.
* Không có business logic trong UI.
* Có tooltip đầy đủ.
* Có xử lý trạng thái lỗi và rỗng.
* Hoạt động nhất quán với các màn hình khác.
