from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class MenuStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"

# Schema dùng cho việc Thêm mới (POST) và Cập nhật toàn diện (PUT)
class MenuItemSchema(BaseModel):
    dish_code: str = Field(..., min_length=1, description="Mã món ăn không được trùng lặp")
    dish_name: str = Field(..., min_length=1, description="Tên món ăn không được để trống")
    calorie_count: int = Field(..., gt=0, description="Hàm lượng calo phải lớn hơn 0")
    price: float = Field(..., gt=0, description="Đơn giá món ăn phải lớn hơn 0")
    status: MenuStatus = Field(default=MenuStatus.AVAILABLE, description="Trạng thái món ăn")

# Schema dùng để định hình dữ liệu đầu ra sạch
class MenuItemResponse(BaseModel):
    id: int
    dish_code: str
    dish_name: str
    calorie_count: int
    price: float
    status: str

    model_config = {
        "from_attributes": True  # Kích hoạt tính năng ánh xạ ngược từ đối tượng ORM
    }