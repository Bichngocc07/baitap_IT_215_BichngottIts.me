#VALIDETA DỮ LIỆU TỪ CLIENT GỬI LÊN VÀ CẤU HÌNH RESPONSE TRẢ VỀ
from pydantic import BaseModel
class ProductCreate(BaseModel):
    name:str
    price:float