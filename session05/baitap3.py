# Phần 1: Phân tích và thiết kế giải pháp1. 
# Phân tích bài toánInput 
# API nhận là gì?
# Nhận một Request Body định dạng JSON chứa dữ liệu đăng ký mới từ phía Client gửi lên bao gồm hai trường thông tin bắt buộc:
# student_id (Kiểu số nguyên int): Mã định danh của sinh viên muốn đăng ký.
# course_id (Kiểu số nguyên int): Mã định danh của khóa học được chọn.
# Output khi thành công trả về giá trị gì?
# HTTP Status Code: 201 Created.
# Dữ liệu trả về (Response Body): JSON Object chứa phiếu đăng ký mới đã được gán ID tự tăng (id, student_id, course_id).
# Output khi thất bại trả về giá trị gì?
# HTTP Status Code: 400 Bad Request (hoặc 404 Not Found tùy thuộc vào việc check ID tồn tại).
# Dữ liệu trả về: JSON Object chứa thông báo lỗi chi tiết theo định dạng hệ thống:
# Trùng lịch đăng ký: {"detail": "Student already registered this course"}
# Khóa học đầy sĩ số: {"detail": "Course is full"}
# 2. Đề xuất giải pháp
# Xây dựng luồng xử lý tuần tự qua 4 bước kiểm tra (bẫy dữ liệu) để tối ưu hiệu năng:
# Bước 1: Kiểm tra student_id có tồn tại trong danh sách students hay không. Nếu không, báo lỗi.
# Bước 2: Kiểm tra course_id có tồn tại trong danh sách courses hay không. Nếu không, báo lỗi.
# Bước 3 (Bẫy 1): Duyệt mảng registrations, nếu phát hiện bản ghi nào trùng cả student_id và course_id $\rightarrow$ Trả về lỗi "Student already registered this course".
# Bước 4 (Bẫy 2): Đếm số lượng học viên đã đăng ký khóa học đó trong mảng registrations. So sánh số lượng này với sức chứa capacity của khóa học được cấu hình trong mảng courses. Nếu số lượng hiện tại $\ge$ capacity $\rightarrow$ Trả về lỗi "Course is full".
# Bước 5: Nếu vượt qua toàn bộ các bước kiểm tra trên, tiến hành tạo mới đối tượng phiếu đăng ký, .append() vào mảng và trả về kết quả thành công với mã 201.
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# --- MOCK DATA ---
students = [
    {"id": 1, "name": "Nguyen Van A"},
    {"id": 2, "name": "Tran Thi B"},
    {"id": 3, "name": "Le Van C"}
]

courses = [
    {"id": 1, "name": "FastAPI Basic", "capacity": 2},
    {"id": 2, "name": "Python OOP", "capacity": 2}
]

registrations = [
    {"id": 1, "student_id": 1, "course_id": 1},
    {"id": 2, "student_id": 2, "course_id": 1}
]

# --- SCHEMA ---
class RegistrationCreate(BaseModel):
    student_id: int
    course_id: int

# --- API ENDPOINT ---
@app.post("/registrations", status_code=status.HTTP_201_CREATED)
def create_registration(registration: RegistrationCreate):
    
    # 1. Kiểm tra student_id phải tồn tại trong hệ thống
    student_exists = any(s["id"] == registration.student_id for s in students)
    if not student_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student does not exist"
        )
        
    # 2. Kiểm tra course_id phải tồn tại trong hệ thống và lấy thông tin khóa học đó
    target_course = None
    for c in courses:
        if c["id"] == registration.course_id:
            target_course = c
            break
            
    if not target_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course does not exist"
        )
        
    # 3. [Bẫy 1]: Kiểm tra học viên bị đăng ký trùng một khóa học
    for r in registrations:
        if r["student_id"] == registration.student_id and r["course_id"] == registration.course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student already registered this course"
            )
            
    # 4. [Bẫy 2]: Kiểm tra khóa học đã đủ sĩ số (Capacity) chưa
    # Đếm số lượng sinh viên hiện tại của khóa học đó
    current_enrolled = sum(1 for r in registrations if r["course_id"] == registration.course_id)
    
    if current_enrolled >= target_course["capacity"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is full"
        )
        
    # 5. Tạo phiếu đăng ký mới nếu tất cả điều kiện đều hợp lệ
    new_id = len(registrations) + 1 if registrations else 1
    new_registration = {
        "id": new_id,
        "student_id": registration.student_id,
        "course_id": registration.course_id
    }
    
    registrations.append(new_registration)
    return new_registration