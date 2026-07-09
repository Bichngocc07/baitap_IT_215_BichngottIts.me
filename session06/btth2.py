from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# --- 3. DỮ LIỆU MẪU (Mock Data) ---
students = [
    {"id": 1, "code": "SV001", "name": "Nguyen Van A", "email": "a@gmail.com", "age": 20},
    {"id": 2, "code": "SV002", "name": "Tran Thi B", "email": "b@gmail.com", "age": 22},
    {"id": 3, "code": "SV003", "name": "Le Van C", "email": "c@gmail.com", "age": 18}
]

# Định nghĩa Model hứng dữ liệu thô từ Client gửi lên
class StudentCreate(BaseModel):
    code: str
    name: str
    email: str
    age: int

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None


# --- 4. CÁC API ENDPOINTS THEO YÊU CẦU ---

# API 1: Thêm học viên (POST /students)
@app.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(student_in: StudentCreate):
    
    # --- KIỂM TRA ĐIỀU KIỆN XỬ LÝ (MỤC 6) BẰNG LỆNH IF THỦ CÔNG ---
    # 1. Kiểm tra name không được rỗng
    if student_in.name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên học viên không được để trống"
        )
        
    # 2. Kiểm tra email không được rỗng
    if student_in.email.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email không được để trống"
        )
        
    # 3. Kiểm tra age phải lớn hơn 0
    if student_in.age <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tuổi phải lớn hơn 0"
        )
        
    # 4. Kiểm tra code không được trùng (Quét mảng dữ liệu hiện tại)
    for student in students:
        if student["code"].strip().upper() == student_in.code.strip().upper():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã học viên đã tồn tại"
            )

    # Tự tăng ID an toàn bằng hàm max() dựa trên id lớn nhất hiện có
    new_id = max([s["id"] for s in students]) + 1 if students else 1
    
    new_student = {
        "id": new_id,
        "code": student_in.code.strip().upper(),
        "name": student_in.name.strip(),
        "email": student_in.email.strip(),
        "age": student_in.age
    }
    
    # Thêm học viên mới vào cuối mảng
    students.append(new_student)
    return {"message": "Thêm học viên thành công", "data": new_student}


# API 2: Lấy danh sách học viên + Tìm kiếm và lọc (GET /students)
@app.get("/students")
def get_all_students(
    keyword: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None
):
    filtered_students = []
    
    for student in students:
        is_match = True
        
        # 5. Tìm kiếm theo keyword (không phân biệt hoa thường, check trong name, code hoặc email)
        if keyword is not None:
            k = keyword.strip().lower()
            if (k not in student["name"].lower() and 
                k not in student["code"].lower() and 
                k not in student["email"].lower()):
                is_match = False
                
        # Lọc theo tuổi tối thiểu (min_age)
        if min_age is not None:
            if student["age"] < min_age:
                is_match = False
                
        # Lọc theo tuổi tối đa (max_age)
        if max_age is not None:
            if student["age"] > max_age:
                is_match = False
                
        if is_match:
            filtered_students.append(student)
            
    return {"message": "Lấy danh sách học viên thành công", "data": filtered_students}


# API 3: Lấy chi tiết học viên (GET /students/{student_id})
@app.get("/students/{student_id}")
def get_student_detail(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return {"message": "Tìm thấy học viên", "data": student}
            
    # Không tìm thấy -> trả lỗi Student not found theo đúng yêu cầu đề bài
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


# API 4: Cập nhật học viên (PUT /students/{student_id})
@app.put("/students/{student_id}")
def update_student(student_id: int, student_update: StudentUpdate):
    for student in students:
        if student["id"] == student_id:
            
            # Kiểm tra thủ công từng trường nếu client gửi dữ liệu lên để sửa
            if student_update.name is not None:
                if student_update.name.strip() == "":
                    raise HTTPException(status_code=400, detail="Tên không được để trống")
                student["name"] = student_update.name.strip()
                
            if student_update.email is not None:
                if student_update.email.strip() == "":
                    raise HTTPException(status_code=400, detail="Email không được để trống")
                student["email"] = student_update.email.strip()
                
            if student_update.age is not None:
                if student_update.age <= 0:
                    raise HTTPException(status_code=400, detail="Tuổi phải lớn hơn 0")
                student["age"] = student_update.age
                
            return {"message": "Cập nhật học viên thành công", "data": student}
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")


# API 5: Xóa học viên (DELETE /students/{student_id})
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for index, student in enumerate(students):
        if student["id"] == student_id:
            # Xóa học viên khỏi mảng dựa trên vị trí index
            deleted_student = students.pop(index)
            return {"message": "Xóa học viên thành công", "data": deleted_student}
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")