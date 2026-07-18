#CÁC HÀM TƯƠNG TÁC VỚI DỮ LIỆU TRONG DB
#HÀM LẤY DỮ LIỆU TẤT CẢ DANH SÁCH SẢN PHẨM
from fastapi import HTTPException,UpdateProduct
from models import Product,ProductUpdate
def get_all_product(db):
    return db.query(Product).all()
def get_product_detail(id:int,db):
    Product = db.query(Product).filter(Product.id == id)
    if Product is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy sản phẩm"
        )
    return{
        "message":"Tìm thấy chi tiết sản phẩm thành công",
        "data"   : Product
    }
#HÀM THÊM SẢN PHẨM VÀO DATABASE
def add_new_product(product,db):
    new_product = product (
        name = Product.name,
        price = product.price
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return{
        "message":"Thêm sản phẩm vào thành công",
        "data"   : new_product
    }
def update_new_product(product_id:int,UpdatefProduct:ProductUpdate,db):
    product is None:
    raise HTTPException(
        status_code=404,
        detail="Không tìm thấy sản phẩm có id là: {product_id}"
    )
Product.name = UpdateProduct.name
Product.price = UpdateProduct.price