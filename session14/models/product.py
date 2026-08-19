from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.product import Product

"""
VIẾT API lấy dữ liệu
"""

router_product = APIRouter(
    prefix="/products",
    tags=["Product"]
)


@router_product.get("")
def get_all_product(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return {
        "message": "Lấy danh sách sản phẩm",
        "data": products
    }