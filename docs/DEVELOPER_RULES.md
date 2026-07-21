Developer Rules v1.0 (Frozen)
DR-001 — Minimal Modification

Chỉ sửa những file thực sự cần thiết.

Không refactor ngoài phạm vi Sprint.
Không đổi tên file/class nếu không có lý do kiến trúc.
Không sửa code chỉ vì "đẹp hơn".

Mục tiêu: Giảm rủi ro và giữ lịch sử thay đổi rõ ràng.

DR-002 — Single Responsibility per Work Package

Mỗi Work Package chỉ có một mục tiêu chính.

Ví dụ:

WP-1.1 → Core Foundation
WP-1.2 → Models
WP-1.3 → Services

Không trộn GUI vào WP của Foundation.

Mục tiêu: Dễ kiểm thử, dễ rollback.

DR-003 — Backlog First

Nếu phát hiện vấn đề ngoài phạm vi Sprint:

Không sửa ngay.
Đánh dấu vào Product Backlog.
Chỉ thực hiện khi được đưa vào Sprint phù hợp.

Mục tiêu: Chống "scope creep".

DR-004 — Backward Compatibility First

Mọi thay đổi trong Sprint phải ưu tiên:

Không phá chức năng đang chạy.
Không đổi API nội bộ nếu chưa cần.
Không thay đổi hành vi mặc định nếu người dùng không yêu cầu.
Nếu bắt buộc phải thay đổi hành vi, phải có kế hoạch chuyển đổi (migration) hoặc tương thích ngược.

Đây là nguyên tắc tôi sẽ tuân thủ xuyên suốt dự án, đặc biệt vì DistanceCalculatorPro đã có nền tảng hoạt động.