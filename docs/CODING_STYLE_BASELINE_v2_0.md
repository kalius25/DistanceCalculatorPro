Coding Style (CS)
Document Name : Coding Style

Code          : CS

Version       : 2.0.0

Status        : FROZEN

Authoritative : YES
CS-000 Document Information
CS-001 Purpose

Định nghĩa chuẩn viết mã nguồn cho toàn bộ dự án DistanceCalculatorPro, đảm bảo:

Đồng nhất
Dễ đọc
Dễ review
Dễ bảo trì
Dễ mở rộng
CS-002 Scope

Áp dụng cho toàn bộ source code.

CS-003 References
DOC
SS
ADR
MC
DR
CS-100 Naming Convention
CS-101 File Name

Sử dụng snake_case.py

Ví dụ:

browser_manager.py
google_web_provider.py
route_result.py
CS-102 Class Name

Sử dụng PascalCase.

Ví dụ:

BrowserManager
CalculationService
RouteResult
CS-103 Function Name

Sử dụng snake_case.

Ví dụ:

calculate_distance()
load_excel()
parse_duration()
CS-104 Variable Name

Sử dụng snake_case.

Ví dụ:

route_result
travel_time
browser_context
CS-105 Constant

Viết HOA.

Ví dụ:

MAX_RETRY
DEFAULT_TIMEOUT
APP_VERSION
CS-106 Enum

Tên Enum:

ProviderType

Giá trị:

GOOGLE
BING
CS-200 Code Organization
CS-201 Import Order

Thứ tự import:

Standard Library
Third-party Library
Internal Package

Ví dụ

import os
from pathlib import Path

from playwright.sync_api import Page

from app.models.route_result import RouteResult
CS-202 One Class Per File

Mỗi file chỉ nên có một class chính.

CS-203 Function Length

Khuyến nghị:

≤ 50 dòng.

Nếu dài hơn nên tách nhỏ.

CS-204 Class Length

Khuyến nghị:

≤ 500 dòng.

Nếu dài hơn nên xem xét tách class.

CS-205 Maximum Nesting

Không quá 3 cấp.

Ví dụ:

if
    for
        if

Nếu sâu hơn nên tách hàm.

CS-300 Documentation
CS-301 Module Docstring

Mỗi module nên có mô tả.

CS-302 Class Docstring

Public class nên có mô tả.

CS-303 Public Method Docstring

Bao gồm:

Purpose
Parameters
Returns
Raises
CS-304 TODO Format

Định dạng:

# TODO(SP-3):

Ví dụ:

# TODO(SP-4): Add Runtime Settings UI.
CS-400 Exception Style
CS-401

Không dùng:

except:
CS-402

Không dùng:

except Exception:
    pass
CS-403

Exception phải có đầy đủ ngữ cảnh khi ghi log hoặc bọc lại.

CS-500 Logging Style
CS-501

Không dùng print() để ghi log nghiệp vụ.

CS-502

Chỉ sử dụng Logger thống nhất của dự án.

CS-503

Các mức log:

DEBUG
INFO
WARNING
ERROR
CRITICAL
CS-600 Type Hint
CS-601

Public API phải có Type Hint.

Ví dụ:

def calculate(request: RouteRequest) -> RouteResult:
CS-602

Ưu tiên pathlib.Path thay cho chuỗi đường dẫn.

CS-700 Formatting
CS-701

Tuân thủ chuẩn PEP 8.

CS-702

Độ dài dòng:

≤ 100 ký tự.

CS-703

Indent:

4 spaces.

Không dùng Tab.

CS-800 Architecture Compliance
CS-801

Không được vi phạm Module Contract.

CS-802

Không được vi phạm Developer Rules.

CS-803

Không được phá Backward Compatibility nếu chưa có ADR.

CS-804

Ưu tiên mở rộng module hiện có trước khi tạo module mới.

CS-805 Preserve Existing Style

Khi chỉnh sửa một file hiện có:

Giữ nguyên phong cách viết của file nếu không xung đột với Coding Style.
Không đổi dấu nháy chỉ vì sở thích.
Không đổi thứ tự code nếu không cần.
Không format lại toàn bộ file.
Không đổi tên biến chỉ để đẹp hơn.
Chỉ chỉnh phần cần thiết của Work Package.

Quy tắc này hỗ trợ:

DR-001 (Minimal Modification)
DR-004 (Backward Compatibility First)

Mục tiêu là giảm Git Diff, tăng khả năng review và giảm rủi ro.

CS-900 Code Review Checklist

Trước khi đóng một Work Package, tự kiểm tra:

 Đặt tên file đúng chuẩn.
 Đặt tên class đúng chuẩn.
 Đặt tên function đúng chuẩn.
 Đặt tên variable đúng chuẩn.
 Có Type Hint cho Public API.
 Không dùng print() để log.
 Không có except:.
 Không có except Exception: pass.
 Không vi phạm Module Contract.
 Không vi phạm Developer Rules.
 Không tạo Global State.
 Không phá API ngoài phạm vi WP.
 Giữ nguyên Coding Style của file hiện có (CS-805).
 Cập nhật ADR nếu thay đổi kiến trúc.
 Cập nhật tài liệu liên quan nếu cần.
Revision History
Version	Thay đổi
1.0.0	Khởi tạo Coding Style.
2.0.0	Chuẩn hóa theo cấu trúc nhóm (CS-000 → CS-900), bổ sung CS-805 (Preserve Existing Style), đồng bộ với SS v2.0.0 và MC v2.0.0.