from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate

# 1. Lấy toàn bộ sản phẩm
def get_all_products(db: Session):
    return db.query(Product).all()


# 2. Lấy chi tiết sản phẩm theo ID (Có sửa lỗi .first() để trả về dữ liệu thực tế)
def get_product_by_id(product_id: int, db: Session):
    return db.query(Product).filter(Product.id == product_id).first()


# 3. Thêm sản phẩm mới (Có db.commit và db.refresh)
def create_product(product_in: ProductCreate, db: Session):
    new_product = Product(
        sku=product_in.sku,
        name=product_in.name,
        price=product_in.price
    )
    db.add(new_product)
    db.commit()          # Lưu vĩnh viễn
    db.refresh(new_product) # Đồng bộ lấy ID tự tăng
    return new_product


# 4. Cập nhật thông tin sản phẩm (Sửa lỗi "updata")
def update_product(product_id: int, product_in: ProductCreate, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        return None
        
    product.name = product_in.name
    product.price = product_in.price
    
    db.commit()
    db.refresh(product)
    return product


# 5. Xóa sản phẩm
def delete_product(product_id: int, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        return None
        
    db.delete(product)
    db.commit()
    return product