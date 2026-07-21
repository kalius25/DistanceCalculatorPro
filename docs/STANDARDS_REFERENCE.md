Standards Reference (SR)
Document Name : Standards Reference

Code          : SR

Version       : 1.0.0

Status        : FROZEN

Authoritative : YES
SR-000 Document Information
SR-001 Purpose

Standards Reference (SR) là tài liệu quản lý tập trung toàn bộ các tiêu chuẩn (Standards) đang có hiệu lực trong dự án.

SR là điểm tra cứu duy nhất để xác định:

Dự án hiện có những tiêu chuẩn nào.
Phiên bản nào đang có hiệu lực.
Trạng thái của từng tiêu chuẩn.
Quan hệ giữa các tiêu chuẩn.

SR không thay thế các tài liệu gốc mà chỉ đóng vai trò Registry.

SR-002 Scope

Áp dụng cho toàn bộ dự án DistanceCalculatorPro.

SR-003 References
DOC
ADR
SR-100 Standard Register
Code	Standard	Current Version	Status	Authoritative
DOC	Document Index	1.0.0	Frozen	Yes
SR	Standards Reference	1.0.0	Frozen	Yes
SS	Software Specification	2.0.0	Frozen	Yes
MC	Module Contract	2.0.0	Frozen	Yes
DR	Developer Rules	1.0.0	Frozen	Yes
CS	Coding Style	2.0.0	Frozen	Yes
ADR	Architecture Decision Records	Active	Active	Yes
PB	Product Backlog	1.0.0	Active	Yes
SP	Sprint Plan	1.0.0	Active	Yes
WP	Work Package	1.0.0	Active	Yes
SR-200 Status Definition
Status	Ý nghĩa
Draft	Đang soạn thảo.
Review	Đang xem xét.
Frozen	Đã phê duyệt, là chuẩn chính thức.
Active	Được cập nhật liên tục theo vòng đời dự án.
Deprecated	Không còn khuyến nghị sử dụng nhưng vẫn lưu để tham chiếu.
Retired	Không còn hiệu lực.
SR-300 Document Category
Governance Documents
DOC
SR
ADR
Engineering Standards
SS
MC
DR
CS
Project Management
PB
SP
WP
SR-400 Standard Lifecycle
Draft
   │
   ▼
Review
   │
   ▼
Frozen
   │
   ├────────► Deprecated
   │
   └────────► Retired

Riêng ADR, PB, SP và WP có vòng đời riêng nên được quản lý theo trạng thái Active thay vì Frozen.

SR-500 Update Rules
SR-501 New Standard

Khi bổ sung một tiêu chuẩn mới:

Phải được phê duyệt.
Phải được cấp mã (Code).
Phải được thêm vào Standard Register.
Nếu ảnh hưởng đến kiến trúc, phải tạo ADR mới.
SR-502 Version Update

Khi tiêu chuẩn thay đổi:

Cập nhật phiên bản.
Ghi Revision History.
Đồng bộ các tài liệu liên quan.
SR-503 Deprecation

Một tiêu chuẩn chỉ được chuyển sang Deprecated khi đã có tiêu chuẩn mới thay thế hoặc có quyết định chính thức thông qua ADR.

SR-600 Cross Reference

Mọi tài liệu phải tham chiếu bằng mã.

Ví dụ:

SS-402

MC-301

DR-004

CS-805

ADR-024

WP-1.1
SR-700 Naming Convention

Các mã chuẩn của dự án:

Code	Tên
DOC	Document Index
SR	Standards Reference
SS	Software Specification
ADR	Architecture Decision Record
MC	Module Contract
DR	Developer Rules
CS	Coding Style
PB	Product Backlog
SP	Sprint Plan
WP	Work Package

Quy tắc:

Mỗi Code là duy nhất.
Không tái sử dụng Code.
Không đổi tên Code sau khi được phê duyệt.
SR-800 Governance Principles

Tất cả tiêu chuẩn của dự án phải tuân thủ các nguyên tắc sau:

Single Source of Truth – Mỗi loại thông tin chỉ có một nguồn chính thức.
Documentation First – Tài liệu được thống nhất trước khi triển khai.
Backward Compatibility First – Hạn chế phá vỡ hành vi hiện có.
Minimal Modification – Chỉ thay đổi những gì cần thiết.
Traceability – Mọi thay đổi đều có thể truy vết qua ADR và Revision History.
Consistency – Các tiêu chuẩn không được mâu thuẫn với nhau.
SR-900 Revision History
Version	Thay đổi
1.0.0	Khởi tạo Standards Reference Baseline.
Đánh giá

Theo tôi, từ thời điểm này bộ tài liệu quản trị của DistanceCalculatorPro đã hình thành một hệ thống hoàn chỉnh:

Nhóm	Tài liệu	Vai trò
Registry	DOC	Danh mục tài liệu
Registry	SR	Danh mục tiêu chuẩn
Architecture	ADR	Lịch sử quyết định kiến trúc
Specification	SS	Đặc tả phần mềm
Architecture	MC	Hợp đồng giữa các module
Engineering	DR	Quy tắc phát triển
Engineering	CS	Chuẩn viết mã
Planning	PB	Danh sách ý tưởng và cải tiến
Planning	SP	Kế hoạch Sprint
Execution	WP	Gói công việc triển khai