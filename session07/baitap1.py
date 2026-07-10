# Phần 1: Chỉ ra lỗi bằng test case cụ thể
# TEST CASE 1: Thử nghiệm đọc đơn hàng không tồn tại (ID = 999)
# STT: 1
# Dữ liệu gửi lên (URL Path): GET /orders/999
# Kết quả hiện tại (Mã HTTP + Body): * Mã HTTP: 200 OK
# Body: {"message": "Order not found"}
# Kết quả đúng mong muốn: * Mã HTTP: 404 Not Found
# Body: {"detail": "Order not found"} (hoặc thông báo lỗi rõ ràng của hệ thống).
# Lỗi phát hiện: Lỗi trả về mã trạng thái "ảo". Hệ thống tìm không thấy dữ liệu nhưng vẫn trả về mã thành công 200 thay vì phải ném ra mã lỗi 404.
# TEST CASE 2: Thử nghiệm đọc đơn hàng hợp lệ để kiểm tra bảo mật (ID = 1)
# STT: 2
# Dữ liệu gửi lên (URL Path): GET /orders/1
# Kết quả hiện tại (Mã HTTP + Body): * Mã HTTP: 200 OK
# Body:
# JSON
# {
#   "id": 1,
#   "customer_name": "Nguyen Van A",
#   "total_amount": 150000.0,
#   "profit_margin": 0.25,
#   "supplier_id": "SUP_DELL_01"
# }
# Kết quả đúng mong muốn: * Mã HTTP: 200 OK
# Body: Bắt buộc loại bỏ hai trường nhạy cảm profit_margin và supplier_id. Chỉ công khai thông tin cơ bản:
# JSON
# {
#   "id": 1,
#   "customer_name": "Nguyen Van A",
#   "total_amount": 150000.0
# }
# Lỗi phát hiện: Lỗi lộ dữ liệu nội bộ nghiêm trọng. API bê nguyên đối tượng gốc trong database trả về cho khách hàng, làm lộ biên lợi nhuận và mã nhà cung cấp bí mật.
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Dữ liệu nội bộ trong bộ nhớ tạm (Database giả lập)
orders_db = [
    {
        "id": 1,
        "customer_name": "Nguyen Van A",
        "total_amount": 150000.0,
        "profit_margin": 0.25,        # Nhạy cảm - Cấm lộ!
        "supplier_id": "SUP_DELL_01"  # Nhạy cảm - Cấm lộ!
    },
    {
        "id": 2,
        "customer_name": "Tran Thi B",
        "total_amount": 350000.0,
        "profit_margin": 0.30,        # Nhạy cảm - Cấm lộ!
        "supplier_id": "SUP_LOGI_02"  # Nhạy cảm - Cấm lộ!
    }
]

# API lấy chi tiết đơn hàng
@app.get("/orders/{order_id}")
def get_order_detail(order_id: int):
    
    # Duyệt mảng để đọc dữ liệu đơn hàng
    for order in orders_db:
        if order["id"] == order_id:
            
            # XỬ LÝ BẢO MẬT THỦ CÔNG: Tạo một dict mới chỉ chứa các trường được phép công khai
            public_order = {
                "id": order["id"],
                "customer_name": order["customer_name"],
                "total_amount": order["total_amount"]
            }
            
            # Trả về dữ liệu sạch đã lọc (Mã HTTP tự động là 200 OK)
            return public_order

    # BẪY LỖI TRẠNG THÁI "ẢO": Nếu chạy hết vòng lặp mà không tìm thấy ID khớp
    # Dùng raise HTTPException để ép trình duyệt trả về đúng mã lỗi 404 chuẩn RESTful
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Order not found"
    )