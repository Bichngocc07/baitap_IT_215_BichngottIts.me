from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, description="Mã SKU không được trống")
    name: str = Field(..., min_length=1, description="Tên sản phẩm không được trống")
    price: float = Field(..., gt=0, description="Giá sản phẩm phải lớn hơn 0")