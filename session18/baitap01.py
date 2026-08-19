from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
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


# ==========================================
# DATABASE
# ==========================================

DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/course_registration_db"

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


# ==========================================
# MODEL STUDENT
# ==========================================

class Student(Base):
    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="student"
    )


# ==========================================
# MODEL COURSE
# ==========================================

class Course(Base):
    __tablename__ = "courses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    max_students = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="course"
    )


# ==========================================
# MODEL ENROLLMENT
# ==========================================

class Enrollment(Base):
    __tablename__ = "enrollments"

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

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    enrolled_at = Column(
        DateTime,
        nullable=False
    )

    student = relationship(
        "Student",
        back_populates="enrollments"
    )

    course = relationship(
        "Course",
        back_populates="enrollments"
    )

    # Không cho đăng ký trùng
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_id",
            name="unique_student_course"
        ),
    )


# ==========================================
# TẠO DATABASE TABLE
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# PYDANTIC SCHEMA
# ==========================================

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    id: int
    name: str


class StudentCoursesResponse(BaseModel):
    student_id: int
    full_name: str
    courses: list[CourseResponse]


# ==========================================
# FASTAPI
# ==========================================

app = FastAPI(
    title="Course Registration API",
    description="API đăng ký khóa học cho sinh viên",
    version="1.0.0"
)


# ==========================================
# API ĐĂNG KÝ KHÓA HỌC
# ==========================================

@app.post(
    "/enrollments",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_enrollment(
    data: EnrollmentCreate,
    db: Session = Depends(get_db)
):

    # 1. Kiểm tra sinh viên
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

    # 2. Kiểm tra khóa học
    course = (
        db.query(Course)
        .filter(Course.id == data.course_id)
        .first()
    )

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Khóa học không tồn tại"
        )

    # 3. Kiểm tra sinh viên ACTIVE
    if student.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Sinh viên không ở trạng thái ACTIVE"
        )

    # 4. Kiểm tra khóa học OPEN
    if course.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="Khóa học không ở trạng thái OPEN"
        )

    # 5. Kiểm tra đăng ký trùng
    existing = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == data.student_id,
            Enrollment.course_id == data.course_id
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Sinh viên đã đăng ký khóa học này"
        )

    # 6. Đếm số lượng sinh viên đã đăng ký
    current_count = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == data.course_id
        )
        .count()
    )

    # 7. Kiểm tra max_students
    if current_count >= course.max_students:
        raise HTTPException(
            status_code=400,
            detail="Khóa học đã đủ số lượng sinh viên"
        )

    # 8. Tạo Enrollment
    enrollment = Enrollment(
        student_id=data.student_id,
        course_id=data.course_id,
        enrolled_at=datetime.now()
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment


# ==========================================
# API XEM KHÓA HỌC CỦA SINH VIÊN
# ==========================================

@app.get(
    "/students/{student_id}/courses",
    response_model=StudentCoursesResponse
)
def get_student_courses(
    student_id: int,
    db: Session = Depends(get_db)
):

    # Kiểm tra sinh viên
    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Sinh viên không tồn tại"
        )

    # Lấy các khóa học sinh viên đã đăng ký
    courses = (
        db.query(Course)
        .join(
            Enrollment,
            Course.id == Enrollment.course_id
        )
        .filter(
            Enrollment.student_id == student_id
        )
        .all()
    )

    return {
        "student_id": student.id,
        "full_name": student.full_name,
        "courses": courses
    }


# ==========================================
# API TEST
# ==========================================

@app.get("/")
def root():
    return {
        "message": "API đang hoạt động"
    }
