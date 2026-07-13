from fastapi import FastAPI
from pydantic import BaseModel
add = FastAPI(
    #title="🧸phát ây pi em cũa bích ngott cte💕"
)

"""
METHOD
GET    : Lấy dữ liệu
POST   : Thêm dữ liệu
PUT    : Cập nhật toàn bộ
PATCH  : Cập nhật một phần
DELETE : Xóa dữ liệu
"""

students = [
    {
        "id": 2,
        "name": "Bích Ngọc",
        "email": "ngoc@gmail.com"
    }
]
class StudentCreate(BaseModel):
    name: str
    email:str
@add.get("/")
def home():
    return {
        "message": "API đang chạy"
    }


@add.get("/student")
def get_student():
    return {
        "message": "Lấy danh sách thành công",
        "data": students
    }


# API lấy chi tiết 1 sinh viên
@add.get("/student/{student_id}")
def get_student_detail(student_id: int):
    print("ID sinh viên là:", student_id)

    for student in students:
        if student["id"] == student_id:
            return {
                "message": "Tìm thấy sinh viên",
                "data": student
            }

    return {
        "message": "Không tìm thấy sinh viên",
        "data": None
    }
#API thêm mới sinh viên
@add.post("/students")
def add_student(new_student: StudentCreate):
    print("new_studen",new_student)
    add_new_student = {
        "id": new_student.id,
        "name": new_student.name,
        "email": new_student.email
    }
    students.append(add_new_student)
    return{
        "message":"thêm sv thành công",
        "data": students
    }
#API xóa sinh viên 
@add.delete("/students/student_id")
def delete_student(student_id:int):
    print("id sv cần xóa", student_id)
    for std in students:
        if std["id"] == student_id:
            return{
                "message":"xóa sv tcong",
                "data"   : std
            }
    return{
        "message":"kh tìm thấy svien",
        "data"   : None
    }
#API cập nhật thông tin sinh viên
@add.put("students/{student_id}")
def update_student(student_id:int,updata_student:StudentCreate):
    for std in students:
        if std["id"] == student_id:
            std["name"] = updata_student.name
            std["email"] = updata_student.email
            return{
                "message":"cập nhật sinh viên thành công",
                "data"   : students
            }
    return{
            "message":"kh tìm thấy sinh viên",
            "data"   : None
        }