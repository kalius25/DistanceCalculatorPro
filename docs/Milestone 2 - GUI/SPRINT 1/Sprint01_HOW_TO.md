Mình muốn điều chỉnh thêm cấu trúc thư mục

Mình đề xuất từ Sprint 01 sẽ như sau:

app/
│
├── controllers/
│
├── services/
│
├── workers/
│
├── gui/
│
│     batch_window.py
│
│     widgets/
│
├── resources/
│
│     ui/
│          batch_window.ui
│
│     icons/
│
│     styles/
│
└── models/

Sau này nếu có thêm:

Settings
About
History
Batch Summary

chỉ cần thêm file .ui.

Sprint 01A (phiên bản cuối)

Mình chốt phạm vi như sau.

File mới
resources/ui/
    batch_window.ui
app/gui/
    batch_window.py
app/gui/
    batch_constants.py
Chưa làm

❌ Excel

❌ Controller

❌ Worker

❌ Progress

❌ Statistics

❌ Log

Chỉ tạo đúng layout.

Sprint 01B

Tạo

StatisticsWidget

ProgressWidget

LogWidget

ControlWidget

và nhúng vào batch_window.ui.

Sprint 01C

Kết nối MainWindow

↓

Mở Batch Window.

Sau Sprint 01

Bạn sẽ có một cửa sổ gần như hoàn chỉnh về giao diện.

Sau đó Sprint 02 mới bắt đầu đọc Excel.

Mình có thêm một đề xuất rất quan trọng (đây là quyết định cuối cùng trước khi code)
Chúng ta dùng GitFlow ngay từ đầu

Ví dụ:

main

luôn chạy được.

Mỗi Sprint

feature/batch-gui

↓

Merge

↓

Delete branch

Sprint 02

feature/excel-import

↓

Merge

↓

Delete

Sau này nhìn lịch sử Git sẽ rất đẹp và chuyên nghiệp.

Điều mình cam kết với bạn

Từ Sprint 01 trở đi, mình sẽ không còn trả lời theo kiểu "gợi ý".

Mình sẽ làm như một Technical Lead thực thụ:

Thiết kế trước.
Viết mã theo từng sprint.
Review kiến trúc.
Đảm bảo không tạo nợ kỹ thuật.
Giữ toàn bộ module mới ở mức có thể đạt 100% unit test coverage như phần lõi hiện tại.
Mình cũng muốn thống nhất một nguyên tắc làm việc cuối cùng

Đối với mỗi Sprint, mình sẽ luôn cung cấp:

Mục tiêu Sprint.
Danh sách file mới và file sửa đổi.
Giải thích quyết định thiết kế.
Mã nguồn hoàn chỉnh cho từng file trong Sprint (không phải đoạn mã rời).
Checklist kiểm thử (build, chạy, test).
Tiêu chí hoàn thành Sprint.

Theo mình, cách làm này sẽ biến cuộc trò chuyện của chúng ta thành một quá trình phát triển phần mềm có tổ chức, gần giống như đang làm việc chung trong một repository Git thực tế.