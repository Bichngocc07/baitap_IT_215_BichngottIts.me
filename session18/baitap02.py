
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    relationship,
    Session
)


# ==================================================
# DATABASE
# ==================================================

DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/workshop_db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==================================================
# MODEL STUDENT
# ==================================================

class Student(Base):
    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_code = Column(
        String(20),
        unique=True,
        nullable=False
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    registrations = relationship(
        "Registration",
        back_populates="student"
    )


# ==================================================
# MODEL WORKSHOP
# ==================================================

class Workshop(Base):
    __tablename__ = "workshops"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    maximum_participants = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="OPEN"
    )

    start_time = Column(
        DateTime,
        nullable=False
    )

    registrations = relationship(
        "Registration",
        back_populates="workshop"
    )


# ==================================================
# MODEL REGISTRATION
# ==================================================

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        nullable=False
    )

    workshop_id = Column(
        Integer,
        ForeignKey("workshops.id"),
        nullable=False
    )

    registered_at = Column(
        DateTime,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="REGISTERED"
    )

    student = relationship(
        "Student",
        back_populates="registrations"
    )

    workshop = relationship(
        "Workshop",
        back_populates="registrations"
    )

    # Không cho đăng ký trùng
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "workshop_id",
            name="unique_student_workshop"
        ),
    )


# Tạo bảng
Base.metadata.create_all(bind=engine)


# ==================================================
# PYDANTICS SCHEMA
# ==================================================

class StudentCreate(BaseModel):
    student_code: str
    full_name: str
    email: EmailStr


class StudentResponse(BaseModel):
    id: int
    student_code: str
    full_name: str
    email: str
    status: str

    class Config:
        from_attributes = True


class WorkshopCreate(BaseModel):
    title: str
    description: str | None = None
    maximum_participants: int
    status: str = "OPEN"
    start_time: datetime


class WorkshopResponse(BaseModel):
    id: int
    title: str
    description: str | None
    maximum_participants: int
    status: str
    start_time: datetime

    class Config:
        from_attributes = True


class RegistrationCreate(BaseModel):
    student_id: int
    workshop_id: int


class RegistrationResponse(BaseModel):
    id: int
    student_id: int
    workshop_id: int
    registered_at: datetime
    status: str

    class Config:
        from_attributes = True


# ==================================================
# FASTAPI
# ==================================================

app = FastAPI(
    title="Student Workshop Registration API",
    description="Hệ thống đăng ký workshop cho sinh viên",
    version="1.0.0"
)


# ==================================================
# 1. TẠO SINH VIÊN
# POST /students
# ==================================================

