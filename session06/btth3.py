from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# --- 3. DỮ LIỆU MẪU (Mock Data) ---
rooms = [
    {"id": 1, "code": "R101", "name": "Room 101", "capacity": 30, "status": "AVAILABLE"},
    {"id": 2, "code": "R102", "name": "Room 102", "capacity": 20, "status": "AVAILABLE"},
    {"id": 3, "code": "R103", "name": "Room 103", "capacity": 40, "status": "MAINTENANCE"}
]

room_bookings = [
    {
        "id": 1,
        "room_id": 1,
        "class_name": "Python Basic",
        "student_count": 25,
        "date": "2026-07-02",
        "slot": "MORNING"
    }
]

# Danh mục cấu hình trạng thái và slot hợp lệ
VALID_ROOM_STATUSES = ["AVAILABLE", "IN_USE", "MAINTENANCE"]
VALID_SLOTS = ["MORNING", "AFTERNOON", "EVENING"]


# --- PYDANTIC SCHEMAS (Nhận dữ liệu thô) ---
class RoomCreate(BaseModel):
    code: str
    name: str
    capacity: int
    status: str

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = None

class BookingCreate(BaseModel):
    room_id: int
    class_name: str
    student_count: int
    date: str  # Định dạng "YYYY-MM-DD"
    slot: str  # MORNING / AFTERNOON / EVENING


# =================================================================
# I. CÁC API QUẢN LÝ PHÒNG HỌC (ROOMS)
# =================================================================

# API 1: Thêm phòng học (POST /rooms)
@app.post("/rooms", status_code=status.HTTP_201_CREATED)
def create_room(room_in: RoomCreate):
    # Quy tắc xử lý bằng lệnh if thủ công
    if room_in.name.strip() == "":
        raise HTTPException(status_code=400, detail="Tên phòng học không được để trống")
    if room_in.capacity <= 0:
        raise HTTPException(status_code=400, detail="Sức chứa (capacity) phải lớn hơn 0")
    if room_in.status.strip().upper() not in VALID_ROOM_STATUSES:
        raise HTTPException(status_code=400, detail="Trạng thái phòng không hợp lệ")
        
    for room in rooms:
        if room["code"].strip().upper() == room_in.code.strip().upper():
            raise HTTPException(status_code=400, detail="Mã phòng học (code) đã tồn tại")

    new_id = max([r["id"] for r in rooms]) + 1 if rooms else 1
    new_room = {
        "id": new_id,
        "code": room_in.code.strip().upper(),
        "name": room_in.name.strip(),
        "capacity": room_in.capacity,
        "status": room_in.status.strip().upper()
    }
    rooms.append(new_room)
    return {"message": "Thêm phòng học thành công", "data": new_room}


# API 2: Lấy danh sách phòng học + Tìm kiếm và lọc (GET /rooms)
@app.get("/rooms")
def get_all_rooms(keyword: Optional[str] = None, status: Optional[str] = None, min_capacity: Optional[int] = None):
    filtered_rooms = []
    for room in rooms:
        is_match = True
        
        if keyword is not None:
            k = keyword.strip().lower()
            if k not in room["name"].lower() and k not in room["code"].lower():
                is_match = False
                
        if status is not None:
            if room["status"].lower() != status.strip().lower():
                is_match = False
                
        if min_capacity is not None:
            if room["capacity"] < min_capacity:
                is_match = False
                
        if is_match:
            filtered_rooms.append(room)
            
    return {"message": "Lấy danh sách phòng học thành công", "data": filtered_rooms}


# API 3: Lấy chi tiết phòng học (GET /rooms/{room_id})
@app.get("/rooms/{room_id}")
def get_room_detail(room_id: int):
    for room in rooms:
        if room["id"] == room_id:
            return {"message": "Tìm thấy phòng học", "data": room}
    raise HTTPException(status_code=404, detail="Room not found")


