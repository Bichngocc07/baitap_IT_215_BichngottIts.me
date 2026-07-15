import datetime
from typing import Optional, Any
from fastapi import FastAPI, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# =================================================================
# I. CẤU HÌNH DATABASE & SQLALCHEMY
# =================================================================
# Lưu ý: Bạn cần tạo database "connect_db" trong MySQL trước
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/connect_db"

engine = create_engine(
    DATABASE_URL, 
    pool_recycle=3600, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. Model cho Sản phẩm (Bài tập 1)
class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

# 2. Model cho Vị trí đỗ xe (Bài tập 2)
class ParkingSlotModel(Base):
    __tablename__ = "parking_slots"
    id = Column(Integer, primary_key=True, index=True)
    slot_code = Column(String(50), unique=True, nullable=False)
    zone_name = Column(String(255), nullable=False)
    max_weight = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

# Khởi tạo toàn bộ bảng vào MySQL
Base.metadata.create_all(bind=engine)

# =================================================================
# II. ĐỊNH NGHĨA SCHEMAS (PYDANTIC)
# =================================================================

# Schema Sản phẩm
class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=2)
    name: str = Field(..., min_length=2)
    price: float = Field(..., gt=0)

# Schema Bãi đỗ xe
class ParkingSlotCreate(BaseModel):
    slot_code: str = Field(..., min_length=1)
    zone_name: str = Field(..., min_length=3)
    max_weight: int = Field(..., gt=0)

# =================================================================
# III. UTILITIES & DEPENDENCIES
# =================================================================

# Dependency: Quản lý Session an toàn (Tự động đóng kết nối)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper: Hàm đóng gói Response 6 trường quy chuẩn
def unified_response(
    status_code: int, 
    message: str, 
    data: Any = None, 
    error: Any = None, 
    path: str = ""
):
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

# =================================================================
# IV. KHỞI TẠO APP & ENDPOINTS
# =================================================================

app = FastAPI(title="Integrated Management System API")

@app.get("/")
def health_check(request: Request):
    return unified_response(200, "Hệ thống đang hoạt động ổn định", None, None, request.url.path)

# --- 1. PHÂN HỆ QUẢN LÝ SẢN PHẨM ---

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(request: Request, product_in: ProductCreate, db: Session = Depends(get_db)):
    try:
        # Kiểm tra trùng SKU
        exists = db.query(ProductModel).filter(ProductModel.sku == product_in.sku).first()
        if exists:
            return unified_response(400, "Lỗi: SKU đã tồn tại", None, "Bad Request", request.url.path)

        new_product = ProductModel(**product_in.model_dump())
        db.add(new_product)
        db.commit()      # Xác thực lưu trữ (Khắc phục lỗi 1)
        db.refresh(new_product)
        
        return unified_response(201, "Thêm sản phẩm thành công", new_product, None, request.url.path)
    except Exception as e:
        db.rollback()    # Rollback nếu lỗi để bảo vệ dữ liệu
        return unified_response(500, "Lỗi máy chủ nội bộ", None, str(e), request.url.path)

@app.get("/products")
def get_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(ProductModel).all()
    return unified_response(200, "Lấy danh sách sản phẩm thành công", products, None, request.url.path)

# --- 2. PHÂN HỆ QUẢN LÝ BÃI ĐỖ XE ---

@app.post("/parking-slots", status_code=status.HTTP_201_CREATED)
def create_parking_slot(request: Request, slot_in: ParkingSlotCreate, db: Session = Depends(get_db)):
    try:
        # Kiểm tra trùng mã vị trí
        exists = db.query(ParkingSlotModel).filter(ParkingSlotModel.slot_code == slot_in.slot_code).first()
        if exists:
            return unified_response(400, "Lỗi: Mã vị trí đỗ xe đã tồn tại", None, "Bad Request", request.url.path)

        new_slot = ParkingSlotModel(**slot_in.model_dump())
        db.add(new_slot)
        db.commit()
        db.refresh(new_slot)
        
        return unified_response(201, "Thêm vị trí đỗ xe thành công", new_slot, None, request.url.path)
    except Exception as e:
        db.rollback()
        return unified_response(500, "Lỗi hệ thống database", None, str(e), request.url.path)

@app.get("/parking-slots")
def get_all_slots(request: Request, db: Session = Depends(get_db)):
    slots = db.query(ParkingSlotModel).all()
    return unified_response(200, "Lấy danh sách vị trí đỗ thành công", slots, None, request.url.path)

@app.get("/parking-slots/{slot_id}")
def get_slot_detail(slot_id: int, request: Request, db: Session = Depends(get_db)):
    slot = db.query(ParkingSlotModel).filter(ParkingSlotModel.id == slot_id).first()
    
    if not slot:
        raise HTTPException(
            status_code=404,
            detail=unified_response(404, "Parking slot not found", None, "Not Found", request.url.path)
        )
        
    return unified_response(200, "Lấy chi tiết vị trí đỗ thành công", slot, None, request.url.path)