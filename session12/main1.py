import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from schemas import ProductCreate
import services  # Import file services

# Đồng bộ tạo bảng MySQL khi chạy chương trình
Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API Standard")

# Hàm bổ trợ bọc dữ liệu trả về 6 trường chuẩn hóa
def make_response(status_code: int, message: str, data=None, error=None, path: str = ""):
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

# API: Trạng thái hệ thống
@app.get("/")
def home(request: Request):
    return make_response(status.HTTP_200_OK, "API đang chạy", path=request.url.path)


# API: Lấy danh sách sản phẩm
@app.get("/products")
def get_all_products_api(request: Request, db: Session = Depends(get_db)):
    products = services.get_all_products(db)
    return make_response(200, "Lấy danh sách sản phẩm thành công", products, path=request.url.path)


# API: Lấy chi tiết sản phẩm
@app.get("/products/{product_id}")
def get_product_detail_api(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = services.get_product_by_id(product_id, db)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail=make_response(404, "Product not found", error="Not Found", path=request.url.path)
        )
    return make_response(200, "Lấy chi tiết sản phẩm thành công", product, path=request.url.path)


# API: Thêm mới sản phẩm (Trạng thái 201 Created)
@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product_api(request: Request, product_in: ProductCreate, db: Session = Depends(get_db)):
    try:
        new_product = services.create_product(product_in, db)
        return make_response(201, "Thêm sản phẩm thành công", new_product, path=request.url.path)
    except Exception as e:
        db.rollback()  # Bảo vệ giao dịch
        raise HTTPException(
            status_code=500,
            detail=make_response(500, "Lỗi hệ thống database", error=str(e), path=request.url.path)
        )


# API: Cập nhật thông tin sản phẩm
@app.put("/products/{product_id}")
def update_product_api(
    product_id: int, 
    product_in: ProductCreate, 
    request: Request, 
    db: Session = Depends(get_db)
):
    updated_product = services.update_product(product_id, product_in, db)
    if updated_product is None:
        raise HTTPException(
            status_code=404,
            detail=make_response(404, "Không tìm thấy sản phẩm cập nhật", error="Not Found", path=request.url.path)
        )
    return make_response(200, "Cập nhật sản phẩm thành công!", updated_product, path=request.url.path)


# API: Xóa sản phẩm
@app.delete("/products/{product_id}")
def delete_product_api(product_id: int, request: Request, db: Session = Depends(get_db)):
    deleted_product = services.delete_product(product_id, db)
    if deleted_product is None:
        raise HTTPException(
            status_code=404,
            detail=make_response(404, "Không tìm thấy sản phẩm để xóa", error="Not Found", path=request.url.path)
        )
    return make_response(200, "Xóa sản phẩm thành công", deleted_product, path=request.url.path)