Sprint 1 – WP-1.1
Step 1 – Core Foundation Impact Report

Status

ANALYSIS COMPLETED

Lần này tôi không dựa vào thiết kế nữa mà dựa trên repository thực tế.

1. Kết quả rà soát Core Foundation

Qua kiểm tra project, các thành phần liên quan trực tiếp đến WP-1.1 hiện có là:

File	Vai trò	Đánh giá
app/config.py	Cấu hình toàn cục	🟡 Cần chuẩn hóa
app/enums/provider_type.py	Enum Provider	🟢 Giữ
app/enums/travel_mode.py	Enum Travel	🟢 Giữ
app/enums/route_preference.py	Enum Route	🟢 Giữ
app/exceptions/base_exception.py	Base Exception	🟢 Giữ
app/exceptions/engine_exception.py	Engine Exception	🟢 Giữ
app/exceptions/parser_exception.py	Parser Exception	🟢 Giữ
app/exceptions/provider_exception.py	Provider Exception	🟢 Giữ
2. Phát hiện quan trọng

Điều này khác với giả định ban đầu của chúng ta.

Project đã có
Config
Enum
Exception

Tức là Foundation đã tồn tại.

Điều chưa có là:

Version Management
ErrorCode chuẩn hóa
Settings Manager
Constants Policy
Configuration Layer hoàn chỉnh

Nói cách khác:

Chúng ta không xây Foundation, mà chuẩn hóa Foundation.

3. Phân tích app/config.py

Đây là file quan trọng nhất của WP-1.1.

Tôi đã đọc nội dung và có các nhận xét:

Điểm mạnh
Có phân chia theo nhóm (Browser, Logging, Parser...).
Dùng pathlib.Path.
Có StrEnum cho AppMode.
Có tạo thư mục logs tự động.
Có chú thích rõ ràng.

Đây là nền tảng tốt.

Những điểm cần chuẩn hóa
(1) Config đang là hằng số toàn cục

Ví dụ:

HEADLESS
MAX_RETRY
LOG_LEVEL

được khai báo trực tiếp.

Điều này phù hợp ở giai đoạn đầu, nhưng chưa phù hợp với mục tiêu của chúng ta là Settings có thể lưu/đọc từ JSON.

Đề xuất:

Giữ nguyên API hiện tại để đảm bảo tương thích ngược.
Bổ sung một lớp quản lý Settings trong Sprint sau, thay vì thay đổi ngay config.py.

=> Sprint 1 không phá API.

(2) Chưa có Version

Hiện chưa thấy:

APP_VERSION
BUILD_NUMBER

Đây là hạng mục nên bổ sung.

(3) Chưa có ErrorCode chuẩn hóa

Hiện Exception đã được phân tầng, nhưng chưa có tập mã lỗi thống nhất như chúng ta đã thiết kế:

OK
SKIPPED
TIMEOUT
INVALID_COORDINATE
NO_ROUTE
UNKNOWN

Tôi đề xuất bổ sung ErrorCode độc lập thay vì nhúng vào Exception.

(4) Config và Runtime Settings

Hiện config.py đang chứa cả:

cấu hình hệ thống (ví dụ GOOGLE_MAPS_URL)
cấu hình người dùng (ví dụ HEADLESS, LOG_LEVEL)

Theo kiến trúc đã chốt, hai loại này nên được tách về mặt khái niệm:

System Configuration (ít thay đổi)
Runtime/User Settings (thay đổi được)

Tôi không tách file trong Sprint 1, nhưng sẽ phản ánh rõ trong tài liệu và chuẩn bị nền cho Sprint Settings.

4. Danh sách thay đổi của WP-1.1
Sẽ sửa
File	Mức độ
app/config.py	🟡 Nhẹ
Sẽ bổ sung
Thành phần	Lý do
Version	Quản lý phiên bản
ErrorCode	Chuẩn hóa trạng thái hệ thống

Lưu ý: Trước khi tạo file mới, tôi sẽ kiểm tra kỹ toàn bộ repository để tránh trùng với module đã tồn tại.

Giữ nguyên
Provider Enum
Travel Enum
Route Preference
Exception Hierarchy

Không có lý do kỹ thuật để sửa các file này trong Sprint 1.

5. Backward Compatibility Assessment
Hạng mục	Trạng thái
Public API	✅ Giữ nguyên
Provider	✅ Không ảnh hưởng
Engine	✅ Không ảnh hưởng
Parser	✅ Không ảnh hưởng
GUI	✅ Không ảnh hưởng
Tests	✅ Không ảnh hưởng

Đây là đúng tinh thần của Developer Rule 004.

6. Quyết định kỹ thuật

Sau khi đọc config.py, tôi đưa ra một quyết định mà tôi tin sẽ giúp dự án ổn định lâu dài:

Sprint 1 sẽ ưu tiên "chuẩn hóa trên nền hiện có", không áp đặt cấu trúc mới nếu repository đã có giải pháp hợp lý.

Điều này có nghĩa là:

Không tạo core/ chỉ để chứa constants.
Không tạo settings.py nếu sau này có thể mở rộng từ config.py.
Không tạo error.py nếu đã có hệ thống exceptions phù hợp.

Chúng ta sẽ tận dụng tối đa kiến trúc hiện có, chỉ bổ sung những thành phần còn thiếu thật sự (như Version và ErrorCode) sau khi xác nhận không có module tương đương trong repository.

Đây sẽ là nguyên tắc xuyên suốt cho các Sprint tiếp theo và giúp DistanceCalculatorPro phát triển ổn định mà không làm tăng độ phức tạp kiến trúc.