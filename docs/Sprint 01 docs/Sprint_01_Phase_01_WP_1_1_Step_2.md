WP-1.1 – Step 2
Implementation Plan
Work Package

WP-1.1

Name

Core Foundation

Step

2 – Implementation Plan

Status

Approved
1. Objective

Chuẩn hóa tầng Foundation của dự án mà không phá vỡ API hiện tại.

Toàn bộ thay đổi phải tuân thủ:

ADR-001 Foundation Standardization
ADR-002 Reuse Existing Modules First
ADR-003 Backward Compatibility First
MC v2.0.0
DR v1.0.0
CS v2.0.0
2. Scope
Included
Configuration
Chuẩn hóa Version Management.
Chuẩn hóa ErrorCode.
Chuẩn hóa Runtime Settings.
Chuẩn hóa Constants.
Exception
Chuẩn hóa BaseException.
Chuẩn hóa ErrorCode.
Chuẩn hóa Exception Hierarchy.
Metadata
Đồng bộ Version.
Excluded

Không thực hiện trong WP-1.1:

GUI
Controller
Service
Provider Logic
Engine
Parser Logic
Database
Excel
Browser Workflow
3. Design Decisions
3.1 Config API

Giữ nguyên API hiện tại.

Ví dụ:

HEADLESS

MAX_RETRY

GOOGLE_MAPS_URL

không đổi tên.

Lý do:

Backward Compatibility.

3.2 Version

Bổ sung Version Management tập trung.

Không hardcode Version ở nhiều nơi.

Nguồn chính thức:

Config Layer
3.3 ErrorCode

Bổ sung:

ErrorCode Enum

độc lập với Exception.

Ví dụ:

CONFIG_ERROR

PARSER_ERROR

PROVIDER_ERROR

ENGINE_ERROR
3.4 Runtime Settings

Tách về mặt khái niệm:

System Configuration

↓

Runtime Settings

Nhưng chưa tách file.

Lý do:

Minimal Modification.

3.5 Compatibility Alias

Tiếp tục giữ:

GOOGLE_MAPS_DIRECTIONS_URL

GOOGLE_MAPS_SEARCH_URL

để tương thích ngược.

4. Files Planned
Modify
app/config.py
Modify
app/exceptions/
Read Only
pyproject.toml

requirements.txt

requirements-dev.txt
No New Folder

Không tạo package mới.

5. Expected Deliverables

Sau WP-1.1 sẽ có:

Version Management chuẩn.
ErrorCode chuẩn.
Exception Hierarchy chuẩn.
Runtime Settings rõ ràng.
Không phá API.
6. Risk Assessment
Low Risk
Version constant
ErrorCode Enum
Documentation
Medium Risk

Exception hierarchy.

Cần giữ nguyên các Exception hiện tại.

High Risk

Không có.

7. Compatibility Strategy

Không đổi:

Tên module.
Public API.
Constants đang sử dụng.
Import path.
Folder structure.

Chỉ bổ sung.

8. Testing Plan

Sau khi hoàn thành sẽ kiểm tra:

Import toàn bộ project.
Không phát sinh Circular Import.
Config hoạt động.
Exception hoạt động.
Không ảnh hưởng Provider.
Không ảnh hưởng GUI.
9. Acceptance Criteria

WP-1.1 được coi là hoàn thành khi đáp ứng tất cả:

Không phá Backward Compatibility.
Không thay đổi Public API.
Có Version Management tập trung.
Có ErrorCode Standard.
Exception tuân thủ chuẩn.
Config tiếp tục là Single Source of Truth.
Không phát sinh Circular Import.
Toàn bộ thay đổi tuân thủ SS, MC, DR, CS và các ADR hiện hành.

Đánh giá trước khi triển khai

Sau khi xem các file bạn cung cấp, tôi không thấy cần điều chỉnh kế hoạch của WP-1.1. Kiến trúc hiện tại phù hợp với các quyết định đã được chốt. Điều này có nghĩa là khi bước sang WP-1.1 – Step 3 (Implementation), chúng ta sẽ chỉ thực hiện các thay đổi có phạm vi hẹp trên config.py và hệ thống exceptions, đúng với tinh thần Foundation Standardization, Minimal Modification và Backward Compatibility First.