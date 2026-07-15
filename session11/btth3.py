import datetime
from typing import Optional, Any
from fastapi import FastAPI, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Double
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# =================================================================
# I. CẤU HÌNH DATABASE & ENGINE SQLALCHEMY
# =================================================================
# Đảm bảo bạn đã tạo database mang tên "connect_db" trong MySQL trước khi khởi chạy
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/connect_db"

engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,  # Tự động dọn dẹp các kết nối cũ sau 1 giờ
    pool_pre_ping=True  # Kiểm tra trạng thái kết nối trước khi thực thi truy vấn
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =================================================================
# II. ĐỊNH NGHĨA CÁC MÔ HÌNH DATABASE (SQLALCHEMY MODELS)
# =================================================================

# Phân hệ 1: Bảng Sản phẩm (Hình 1)
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

# Phân hệ 2: Bảng Gói thiết bị nhà thông minh (Hình 2)
class SmartHomePlan(Base):
    __tablename__ = "smart_home_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_code = Column(String(50), unique=True, nullable=False)
    plan_name = Column(String(255), nullable=False)
    device_quantity = Column(Integer, nullable=False)
    price = Column(Double, nullable=False)

# Tự động đồng bộ và tạo bảng vật lý trong MySQL nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

# =================================================================
# III. ĐỊNH NGHĨA CÁC SCHEMAS ĐẦU VÀO (PYDANTIC VALIDATION)
# =================================================================

# Schema dữ liệu cho Sản phẩm
class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, description="Mã sản phẩm không được để trống")
    name: str = Field(..., min_length=1, description="Tên sản phẩm không được để trống")
    price: float = Field(..., gt=0, description="Giá sản phẩm phải lớn hơn 0")

# Schema dữ liệu cho Gói thiết bị nhà thông minh
class SmartHomePlanCreate(BaseModel):
    plan_code: str = Field(..., min_length=1, description="Mã gói thiết bị không được để trống")
    plan_name: str = Field(..., min_length=1, description="Tên gói thiết bị không được để trống")
    device_quantity: int = Field(..., gt=0, description="Số lượng thiết bị đi kèm phải là số nguyên lớn hơn 0")
    price: float = Field(..., gt=0, description="Đơn giá gói sản phẩm phải là kiểu số thực lớn hơn 0")

# =================================================================
# IV. UTILITIES & DEPENDENCIES
# =================================================================

# Dependency Injection: Đảm bảo kết nối được đóng và giải phóng an toàn (Tránh Connection Leak)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper: Sinh cấu trúc phản hồi chuẩn hóa 6 trường bắt buộc
def make_unified_response(
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
# V. HỆ THỐNG APIs ENDPOINTS
# =================================================================

app = FastAPI(title="Integrated Enterprise API System", version="1.0.0")

# ----------------- PHÂN HỆ 1: QUẢN LÝ SẢN PHẨM (HÌNH 1) -----------------

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(request: Request, product_in: ProductCreate, db: Session = Depends(get_db)):
    # Kiểm tra trùng lặp mã SKU
    exists = db.query(Product).filter(Product.sku == product_in.sku).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=make_unified_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Product SKU already exists",
                error="Bad Request",
                path=request.url.path
            )
        )
    
    try:
        new_product = Product(
            sku=product_in.sku,
            name=product_in.name,
            price=product_in.price
        )
        db.add(new_product)
        db.commit()          # Xác thực và lưu trữ dữ liệu vĩnh viễn xuống MySQL
        db.refresh(new_product)
        
        product_data = {
            "id": new_product.id,
            "sku": new_product.sku,
            "name": new_product.name,
            "price": new_product.price
        }
        return make_unified_response(
            status_code=status.HTTP_201_CREATED,
            message="Thêm sản phẩm thành công",
            data=product_data,
            path=request.url.path
        )
    except Exception as e:
        db.rollback()        # Hoàn tác giao dịch nếu xảy ra sự cố đột xuất
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=make_unified_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Database transaction error",
                error=str(e),
                path=request.url.path
            )
        )


# ----- PHÂN HỆ 2: QUẢN LÝ GÓI THIẾT BỊ NHÀ THÔNG MINH (HÌNH 2) -----

# API 1: Thêm gói thiết bị mới
@app.post("/smart-home-plans", status_code=status.HTTP_201_CREATED)
def create_smart_home_plan(request: Request, plan_in: SmartHomePlanCreate, db: Session = Depends(get_db)):
    # Kiểm tra trùng lặp mã gói thiết bị (plan_code)
    exists = db.query(SmartHomePlan).filter(SmartHomePlan.plan_code == plan_in.plan_code).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=make_unified_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Plan code already exists",
                error="Bad Request",
                path=request.url.path
            )
        )
        
    try:
        new_plan = SmartHomePlan(
            plan_code=plan_in.plan_code,
            plan_name=plan_in.plan_name,
            device_quantity=plan_in.device_quantity,
            price=plan_in.price
        )
        db.add(new_plan)
        db.commit()          # Đồng bộ và ghi nhận trạng thái giao dịch
        db.refresh(new_plan)
        
        plan_data = {
            "id": new_plan.id,
            "plan_code": new_plan.plan_code,
            "plan_name": new_plan.plan_name,
            "device_quantity": new_plan.device_quantity,
            "price": new_plan.price
        }
        return make_unified_response(
            status_code=status.HTTP_201_CREATED,
            message="Thêm gói thiết bị mới thành công",
            data=plan_data,
            path=request.url.path
        )
    except Exception as e:
        db.rollback()        # Bảo vệ toàn vẹn dữ liệu tránh xung đột/nghẽn mạng đột ngột
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=make_unified_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Database processing error",
                error=str(e),
                path=request.url.path
            )
        )

# API 2: Lấy danh sách toàn bộ gói thiết bị
@app.get("/smart-home-plans")
def get_all_smart_home_plans(request: Request, db: Session = Depends(get_db)):
    plans = db.query(SmartHomePlan).all()
    plans_list = [
        {
            "id": p.id,
            "plan_code": p.plan_code,
            "plan_name": p.plan_name,
            "device_quantity": p.device_quantity,
            "price": p.price
        } for p in plans
    ]
    return make_unified_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách thành công",
        data=plans_list,
        path=request.url.path
    )

# API 3: Lấy thông tin chi tiết một gói thiết bị theo ID
@app.get("/smart-home-plans/{plan_id}")
def get_smart_home_plan_detail(plan_id: int, request: Request, db: Session = Depends(get_db)):
    plan = db.query(SmartHomePlan).filter(SmartHomePlan.id == plan_id).first()
    
    # Bẫy lỗi: Trả về lỗi 404 nếu không tìm thấy gói thiết bị theo id
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=make_unified_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Plan not found",
                error="Not Found",
                path=request.url.path
            )
        )
        
    plan_data = {
        "id": plan.id,
        "plan_code": plan.plan_code,
        "plan_name": plan.plan_name,
        "device_quantity": plan.device_quantity,
        "price": plan.price
    }
    return make_unified_response(
        status_code=status.HTTP_200_OK,
        message="Lấy chi tiết gói thiết bị thành công",
        data=plan_data,
        path=request.url.path
    )