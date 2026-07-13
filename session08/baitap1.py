from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# --- 3. DỮ LIỆU MẪU (Mock Data) ---
carriers = [
    {"id": 1, "code": "GHN", "name": "Giao Hang Nhanh", "max_weight_capacity": 5000, "status": "ACTIVE"},
    {"id": 2, "code": "GHTK", "name": "Giao Hang Tiet Kiem", "max_weight_capacity": 3000, "status": "ACTIVE"},
    {"id": 3, "code": "VTP", "name": "Viettel Post", "max_weight_capacity": 10000, "status": "SUSPENDED"}
]

shipments = [
    {
        "id": 1,
        "carrier_id": 1,
        "order_reference": "ORD-2026-001",
        "total_weight": 4500,
        "dispatch_date": "2026-07-01",
        "shift": "MORNING"
    }
]

# Danh mục quy chuẩn hệ thống
VALID_CARRIER_STATUSES = ["ACTIVE", "INACTIVE", "SUSPENDED"]
VALID_SHIFTS = ["MORNING", "AFTERNOON", "NIGHT"]


# --- PYDANTIC SCHEMAS (Nhận dữ liệu thô) ---
class CarrierCreate(BaseModel):
    code: str
    name: str
    max_weight_capacity: int
    status: str

class CarrierUpdate(BaseModel):
    name: Optional[str] = None
    max_weight_capacity: Optional[int] = None
    status: Optional[str] = None

class ShipmentCreate(BaseModel):
    carrier_id: int
    order_reference: str
    total_weight: int
    dispatch_date: str  # Định dạng "YYYY-MM-DD"
    shift: str          # MORNING / AFTERNOON / NIGHT


# =================================================================
# I. CÁC API QUẢN LÝ ĐỐI TÁC VẬN CHUYỂN (CARRIERS)
# =================================================================

# API 1: Thêm đối tác vận chuyển mới (POST /carriers)
@app.post("/carriers", status_code=status.HTTP_201_CREATED)
def create_carrier(carrier_in: CarrierCreate):
    
    # Kiểm tra thủ công: name không được rỗng và có độ dài tối thiểu là 3 ký tự
    if len(carrier_in.name.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Tên đối tác không được rỗng và phải có độ dài tối thiểu là 3 ký tự"
        )
        
    # Kiểm tra thủ công: max_weight_capacity phải là số nguyên lớn hơn 0
    if carrier_in.max_weight_capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Năng lực vận chuyển tối đa phải lớn hơn 0"
        )
        
    # Kiểm tra thủ công: status phải đúng quy chuẩn
    status_upper = carrier_in.status.strip().upper()
    if status_upper not in VALID_CARRIER_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Trạng thái đối tác phải là ACTIVE, INACTIVE hoặc SUSPENDED"
        )
        
    # Kiểm tra thủ công: code không được trùng trong hệ thống
    for c in carriers:
        if c["code"].strip().upper() == carrier_in.code.strip().upper():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Mã đối tác vận chuyển (code) đã tồn tại"
            )

    # Tự động tăng ID an toàn bằng hàm max()
    new_id = max([c["id"] for c in carriers]) + 1 if carriers else 1
    
    new_carrier = {
        "id": new_id,
        "code": carrier_in.code.strip().upper(),
        "name": carrier_in.name.strip(),
        "max_weight_capacity": carrier_in.max_weight_capacity,
        "status": status_upper
    }
    carriers.append(new_carrier)
    return {"message": "Thêm đối tác vận chuyển thành công", "data": new_carrier}


# API 2: Lấy danh sách đối tác + Tìm kiếm và lọc (GET /carriers)
@app.get("/carriers")
def get_all_carriers(
    keyword: Optional[str] = None, 
    status: Optional[str] = None, 
    min_weight: Optional[int] = None
):
    filtered_carriers = []
    for c in carriers:
        is_match = True
        
        # Lọc theo keyword (tìm trong name hoặc code không phân biệt hoa thường)
        if keyword is not None:
            k = keyword.strip().lower()
            if k not in c["name"].lower() and k not in c["code"].lower():
                is_match = False
                
        # Lọc theo trạng thái hoạt động chính xác
        if status is not None:
            if c["status"].lower() != status.strip().lower():
                is_match = False
                
        # Lọc theo năng lực vận chuyển tối đa từ mức này trở lên
        if min_weight is not None:
            if c["max_weight_capacity"] < min_weight:
                is_match = False
                
        if is_match:
            filtered_carriers.append(c)
            
    return {"message": "Lấy danh sách đối tác vận chuyển thành công", "data": filtered_carriers}


# API 3: Lấy chi tiết một đối tác (GET /carriers/{carrier_id})
@app.get("/carriers/{carrier_id}")
def get_carrier_detail(carrier_id: int):
    for c in carriers:
        if c["id"] == carrier_id:
            return {"message": "Tìm thấy đối tác vận chuyển", "data": c}
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrier not found")


