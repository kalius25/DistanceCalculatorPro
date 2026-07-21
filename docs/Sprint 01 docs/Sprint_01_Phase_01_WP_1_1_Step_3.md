Bắt đầu WP-1.1 – Step 3 (Implementation).

Sau khi phân tích config.py và toàn bộ package exceptions, tôi sẽ không sửa ngay source code hàng loạt, mà triển khai theo đúng DR-001 (Minimal Modification) và ADR-001 (Foundation Standardization).

Implementation Order
Phase 1 – Exception Foundation ✅ (thực hiện trước)

Đây là phần có tác động nhỏ nhất nhưng tạo nền tảng cho toàn bộ project.

Thứ tự thực hiện:

Tạo ErrorCode (Enum).
Mở rộng DistanceCalculatorError.
Giữ nguyên API cũ (DistanceCalculatorError("message") vẫn hoạt động).
Cho phép sử dụng API mới:
raise ParserException(
    "Cannot parse Google Maps page",
    error_code=ErrorCode.PARSER_ERROR,
)

Đồng thời vẫn hỗ trợ:

raise ParserException("Cannot parse Google Maps page")

=> 100% backward compatible.

Phase 2 – Version Management

Sau khi Exception ổn định sẽ chuẩn hóa Version.

Mục tiêu:

Không hardcode version ở nhiều nơi.

Ví dụ:

APP_VERSION

VERSION

__version__

chỉ còn một nguồn sinh ra (Single Source of Truth).

Phase 3 – Runtime Settings

Không tách file.

Chỉ gom nhóm rõ hơn trong config.py.

API cũ giữ nguyên.

Những gì sẽ KHÔNG thay đổi

Trong WP-1.1 tôi sẽ không sửa:

Provider
Parser
Engine
GUI
Service
Controller
BrowserManager

để bảo đảm phạm vi đúng với Work Package.

Kế hoạch chỉnh sửa cụ thể
1. app/config.py

Giữ nguyên gần như toàn bộ.

Chỉ bổ sung:

Version metadata.
Runtime Settings grouping.
Một số comment/documentation.
Không đổi tên constant hiện có.
2. app/exceptions/base_exception.py

Đây sẽ là file thay đổi nhiều nhất.

Từ:

DistanceCalculatorError(message)

thành mô hình:

DistanceCalculatorError(
    message,
    error_code=...,
    cause=...
)

nhưng vẫn tương thích với constructor cũ.

3. app/exceptions/

Các exception:

EngineException
ParserException
ProviderException

sẽ không thay đổi hành vi.

Chỉ kế thừa BaseException mới.

4. app/exceptions/init.py

Export thêm:

ErrorCode

để toàn project import thống nhất.

Chưa triển khai ngay ErrorCode vào toàn bộ project

Đây là một quyết định kỹ thuật tôi muốn giữ.

Trong WP-1.1 tôi sẽ:

✔ xây dựng ErrorCode.

Nhưng không ép toàn bộ project phải dùng ngay.

Ví dụ code cũ:

raise ParserException("Invalid HTML")

vẫn hợp lệ.

Sau này Sprint khác mới migrate dần.

Điều này phù hợp với:

ADR-003 Backward Compatibility First
DR-001 Minimal Modification
Đánh giá

Sau khi xem mã nguồn thực tế, tôi muốn điều chỉnh nhẹ so với kế hoạch Step 2:

Thay vì chỉnh đồng thời config.py và exceptions, tôi sẽ hoàn thành toàn bộ phần exceptions trước, vì đây là nền tảng cho việc chuẩn hóa ErrorCode và sẽ ít rủi ro hơn. Khi phần này ổn định, việc cập nhật config.py chỉ còn là bổ sung metadata và không ảnh hưởng đến các module khác. Đây là cách triển khai an toàn hơn nhưng vẫn hoàn toàn phù hợp với phạm vi của WP-1.1.