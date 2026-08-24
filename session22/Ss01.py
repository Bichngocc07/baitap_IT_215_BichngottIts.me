import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session


# =========================
# LOAD ENV
# =========================

load_dotenv()

SECRET_KEY = os.getenv("MEDCARE_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "MEDCARE_SECRET_KEY chưa được cấu hình trong .env"
    )

ALGORITHM = "HS256"


# =========================
# DATABASE
# =========================

DATABASE_URL = "sqlite:///./medcare.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class MedicalStaff(Base):
    __tablename__ = "medical_staff"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False
    )


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# FASTAPI
# =========================

app = FastAPI(
    title="MedCare E-Prescription API"
)


# =========================
# SCHEMA
# =========================

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class PrescriptionRequest(BaseModel):
    patient_name: str
    medicine: str
    quantity: int


# =========================
# JWT SECURITY
# =========================

security = HTTPBearer()


# =========================
# REGISTER
# =========================

@app.post("/api/v1/medical/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    # Chỉ cho phép doctor hoặc pharmacist
    if request.role not in ["doctor", "pharmacist"]:
        raise HTTPException(
            status_code=400,
            detail="Role phải là doctor hoặc pharmacist"
        )

    # Kiểm tra username
    existing_user = (
        db.query(MedicalStaff)
        .filter(
            MedicalStaff.username == request.username
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username đã tồn tại"
        )

    # Hash password bằng bcrypt
    hashed_password = bcrypt.hashpw(
        request.password.encode("utf-8"),
        bcrypt.gensalt()
    )

    # Tạo nhân viên
    new_user = MedicalStaff(
        username=request.username,
        hashed_password=hashed_password.decode("utf-8"),
        role=request.role
    )

    # Lưu database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "statusCode": 201,
        "message": "Đăng ký tài khoản thành công!",
        "data": {
            "id": new_user.id,
            "username": new_user.username,
            "role": new_user.role
        }
    }


# =========================
# LOGIN
# =========================

@app.post("/api/v1/medical/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    # Tìm user theo username
    user = (
        db.query(MedicalStaff)
        .filter(
            MedicalStaff.username == request.username
        )
        .first()
    )

    # Không tìm thấy user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không chính xác"
        )

    # Kiểm tra password
    password_valid = bcrypt.checkpw(
        request.password.encode("utf-8"),
        user.hashed_password.encode("utf-8")
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không chính xác"
        )

    # =========================
    # TẠO JWT
    # =========================

    now = datetime.now(timezone.utc)

    # Token hết hạn sau 20 phút
    expiration = now + timedelta(minutes=20)

    payload = {
        "sub": user.username,
        "role": user.role,
        "iat": int(now.timestamp()),
        "exp": int(expiration.timestamp())
    }

    access_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "statusCode": 200,
        "message": "Đăng nhập thành công!",
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# GET CURRENT USER
# =========================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        # Giải mã và kiểm tra JWT
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        role = payload.get("role")

        if not username or not role:
            raise HTTPException(
                status_code=401,
                detail="Token không hợp lệ"
            )

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token đã hết hạn"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ"
        )

    # Tìm user trong database
    user = (
        db.query(MedicalStaff)
        .filter(
            MedicalStaff.username == username
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ"
        )

    return user


# =========================
# TẠO ĐƠN THUỐC
# DOCTOR ONLY
# =========================

@app.post("/api/v1/prescriptions")
def create_prescription(
    request: PrescriptionRequest,
    user: MedicalStaff = Depends(get_current_user)
):

    # Kiểm tra quyền
    if user.role != "doctor":
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền tạo đơn thuốc"
        )

    return {
        "statusCode": 201,
        "message": "Tạo đơn thuốc thành công!",
        "data": {
            "doctor": user.username,
            "patient_name": request.patient_name,
            "medicine": request.medicine,
            "quantity": request.quantity
        }
    }


# =========================
# XEM ĐƠN THUỐC
# DOCTOR + PHARMACIST
# =========================

@app.get("/api/v1/prescriptions/view")
def view_prescriptions(
    user: MedicalStaff = Depends(get_current_user)
):

    return {
        "statusCode": 200,
        "message": "Xem đơn thuốc thành công!",
        "data": {
            "username": user.username,
            "role": user.role
        }
    }