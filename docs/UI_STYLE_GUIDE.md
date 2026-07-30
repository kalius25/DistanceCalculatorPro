# UI_STYLE_GUIDE.md

DistanceCalculatorPro

Version 1.0

Status: Approved

---

# 1. Mục đích

UI Style Guide mô tả cách xây dựng giao diện người dùng thống nhất cho toàn bộ ứng dụng.

Tài liệu này là phần bổ sung cho:

* DESIGN_SYSTEM.md
* DEVELOPMENT_PRINCIPLES.md

Mọi màn hình mới phải tuân thủ tài liệu này.

---

# 2. Triết lý thiết kế

DistanceCalculatorPro là phần mềm phục vụ công việc.

Giao diện phải hướng tới:

* Hiệu quả
* Rõ ràng
* Nhanh
* Ít thao tác
* Dễ học
* Dễ sử dụng trong thời gian dài

Không theo phong cách trình diễn.

Không ưu tiên hiệu ứng.

---

# 3. Layout tổng thể

Tất cả các màn hình đều sử dụng cấu trúc sau.

```text
┌──────────────────────────────────────────────────────────────┐
│ Menu Bar                                                    │
├──────────────────────────────────────────────────────────────┤
│ Toolbar                                                     │
├──────────────┬───────────────────────────────────────────────┤
│ Navigation   │                                               │
│              │                                               │
│              │                                               │
│              │               Content Area                    │
│              │                                               │
│              │                                               │
│              │                                               │
├──────────────┴───────────────────────────────────────────────┤
│ Status Bar                                                   │
└──────────────────────────────────────────────────────────────┘
```

---

# 4. Navigation

Navigation luôn nằm bên trái.

Không thay đổi vị trí.

Danh sách mặc định:

```text
Home

History

Settings

About
```

Mỗi mục:

* Icon
* Tên
* Không có submenu

---

# 5. Trang Home

Đây là màn hình làm việc chính.

Thứ tự các nhóm luôn cố định.

```text
FILE

↓

COLUMN MAPPING

↓

ROUTE SETTINGS

↓

DATA PREVIEW

↓

PROGRESS

↓

ACTIVITY LOG
```

Không thay đổi thứ tự.

---

# 6. File Section

```text
+------------------------------------------------+

FILE

File

[__________________________] [Browse]

Sheet

[Data ▼]

+------------------------------------------------+
```

Quy tắc:

Browse luôn ở bên phải.

Textbox chiếm toàn bộ chiều rộng còn lại.

---

# 7. Column Mapping

```text
+------------------------------------------------+

COLUMN MAPPING

Origin

[Origin ▼]

Destination

[Destination ▼]

Distance

[Distance ▼]

Duration

[Duration ▼]

+------------------------------------------------+
```

Label luôn nằm phía trên điều khiển.

Không đặt label bên trái.

---

# 8. Route Settings

```text
+------------------------------------------------+

ROUTE SETTINGS

Provider

Travel Mode

Language

Region

Timeout

Alternative Routes

Avoid Tolls

Avoid Highways

Avoid Ferry

+------------------------------------------------+
```

Checkbox luôn đặt phía dưới các ComboBox.

Không xen kẽ.

---

# 9. Data Preview

Sử dụng toàn bộ chiều ngang.

Các cột mặc định:

```text
Row

Origin

Destination

Status
```

Canh trái.

Không canh giữa dữ liệu văn bản.

---

# 10. Progress

```text
Progress Bar

Processed

Success

Failed

Elapsed

ETA

Buttons
```

Buttons luôn theo thứ tự:

```text
Start

Pause

Stop

Retry Failed
```

Không thay đổi.

---

# 11. Activity Log

Log luôn nằm cuối.

Chiếm toàn bộ chiều ngang.

Mỗi dòng gồm:

```text
Time

Level

Message
```

Ví dụ:

```text
23:15:18

INFO

Started calculation.
```

---

# 12. Button Style

Button chính

* Start
* Browse
* Save

Button phụ

* Pause
* Retry
* Reset

Button nguy hiểm

* Stop
* Delete

Mỗi nhóm dùng cùng một kiểu trên toàn bộ ứng dụng.

---

# 13. Khoảng cách

Mọi widget đều căn theo lưới 8 px.

Không có widget nào chạm sát nhau.

Mỗi GroupBox cách nhau 16 px.

---

# 14. Căn lề

Tất cả Label đều căn trái.

Tất cả TextBox cùng chiều rộng.

Tất cả ComboBox cùng chiều rộng.

Button cùng chiều cao.

---

# 15. Bảng dữ liệu

Không cho phép:

* Viền dày
* Màu nền sặc sỡ
* Font khác nhau

Hàng được chọn chỉ đổi màu nền nhẹ.

---

# 16. Empty State

Ví dụ Preview.

