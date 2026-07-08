# Phần 1: Chỉ ra lỗi bằng test case cụ thể
# TEST CASE 1: Thử nghiệm đăng ký trùng cặp giá trị "SV001" và "course_id = 1"
# STT: 1
# Dữ liệu gửi lên (Request Body):
# JSON
# {
#   "student_id": "SV001",
#   "course_id": 1
# }
# Kết quả hiện tại: Hệ thống vẫn tạo thành công bản ghi mới với ID tự tăng. Mảng enrollments xuất hiện 2 bản ghi trùng lặp đồng thời cả hai giá trị student_id và course_id này.
# Kết quả đúng mong muốn: Hệ thống phải trả về thông báo lỗi bằng HTTPException (Mã lỗi 400 Bad Request) để cảnh báo rằng học viên đã đăng ký khóa học này trước đó rồi.
# Lỗi phát hiện: Hàm xử lý hoàn toàn khuyết thiếu logic kiểm tra sự tồn tại đồng thời của cặp student_id và course_id trước khi thực hiện hành động ghi dữ liệu.

# TEST CASE 2: Thử nghiệm đăng ký trùng cặp giá trị "SV002" và "course_id = 1"
# STT: 2
# Dữ liệu gửi lên (Request Body):
# JSON
# {
#   "student_id": "SV002",
#   "course_id": 1
# }
# Kết quả hiện tại: Hệ thống vẫn chấp nhận request và tạo thành công bản ghi đăng ký mới, dẫn đến dữ liệu bị trùng lặp trực tiếp với bản ghi thứ hai đang sẵn có trong database giả lập.
# Kết quả đúng mong muốn: Hệ thống phải chặn lại ngay lập tức, ném ra lỗi thông báo trùng lịch đăng ký nhằm đảm bảo tính toàn vẹn và nhất quán của dữ liệu.
# Lỗi phát hiện: Tương tự như cấu trúc trên, hệ thống bỏ qua bước quét toàn bộ mảng dữ liệu enrollments hiện tại trước khi gọi phương thức .append().
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Dữ liệu đăng ký khóa học giả lập ban đầu (Mock Data)
enrollments = [
    {
        "id": 1,
        "student_id": "SV001",
        "course_id": 1
    },
    {
        "id": 2,
        "student_id": "SV002",
        "course_id": 1
    }
]

# Định nghĩa Schema tiếp nhận dữ liệu từ Client gửi lên
class EnrollmentCreate(BaseModel):
    student_id: str
    course_id: int
# SỬA LỖI: Cấu hình status_code=201 chuẩn RESTful cho hành động Tạo mới thành công
@app.post("/enrollments", status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment: EnrollmentCreate):
    
    # 1. Logic kiểm tra trùng lặp bản ghi đăng ký
    for e in enrollments:
        # Nếu trùng đồng thời cả student_id VÀ course_id
        if e["student_id"] == enrollment.student_id and e["course_id"] == enrollment.course_id:
            # Lập tức ném lỗi HTTPException (Mã 400 Bad Request) để ngăn chặn hành động
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Học viên '{enrollment.student_id}' đã đăng ký khóa học này trước đó."
            )
            
    # 2. Tạo bản ghi đăng ký mới nếu kiểm tra hợp lệ
    new_enrollment = {
        "id": len(enrollments) + 1,
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id
    }
    
    # Lưu bản ghi mới vào danh sách hệ thống
    enrollments.append(new_enrollment)
    
    # 3. Trả về thông báo thành công và cấu trúc bản ghi vừa được tạo
    return {
        "message": "Enroll successfully",
        "data": new_enrollment
    }