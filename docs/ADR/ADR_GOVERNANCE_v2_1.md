ADR Governance v2.1 (Approved)

Từ nay ADR không còn là một tài liệu chứa nhiều quyết định.

Thay vào đó sẽ gồm hai loại tài liệu.

1. ADR Index

Đây là tài liệu duy nhất quản lý danh sách ADR.

Ví dụ

ADR	Title	Status
ADR-001	Foundation Standardization	Approved
ADR-002	Reuse Existing Modules First	Approved
ADR-003	Backward Compatibility First	Approved
ADR-004	Layered Architecture	Approved
ADR-005	Config Standardization	Approved

ADR Index chỉ có nhiệm vụ:

đánh số
liệt kê
tra cứu

Không chứa nội dung chi tiết.

2. Mỗi ADR là một tài liệu độc lập

Ví dụ:

ADR-001 — Foundation Standardization
Title

Foundation Standardization

Status

Approved

Context

Repository đã có đầy đủ kiến trúc cơ bản.

Decision

Không rewrite.

Chuẩn hóa trên nền hiện có.

Consequences

Giảm rủi ro.
Giữ nguyên API.
Sprint 1 chỉ Standardization.

Affected Documents

SS
MC
DR

Affected Sprint

SP-1

Tiếp theo

ADR-002 — Reuse Existing Modules First

là một tài liệu khác.