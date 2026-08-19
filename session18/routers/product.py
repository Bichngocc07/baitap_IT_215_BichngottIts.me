from fastapi import APIRouter, HTTPException

router_product = APIRouter(
    prefix="/products",
    tags=["Product"]
)

def get_product_detail(id, db):
    product = db.query(Product).filter(Product.id == id).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy sản phẩm"
        )

    return {
        "message": "Tìm thấy sản phẩm thành công",
        "data": product
    } 