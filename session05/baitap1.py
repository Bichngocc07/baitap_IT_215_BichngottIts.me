# TEST CASE 1: Thử nghiệm trùng mã sản phẩm "SP001"
# STT: 1
# Dữ liệu gửi lên (Request Body):
# JSON
# {
#   "code": "SP001",
#   "name": "Bàn phím",
#   "price": 500000,
#   "stock": 10
# }
# Kết quả hiện tại: Hệ thống vẫn tạo thành công sản phẩm mới với ID tự tăng. Lúc này trong danh sách hệ thống xuất hiện đồng thời 2 sản phẩm có cùng code = "SP001".
# Kết quả đúng mong muốn: Hệ thống phải chặn lại, ném ra lỗi HTTPException và trả về mã trạng thái HTTP thích hợp (ví dụ: 400 Bad Request) để thông báo rằng mã sản phẩm này đã tồn tại trên hệ thống.
# Lỗi phát hiện: Khuyết thiếu logic kiểm tra trùng lặp code sản phẩm bằng vòng lặp hoặc hàm quét điều kiện trước khi thực hiện phương thức .append().

# TEST CASE 2: Thử nghiệm trùng mã sản phẩm "SP002"
# STT: 2
# Dữ liệu gửi lên (Request Body):
# JSON
# {
#   "code": "SP002",
#   "name": "Tai nghe",
#   "price": 300000,
#   "stock": 5
# }

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Dữ liệu sản phẩm giả lập ban đầu
products = [
    {
        "id": 1,
        "code": "SP001",
        "name": "Laptop Dell",
        "price": 15000000.0,
        "stock": 10
    },
    {
        "id": 2,
        "code": "SP002",
        "name": "Mouse Logitech",
        "price": 350000.0,
        "stock": 50
    }
]

# Định nghĩa Schema cho dữ liệu gửi lên từ Client
class ProductCreate(BaseModel):
    code: str
    name: str
    price: float
    stock: int

# SỬA LỖI: Thêm status_code=201 chuẩn RESTful cho hành động Tạo mới (Created)
@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    
    # 1. Vòng lặp kiểm tra xem mã sản phẩm (code) đã tồn tại trong hệ thống chưa
    for p in products:
        if p["code"] == product.code:
            # Nếu đã tồn tại, lập tức quăng lỗi HTTPException (Mã 400 Bad Request) để chặn lại
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mã sản phẩm '{product.code}' đã tồn tại trong hệ thống."
            )
            
    # 2. Logic tạo sản phẩm mới nếu không bị trùng mã
    new_product = {
        "id": len(products) + 1,
        "code": product.code,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }
    
    # Thêm sản phẩm hợp lệ vào danh sách
    products.append(new_product)
    
    # 3. Trả về thông báo thành công và cấu trúc dữ liệu vừa tạo
    return {
        "message": "Create product successfully",
        "data": new_product
    }