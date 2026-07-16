from pydantic import BaseModel, Field

# --- Schemas Sản phẩm ---
class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

# --- Schemas Khách hàng ---
class CustomerUpdate(BaseModel):
    full_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)