#  Phần 1: Báo cáo phân tích
# Input của bài toán là gì?
# Dữ liệu gốc: Danh sách sản phẩm giả lập products (mảng các dictionary), mỗi sản phẩm có các trường: id, name, và price.
# Tham số từ Client: Hai tham số truy vấn (Query Parameters) tùy chọn (không bắt buộc) truyền qua URL:
# keyword: Kiểu dữ liệu string, dùng để tìm kiếm sản phẩm theo tên.
# max_price: Kiểu dữ liệu float, dùng để lọc sản phẩm có giá nhỏ hơn hoặc bằng giá trị này.
# Output mong muốn là gì?Trường hợp dữ liệu hợp lệ: Trả về một danh sách (JSON Array) chứa các sản phẩm thỏa mãn đồng thời các điều kiện lọc. Nếu không truyền tham số nào, trả về toàn bộ danh sách.Trường hợp lỗi dữ liệu (Bẫy giá tối đa không hợp lệ): Trả về mã lỗi hoặc một JSON Object chứa thông báo chi tiết lỗi định dạng dạng:JSON{
#   "detail": "max_price không được âm"
# }
# Đề xuất giải pháp xử lý bài toán:
# Sử dụng framework FastAPI để định nghĩa endpoint GET /products.
# Khai báo hai tham số keyword và max_price trong hàm xử lý dưới dạng Optional (mặc định bằng None) để thể hiện tính chất không bắt buộc.
# Thực hiện bẫy lỗi đầu vào ngay đầu hàm: Nếu max_price được truyền vào và nhỏ hơn 0, lập tức trả về thông báo lỗi (có thể dùng cấu trúc dict thường hoặc ném lỗi HTTPException chuẩn hóa của FastAPI với mã trạng thái 400 Bad Request).
# Sử dụng một mảng trung gian (hoặc kỹ thuật duyệt mảng) để kiểm tra từng sản phẩm dựa trên trạng thái None hay có giá trị của keyword và max_price.
# Thiết kế các bước xử lý bài toán:
# Bước 1: Khởi tạo ứng dụng FastAPI và khai báo danh sách dữ liệu cứng products.
# Bước 2: Định nghĩa route @app.get("/products") nhận hai tham số keyword: str = None và max_price: float = None.Bước 
# 3: Kiểm tra ràng buộc: Nếu max_price is not None và max_price < 0, trả về kết quả lỗi {"detail": "max_price không được âm"}.
# Bước 4: Tạo một danh sách rỗng để chứa kết quả lọc: filtered_products = [].
# Bước 5: Duyệt qua từng sản phẩm trong danh sách gốc products:Chuyển tên sản phẩm và từ khóa keyword về dạng chữ thường (.lower()) để tìm kiếm không phân biệt hoa thường.Kiểm tra điều kiện thỏa mãn:Nếu có keyword nhưng tên sản phẩm không chứa keyword $\rightarrow$ Loại.Nếu có max_price nhưng giá sản phẩm lớn hơn max_price $\rightarrow$ Loại.Nếu vượt qua các bộ lọc trên, thêm sản phẩm đó vào filtered_products.
# Bước 6: Trả về danh sách filtered_products.
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()

# Dữ liệu danh sách sản phẩm (Mock Data)
products = [
    {"id": 1, "name": "Laptop", "price": 15000000},
    {"id": 2, "name": "Mouse", "price": 250000},
    {"id": 3, "name": "Keyboard", "price": 1200000},
    {"id": 4, "name": "Monitor", "price": 3500000}
]

# Định nghĩa API GET /products với các Query Parameters tùy chọn
@app.get("/products")
def get_products(keyword: str = None, max_price: float = None):
    
    # 1. Ràng buộc & Bẫy dữ liệu: Kiểm tra giá tối đa không hợp lệ
    if max_price is not None and max_price < 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "max_price không được âm"}
        )
        
    # 2. Tiến hành lọc dữ liệu dựa trên các tham số được truyền lên
    filtered_products = []
    
    for product in products:
        # Giả định ban đầu là sản phẩm thỏa mãn điều kiện
        is_match = True
        
        # Kiểm tra điều kiện 1: Tìm kiếm theo từ khóa (keyword)
        if keyword is not None:
            # Chuyển đổi cả hai chuỗi về chữ thường để không phân biệt hoa/thường
            if keyword.lower() not in product["name"].lower():
                is_match = False
                
        # Kiểm tra điều kiện 2: Lọc theo giá tối đa (max_price)
        if max_price is not None:
            if product["price"] > max_price:
                is_match = False
                
        # Nếu sản phẩm thỏa mãn tất cả các bộ lọc hiện tại, đưa vào danh sách kết quả
        if is_match:
            filtered_products.append(product)
            
    # 3. Trả về kết quả cuối cùng cho Client
    return filtered_products