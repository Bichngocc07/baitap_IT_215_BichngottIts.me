from sqlalchemy.orm import Session
from models import Product

def get_all_product(db):
    products = db.query(Product).all()

    return {
        "message": "Lấy danh sách thành công",
        "data": products
    }
#Hàm lấy chi tiết sản phẩm
def get_product_detail(product_id:int,db):
    product = db.query(Product).filter(Product.id == product_id)
    if product is None:
        raise HTTPException
    
#API XÓA SẢN PHẨM
@app.delete("/products/{product_id}")
def delete_product(product_id:int, db:Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code= 404,
            detail="Không tìm thấy sản phẩm để xóa"
        )
    db.delete(product)
    db.commit()
    return{
        "message": "Xóa sản phẩm thành công",
        "data": product
    }
#API CẬP NHẬT SẢN PHẨM
@app.put("/products/{product_id}")
def updata_product(product_id:int,updata_product:ProductCreate,
                   db:Session = Depends(get_db)):
    product  = db.query(Product).filter(Product.id == product_id).filter()
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="không tìm thấy sản phẩm cập nhật"
        )
    product.name=updata_product.name
    product.price=updata_product.price
    db.commit()
    db.refresh(product)
    return{
        "message": "Cập nhật sản phẩm thành công!",
        "data": product
    }