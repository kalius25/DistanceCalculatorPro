Document Index (DOC)
Document Name : Document Index

Code          : DOC

Version       : 1.0.0

Status        : FROZEN

Authoritative : YES
DOC-001 Mục đích

Document Index là mục lục chính thức của toàn bộ tài liệu dự án.

Mọi tài liệu mới phải được đăng ký tại đây trước khi được sử dụng.

DOC-100 Danh mục tài liệu
ID	Code	Document	Version	Status	Authoritative Source
DOC-101	SS	Software Specification	1.0.3	Frozen	Yes
DOC-102	ADR	Architecture Decision Record	Active	Active	Yes
DOC-103	MC	Module Contract	1.2	Frozen	Yes
DOC-104	DR	Developer Rules	1.0	Frozen	Yes
DOC-105	PB	Product Backlog	Active	Active	Yes
DOC-106	SP	Sprint Plan	Active	Active	Yes
DOC-107	WP	Work Package	Active	Active	Yes
DOC-108	DOC	Document Index	1.0	Frozen	Yes
DOC-200 Quan hệ giữa các tài liệu
                   DOC
                    │
        ┌───────────┼───────────┐
        │           │           │
       SS          ADR         DR
        │           │
        │           │
        └──────┬────┘
               │
              MC
               │
               │
         Sprint Plan (SP)
               │
               │
        Work Package (WP)
               │
               │
      Product Backlog (PB)

Giải thích:

DOC là tài liệu gốc.
SS mô tả hệ thống cần làm gì.
ADR ghi lại các quyết định kiến trúc.
DR quy định cách phát triển.
MC quy định hợp đồng giữa các module.
SP chia kế hoạch theo Sprint.
WP chia Sprint thành các Work Package.
PB ghi nhận các ý tưởng hoặc hạng mục ngoài phạm vi Sprint.
DOC-300 Quy tắc tham chiếu
DOC-301

Mọi tài liệu phải có Code Prefix riêng.

Ví dụ:

SS-023
ADR-004
MC-301
DR-002
PB-005
SP-3
WP-2.4
DOC-104
DOC-302

Mọi báo cáo kỹ thuật phải tham chiếu bằng mã định danh thay vì mô tả tự do.

Ví dụ:

Implemented:
ADR-003
MC-301
MC-303

Compliant with:
DR-001
DR-004
DOC-303

Một tài liệu chỉ có một nguồn chính thức (Single Authoritative Source).

Ví dụ:

Chủ đề	Tài liệu chính thức
Yêu cầu phần mềm	SS
Quyết định kiến trúc	ADR
Hợp đồng giữa các module	MC
Quy tắc phát triển	DR
Ý tưởng phát sinh	PB
Kế hoạch Sprint	SP
Công việc Sprint	WP
DOC-400 Quy tắc quản lý phiên bản
Loại thay đổi	Quy tắc
Sửa lỗi chính tả hoặc trình bày	Tăng Patch (1.0.0 → 1.0.1)
Bổ sung nội dung nhưng tương thích	Tăng Minor (1.0 → 1.1)
Thay đổi cấu trúc hoặc quy tắc lớn	Tăng Major (1.x → 2.0)

Quy tắc này sẽ được áp dụng thống nhất cho toàn bộ tài liệu trong dự án.

DOC-500 Trạng thái tài liệu

Để thống nhất cách quản lý, mỗi tài liệu sẽ có một trong các trạng thái sau:

Status	Ý nghĩa
Draft	Đang soạn thảo, có thể thay đổi
Review	Chờ xem xét hoặc phê duyệt
Frozen	Đã phê duyệt, chỉ thay đổi bằng quyết định chính thức
Active	Được cập nhật thường xuyên trong quá trình phát triển
Deprecated	Không còn sử dụng, chỉ lưu để tham chiếu
Archived	Đã kết thúc vòng đời, lưu trữ lịch sử
DOC-600 Quy tắc thay đổi tài liệu
DOC-601

Không sửa trực tiếp tài liệu ở trạng thái Frozen nếu chưa có quyết định chính thức.

DOC-602

Mọi thay đổi làm ảnh hưởng đến kiến trúc hoặc phạm vi phải được ghi nhận trong ADR trước khi cập nhật các tài liệu liên quan.

DOC-603

Mọi hạng mục ngoài phạm vi Sprint hiện tại phải được ghi vào PB, không được bổ sung trực tiếp vào SS hoặc MC.

Tài liệu quản trị chính thức của DistanceCalculatorPro

Đến thời điểm hiện tại, bộ tài liệu quản trị của dự án đã hoàn chỉnh:

Mã	Tài liệu	Trạng thái
DOC	Document Index	Frozen
SS	Software Specification	Frozen
ADR	Architecture Decision Record	Active
MC	Module Contract	Frozen
DR	Developer Rules	Frozen
PB	Product Backlog	Active
SP	Sprint Plan	Active
WP	Work Package	Active

Tôi coi đây là baseline quản trị (Project Governance Baseline) v1.0 của dự án. Kể từ thời điểm này, mọi Sprint, Work Package, báo cáo kỹ thuật và mã nguồn sẽ được phát triển dựa trên hệ thống tài liệu này, đảm bảo tính nhất quán và khả năng mở rộng lâu dài.