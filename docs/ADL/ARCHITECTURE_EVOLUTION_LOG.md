Architecture Evolution Log (AEL)
Document Information
Field	Value
Document ID	AEL
Title	Architecture Evolution Log
Status	Active
Version	1.0.0
Maintainer	Project Architecture Team
Scope	DistanceCalculatorPro
Purpose

AEL ghi lại những thay đổi kiến trúc đã được triển khai thành công trong mã nguồn.

Khác với:

ADR trả lời câu hỏi: Chúng ta quyết định điều gì?
CS trả lời câu hỏi: Chúng ta lập trình theo quy tắc nào?
PB trả lời câu hỏi: Chúng ta cần làm gì?
AEL trả lời câu hỏi: Điều gì đã thực sự được triển khai?

AEL là nhật ký triển khai (implementation history), không phải nhật ký commit Git.

Entry Format
Field	Description
AEL ID	Mã định danh
Date	Ngày hoàn thành
Version	Phiên bản dự án
Work Package	Gói công việc
Related PB	Product Backlog
Related ADR	Kiến trúc áp dụng
Summary	Tóm tắt thay đổi
Result	Kết quả
Notes	Ghi chú


AEL Index
AEL ID	Date	Work Package	Status
AEL-001	2026-07-22	EX-005.1B	✅ Completed
Quy tắc cập nhật AEL

Tôi đề xuất từ nay áp dụng quy tắc sau:

Mỗi Work Package hoàn thành → tạo một AEL Entry.
AEL chỉ ghi nhận thay đổi đã được triển khai và xác nhận, không ghi các kế hoạch.
Một AEL có thể tham chiếu nhiều ADR, CS và PB.
Mỗi AEL phải có bằng chứng hoàn thành (ví dụ: test PASS, review PASS hoặc kiểm tra tích hợp).
Kiến trúc tài liệu sau khi bổ sung AEL
Architecture/
│
├── ADR/
│
├── Coding Standards/
│
├── Product Backlog/
│
├── Architecture Evolution Log/
│
└── Governance/

Đến thời điểm này, bộ tài liệu của DistanceCalculatorPro đã hình thành một chu trình quản trị hoàn chỉnh:

ADR: quản lý quyết định kiến trúc.
Coding Standards (CS): quản lý quy tắc phát triển.
Product Backlog (PB): quản lý nhu cầu và hạng mục công việc.
Architecture Evolution Log (AEL): quản lý lịch sử triển khai thực tế.

Bốn tài liệu này bổ sung cho nhau và tạo thành một hệ thống có khả năng theo dõi từ quyết định → kế hoạch → triển khai → xác nhận kết quả, rất phù hợp để duy trì và mở rộng dự án trong dài hạn.


