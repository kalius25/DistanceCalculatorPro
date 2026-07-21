1. Quy tắc về Coding Style ⭐⭐⭐⭐⭐

Đây là thứ quyết định sau này code có dễ đọc hay không.

Ví dụ thống nhất:

Class
GoogleWebProvider
ExcelPreviewWidget
BatchCalculationService

PascalCase.

Function
load_excel()

calculate_distance()

save_workbook()

snake_case.

Variable
sheet_name

total_rows

processed_rows

Không dùng

a

b

temp1

abc
Constant
DEFAULT_TIMEOUT

DEFAULT_DELAY

MAX_RETRY

UPPER_CASE.

2. Quy tắc đặt tên File ⭐⭐⭐⭐⭐

Ví dụ

google_web_provider.py

excel_service.py

progress_widget.py

settings_dialog.py

Không dùng

Google.py

Excel2.py

GUI_Final.py
3. Quy tắc Comment ⭐⭐⭐⭐☆

Tôi đề nghị:

Không comment giải thích từng dòng.

Chỉ comment

Business Rule
Thuật toán
Vì sao làm như vậy

Ví dụ

# Skip rows that already have a calculated distance.

Không

# tăng i lên 1

i += 1
4. Quy tắc Exception ⭐⭐⭐⭐⭐

Tuyệt đối

Không

except:
    pass

Mà

except TimeoutError:

...

except ExcelError:

...

except GoogleError:

...

Mỗi lỗi đều ghi Log.

5. Quy tắc Logging ⭐⭐⭐⭐⭐

Tôi muốn chia thành 4 mức.

INFO

WARNING

ERROR

DEBUG

Ví dụ

INFO

Workbook loaded
WARNING

Retry Row 25
ERROR

Google Timeout
6. Quy tắc Config ⭐⭐⭐⭐⭐

Không hardcode.

Ví dụ

config/

settings.json

provider.json

ui.json

Sau này thay đổi mà không cần build lại.

7. Quy tắc Backup ⭐⭐⭐⭐⭐

Tôi rất khuyến nghị.

Ví dụ

Trước khi ghi Excel

↓

tự tạo

Distance.xlsx

↓

Distance_backup_20260721.xlsx

Nếu ghi lỗi

↓

không mất dữ liệu.

8. Quy tắc Auto Save ⭐⭐⭐⭐⭐

Ví dụ

100 dòng

↓

Save

Nếu

Crash

↓

Resume.

9. Quy tắc Version ⭐⭐⭐⭐⭐

Ví dụ

0.90

Architecture

0.91

GUI

0.92

Preview

0.93

Worker

0.94

Google

1.00

Stable

Không dùng

Final

Final2

Final_New
10. Quy tắc Release ⭐⭐⭐⭐☆

Ví dụ

Release/

DistanceCalculatorPro.exe

CHANGELOG.md

README.md
11. Quy tắc Test ⭐⭐⭐⭐⭐

Mỗi Module đều có Test.

Ví dụ

Excel

Open Workbook

Read Sheet

Preview

Save

Google

Calculate

Retry

Timeout

Stop

GUI

Browse

Start

Stop

Resume
12. Quy tắc Performance ⭐⭐⭐⭐⭐

Ví dụ

Không được

Đọc Workbook

100 lần

Mà

Đọc 1 lần

Cache
13. Quy tắc UI ⭐⭐⭐⭐☆

Ví dụ

Tất cả Button

cao

36 px

Dropdown

36 px

Padding

8 px

Font

Segoe UI 10

Sau này GUI rất đồng nhất.

14. Quy tắc Icon ⭐⭐⭐☆☆

Ví dụ

Browse

📂

Start

▶

Stop

■

Settings

⚙

About

ⓘ

Không mỗi nơi một kiểu.

15. Quy tắc Provider ⭐⭐⭐⭐⭐

Mọi Provider đều phải hỗ trợ tối thiểu

initialize()

calculate()

close()

health_check()

Nhờ vậy GUI không cần biết Provider nào đang chạy.

16. Quy tắc tương thích Excel ⭐⭐⭐⭐⭐

Đây là cái tôi muốn thống nhất nhất.

Phần mềm sẽ chỉ:

✅ Ghi vào các cột kết quả (Distance, Duration, Status...)

Không:

đổi định dạng ô
đổi màu
đổi width
đổi công thức
đổi Filter
đổi Freeze Pane
đổi Sheet khác

Nói cách khác:

Mọi dữ liệu và định dạng ngoài các cột đầu ra phải được giữ nguyên tuyệt đối.

Đây là nguyên tắc rất quan trọng đối với người dùng Excel.

17. Quy tắc "Không có Magic Number"

Ví dụ

Không viết

time.sleep(2)

Mà

time.sleep(config.delay)

Không viết

retry = 3

Mà

retry = settings.max_retry
18. Quy tắc Tài liệu hóa

Tôi nghĩ đây là điểm còn thiếu và rất đáng bổ sung.

Mỗi Sprint hoàn thành sẽ cập nhật 4 tài liệu:

Architecture.md – Kiến trúc tổng thể.
User Guide.md – Hướng dẫn sử dụng.
Developer Guide.md – Hướng dẫn cho lập trình viên (cấu trúc thư mục, quy tắc mở rộng Provider...).
CHANGELOG.md – Lịch sử thay đổi.

Nhờ vậy, nếu sau này bạn hoặc một lập trình viên khác tiếp tục phát triển dự án, sẽ không cần đọc toàn bộ mã nguồn mới hiểu cách hoạt động.

Điều cuối cùng tôi muốn thống nhất

Đây là quy tắc mà tôi cho là quan trọng nhất:

Mọi quyết định có ảnh hưởng đến kiến trúc (thư mục, interface, workflow, định dạng dữ liệu, giao diện chính...) phải được thống nhất trước khi viết mã. Những thay đổi nhỏ như sửa lỗi, cải thiện hiệu năng hoặc điều chỉnh giao diện trong phạm vi đã thống nhất thì có thể thực hiện mà không cần thiết kế lại toàn bộ.

Như vậy, chúng ta sẽ tránh được tình trạng phải "đập đi làm lại" khi dự án đã phát triển đến quy mô lớn.

Nếu áp dụng toàn bộ các quy tắc này, tôi tin rằng DistanceCalculatorPro sẽ có nền tảng đủ tốt để phát triển từ phiên bản hiện tại lên nhiều Provider và nhiều tính năng mới mà vẫn giữ được cấu trúc rõ ràng, ổn định và dễ bảo trì.