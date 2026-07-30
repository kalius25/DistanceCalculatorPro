# Development Principles

DistanceCalculatorPro

Version 1.0

Status: Approved

---

# Mục tiêu

Các nguyên tắc này nhằm đảm bảo mọi thay đổi trong dự án đều hướng tới:

* Trải nghiệm người dùng tốt hơn.
* Kiến trúc ổn định.
* Dễ bảo trì.
* Dễ mở rộng.
* Chất lượng mã nguồn cao.

---

# DP-001 Business First

Business Layer là trung tâm của hệ thống.

Mọi tính năng mới phải được thiết kế từ Business Layer trước, sau đó mới đến UI.

Không đưa business logic vào:

* MainWindow
* Dialog
* Widget
* QThread
* Signal/Slot

---

# DP-002 Presentation Only

Presentation Layer chỉ có trách nhiệm:

* Hiển thị dữ liệu.
* Nhận thao tác người dùng.
* Gọi Controller.
* Hiển thị kết quả.

Presentation Layer không được:

* Tính toán khoảng cách.
* Đọc Excel trực tiếp.
* Truy cập Selenium.
* Thực hiện business validation.

---

# DP-003 Backward Compatibility

Mọi thay đổi phải hạn chế làm hỏng:

* API hiện có.
* Unit Test.
* Business Flow.
* Dữ liệu cũ.

Nếu bắt buộc thay đổi, phải có kế hoạch migration rõ ràng.

---

# DP-004 Small Iteration

Mỗi Sprint chỉ giải quyết một nhóm chức năng.

Không phát triển nhiều tính năng lớn trong cùng một Sprint.

---

# DP-005 Test Before Merge

Không merge nếu:

* Test chưa PASS.
* Coverage giảm.
* Architecture bị vi phạm.

---

# DP-006 UI Responsiveness

Mọi tác vụ kéo dài hơn khoảng 100ms đều phải chạy ngoài UI Thread.

Main Thread chỉ dùng để:

* Render giao diện.
* Xử lý sự kiện.
* Hiển thị kết quả.

---

# DP-007 Single Source of Truth

Một dữ liệu chỉ có một nơi chịu trách nhiệm quản lý.

Ví dụ:

* RouteRequest
* RouteResult
* Configuration

Không tạo nhiều bản sao cùng một trạng thái.

---

# DP-008 Consistency

Tên class.

Tên widget.

Tên signal.

Tên method.

Tên file.

Phải thống nhất trong toàn bộ dự án.

---

# DP-009 Simplicity

Ưu tiên:

* Dễ đọc.
* Dễ debug.
* Dễ bảo trì.

Không tối ưu quá sớm.

Không over-engineering.

---

# DP-010 Release Quality

Mỗi phiên bản phát hành phải đạt:

✓ Build thành công

✓ Test PASS

✓ Coverage đạt yêu cầu

✓ UI ổn định

✓ Không có lỗi nghiêm trọng

---

# DP-011 User Experience First

Nếu có nhiều phương án kỹ thuật đúng,

hãy chọn phương án mang lại trải nghiệm người dùng tốt hơn.

---

# DP-012 Architecture Freeze

Business Architecture chỉ thay đổi khi có lý do rõ ràng.

Không refactor chỉ vì sở thích cá nhân.

---

# DP-013 Incremental Dependency Principle

Chỉ bổ sung thư viện vào `requirements.txt` khi Sprint hiện tại thực sự bắt đầu
sử dụng thư viện đó.

Không cài đặt trước dependency chưa dùng.

Dự án chỉ duy trì một file `requirements.txt`; các nhóm dependency được phân
chia bằng comment và cập nhật cùng Sprint phát sinh nhu cầu.
