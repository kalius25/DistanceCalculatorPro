# CODING_CONVENTION.md

**Project:** DistanceCalculatorPro
**Version:** 1.0
**Status:** Approved
**Scope:** Presentation Layer — PySide6

---

# 1. Mục đích

Tài liệu này quy định cách viết mã cho Presentation Layer sử dụng PySide6.

Tài liệu được áp dụng cùng với:

* `CODING_STANDARD.md`
* `DEVELOPMENT_PRINCIPLES.md`
* `DESIGN_SYSTEM.md`
* `UI_STYLE_GUIDE.md`
* `UI_COMPONENT_SPECIFICATION.md`

Mục tiêu:

* Mã nguồn giao diện thống nhất.
* Dễ đọc và dễ review.
* Không đưa business logic vào UI.
* Dễ kiểm thử.
* Dễ mở rộng trong các Sprint tiếp theo.

---

# 2. Quy tắc chung

Mã nguồn Presentation Layer phải:

* Tuân thủ PEP 8.
* Có type hint cho constructor, public method, signal và giá trị trả về.
* Ưu tiên mã rõ ràng hơn mã viết tắt.
* Không chứa business logic.
* Không đọc hoặc ghi Excel trực tiếp.
* Không truy cập Provider, Engine hoặc Selenium.
* Không tạo global state.
* Không sử dụng Singleton.
* Ưu tiên Composition hơn Inheritance.

---

# 3. Quy tắc file và class

Mỗi file chỉ chứa một public class chính.

Tên file dùng:

```text
snake_case
```

Tên class dùng:

```text
PascalCase
```

Tên method và biến dùng:

```text
snake_case
```

Tên constant dùng:

```text
UPPER_SNAKE_CASE
```

Private attribute và private method bắt đầu bằng `_`.

Ví dụ:

```text
main_window.py       → MainWindow
theme_manager.py     → ThemeManager
home_page.py         → HomePage
navigation_panel.py  → NavigationPanel
```

---

# 4. Cấu trúc package

```text
presentation/
├── app.py
├── main_window.py
├── theme_manager.py
├── pages/
├── widgets/
├── dialogs/
├── workers/
├── viewmodels/
├── styles/
└── resources/
```

Mọi package Python phải có:

```text
__init__.py
```

---

# 5. Thứ tự import

Import theo thứ tự:

1. Standard Library.
2. Third-party Library.
3. Project Module.

Giữa các nhóm có một dòng trống.

```python
from pathlib import Path

from PySide6.QtWidgets import QApplication

from presentation.main_window import MainWindow
```

Không sử dụng wildcard import:

```python
from module import *
```

---

# 6. Constructor Injection

Dependency phải được truyền qua constructor.

```python
class MainWindow(QMainWindow):
    def __init__(
        self,
        application: QApplication,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__()
        self._application = application
        self._theme_manager = theme_manager
```

Widget không được tự tạo:

* Controller.
* Service.
* Provider.
* Engine.
* Shared Manager.

---

# 7. Quyền sở hữu Widget

Qt parent-child ownership phải rõ ràng.

* Parent widget sở hữu child widget.
* Dependency sống lâu được lưu bằng private attribute.
* Layout cục bộ có thể giữ ở local variable sau khi được Qt tiếp quản.
* Không giữ reference không cần thiết.

---

# 8. Thứ tự xây dựng UI

Một class giao diện nên có cấu trúc:

```python
class ExampleWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._create_actions()
        self._create_widgets()
        self._create_layout()
        self._connect_signals()
        self._apply_initial_state()
```

Các private method tiêu chuẩn:

```text
_create_actions()
_create_widgets()
_create_layout()
_create_menu_bar()
_create_toolbar()
_create_status_bar()
_connect_signals()
_apply_initial_state()
```

Không viết toàn bộ phần dựng giao diện trong `__init__()`.

---

# 9. Quy tắc đặt tên Signal

Signal phải mô tả sự kiện đã xảy ra.

Đúng:

```text
file_selected
page_changed
theme_changed
start_clicked
```

Không đúng:

```text
load_excel
calculate_distance
open_google
```

Tên signal Python sử dụng:

```text
snake_case
```

Ví dụ:

```python
page_changed = Signal(int)
```

---

# 10. Quy tắc đặt tên Slot và Handler

Internal handler dùng mẫu:

```text
_on_<event>()
```

Ví dụ:

```python
def _on_navigation_changed(self, page_index: int) -> None:
    self._content_stack.setCurrentIndex(page_index)
```

Tên method phải mô tả rõ sự kiện đang được xử lý.

---

# 11. Widget Object Name

Thuộc tính Qt `objectName` dùng tên mô tả theo dạng `camelCase`.

Ví dụ:

```text
btnStart
btnPause
btnStop

cmbProvider
cmbTravelMode

chkAvoidFerry

lstNavigation
stkContent
txtActivityLog
```

Không sử dụng:

```text
pushButton1
comboBox2
widget3
```

`objectName` được dùng cho:

* QSS selector.
* UI test.
* Debug.
* Accessibility.

---

# 12. Quy tắc Layout

Không sử dụng tọa độ tuyệt đối.

Chỉ sử dụng:

* `QVBoxLayout`
* `QHBoxLayout`
* `QGridLayout`
* `QFormLayout`

Các quy tắc:

* Khoảng cách theo Design System.
* Stretch factor phải có chủ đích.
* Không lồng layout quá sâu.
* Khi một nhóm trở nên phức tạp, tách thành component.
* Không sử dụng `setGeometry()` để bố trí giao diện.

---

# 13. Quy tắc Styling

Không hardcode màu trong Python.

Không đúng:

```python
widget.setStyleSheet("background: #ffffff;")
```

Đúng:

```text
presentation/styles/light.qss
presentation/styles/dark.qss
```

Các quy tắc:

* Style được quản lý tập trung.
* Sử dụng `objectName` hoặc dynamic property làm QSS selector.
* Không tạo style riêng tùy tiện cho từng widget.
* Không hardcode đường dẫn resource.

---

# 14. Text và Translation

Text hiển thị cho người dùng phải:

* Hoàn chỉnh.
* Dễ hiểu.
* Không hiển thị tên exception kỹ thuật.
* Có hướng xử lý khi xảy ra lỗi.
* Dễ chuyển sang Qt Translation trong tương lai.

Không dùng viết tắt nếu người dùng phổ thông có thể không hiểu.

---

# 15. Error Handling

Presentation Layer chỉ catch exception khi cần:

* Chuyển thành trạng thái giao diện.
* Hiển thị thông báo dễ hiểu.
* Ghi chi tiết kỹ thuật vào logging layer.

Không được:

* Bỏ qua exception im lặng.
* Hiển thị stack trace cho người dùng.
* Dùng exception làm luồng điều khiển thông thường.

---

# 16. Threading

Không chạy tác vụ lâu trên Qt Main Thread.

Worker thread:

* Không thay đổi widget trực tiếp.
* Giao tiếp với UI bằng signal.
* Hỗ trợ cooperative pause.
* Hỗ trợ cooperative stop.
* Không kill thread cưỡng bức.

UI update chỉ thực hiện trên Main Thread.

---

# 17. Public API của Component

Một reusable component chỉ nên public:

* Property đọc trạng thái giao diện.
* Method cập nhật dữ liệu hiển thị.
* Signal báo sự kiện người dùng.

Không public child widget nội bộ nếu không có lý do kiểm thử hoặc tích hợp rõ ràng.

Ví dụ:

```python
def current_file(self) -> str:
    ...

def set_sheet_list(self, sheets: list[str]) -> None:
    ...
```

---

# 18. State Method

Ưu tiên các method trạng thái rõ ràng:

```python
set_empty_state()
set_ready_state()
set_loading_state()
set_error_state(message)
set_disabled_state()
```

Không phân tán nhiều lệnh:

