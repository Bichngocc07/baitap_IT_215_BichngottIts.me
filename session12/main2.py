from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from schemas import ProductCreate, CustomerUpdate
import services  # Import tầng nghiệp vụ

# Tự động đồng bộ và khởi tạo bảng MySQL nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Integrated Enterprise Service API")

# --- API 1: Tạo mới sản phẩm (Bài 1) ---
@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product_api(product_in: ProductCreate, db: Session = Depends(get_db)):
    new_product = services.create_product_service(product_in, db)
    
    if new_product is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã sản phẩm (SKU) đã tồn tại trên hệ thống"
        )
        
    return {
        "message": "Product prepared successfully",
        "data": {
            "sku": new_product.sku,
            "name": new_product.name
        }
    }


# --- API 2: Cập nhật thông tin khách hàng (Bài 2) ---
@app.put("/customers/{customer_id}", status_code=status.HTTP_200_OK)
def update_customer_api(
    customer_id: int, 
    customer_update: CustomerUpdate, 
    db: Session = Depends(get_db)
):
    updated_customer = services.update_customer_service(customer_id, customer_update, db)
    
    # Bẫy lỗi: Trả về lỗi 404 nếu không tìm thấy ID khách hàng
    if updated_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
        
    return {
        "message": "Customer updated successfully",
        "data": {
            "id": updated_customer.id,
            "full_name": updated_customer.full_name,
            "phone": updated_customer.phone,
            "address": updated_customer.address
        }
    }