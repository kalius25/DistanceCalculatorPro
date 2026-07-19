📌 Working Agreement (Freeze)

Đây là cam kết làm việc giữa chúng ta trong suốt dự án.

1. Review trên code thật
Không suy đoán.
Không tự tạo file.
Không tự viết lại toàn bộ nếu không cần.
Chỉ review đúng file đang xét.
2. Ưu tiên ổn định

Nếu có hai phương án:

Phương án A đẹp hơn nhưng phải sửa 10 file.
Phương án B đơn giản hơn, chỉ sửa 1 file.

→ Ưu tiên phương án B nếu vẫn đúng kiến trúc.

3. Không over-engineering

Không thêm:

Factory
Strategy
Abstract Base Class
Plugin
Generic

...trừ khi dự án thực sự cần.

4. Luôn đánh giá tác động

Mỗi đề xuất sẽ được phân tích theo mẫu:

Issue

↓

Impact

↓

Recommendation

↓

Affected Modules

↓

Risk

↓

Decision

Ví dụ:

Issue

Parser đang convert đơn vị

↓

Impact

Vi phạm SRP

↓

Recommendation

Chuyển sang TextConverter

↓

Affected

Parser
Converter

↓

Risk

Thấp

↓

Decision

Approved
5. Freeze từng module

Một module Freeze nghĩa là:

Không quay lại sửa chỉ vì có ý tưởng mới.

Chỉ sửa khi:

Bug
Security
Google Maps thay đổi
Có DDD mới
6. Mọi thay đổi kiến trúc đều phải có DDD

Ví dụ sau này:

DDD-021

Support Google Maps API

DDD-022

Support HERE Maps

DDD-023

Support Async

DDD-024

Support Cache

DDD-025

Plugin Provider

Không sửa trực tiếp.

📈 Code Quality Target

Tôi đề xuất mục tiêu chất lượng cho dự án:

Tiêu chí	Mục tiêu
Compile Success	100%
Type Hint Coverage	100% (public API)
Public API Docstring	100%
Hardcode Runtime Config	0
Duplicate Business Logic	0
Circular Dependency	0
Layer Violation	0
Critical Code Smell	0

Đây là những mục tiêu cụ thể và có thể kiểm tra được.

📋 Sprint Board

Đây sẽ là bảng theo dõi tiến độ kỹ thuật:

Sprint	Module	Status
1	Config	✅ Freeze
1	URL Builder	✅ Freeze
1	Locator	✅ Freeze
2	TextConverter	⏳ Ready
2	GoogleMapsParser	⏳ Pending
3	GoogleMapsEngine	⏳ Pending
4	GoogleMapsProvider	⏳ Pending
5	RouteService	⏳ Pending
6	Controller	⏳ Pending
7	GUI	⏳ Pending
8	Integration Test	⏳ Pending
9	Release v1.0	⏳ Pending
🎯 Mục tiêu của chúng ta

Không chỉ là tạo ra một ứng dụng chạy được, mà là tạo ra một dự án có:

Kiến trúc rõ ràng.
Mã nguồn nhất quán.
Dễ bảo trì.
Dễ mở rộng.
Có tài liệu đầy đủ.
Có thể chuyển giao cho lập trình viên khác mà không phải giải thích lại toàn bộ.