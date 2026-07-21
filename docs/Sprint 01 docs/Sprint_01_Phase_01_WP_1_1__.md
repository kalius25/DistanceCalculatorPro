Bắt đầu WP-1.1 – Core Foundation
Mục tiêu

Chuẩn hóa các thành phần nền tảng của hệ thống mà không thay đổi chức năng hiện có.

Phạm vi
Chuẩn hóa
Version
ErrorCode
Constants
Settings
Config
Không thay đổi
GUI
Provider Logic
Playwright
Excel
Parser
Business Workflow
Nguyên tắc của WP-1.1

Sau khi phân tích repository, tôi không muốn tạo file mới nếu project đã có thành phần tương đương.

Điều này rất quan trọng.

Ví dụ:

Nếu project đã có:

app/enums/

thì tôi sẽ ưu tiên mở rộng hoặc chuẩn hóa trong đó thay vì tạo thêm:

app/core/

làm phát sinh hai nơi chứa hằng số.

Tương tự:

Nếu đã có config.py thì không tạo settings.py chỉ vì tên khác.
Nếu đã có route_result.py thì sẽ đánh giá có thể mở rộng hay không trước khi tạo distance_result.py.

Đây chính là tinh thần của Foundation Standardization: chuẩn hóa trên nền hiện có, không tạo thêm cấu trúc song song.

Execution Plan của WP-1.1

Tôi sẽ thực hiện theo đúng thứ tự:

Bước 1

Phân tích các file hiện có liên quan đến:

Version
Config
Constants
ErrorCode
Settings

Mục tiêu: Xác định file nào giữ nguyên, file nào cần sửa, file nào cần bổ sung.

Bước 2

Lập Impact Report của WP-1.1:

Danh sách file sẽ sửa.
Danh sách file mới (nếu thực sự cần).
Lý do của từng thay đổi.
Ảnh hưởng đến module khác.
Bước 3

Bắt đầu bàn giao mã nguồn.

Tôi quyết định thay đổi một điểm quan trọng

Sau khi đã có mã nguồn thực tế, tôi không muốn dự đoán tên file nữa như ở giai đoạn thiết kế.

Thay vào đó:

Mọi file trong WP-1.1 sẽ dùng đúng tên file đang tồn tại trong repository.
Chỉ tạo file mới khi sau bước phân tích xác nhận rằng repository chưa có vị trí phù hợp.

Điều này sẽ tránh việc sau này phải đổi tên hoặc xóa file vì trùng chức năng.

Vì vậy, phản hồi tiếp theo sẽ là:

WP-1.1 – Step 1: Core Foundation Impact Report

Trong báo cáo đó, tôi sẽ liệt kê chính xác các file hiện có trong project liên quan đến Core Foundation, đánh giá từng file và quyết định file nào sẽ được sửa trong Sprint 1 trước khi bàn giao bất kỳ dòng mã nào. Đây sẽ là điểm khởi đầu an toàn nhất để đảm bảo Sprint 1 chỉ tác động đúng phạm vi đã khóa.