Nếu chưa mở file.

Hiển thị:

```text
No data available.
```

Không hiển thị bảng trắng.

---

# 17. Loading

Không khóa cửa sổ.

Hiển thị:

* Progress Bar
* ETA
* Trạng thái hiện tại

Người dùng vẫn có thể:

* Di chuyển cửa sổ
* Cuộn Log
* Chuyển Theme (nếu an toàn)

---

# 18. Error Style

Thông báo lỗi phải:

* Ngắn gọn
* Có hướng xử lý
* Không hiển thị stack trace

Ví dụ:

Sai:

```text
AttributeError
```

Đúng:

```text
Không thể đọc Sheet "Data".

Vui lòng kiểm tra tên Sheet hoặc mở lại file Excel.
```

---

# 19. Tooltip

Tất cả điều khiển chính phải có Tooltip.

Ví dụ:

Avoid Ferry

```text
Không sử dụng tuyến đường có phà nếu nhà cung cấp bản đồ hỗ trợ.
```

Timeout

```text
Thời gian tối đa chờ phản hồi cho mỗi yêu cầu.
```

---

# 20. Icon Style

Toàn bộ icon:

* SVG
* Một phong cách
* Một kích thước
* Không trộn nhiều bộ icon

---

# 21. Dialog Style

Tiêu đề.

Nội dung.

Nút hành động.

Theo đúng thứ tự.

Ví dụ:

```text
Calculation Completed

1,250 rows processed successfully.

[Open Result]

[Close]
```

---

# 22. Status Bar

Luôn hiển thị:

```text
Ready

Provider

Theme

Version
```

Trong khi chạy:

```text
Running

Google

Light

v1.2.0
```

---

# 23. Theme

Không đổi vị trí widget giữa Light và Dark.

Chỉ thay đổi:

* Màu
* Border
* Shadow (nếu có)

---

# 24. Keyboard Flow

Tab phải đi theo đúng thứ tự:

```text
File

↓

Browse

↓

Sheet

↓

Origin

↓

Destination

↓

Distance

↓

Duration

↓

Provider

↓

Travel Mode

↓

Language

↓

Region

↓

Timeout

↓

Alternative Routes

↓

Avoid Tolls

↓

Avoid Highways

↓

Avoid Ferry

↓

Start
```

Không để Tab nhảy lung tung.

---

# 25. Responsive Rules

Khi cửa sổ lớn hơn.

Preview mở rộng.

Log mở rộng.

Khoảng trắng tăng đều.

Không phóng to Button.

---

# 26. Naming

Tên hiển thị phải ngắn.

Ví dụ:

Đúng:

```text
History

Settings

About
```

Sai:

```text
Application History

Software Configuration

About This Application
```

---

# 27. Screen Review Checklist

Mỗi màn hình trước khi hoàn thành phải kiểm tra:

□ Tuân thủ Design System.

□ Khoảng cách đúng chuẩn.

□ Font đúng.

□ Không hardcode màu.

□ Tooltip đầy đủ.

□ Keyboard Tab đúng.

□ Có Empty State.

□ Có Error State.

□ Có Loading State.

□ Không có business logic.

□ Hỗ trợ Light Theme.

□ Hỗ trợ Dark Theme.

□ Hoạt động ở 125%, 150% và 200% DPI.

□ Widget đặt tên đúng chuẩn.

□ Không có điều khiển dư thừa.

---

# 28. Wireframe Library

Các màn hình chuẩn của ứng dụng gồm:

* Home
* History
* Settings
* About

Các màn hình bổ sung trong tương lai:

* Provider Manager
* Batch History
* Route Comparison
* Cache Manager
* Logs
* Diagnostics
* Logistics Intelligence Dashboard

Mỗi màn hình mới phải có wireframe được phê duyệt trước khi bắt đầu lập trình.

---

# 29. UX Review

Một chức năng mới chỉ được chấp nhận khi:

* Người dùng mới có thể hiểu trong vòng 5 phút.
* Không cần đọc tài liệu để hoàn thành tác vụ cơ bản.
* Không phát sinh thao tác thừa.
* Không làm thay đổi quy trình quen thuộc của người dùng nếu không cần thiết.

---

# 30. Definition of Done

Một màn hình UI chỉ được xem là hoàn thành khi đáp ứng đồng thời:

* Đúng wireframe đã được phê duyệt.
* Tuân thủ Design System.
* Tuân thủ UI Style Guide.
* Hoạt động ổn định trên Light và Dark Theme.
* Không chứa business logic.
* Có đầy đủ Empty State, Loading State và Error State.
* Hỗ trợ điều hướng bằng chuột và bàn phím.
* Được kiểm thử trên các mức DPI chuẩn của Windows.
* Sẵn sàng tái sử dụng làm mẫu cho các màn hình khác.
