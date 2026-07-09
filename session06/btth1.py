from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# --- 3. DỮ LIỆU MẪU (Mock Data) ---
courses = [
    {"id": 1, "code": "PY101", "name": "Python Basic", "duration": 30, "fee": 3000000},
    {"id": 2, "code": "API101", "name": "FastAPI Basic", "duration": 24, "fee": 2500000},
    {"id": 3, "code": "JV101", "name": "Java Basic", "duration": 40, "fee": 4000000}
]

# Định nghĩa Model để hứng dữ liệu thô từ Client gửi lên
class CourseCreate(BaseModel):
    code: str
    name: str
    duration: int
    fee: int

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    duration: Optional[int] = None
    fee: Optional[int] = None


# --- 4. CÁC API ENDPOINTS THEO YÊU CẦU ---

# API 1: Thêm khóa học (POST /courses)
@app.post("/courses", status_code=status.HTTP_201_CREATED)
def create_course(course_in: CourseCreate):
    
    # --- KIỂM TRA ĐIỀU KIỆN XỬ LÝ (MỤC 6) BẰNG LỆNH IF THỦ CÔNG ---
    # 1. Kiểm tra name không được rỗng
    if course_in.name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Tên khóa học không được để trống"
        )
        
    # 2. Kiểm tra duration phải lớn hơn 0
    if course_in.duration <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Thời lượng phải lớn hơn 0"
        )
        
    # 3. Kiểm tra fee phải lớn hơn hoặc bằng 0
    if course_in.fee < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Học phí phải lớn hơn hoặc bằng 0"
        )
        
    # 4. Kiểm tra code không được trùng (Quét mảng dữ liệu hiện tại)
    for course in courses:
        if course["code"].strip().upper() == course_in.code.strip().upper():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Mã khóa học đã tồn tại"
            )

    # Giải pháp tự tăng ID an toàn bằng hàm max() để tránh trùng ID khi xóa phần tử
    new_id = max([c["id"] for c in courses]) + 1 if courses else 1
    
    new_course = {
        "id": new_id,
        "code": course_in.code.strip().upper(),
        "name": course_in.name.strip(),
        "duration": course_in.duration,
        "fee": course_in.fee
    }
    
    # THÊM VÀO MẢNG GIẢ LẬP
    courses.append(new_course)
    return {"message": "Thêm khóa học thành công", "data": new_course}


# API 2: Lấy danh sách khóa học + Tìm kiếm và lọc (GET /courses)
@app.get("/courses")
def get_all_courses(
    keyword: Optional[str] = None, 
    min_fee: Optional[int] = None, 
    max_fee: Optional[int] = None
):
    filtered_courses = []
    
    for course in courses:
        is_match = True
        
        # 5. Tìm kiếm theo keyword (không phân biệt hoa thường, check trong name hoặc code)
        if keyword is not None:
            k = keyword.strip().lower()
            if k not in course["name"].lower() and k not in course["code"].lower():
                is_match = False
                
        # Lọc theo học phí tối thiểu (min_fee)
        if min_fee is not None:
            if course["fee"] < min_fee:
                is_match = False
                
        # Lọc theo học phí tối đa (max_fee)
        if max_fee is not None:
            if course["fee"] > max_fee:
                is_match = False
                
        if is_match:
            filtered_courses.append(course)
            
    return {"message": "Lấy danh sách khóa học thành công", "data": filtered_courses}


# API 3: Lấy chi tiết khóa học (GET /courses/{course_id})
@app.get("/courses/{course_id}")
def get_course_detail(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            return {"message": "Tìm thấy khóa học", "data": course}
            
    # Bẫy lỗi: Nếu không tìm thấy khóa học theo id, trả lỗi Course not found
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


# API 4: Cập nhật khóa học (PUT /courses/{course_id})
@app.put("/courses/{course_id}")
def update_course(course_id: int, course_update: CourseUpdate):
    for course in courses:
        if course["id"] == course_id:
            
            # Kiểm tra thủ công từng trường xem client có truyền lên để cập nhật không
            if course_update.name is not None:
                if course_update.name.strip() == "":
                    raise HTTPException(status_code=400, detail="Tên không được để trống")
                course["name"] = course_update.name.strip()
                
            if course_update.duration is not None:
                if course_update.duration <= 0:
                    raise HTTPException(status_code=400, detail="Thời lượng phải lớn hơn 0")
                course["duration"] = course_update.duration
                
            if course_update.fee is not None:
                if course_update.fee < 0:
                    raise HTTPException(status_code=400, detail="Học phí không được âm")
                course["fee"] = course_update.fee
                
            return {"message": "Cập nhật khóa học thành công", "data": course}
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


# API 5: Xóa khóa học (DELETE /courses/{course_id})
@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    for index, course in enumerate(courses):
        if course["id"] == course_id:
            # Xóa phần tử khỏi mảng dựa trên vị trí index
            deleted_course = courses.pop(index)
            return {"message": "Xóa khóa học thành công", "data": deleted_course}
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")