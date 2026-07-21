ADR Index
Document Name : ADR Index

Code          : ADR-INDEX

Version       : 2.0.0

Status        : ACTIVE

Authoritative : YES
ADR-000 Document Information
Purpose

ADR Index là danh mục chính thức của toàn bộ Architecture Decision Record trong dự án.

ADR Index chỉ có nhiệm vụ:

Quản lý số thứ tự ADR.
Quản lý trạng thái ADR.
Theo dõi ADR thay thế (Supersedes).
Tra cứu nhanh.
Không chứa nội dung chi tiết của từng ADR.
References
DOC
SS
MC
DR
CS

ADR Register
ADR	Title	Status	Supersedes
ADR-001	Foundation Standardization	Approved	None
ADR-002	Reuse Existing Modules First	Approved	None
ADR-003	Backward Compatibility First	Approved	None
ADR-004	Layered Architecture	Approved	None
ADR-005	Config Standardization	Approved	None
ADR-006	Runtime Settings Separation	Approved	None
ADR-007	ErrorCode Standard	Approved	None
ADR-008	Config Single Source of Truth	Approved	None
ADR-009	Documentation First	Approved	None
ADR-010	Minimal Modification	Approved	None
ADR-011	Product Backlog First	Approved	None
ADR-012	One Main Objective Per Work Package	Approved	None
ADR-013	Preserve Existing Style	Approved	None
ADR-014	Sprint Workflow Standardization	Approved	None
ADR-015	Complete File Delivery Strategy	Approved	None
ADR-016	Request Only Needed Files	Approved	None
ADR-017	Product Backlog Policy	Approved	None
ADR-018	Unified Document Prefix	Approved	None
ADR-019	Cross Reference Standard	Approved	None
ADR-020	Baseline Document Policy	Approved	None
ADR-021	Independent ADR Document	Approved	None
ADR-022	ADR Supersedes Mechanism	Approved	None
ADR-023	ADR Update Workflow	Approved	None
ADR-024	Decision Immutability	Approved	None
ADR-025	Standards Reference Registry	Approved	None
ADR-026	ADR Scope Definition	Approved	None

ADR Status Definition
Status	Ý nghĩa
Proposed	Đề xuất, chưa được phê duyệt.
Approved	Đã được phê duyệt và có hiệu lực.
Superseded	Đã bị thay thế bởi ADR mới.
Deprecated	Không còn khuyến nghị áp dụng nhưng vẫn giữ để tham chiếu.
Rejected	Đã xem xét nhưng không được chấp nhận.
ADR Numbering Rules
Mỗi ADR có một số duy nhất.
Số ADR không được tái sử dụng.
ADR đã xóa vẫn giữ số để đảm bảo khả năng truy vết.
Không được chèn lại số cũ.

Ví dụ:

ADR-001
ADR-002
ADR-003
...
ADR-024
ADR Lifecycle
Proposed
    │
    ▼
Discussion
    │
    ▼
Approved
    │
    ├──────────────► Superseded
    │
    └──────────────► Deprecated
ADR Update Rules

Khi một quyết định kiến trúc mới được phê duyệt:

Cấp số ADR mới.
Thêm vào ADR Register.
Tạo tài liệu ADR độc lập.
Nếu thay thế ADR cũ:
ADR mới ghi rõ trường Supersedes.
ADR cũ đổi trạng thái thành Superseded.
Đồng bộ các tài liệu liên quan (SS, MC, DR, CS...) nếu quyết định mới làm thay đổi kiến trúc hoặc quy định.
Revision History
Version	Thay đổi
1.0.0	Khởi tạo ADR Index.
2.0.0	Chuẩn hóa ADR Index, bổ sung Register, Status, Numbering Rules, Lifecycle, trường Supersedes và quy trình cập nhật ADR.