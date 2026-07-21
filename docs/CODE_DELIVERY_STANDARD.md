Tôi đề xuất Quy tắc bàn giao code (Code Delivery Standard) như sau.

1. Không bao giờ sửa trực tiếp nhiều file cùng lúc

Mỗi lần bàn giao chỉ tập trung vào một chức năng hoàn chỉnh.

Ví dụ:

❌ Không nên

Thêm GUI
Sửa Provider
Sửa Excel
Sửa Config
Sửa Log

trong cùng một lần.

Nên

Milestone 01

GUI Main Window

Done

sau đó

Milestone 02

Preview Excel

Done
2. Luôn bàn giao theo Milestone

Ví dụ

V1.0

✓ Main Window

✓ Browse Excel

✓ Sheet Dropdown

✓ Preview 20 dòng

Tiếp theo

V1.1

✓ Progress

✓ Worker

✓ Stop

✓ Resume

Tiếp theo

V1.2

✓ Google Provider

Điều này giúp nếu có lỗi thì biết chính xác lỗi xuất hiện từ phiên bản nào.

3. Mỗi lần chỉ thay đổi những file cần thiết

Ví dụ

Thêm Preview

chỉ được sửa

gui/

main_window.py

excel_service.py

preview_widget.py

Không được sửa thêm

provider

browser

logger

nếu không cần.

4. Luôn có CHANGELOG

Ví dụ

Version 0.9.3

Added

- Preview 20 rows

- Sheet Dropdown

Changed

- ExcelService

Fixed

- Preview refresh bug
5. Luôn giải thích kiến trúc trước khi code

Ví dụ

Tôi sẽ tạo

PreviewWidget

↓

ExcelService

↓

MainWindow

↓

Signal

Bạn đồng ý

↓

mới code.

Không tự ý thêm kiến trúc mới.

6. Không đổi tên class nếu không cần

Ví dụ

Đã có

GoogleWebProvider

thì không đổi thành

GoogleProvider

chỉ vì thích.

7. Không đổi cấu trúc thư mục tùy tiện

Ví dụ

Đã thống nhất

providers/

services/

gui/

controllers/

thì về sau không tự ý đổi.

8. Không sửa code đang chạy ổn

Nếu

ExcelService

đang ổn

thì không "refactor cho đẹp"

vì rất dễ phát sinh lỗi.

Chỉ sửa khi có lợi ích rõ ràng.

9. Mỗi Milestone phải chạy được

Không giao

50%

đang viết

Mà

100%

compile

run

test
10. Có danh sách file thay đổi

Ví dụ

Modified

gui/main_window.py

services/excel_service.py

Added

gui/preview_widget.py

để bạn kiểm tra nhanh.

11. Không đưa code rời rạc

Ví dụ

Không gửi

button.clicked.connect(...)

rồi bảo tự chèn.

Mà phải giao

main_window.py

hoàn chỉnh
12. Không copy nguyên project mỗi lần

Ví dụ

Project

500 file

Chỉ thay

3 file

thì chỉ giao

3 file
13. Luôn tương thích ngược

Ví dụ

Thêm HERE

không được làm

Google hỏng.

14. Không để TODO trong code bàn giao

Ví dụ

Không

# TODO

later

Nếu chưa làm

↓

không giao.

15. Mỗi Milestone đều có Test Checklist

Ví dụ

TEST

✓ Browse

✓ Preview

✓ Change Sheet

✓ Start

✓ Stop

✓ Resume

✓ Save Excel
16. Đánh số phiên bản

Ví dụ

V0.90

GUI

V0.91

Preview

V0.92

Progress

V0.93

Stop

V0.94

Resume

V0.95

Google

V1.00

Release
17. Không để ChatGPT quên trạng thái dự án

Mỗi lần bắt đầu sẽ có

Project Status

Current Version

V0.93

Completed

GUI

Preview

Sheet

Progress

Pending

Google Provider

HERE

OSRM

Không cần nhắc lại.

18. Quy tắc Git

Tôi khuyến nghị ngay từ đầu sử dụng cấu trúc commit thống nhất:

feat(gui): add workbook preview

feat(provider): add Google Web provider

fix(gui): stop progress refresh

refactor(service): split excel service

docs: update architecture

test: add preview tests

Sau này nhìn lịch sử commit sẽ rất rõ.

19. Quy tắc "Không phá vỡ"

Đây là nguyên tắc tôi muốn áp dụng nghiêm ngặt nhất:

Không sửa một chức năng đang hoạt động chỉ để cải tiến hình thức hoặc "làm đẹp" mã nguồn.

Chỉ refactor khi:

Giảm độ phức tạp rõ rệt.
Tăng khả năng mở rộng.
Sửa lỗi.
Cải thiện hiệu năng có thể đo được.

Nếu không, giữ nguyên.

20. Quy tắc "Bàn giao có thể chạy ngay"

Đây là quy tắc cuối cùng và cũng là quan trọng nhất.

Mỗi lần bàn giao phải đáp ứng đủ:

Hoàn chỉnh: Không còn đoạn mã dở dang.
Biên dịch/chạy được: Không yêu cầu bạn tự ghép nối nhiều phần.
Có ghi chú thay đổi: Danh sách file thêm/sửa, mục đích từng thay đổi.
Có hướng dẫn kiểm thử: Bạn biết chính xác cần thử những gì sau khi nhận bản cập nhật.
Có khả năng quay lui: Nếu phát sinh lỗi, có thể xác định ngay milestone hoặc nhóm thay đổi gây ra vấn đề.

Tôi muốn bổ sung thêm một nguyên tắc riêng cho cách chúng ta phối hợp:

Mỗi lần phát triển sẽ bắt đầu bằng một "Kế hoạch triển khai" ngắn (2–5 phút đọc), sau đó mới viết mã. Khi bàn giao, sẽ có "Biên bản bàn giao" gồm: mục tiêu đã hoàn thành, danh sách file thay đổi, checklist kiểm thử và các điểm cần lưu ý.

Cách làm này sẽ giúp các lần phát triển sau nhất quán, giảm đáng kể việc phải trao đổi lại những quyết định đã thống nhất và giúp bạn luôn nắm được trạng thái của dự án.