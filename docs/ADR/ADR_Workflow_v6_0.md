ADR Workflow v6.0.0
1. Mục đích

Architecture Decision Record (ADR) là tài liệu ghi nhận các quyết định kiến trúc đã được phê duyệt trong suốt vòng đời của dự án.

Mục tiêu:

Lưu giữ lịch sử quyết định.
Giải thích lý do của từng quyết định.
Hỗ trợ bảo trì và mở rộng.
Tránh lặp lại các cuộc thảo luận đã kết thúc.
Tạo cơ sở thống nhất cho mọi thành viên khi phát triển hệ thống.
2. Phạm vi

ADR chỉ ghi nhận các quyết định có ảnh hưởng lâu dài đến kiến trúc, bao gồm:

Kiến trúc hệ thống.
Thiết kế tổng thể.
Cấu trúc module.
Quy tắc phụ thuộc giữa các Layer.
Chuẩn hóa mô hình dữ liệu dùng chung.
Chiến lược mở rộng hệ thống.
Nguyên tắc thiết kế có ảnh hưởng lâu dài.

ADR không dùng cho:

Coding Style.
Developer Rules.
Sprint Planning.
Work Package.
Task hằng ngày.
Bug Fix.
Refactoring nhỏ.
Quy trình triển khai.
3. One Decision Per ADR

Một ADR chỉ ghi nhận một quyết định kiến trúc duy nhất.

Không gộp nhiều quyết định độc lập vào cùng một ADR.

4. Decision Immutability

Sau khi ADR được phê duyệt:

Không chỉnh sửa nội dung quyết định.
Không ghi đè ADR cũ.
Không thay đổi lịch sử quyết định.
ADR đã phát hành được xem là tài liệu lịch sử.
5. Khi nào tạo ADR mới

Tạo ADR mới khi:

Có quyết định kiến trúc mới.
Mở rộng một quyết định kiến trúc đã có.
Thay đổi hướng thiết kế.
Bổ sung nguyên tắc kiến trúc mới.
Thay thế một quyết định kiến trúc trước đó.

Không tạo ADR mới cho:

Chỉnh sửa câu chữ.
Sửa lỗi chính tả.
Cập nhật định dạng.
Bổ sung ví dụ.
Cập nhật tham chiếu.
6. Supersedes

Nếu một ADR thay thế hoàn toàn ADR khác:

Supersedes : ADR-015

ADR cũ:

Không bị xóa.
Không bị sửa.
Chuyển trạng thái thành Superseded.
7. Editorial Revision

Editorial Revision chỉ áp dụng cho các thay đổi mang tính biên tập.

Được phép:

Sửa lỗi chính tả.
Chuẩn hóa định dạng.
Cải thiện cách diễn đạt.
Bổ sung ví dụ minh họa.
Cập nhật liên kết tham chiếu.

Không được:

Thay đổi Decision.
Thêm Decision mới.
Mở rộng phạm vi Decision.
Thay đổi Consequences.
Thay đổi phạm vi áp dụng của ADR.

Nếu thay đổi làm ảnh hưởng đến Decision, Context, Consequences hoặc phạm vi kiến trúc thì phải tạo ADR mới.

8. Cấu trúc chuẩn của ADR

Mỗi ADR gồm các phần sau:

ADR ID

Title

Status

Approved By

Approval Date

Editorial Revision

Context

Decision

Alternatives Considered

Consequences

Affected Documents

First Applied In

Related ADR

Supersedes

Editorial History
Ý nghĩa các trường
Trường	Ý nghĩa
Approved By	Cá nhân hoặc hội đồng phê duyệt ADR
Approval Date	Ngày quyết định kiến trúc được phê duyệt; không thay đổi khi có Editorial Revision
Editorial Revision	Phiên bản biên tập của tài liệu
Editorial History	Lịch sử chỉnh sửa biên tập, không phải lịch sử quyết định
First Applied In	Sprint hoặc phiên bản đầu tiên áp dụng quyết định
9. Quy trình ban hành ADR
Đề xuất
      │
      ▼
Thảo luận
      │
      ▼
Đạt đồng thuận
      │
      ▼
Cấp ADR ID
      │
      ▼
Phê duyệt
      │
      ▼
Ghi nhận:
- Approved By
- Approval Date
      │
      ▼
Tạo ADR
      │
      ▼
Cập nhật ADR Index
      │
      ▼
ADR có hiệu lực
10. ADR Index

Mỗi ADR mới phải:

Được cấp số ADR tiếp theo.
Được cập nhật vào ADR Index.
Không được bỏ số.
Không được tái sử dụng số ADR.
Giữ nguyên thứ tự theo thời gian ban hành.
11. Trạng thái ADR
Status	Ý nghĩa
Proposed	Đang đề xuất
Approved	Đã được phê duyệt và có hiệu lực
Superseded	Được thay thế bởi ADR khác
Deprecated	Không còn áp dụng nhưng giữ để tham khảo
12. Cross Reference

ADR được phép tham chiếu tới:

SS
MC
CS
DR
PB
SP
WP
ADR khác

ADR không sao chép nội dung của các tài liệu trên mà chỉ tham chiếu khi cần.

13. Governance Principles

Hệ thống ADR tuân thủ các nguyên tắc:

One Decision Per ADR.
Decision Immutability.
Architecture Only.
History Preservation.
Cross Reference First.
Single Source of Truth.
Incremental Evolution.
Traceability.
Accountability.
14. Decision, Not Implementation

ADR mô tả:

Chúng ta quyết định điều gì.
Vì sao đưa ra quyết định đó.
Quyết định đó ảnh hưởng như thế nào.

ADR không mô tả:

Thuật toán.
Mã nguồn.
Thiết kế lớp chi tiết.
Các bước triển khai.
Kế hoạch thực hiện.

Việc triển khai thuộc các tài liệu khác:

Nội dung	Tài liệu
Quyết định kiến trúc	ADR
Yêu cầu hệ thống	SS
Trách nhiệm module	MC
Quy tắc lập trình	CS
Quy tắc phát triển	DR
Kế hoạch Sprint	SP
Công việc triển khai	WP
15. Tiêu chí của một ADR tốt

Một ADR được xem là hoàn chỉnh khi:

Chỉ chứa một quyết định kiến trúc.
Có Context rõ ràng.
Có Decision rõ ràng.
Có Alternatives Considered (khi cần).
Có Consequences.
Có khả năng truy vết.
Không chứa chi tiết triển khai.
Có thể đọc độc lập mà không cần xem mã nguồn.
16. Lifecycle của ADR
Proposed
    │
    ▼
Discussion
    │
    ▼
Approved
    │
    ├──────────────┐
    │              │
    ▼              ▼
Superseded    Deprecated

Nguyên tắc:

Approved là trạng thái mặc định sau khi được thông qua.
Superseded khi có ADR khác thay thế quyết định.
Deprecated khi quyết định không còn áp dụng nhưng không có ADR thay thế trực tiếp.
ADR không bao giờ bị xóa khỏi lịch sử dự án.