# API 4: Cập nhật phòng học (PUT /rooms/{room_id})
@app.put("/rooms/{room_id}")
def update_room(room_id: int, room_update: RoomUpdate):
    for room in rooms:
        if room["id"] == room_id:
            if room_update.name is not None:
                if room_update.name.strip() == "":
                    raise HTTPException(status_code=400, detail="Tên không được để trống")
                room["name"] = room_update.name.strip()
                
            if room_update.capacity is not None:
                if room_update.capacity <= 0:
                    raise HTTPException(status_code=400, detail="Sức chứa phải lớn hơn 0")
                room["capacity"] = room_update.capacity
                
            if room_update.status is not None:
                status_upper = room_update.status.strip().upper()
                if status_upper not in VALID_ROOM_STATUSES:
                    raise HTTPException(status_code=400, detail="Trạng thái không hợp lệ")
                room["status"] = status_upper
                
            return {"message": "Cập nhật phòng học thành công", "data": room}
            
    raise HTTPException(status_code=404, detail="Room not found")


# API 5: Xóa phòng học (DELETE /rooms/{room_id})
@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    for index, room in enumerate(rooms):
        if room["id"] == room_id:
            deleted_room = rooms.pop(index)
            return {"message": "Xóa phòng học thành công", "data": deleted_room}
    raise HTTPException(status_code=404, detail="Room not found")


# =================================================================
# II. CÁC API ĐẶT PHÒNG HỌC (ROOM BOOKINGS)
# =================================================================

# API 6: Đặt lịch sử dụng phòng (POST /room-bookings)
@app.post("/room-bookings", status_code=status.HTTP_201_CREATED)
def create_room_booking(booking_in: BookingCreate):
    
    # 1. Kiểm tra slot chỉ được nhận một trong các giá trị quy định
    slot_upper = booking_in.slot.strip().upper()
    if slot_upper not in VALID_SLOTS:
        raise HTTPException(status_code=400, detail="Slot học phải là MORNING, AFTERNOON hoặc EVENING")
        
    # 2. Kiểm tra student_count phải lớn hơn 0
    if booking_in.student_count <= 0:
        raise HTTPException(status_code=400, detail="Số lượng học viên phải lớn hơn 0")

    # 3. Kiểm tra room_id phải tồn tại và lấy thông tin phòng để kiểm tra trạng thái & sức chứa
    target_room = None
    for room in rooms:
        if room["id"] == booking_in.room_id:
            target_room = room
            break
            
    if target_room is None:
        raise HTTPException(status_code=400, detail="Phòng học (room_id) không tồn tại")
        
    # 4. Kiểm tra phòng phải có status = "AVAILABLE"
    if target_room["status"] != "AVAILABLE":
        raise HTTPException(status_code=400, detail="Phòng học hiện không ở trạng thái trống (AVAILABLE)")
        
    # 5. Kiểm tra student_count không được vượt quá capacity của phòng
    if booking_in.student_count > target_room["capacity"]:
        raise HTTPException(status_code=400, detail="Số lượng học viên vượt quá sức chứa tối đa của phòng")
        
    # 6. Kiểm tra bẫy lỗi TRÙNG LỊCH: Một phòng không được đặt trùng date và slot
    for booking in room_bookings:
        if (booking["room_id"] == booking_in.room_id and 
            booking["date"] == booking_in.date.strip() and 
            booking["slot"] == slot_upper):
            raise HTTPException(status_code=400, detail="Phòng học đã bị đặt trùng lịch vào ngày và ca học này")

    # Tự tăng ID cho bảng đặt phòng
    new_booking_id = max([b["id"] for b in room_bookings]) + 1 if room_bookings else 1
    
    new_booking = {
        "id": new_booking_id,
        "room_id": booking_in.room_id,
        "class_name": booking_in.class_name.strip(),
        "student_count": booking_in.student_count,
        "date": booking_in.date.strip(),
        "slot": slot_upper
    }
    
    room_bookings.append(new_booking)
    return {"message": "Đặt lịch phòng học thành công", "data": new_booking}


# API 7: Xem danh sách lịch đặt phòng (GET /room-bookings)
@app.get("/room-bookings")
def get_all_bookings():
    return {"message": "Lấy danh sách lịch đặt phòng thành công", "data": room_bookings}