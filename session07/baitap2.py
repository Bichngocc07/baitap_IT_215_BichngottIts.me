# Phần 1: Chỉ ra lỗi bằng test case cụ thể
# TEST CASE 1: Thử nghiệm cập nhật đơn hàng không tồn tại (ID = 999)
# STT: 1
# Dữ liệu/Endpoint gửi lên: * Path: PUT /orders/999/status
# Body: {"status": "SHIPPING"}
# Kết quả hiện tại (Mã HTTP + Body): * Mã HTTP: 200 OK
# Body: {"statuscode": 200, "message": "Cập nhật thành công", "data": null}
# Kết quả đúng mong muốn: * Mã HTTP: 404 Not Found
# Body: {"detail": "Order not found"}
# Lỗi phát hiện: Lọt luồng xử lý lỗi nghiêm trọng. Khi không tìm thấy đơn hàng (if not order), hàm chỉ dùng lệnh print() ra màn hình console của backend chứ không hề ngắt
# hàm bằng return hay raise. Code bên dưới vẫn tiếp tục chạy
# và ghi đè trạng thái vào một đối tượng rỗng (None), dẫn đến việc phản hồi về client thông báo "thành công ảo" với mã HTTP 200.
# TEST CASE 2: Thử nghiệm gửi sai trạng thái quy định (status = "TRONG_SANG")
# STT: 2
# Dữ liệu/Endpoint gửi lên: * Path: PUT /orders/1/status
# Body: {"status": "TRONG_SANG"}
# Kết quả hiện tại (Mã HTTP + Body): * Mã HTTP: 200 OK
# Body: {"error": "Trạng thái không hợp lệ"}
# Kết quả đúng mong muốn: * Mã HTTP: 400 Bad Request
# Body: {"detail": "Trạng thái không hợp lệ"}
# Lỗi phát hiện: Lỗi lọt mã trạng thái HTTP. Hệ thống phát hiện ra trạng thái "TRONG_SANG" gửi lên là sai quy định (không nằm trong danh sách 3 trạng thái
#  hợp lệ). Tuy nhiên, lập trình viên lạidùng câu lệnh return {"error": ...} thông thường, khiến FastAPI hiểu đây là một xử lý thành công và trả về mã HTTP 200 OK cho một request lỗi.

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Dữ liệu database giả lập
orders_db = [
    {"id": 1, "customer_name": "Nguyen Van A", "status": "PENDING"},
    {"id": 2, "customer_name": "Tran Thi B", "status": "SHIPPING"}
]

# Danh sách trạng thái hợp lệ của hệ thống
VALID_STATUSES = ["PENDING", "SHIPPING", "DELIVERED"]

class StatusUpdate(BaseModel):
    status: str

# API Cập nhật trạng thái giao hàng
@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, data: StatusUpdate):
    
    # 1. Quét mảng tìm đơn hàng theo order_id
    order = None
    for o in orders_db:
        if o["id"] == order_id:
            order = o
            break
            
    # BẪY LỖI 1: Nếu order_id không tồn tại, ngắt luồng và trả về lỗi 404 ngay lập tức
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
        
    # Chuẩn hóa chuỗi trạng thái nhận vào (viết hoa, xóa khoảng trắng)
    input_status = data.status.strip().upper()
        
    # BẪY LỖI 2: Nếu trạng thái gửi lên nằm ngoài danh sách quy định, ngắt luồng trả về lỗi 400
    if input_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Trạng thái không hợp lệ"
        )
        
    # 2. CẬP NHẬT: Khi mọi thứ đã hợp lệ, tiến hành lưu trạng thái mới vào bộ nhớ
    order["status"] = input_status
    
    # 3. TRẢ VỀ: Đúng chuẩn RESTful Status Code (Tự động là 200 OK khi hàm return thông thường)
    return {
        "message": "Cập nhật thành công", 
        "data": order
    }