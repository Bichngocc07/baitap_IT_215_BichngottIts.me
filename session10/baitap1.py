from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel

# 1. KHỞI TẠO FASTAPI
app = FastAPI(title="Product Management API")

# 2. CẤU HÌNH CƠ SỞ DỮ LIỆU (MYSQL)
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/connect_db"
engine = create_engine(
    DATABASE_URL, 
    pool_recycle=3600, 
    pool_pre_ping=True
)

# 3. KHỞI TẠO PHIÊN LÀM VIỆC (SESSION) VÀ BASE MODEL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. DEPENDENCY: QUẢN LÝ KẾT NỐI DB AN TOÀN (TRÁNH RÒ RỈ KẾT NỐI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Luôn đóng kết nối sau khi xử lý xong API

# 5. ĐỊNH NGHĨA MODEL DATABASE (SQLAlchemy)
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Sửa từ Float thành String chuẩn xác
    price = Column(Float, nullable=False)

# Tự động tạo bảng trong MySQL nếu chưa tồn tại
Base.metadata.create_all(bind=engine)


# 6. ĐỊNH NGHĨA SCHEMAS (Pydantic Models để nhận/validate dữ liệu đầu vào)
class ProductCreate(BaseModel):
    name: str
    price: float  # Nhận kiểu số thực để khớp với cấu trúc Database


# =================================================================
# VII. HỆ THỐNG ENDPOINT APIs
# =================================================================

# API 1: Kiểm tra trạng thái hệ thống
@app.get("/")
def home():
    return {
        "message": "API đang hoạt động ổn định"
    }


# API 2: Lấy danh sách toàn bộ sản phẩm
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return {
        "message": "Lấy danh sách sản phẩm thành công",
        "data": products
    }


# API 3: Lấy chi tiết một sản phẩm theo ID
@app.get("/products/{product_id}")
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    # Tìm kiếm phần tử đầu tiên khớp điều kiện ID
    product = db.query(Product).filter(Product.id == product_id).first()
    
    # Bẫy lỗi nếu không tìm thấy ID sản phẩm
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy sản phẩm yêu cầu"
        )
        
    return {
        "message": "Lấy chi tiết sản phẩm thành công",
        "data": product
    }


# API 4: Thêm sản phẩm mới (Chuẩn hóa mã trạng thái thành 201 Created)
@app.post("/products", status_code=status.HTTP_201_CREATED)
def add_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    # 1. Ánh xạ dữ liệu từ Schema đầu vào sang Model SQLAlchemy
    new_product = Product(
        name=product_in.name,
        price=product_in.price
    )
    
    # 2. Thực hiện transaction ghi dữ liệu xuống database thực tế
    db.add(new_product)
    db.commit()          # Xác nhận lưu thay đổi vĩnh viễn
    db.refresh(new_product)  # Đồng bộ lại thực thể để lấy ID tự tăng từ DB
    
    return {
        "message": "Thêm sản phẩm thành công",
        "data": new_product
    }