Governance Standard

GS-001 — Architecture Evolution Logging
Standard ID

GS-001

Title

Architecture Evolution Logging

Status

Approved

Category

Governance Standard

Purpose

Đảm bảo mọi thay đổi kiến trúc đã triển khai đều được ghi nhận nhất quán, có khả năng truy vết và kiểm toán.

Rule 1 — One Completed Work Package, One AEL Entry

Mỗi Work Package (WP) hoặc Execution Package (EX) hoàn thành phải tạo đúng một AEL Entry.

Ví dụ:

Work Package	AEL
EX-005.1B	AEL-001
EX-005.2	AEL-002
EX-006	AEL-003
Rule 2 — AEL chỉ ghi nhận thay đổi đã hoàn thành

AEL không ghi:

kế hoạch,
ý tưởng,
backlog,
ADR đang thảo luận.

AEL chỉ ghi:

đã triển khai,
đã review,
đã xác nhận.
Rule 3 — Mỗi AEL phải liên kết tới tài liệu liên quan

Ít nhất phải tham chiếu:

Work Package
Product Backlog

Khuyến nghị thêm:

ADR
Coding Standards
Test Report
Version
Rule 4 — Mỗi AEL phải có bằng chứng hoàn thành

Ví dụ:

Unit Test PASS
Integration Test PASS
Manual Verification PASS
Code Review PASS

Không có bằng chứng thì không được đánh dấu Completed.

Rule 5 — AEL không thay thế Git History

Git ghi:

commit,
diff,
author.

AEL ghi:

mục tiêu,
tác động kiến trúc,
kết quả,
trạng thái.

Hai tài liệu bổ sung cho nhau.

Rule 6 — AEL phải theo trình tự thời gian

AEL ID tăng dần:

AEL-001

AEL-002

AEL-003

Không sửa nội dung lịch sử, chỉ được:

bổ sung ghi chú,
đính chính bằng AEL mới nếu cần.
Rule 7 — Mỗi Product Backlog hoàn thành phải có ít nhất một AEL

Ví dụ:

PB-001

↓

AEL-001

Điều này tạo liên kết hai chiều:

Backlog → Implementation → Verification

Governance Lifecycle

Sau khi bổ sung GS-001, tôi đề xuất coi đây là vòng đời chuẩn cho mọi thay đổi của dự án:

Issue / Requirement
        │
        ▼
Product Backlog (PB)
        │
        ▼
Architecture Decision Record (ADR)
        │
        ▼
Coding Standards (CS)
        │
        ▼
Implementation (WP / EX)
        │
        ▼
Testing
        │
        ▼
Architecture Evolution Log (AEL)
        │
        ▼
Release
Bộ Governance hiện tại

Đến thời điểm này, hệ thống quản trị của DistanceCalculatorPro gồm:

Nhóm	Mục đích	Trạng thái
ADR	Quyết định kiến trúc	✅ Hoàn chỉnh
CS	Quy tắc lập trình	✅ Hoàn chỉnh
PB	Quản lý backlog	✅ Hoạt động
AEL	Nhật ký triển khai	✅ Hoạt động
GS	Quy tắc quản trị	✅ Khởi tạo (GS-001)


GS-002 — Document Versioning & Editorial Policy
Standard ID

GS-002

Title

Document Versioning & Editorial Policy

Status

Approved

Category

Governance Standard

Purpose

Thiết lập quy tắc thống nhất để quản lý:

Phiên bản tài liệu.
Chỉnh sửa nội dung.
Lịch sử thay đổi.
Khả năng truy vết.
Tính bất biến (immutability) của tài liệu đã được phê duyệt.

GS-002 áp dụng cho toàn bộ tài liệu Governance của dự án.

Scope

Áp dụng cho:

ADR
CS
GS
PB
AEL

Có thể mở rộng cho:

Architecture Guide
Design Specification
API Specification
Rule GS-002.1 — Every Document Has a Version

Mọi tài liệu Governance phải có trường:

Version

Ví dụ:

Version: 1.0.0
Rule GS-002.2 — Semantic Versioning

Phiên bản tài liệu sử dụng quy ước:

MAJOR.MINOR.PATCH
PATCH

Ví dụ:

1.0.0

↓

1.0.1

Áp dụng khi:

sửa lỗi chính tả;
sửa định dạng;
cải thiện cách diễn đạt;
không thay đổi ý nghĩa.
MINOR

Ví dụ:

1.0.0

↓

1.1.0

Áp dụng khi:

bổ sung ví dụ;
bổ sung ghi chú;
bổ sung giải thích;
không thay đổi quyết định cốt lõi.
MAJOR

Ví dụ:

1.0.0

↓

2.0.0

Áp dụng khi:

thay đổi quyết định;
thay đổi quy tắc;
thay đổi kiến trúc;
thay đổi phạm vi áp dụng.
Rule GS-002.3 — Editorial History

Mỗi tài liệu phải có phần:

Editorial History

Ví dụ:

Version	Date	Description
1.0.0	2026-07-22	Initial Version
1.0.1	2026-07-25	Fixed grammar
1.1.0	2026-08-01	Added examples
Rule GS-002.4 — Approved Documents Are Immutable

Sau khi tài liệu được phê duyệt:

Không được:

sửa trực tiếp nội dung quyết định;
thay đổi lịch sử;
xóa nội dung đã phê duyệt.

Nếu cần thay đổi quyết định:

tạo phiên bản MAJOR mới, hoặc
tạo tài liệu mới (ADR mới, CS mới, GS mới...), tùy theo loại thay đổi.
Rule GS-002.5 — Editorial Changes Must Preserve Intent

Các thay đổi Editorial chỉ được:

sửa lỗi;
cải thiện khả năng đọc;
chuẩn hóa thuật ngữ;
bổ sung ví dụ.

Không được làm thay đổi ý nghĩa.

Rule GS-002.6 — Superseded Documents

Nếu một tài liệu bị thay thế, phải ghi rõ:

Superseded By

Ví dụ:

ADR-018

Superseded By

ADR-027

Tài liệu cũ vẫn được lưu để phục vụ truy vết.

Rule GS-002.7 — Document Relationships

Tài liệu phải tham chiếu hai chiều khi có liên quan.

Ví dụ:

PB-001
        │
        ▼
ADR-030
        │
        ▼
CS-817
        │
        ▼
AEL-001

Mỗi tài liệu cần có mục:

Related ADR
Related CS
Related PB
Related AEL
Related GS (nếu có)
Rule GS-002.8 — Stable Document Identifier

Mã định danh tài liệu là bất biến.

Ví dụ:

ADR-030

Không đổi thành:

ADR-031

chỉ vì cập nhật nội dung.

Phiên bản thay đổi, ID giữ nguyên.

Rule GS-002.9 — Archive Policy

Tài liệu không còn hiệu lực:

không được xóa;
chuyển sang trạng thái:
Deprecated

hoặc

Superseded

để bảo toàn lịch sử.

Rule GS-002.10 — Governance Review

Mọi tài liệu Governance mới phải trải qua quy trình:

Draft

↓

Review

↓

Approved

↓

Implemented (nếu áp dụng)

↓

Archived / Superseded (nếu có)
Governance Document Lifecycle
Idea
 │
 ▼
Draft
 │
 ▼
Review
 │
 ▼
Approved
 │
 ▼
Version Control
 │
 ▼
Implementation
 │
 ▼
Architecture Evolution Log
 │
 ▼
Maintenance
 │
 ▼
Superseded / Deprecated
 │
 ▼
Archive
Editorial History
Version	Date	Description
1.0.0	2026-07-22	Initial Version
Related Standards
GS-001 — Architecture Evolution Logging
ADR-024 — Decision Immutability
ADR-030 — Canonical Domain Models
CS-817 — Public Property Coverage
Đánh giá

Đến thời điểm hiện tại, bộ Governance của DistanceCalculatorPro đã có cấu trúc khá hoàn chỉnh:

Layer	Mục đích	Trạng thái
GS	Quản trị quy trình và tài liệu	✅ Khởi tạo
ADR	Quản lý quyết định kiến trúc	✅ Hoàn chỉnh
CS	Chuẩn hóa quy tắc lập trình	✅ Hoạt động
PB	Quản lý công việc và ưu tiên	✅ Hoạt động
AEL	Ghi nhận triển khai thực tế	✅ Hoạt động

GS-002.11 — Separation of Responsibilities
Rule

Mỗi loại tài liệu Governance phải có một trách nhiệm duy nhất (Single Responsibility).

Không được đưa nội dung thuộc phạm vi của tài liệu khác vào.

Responsibility Matrix
Document	Responsibility
Governance Standard (GS)	Quy trình quản trị, vòng đời tài liệu, quy trình review, versioning, traceability, audit, release governance
Architecture Decision Record (ADR)	Quyết định kiến trúc, rationale, trade-off, tác động kiến trúc
Coding Standard (CS)	Quy tắc lập trình, coding convention, testing convention, packaging, exception handling, naming, logging
Product Backlog (PB)	Danh sách công việc, ưu tiên, trạng thái, kế hoạch triển khai
Architecture Evolution Log (AEL)	Nhật ký các thay đổi đã triển khai và được xác nhận
Governance Boundary
Governance Standard (GS)

Chỉ quản lý:

quy trình
workflow
review
approval
versioning
traceability
documentation lifecycle

Ví dụ:

GS-001 Architecture Evolution Logging
GS-002 Document Versioning & Editorial Policy
Architecture Decision Record (ADR)

Chỉ quản lý:

quyết định kiến trúc

Ví dụ:

Canonical Domain Models
Exception Hierarchy
Default ErrorCode
Dependency Injection Strategy
Coding Standard (CS)

Chỉ quản lý:

coding rule
unit test
packaging
exception
logging
naming
formatter
import rule

Ví dụ:

CS-812 Exception Package Export
CS-813 Exception Chaining
CS-817 Public Property Coverage
Product Backlog (PB)

Chỉ quản lý:

feature
technical debt
refactor
enhancement
roadmap
Architecture Evolution Log (AEL)

Chỉ quản lý:

implementation history
deployment milestone
verification result
Benefits

Việc phân tách này mang lại nhiều lợi ích:

Không chồng chéo trách nhiệm giữa các tài liệu.
Dễ tìm kiếm thông tin: biết cần xem loại tài liệu nào cho từng câu hỏi.
Giảm trùng lặp nội dung.
Dễ mở rộng khi số lượng ADR, CS, PB và AEL tăng lên.
Đơn giản hóa review vì mỗi tài liệu chỉ được đánh giá theo một mục tiêu.
Governance Architecture

Tôi đề xuất coi đây là kiến trúc quản trị chính thức của dự án:

                           Governance
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
   Governance              Architecture          Engineering
    Standards               Decisions             Standards
       (GS)                   (ADR)                  (CS)
         │                      │                      │
         └──────────────┬───────┴──────────────┬───────┘
                        ▼                      ▼
              Product Backlog (PB)     Architecture Evolution Log (AEL)

Trong mô hình này:

GS điều phối cách dự án được quản trị.
ADR quyết định kiến trúc sẽ được xây dựng như thế nào.
CS quy định cách hiện thực hóa kiến trúc bằng mã nguồn.
PB quản lý những việc cần làm.
AEL ghi nhận những gì đã thực sự hoàn thành.