📜 DistanceCalculatorPro Project Constitution v1.0
Principle 1 – Architecture First

Kiến trúc luôn được quyết định trước khi code.

Principle 2 – Freeze Before Expand

Một module phải được Freeze trước khi phát triển module tiếp theo.

Principle 3 – Backward Compatibility

Không phá API đang sử dụng nếu chưa có kế hoạch migration rõ ràng.

Principle 4 – Single Source of Truth

Mỗi loại dữ liệu chỉ có một nơi chịu trách nhiệm.

Ví dụ:

Thành phần	Chủ sở hữu
URL	GoogleMapsUrlBuilder
Selector	GoogleMapsLocator
Runtime Config	config.py
Unit Conversion	TextConverter
Route Parsing	GoogleMapsParser
Browser Automation	GoogleMapsEngine
Principle 5 – Separation of Responsibility

Mỗi tầng chỉ làm đúng việc của mình.

Ví dụ:

GUI không parse.
Parser không convert.
Converter không log.
Engine không xử lý business.
Provider không biết giao diện GUI.
Principle 6 – Canonical Data

Dữ liệu nội bộ luôn lưu theo định dạng chuẩn.

Ví dụ:

Distance → km
Duration → phút

Hiển thị theo đơn vị nào là việc của Formatter/UI.

Principle 7 – Review Before Refactor

Trước khi sửa code phải xác định:

Đây là Bug?
Đây là Design Issue?
Đây là Code Smell?
Đây là Future Improvement?

Không refactor chỉ vì "có thể đẹp hơn".

Principle 8 – Simplicity Wins

Nếu có hai giải pháp đúng:

ưu tiên giải pháp đơn giản hơn;
chỉ tăng độ phức tạp khi lợi ích đủ lớn.
Principle 9 – Measurable Quality

Một module chỉ được Freeze khi đạt checklist đã thống nhất:

Compile OK
Logic OK
Architecture OK
Coding Standard OK
Design Decision OK
Type Hint OK
Docstring OK
Unit Test (nếu phù hợp)
Principle 10 – Design Decisions Are Stable

Các DDD đã Freeze được xem là nền tảng.

Nếu muốn thay đổi:

Nêu vấn đề.
Phân tích lợi ích và tác động.
Tạo DDD mới hoặc cập nhật DDD hiện có.
Sau khi thống nhất mới sửa code.

Không thay đổi kiến trúc trong lúc đang review một module.

Cam kết của tôi trong dự án này

Từ bây giờ tôi sẽ làm việc theo vai trò Technical Architect + Senior Code Reviewer, không chỉ là người trả lời câu hỏi.

Điều đó có nghĩa là:

Tôi sẽ luôn kiểm tra sự phù hợp với CS và DDD trước khi đề xuất thay đổi.
Tôi sẽ phân biệt rõ:
Critical (phải sửa),
Recommended (nên sửa),
Optional (có thể sửa),
Future (để phiên bản sau).
Tôi sẽ ưu tiên sự ổn định của dự án hơn là theo đuổi những kỹ thuật mới nếu chúng không mang lại giá trị rõ ràng.
Khi có đề xuất kiến trúc mới, tôi sẽ trình bày như một Design Decision để bạn quyết định, thay vì tự coi đó là hướng đi mặc định.

Theo tôi, với bộ Coding Standard + Design Decisions + Project Constitution, chúng ta đã có một nền tảng rất vững. Từ Sprint tiếp theo trở đi, trọng tâm sẽ là thực thi nhất quán các nguyên tắc đã thống nhất, giúp dự án phát triển ổn định và dễ bảo trì trong dài hạn.