# Phần 1: Phân tích lỗi
# Khi gọi GET /products/1, vì sao API trả về 404 Not Found?
# Vì trong cấu hình route hiện tại, backend khai báo đường dẫn thô là "/products/product_id". FastAPI hiểu đây là một đường dẫn cố định (static path).
# Khi bạn gọi /products/1, FastAPI so sánh chuỗi tĩnh "/products/1" với chuỗi tĩnh "/products/product_id". Thấy không trùng khớp và hệ thống không có route nào xử lý /products/1, dẫn đến trả về lỗi HTTP 404 Not Found.
# Dòng code nào đang khai báo sai Path Parameter?
# Dòng code số 10 trong ảnh: @app.get("/products/product_id") đang khai báo sai.
# Để biến một định danh trên URL thành Path Parameter, biến đó bắt buộc phải được bao bọc bởi cặp dấu ngoặc nhọn {}. Do đó, viết đúng phải là @app.get("/products/{product_id}").
# Vì sao /products/product_id không phải là Path Parameter?
# FastAPI dựa hoàn toàn vào cú pháp cấu trúc chuỗi định tuyến (routing syntax). Do thiếu cặp dấu ngoặc nhọn {} bao quanh product_id, FastAPI xem toàn bộ cụm từ product_id chỉ là một đoạn text tĩnh trên URL tương tự như chữ products.
# Endpoint đúng cần sửa thành gì?
# Đường dẫn đúng cần sửa ở decorator là: @app.get("/products/{product_id}")
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Danh sách sản phẩm (Mock Data)
products = [
    {"id": 1, "name": "Laptop Dell", "price": 15000000},
    {"id": 2, "name": "Chuột Logitech", "price": 350000},
    {"id": 3, "name": "Bàn phím cơ", "price": 1200000}
]

# SỬA LỖI: Thêm cặp dấu {} bao quanh product_id để chuyển thành Path Parameter
@app.get("/products/{product_id}")
def get_product_detail(product_id: int): # FastAPI tự động ép kiểu dữ liệu sang int và validate URL
    # Duyệt danh sách tìm sản phẩm khớp ID
    for product in products:
        if product["id"] == product_id:
            return product # Trả về trực tiếp thông tin sản phẩm (JSON Object) nếu tìm thấy

    # Xử lý trường hợp không tìm thấy: Trả về thông báo rõ ràng
    # (Có thể dùng cấu trúc dict thường hoặc dùng HTTPException của FastAPI để chuẩn hóa)
    return {
        "message": "Không tìm thấy sản phẩm"
    }