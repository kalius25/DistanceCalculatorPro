Module Contract (MC)
Document Name : Module Contract

Code          : MC

Version       : 2.0.0

Status        : FROZEN

Authoritative : YES
MC-000 Document Information
MC-001 Purpose

Định nghĩa trách nhiệm, quyền hạn, ranh giới và quy tắc tương tác giữa các module trong DistanceCalculatorPro.

Đây là tài liệu chính thức để đảm bảo kiến trúc luôn nhất quán.

MC-002 Scope

Áp dụng cho toàn bộ source code.

MC-003 References
DOC
SS
ADR
DR
MC-100 Layer Contracts
MC-110 GUI Layer
MC-111 Purpose

Hiển thị giao diện và nhận thao tác từ người dùng.

MC-112 Responsibilities
Hiển thị dữ liệu
Điều khiển giao diện
Nhận sự kiện người dùng
MC-113 Inputs
User Action
Controller Response
MC-114 Outputs
Controller Request
MC-115 Allowed Dependencies
Controller Layer
MC-116 Forbidden Dependencies
Service
Provider
Engine
Parser
Database
Excel
Browser
MC-117 Ownership

Owns

Window State
Widget State
ViewModel
Progress UI
Control Enable/Disable State

Does NOT Own

Business Data
Runtime Settings
Browser State
Batch State
Provider State
MC-120 Controller Layer
MC-121 Purpose

Điều phối luồng xử lý.

MC-122 Responsibilities
Nhận Request
Điều hướng Workflow
Gọi Service
Trả kết quả cho GUI
MC-123 Inputs
GUI Request
MC-124 Outputs
Service Request
GUI Response
MC-125 Allowed Dependencies
Service
Model
MC-126 Forbidden Dependencies
Engine
Parser
Browser
MC-127 Ownership

Owns

Request Context
Response Context

Does NOT Own

Batch Progress
Runtime Settings
Browser
Cache
MC-130 Service Layer
MC-131 Purpose

Business Logic.

MC-132 Responsibilities
Workflow
Business Rules
Retry Logic
Batch Logic
Logging
MC-133 Inputs
RouteRequest
MC-134 Outputs
RouteResult
MC-135 Allowed Dependencies
Provider
Model
Utility
Config
MC-136 Forbidden Dependencies
GUI
Browser
DOM
MC-137 Ownership

Owns

Business Session
Batch Progress
Retry State
Workflow State

Does NOT Own

Browser Lifetime
HTML
GUI State
MC-140 Provider Layer
MC-141 Purpose

Kết nối tới dịch vụ bên ngoài.

MC-142 Responsibilities
Chuẩn hóa Provider Interface
Gọi Engine
Trả dữ liệu cho Service
MC-143 Inputs
RouteRequest
MC-144 Outputs
DistanceResult
MC-145 Allowed Dependencies
Engine
Parser
Model
MC-146 Forbidden Dependencies
GUI
Excel
Runtime Settings
Business Workflow
MC-147 Ownership

Owns

Provider Request Context
Provider Response Context

Does NOT Own

Batch Progress
Browser Lifetime
Runtime Settings
MC-150 Engine Layer
MC-151 Purpose

Browser Automation.

MC-152 Responsibilities
Browser
Navigation
DOM
Retry thấp tầng
MC-153 Inputs
URL
Browser Command
MC-154 Outputs
HTML
DOM
MC-155 Allowed Dependencies
Playwright
Utility
MC-156 Forbidden Dependencies
GUI
Service
Excel
Business Logic
MC-157 Ownership

Owns

Browser Instance
Browser Context
Page
DOM State
Navigation State

Does NOT Own

Business Result
Excel State
GUI State
MC-160 Parser Layer
MC-161 Purpose

HTML → Model.

MC-162 Responsibilities
Parse
Validate
MC-163 Inputs
HTML
MC-164 Outputs
Model
MC-165 Allowed Dependencies
Model
MC-166 Forbidden Dependencies
Browser
GUI
Workflow
Excel
MC-167 Ownership

Owns

None

Parser must be Stateless.

MC-170 Model Layer
MC-171 Purpose

Định nghĩa dữ liệu.

MC-172 Responsibilities
DTO
Entity
Value Object
MC-173 Inputs
Data
MC-174 Outputs
Data
MC-175 Allowed Dependencies
Enum
MC-176 Forbidden Dependencies
Service
Provider
Engine
Config
MC-177 Ownership

Owns

Data Structure

Does NOT Own

Workflow
Business Logic
MC-180 Config Layer
MC-181 Purpose

Quản lý cấu hình hệ thống.

MC-182 Responsibilities
Version
Runtime Settings
Constants
Configuration
Feature Flags
MC-183 Inputs
JSON
Default Values
MC-184 Outputs
Config Object
MC-185 Allowed Dependencies
None
MC-186 Forbidden Dependencies
GUI
Service
Provider
MC-187 Ownership

Owns

Application Version
Runtime Settings
System Configuration
Constants
Feature Flags

Single Source of Truth cho toàn bộ cấu hình hệ thống.

MC-190 Utility & Exception Layer
MC-191 Purpose

Cung cấp chức năng dùng chung.

MC-192 Responsibilities
Logging
Helper
Converter
Exception
MC-193 Inputs
Generic Data
MC-194 Outputs
Generic Result
MC-195 Allowed Dependencies
Python Standard Library
MC-196 Forbidden Dependencies
GUI
Business Workflow
MC-197 Ownership

Owns

Không sở hữu Business State.
MC-200 Dependency Rules
Rule	Nội dung
MC-201	GUI chỉ được gọi Controller.
MC-202	Controller chỉ điều phối Workflow, không chứa Business Logic.
MC-203	Service không được cập nhật GUI trực tiếp.
MC-204	Provider không được chứa Business Workflow.
MC-205	Engine không được biết Business Workflow.
MC-206	Parser phải Stateless.
MC-207	Model không được chứa Business Logic.
MC-208	Config là nguồn duy nhất của Runtime Settings (Single Source of Truth).
MC-300 Ownership Rules
Rule	Nội dung
MC-301	Single Owner Rule – Một State chỉ có một Owner duy nhất.
MC-302	Owner Access Rule – Module khác chỉ được truy cập State thông qua Owner của State đó.
MC-303	No Global State Rule – Không chia sẻ State bằng Global Variable.
MC-304	State Lifetime Rule – Mỗi State phải có vòng đời rõ ràng (Application, Session, Request hoặc Temporary).
MC-305	State Consistency Rule – Không được tạo nhiều bản sao có thể ghi (mutable copies) của cùng một State ở nhiều Layer.
MC-400 Design Principles
Rule	Nội dung
MC-401	Backward Compatibility First
MC-402	Layer Isolation
MC-403	Single Responsibility
MC-404	Loose Coupling
MC-405	High Cohesion
MC-406	Reuse Existing Modules First
MC-407	Documentation First
MC-408	Minimal Modification
MC-500 Future Extensions

Dành cho các Sprint sau.

ID	Nội dung
MC-501	Plugin Contract
MC-502	Provider Contract
MC-503	API Contract
MC-504	Event Contract
MC-505	Cache Contract
Revision History
Version	Thay đổi
1.0	Khởi tạo Module Contract
1.2	Bổ sung Ownership và Design Principles
2.0.0	Chuẩn hóa cấu trúc theo nhóm MC-000 → MC-500, bổ sung State Lifetime, State Consistency và thống nhất với SS v2.0.0