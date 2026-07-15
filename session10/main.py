from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
# 1. Khởi tạo FastAPI
app = FastAPI()

# 2. Cấu hình CSDL (Lưu ý: Viết thường mysql+pymysql)
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/connect_db"
engine = create_engine(DATABASE_URL)

# 3. Tạo SessionLocal (Đặt tên này để tránh trùng với hàm sessionmaker)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Sửa lại hàm get_db để tạo phiên làm việc đúng cách
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. Định nghĩa bảng (Phải kế thừa Base)
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False) # Sửa Float -> String
    price = Column(Float, nullable=False)

# 6. Viết các API
@app.get("/")
def home():
    return {"message": "API đang chạy"}

@app.get("/products")
def get_all_product(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return {
        "message": "Lấy danh sách sản phẩm thành công", 
        "data": products
    }
#Lấy chi tiết 1sản phẩm
@app.get("/products/{product_id}")
def get_product_detail(product_id:int,db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).filter()
    if product is None:
        raise HTTPException(status_code=404, detai="không tìm thấy sản phẩm nào")
    return{"message":"lấy chi tiết sản phẩm thành công","data":product}
#API THÊM SẢN PHẨM
class ProductCreate:
    name: str
    price: str
@app.post("/products")
def add_product(product:ProductCreate):
    print("sản phẩm vừa thêm vào",product)
    new_product = {
        "name": product.name,
        "price": product.price
    }
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return{
        "message": "Thêm sản phẩm thành công",
        "data": new_product
    }
#API XÓA SẢN PHẨM
@app.delete("/products/{product_id}")
def delete_product(product_id:int, db:Session = Depends(get_db))
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code= 404,
            detail="Không tìm thấy sản phẩm để xóa"
        )
    db.delete(product)
    db.commit()
    return{
        "message": "Xóa sản phẩm thành công",
        "data": product
    }
#API CẬP NHẬT SẢN PHẨM
@app.put("/products/{product_id}")
def updata_product(product_id:int,updata_product:ProductCreate,
                   db:Session = Depends(get_db)):
    product  = db.query(Product).filter(Product.id == product_id).filter()
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="không tìm thấy sản phẩm cập nhật"
        )
    product.name=updata_product.name
    product.price=updata_product.price
    db.commit()
    db.refresh(product)
    return{
        "message": "Cập nhật sản phẩm thành công!",
        "data": product
    }