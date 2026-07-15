from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# =================================================================
# I. CẤU HÌNH DATABASE & ENGINE SQLALCHEMY
# =================================================================
# Đảm bảo bạn đã tạo database mang tên "ecommerce_db" trong MySQL trước khi khởi chạy
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"

engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,  # Tự động dọn dẹp các kết nối cũ sau 1 giờ
    pool_pre_ping=True  # Kiểm tra trạng thái kết nối trước khi thực thi truy vấn để tránh rò rỉ
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =================================================================
# II. ĐỊNH NGHĨA CÁC MÔ HÌNH DATABASE (SQLALCHEMY MODELS)
# =================================================================

# Phân hệ 1: Bảng Sản phẩm (Hình 1)
class ProductModel(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

# Phân hệ 2: Bảng Mã vận đơn (Hình 2)
class ShipmentModel(Base):
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="PREPARING")

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

# Schema dữ liệu cho Mã vận đơn
class ShipmentCreate(BaseModel):
    tracking_number: str = Field(..., min_length=1, description="Mã vận đơn không được để trống")

# =================================================================
# IV. UTILITIES & DEPENDENCIES
# =================================================================

# Dependency Injection: Đảm bảo kết nối được đóng và giải phóng an toàn (Tránh Connection Leak)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Khắc phục lỗi 2: Giải phóng kết nối vật lý về Pool ngay khi kết thúc request

# =================================================================
# V. HỆ THỐNG APIs ENDPOINTS
# =================================================================

app = FastAPI(title="Integrated E-Commerce & Shipping API System", version="1.0.0")

@app.get("/")
def home():
    return {"message": "API đang hoạt động ổn định"}


# ----------------- PHÂN HỆ 1: QUẢN LÝ SẢN PHẨM (HÌNH 1) -----------------

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    # Kiểm tra trùng lặp mã SKU
    exists = db.query(ProductModel).filter(ProductModel.sku == product_in.sku).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã sản phẩm (SKU) đã tồn tại trên hệ thống"
        )
    
    try:
        new_product = ProductModel(
            sku=product_in.sku,
            name=product_in.name,
            price=product_in.price
        )
        db.add(new_product)
        db.commit()          # Khắc phục lỗi 1: Xác nhận và lưu trữ dữ liệu vĩnh viễn xuống MySQL
        db.refresh(new_product)
        
        return {
            "message": "Product created successfully",
            "data": {
                "id": new_product.id,
                "sku": new_product.sku,
                "name": new_product.name,
                "price": new_product.price
            }
        }
    except Exception as e:
        db.rollback()        # Hoàn tác giao dịch nếu xảy ra sự cố đột xuất
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi lưu trữ dữ liệu sản phẩm: {str(e)}"
        )


# ----- PHÂN HỆ 2: QUẢN LÝ MÃ VẬN ĐƠN SHIPPING (HÌNH 2) -----

# Chức năng 1: Đăng ký mã vận đơn mới (POST /shipments)
@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(shipment_in: ShipmentCreate, db: Session = Depends(get_db)):
    # 1. Sử dụng câu lệnh db.query(...).filter(...).first() để kiểm tra trùng lặp mã vận đơn
    existing_shipment = db.query(ShipmentModel).filter(
        ShipmentModel.tracking_number == shipment_in.tracking_number
    ).first()
    
    # Nếu đã tồn tại, lập tức quăng lỗi 400 Bad Request kèm thông báo quy định
    if existing_shipment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã vận đơn này đã được khởi tạo trước đó"
        )
        
    try:
        # 2. Tạo đối tượng model mới
        new_shipment = ShipmentModel(
            tracking_number=shipment_in.tracking_number,
            status="PREPARING"  # Trạng thái mặc định ban đầu
        )
        # 3. Triển khai thao tác INSERT bằng add() và commit()
        db.add(new_shipment)
        db.commit()          # Đảm bảo lưu dữ liệu vĩnh viễn
        db.refresh(new_shipment)
        
        return {
            "message": "Đăng ký mã vận đơn thành công",
            "data": {
                "id": new_shipment.id,
                "tracking_number": new_shipment.tracking_number,
                "status": new_shipment.status
            }
        }
    except Exception as e:
        db.rollback()        # Bảo vệ toàn vẹn dữ liệu tránh xung đột/nghẽn mạng đột ngột
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi khởi tạo mã vận đơn: {str(e)}"
        )


# Chức năng 2: Lấy danh sách tất cả mã vận đơn (GET /shipments)
@app.get("/shipments", status_code=status.HTTP_200_OK)
def get_all_shipments(db: Session = Depends(get_db)):
    # Sử dụng lệnh truy vấn .all() để lấy toàn bộ danh sách dữ liệu từ database
    shipments = db.query(ShipmentModel).all()
    
    shipments_list = [
        {
            "id": s.id,
            "tracking_number": s.tracking_number,
            "status": s.status
        } for s in shipments
    ]
    
    return {
        "message": "Lấy danh sách mã vận đơn thành công",
        "data": shipments_list
    }