# Phần 1: Báo cáo phân tích và thiết kế giải pháp
# 1. Phân tích bài toán (I/O)
# Input API nhận là gì? (Request Body dạng JSON):
# product_id (Kiểu số nguyên int): Mã định danh của sản phẩm muốn mua.
# quantity (Kiểu số nguyên int): Số lượng sản phẩm khách hàng đặt mua.
# Output khi thành công (Mã HTTP 201 Created):
# Trả về thông tin đơn hàng vừa tạo bao gồm: id (tự tăng), product_id, quantity, và tổng tiền total_price.
# Số lượng tồn kho (stock) của sản phẩm trong products_db bị trừ bớt đi đúng bằng số lượng đặt mua.
# Output khi thất bại (Mã HTTP 400 Bad Request):
# Trả về JSON Object thông báo lỗi chi tiết: {"detail": "Thông báo lỗi tương ứng"}.
# 2. Thiết kế các bước xử lý logic (Tuần tự)
# Bước 1: Nhận dữ liệu đơn hàng từ Client gửi lên.
# Bước 2 (Bẫy số lượng không hợp lệ): Kiểm tra xem quantity có $\le 0$ hay không. Nếu có, lập tức raise lỗi "Số lượng mua phải lớn hơn 0".
# Bước 3 (Tìm kiếm sản phẩm): Quét mảng products_db tìm sản phẩm có id == product_id. Nếu quét hết mảng mà không thấy sản phẩm $\rightarrow$ raise lỗi "Sản phẩm không tồn tại".
# Bước 4 (Bẫy vượt quá tồn kho): So sánh quantity người mua gửi lên với stock hiện tại của sản phẩm đó. Nếu quantity > stock $\rightarrow$ raise lỗi "Sản phẩm không đủ số lượng trong kho".
# Bước 5 (Cập nhật dữ liệu & Tạo đơn): Trừ bớt số lượng kho (stock = stock - quantity). Tính tổng tiền. Sinh ID tự tăng rồi dùng phương thức .append() để nạp đơn mới vào mảng orders_db. Trả về kết quả thành công với mã 201.
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# --- 3. DỮ LIỆU GIẢ LẬP BAN ĐẦU ---
products_db = [
    {"id": 101, "name": "Bàn phím cơ", "stock": 5, "price": 1200000.0},
    {"id": 102, "name": "Chuột Gaming", "stock": 2, "price": 600000.0}
]

orders_db = []


# Schema nhận dữ liệu thô đầu vào từ client
class OrderCreate(BaseModel):
    product_id: int
    quantity: int


# --- API ENDPOINT: Khởi tạo đơn hàng ---
@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrderCreate):
    
    # BẪY LỖI 2: Số lượng đặt mua không hợp lệ (Invalid Quantity)
    if order_in.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số lượng mua phải lớn hơn 0"
        )
        
    # Tìm kiếm sản phẩm trong database giả lập
    target_product = None
    for p in products_db:
        if p["id"] == order_in.product_id:
            target_product = p
            break
            
    # Bẫy lỗi phụ trợ: Kiểm tra sản phẩm có tồn tại hay không
    if target_product is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sản phẩm không tồn tại trong hệ thống"
        )
        
    # BẪY LỖI 1: Số lượng đặt vượt quá tồn kho (Out of Stock)
    if order_in.quantity > target_product["stock"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sản phẩm không đủ số lượng trong kho"
        )
        
    # --- XỬ LÝ KHI MỌI ĐIỀU KIỆN ĐỀU HỢP LỆ ---
    
    # 1. Tiến hành trừ bớt số lượng kho (stock) của sản phẩm đó
    target_product["stock"] = target_product["stock"] - order_in.quantity
    
    # 2. Tính toán tổng tiền hóa đơn đơn hàng
    total_price = target_product["price"] * order_in.quantity
    
    # 3. Tạo ID tự tăng an toàn dựa trên độ dài mảng orders_db
    new_order_id = max([o["id"] for o in orders_db]) + 1 if orders_db else 1
    
    # 4. Đóng gói đối tượng đơn hàng mới
    new_order = {
        "id": new_order_id,
        "product_id": order_in.product_id,
        "product_name": target_product["name"],
        "quantity": order_in.quantity,
        "total_price": total_price
    }
    
    # 5. Thêm bản ghi mới vào mảng lưu trữ đơn hàng
    orders_db.append(new_order)
    
    # Trả về dữ liệu đơn hàng thành công kèm mã trạng thái 201 Created
    return new_order