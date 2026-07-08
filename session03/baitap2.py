# Phần 1: Phân tích lỗi
# Endpoint hiện tại có Path Parameter không?
# Có. Endpoint hiện tại đang cấu hình khai báo Path Parameter thông qua cú pháp cụm {status} đặt trong chuỗi định tuyến.
# Path Parameter trong bài này là gì?
# Path Parameter trong bài này là status.
# Khi gọi /orders/status/pending, biến status nhận giá trị gì?
# Biến status sẽ nhận giá trị là chuỗi tĩnh: "pending".
# Vì sao API hiện tại lại trả về sai dữ liệu?
# Vì trong logic xử lý của hàm get_orders_by_status(status: str), lập trình viên đang dùng lệnh return orders. Câu lệnh này trả về nguyên vẹn toàn bộ danh sách mảng dữ liệu gốc ban đầu mà hoàn toàn bỏ qua bước lọc (filter) điều kiện theo biến truyền vào.
# Dòng code nào đang khiến API bỏ qua giá trị status?
# Dòng code số 13 (dòng cuối cùng trong ảnh mã nguồn): return orders. Dòng này trực tiếp trả về mảng tổng thay vì mảng đã được lọc theo giá trị của tham số status.
from fastapi import FastAPI

app = FastAPI()

# Danh sách đơn hàng giả lập (Mock Data)
orders = [
    {"id": 1, "customer_name": "Nguyen Van An", "total": 250000, "status": "pending"},
    {"id": 2, "customer_name": "Tran Thi Binh", "total": 500000, "status": "paid"},
    {"id": 3, "customer_name": "Le Van Cuong", "total": 450000, "status": "cancelled"},
    {"id": 4, "customer_name": "Pham Thi Dung", "total": 320000, "status": "pending"}
]

# Danh sách các trạng thái hợp lệ theo quy định nghiệp vụ
VALID_STATUSES = ["pending", "paid", "cancelled"]

@app.get("/orders/status/{status}")
def get_orders_by_status(status: str):
    # 1. Kiểm tra tính hợp lệ của tham số đầu vào từ URL
    if status not in VALID_STATUSES:
        return {
            "message": "Trạng thái đơn hàng không hợp lệ"
        }
    
    # 2. Tiến hành lọc danh sách đơn hàng có status khớp với Path Parameter
    filtered_orders = [order for order in orders if order["status"] == status]
    
    # 3. Trả về danh sách đơn hàng sau khi lọc thành công
    return filtered_orders