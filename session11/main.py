# 1.TẠO DATABASE: connect_db
# 2.TẠO BẢNG STUDENTS VỚI CÁC THUỘC TÍNH
#   +id:mã sinh viên
#   +name:tên sinh viên
#   +class:tên lớp
#   +email:email sinh viên
# 3.Viết các API
#   +test api đang chạy
#   +api lấy ds sinh viên
#   +api lấy chi tiết sinh viên theo id
#   +api thêm sinh viên
#   +api xóa sinh viên
#   +api cập nhật sinh viên
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel, EmailStr

# 1. KHỞI TẠO FASTAPI
app = FastAPI(title="Student Management API")

# 2. CẤU HÌNH CƠ SỞ DỮ LIỆU (DATABASE: connect_db)
# Đảm bảo bạn đã tạo database mang tên 'connect_db' trong MySQL trước khi chạy
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/connect_db"
engine = create_engine(
    DATABASE_URL, 
    pool_recycle=3600, 
    pool_pre_ping=True
)

# 3. KHỞI TẠO PHIÊN LÀM VIỆC (SESSION) VÀ BASE MODEL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. DEPENDENCY: QUẢN LÝ KẾT NỐI DB AN TOÀN
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Giải phóng kết nối ngay sau khi phản hồi API hoàn tất để tránh Connection Leak

# 5. ĐỊNH NGHĨA BẢNG TRONG DATABASE (Model SQLAlchemy)
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    # Vì 'class' là từ khóa hệ thống trong Python nên ta đặt tên thuộc tính/biến là 'class_name'
    # nhưng cấu hình ánh xạ cột trong MySQL vẫn là tên 'class' đúng chuẩn đề bài yêu cầu
    class_name = Column("class", String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)

# Tự động đồng bộ và khởi tạo bảng 'students' trong MySQL nếu chưa tồn tại
Base.metadata.create_all(bind=engine)


# 6. ĐỊNH NGHĨA SCHEMAS (Pydantic Models để nhận/validate dữ liệu đầu vào)
class StudentCreate(BaseModel):
    name: str
    class_name: str
    email: EmailStr  # Tự động validate đúng định dạng email (cần cài pip install pydantic[email])

class StudentUpdate(BaseModel):
    name: str | None = None
    class_name: str | None = None
    email: EmailStr | None = None


# =================================================================
# 7. HỆ THỐNG ENDPOINT APIs
# =================================================================

# API 1: Test API đang hoạt động
@app.get("/")
def home():
    return {
        "message": "API đang chạy"
    }


# API 2: Lấy danh sách toàn bộ sinh viên
@app.get("/students")
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return {
        "message": "Lấy danh sách sinh viên thành công",
        "data": students
    }


# API 3: Lấy chi tiết sinh viên theo ID
@app.get("/students/{student_id}")
def get_student_detail(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    
    # Bẫy lỗi nếu không tìm thấy ID sinh viên
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID: {student_id}"
        )
        
    return {
        "message": "Lấy chi tiết sinh viên thành công",
        "data": student
    }


# API 4: Thêm mới sinh viên (Chuẩn hóa mã trả về 201 Created)
@app.post("/students", status_code=status.HTTP_201_CREATED)
def add_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    # Bẫy lỗi: Kiểm tra trùng lặp Email trong hệ thống
    exist_email = db.query(Student).filter(Student.email == student_in.email).first()
    if exist_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã tồn tại trên hệ thống"
        )

    # Khởi tạo bản ghi sinh viên mới
    new_student = Student(
        name=student_in.name,
        class_name=student_in.class_name,
        email=student_in.email
    )
    
    try:
        db.add(new_student)
        db.commit()          # Xác nhận lưu thay đổi xuống MySQL (Tránh lỗi mất transaction)
        db.refresh(new_student)  # Lấy ID tự tăng vừa sinh ra
        
        return {
            "message": "Thêm sinh viên thành công",
            "data": new_student
        }
    except Exception as e:
        db.rollback()        # Hoàn tác giao dịch nếu xảy ra lỗi trong quá trình lưu trữ
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống: {str(e)}"
        )


# API 5: Cập nhật thông tin sinh viên (PUT)
@app.put("/students/{student_id}")
def update_student(student_id: int, student_in: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    
    # Bẫy lỗi: Kiểm tra sự tồn tại của sinh viên cần cập nhật
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID: {student_id} để cập nhật"
        )
        
    # Tiến hành cập nhật từng trường nếu Client gửi lên thông tin mới
    if student_in.name is not None:
        student.name = student_in.name
    if student_in.class_name is not None:
        student.class_name = student_in.class_name
    if student_in.email is not None:
        # Kiểm tra nếu đổi sang email mới mà trùng với người khác trong DB
        if student_in.email != student.email:
            exist_email = db.query(Student).filter(Student.email == student_in.email).first()
            if exist_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email mới này đã được sử dụng bởi sinh viên khác"
                )
        student.email = student_in.email
        
    try:
        db.commit()
        db.refresh(student)
        return {
            "message": "Cập nhật thông tin sinh viên thành công",
            "data": student
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi cập nhật: {str(e)}"
        )


# API 6: Xóa sinh viên khỏi hệ thống (DELETE)
@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    
    # Bẫy lỗi nếu không tìm thấy tài nguyên cần xóa
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên có ID: {student_id} để thực hiện xóa"
        )
        
    try:
        db.delete(student)
        db.commit()  # Thực thi lệnh DELETE xuống MySQL thực tế
        return {
            "message": f"Xóa sinh viên có ID {student_id} thành công"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi xóa: {str(e)}"
        )