# API 4: Cập nhật thông tin đối tác (PUT /carriers/{carrier_id})
@app.put("/carriers/{carrier_id}")
def update_carrier(carrier_id: int, carrier_update: CarrierUpdate):
    for c in carriers:
        if c["id"] == carrier_id:
            
            if carrier_update.name is not None:
                if len(carrier_update.name.strip()) < 3:
                    raise HTTPException(status_code=400, detail="Tên đối tác phải có độ dài tối thiểu là 3 ký tự")
                c["name"] = carrier_update.name.strip()
                
            if carrier_update.max_weight_capacity is not None:
                if carrier_update.max_weight_capacity <= 0:
                    raise HTTPException(status_code=400, detail="Năng lực vận chuyển tối đa phải lớn hơn 0")
                c["max_weight_capacity"] = carrier_update.max_weight_capacity
                
            if carrier_update.status is not None:
                st_upper = carrier_update.status.strip().upper()
                if st_upper not in VALID_CARRIER_STATUSES:
                    raise HTTPException(status_code=400, detail="Trạng thái đối tác không hợp lệ")
                c["status"] = st_upper
                
            return {"message": "Cập nhật thông tin đối tác thành công", "data": c}
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrier not found")


# API 5: Xóa đối tác vận chuyển (DELETE /carriers/{carrier_id})
@app.delete("/carriers/{carrier_id}")
def delete_carrier(carrier_id: int):
    for index, c in enumerate(carriers):
        if c["id"] == carrier_id:
            deleted = carriers.pop(index)
            return {"message": "Xóa đối tác vận chuyển thành công", "data": deleted}
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrier not found")


# =================================================================
# II. CÁC API QUẢN LÝ CHUYẾN GIAO HÀNG (SHIPMENTS)
# =================================================================

# API 6: Khởi tạo chuyến giao hàng mới (POST /shipments)
@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(shipment_in: ShipmentCreate):
    
    # 1. Kiểm tra ca làm việc (shift) phải nằm trong các giá trị quy chuẩn
    shift_upper = shipment_in.shift.strip().upper()
    if shift_upper not in VALID_SHIFTS:
        raise HTTPException(status_code=400, detail="Ca làm việc phải là MORNING, AFTERNOON hoặc NIGHT")
        
    # 2. Kiểm tra khối lượng chuyến hàng (total_weight) phải lớn hơn 0
    if shipment_in.total_weight <= 0:
        raise HTTPException(status_code=400, detail="Khối lượng chuyến hàng phải lớn hơn 0")
        
    # 3. Kiểm tra carrier_id truyền lên phải tồn tại trong tập dữ liệu carriers
    target_carrier = None
    for c in carriers:
        if c["id"] == shipment_in.carrier_id:
            target_carrier = c
            break
            
    if target_carrier is None:
        raise HTTPException(status_code=400, detail="Đối tác vận chuyển (carrier_id) không tồn tại")
        
    # 4. Kiểm tra đối tác vận chuyển phải có trạng thái hoạt động là "ACTIVE"
    if target_carrier["status"] != "ACTIVE":
        raise HTTPException(status_code=400, detail="Đối tác vận chuyển được chọn hiện đang bị đình chỉ hoặc bảo trì hệ thống")
        
    # 5. Kiểm tra khối lượng không được phép vượt quá năng lực vận chuyển tối đa (max_weight_capacity) của đối tác
    if shipment_in.total_weight > target_carrier["max_weight_capacity"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Khối lượng chuyến hàng ({shipment_in.total_weight}) vượt quá năng lực vận chuyển tối đa của đối tác ({target_carrier['max_weight_capacity']})"
        )
        
    # 6. Kiểm tra TRÙNG LỊCH: Một đối tác vận chuyển không được xếp trùng lịch điều phối trên cùng một ngày (dispatch_date) và cùng ca làm việc (shift)
    for s in shipments:
        if (s["carrier_id"] == shipment_in.carrier_id and 
            s["dispatch_date"] == shipment_in.dispatch_date.strip() and 
            s["shift"] == shift_upper):
            raise HTTPException(status_code=400, detail="Đối tác vận chuyển này đã được xếp lịch điều phối chuyến hàng vào ngày và ca làm việc này rồi")

    # Tiến hành tạo chuyến hàng khi vượt qua toàn bộ các bẫy dữ liệu
    new_shipment_id = max([s["id"] for s in shipments]) + 1 if shipments else 1
    
    new_shipment = {
        "id": new_shipment_id,
        "carrier_id": shipment_in.carrier_id,
        "order_reference": shipment_in.order_reference.strip(),
        "total_weight": shipment_in.total_weight,
        "dispatch_date": shipment_in.dispatch_date.strip(),
        "shift": shift_upper
    }
    
    shipments.append(new_shipment)
    return {"message": "Khởi tạo chuyến giao hàng thành công", "data": new_shipment}


# API 7: Xem toàn bộ danh sách các chuyến giao hàng (GET /shipments)
@app.get("/shipments")
def get_all_shipments():
    return {"message": "Lấy danh sách các chuyến giao hàng thành công", "data": shipments}