@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db)
):

    # Kiểm tra mã sinh viên trùng
    existing_code = (
        db.query(Student)
        .filter(
            Student.student_code == data.student_code
        )
        .first()
    )

    if existing_code:
        raise HTTPException(
            status_code=400,
            detail="Mã sinh viên đã tồn tại"
        )

    # Kiểm tra email trùng
    existing_email = (
        db.query(Student)
        .filter(
            Student.email == data.email
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email đã tồn tại"
        )

    student = Student(
        student_code=data.student_code,
        full_name=data.full_name,
        email=data.email,
        status="ACTIVE"
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


# ==================================================
# 2. LẤY DANH SÁCH SINH VIÊN
# GET /students
# ==================================================

@app.get(
    "/students",
    response_model=list[StudentResponse]
)
def get_students(
    db: Session = Depends(get_db)
):

    return db.query(Student).all()


# ==================================================
# 3. TẠO WORKSHOP
# POST /workshops
# ==================================================

@app.post(
    "/workshops",
    response_model=WorkshopResponse,
    status_code=status.HTTP_201_CREATED
)
def create_workshop(
    data: WorkshopCreate,
    db: Session = Depends(get_db)
):

    if data.maximum_participants <= 0:
        raise HTTPException(
            status_code=400,
            detail="Số lượng người tham gia phải lớn hơn 0"
        )

    if data.status not in ["OPEN", "CLOSED", "CANCELLED"]:
        raise HTTPException(
            status_code=400,
            detail="Trạng thái workshop không hợp lệ"
        )

    workshop = Workshop(
        title=data.title,
        description=data.description,
        maximum_participants=data.maximum_participants,
        status=data.status,
        start_time=data.start_time
    )

    db.add(workshop)
    db.commit()
    db.refresh(workshop)

    return workshop


# ==================================================
# 4. LẤY DANH SÁCH WORKSHOP
# GET /workshops
# ==================================================

@app.get(
    "/workshops",
    response_model=list[WorkshopResponse]
)
def get_workshops(
    db: Session = Depends(get_db)
):

    return db.query(Workshop).all()


# ==================================================
# 5. CHI TIẾT WORKSHOP
# GET /workshops/{id}
# ==================================================

@app.get(
    "/workshops/{id}",
    response_model=WorkshopResponse
)
def get_workshop(
    id: int,
    db: Session = Depends(get_db)
):

    workshop = (
        db.query(Workshop)
        .filter(Workshop.id == id)
        .first()
    )

    if workshop is None:
        raise HTTPException(
            status_code=404,
            detail="Workshop không tồn tại"
        )

    return workshop


# ==================================================
# 6. ĐĂNG KÝ WORKSHOP
# POST /registrations
# ==================================================

@app.post(
    "/registrations",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_registration(
    data: RegistrationCreate,
    db: Session = Depends(get_db)
):

    # ----------------------------------------------
    # 1. Kiểm tra sinh viên tồn tại
    # ----------------------------------------------

    student = (
        db.query(Student)
        .filter(Student.id == data.student_id)
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Sinh viên không tồn tại"
        )

    # ----------------------------------------------
    # 2. Kiểm tra sinh viên ACTIVE
    # ----------------------------------------------

    if student.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Sinh viên không còn hoạt động"
        )

    # ----------------------------------------------
    # 3. Kiểm tra workshop tồn tại
    # ----------------------------------------------

    workshop = (
        db.query(Workshop)
        .filter(Workshop.id == data.workshop_id)
        .first()
    )

    if workshop is None:
        raise HTTPException(
            status_code=404,
            detail="Workshop không tồn tại"
        )

    # ----------------------------------------------
    # 4. Workshop phải OPEN
    # ----------------------------------------------

    if workshop.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="Workshop đã đóng hoặc bị hủy"
        )

    # ----------------------------------------------
    # 5. Workshop chưa bắt đầu
    # ----------------------------------------------

    if workshop.start_time <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Workshop đã bắt đầu, không thể đăng ký"
        )

    # ----------------------------------------------
    # 6. Kiểm tra đăng ký trùng
    # ----------------------------------------------

    existing = (
        db.query(Registration)
        .filter(
            Registration.student_id == data.student_id,
            Registration.workshop_id == data.workshop_id,
            Registration.status == "REGISTERED"
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Sinh viên đã đăng ký workshop này"
        )

    # ----------------------------------------------
    # 7. Đếm số người đã đăng ký
    # ----------------------------------------------

    current_count = (
        db.query(Registration)
        .filter(
            Registration.workshop_id == data.workshop_id,
            Registration.status == "REGISTERED"
        )
        .count()
    )

    # ----------------------------------------------
    # 8. Kiểm tra số lượng tối đa
    # ----------------------------------------------

    if current_count >= workshop.maximum_participants:
        raise HTTPException(
            status_code=400,
            detail="Workshop đã đủ số lượng người tham gia"
        )

    # ----------------------------------------------
    # 9. Tạo Registration
    # ----------------------------------------------

    registration = Registration(
        student_id=data.student_id,
        workshop_id=data.workshop_id,
        registered_at=datetime.now(),
        status="REGISTERED"
    )

    db.add(registration)
    db.commit()
    db.refresh(registration)

    return registration


# ==================================================
# 7. WORKSHOP CỦA SINH VIÊN
# GET /students/{id}/workshops
# ==================================================

@app.get("/students/{id}/workshops")
def get_student_workshops(
    id: int,
    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(Student.id == id)
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Sinh viên không tồn tại"
        )

    registrations = (
        db.query(Registration)
        .filter(
            Registration.student_id == id,
            Registration.status == "REGISTERED"
        )
        .all()
    )

    workshops = []

    for registration in registrations:

        workshop = (
            db.query(Workshop)
            .filter(
                Workshop.id == registration.workshop_id
            )
            .first()
        )

        if workshop:
            workshops.append({
                "id": workshop.id,
                "title": workshop.title,
                "description": workshop.description,
                "start_time": workshop.start_time,
                "status": workshop.status
            })

    return {
        "student_id": student.id,
        "full_name": student.full_name,
        "workshops": workshops
    }


# ==================================================
# 8. SINH VIÊN CỦA WORKSHOP
# GET /workshops/{id}/students
# ==================================================

@app.get("/workshops/{id}/students")
def get_workshop_students(
    id: int,
    db: Session = Depends(get_db)
):

    workshop = (
        db.query(Workshop)
        .filter(Workshop.id == id)
        .first()
    )

    if workshop is None:
        raise HTTPException(
            status_code=404,
            detail="Workshop không tồn tại"
        )

    registrations = (
        db.query(Registration)
        .filter(
            Registration.workshop_id == id,
            Registration.status == "REGISTERED"
        )
        .all()
    )

    students = []

    for registration in registrations:

        student = (
            db.query(Student)
            .filter(
                Student.id == registration.student_id
            )
            .first()
        )

        if student:
            students.append({
                "id": student.id,
                "student_code": student.student_code,
                "full_name": student.full_name,
                "email": student.email
            })

    return {
        "workshop_id": workshop.id,
        "title": workshop.title,
        "students": students
    }


# ==================================================
# 9. HỦY ĐĂNG KÝ
# DELETE /registrations/{id}
# ==================================================

@app.delete("/registrations/{id}")
def cancel_registration(
    id: int,
    db: Session = Depends(get_db)
):

    registration = (
        db.query(Registration)
        .filter(Registration.id == id)
        .first()
    )

    if registration is None:
        raise HTTPException(
            status_code=404,
            detail="Đăng ký không tồn tại"
        )

    if registration.status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Đăng ký đã được hủy trước đó"
        )

    # Chọn phương án đổi trạng thái
    # thay vì xóa dữ liệu
    registration.status = "CANCELLED"

    db.commit()

    return {
        "message": "Hủy đăng ký thành công",
        "registration_id": registration.id
    }


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():

    return {
        "message": "API đang hoạt động"
    }