```python
setEnabled()
setVisible()
setText()
```

ở nhiều class không liên quan.

---

# 19. Quy tắc Page

Mỗi page:

* Là một `QWidget` độc lập.
* Tự sở hữu layout của mình.
* Không biết index của navigation.
* Không tự chuyển sang page khác.
* Không gọi Service.
* Không gọi Provider.
* Không đọc Excel.

Việc điều hướng do `MainWindow` hoặc Presentation Coordinator thực hiện.

---

# 20. Quy tắc MainWindow

`MainWindow` được phép:

* Ghép các presentation component.
* Điều phối signal ở cấp giao diện.
* Quản lý menu bar.
* Quản lý toolbar.
* Quản lý navigation.
* Quản lý stacked pages.
* Quản lý status bar.

`MainWindow` không được:

* Đọc Excel.
* Tính khoảng cách.
* Tạo Provider.
* Thực hiện business validation.
* Ghi file kết quả.
* Truy cập Selenium.

---

# 21. Quy tắc ThemeManager

`ThemeManager` có trách nhiệm:

* Đọc QSS.
* Áp dụng theme cho `QApplication`.
* Quản lý tên theme hiện tại.
* Kiểm tra theme hợp lệ.
* Báo lỗi rõ ràng nếu thiếu file theme.

`ThemeManager` không phụ thuộc vào `MainWindow`.

---

# 22. Logging

Sử dụng project logging system.

Không dùng:

```python
print()
```

trong application code đã commit.

Phân biệt:

* Technical Log: ghi vào file.
* Activity Log: hiển thị hoạt động dễ hiểu trên UI.

Không ghi dữ liệu nhạy cảm vào log.

---

# 23. Testing

Presentation test phải kiểm tra hành vi quan sát được.

Ví dụ:

* Window được tạo thành công.
* Navigation thay đổi active page.
* Theme action áp dụng đúng theme.
* Signal phát đúng giá trị.
* Initial state chính xác.
* Status bar hiển thị đúng dữ liệu.

Không test Qt internal implementation.

---

# 24. Comment và Docstring

Comment phải giải thích:

> Vì sao cần làm như vậy.

Không giải thích lại điều mã nguồn đã thể hiện rõ.

Public class và public method không hiển nhiên cần có docstring ngắn gọn.

---

# 25. Definition of Done

Mã nguồn Presentation Layer chỉ được xem là hoàn thành khi:

* Formatter PASS.
* Linter PASS.
* Type checking PASS.
* Test PASS.
* Coverage không giảm.
* Không có business logic trong UI.
* Không hardcode màu.
* Không sử dụng tọa độ tuyệt đối.
* Signal và object name đúng quy ước.
* Light Theme hoạt động.
* Dark Theme hoạt động.
* Keyboard navigation sử dụng được.
* Giao diện không bị block.
* Tuân thủ toàn bộ tài liệu UI đã phê duyệt.

---

# 26. Dependency Management

* Dự án chỉ sử dụng một file `requirements.txt`.
* Dependency được phân nhóm bằng comment theo mục đích và Sprint.
* Mỗi thư viện phải có ghi chú ngắn về mục đích sử dụng.
* Chỉ thêm thư viện khi Sprint hiện tại thực sự sử dụng.
* Không xóa dependency vẫn còn được mã nguồn sử dụng.
* Mọi thay đổi dependency phải được commit cùng mã nguồn sử dụng dependency đó.

---

# 27. Anonymous Callback

Ưu tiên private handler có tên rõ nghĩa thay cho `lambda` khi kết nối signal UI.

Ví dụ nên dùng:

```python
self._action_settings.triggered.connect(self._show_settings_page)
```

Không nên dùng:

```python
self._action_settings.triggered.connect(
    lambda: self._navigation.setCurrentRow(2)
)
```

`lambda` chỉ được dùng khi biểu thức rất ngắn, không tái sử dụng và không làm
mất ý nghĩa của hành vi giao diện.
