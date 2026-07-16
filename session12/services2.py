from sqlalchemy.orm import Session
from models import ProductModel, CustomerModel
from schemas import ProductCreate, CustomerUpdate

# =================================================================
# XỬ LÝ PHÂN HỆ SẢN PHẨM (Bài 1)
# =================================================================

def create_product_service(product_in: ProductCreate, db: Session):
    # Kiểm tra xem SKU đã tồn tại chưa
    exists = db.query(ProductModel).filter(ProductModel.sku == product_in.sku).first()
    if exists:
        return None  # Trả về None báo hiệu trùng mã SKU
        
    new_product = ProductModel(
        sku=product_in.sku,
        name=product_in.name,
        price=product_in.price
    )
    db.add(new_product)
    db.commit()          # SỬA LỖI 1: Thực thi lưu xuống đĩa cứng
    db.refresh(new_product) # Đồng bộ lấy ID tự tăng
    return new_product


# =================================================================
# XỬ LÝ PHÂN HỆ KHÁCH HÀNG (Bài 2)
# =================================================================

def update_customer_service(customer_id: int, customer_in: CustomerUpdate, db: Session):
    # Tìm kiếm khách hàng theo ID
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    
    if customer is None:
        return None  # Trả về None báo hiệu không tìm thấy
        
    # Cập nhật thông tin mới
    customer.full_name = customer_in.full_name
    customer.phone = customer_in.phone
    customer.address = customer_in.address
    
    db.commit()          # SỬA LỖI: Commit để lưu thay đổi thực tế vào MySQL
    db.refresh(customer) # SỬA LỖI: Đồng bộ trạng thái mới nhất của Object
    return customer